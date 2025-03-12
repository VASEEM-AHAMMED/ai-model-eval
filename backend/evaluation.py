from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from backend.utils import load_model, evaluate_model

router = APIRouter()

class EvaluationRequest(BaseModel):
    model_id: str
    test_data: List[float]

@router.post("/evaluate")
async def evaluate(request: EvaluationRequest):
    model = await load_model(request.model_id)
    evaluation_result = await evaluate_model(model, request.test_data)
    return {"evaluation_result": evaluation_result}
