from fastapi import FastAPI
from pydantic import BaseModel
from routes.base import base_router
from routes.data import data_router
from helpers.config import get_settings
settings = get_settings()
API_PREFIX = settings.api_prefix
app = FastAPI(
    title="Mini RAG API",
    version="0.1.0",
)


app.include_router(base_router, prefix=API_PREFIX)
app.include_router(data_router, prefix=API_PREFIX)
