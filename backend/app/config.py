"""
PayGuard AI — Centralized Configuration
Defines paths for datasets, artifacts, model weights, and authentication settings.
All paths are relative to the payguard-ai project root, ensuring 100% portability.
"""
import os
from pathlib import Path

# Base Paths
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Data & Artifacts
DATA_DIR = BACKEND_DIR / "data"
ARTIFACTS_DIR = BACKEND_DIR / "artifacts"
SAVED_MODELS_DIR = ARTIFACTS_DIR / "saved_models"

# Specific File Locations
PAYMENTS_DB_PATH = DATA_DIR / "payments_db.json"
USERS_DB_PATH = DATA_DIR / "users_db.json"
PAYSIM_DATA_PATH = DATA_DIR / "paysim.csv"

# Trained ML Model Paths
LIGHTGBM_MODEL_PATH = SAVED_MODELS_DIR / "lightgbm_model.pkl"
LABEL_ENCODER_PATH = SAVED_MODELS_DIR / "label_encoder.pkl"
XGBOOST_MODEL_PATH = SAVED_MODELS_DIR / "xgboost_model.pkl"
AUTOENCODER_MODEL_PATH = SAVED_MODELS_DIR / "autoencoder.pt"
AUTOENCODER_SCALER_PATH = SAVED_MODELS_DIR / "autoencoder_scaler.pkl"
METRICS_REPORT_PATH = SAVED_MODELS_DIR / "metrics.json"

# Auth Settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "payguard-ai-secret-key-quantum-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))

# Server Settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
