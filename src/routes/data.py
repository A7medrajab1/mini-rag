from fastapi import APIRouter, UploadFile, Depends, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
import os
import logging
from .schemes.data import ProcessRequest

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/data",
    tags=["data"]
)


@data_router.post("/upload/{project_id}")
async def upload_data(
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):

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



    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Data uploaded for project {project_id}",
            "file_id": file_id,
        }
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, process_request: ProcessRequest):
    data_controller = DataController()
    # params from the request
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    process_controller = ProcessController(project_id=project_id)
    # file_content = process_controller.get_file_content(file_id=file_id)
    file_chunks = process_controller.process_file_content(
        # file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size,
        do_reset=do_reset
    )

    if not file_chunks:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": f"No chunks were created for file_id {file_id}. Please check the file content and parameters."
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "content": file_chunks[10].page_content,
            "metadata": file_chunks[10].metadata,
            "message": f"Processing data for file_id {file_id} with chunk_size {chunk_size}, overlap_size {process_request.overlap_size}, do_reset {process_request.do_reset}"
        }
    )
