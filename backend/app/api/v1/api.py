from fastapi import APIRouter
from app.api.v1.endpoints import upload, analyze

api_router = APIRouter()
api_router.include_router(upload.router, tags=["upload"])
api_router.include_router(analyze.router, tags=["analyze"])
