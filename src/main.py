from fastapi import FastAPI
from pydantic import BaseModel
from routes.base import base_router
from routes.data import data_router
from helpers.config import get_settings
from motors import AsyncIOMotorClient
from helpers.config import Settings, get_settings

settings = get_settings() -> Settings


API_PREFIX = settings.api_prefix
app = FastAPI(
    title = settings.app_name,
    version = settings.app_version,
)

@app.on_event = "startup"
async def startup_db_client():
    # Initialize MongoDB client
    app.state.mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    app.state.mongo_db = app.state.mongo_client[settings.MONGO_DB_NAME]


@app.on_event = "shutdown"
async def shutdown_db_client():
    # Close MongoDB client
    app.state.mongo_client.close()


app.include_router(base_router, prefix=API_PREFIX)
app.include_router(data_router, prefix=API_PREFIX)
