"""System metrics API routes."""
from fastapi import APIRouter
from app.services.system_monitor import system_monitor
from app.services.resource_predictor import resource_predictor

router = APIRouter(prefix="/api/system", tags=["System"])

@router.get("/metrics")
async def get_metrics():
    return system_monitor.get_all_metrics()

@router.get("/history")
async def get_history():
    return system_monitor.get_history()

@router.get("/info")
async def get_info():
    return system_monitor.get_system_info()

@router.get("/predictions")
async def get_predictions():
    return resource_predictor.predict_all()
