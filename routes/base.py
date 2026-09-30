from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
import os

base_router = APIRouter(tags=["Base"], prefix="/base")

@base_router.get("/health")
async def health_check():
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")
    return {"status": "ok", "app_name": app_name, "app_version": app_version}