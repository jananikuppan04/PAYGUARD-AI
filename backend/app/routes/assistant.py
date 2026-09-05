from fastapi import APIRouter
from models import AssistantChatRequest, AssistantChatResponse
from engine.merchant_assistant import MerchantAssistantEngine

router = APIRouter(prefix="/api/v1/assistant", tags=["Assistant"])

@router.post("/chat", response_model=AssistantChatResponse)
async def chat_assistant(req: AssistantChatRequest):
    res = MerchantAssistantEngine.process_query(req.query, req.transaction_id)
    return AssistantChatResponse(
        answer=res["answer"],
        evidence=res.get("evidence", []),
        suggested_actions=res.get("suggested_actions", [])
    )
