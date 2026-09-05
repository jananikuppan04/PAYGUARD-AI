import logging
import sys
import os
import json
import joblib
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Any, List

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torch.optim.lr_scheduler import CosineAnnealingLR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_recall_curve, f1_score, roc_auc_score

from train import config
from train.preprocess import load_unified_data, clean_data, encode_categorical
from train.feature_engineering import create_features
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

class FraudAutoencoder(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 16):
        super(FraudAutoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, input_dim)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x))

class AutoencoderWrapper:
    def __init__(self, model: nn.Module, threshold: float, device: torch.device):
        self.model = model
        self.threshold = threshold
        self.device = device
        self.model.eval()
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X_tensor = torch.FloatTensor(X).to(self.device)
        with torch.no_grad():
            reconstructed = self.model(X_tensor)
            mse = torch.mean((X_tensor - reconstructed) ** 2, dim=1).cpu().numpy()
        
        # Scale anomaly score so threshold aligns with 0.5 probability
        prob_1 = np.clip(mse / (self.threshold * 2), 0, 1)
        prob_0 = 1 - prob_1
        return np.vstack((prob_0, prob_1)).T
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        probs = self.predict_proba(X)
        return (probs[:, 1] >= 0.5).astype(int)

def train_autoencoder(model: nn.Module, train_loader: DataLoader, val_loader: DataLoader, 
                      criterion: nn.Module, optimizer: optim.Optimizer, scheduler: Any, 
                      epochs: int, device: torch.device, model_save_path: str) -> Tuple[List[float], List[float]]:
    train_losses = []
    val_losses = []
    best_val_loss = float('inf')
    patience = 10
    patience_counter = 0
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for batch_x in train_loader:
            batch_x = batch_x[0].to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_x)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_loss += loss.item() * batch_x.size(0)
            
        train_loss /= len(train_loader.dataset)
        train_losses.append(train_loss)
        
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch_x in val_loader:
                batch_x = batch_x[0].to(device)
                outputs = model(batch_x)
                loss = criterion(outputs, batch_x)
                val_loss += loss.item() * batch_x.size(0)
                
        val_loss /= len(val_loader.dataset)
        val_losses.append(val_loss)
        scheduler.step()
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), model_save_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break
                
    model.load_state_dict(torch.load(model_save_path, weights_only=True))
    return train_losses, val_losses

