from bson import ObjectId

from .BaseDataModel import BaseDataModel
from .db_schemes.Asset import Asset
from .enums.DataBaseEnum import DataBaseEnum


class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)

        self.db_client = db_client
        self.collection = db_client[
            DataBaseEnum.COLLECTION_ASSET_NAME.value
        ]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        indexes = Asset.get_indexes()

        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(
            asset.model_dump(
                by_alias=True,
                exclude_none=True
            )
        )

        asset.id = result.inserted_id
        return asset

    async def get_assets_by_project_id(
        self,
        project_id: ObjectId
    ):
        cursor = self.collection.find(
            {"asset_project_id": project_id}
        ).sort("asset_pushed_at", -1)

        assets = []

        async for document in cursor:
            assets.append(Asset(**document))

        return assets

    async def get_asset_by_name(
        self,
        project_id: ObjectId,
        asset_name: str
    ):
        document = await self.collection.find_one({
            "asset_project_id": project_id,
            "asset_name": asset_name
        })

        if document is None:
            return None

        return Asset(**document)

    async def delete_asset(self, asset_id: ObjectId):
        result = await self.collection.delete_one({
            "_id": asset_id
        })

        return result.deleted_count

    async def delete_assets_by_project_id(
        self,
        project_id: ObjectId
    ):
        result = await self.collection.delete_many({
            "asset_project_id": project_id
        })

        return result.deleted_count
