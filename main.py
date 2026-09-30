from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv('.env')
from routes.base import base_router

app = FastAPI(
    title="Mini RAG API",
    version="0.1.0",
)
API_PREFIX = "/api/v1"


app.include_router(base_router, prefix=API_PREFIX)
