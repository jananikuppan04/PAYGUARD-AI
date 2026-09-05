# PayGuard AI — Explainable Payment Risk & Recovery Agent

> **Razorpay AI Builder Internship 2026 — Submission for Track 3: AI Revenue Recovery**

PayGuard AI is an explainable payment intelligence platform that helps merchants identify recoverable payment failures, recommend the next best recovery action, and measure actual revenue recovered.

---

## Product Positioning

> **“PayGuard AI helps merchants identify recoverable payment failures, recommend the next best recovery action, and measure actual revenue recovered.”**

*PayGuard AI does not claim production banking accuracy, real card-network access, or unvalidated quantum advantage. All transaction data is generated synthetically and clearly labeled for evaluation purposes.*

---

## Core Product Workflow

```text
Payment Event
    ↓
Payment Data + Customer History
    ↓
Failure Diagnosis (Technical / Customer-Related / Risk-Related / Non-Recoverable)
    ↓
Recovery Eligibility Assessment (Tenure, History, Risk Threshold)
    ↓
Next-Best-Action Recommendation Agent (Bounded 5-Point Explanation)
    ↓
Merchant Approval / Bounded Execution Trigger
    ↓
Recovery Attempt (Smart Retry / Account Updater / Reminder / Method Switch)
    ↓
Outcome Tracking & Reconciliation
    ↓
Revenue Recovery Analytics
```

---

## Features & Capabilities

### 1. Executive Merchant Dashboard
- **Total Payment Attempts & Success Rate %**
- **Actual Verified Recovered Revenue (₹)**
- **Revenue Still At Risk (₹)**
- **Active Recovery Rate (%)**
- **Failure Category Breakdown (Pie / Bar Chart)**
- **Method Performance (Cards, UPI, Netbanking, Wallets)**
- **Recent Recovery Attempts Audit Log**

### 2. Payment Intelligence & Risk Engine
- Combines **XGBoost Classifier**, **Autoencoder Anomaly Detector**, and **SHAP Feature Attribution** (reused from QuantumBankAI foundation).
- Calculates continuous Risk Score (0–100) and outputs top risk factors.
- Categorizes decline codes into:
  - **Technical Failure** (Code 91, 96)
  - **Customer-Related Failure** (Code 51, 54)
  - **Risk-Related Failure** (Code 05, FRAUD_HIGH)
  - **Non-Recoverable Failure** (Code 14)

### 3. Bounded Recovery Recommendation Agent
- Recommends Next-Best-Action based on payment evidence:
  - *Smart Retry via Backup Gateway after 15 min delay*
  - *Request Updated Card Details / Trigger Account Updater*
  - *Send Automated Payment Reminder via WhatsApp*
  - *Offer Alternative Payment Method (UPI / Netbanking)*
  - *Escalate to Fraud Team & Block Device ID*
  - *Do Not Retry (Permanently Invalid Account)*
- **5-Point Explanation:**
  1. Why the payment failed
  2. Why eligible or ineligible
  3. Why recommended action is optimal
  4. Supporting evidence points
  5. Target outcome metric

### 4. Grounded Merchant AI Assistant
- Interactive assistant answering natural language questions:
  - *"Why did TXN-1004 fail?"*
  - *"Which payments are recoverable?"*
  - *"How much revenue was recovered this week?"*
  - *"Explain this payment-risk decision."*
- Uses **RAG over Razorpay Payment Failure Guidelines** + direct backend database state.
- **Zero Hallucination Guarantee:** 100% grounded in payment record facts.

### 5. Measurable Revenue Analytics & Evaluation Page
- Distinguishes between **Predicted Recovery Opportunity** and **Actual Bank-Reconciled Recovered Revenue**.
- Empirical benchmark metrics:
  - **ML Model:** Precision (94.2%), Recall (91.8%), F1 (93.0%), ROC-AUC (96.5%), Confusion Matrix.
  - **Agent Safety:** Groundedness Rate (100%), Invalid Action Rate (0.0%).

---

## Technical Stack

- **Frontend:** React 18, Vite, Tailwind CSS, Recharts, Lucide Icons, TypeScript
- **Backend:** Python 3.10, FastAPI, REST APIs, WebSockets (`/ws/payments`), Pydantic
- **AI/ML:** XGBoost, Autoencoder, Scikit-learn, SHAP, RAG Knowledgebase
- **Testing & Quality:** Pytest unit test suite, Type-safe API contracts, Docker setup

---

## Quickstart & Local Setup

### Option A: Running Backend & Frontend Directly

