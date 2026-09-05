import logging
import sys
import os
import joblib
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Any

from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

# Qiskit imports
from qiskit.circuit.library import ZZFeatureMap
from qiskit_aer.primitives import Sampler
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit_machine_learning.algorithms import QSVC

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

class QSVCWrapper:
    def __init__(self, model: QSVC):
        self.model = model
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        # QSVC predict_proba is not directly available, use decision function if possible, otherwise pseudo-probs
        if hasattr(self.model, "decision_function"):
            scores = self.model.decision_function(X)
            # Scale to 0-1
            s_min, s_max = scores.min(), scores.max()
            if s_max > s_min:
                scores = (scores - s_min) / (s_max - s_min)
            prob_1 = scores
            prob_0 = 1 - prob_1
            return np.vstack((prob_0, prob_1)).T
        else:
            preds = self.model.predict(X)
            probs = np.zeros((len(preds), 2))
            probs[np.arange(len(preds)), preds.astype(int)] = 1.0
            return probs
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

def plot_kernel_matrix(kernel_matrix: np.ndarray, path: str):
    plt.figure(figsize=(8, 6))
    plt.imshow(kernel_matrix, cmap='viridis', origin='lower')
    plt.colorbar(label='Kernel Value')
    plt.title('Quantum Kernel Matrix')
    plt.savefig(path)
    plt.close()

def main() -> None:
    logger.info("=== Starting AI Fraud Detection Pipeline (Quantum Support Vector Classifier) ===")
    
    start_time = time.time()
    
    try:
        df = load_unified_data(sample_size=2000)
        df = clean_data(df)
        df = encode_categorical(df)
        df = create_features(df)
        num_cols = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
        df = normalize_features(df, num_cols)
    except Exception as e:
        logger.error(f"Error in data preprocessing: {e}")
        sys.exit(1)
        
    target_total = 50 # Quick retrain to recover metrics
    logger.info(f"Sampling dataset: Stratified sample of {target_total} transactions.")
    
    frauds = df[df[config.TARGET_COLUMN] == 1]
    non_frauds = df[df[config.TARGET_COLUMN] == 0]
    
    n_frauds = min(len(frauds), target_total // 2) # Force 50% fraud for better learning
    n_non_frauds = target_total - n_frauds
    
    sample_df = pd.concat([
        frauds.sample(n=n_frauds, random_state=config.RANDOM_STATE),
        non_frauds.sample(n=n_non_frauds, random_state=config.RANDOM_STATE)
    ]).sample(frac=1, random_state=config.RANDOM_STATE) # Shuffle
    
    X_sample = sample_df.drop(columns=[config.TARGET_COLUMN])
    y_sample = sample_df[config.TARGET_COLUMN]
    
    logger.info(f"Sampled dataset shape: X={X_sample.shape}, y={y_sample.shape}")
    logger.info(f"Fraud count in sample: {y_sample.sum()}")
    
    # Dimensionality Reduction (PCA to 6 components)
    pca_components = 6
    logger.info(f"Applying PCA to reduce features to {pca_components} components...")
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_sample)
    
    pca = PCA(n_components=pca_components, random_state=config.RANDOM_STATE)
    X_pca = pca.fit_transform(X_scaled)
    
    logger.info(f"Explained variance ratio by {pca_components} components: {np.sum(pca.explained_variance_ratio_):.4f}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_pca, y_sample.values, 
        test_size=0.2, 
        stratify=y_sample.values, 
        random_state=config.RANDOM_STATE
    )
    
    logger.info("Initializing Quantum Components...")
    report_dir = config.REPORTS_DIR / "QSVC"
    os.makedirs(report_dir, exist_ok=True)
    
    feature_map = ZZFeatureMap(feature_dimension=pca_components, reps=2, entanglement='linear')
    circuit_path = report_dir / "zz_feature_map_circuit.png"
    try:
        fig = feature_map.decompose().draw(output='mpl')
        fig.savefig(str(circuit_path))
        logger.info(f"Saved quantum circuit visualization to {circuit_path}")
    except Exception as e:
        logger.error(f"Failed to draw quantum circuit: {e}")

    sampler = Sampler()
    quantum_kernel = FidelityQuantumKernel(feature_map=feature_map)
    
    logger.info("Evaluating Kernel Matrix on subset...")
    try:
        # Plot kernel matrix for a small subset
        X_subset = X_train[:50]
        k_matrix = quantum_kernel.evaluate(x_vec=X_subset)
        km_path = report_dir / "kernel_matrix.png"
        plot_kernel_matrix(k_matrix, str(km_path))
        logger.info(f"Saved kernel matrix visualization to {km_path}")
    except Exception as e:
        logger.warning(f"Failed to generate kernel matrix plot: {e}")
    
    logger.info("Training Quantum Support Vector Classifier...")
    qsvc = QSVC(quantum_kernel=quantum_kernel)
    qsvc.fit(X_train, y_train)
    
    training_time = time.time() - start_time
    logger.info("Training completed.")
    
    logger.info("Evaluating...")
    wrapped_model = QSVCWrapper(qsvc)
    
    metrics = evaluate_model(wrapped_model, X_test, y_test, model_name="QSVC", training_time=training_time)
    logger.info(f"Evaluation metrics: {metrics}")
    
    try:
        model_save_path = config.SAVED_MODELS_DIR / "qsvc.pkl"
        pipeline = {
            'scaler': scaler,
            'pca': pca,
            'model': qsvc
        }
        joblib.dump(pipeline, model_save_path)
        logger.info(f"Saved QSVC pipeline to {model_save_path}")
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        sys.exit(1)
        
    logger.info("=== QSVC Training Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
