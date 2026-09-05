import logging
import sys
import os
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt

from train import config
from train.preprocess import load_unified_data, clean_data, encode_categorical
from train.feature_engineering import create_features, normalize_features

from sklearn.base import BaseEstimator, ClassifierMixin

class ThresholdOptimizedModel(BaseEstimator, ClassifierMixin):
    pass

try:
    from train.train_autoencoder import FraudAutoencoder
    from train.train_ensemble import StackingEnsemble
except ImportError:
    pass

# Setup local specific paths
SHAP_LOG_PATH = config.LOGS_DIR / "shap_explainer.log"
SHAP_REPORTS_DIR = config.REPORTS_DIR / "shap"
os.makedirs(SHAP_REPORTS_DIR, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(SHAP_LOG_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def generate_tree_shap(model, model_name: str, X: pd.DataFrame):
    """Generates SHAP values and plots for tree-based models."""
    logger.info(f"Generating SHAP plots for {model_name}...")
    
    if hasattr(model, 'model'):
        model = model.model
        
    # Use TreeExplainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    
    # Handle lightgbm/rf returning list of shap values for multiclass/binary
    if isinstance(shap_values, list):
        shap_values = shap_values[1] # Take positive class
    elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
        shap_values = shap_values[:, :, 1]
        
    # 1. Summary Plot
    plt.figure()
    shap.summary_plot(shap_values, X, show=False)
    plt.tight_layout()
    plt.savefig(SHAP_REPORTS_DIR / f"{model_name}_summary_plot.png")
    plt.close()
    
    # 2. Bar Plot
    plt.figure()
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig(SHAP_REPORTS_DIR / f"{model_name}_bar_plot.png")
    plt.close()
    
    # 3. Waterfall Plot (for a single instance)
    plt.figure()
    # TreeExplainer might not return an Explanation object natively in all versions,
    # so we create one or use the explainer directly if supported.
    # To be safe across versions, force plot is safer for single instance if Explanation is not formed,
    # but waterfall is requested. We use Explanation object.
    exp = shap.Explanation(values=shap_values[0], base_values=explainer.expected_value, data=X.iloc[0].values, feature_names=X.columns)
    if isinstance(explainer.expected_value, (list, np.ndarray)):
        exp.base_values = explainer.expected_value[1] # positive class
        
    try:
        shap.waterfall_plot(exp, show=False)
        plt.tight_layout()
        plt.savefig(SHAP_REPORTS_DIR / f"{model_name}_waterfall_plot.png")
        plt.close()
    except Exception as e:
        logger.warning(f"Could not generate waterfall plot for {model_name}: {e}")
        
    # 4. Dependence Plot (most important feature)
    try:
        # Find most important feature
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        top_feature_idx = np.argmax(mean_abs_shap)
        top_feature = X.columns[top_feature_idx]
        
        plt.figure()
        shap.dependence_plot(top_feature, shap_values, X, show=False)
        plt.tight_layout()
        plt.savefig(SHAP_REPORTS_DIR / f"{model_name}_dependence_plot.png")
        plt.close()
    except Exception as e:
        logger.warning(f"Could not generate dependence plot for {model_name}: {e}")
        
    # 5. Force Plot
    try:
        # We save force plot as HTML since it's interactive, or as matplotlib if possible
        shap.force_plot(
            explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value, 
            shap_values[0], 
            X.iloc[0], 
            matplotlib=True, 
            show=False
        )
        plt.tight_layout()
        plt.savefig(SHAP_REPORTS_DIR / f"{model_name}_force_plot.png")
        plt.close()
    except Exception as e:
        logger.warning(f"Could not generate force plot for {model_name}: {e}")
        
    # Generate Feature Ranking
    ranking = pd.DataFrame({
        'Feature': X.columns,
        'Importance (Mean Abs SHAP)': np.abs(shap_values).mean(axis=0)
    }).sort_values(by='Importance (Mean Abs SHAP)', ascending=False)
    
    ranking.to_csv(SHAP_REPORTS_DIR / f"{model_name}_feature_ranking.csv", index=False)
    logger.info(f"Saved feature ranking for {model_name}")

def generate_ensemble_shap(ensemble, model_name: str, X: pd.DataFrame):
    """Generates SHAP for black-box ensemble using KernelExplainer."""
    logger.info(f"Generating SHAP plots for {model_name} (KernelExplainer)...")
    
    # KernelExplainer is slow, use a small background dataset and small sample for explanation
    X_background = shap.kmeans(X, 10)
    
    def predict_wrapper(data):
        # Data comes in as numpy array, ensemble expects DataFrame
        df_data = pd.DataFrame(data, columns=X.columns)
        return ensemble.predict_proba(df_data)[:, 1]
        
    explainer = shap.KernelExplainer(predict_wrapper, X_background)
    shap_values = explainer.shap_values(X.iloc[:50]) # Explain only 50 instances to save time
    
    X_sample = X.iloc[:50]
    
    plt.figure()
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.tight_layout()
    plt.savefig(SHAP_REPORTS_DIR / f"{model_name}_summary_plot.png")
    plt.close()
    
    plt.figure()
    shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig(SHAP_REPORTS_DIR / f"{model_name}_bar_plot.png")
    plt.close()
    
    ranking = pd.DataFrame({
        'Feature': X.columns,
        'Importance (Mean Abs SHAP)': np.abs(shap_values).mean(axis=0)
    }).sort_values(by='Importance (Mean Abs SHAP)', ascending=False)
    
    ranking.to_csv(SHAP_REPORTS_DIR / f"{model_name}_feature_ranking.csv", index=False)
    logger.info(f"Saved feature ranking for {model_name}")

def main() -> None:
    logger.info("=== Starting AI Fraud Detection Pipeline (SHAP Explainer) ===")
    
    # 1. Load Data
    try:
        logger.info("Loading and preparing sample data for SHAP...")
        df = load_unified_data(sample_size=2000)
        df = clean_data(df)
        df = encode_categorical(df)
        df = create_features(df)
        num_cols = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
        df = normalize_features(df, num_cols)
        
        # Take a small sample (e.g., 500 rows) for SHAP generation to ensure reasonable execution time
        df_sample = df.sample(n=500, random_state=config.RANDOM_STATE)
        X = df_sample.drop(columns=[config.TARGET_COLUMN])
        
    except Exception as e:
        logger.error(f"Error in data preprocessing: {e}")
        sys.exit(1)
        
    # 2. Load Models and Generate Explanations
    try:
        # XGBoost
        logger.info("Loading XGBoost...")
        xgb_model = joblib.load(config.SAVED_MODELS_DIR / "xgboost_model.pkl")
        generate_tree_shap(xgb_model, "xgboost", X)
        
        # LightGBM
        logger.info("Loading LightGBM...")
        lgbm_model = joblib.load(config.SAVED_MODELS_DIR / "lightgbm_model.pkl")
        generate_tree_shap(lgbm_model, "lightgbm", X)
        
        # Random Forest
        logger.info("Loading Random Forest...")
        rf_model = joblib.load(config.SAVED_MODELS_DIR / "randomforest.pkl")
        generate_tree_shap(rf_model, "randomforest", X)
        
        # Ensemble
        logger.info("Loading Ensemble...")
        ensemble_model = joblib.load(config.SAVED_MODELS_DIR / "ensemble.pkl")
        generate_ensemble_shap(ensemble_model, "ensemble", X)
        
    except Exception as e:
        logger.error(f"Error during SHAP generation: {e}")
        sys.exit(1)
        
    logger.info("=== SHAP Explainer Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
