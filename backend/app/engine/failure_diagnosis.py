from typing import Dict, Any
from models import FailureCategory

class FailureDiagnosisEngine:
    """Diagnoses payment failure events into distinct technical, customer, risk, or non-recoverable categories."""

    DIAGNOSIS_MAP = {
        "51": {
            "reason": "Insufficient Funds in Account",
            "category": FailureCategory.CUSTOMER_RELATED,
            "description": "The customer's bank account or card balance was insufficient to authorize the requested amount at the moment of billing."
        },
        "54": {
            "reason": "Card Expired or Invalid Expiry Date",
            "category": FailureCategory.CUSTOMER_RELATED,
            "description": "The credit or debit card expiration date provided has passed or does not match bank records."
        },
        "91": {
            "reason": "Acquirer / Bank Gateway Timeout",
            "category": FailureCategory.TECHNICAL,
            "description": "The acquiring bank or payment switch failed to respond within the designated 3DS/MPI timeout window."
        },
        "05": {
            "reason": "Do Not Honor (Risk Blocked)",
            "category": FailureCategory.RISK_RELATED,
            "description": "The issuing bank risk engine declined authorization due to velocity rules, geographical mismatch, or card security policy."
        },
        "96": {
            "reason": "System Malfunction / Issuer Offline",
            "category": FailureCategory.TECHNICAL,
            "description": "The issuing bank core database system experienced a transient maintenance outage during transaction routing."
        },
        "14": {
            "reason": "Invalid Card Number / Account Closed",
            "category": FailureCategory.NON_RECOVERABLE,
            "description": "The bank card number or account reference is invalid or has been permanently closed by the holder."
        },
        "FRAUD_HIGH": {
            "reason": "Stolen Card Anomaly / Risk Alert",
            "category": FailureCategory.RISK_RELATED,
            "description": "PayGuard anomaly detection flagged suspicious transaction characteristics matching stolen card or bot automated patterns."
        }
    }

    @classmethod
    def diagnose(cls, failure_code: str) -> Dict[str, Any]:
        info = cls.DIAGNOSIS_MAP.get(failure_code, {
            "reason": "Unspecified Gateway Processing Error",
            "category": FailureCategory.TECHNICAL,
            "description": "Generic decline response received from payment processor switch."
        })
        return info
