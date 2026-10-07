from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict


class Project(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_id: str
    name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )