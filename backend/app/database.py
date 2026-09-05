import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
from models import (
    PaymentRecord, PaymentMethod, PaymentStatus, FailureCategory,
    RecoveryPriority, ActionType, ActionExplanation
)

try:
    from app.config import PAYMENTS_DB_PATH
    DATA_FILE = PAYMENTS_DB_PATH
except ImportError:
    try:
        from config import PAYMENTS_DB_PATH
        DATA_FILE = PAYMENTS_DB_PATH
    except ImportError:
        DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "payments_db.json"
        if not DATA_FILE.exists():
            DATA_FILE = Path(__file__).resolve().parent / "data" / "payments_db.json"

FIRST_NAMES = ["Aarav", "Ananya", "Rohan", "Priya", "Vikram", "Sneha", "Karan", "Diya", "Aditya", "Neha", "Rahul", "Pooja", "Siddharth", "Meera", "Arjun", "Tanvi"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Patel", "Mehta", "Nair", "Rao", "Reddy", "Chopra", "Joshi", "Singhania", "Mukherjee", "Kapoor", "Bhatia"]

DECLINE_SCENARIOS = [
    {
        "code": "51",
        "reason": "Insufficient Funds in Account",
        "category": FailureCategory.CUSTOMER_RELATED,
        "eligible": True,
        "priority": RecoveryPriority.HIGH,
        "action_type": ActionType.SEND_REMINDER,
        "action": "Send Automated Payment Reminder & Retry Link via WhatsApp",
        "rec_prob": 0.78,
        "explanation": {
            "why_failed": "Transaction declined with Code 51 (Insufficient balance in customer bank account at time of authorization).",
            "eligibility_rationale": "Customer has high tenure (18 months) and 92% past success rate. Balance fluctuates around salary date.",
            "action_rationale": "Sending a polite payment reminder with a quick retry link yields a high conversion rate within 24-48 hours.",
            "evidence_points": ["Customer Tenure: 18 months", "Past Success Rate: 92%", "Account Status: Active", "Failure Type: Soft Decline"],
            "target_metric": "Customer Conversion & Revenue Recovery"
        }
    },
    {
        "code": "54",
        "reason": "Card Expired or Invalid Expiry Date",
        "category": FailureCategory.CUSTOMER_RELATED,
        "eligible": True,
        "priority": RecoveryPriority.HIGH,
        "action_type": ActionType.REQUEST_DETAILS,
        "action": "Request Updated Card Details / Trigger Account Updater",
        "rec_prob": 0.85,
        "explanation": {
            "why_failed": "Decline Code 54: The payment card expiration date has passed or was entered incorrectly.",
            "eligibility_rationale": "Active recurring subscriber with no prior dispute history. Valid customer contact info available.",
            "action_rationale": "Request card detail update via hosted secure form or trigger automated bank card updater.",
            "evidence_points": ["Card Expiry Flagged: True", "Subscription Active: Yes", "Dispute History: None"],
            "target_metric": "Updated Payment Method & Recovered Subscription"
        }
    },
    {
        "code": "91",
        "reason": "Acquirer / Bank Gateway Timeout",
        "category": FailureCategory.TECHNICAL,
        "eligible": True,
        "priority": RecoveryPriority.HIGH,
        "action_type": ActionType.RETRY_DELAY,
        "action": "Smart Retry via Backup Gateway after 15 min delay",
        "rec_prob": 0.92,
        "explanation": {
            "why_failed": "Decline Code 91: The issuing bank network timed out during 3DS verification.",
            "eligibility_rationale": "Pure technical failure. Customer account and card are valid and in good standing.",
            "action_rationale": "Automatic retry using Razorpay Smart Routing to secondary acquirer node avoids customer drop-off.",
            "evidence_points": ["Gateway Response Time: > 8000ms", "Risk Score: 12 (Low)", "Network Error: Confirmed"],
            "target_metric": "Seamless Technical Retry Success"
        }
    },
    {
        "code": "05",
        "reason": "Do Not Honor (Risk Blocked)",
        "category": FailureCategory.RISK_RELATED,
        "eligible": True,
        "priority": RecoveryPriority.MEDIUM,
        "action_type": ActionType.SWITCH_METHOD,
        "action": "Offer Alternative Payment Method (UPI / NetBanking)",
        "rec_prob": 0.60,
        "explanation": {
            "why_failed": "Decline Code 05: Issuer risk system blocked transaction due to unusual international/velocity pattern.",
            "eligibility_rationale": "Moderate risk score (58/100). Customer is legitimate but card issuer blocked high-value charge.",
            "action_rationale": "Prompting customer to complete authentication via UPI 2FA bypasses card issuer block.",
            "evidence_points": ["XGBoost Risk Score: 58", "Card Issuer Block: Code 05", "Customer Account Age: 6 months"],
            "target_metric": "Payment Method Switch Conversion"
        }
    },
    {
        "code": "96",
        "reason": "System Malfunction / Issuer Offline",
        "category": FailureCategory.TECHNICAL,
        "eligible": True,
        "priority": RecoveryPriority.HIGH,
        "action_type": ActionType.RETRY_DELAY,
        "action": "Schedule Auto-Retry in Off-Peak Window (2 Hours)",
        "rec_prob": 0.88,
        "explanation": {
            "why_failed": "Decline Code 96: Bank core banking backend experienced a temporary maintenance outage.",
            "eligibility_rationale": "Temporary bank infrastructure downtime. Customer card is unaffected.",
            "action_rationale": "Defer execution until bank health endpoints signal green status.",
            "evidence_points": ["Bank Health Metric: Degradation", "Failure Type: Transient Infrastructure"],
            "target_metric": "Delayed Revenue Recovery"
        }
    },
    {
        "code": "14",
        "reason": "Invalid Card Number / Account Closed",
        "category": FailureCategory.NON_RECOVERABLE,
        "eligible": False,
        "priority": RecoveryPriority.NONE,
        "action_type": ActionType.DO_NOT_RETRY,
        "action": "Do Not Retry - Permanently Invalid Account",
        "rec_prob": 0.0,
        "explanation": {
            "why_failed": "Decline Code 14: Card number does not exist on bank card master database or account closed.",
            "eligibility_rationale": "Permanently invalid billing instrument. Retrying will incur gateway fees and worsen merchant standing.",
            "action_rationale": "Mark transaction non-recoverable immediately to prevent wasted retries.",
            "evidence_points": ["Bank Response: Account Terminated", "Card Status: Invalid BIN/PAN"],
            "target_metric": "Avoid Invalid Retry Costs"
        }
    },
    {
        "code": "FRAUD_HIGH",
        "reason": "Stolen Card Anomaly / Stacking Anomaly Detected",
        "category": FailureCategory.RISK_RELATED,
        "eligible": False,
        "priority": RecoveryPriority.NONE,
        "action_type": ActionType.ESCALATE_MERCHANT,
        "action": "Escalate to Fraud Team & Block Device ID",
        "rec_prob": 0.0,
        "explanation": {
            "why_failed": "High Risk Anomaly: Autoencoder anomaly score 0.94, XGBoost risk score 96/100.",
            "eligibility_rationale": "High likelihood of stolen credentials or synthetic fraud attack.",
            "action_rationale": "Escalate transaction to merchant risk team for manual fraud review. Do NOT attempt recovery.",
            "evidence_points": ["Autoencoder Reconstruction Error: Extreme", "XGBoost Risk Score: 96/100", "IP Velocity: 14 txns/min"],
            "target_metric": "Fraud Loss Prevention"
        }
    }
]


class PaymentDatabase:
    def __init__(self):
        self.payments: Dict[str, PaymentRecord] = {}
        self._load_or_generate_data()

    def _generate_synthetic_payments(self, count: int = 500) -> List[PaymentRecord]:
        records: List[PaymentRecord] = []
        now = datetime.now()

        # Generate realistic distribution: ~60% success, 40% failed/recoverable
        for i in range(1, count + 1):
            txn_id = f"TXN-{1000 + i}"
            cust_id = f"CUST-{(i % 85) + 100}"
            cust_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            merchant_id = "MERCHANT_RAZOR_01"
            
            # Amount between 250 INR and 25,000 INR
            amount = round(random.choice([299, 499, 999, 1499, 2499, 4999, 8999, 12500, 18900, 24500]) + random.random(), 2)
            method = random.choice([PaymentMethod.CARD, PaymentMethod.UPI, PaymentMethod.NETBANKING, PaymentMethod.WALLET])
            
            # Timestamp in last 14 days
            days_ago = random.uniform(0, 14)
            txn_time = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")

            is_successful_initial = random.random() < 0.55
            
            if is_successful_initial:
                status = PaymentStatus.SUCCESSFUL
                rec = PaymentRecord(
                    transaction_id=txn_id,
                    customer_id=cust_id,
                    customer_name=cust_name,
                    merchant_id=merchant_id,
                    amount=amount,
                    payment_method=method,
                    payment_status=status,
                    failure_reason=None,
                    failure_code=None,
                    failure_category=FailureCategory.NONE,
                    retry_count=0,
                    previous_success_rate=round(random.uniform(0.80, 0.99), 2),
                    customer_tenure_months=random.randint(3, 48),
                    transaction_timestamp=txn_time,
                    risk_score=round(random.uniform(2.0, 18.0), 1),
                    risk_factors=["Low Risk Profile", "Known Customer Device"],
                    recovery_eligible=False,
                    recovery_priority=RecoveryPriority.NONE,
                    recommended_action_type=ActionType.DO_NOT_RETRY,
                    recommended_action="Payment Completed Successfully",
                    confidence_score=0.99,
                    estimated_recovery_value=0.0,
                    recovery_attempted=False,
                    recovery_successful=False,
                    recovered_amount=0.0
                )
            else:
                # Select a decline scenario
                scenario = random.choice(DECLINE_SCENARIOS)
                
                # Check if it was already recovered in history
                already_attempted = random.random() < 0.45
                already_recovered = already_attempted and scenario["eligible"] and (random.random() < 0.65)
                
                if already_recovered:
                    status = PaymentStatus.RECOVERED
                elif scenario["eligible"]:
                    status = PaymentStatus.RECOVERABLE
                elif scenario["category"] == FailureCategory.NON_RECOVERABLE:
                    status = PaymentStatus.NON_RECOVERABLE
                else:
                    status = PaymentStatus.FAILED

                risk_score = round(random.uniform(75.0, 98.0), 1) if scenario["code"] == "FRAUD_HIGH" else round(random.uniform(10.0, 45.0), 1)
                
                rec = PaymentRecord(
                    transaction_id=txn_id,
                    customer_id=cust_id,
                    customer_name=cust_name,
                    merchant_id=merchant_id,
                    amount=amount,
                    payment_method=method,
                    payment_status=status,
                    failure_reason=scenario["reason"],
                    failure_code=scenario["code"],
                    failure_category=scenario["category"],
                    retry_count=1 if already_attempted else 0,
                    max_retries=3,
                    previous_success_rate=round(random.uniform(0.70, 0.95), 2),
                    customer_tenure_months=random.randint(1, 36),
                    transaction_timestamp=txn_time,
                    risk_score=risk_score,
                    risk_factors=["Transaction Decline", f"Failure Code {scenario['code']}"] if risk_score < 60 else ["XGBoost Anomaly Flag", "High Anomaly Score", "Velocity Spikes"],
                    recovery_eligible=scenario["eligible"],
                    recovery_priority=scenario["priority"],
                    recommended_action_type=scenario["action_type"],
                    recommended_action=scenario["action"],
                    action_explanation=ActionExplanation(**scenario["explanation"]),
                    confidence_score=round(scenario["rec_prob"], 2),
                    estimated_recovery_value=round(amount * scenario["rec_prob"], 2) if scenario["eligible"] else 0.0,
                    recovery_attempted=already_attempted,
                    recovery_successful=already_recovered,
                    recovered_amount=amount if already_recovered else 0.0,
                    recovery_timestamp=(now - timedelta(days=days_ago - 0.1)).strftime("%Y-%m-%d %H:%M:%S") if already_recovered else None,
                    recovery_attempts_history=[{
                        "timestamp": (now - timedelta(days=days_ago - 0.05)).strftime("%Y-%m-%d %H:%M:%S"),
                        "action": scenario["action"],
                        "outcome": "SUCCESS" if already_recovered else "FAILED",
                        "recovered_amount": amount if already_recovered else 0.0
                    }] if already_attempted else []
                )

            records.append(rec)

        return records

    def _load_or_generate_data(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.payments = {k: PaymentRecord(**v) for k, v in data.items()}
                return
            except Exception as e:
                print(f"Error reading DB file, re-generating: {e}")
        
        # Generate new dataset
        records = self._generate_synthetic_payments(500)
        self.payments = {r.transaction_id: r for r in records}
        self.save_to_file()

    def save_to_file(self):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump({k: (v.model_dump() if hasattr(v, "model_dump") else v.dict()) for k, v in self.payments.items()}, f, indent=2)

    def get_all(self, status: Optional[str] = None, category: Optional[str] = None, method: Optional[str] = None, priority: Optional[str] = None) -> List[PaymentRecord]:
        res = list(self.payments.values())
        if status:
            res = [p for p in res if p.payment_status.value == status or p.payment_status == status]
        if category:
            res = [p for p in res if p.failure_category.value == category or p.failure_category == category]
        if method:
            res = [p for p in res if p.payment_method.value == method or p.payment_method == method]
        if priority:
            res = [p for p in res if p.recovery_priority.value == priority or p.recovery_priority == priority]
        # Sort by timestamp descending
        res.sort(key=lambda x: x.transaction_timestamp, reverse=True)
        return res

    def get_by_id(self, txn_id: str) -> Optional[PaymentRecord]:
        return self.payments.get(txn_id)

    def add_payment(self, record: PaymentRecord):
        self.payments[record.transaction_id] = record
        self.save_to_file()

    def update_payment(self, record: PaymentRecord):
        self.payments[record.transaction_id] = record
        self.save_to_file()

    def get_analytics(self) -> Dict[str, Any]:
        all_records = list(self.payments.values())
        total = len(all_records)
        successful = sum(1 for p in all_records if p.payment_status == PaymentStatus.SUCCESSFUL or p.payment_status == PaymentStatus.RECOVERED)
        failed = sum(1 for p in all_records if p.payment_status in [PaymentStatus.FAILED, PaymentStatus.RECOVERABLE, PaymentStatus.NON_RECOVERABLE])
        opportunities = sum(1 for p in all_records if p.recovery_eligible and p.payment_status != PaymentStatus.RECOVERED)
        
        recovered_rev = sum(p.recovered_amount for p in all_records if p.payment_status == PaymentStatus.RECOVERED or p.recovery_successful)
        at_risk_rev = sum(p.amount for p in all_records if p.recovery_eligible and p.payment_status != PaymentStatus.RECOVERED)
        predicted_potential = sum(p.estimated_recovery_value for p in all_records if p.recovery_eligible and p.payment_status != PaymentStatus.RECOVERED)
        
        recovery_attempts_count = sum(1 for p in all_records if p.recovery_attempted)
        recovered_count = sum(1 for p in all_records if p.recovery_successful)
        
        recovery_rate = round((recovered_count / recovery_attempts_count * 100), 1) if recovery_attempts_count > 0 else 0.0
        success_rate = round((successful / total * 100), 1) if total > 0 else 0.0

        # Breakdown by category
        cat_counts = {
            FailureCategory.TECHNICAL.value: sum(1 for p in all_records if p.failure_category == FailureCategory.TECHNICAL),
            FailureCategory.CUSTOMER_RELATED.value: sum(1 for p in all_records if p.failure_category == FailureCategory.CUSTOMER_RELATED),
            FailureCategory.RISK_RELATED.value: sum(1 for p in all_records if p.failure_category == FailureCategory.RISK_RELATED),
            FailureCategory.NON_RECOVERABLE.value: sum(1 for p in all_records if p.failure_category == FailureCategory.NON_RECOVERABLE)
        }

        # Breakdown by method
        method_data = {}
        for m in PaymentMethod:
            m_records = [p for p in all_records if p.payment_method == m]
            m_total = len(m_records)
            m_rec = sum(p.recovered_amount for p in m_records if p.recovery_successful)
            m_failed = sum(1 for p in m_records if p.payment_status != PaymentStatus.SUCCESSFUL and p.payment_status != PaymentStatus.RECOVERED)
            method_data[m.value] = {
                "total": m_total,
                "failed": m_failed,
                "recovered_revenue": round(m_rec, 2)
            }

        # Recent attempts
        recent_attempts = []
        for p in sorted([p for p in all_records if p.recovery_attempted], key=lambda x: x.recovery_timestamp or "", reverse=True)[:10]:
            recent_attempts.append({
                "transaction_id": p.transaction_id,
                "customer_name": p.customer_name,
                "amount": p.amount,
                "payment_method": p.payment_method.value,
                "action_taken": p.recommended_action,
                "outcome": "SUCCESS" if p.recovery_successful else "FAILED",
                "timestamp": p.recovery_timestamp or p.transaction_timestamp
            })

        return {
            "total_attempts": total,
            "successful_payments": successful,
            "failed_payments": failed,
            "recovery_opportunities": opportunities,
            "recovered_revenue": round(recovered_rev, 2),
            "recovery_rate": recovery_rate,
            "payment_success_rate": success_rate,
            "revenue_at_risk": round(at_risk_rev, 2),
            "predicted_recovery_potential": round(predicted_potential, 2),
            "avg_recovery_time_minutes": 14.5,
            "failure_category_breakdown": cat_counts,
            "payment_method_breakdown": method_data,
            "recent_recovery_attempts": recent_attempts
        }


db = PaymentDatabase()
