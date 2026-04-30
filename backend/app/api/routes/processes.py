"""Process management API routes."""
from fastapi import APIRouter, Query
from app.services.process_manager import process_manager

router = APIRouter(prefix="/api/processes", tags=["Processes"])

@router.get("/")
async def list_processes(sort_by: str = Query("cpu", enum=["cpu", "memory", "pid", "name"]), limit: int = Query(100, ge=1, le=500)):
    return process_manager.get_all_processes(sort_by=sort_by, limit=limit)

@router.get("/top")
async def top_processes(n: int = Query(10, ge=1, le=50), by: str = Query("cpu", enum=["cpu", "memory"])):
    return process_manager.get_top_processes(n=n, by=by)

@router.get("/search")
async def search_processes(q: str = Query(..., min_length=1)):
    return process_manager.search_processes(q)

@router.post("/{pid}/kill")
async def kill_process(pid: int):
    return process_manager.kill_process(pid)
