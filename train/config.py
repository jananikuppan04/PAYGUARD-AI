import os
from typing import Final
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Files
DATA_PATH = DATA_DIR / "paysim.csv"
MODEL_PATH = SAVED_MODELS_DIR / "xgboost_model.pkl"
LABEL_ENCODER_PATH = SAVED_MODELS_DIR / "label_encoder.pkl"
METRICS_PATH = SAVED_MODELS_DIR / "metrics.json"
CLASSIFICATION_REPORT_PATH = REPORTS_DIR / "classification_report.txt"
LOG_PATH = LOGS_DIR / "training.log"

# Plots
CONFUSION_MATRIX_PATH = REPORTS_DIR / "confusion_matrix.png"
ROC_CURVE_PATH = REPORTS_DIR / "roc_curve.png"
PR_CURVE_PATH = REPORTS_DIR / "precision_recall_curve.png"
FEATURE_IMPORTANCE_PATH = REPORTS_DIR / "feature_importance.png"

# Ensure directories exist
for d in [DATA_DIR, MODELS_DIR, SAVED_MODELS_DIR, REPORTS_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# Dataset columns
TARGET_COLUMN = "isFraud"
FEATURES = [
    "type",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "step"
]
IGNORE_COLUMNS = ["nameOrig", "nameDest", "isFlaggedFraud"]

# Training configuration
TEST_SIZE = 0.2
RANDOM_STATE = 42

XGB_PARAMS = {
    "n_estimators": 500,
    "learning_rate": 0.05,
    "max_depth": 6,
    "min_child_weight": 1,
    "gamma": 0,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "tree_method": "hist",
    "eval_metric": "aucpr",
    "random_state": RANDOM_STATE,
    "early_stopping_rounds": 10
}

# ===========================================================================
# Quantum Runtime Configuration
# ===========================================================================
# Switch between "simulator" (local AerSimulator) and "hardware" (IBM Quantum)
# by changing QUANTUM_BACKEND_MODE.  All other settings below only apply when
# mode is "hardware", except QUANTUM_MAX_SHOTS which is used in both modes.
# ===========================================================================

# --- Execution mode --------------------------------------------------------
# Valid values: "simulator" | "hardware"
QUANTUM_BACKEND_MODE: Final[str] = os.getenv(
    "QUANTUM_BACKEND_MODE", "simulator"
)

# --- IBM Quantum authentication --------------------------------------------
# Obtain your token from https://quantum.ibm.com/account
IBM_QUANTUM_TOKEN: Final[str] = os.getenv(
    "IBM_QUANTUM_TOKEN", ""
)

# Channel: "ibm_quantum" (legacy free-tier) or "ibm_cloud"
IBM_QUANTUM_CHANNEL: Final[str] = os.getenv(
    "IBM_QUANTUM_CHANNEL", "ibm_quantum"
)

# Instance (hub/group/project) — only required for ibm_quantum channel
IBM_QUANTUM_INSTANCE: Final[str] = os.getenv(
    "IBM_QUANTUM_INSTANCE", "ibm-q/open/main"
)

# --- Backend selection -----------------------------------------------------
# Leave empty ("") to auto-select the least-busy backend at connect time.
# Examples: "ibm_brisbane", "ibm_osaka", "ibm_sherbrooke"
IBM_QUANTUM_BACKEND_NAME: Final[str] = os.getenv(
    "IBM_QUANTUM_BACKEND_NAME", ""
)

# --- Execution parameters --------------------------------------------------
QUANTUM_MAX_SHOTS: Final[int] = int(os.getenv(
    "QUANTUM_MAX_SHOTS", "4096"
))

# Number of samples to use for quantum models (to keep training times reasonable)
QUANTUM_SAMPLE_SIZE: Final[int] = int(os.getenv(
    "QUANTUM_SAMPLE_SIZE", "500"
))

# Transpiler optimization level: 0 (none) → 3 (heavy)
QUANTUM_OPTIMIZATION_LEVEL: Final[int] = int(os.getenv(
    "QUANTUM_OPTIMIZATION_LEVEL", "1"
))

# Error mitigation resilience level: 0 (none) → 2 (heavy)
QUANTUM_RESILIENCE_LEVEL: Final[int] = int(os.getenv(
    "QUANTUM_RESILIENCE_LEVEL", "1"
))

# --- Job lifecycle ---------------------------------------------------------
# Maximum seconds to wait for a job before cancelling
QUANTUM_JOB_TIMEOUT_SECONDS: Final[int] = int(os.getenv(
    "QUANTUM_JOB_TIMEOUT_SECONDS", "3600"
))

# Seconds between status polls while monitoring a job
QUANTUM_JOB_POLL_INTERVAL_SECONDS: Final[int] = int(os.getenv(
    "QUANTUM_JOB_POLL_INTERVAL_SECONDS", "10"
))

