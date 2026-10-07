from bson import ObjectId

from .BaseDataModel import BaseDataModel
from .db_schemes.DataChunk import DataChunk
from .enums.DataBaseEnum import DataBaseEnum


class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)

        self.db_client = db_client

        self.collection = db_client[
            DataBaseEnum.COLLECTION_CHUNK_NAME.value
        ]

    async def create_chunk(self, chunk: DataChunk):

        result = await self.collection.insert_one(
            chunk.model_dump(
                by_alias=True,
                exclude_none=True
            )
        )

        chunk.id = result.inserted_id

        return chunk

    async def create_chunks(self, chunks: list[DataChunk]):

        if not chunks:
            return []

        result = await self.collection.insert_many(
            [
                chunk.model_dump(
                    by_alias=True,
                    exclude_none=True
                )
                for chunk in chunks
            ]
        )

        for chunk, inserted_id in zip(
            chunks,
            result.inserted_ids
        ):
            chunk._id = inserted_id

        return chunks

    async def get_chunks_by_project(
        self,
        project_id: ObjectId
    ):

        cursor = (
            self.collection
            .find({
                "chunk_project_id": project_id
            })
            .sort("chunk_order", 1)
        )

        chunks = []

        async for document in cursor:
            chunks.append(
                DataChunk(**document)
            )

        return chunks
    
    async def delete_chunks_by_project_id(
        self,
        project_id: ObjectId
    ):
        result = await self.collection.delete_many(
            {
                "chunk_project_id": project_id
            }
        )

        return result.deleted_count
