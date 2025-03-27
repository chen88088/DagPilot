from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_engine import run_ai_assist

router = APIRouter()

# 請求與回應格式
class AIAssistRequest(BaseModel):
    question: str
    dag_code: str

class AIAssistResponse(BaseModel):
    answer: str
    suggested_code: str

@router.post("/ai-assist", response_model=AIAssistResponse)
def ai_assist(req: AIAssistRequest):
    full_answer, suggested_code = run_ai_assist(
        question=req.question,
        dag_code=req.dag_code
    )
    return AIAssistResponse(answer=full_answer, suggested_code=suggested_code)
