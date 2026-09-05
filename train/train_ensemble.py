import logging
import sys
import os
import joblib
import time
import pandas as pd
import numpy as np
from typing import Dict, Any

import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV

from train import config
from train.preprocess import load_unified_data, clean_data, encode_categorical
from train.feature_engineering import create_features, normalize_features
from train.evaluate import evaluate_model
from train.train_autoencoder import FraudAutoencoder, AutoencoderWrapper
from sklearn.base import BaseEstimator, ClassifierMixin

class ThresholdOptimizedModel(BaseEstimator, ClassifierMixin):
    def predict_proba(self, X):
        if hasattr(self, 'model'):
            return self.model.predict_proba(X)
        return super().predict_proba(X)
    
    def predict(self, X):
        if hasattr(self, 'model'):
            return self.model.predict(X)
        return super().predict(X)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class StackingEnsemble:
    def __init__(self, meta_learner, models: Dict[str, Any], device: torch.device):
        self.meta_learner = meta_learner
        self.models = models
        self.device = device
        
    def _get_meta_features(self, X_raw: pd.DataFrame) -> np.ndarray:
        meta_features = []
        X_std = X_raw.values
        
        # XGBoost, LightGBM, Random Forest
        for name in ['xgboost', 'lightgbm', 'randomforest']:
            if name in self.models:
                meta_features.append(self.models[name].predict_proba(X_std)[:, 1])
            else:
                meta_features.append(np.zeros(len(X_std))) # Fallback if missing
                
        # Autoencoder
        if 'autoencoder' in self.models:
            ae_scaler = self.models['autoencoder_scaler']
            ae_model = self.models['autoencoder']
            num_cols = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest",
                        "balanceDiffOrig", "balanceDiffDest", "origBalanceChange", "destBalanceChange",
                        "amountToOrigRatio", "amountToDestRatio", "transactionHour", "transactionDay", "step"]
            cols_to_scale = [c for c in num_cols if c in X_raw.columns]
            
            X_ae = X_raw.copy()
            X_ae[cols_to_scale] = ae_scaler.transform(X_ae[cols_to_scale])
            X_ae_tensor = torch.FloatTensor(X_ae.values).to(self.device)
            
            with torch.no_grad():
                reconstructed = ae_model(X_ae_tensor)
                mse = torch.mean((X_ae_tensor - reconstructed) ** 2, dim=1).cpu().numpy()
            meta_features.append(mse)
        else:
            meta_features.append(np.zeros(len(X_std)))
            
        # Isolation Forest
        if 'isolationforest' in self.models:
            meta_features.append(-self.models['isolationforest'].decision_function(X_std))
        else:
            meta_features.append(np.zeros(len(X_std)))
            
        # QSVC
        if 'qsvc' in self.models:
            pipe = self.models['qsvc']
            if isinstance(pipe, dict) and 'model' in pipe:
                X_qsvc_scaled = pipe['scaler'].transform(X_std)
                X_qsvc_pca = pipe['pca'].transform(X_qsvc_scaled)
                meta_features.append(pipe['model'].predict(X_qsvc_pca))
            else:
                 meta_features.append(pipe.predict(X_std))
        else:
            meta_features.append(np.zeros(len(X_std)))
            
        # VQC
        if 'vqc' in self.models:
            pipe = self.models['vqc']
            if isinstance(pipe, dict) and 'model' in pipe:
                X_vqc_scaled = pipe['scaler'].transform(X_std)
                X_vqc_pca = pipe['pca'].transform(X_vqc_scaled)
                meta_features.append(pipe['model'].predict(X_vqc_pca))
            else:
                meta_features.append(pipe.predict(X_std))
        else:
            meta_features.append(np.zeros(len(X_std)))
            
        return np.column_stack(meta_features)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        meta_X = self._get_meta_features(X)
        return self.meta_learner.predict_proba(meta_X)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        meta_X = self._get_meta_features(X)
        probs = self.meta_learner.predict_proba(meta_X)[:, 1]
        threshold = getattr(self, "optimal_threshold_", 0.5)
        return (probs >= threshold).astype(int)

    def predict_risk(self, X: pd.DataFrame) -> pd.DataFrame:
        probs = self.predict_proba(X)[:, 1]
        risk_score = np.round(probs * 100, 2)
        confidence = np.round(np.abs(probs - 0.5) * 2 * 100, 2)
        return pd.DataFrame({'Fraud_Probability': probs, 'Risk_Score': risk_score, 'Confidence': confidence})