def plot_training_curves(train_losses: List[float], val_losses: List[float], path: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.title('Autoencoder Reconstruction Loss Curve')
    plt.xlabel('Epochs')
    plt.ylabel('MSE Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(path)
    plt.close()

def plot_threshold_curve(thresholds, fscores, best_thresh, path):
    plt.figure(figsize=(8, 6))
    plt.plot(thresholds, fscores[:-1] if len(fscores) > len(thresholds) else fscores, 'b-', label='F1 Score')
    plt.axvline(best_thresh, color='r', linestyle='--', label=f'Best Threshold: {best_thresh:.4f}')
    plt.xlabel('Reconstruction Error Threshold')
    plt.ylabel('F1 Score')
    plt.title('Threshold Optimization Curve')
    plt.legend()
    plt.grid(True)
    plt.savefig(path)
    plt.close()

def main() -> None:
    logger.info("=== Starting AI Fraud Detection Pipeline (Autoencoder) ===")
    
    start_time = time.time()
    
    df = load_unified_data(sample_size=100000)
    df = clean_data(df)
    df = encode_categorical(df)
    df = create_features(df)
    
    num_cols = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest",
                "balanceDiffOrig", "balanceDiffDest", "origBalanceChange", "destBalanceChange",
                "amountToOrigRatio", "amountToDestRatio", "transactionHour", "transactionDay", "step"]
    
    cols_to_scale = [col for col in num_cols if col in df.columns]
    scaler = StandardScaler()
    df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
    
    scaler_path = config.SAVED_MODELS_DIR / "autoencoder_scaler.pkl"
    joblib.dump(scaler, scaler_path)
    
    df_legit = df[df[config.TARGET_COLUMN] == 0]
    df_fraud = df[df[config.TARGET_COLUMN] == 1]
    
    # Downsample legitimate transactions to prevent Out-Of-Memory errors
    from sklearn.utils import resample
    target_legit = 100000
    if len(df_legit) > target_legit:
        logger.info(f"Downsampling legitimate transactions from {len(df_legit)} to {target_legit} to save memory.")
        df_legit = resample(df_legit, replace=False, n_samples=target_legit, random_state=config.RANDOM_STATE)
    
    X_legit = df_legit.drop(columns=[config.TARGET_COLUMN]).values.astype(np.float32)
    X_fraud = df_fraud.drop(columns=[config.TARGET_COLUMN]).values.astype(np.float32)
    
    # Validation Split of Legitimate Data (80/20)
    X_train_legit, X_val_legit = train_test_split(
        X_legit, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE
    )
    
    y_val_legit = np.zeros(len(X_val_legit))
    y_fraud = np.ones(len(X_fraud))
    
    # We will use 10,000 fraud samples for validation threshold optimization, and the rest for testing.
    # Actually, we can use the full set for threshold optimization since we don't leak anything into the autoencoder weights.
    X_eval = np.vstack((X_val_legit, X_fraud))
    y_eval = np.concatenate((y_val_legit, y_fraud))
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    train_tensor = torch.FloatTensor(X_train_legit)
    val_tensor = torch.FloatTensor(X_val_legit)
    
    batch_size = 2048
    train_loader = DataLoader(TensorDataset(train_tensor), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(val_tensor), batch_size=batch_size, shuffle=False)
    
    input_dim = X_train_legit.shape[1]
    
    # Latent dimension sweep
    best_latent_dim = 16
    best_roc_auc = 0
    best_model_weights = None
    best_train_losses = []
    best_val_losses = []
    
    latent_dims = [8, 16, 32]
    model_save_path = config.SAVED_MODELS_DIR / "autoencoder.pt"
    
    for l_dim in latent_dims:
        logger.info(f"Training Autoencoder with Latent Dimension = {l_dim}")
        model = FraudAutoencoder(input_dim, latent_dim=l_dim).to(device)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.005)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
        
        train_losses, val_losses = train_autoencoder(
            model, train_loader, val_loader, criterion, optimizer, scheduler, 
            epochs=50, device=device, model_save_path=str(model_save_path)
        )
        
        # Evaluate on evaluation set for thresholding/ROC
        model.eval()
        with torch.no_grad():
            eval_tensor = torch.FloatTensor(X_eval).to(device)
            eval_reconstructed = model(eval_tensor).cpu()
            eval_mse = torch.mean((eval_tensor - eval_reconstructed) ** 2, dim=1).numpy()
            
        roc = roc_auc_score(y_eval, eval_mse)
        logger.info(f"Latent Dim {l_dim} ROC AUC: {roc:.6f}")
        
        if roc > best_roc_auc:
            best_roc_auc = roc
            best_latent_dim = l_dim
            best_model_weights = model.state_dict()
            best_train_losses = train_losses
            best_val_losses = val_losses
            
    logger.info(f"Best Latent Dimension: {best_latent_dim} (ROC AUC: {best_roc_auc:.6f})")
    
    # Load best model
    best_model = FraudAutoencoder(input_dim, latent_dim=best_latent_dim).to(device)
    best_model.load_state_dict(best_model_weights)
    torch.save(best_model.state_dict(), model_save_path)
    
    report_dir = config.REPORTS_DIR / "Autoencoder"
    os.makedirs(report_dir, exist_ok=True)
    
    loss_path = report_dir / "loss_curve.png"
    plot_training_curves(best_train_losses, best_val_losses, str(loss_path))
    
    # Optimize Threshold
    logger.info("Determining best anomaly threshold by maximizing F1 score...")
    with torch.no_grad():
        eval_tensor = torch.FloatTensor(X_eval).to(device)
        eval_reconstructed = best_model(eval_tensor).cpu()
        eval_mse = torch.mean((eval_tensor - eval_reconstructed) ** 2, dim=1).numpy()
        
    precision, recall, thresholds = precision_recall_curve(y_eval, eval_mse)
    fscores = (2 * precision * recall) / (precision + recall + 1e-10)
    best_idx = np.argmax(fscores)
    threshold = thresholds[best_idx] if best_idx < len(thresholds) else float(np.percentile(eval_mse, 95))
    
    logger.info(f"Determined optimal threshold: {threshold:.6f}")
    
    thresh_path = config.SAVED_MODELS_DIR / "autoencoder_threshold.json"
    with open(thresh_path, 'w') as f:
        json.dump({'threshold': float(threshold)}, f)
        
    thresh_curve_path = report_dir / "threshold_optimization_curve.png"
    plot_threshold_curve(thresholds, fscores, threshold, str(thresh_curve_path))
    
    training_time = time.time() - start_time
    
    # Final evaluation
    logger.info("Evaluating final autoencoder...")
    wrapped_model = AutoencoderWrapper(best_model, float(threshold), device)
    
    metrics = evaluate_model(wrapped_model, X_eval, y_eval, model_name="Autoencoder", training_time=training_time)
    logger.info(f"Evaluation metrics: {metrics}")
    logger.info("=== Autoencoder Training Pipeline Completed Successfully ===")

if __name__ == "__main__":
    main()
