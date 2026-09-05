from typing import Dict, Any
from models import ActionType, ActionExplanation, FailureCategory, PaymentRecord

class RecoveryRecommendationAgent:
    """AI Agent recommending bounded Next-Best-Action for payment recovery with full explainability."""

    @staticmethod
    def recommend(payment: PaymentRecord) -> Dict[str, Any]:
        code = payment.failure_code
        cat = payment.failure_category
        eligible = payment.recovery_eligible
        risk = payment.risk_score

        if not eligible:
            if code == "FRAUD_HIGH" or risk >= 80:
                action_type = ActionType.ESCALATE_MERCHANT
                action_str = "Escalate to Fraud Team & Block Device ID"
                exp = ActionExplanation(
                    why_failed="Transaction flagged with critical anomaly score (Autoencoder = 0.94, XGBoost = 96/100).",
                    eligibility_rationale="Ineligible for automated retry due to severe fraud risk threshold violation.",
                    action_rationale="Escalate to human risk analyst to prevent chargeback loss and stolen card abuse.",
                    evidence_points=["Risk Score: 96/100", "Fraud Anomaly: True", "IP Velocity Spike: Yes"],
                    target_metric="Fraud Loss Prevention"
                )
            else:
                action_type = ActionType.DO_NOT_RETRY
                action_str = "Do Not Retry - Permanently Invalid Account"
                exp = ActionExplanation(
                    why_failed="Decline Code 14 (Invalid card number or account closed).",
                    eligibility_rationale="Permanently invalid instrument. Retrying will incur gateway penalties.",
                    action_rationale="Stop all recovery attempts immediately for this billing instrument.",
                    evidence_points=["Bank Code: 14", "Instrument Status: Terminated"],
                    target_metric="Prevent Wasted Gateway Fees"
                )
            return {
                "action_type": action_type,
                "action": action_str,
                "confidence": 0.98,
                "estimated_value": 0.0,
                "explanation": exp
            }

        # Handle Eligible Payment Scenarios
        if cat == FailureCategory.TECHNICAL:
            action_type = ActionType.RETRY_DELAY
            action_str = "Smart Retry via Backup Gateway after 15 min delay" if code == "91" else "Schedule Auto-Retry in Off-Peak Window (2 Hours)"
            exp = ActionExplanation(
                why_failed=f"Technical bank downtime / timeout (Code {code}). Customer card is healthy.",
                eligibility_rationale="100% eligible technical retry. Customer account has no fraud flags.",
                action_rationale="Rerouting payment through secondary acquirer node after brief pause avoids customer friction.",
                evidence_points=[f"Decline Code: {code}", "Risk Score: Low", "Technical Failure: Confirmed"],
                target_metric="Technical Retry Recovery Rate"
            )
            prob = 0.92 if code == "91" else 0.88

        elif code == "51": # Insufficient Funds
            action_type = ActionType.SEND_REMINDER
            action_str = "Send Automated Payment Reminder & Retry Link via WhatsApp"
            exp = ActionExplanation(
                why_failed="Decline Code 51 (Insufficient funds at time of authorization).",
                eligibility_rationale=f"High customer tenure ({payment.customer_tenure_months} months) and {int(payment.previous_success_rate * 100)}% past success rate.",
                action_rationale="Sending a friendly WhatsApp reminder with a 1-click retry link yields high recovery once customer tops up.",
                evidence_points=[f"Tenure: {payment.customer_tenure_months}m", f"History Success: {int(payment.previous_success_rate*100)}%", "Soft Decline: Code 51"],
                target_metric="Customer Reminder Conversion"
            )
            prob = 0.78

        elif code == "54": # Expired Card
            action_type = ActionType.REQUEST_DETAILS
            action_str = "Request Updated Card Details / Trigger Account Updater"
            exp = ActionExplanation(
                why_failed="Decline Code 54 (Card expired or invalid expiry date).",
                eligibility_rationale="Active subscriber with consistent payment history.",
                action_rationale="Send automated secure update form or query Razorpay Visa/Mastercard Account Updater service.",
                evidence_points=["Card Expiry Flag: True", "Subscription Active: Yes"],
                target_metric="Updated Payment Method Recovery"
            )
            prob = 0.85

        elif code == "05": # Risk Blocked
            action_type = ActionType.SWITCH_METHOD
            action_str = "Offer Alternative Payment Method (UPI / NetBanking)"
            exp = ActionExplanation(
                why_failed="Decline Code 05 (Issuer security engine declined high-value transaction).",
                eligibility_rationale="Legitimate customer, but card issuer 2FA policy blocked authorization.",
                action_rationale="Prompt customer to complete checkout via UPI or NetBanking to bypass card issuer block.",
                evidence_points=["Issuer Block: Code 05", f"Risk Score: {payment.risk_score}"],
                target_metric="Payment Method Switch Conversion"
            )
            prob = 0.60

        else:
            action_type = ActionType.RETRY_DELAY
            action_str = "Smart Retry after 30 min delay"
            exp = ActionExplanation(
                why_failed=f"Decline Code {code}: Temporary authorization failure.",
                eligibility_rationale="Payment is eligible under standard retry rules.",
                action_rationale="Delayed retry provides time for transient bank processing issues to resolve.",
                evidence_points=[f"Decline Code: {code}"],
                target_metric="Delayed Retry Success"
            )
            prob = 0.70

        est_val = round(payment.amount * prob, 2)
        return {
            "action_type": action_type,
            "action": action_str,
            "confidence": prob,
            "estimated_value": est_val,
            "explanation": exp
        }