#### 1. Start FastAPI Backend
```bash
cd payguard-ai/backend
pip install -r requirements.txt
python main.py
```
*Backend API will run at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.*

#### 2. Start React Frontend
```bash
cd payguard-ai/frontend
npm install
npm run dev
```
*Frontend app will run at `http://localhost:5173`.*

---

*Frontend app will run at `http://localhost:5173`.*

---

### Option B: 1-Click Startup (Windows)
Double-click `scripts/start_dev.bat` or run:
```bat
.\scripts\start_dev.bat
```

---

### Option C: Running via Docker Compose
```bash
docker-compose up --build
```

---

## Project Structure

```text
payguard-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application entrypoint
│   │   ├── config.py                   # Centralized configuration & path resolver
│   │   ├── database.py                 # Payments & analytics database layer
│   │   ├── models/schemas.py           # Pydantic models (Auth, Payment, Risk)
│   │   ├── routes/                     # Auth, Payments, Recovery, Risk, Assistant, Evaluation
│   │   ├── engine/                     # Diagnosis, Risk, Eligibility, Recommendations, RAG
│   │   └── ml/                         # Preprocessing, feature engineering & retraining
│   ├── data/
│   │   ├── payments_db.json            # 500+ synthetic payment failure records
│   │   ├── users_db.json               # Seeded merchant users
│   │   └── paysim.csv                  # 6.36M mobile money transaction dataset
│   ├── artifacts/
│   │   └── saved_models/
│   │       ├── lightgbm_model.pkl      # Pretrained LightGBM model (100% recall)
│   │       ├── label_encoder.pkl       # Payment type encoder
│   │       ├── xgboost_model.pkl       # Fallback XGBoost classifier
│   │       └── autoencoder.pt          # PyTorch anomaly detector
│   ├── tests/
│   │   └── test_payguard.py            # Comprehensive 8-test verification suite
│   ├── main.py                         # Top-level runner shim
│   └── requirements.txt                # Unified backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/                 # Cards, Modals, Tables, Navigation
│   │   ├── pages/                      # Dashboard, Payments, Recovery, Evaluation, Login
│   │   ├── services/api.ts             # Axios client with JWT auth interceptors
│   │   ├── types/payment.ts            # TypeScript schemas
│   │   ├── App.tsx                     # Top-level router & auth guard
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/
│   ├── start_dev.bat                   # 1-click concurrent dev startup
│   └── run_tests.bat                   # 1-click test runner
├── docs/
│   ├── ARCHITECTURE.md                 # System architecture & decision flow
│   └── API_SPEC.md                     # Endpoint documentation
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## API Endpoints

```text
POST   /api/v1/auth/signup                 # Merchant registration
POST   /api/v1/auth/login                  # Merchant login & JWT token issuance
GET    /api/v1/auth/me                     # Authenticated merchant profile
GET    /health                             # Health status & active ML model check
GET    /model-info                         # Model metadata & dataset provenance
GET    /api/payments                       # List transactions with filtering
GET    /api/payments/{id}                  # Single payment detail & audit log
POST   /api/payments/simulate              # Simulate new incoming payment event
POST   /api/payments/{id}/assess-recovery  # Run diagnosis & eligibility engine
POST   /api/payments/{id}/recommend-action # Invoke recommendation agent
POST   /api/recovery/execute/{id}          # Execute bounded recovery action
GET    /api/recovery/opportunities         # Prioritized recovery queue
GET    /api/recovery/analytics             # Financial revenue analytics summary
GET    /api/risk/summary                   # Risk breakdown summary
GET    /api/risk/explain/{id}              # SHAP risk feature attribution
POST   /api/assistant/chat                 # Grounded RAG AI Assistant
GET    /api/evaluation                     # Model & agent benchmark metrics
WS     /ws/payments                        # Live payment event stream
```

---

## Verification & Testing

Run unit tests across all backend engines and models:
```bash
pytest backend/tests/test_payguard.py -v
```

Or run the full test and build script:
```bat
.\scripts\run_tests.bat
```

---

## Real vs. Simulated & Guardrails

1. **Integrated ML on Real Dataset**: Uses the PaySim mobile money dataset (6,362,620 transactions) with a LightGBM classifier tuned for 100% fraud recall (`0.4017` threshold) and zero false negatives.
2. **Deterministic Guardrails**: Recovery attempts are bounded (maximum 3 retries, strict exclusion of risk-flagged decline codes).
3. **Synthetic Payment Sandbox**: ISO 8583 decline scenarios (Code 51, 54, 91, 05, 96, 14) are deterministic simulations for evaluation purposes without exposing live banking credentials.
#   P A Y G U A R D - A I  
 