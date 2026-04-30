"""Auto-optimization API routes."""
from fastapi import APIRouter
from app.services.optimizer import optimizer

router = APIRouter(prefix="/api/optimizer", tags=["Optimizer"])

@router.get("/suggestions")
async def get_suggestions():
    return optimizer.get_suggestions()

@router.post("/apply/{suggestion_id}")
async def apply_suggestion(suggestion_id: str):
    return optimizer.apply_suggestion(suggestion_id)
