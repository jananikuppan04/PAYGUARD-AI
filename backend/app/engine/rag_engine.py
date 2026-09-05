from typing import List, Dict, Any

PAYMENT_KNOWLEDGEBASE = [
    {
        "topic": "Decline Code 51 (Insufficient Funds)",
        "content": "Decline Code 51 occurs when the customer's card issuing bank denies authorization due to lack of available funds. Recommended recovery policy: Do not instantly retry on card network. Send automated WhatsApp/Email reminder with a 1-click retry link valid for 48 hours. Most funds become available on 1st/15th salary cycle or weekend."
    },
    {
        "topic": "Decline Code 54 (Expired Card)",
        "content": "Decline Code 54 indicates an expired billing card. Policy: Trigger automated Razorpay Card Account Updater (CAU) to poll Visa/Mastercard VAU network for renewed card token, or prompt customer to update payment instrument via secure SMS update link."
    },
    {
        "topic": "Decline Code 91 & 96 (Technical Timeout & Gateway Outage)",
        "content": "Decline Code 91 (MPI Timeout) and 96 (Issuer System Malfunction) represent transient bank gateway infrastructure issues. Policy: Execute automatic background retry using Smart Routing secondary acquirer node after 15 to 30 minutes delay. Do not alert customer."
    },
    {
        "topic": "Decline Code 05 (Do Not Honor / Risk Block)",
        "content": "Decline Code 05 is an issuer-side fraud prevention block. Policy: Recommend customer switch payment method to 2FA UPI or NetBanking. Do not retry original card."
    },
    {
        "topic": "Decline Code 14 (Invalid Card / Account Closed)",
        "content": "Decline Code 14 represents a hard permanent failure. Account or BIN is permanently closed or non-existent. Policy: Mark Non-Recoverable immediately. Prevent all retries to avoid gateway penalty fees."
    },
    {
        "topic": "PayGuard Anomaly & Risk Policy",
        "content": "Transactions with XGBoost Risk Score > 80 or Autoencoder Anomaly Score > 0.90 are automatically classified as High Risk / Potential Stolen Credentials. Policy: Block automated recovery retries and escalate to merchant risk desk."
    }
]

class RAGEngine:
    """RAG Retrieval Engine over Merchant Payment Policy Knowledge Base."""

    @staticmethod
    def search_kb(query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        matched = []
        for doc in PAYMENT_KNOWLEDGEBASE:
            if any(term in doc["topic"].lower() or term in doc["content"].lower() for term in query_lower.split()):
                matched.append(doc)
        if not matched:
            matched = PAYMENT_KNOWLEDGEBASE[:2] # Default fallback context
        return matched
