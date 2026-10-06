from enum import Enum


class DataBaseEnum(str, Enum):
    COLLECTION_PROJECTS_NAME = "projects"
    COLLECTION_CHUNK_NAME = "chunks"