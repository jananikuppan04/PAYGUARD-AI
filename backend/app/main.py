import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure python path can load local backend modules
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from routes.payments import router as payments_router
from routes.recovery import router as recovery_router
from routes.risk import router as risk_router
from routes.assistant import router as assistant_router
from routes.evaluation import router as evaluation_router
from routes.websocket import router as websocket_router
from routes.auth import router as auth_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PayGuardAI")

app = FastAPI(
    title="PayGuard AI — Explainable Payment Risk & Revenue Recovery Agent",
    description=(
        "Backend for PayGuard AI (Razorpay AI Builder 2026, Track 3). "
        "Integrates pre-trained QuantumBankAI LightGBM fraud model (PaySim 6.36M txns), "
        "Payment Failure Diagnosis, Risk Explainability (SHAP), AI Next-Best-Action Agent, "
        "Recovery Execution, and Grounded Merchant Assistant."
    ),
    version="2.1.0"
)

# Enable CORS for React Frontend (Port 5173 / 3000 / Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(payments_router)
app.include_router(recovery_router)
app.include_router(risk_router)
app.include_router(assistant_router)
app.include_router(evaluation_router)
app.include_router(websocket_router)

@app.get("/health", tags=["System"])
async def health_check():
    from engine.risk_engine import lgbm_model, xgb_model
    model_loaded = lgbm_model is not None or xgb_model is not None
    return {
        "status": "healthy",
        "service": "PayGuard AI Engine",
        "version": "2.1.0",
        "ml_model_loaded": model_loaded,
        "model_source": "backend/artifacts/saved_models/lightgbm_model.pkl"
    }

@app.get("/model-info", tags=["System"])
async def model_info():
    return {
        "platform": "PayGuard AI Revenue Recovery Agent",
        "track": "Razorpay AI Builder Track 3 (AI Revenue Recovery)",
        "pretrained_model": {
            "name": "QuantumBankAI LightGBM (ThresholdOptimized)",
            "dataset": "PaySim Mobile Money Fraud Dataset",
            "dataset_rows": 6362620,
            "dataset_features": 11,
            "trained_features": 23,
            "target_column": "isFraud",
            "fraud_ratio_pct": 0.129,
            "test_accuracy": 0.9927,
            "test_recall": 1.0,
            "test_roc_auc": 1.0,
            "test_pr_auc": 1.0,
            "false_negatives": 0,
            "threshold": 0.4017,
            "model_file": "backend/artifacts/saved_models/lightgbm_model.pkl",
            "dataset_file": "backend/data/paysim.csv"
        },
        "pipeline": [
            "Payment Event Input",
            "Feature Engineering (23 engineered features)",
            "QuantumBankAI Pre-trained LightGBM Model",
            "Fraud Probability & Risk Score",
            "Recovery Eligibility Assessment",
            "Next-Best-Action Recommendation",
            "Recovery Execution Engine",
            "Grounded Merchant Assistant (RAG)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

