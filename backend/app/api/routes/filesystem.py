"""File system analyzer API routes."""
from fastapi import APIRouter
from app.models.schemas import ScanRequest
from app.services.fs_analyzer import fs_analyzer

router = APIRouter(prefix="/api/filesystem", tags=["File System"])

@router.post("/scan")
async def scan_directory(request: ScanRequest):
    return fs_analyzer.scan_directory(request.path, request.max_depth)

@router.get("/duplicates")
async def get_duplicates():
    return fs_analyzer.find_duplicates()

@router.get("/junk")
async def get_junk():
    return fs_analyzer.find_junk_files()
