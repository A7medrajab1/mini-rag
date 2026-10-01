from fastapi import FastAPI, APIRouter, Depends
from pydantic import BaseModel
from helpers.config import get_settings, Settings 


base_router = APIRouter(tags=["Base"], prefix="/base")

@base_router.get("/health")
async def health_check(app_settings : Settings = Depends(get_settings)):
    app_settings = get_settings()
    app_name = settings.app_name.value
    app_version = settings.app_version.value
    return {"status": "ok", "app_name": app_name, "app_version": app_version}