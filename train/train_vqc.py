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

# Qiskit imports
from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from qiskit_aer.primitives import Sampler
from qiskit_algorithms.optimizers import COBYLA
from qiskit_machine_learning.algorithms import VQC

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

class VQCWrapper:
    def __init__(self, model: VQC):
        self.model = model
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        
        preds = self.model.predict(X)
        probs = np.zeros((len(preds), 2))
        probs[np.arange(len(preds)), preds.astype(int)] = 1.0
        return probs
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

def plot_loss_curve(loss_values: list, path: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(loss_values, label='VQC Objective Loss')
    plt.title('Variational Quantum Classifier Loss')
    plt.xlabel('Iterations')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(path)
    plt.close()

def main() -> None:
    logger.info("=== Starting AI Fraud Detection Pipeline (Variational Quantum Classifier) ===")
    
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
        
    target_total = 50 # Quick retrain to recover pickle
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
    report_dir = config.REPORTS_DIR / "VQC"
    os.makedirs(report_dir, exist_ok=True)
    
    feature_map = ZZFeatureMap(feature_dimension=pca_components, reps=2, entanglement='linear')
    ansatz = RealAmplitudes(num_qubits=pca_components, reps=2)
    optimizer = COBYLA(maxiter=150)
    
    circuit_path = report_dir / "vqc_circuit.png"
    try:
        circuit = feature_map.compose(ansatz)
        fig = circuit.decompose().draw(output='mpl')
        fig.savefig(str(circuit_path))
        logger.info(f"Saved quantum circuit visualization to {circuit_path}")
    except Exception as e:
        logger.error(f"Failed to draw quantum circuit: {e}")

    sampler = Sampler()
    
    objective_func_vals = []
    def callback_graph(weights, obj_func_eval):
        objective_func_vals.append(obj_func_eval)
        
    logger.info("Initializing VQC...")
    vqc = VQC(
        feature_map=feature_map,
        ansatz=ansatz,
        optimizer=optimizer,
        callback=callback_graph
    )
    
    logger.info("Training Variational Quantum Classifier...")
    try:
        # qiskit-machine-learning's VQC usually expects categorical labels encoded, but 0/1 is handled well
        vqc.fit(X_train, y_train)
    except Exception as e:
        logger.error(f"Error during model training: {e}")
        sys.exit(1)
        
    training_time = time.time() - start_time
    logger.info("Training completed.")
    
    loss_path = report_dir / "loss_curve.png"
    plot_loss_curve(objective_func_vals, str(loss_path))
    logger.info(f"Saved VQC loss curve to {loss_path}")
    
    logger.info("Evaluating...")
    wrapped_model = VQCWrapper(vqc)
    
    metrics = evaluate_model(wrapped_model, X_test, y_test, model_name="VQC", training_time=training_time)
    logger.info(f"Evaluation metrics: {metrics}")
    
    try:
        import dill
        model_save_path = config.SAVED_MODELS_DIR / "vqc.pkl"
        pipeline = {
            'scaler': scaler,
            'pca': pca,
            'model': vqc
        }
        with open(model_save_path, 'wb') as f:
            dill.dump(pipeline, f)
        logger.info(f"Saved VQC pipeline to {model_save_path}")
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        sys.exit(1)
        
    logger.info("=== VQC Training Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
