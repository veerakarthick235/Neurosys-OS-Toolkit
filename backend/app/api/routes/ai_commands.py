"""AI command interpreter API routes."""
from fastapi import APIRouter
from app.models.schemas import AICommandRequest
from app.services.ai_engine import ai_engine

router = APIRouter(prefix="/api/ai", tags=["AI Commands"])

@router.post("/interpret")
async def interpret_command(request: AICommandRequest):
    return ai_engine.interpret(request.query)

@router.post("/execute")
async def execute_command(request: AICommandRequest):
    interpretation = ai_engine.interpret(request.query)
    return ai_engine.execute(interpretation)

@router.get("/prompts")
async def get_sample_prompts():
    return ai_engine.get_sample_prompts()
