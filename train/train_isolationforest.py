import logging
import sys
import os
import joblib
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Any

from sklearn.ensemble import IsolationForest
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score

from train import config
from train.preprocess import load_unified_data, clean_data, encode_categorical
from train.feature_engineering import create_features, normalize_features
from train.evaluate import evaluate_model

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

class IsolationForestWrapper:
    """Wrapper to make IsolationForest scikit-learn compatible for evaluate_model."""
    def __init__(self, model: IsolationForest):
        self.model = model
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        # decision_function: lower means more anomalous
        scores = -self.model.decision_function(X)
        
        # Scale to [0, 1] range
        s_min, s_max = scores.min(), scores.max()
        if s_max > s_min:
            scores_scaled = (scores - s_min) / (s_max - s_min)
        else:
            scores_scaled = np.zeros_like(scores)
            
        prob_1 = scores_scaled
        prob_0 = 1 - prob_1
        return np.vstack((prob_0, prob_1)).T
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = self.model.predict(X)
        return (preds == -1).astype(int)

def plot_histogram(scores: np.ndarray, labels: np.ndarray, path: str) -> None:
    plt.figure(figsize=(12, 6))
    plt.hist(scores[labels == 0], bins=50, alpha=0.6, color='blue', label='Normal (Legit)', density=True)
    plt.hist(scores[labels == 1], bins=50, alpha=0.6, color='red', label='Fraud', density=True)
    plt.title('Histogram of Isolation Forest Anomaly Scores')
    plt.xlabel('Anomaly Score (Higher is more anomalous)')
    plt.ylabel('Density')
    plt.yscale('log')
    plt.legend()
    plt.grid(True)
    plt.savefig(path)
    plt.close()

def plot_permutation_importance(importances: Any, feature_names: list, path: str) -> None:
    sorted_idx = importances.importances_mean.argsort()
    plt.figure(figsize=(10, 8))
    plt.boxplot(
        importances.importances[sorted_idx].T,
        vert=False,
        labels=np.array(feature_names)[sorted_idx],
    )
    plt.title("Permutation Feature Importance (Isolation Forest)")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def main() -> None:
    logger.info("=== Starting AI Fraud Detection Pipeline (Isolation Forest) ===")
    
    start_time = time.time()
    
    try:
        df = load_unified_data(sample_size=100000)
        df = clean_data(df)
        df = encode_categorical(df)
        df = create_features(df)
        num_cols = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
        df = normalize_features(df, num_cols)
    except Exception as e:
        logger.error(f"Error in data preprocessing: {e}")
        sys.exit(1)
        
    logger.info(f"Using full unified dataset shape: {df.shape}")
    df_sampled = df.copy()
    
    X = df_sampled.drop(columns=[config.TARGET_COLUMN])
    y = df_sampled[config.TARGET_COLUMN]
    feature_names = X.columns.tolist()
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, stratify=y, random_state=config.RANDOM_STATE
    )
    
    # Auto-calibrate contamination based on fraud ratio
    fraud_ratio = y_train.mean()
    logger.info(f"Training Fraud Ratio: {fraud_ratio:.6f}")
    
    # Grid Search Optimization
    n_estimators_list = [100, 200]
    contamination_list = [fraud_ratio if fraud_ratio > 0 else 'auto', 'auto']
    max_samples_list = [0.8, 1.0]
    
    best_roc = 0
    best_model = None
    best_params = {}
    
    logger.info("Optimizing Isolation Forest parameters...")
    for n_est in n_estimators_list:
        for cont in contamination_list:
            for ms in max_samples_list:
                model = IsolationForest(
                    n_estimators=n_est,
                    contamination=cont,
                    max_samples=ms,
                    random_state=42,
                    n_jobs=-1
                )
                model.fit(X_train)
                
                # Evaluate on test set
                scores = -model.decision_function(X_test)
                roc = roc_auc_score(y_test, scores)
                
                logger.info(f"Params (n_est={n_est}, cont={cont}, ms={ms}) -> ROC AUC: {roc:.6f}")
                
                if roc > best_roc:
                    best_roc = roc
                    best_model = model
                    best_params = {'n_estimators': n_est, 'contamination': cont, 'max_samples': ms}
                    
    logger.info(f"Best parameters: {best_params} with ROC AUC: {best_roc:.6f}")
    
    training_time = time.time() - start_time
    
    # Evaluation
    logger.info("Evaluating final model...")
    wrapped_model = IsolationForestWrapper(best_model)
    
    metrics = evaluate_model(wrapped_model, X_test, y_test, model_name="Isolation Forest", training_time=training_time)
    logger.info(f"Evaluation metrics: {metrics}")
    
    # Generate Anomaly Score Histogram
    report_dir = config.REPORTS_DIR / "Isolation Forest"
    os.makedirs(report_dir, exist_ok=True)
    
    logger.info("Generating anomaly score histogram...")
    anomaly_scores = -best_model.decision_function(X_test)
    hist_path = report_dir / "anomaly_score_histogram.png"
    plot_histogram(anomaly_scores, y_test.values, str(hist_path))
    
    # Generate Permutation Feature Importance
    logger.info("Calculating permutation feature importance (this might take a minute)...")
    def scorer(estimator, X, y):
        scores = -estimator.decision_function(X)
        return roc_auc_score(y, scores)
        
    try:
        # Sample for permutation importance to speed it up
        X_test_samp, _, y_test_samp, _ = train_test_split(X_test, y_test, train_size=5000, stratify=y_test, random_state=42)
        result = permutation_importance(best_model, X_test_samp, y_test_samp, scoring=scorer, n_repeats=5, random_state=42, n_jobs=-1)
        feat_path = report_dir / "feature_importance.png"
        plot_permutation_importance(result, feature_names, str(feat_path))
        logger.info(f"Saved feature importance to {feat_path}")
    except Exception as e:
        logger.error(f"Error calculating feature importance: {e}")
    
    # Save Model
    model_save_path = config.SAVED_MODELS_DIR / "isolationforest.pkl"
    joblib.dump(best_model, model_save_path)
    logger.info(f"Saved trained Isolation Forest model to {model_save_path}")
        
    logger.info("=== Isolation Forest Training Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
