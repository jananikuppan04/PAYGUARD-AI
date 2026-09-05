from fastapi import APIRouter
from engine.evaluator import EvaluationEngine

router = APIRouter(prefix="/api/v1/evaluation", tags=["Evaluation"])

@router.get("")
async def get_evaluation():
    return EvaluationEngine.get_evaluation_report()
