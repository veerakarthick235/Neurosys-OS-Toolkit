"""Log analyzer API routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.log_analyzer import log_analyzer

router = APIRouter(prefix="/api/logs", tags=["Logs"])

class LogContentRequest(BaseModel):
    content: str

@router.get("/system")
async def get_system_logs(max_lines: int = 100):
    return log_analyzer.get_system_logs(max_lines=max_lines)

@router.post("/analyze")
async def analyze_logs(request: LogContentRequest):
    return log_analyzer.analyze_log_content(request.content)
