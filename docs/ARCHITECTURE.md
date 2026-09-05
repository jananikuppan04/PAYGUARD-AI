# PayGuard AI — System Architecture & Design

> **Razorpay AI Builder 2026 — Track 3: AI Revenue Recovery**

PayGuard AI is an autonomous, explainable payment failure intelligence platform. It bridges machine learning risk prediction with policy-bounded recovery execution to maximize recovered merchant revenue.

---

## 1. High-Level Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        React 18 + Vite Frontend                        │
│   (Dashboard, Recovery Queue, Analytics, Evaluation, Merchant Copilot) │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ REST / WebSocket
┌────────────────────────────────────▼───────────────────────────────────┐
│                     PayGuard AI Backend (FastAPI)                     │
├──────────────────┬───────────────────┬─────────────────────────────────┤
│  Authentication  │  Payment Routers  │      Merchant Copilot (RAG)     │
│  (JWT + Bcrypt)  │ (CRUD & Simulate) │ (Evidence & Policy Grounding)  │
├──────────────────┴───────────────────┴─────────────────────────────────┤
│                     Decision & Intelligence Layer                      │
│ ┌────────────────────────┐  ┌────────────────────────────────────────┐ │
│ │ Failure Diagnosis      │  │ Risk Engine (LightGBM + Anomaly + SHAP)│ │
│ │ (ISO 8583 Soft/Hard)   │  │ (Pretrained on PaySim 6.36M txns)      │ │
│ └───────────┬────────────┘  └───────────────────┬────────────────────┘ │
│             └─────────────────┬─────────────────┘                      │
│                               ▼                                        │
│             ┌────────────────────────────────────┐                     │
│             │ Recovery Eligibility Guardrails   │                     │
│             └─────────────────┬──────────────────┘                     │
│                               ▼                                        │
│             ┌────────────────────────────────────┐                     │
│             │ Next-Best-Action Recommendation    │                     │
│             │ (Bounded 5-Point Explanation)      │                     │
│             └─────────────────┬──────────────────┘                     │
│                               ▼                                        │
│             ┌────────────────────────────────────┐                     │
│             │ Execution Simulation & Tracking   │                     │
│             └────────────────────────────────────┘                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. ML Risk Model & Dataset Integration

PayGuard AI houses its trained models in `backend/artifacts/saved_models/` and datasets in `backend/data/`:
- **Model**: `lightgbm_model.pkl` (Threshold-Optimized LightGBM classifier).
- **Threshold**: `0.4017` (calibrated for 100% recall so zero fraud transactions slip through).
- **Features**: 16 runtime features dynamically engineered from transaction amount, originator/destination balances, hour, day, velocity, and payment method encoding.
- **Dataset**: `paysim.csv` (6,362,620 transactions), providing real-world balance shifts and realistic class imbalance.

---

## 3. Recovery Decision Hierarchy

1. **Failure Diagnosis**:
   - `51` Insufficient Funds ➔ Customer-Related (Soft decline)
   - `91` System Timeout ➔ Technical Failure (Soft decline)
   - `54` Expired Card ➔ Customer-Related (Soft decline)
   - `05` Do Not Honor ➔ Risk-Related (Hard decline)
   - `FRAUD_HIGH` ➔ Risk Alert (Block immediately)
2. **Eligibility Rules**:
   - Max 3 retry attempts per transaction.
   - Payments with risk score ≥ 75 or categorized as Risk-Related are ineligible for automatic retry.
3. **5-Point Explanation Structure**:
   - *Why failed*
   - *Eligibility rationale*
   - *Action rationale*
   - *Evidence points*
   - *Target metric*
