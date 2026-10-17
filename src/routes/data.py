from fastapi import APIRouter, UploadFile, Depends, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
import os
from bson import ObjectId
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes.DataChunk import DataChunk
from models.db_schemes.Asset import Asset
from models.enums.AssetTypeEnum import AssetTypeEnum


logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/data",
    tags=["data"]
)


@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    data_controller = DataController()

    is_valid = data_controller.validate_file_extension(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Invalid file type or size."
            }
        )


    project_controller = ProjectController()
    project_dir_path = project_controller.get_project_path(project_id=project_id)
    # file_path = os.path.join(project_dir_path, file.filename)
    file_path, file_id = data_controller.generate_unique_filepath(original_filename=file.filename, project_id=project_id)

    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": f"Failed to upload file: {str(e)}"
            }
        )
    
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db
    )

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(
        asset=asset_resource
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Data uploaded for project {project_id}",
            # "file_id": file_id,
            "file_id": str(asset_record.id)
        }
    )
    



@data_router.post("/process/{project_id}")
async def process_endpoint(
    request: Request,
    project_id: str,
    process_request: ProcessRequest
):
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client=request.app.db
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    asset_model = await AssetModel.create_instance(
        db_client=request.app.db
    )

    # Get one requested file, or all files in the project
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "File not found"}
            )

        project_files = [asset_record]

    else:
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value
        )

    if not project_files:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "No files found!"}
        )

    chunk_model = await ChunkModel.create_instance(
        db_client=request.app.db
    )

    process_controller = ProcessController(
        project_id=project_id
    )

    # Reset chunks for the selected asset, or the entire project
    if do_reset:
        if process_request.file_id:
            await chunk_model.delete_chunks_by_asset_id(
                asset_id=project_files[0].id,
                project_id=project.id
            )
        else:
            await chunk_model.delete_chunks_by_project_id(
                project_id=project.id
            )

    total_chunks = 0
    files_processed = 0

    for asset in project_files:
        try:
            file_content = process_controller.get_file_content(
                file_id=asset.asset_name
            )

            if not file_content:
                logger.warning(
                    f"No content found for {asset.asset_name}"
                )
                continue

            file_chunks = process_controller.process_file_content(
                file_content=file_content,
                file_id=asset.asset_name,
                chunk_size=chunk_size,
                overlap_size=overlap_size
            )

            if not file_chunks:
                continue

            data_chunks = [
                DataChunk(
                    chunk_text=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order=index + 1,
                    chunk_project_id=project.id,
                    chunk_asset_id=asset.id
                )
                for index, chunk in enumerate(file_chunks)
            ]

            await chunk_model.create_chunks(data_chunks)

            total_chunks += len(data_chunks)
            files_processed += 1

        except FileNotFoundError:
            logger.exception(
                f"File not found on disk: {asset.asset_name}"
            )
            continue

    if total_chunks == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Processing failed: no chunks created"
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Successfully created {total_chunks} chunks.",
            "project_id": project_id,
            "files_processed": files_processed,
            "chunks_count": total_chunks
        }
    )