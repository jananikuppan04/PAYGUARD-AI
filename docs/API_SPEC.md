# PayGuard AI — API Specification

Base URL: `http://localhost:8000`

---

## 1. System Endpoints

### `GET /health`
Returns system status, service version, and whether the pretrained LightGBM model is active.
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "PayGuard AI Engine",
    "version": "2.1.0",
    "ml_model_loaded": true,
    "model_source": "backend/artifacts/saved_models/lightgbm_model.pkl"
  }
  ```

### `GET /model-info`
Returns provenance and evaluation benchmarks for the integrated ML model and PaySim dataset.

---

## 2. Authentication Endpoints

### `POST /api/v1/auth/signup`
Registers a new merchant account.
- **Body**: `{"email": "merchant@company.com", "password": "securePassword", "merchant_name": "Acme Inc."}`
- **Response**: `{"access_token": "...", "token_type": "bearer", "expires_in": 86400, "user": {...}}`

### `POST /api/v1/auth/login`
Authenticates a merchant. Default demo credentials:
- **Email**: `merchant@payguard.ai`
- **Password**: `demoPassword123`

### `GET /api/v1/auth/me`
Requires `Authorization: Bearer <token>`. Returns authenticated merchant user profile.

---

## 3. Payment Intelligence Endpoints

### `GET /api/payments`
Lists payment records with filtering by `status`, `category`, `search`, `limit`, and `skip`.

### `POST /api/payments/simulate`
Simulates a new incoming payment event, performs instant failure diagnosis, ML risk evaluation, and agent recommendation.

### `POST /api/recovery/execute/{transaction_id}`
Executes bounded recovery using the recommended strategy or an authorized override.

### `POST /api/assistant/query`
Processes natural language merchant questions with grounded evidence retrieval and citations.

### `GET /api/evaluation`
Returns complete empirical metrics (Accuracy, Recall, Precision, ROC-AUC, PR-AUC, Confusion Matrix, and Agent Groundedness).
