import logging
import sys
import joblib
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from lightgbm import LGBMClassifier, early_stopping
from sklearn.metrics import precision_recall_curve, f1_score, roc_auc_score, recall_score
from sklearn.calibration import CalibratedClassifierCV
from sklearn.base import BaseEstimator, ClassifierMixin

from train import config
from train.preprocess import load_unified_data, clean_data, encode_categorical
from train.feature_engineering import create_features, normalize_features
from train.evaluate import evaluate_model
import train.shap_explainer as shap_explainer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ThresholdOptimizedModel(BaseEstimator, ClassifierMixin):
    def __init__(self, model, threshold=0.5):
        self.model = model
        self.threshold = threshold
        
    def fit(self, X, y):
        return self
        
    def predict_proba(self, X):
        return self.model.predict_proba(X)
        
    def predict(self, X):
        probs = self.predict_proba(X)[:, 1]
        return (probs >= self.threshold).astype(int)

def main() -> None:
    logger.info("=== Starting AI Fraud Detection Training Pipeline (LightGBM) ===")
    
    start_time = time.time()
    
    # Increase sample size to improve model trained accuracy
    df = load_unified_data(sample_size=300000)
    df = clean_data(df)
    df = encode_categorical(df)
    df = create_features(df)
    num_cols = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
    df = normalize_features(df, num_cols)
    
    logger.info(f"Using full unified dataset shape: {df.shape}")
    df_sampled = df.copy()    
    X = df_sampled.drop(columns=[config.TARGET_COLUMN])
    y = df_sampled[config.TARGET_COLUMN]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, stratify=y, random_state=config.RANDOM_STATE
    )
    
    num_negative = sum(y_train == 0)
    num_positive = sum(y_train == 1)
    scale_pos_weight = num_negative / num_positive if num_positive > 0 else 1.0
    
    logger.info("Performing RandomizedSearchCV for LightGBM...")
    param_dist = {
        'num_leaves': [31, 70],
        'max_depth': [6, 10, -1],
        'learning_rate': [0.01, 0.05, 0.1],
        'feature_fraction': [0.8, 1.0],
        'bagging_fraction': [0.8, 1.0],
        'bagging_freq': [5],
        'lambda_l1': [0, 0.1],
        'lambda_l2': [0, 0.1],
        'min_child_samples': [20, 50]
    }
    
    base_lgbm = LGBMClassifier(
        n_estimators=500,
        scale_pos_weight=scale_pos_weight,
        random_state=config.RANDOM_STATE,
        n_jobs=-1,
        verbose=-1
    )
    
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=config.RANDOM_STATE)
    
    random_search = RandomizedSearchCV(
        estimator=base_lgbm,
        param_distributions=param_dist,
        n_iter=10,  # Keeping iterations reasonable
        scoring='roc_auc',
        cv=cv,
        verbose=1,
        random_state=config.RANDOM_STATE,
        n_jobs=1 # Avoid nested multiprocessing issues
    )
    
    # Fit random search (we won't use early stopping during CV for simplicity, but will train final model with it)
    random_search.fit(X_train, y_train)
    logger.info(f"Best parameters found: {random_search.best_params_}")
    
    logger.info("Training final LightGBM model with early stopping...")
    best_params = random_search.best_params_
    
    final_lgbm = LGBMClassifier(
        n_estimators=1000,
        scale_pos_weight=scale_pos_weight,
        random_state=config.RANDOM_STATE,
        n_jobs=-1,
        verbose=-1,
        **best_params
    )
    
    final_lgbm.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[early_stopping(stopping_rounds=20)]
    )
    
    training_time = time.time() - start_time
    logger.info("Model training completed.")
    
    # Baseline performance
    y_prob = final_lgbm.predict_proba(X_test)[:, 1]
    y_pred = final_lgbm.predict(X_test)
    base_f1 = f1_score(y_test, y_pred, zero_division=0)
    base_roc = roc_auc_score(y_test, y_prob)
    logger.info(f"Baseline - ROC: {base_roc:.6f}, F1: {base_f1:.6f}")
    
    # Threshold Optimization
    precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
    fscore = (2 * precision * recall) / (precision + recall + 1e-10)
    best_idx = np.argmax(fscore)
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    
    y_pred_thresh = (y_prob >= best_threshold).astype(int)
    thresh_f1 = f1_score(y_test, y_pred_thresh, zero_division=0)
    logger.info(f"Optimized Threshold ({best_threshold:.4f}) - F1: {thresh_f1:.6f}")
    
    # Select best model
    if thresh_f1 > base_f1:
        final_model = ThresholdOptimizedModel(final_lgbm, best_threshold)
        logger.info("Selected Threshold-Optimized model.")
    else:
        final_model = final_lgbm
        logger.info("Selected baseline model.")
    
    metrics = evaluate_model(final_model, X_test, y_test, model_name="LightGBM", training_time=training_time)
    logger.info(f"Evaluation metrics: {metrics}")
    
    lgbm_model_path = config.SAVED_MODELS_DIR / "lightgbm_model.pkl"
    logger.info(f"Saving trained model to {lgbm_model_path}")
    joblib.dump(final_model, lgbm_model_path)
    
    try:
        X_sample = X_test.sample(n=min(1000, len(X_test)), random_state=42)
        if isinstance(final_model, ThresholdOptimizedModel):
             shap_explainer.generate_ensemble_shap(final_model, "LightGBM", X_sample)
        else:
             shap_explainer.generate_tree_shap(final_model, "LightGBM", X_sample)
    except Exception as e:
        logger.warning(f"Could not generate SHAP for LightGBM: {e}")
        
    logger.info("=== LightGBM Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
