from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class Project(BaseModel):
    _id: Optional[ObjectId] = None

    project_id: str

    name: Optional[str] = Field(
        default=None,
        min_length=1
    )

    description: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True