def main() -> None:
    logger.info("=== Starting AI Fraud Detection Pipeline (Stacking Ensemble) ===")
    
    start_time = time.time()
    
    try:
        df = load_unified_data(sample_size=10000) # smaller size for stacking
        df = clean_data(df)
        df = encode_categorical(df)
        df = create_features(df)
        num_cols = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
        df = normalize_features(df, num_cols)
    except Exception as e:
        logger.error(f"Error in data preprocessing: {e}")
        sys.exit(1)
        
    logger.info(f"Using full unified dataset shape: {df.shape}")
    # Reduce size drastically because QSVC/VQC predictions are extremely slow on large datasets
    target_total = 200
    frauds = df[df[config.TARGET_COLUMN] == 1]
    non_frauds = df[df[config.TARGET_COLUMN] == 0]
    
    n_frauds = min(len(frauds), target_total // 2)
    n_non_frauds = target_total - n_frauds
    
    sample_df = pd.concat([frauds.sample(n=n_frauds, random_state=config.RANDOM_STATE),
                           non_frauds.sample(n=n_non_frauds, random_state=config.RANDOM_STATE)])
    
    X_sample = sample_df.drop(columns=[config.TARGET_COLUMN])
    y_sample = sample_df[config.TARGET_COLUMN]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_sample, y_sample, test_size=0.3, stratify=y_sample, random_state=config.RANDOM_STATE
    )
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    models = {}
    
    logger.info("Loading base models...")
    for model_name, path in [
        ('xgboost', "xgboost_model.pkl"),
        ('lightgbm', "lightgbm_model.pkl"),
        ('randomforest', "randomforest.pkl"),
        ('isolationforest', "isolationforest.pkl"),
        ('qsvc', "qsvc.pkl"),
        ('vqc', "vqc.pkl")
    ]:
        full_path = config.SAVED_MODELS_DIR / path
        if full_path.exists():
            try:
                if model_name in ['vqc']:
                    import dill
                    with open(full_path, 'rb') as f:
                        models[model_name] = dill.load(f)
                else:
                    models[model_name] = joblib.load(full_path)
            except Exception as e:
                logger.warning(f"Could not load {model_name}: {e}")
        else:
            logger.warning(f"Model {model_name} missing at {full_path}")
            
    try:
        ae_path = config.SAVED_MODELS_DIR / "autoencoder.pt"
        if ae_path.exists():
            ae_checkpoint = torch.load(ae_path, map_location=device, weights_only=True)
            # Find input dim from scaler
            ae_scaler = joblib.load(config.SAVED_MODELS_DIR / "autoencoder_scaler.pkl")
            # Create model matching architecture in train_autoencoder.py
            # Input dimension to Autoencoder needs to be exactly matching. We'll extract it from the weights.
            input_dim = ae_checkpoint['encoder.0.weight'].shape[1]
            # Since latent_dim is variable, determine it:
            latent_dim = ae_checkpoint['encoder.4.weight'].shape[0]
            ae_model = FraudAutoencoder(input_dim=input_dim, latent_dim=latent_dim)
            ae_model.load_state_dict(ae_checkpoint)
            ae_model.to(device)
            ae_model.eval()
            models['autoencoder'] = ae_model
            models['autoencoder_scaler'] = ae_scaler
    except Exception as e:
        logger.warning(f"Could not load autoencoder: {e}")
        
    base_meta = LogisticRegression(random_state=config.RANDOM_STATE, max_iter=1000)
    ensemble = StackingEnsemble(base_meta, models, device)
    
    logger.info("Generating meta-features for training...")
    try:
        meta_X_train = ensemble._get_meta_features(X_train)
    except Exception as e:
        logger.error(f"Error generating meta-features: {e}")
        sys.exit(1)
        
    logger.info("Optimizing Meta-Learner via GridSearchCV...")
    param_grid = {'C': [0.01, 0.1, 1.0, 10.0], 'class_weight': [None, 'balanced']}
    grid = GridSearchCV(LogisticRegression(max_iter=1000, random_state=42), param_grid, cv=3, scoring='roc_auc')
    grid.fit(meta_X_train, y_train)
    
    ensemble.meta_learner = grid.best_estimator_
    logger.info(f"Best Meta-Learner params: {grid.best_params_}")
    
    logger.info("Optimizing decision threshold to maximize F1 Score...")
    from sklearn.metrics import precision_recall_curve
    y_train_probs = ensemble.meta_learner.predict_proba(meta_X_train)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y_train, y_train_probs)
    # Avoid division by zero
    f1_scores = np.divide(2 * (precisions * recalls), (precisions + recalls), out=np.zeros_like(precisions), where=(precisions + recalls) != 0)
    best_idx = np.argmax(f1_scores)
    optimal_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    ensemble.optimal_threshold_ = optimal_threshold
    logger.info(f"Optimal Threshold for Ensemble: {optimal_threshold:.4f} (F1 Score: {f1_scores[best_idx]:.4f})")
    
    training_time = time.time() - start_time
    
    logger.info("Evaluating Ensemble...")
    metrics = evaluate_model(ensemble, X_test, y_test.values, model_name="Stacking Ensemble", training_time=training_time)
    logger.info(f"Evaluation metrics: {metrics}")
    
    save_path = config.SAVED_MODELS_DIR / "ensemble.pkl"
    import dill
    with open(save_path, 'wb') as f:
        dill.dump(ensemble, f)
    logger.info(f"Saved Stacking Ensemble model to {save_path}")
    
    logger.info("=== Ensemble Training Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
