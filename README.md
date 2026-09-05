# PayGuard AI

### Explainable AI Revenue Recovery Agent

**Detect revenue at risk. Diagnose the cause. Recover money intelligently.**

[![AI Revenue Recovery](https://img.shields.io/badge/Track-AI%20Revenue%20Recovery-111111?style=flat-square)](#) [![Status](https://img.shields.io/badge/Status-Active%20Development-111111?style=flat-square)](#) [![License](https://img.shields.io/badge/License-MIT-111111?style=flat-square)](#)

PayGuard AI is an AI-powered payment intelligence and revenue recovery platform that helps businesses identify payment failures, understand their causes, prioritize recovery opportunities, and execute bounded recovery workflows.

The platform is designed around a measurable agent loop:

> **Detect → Diagnose → Decide → Execute → Verify → Measure → Audit**

Unlike a dashboard that only reports failed payments, PayGuard AI aims to demonstrate how an AI agent can move from identifying a revenue opportunity to taking a controlled recovery action and measuring the financial outcome.

---

## Table of Contents

* [Overview](#overview)
* [Problem Statement](#problem-statement)
* [Solution](#solution)
* [Why AI Revenue Recovery](#why-ai-revenue-recovery)
* [Core Features](#core-features)
* [How the Agent Works](#how-the-agent-works)
* [Dataset and Data Strategy](#dataset-and-data-strategy)
* [Recovery Evaluation](#recovery-evaluation)
* [System Architecture](#system-architecture)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Application Modules](#application-modules)
* [Getting Started](#getting-started)
* [Configuration](#configuration)
* [Usage](#usage)
* [API Overview](#api-overview)
* [Model Evaluation](#model-evaluation)
* [Security and Guardrails](#security-and-guardrails)
* [Demo Workflow](#demo-workflow)
* [Limitations](#limitations)
* [Future Enhancements](#future-enhancements)
* [Contributing](#contributing)
* [License](#license)

---

## Overview

Revenue loss rarely happens in one clean step.

A payment fails, a checkout is abandoned, a subscription payment is declined, or an invoice becomes overdue. Each event creates a potential recovery opportunity, but not every opportunity should receive the same intervention.

PayGuard AI is designed to help answer:

* How much revenue is currently at risk?
* Why did the payment fail?
* Is the transaction eligible for recovery?
* Which intervention is appropriate?
* What recovery action should be executed?
* What happened after the action?
* How much revenue was actually recovered?
* Why were some opportunities stopped or escalated?

The platform combines payment-risk intelligence, explainable AI, recovery policies, and outcome measurement into one workflow.

---

## Problem Statement

Traditional payment monitoring systems often stop at failure detection.

For example:

> Payment failed → Display error → End of workflow

This creates several operational problems:

* Revenue opportunities remain unidentified.
* Payment failures are not prioritized by financial impact.
* Recovery decisions are made manually.
* Retry actions may be inconsistent.
* Recovery attempts may continue without clear stopping rules.
* Businesses cannot easily measure the money recovered.
* There is limited visibility into why an action was recommended or stopped.

PayGuard AI addresses this gap by connecting **payment intelligence to bounded recovery execution**.

---

## Solution

PayGuard AI transforms payment failure events into actionable recovery opportunities.

The agent analyzes payment events, identifies revenue at risk, diagnoses the failure, checks recovery eligibility, selects an intervention, and executes the supported recovery workflow.

The system then verifies the outcome and records the financial result.

### Core Value Proposition

> **PayGuard AI helps businesses recover revenue that would otherwise be lost by combining explainable AI diagnosis with policy-based recovery execution and measurable outcomes.**

---

## Why AI Revenue Recovery

The AI Revenue Recovery track focuses on closing the loop from detection to action.

PayGuard AI is aligned with this requirement because its core workflow is built around:

* Payment failure detection
* Revenue-at-risk analysis
* AI diagnosis
* Recovery recommendation
* Bounded recovery execution
* Outcome verification
* Measured revenue recovery
* Auditability

The product is not limited to identifying a problem.

It is designed to demonstrate:

> **A complete recovery operation across a batch of payment opportunities.**

---

## Core Features

### 1. Revenue-at-Risk Detection

Identify payment opportunities that may result in lost revenue.

The system can analyze:

* Transaction amount
* Payment method
* Failure category
* Risk indicators
* Transaction status
* Recovery eligibility
* Previous recovery attempts

The goal is to prioritize opportunities based on both **risk and financial impact**.

---

### 2. Explainable AI Diagnosis

Understand why a payment failed and why a recovery action is recommended.

For each opportunity, the system should provide:

* Failure reason
* Risk assessment
* Model explanation
* Recovery recommendation
* Expected outcome
* Eligibility decision

Example:

```text
Transaction: TXN-10294
Amount: ₹2,499
Failure Reason: Insufficient Funds

Risk Level: Medium
Recovery Eligibility: Eligible

Recommended Intervention:
Retry payment using UPI

Reason:
The transaction is retryable and has not exceeded
the configured recovery policy limits.
```

The explanation should be connected to the actual model output and recovery policy.

---

### 3. Bounded Recovery Workflow

Execute recovery actions within configured limits.

Possible interventions include:

* Retry payment
* Retry using an alternate payment method
* Update payment method
* Escalate for manual review

Only interventions supported by the existing backend should be presented as executable.

---

### 4. Recovery Policy Engine

Apply guardrails before executing a recovery action.

Example policy rules:

* Maximum retry attempts
* Minimum time between retries
* Maximum automated recovery amount
* Eligibility restrictions
* Stop after successful recovery
* Stop after retry limit
* Escalate high-value cases
* Do not retry permanently failed transactions

The policy engine should produce a clear decision:

```text
Eligible → Recommended Action → Policy Check → Execute
```

or

```text
Not Eligible → Reason → No Action Taken
```

---

### 5. Batch Recovery Evaluation

Process a complete batch of payment opportunities and measure the outcome.

The evaluation should report:

* Records processed
* Eligible opportunities
* Recovery attempts
* Successful recoveries
* Failed recovery attempts
* Revenue at risk
* Revenue recovered
* Unrecovered revenue
* Recovery rate
* Stopping-rule count
* Manual escalation count

This is the core evidence that the system is a **revenue recovery agent**, not only a prediction dashboard.

---

### 6. Audit Trail

Record important recovery decisions and execution events.

Example events:

```text
Transaction analyzed
        ↓
Risk classified
        ↓
Eligibility approved
        ↓
Intervention recommended
        ↓
Policy check passed
        ↓
Recovery executed
        ↓
Outcome verified
        ↓
Revenue recovered
```

The audit trail should help answer:

> **What did the agent do, why did it do it, and what happened afterward?**

---

### 7. AI Revenue Recovery Assistant

The AI Assistant provides insights into payment performance and recovery operations.

Example questions:

* How much revenue is currently at risk?
* Which failure reason is causing the most revenue loss?
* Which opportunities are eligible for recovery?
* Why was this transaction not eligible?
* How much revenue did the last batch recover?
* Which recovery actions have the highest success rate?
* Explain the recovery policy for this transaction.
* Summarize the audit trail for the last batch.

The assistant should use actual project data and supported backend functionality.

---

### 8. Payment Failure Simulation

The simulation demonstrates the complete recovery loop in a controlled environment.

```text
Simulate Payment Failure
        ↓
Failure Detected
        ↓
AI Diagnosis
        ↓
Recovery Recommendation
        ↓
Policy Check
        ↓
Recovery Execution
        ↓
Outcome Verification
        ↓
Revenue Recovered
        ↓
Audit Trail
```

This allows the product to demonstrate how the agent responds to a payment event.

---

## How the Agent Works

### End-to-End Workflow

```text
┌──────────────────────────────┐
│ Payment / Revenue Event      │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Revenue-at-Risk Detection    │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Failure Diagnosis            │
│ Explainable AI               │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Recovery Eligibility Check   │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Intervention Selection       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Policy & Guardrail Check     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Bounded Recovery Execution   │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Outcome Verification         │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Revenue Recovered Calculation│
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Audit Trail + Metrics        │
└──────────────────────────────┘
```

### Agent Decision Example

```text
INPUT
Payment amount: ₹2,499
Payment method: UPI
Failure reason: Insufficient Funds

DIAGNOSIS
Retryable payment failure

ELIGIBILITY
Eligible for recovery

INTERVENTION
UPI Retry

POLICY
Maximum 2 attempts

EXECUTION
Attempt 1 → Failed
Attempt 2 → Success

OUTCOME
₹2,499 recovered

AUDIT
Recovery action recorded
```

The values above are illustrative. Actual results should come from the implemented recovery workflow.

---

## Dataset and Data Strategy

PayGuard AI uses data for two separate purposes.

### 1. Model Training / Inference

The existing trained dataset and models are used to support payment-risk intelligence.

Depending on the available project data, this may include:

* Payment transaction features
* Failure patterns
* Risk labels
* Fraud or anomaly indicators
* Model evaluation metrics

The training dataset teaches the model how to identify relevant patterns.

### 2. Recovery Operations / Evaluation

A separate, reproducible batch of synthetic or historical payment records is used to demonstrate the recovery agent.

This batch allows the system to:

* Calculate revenue at risk
* Identify eligible opportunities
* Select interventions
* Apply stopping rules
* Execute recovery actions
* Measure recovery outcomes
* Generate an audit trail

### Important Data Distinction

> **The training dataset teaches the model. The recovery batch tests the agent. The dashboard reports the results.**

A trained model alone does not prove that money was recovered.

### Data Transparency

The application should clearly identify:

* Dataset name
* Dataset type
* Number of records
* Features used
* Target / label
* Training status
* Last trained timestamp
* Evaluation metrics

If synthetic data is used, it must be labeled:

**Synthetic Recovery Simulation**

or

**Demo Batch — Synthetic Data**

Synthetic results must not be presented as real merchant production revenue.

---

## Recovery Evaluation

The platform should demonstrate recovery across a complete batch rather than a single successful transaction.

### Evaluation Metrics

| Metric                  | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| Records Processed       | Total payment opportunities analyzed                    |
| Eligible Opportunities  | Transactions approved for recovery                      |
| Recovery Attempts       | Number of recovery actions executed                     |
| Successful Recoveries   | Transactions successfully recovered                     |
| Failed Recoveries       | Transactions where recovery was unsuccessful            |
| Revenue at Risk         | Total value of eligible or at-risk opportunities        |
| Revenue Recovered       | Actual value recovered after successful execution       |
| Unrecovered Revenue     | Revenue that remained unrecovered                       |
| Recovery Rate           | Successful recoveries divided by eligible opportunities |
| Stopping-Rule Count     | Opportunities stopped by configured policies            |
| Manual Escalation Count | Opportunities sent for manual review                    |

### Recovery Rate

The recovery rate should be defined clearly.

For example:

$$
\text{Recovery Rate} =
\frac{\text{Successful Recoveries}}
{\text{Eligible Recovery Opportunities}}
\times 100
$$

The exact definition used by the implementation should be documented.

### Example Batch Evaluation

```text
Batch Recovery Evaluation

Records processed: 100
Eligible opportunities: 70
Recovery attempts: 70
Successful recoveries: 42

Revenue at risk: ₹1,00,000
Revenue recovered: ₹42,000
Unrecovered revenue: ₹58,000

Recovery rate: 60%
Average recovery time: 14.5 minutes

Stopped by policy: 18
Escalated for review: 10
```

**The values above are illustrative only.**

The actual dashboard must calculate these metrics from the backend results.

---

## System Architecture

```text
                    ┌─────────────────────┐
                    │  Training Dataset   │
                    │  Existing ML Data   │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │  Trained Risk Model │
                    └──────────┬──────────┘
                               ↓
┌──────────────────────────────────────────────────────┐
│              RECOVERY OPERATIONS                     │
│                                                      │
│  Synthetic / Historical Payment Batch                │
│                 ↓                                    │
│  Risk Detection → Diagnosis → Eligibility            │
│                 ↓                                    │
│  Recovery Policy → Intervention → Execution          │
│                 ↓                                    │
│  Outcome Verification → Revenue Recovered            │
│                 ↓                                    │
│  Audit Trail + Evaluation Metrics                    │
└──────────────────────────────────────────────────────┘
                               ↓
                    ┌─────────────────────┐
                    │  PayGuard Dashboard │
                    │  Calculated Metrics │
                    └─────────────────────┘
```

### Architecture Components

**Frontend**

* Dashboard
* Payment Intelligence
* Recovery Operations
* Recovery Queue
* Revenue Analytics
* Model & Agent Evaluation
* Architecture & Docs
* AI Assistant

**Backend**

* Payment event processing
* Risk inference
* Recovery eligibility
* Policy engine
* Intervention selection
* Recovery execution
* Outcome verification
* Audit logging
* Evaluation metrics

**Data Layer**

* Training dataset
* Recovery evaluation batch
* Transaction records
* Recovery results
* Audit records

---

## Technology Stack

Use the actual stack implemented in the repository.

| Layer            | Technology                     |
| ---------------- | ------------------------------ |
| Frontend         | React / TypeScript             |
| Styling          | Tailwind CSS                   |
| Backend          | FastAPI / Node.js              |
| Database         | PostgreSQL / SQLite            |
| Machine Learning | Existing trained models        |
| AI Assistant     | Existing AI integration        |
| Authentication   | Existing authentication system |
| Charts           | Existing chart library         |
| Deployment       | Existing deployment platform   |

> **Note:** Update this table with the exact technologies used in the repository before publishing.

---

## Project Structure

Use the existing repository structure where appropriate.

```text
PayGuard-AI/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   └── types/
│   └── ...
│
├── backend/
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── recovery/
│   │   ├── eligibility.py
│   │   ├── policy_engine.py
│   │   ├── intervention_selector.py
│   │   ├── recovery_executor.py
│   │   ├── outcome_verifier.py
│   │   └── audit_service.py
│   ├── ml/
│   ├── database/
│   └── ...
│
├── datasets/
│   ├── training/
│   └── recovery_evaluation/
│
├── models/
│
├── docs/
│
└── README.md
```

**Do not create duplicate files if equivalent modules already exist.**

---

## Application Modules

### Executive Dashboard

The Revenue Recovery Control Center displays:

* Recovered Revenue
* Revenue at Risk
* Active Recovery Rate
* Payment Success Rate
* Eligible Opportunities
* Recovery Attempts
* Successful Recoveries
* Unrecovered Revenue

The dashboard should use actual backend data.

If demo data is used, it must be clearly labeled.

### Payment Intelligence

Provides payment failure analysis and risk insights.

### Recovery Operations

The main agent workflow for processing a batch of payment opportunities.

### Recovery Queue

Displays individual transactions and their recovery status.

### Revenue Analytics

Shows recovery performance and payment-method analysis.

### Model & Agent Evaluation

Evaluates the underlying model and the recovery agent.

### Architecture & Docs

Explains the system architecture, AI pipeline, and recovery workflow.

---

## Getting Started

### Prerequisites

Install the dependencies required by the existing project.

Typical requirements may include:

* Node.js
* npm
* Python
* pip
* Database
* Required AI / ML dependencies

Use the actual project requirements.

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd PayGuard-AI
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create the required environment files.

Example:

```env
DATABASE_URL=
API_BASE_URL=
AI_API_KEY=
MODEL_PATH=
```

Do not commit secrets to the repository.

### 5. Start the Application

Use the existing project commands.

Example:

```bash
npm run dev
```

or

```bash
uvicorn main:app --reload
```

### 6. Open the Application

Use the local URL shown by the development server.

---

## Configuration

The following configuration areas may be required depending on the implementation:

### Database

* Connection URL
* Database name
* Migration configuration

### AI / ML

* Model path
* Model version
* Inference configuration
* AI API credentials if applicable

### Recovery Policies

* Maximum retry attempts
* Retry interval
* Automated recovery amount limit
* Escalation threshold
* Stop conditions

### Authentication

* Authentication provider
* Session configuration
* User permissions

**Do not publish real credentials or sensitive configuration values.**

---

## Usage

### 1. Open the Dashboard

Review:

* Revenue at risk
* Recovery opportunities
* Payment failure distribution
* Recovery performance

### 2. Open Recovery Operations

Select or load a recovery batch.

### 3. Run Analysis

The agent analyzes the batch and identifies eligible opportunities.

### 4. Review Recommendations

Review:

* Failure reason
* Risk level
* Eligibility
* Recommended intervention
* Policy decision

### 5. Execute Recovery

Execute supported recovery actions within configured policies.

### 6. Review Results

View:

* Successful recoveries
* Failed recoveries
* Revenue recovered
* Unrecovered revenue
* Stopping reasons

### 7. Review Audit Trail

Inspect the decisions and execution history.

---

## API Overview

The following endpoints represent the intended recovery workflow.

**Important:** These are example endpoint names. Update them to match the actual backend implementation.

| Endpoint                          | Purpose                             |
| --------------------------------- | ----------------------------------- |
| `GET /api/dashboard/summary`      | Retrieve dashboard metrics          |
| `GET /api/payments`               | Retrieve payment records            |
| `POST /api/payments/simulate`     | Simulate a payment failure          |
| `POST /api/recovery/analyze`      | Analyze a recovery batch            |
| `GET /api/recovery/queue`         | Retrieve recovery opportunities     |
| `GET /api/recovery/{id}`          | Retrieve transaction details        |
| `POST /api/recovery/{id}/execute` | Execute a supported recovery action |
| `POST /api/recovery/{id}/stop`    | Stop a recovery workflow            |
| `GET /api/recovery/evaluation`    | Retrieve batch evaluation metrics   |
| `GET /api/recovery/audit`         | Retrieve audit records              |
| `GET /api/models/evaluation`      | Retrieve model evaluation metrics   |

The frontend should use the actual API routes and response schemas from the repository.

---

## Model Evaluation

PayGuard AI evaluates the underlying risk model and the recovery agent separately.

### Model Evaluation

Depending on the available model, evaluation may include:

* Accuracy
* Precision
* Recall
* F1-score
* ROC-AUC
* Confusion matrix
* Dataset information
* Last trained timestamp

### Agent Evaluation

The recovery agent should be evaluated on:

* Batch size
* Eligible opportunities
* Recovery attempts
* Successful recoveries
* Recovery rate
* Revenue recovered
* Policy violations prevented
* Stopping-rule adherence
* Audit completeness

### Important

Model accuracy does not equal revenue recovered.

A model can identify payment risk accurately without successfully recovering money.

The agent evaluation must measure the **actual recovery workflow outcome**.

---

## Security and Guardrails

PayGuard AI is designed as a payment-risk and recovery platform.

The system should:

* Protect sensitive payment information
* Avoid unnecessary exposure of customer data
* Use permission-aware actions
* Record recovery decisions
* Record recovery execution results
* Provide clear stopping reasons
* Apply configured recovery policies
* Avoid unsupported compliance claims

### Recovery Guardrails

The recovery workflow should support:

* Maximum retry attempts
* Eligibility restrictions
* Amount limits
* Manual escalation
* Stop after successful recovery
* Stop after retry limit
* Stop after permanent failure

Do not claim PCI compliance, encryption certifications, or other security certifications unless they are actually implemented and verified.

---

## Demo Workflow

The recommended demonstration is:

```text
1. Open PayGuard AI Dashboard
        ↓
2. View Revenue at Risk
        ↓
3. Open Recovery Operations
        ↓
4. Load a complete recovery batch
        ↓
5. Run AI analysis
        ↓
6. Review eligibility and recommendations
        ↓
7. Execute bounded recovery workflow
        ↓
8. View successful and stopped actions
        ↓
9. Review recovered revenue
        ↓
10. Open audit trail
```

The demo should show both successful recoveries and cases that were stopped or escalated.

---

## Limitations

* Recovery results depend on the available dataset and implemented backend functionality.
* Synthetic recovery data does not represent real merchant production revenue.
* Model performance depends on dataset quality and distribution.
* Recovery actions are limited to supported payment integrations.
* The system does not guarantee successful recovery for every payment failure.
* Compliance requirements depend on the actual implementation and deployment environment.
* Future recovery directions such as checkout abandonment, failed subscriptions, and B2B receivables may require additional data and integrations.

---

## Future Enhancements

Potential future extensions include:

* Checkout abandonment recovery
* Failed-subscription recovery
* B2B receivables chaser
* Mandate retry sequencer
* Promise-to-pay tracker
* Multilingual recovery assistant
* Advanced recovery policy optimization
* Merchant-specific recovery strategies
* Additional payment gateway integrations
* Real-time payment event ingestion
* Production-grade monitoring and observability

These are future directions and should not be presented as implemented features unless they exist in the repository.

---

## Contributing

Contributions are welcome.

Before submitting changes:

1. Inspect the existing architecture.
2. Preserve working functionality.
3. Follow the existing code style.
4. Avoid unnecessary rewrites.
5. Add or update tests where appropriate.
6. Update documentation for new features.
7. Do not commit secrets or sensitive data.

---

## License

Add the appropriate license for the project.

Example:

```text
MIT License
```

---

## Disclaimer

PayGuard AI is a demonstration and development project.

Unless explicitly stated otherwise, payment records and recovery results may be synthetic or simulated.

The platform does not represent real merchant production revenue unless connected to verified production data.

All recovery actions should be executed only within the configured policies and supported backend functionality.

---

## Project Vision

PayGuard AI aims to demonstrate how AI can move beyond payment-failure prediction and become a **measurable revenue recovery agent**.

The long-term vision is to help businesses:

> **Detect revenue at risk → Understand the cause → Choose the right intervention → Recover money safely → Measure the outcome → Learn from the result.**
