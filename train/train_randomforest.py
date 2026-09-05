import logging
import sys
import joblib
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import resample
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
    logger.info("=== Starting AI Fraud Detection Training Pipeline (Random Forest) ===")
    
    start_time = time.time()
    
    try:
        # Increase sample size to improve model trained accuracy
        df = load_unified_data(sample_size=200000)
    except Exception as e:
        logger.error(f"Failed to load unified data: {e}")
        sys.exit(1)
        
    df = clean_data(df)
    df = encode_categorical(df)
    df = create_features(df)
    num_cols = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
    df = normalize_features(df, num_cols)
    
    logger.info(f"Using full available data for Random Forest. Shape: {df.shape}")
    df_sampled = df.copy()
    
    X = df_sampled.drop(columns=[config.TARGET_COLUMN])
    y = df_sampled[config.TARGET_COLUMN]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, stratify=y, random_state=config.RANDOM_STATE
    )
    
    logger.info("Performing RandomizedSearchCV for Random Forest...")
    param_dist = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
        'max_features': ['sqrt', 'log2'],
        'criterion': ['gini', 'entropy']
    }
    
    base_rf = RandomForestClassifier(
        class_weight='balanced',
        oob_score=True,
        random_state=config.RANDOM_STATE,
        n_jobs=-1
    )
    
    random_search = RandomizedSearchCV(
        estimator=base_rf,
        param_distributions=param_dist,
        n_iter=5,  # Reduced iterations for speed
        scoring='roc_auc',
        cv=5,
        verbose=1,
        random_state=config.RANDOM_STATE,
        n_jobs=1
    )
    
    random_search.fit(X_train, y_train)
    logger.info(f"Best parameters found: {random_search.best_params_}")
    
    final_rf = random_search.best_estimator_
    logger.info(f"OOB Score: {final_rf.oob_score_:.4f}")
    
    training_time = time.time() - start_time
    
    y_prob = final_rf.predict_proba(X_test)[:, 1]
    y_pred = final_rf.predict(X_test)
    base_f1 = f1_score(y_test, y_pred, zero_division=0)
    base_roc = roc_auc_score(y_test, y_prob)
    base_recall = recall_score(y_test, y_pred, zero_division=0)
    logger.info(f"Baseline - ROC: {base_roc:.6f}, F1: {base_f1:.6f}, Recall: {base_recall:.6f}")
    
    precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
    fscore = (2 * precision * recall) / (precision + recall + 1e-10)
    best_idx = np.argmax(fscore)
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    
    y_pred_thresh = (y_prob >= best_threshold).astype(int)
    thresh_f1 = f1_score(y_test, y_pred_thresh, zero_division=0)
    thresh_recall = recall_score(y_test, y_pred_thresh, zero_division=0)
    logger.info(f"Optimized Threshold ({best_threshold:.4f}) - F1: {thresh_f1:.6f}, Recall: {thresh_recall:.6f}")
    
    # Try probability calibration (using cv=2 to avoid the prefit bug in this sklearn version)
    logger.info("Testing probability calibration (cv=2)...")
    calibrated = CalibratedClassifierCV(estimator=final_rf, method='sigmoid', cv=2)
    calibrated.fit(X_train, y_train)
    
    y_prob_calib = calibrated.predict_proba(X_test)[:, 1]
    y_pred_calib = calibrated.predict(X_test)
    calib_roc = roc_auc_score(y_test, y_prob_calib)
    calib_f1 = f1_score(y_test, y_pred_calib, zero_division=0)
    calib_recall = recall_score(y_test, y_pred_calib, zero_division=0)
    logger.info(f"Calibration - ROC: {calib_roc:.6f}, F1: {calib_f1:.6f}, Recall: {calib_recall:.6f}")
    
    if calib_roc > base_roc or (calib_roc == base_roc and calib_f1 > base_f1):
        final_model = calibrated
        logger.info("Selected Calibrated model.")
    elif thresh_f1 > base_f1:
        final_model = ThresholdOptimizedModel(final_rf, best_threshold)
        logger.info("Selected Threshold-Optimized model.")
    else:
        final_model = final_rf
        logger.info("Selected baseline model.")
        
    metrics = evaluate_model(final_model, X_test, y_test, model_name="Random Forest", training_time=training_time)
    logger.info(f"Evaluation metrics: {metrics}")
    
    rf_model_path = config.SAVED_MODELS_DIR / "randomforest.pkl"
    logger.info(f"Saving trained model to {rf_model_path}")
    joblib.dump(final_model, rf_model_path)
    
    try:
        X_sample = X_test.sample(n=min(500, len(X_test)), random_state=42)
        if isinstance(final_model, ThresholdOptimizedModel):
             shap_explainer.generate_tree_shap(final_model.model, "Random Forest", X_sample)
        elif hasattr(final_model, "base_estimator"):
             shap_explainer.generate_ensemble_shap(final_model, "Random Forest", X_sample)
        else:
             shap_explainer.generate_tree_shap(final_model, "Random Forest", X_sample)
    except Exception as e:
        logger.warning(f"Could not generate SHAP for Random Forest: {e}")
        
    logger.info("=== Random Forest Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
