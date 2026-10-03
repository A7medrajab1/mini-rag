from .BaseController import BaseController
from helpers.config import Settings, get_settings
from fastapi import UploadFile
from .ProjectController import ProjectController
import re
import os

class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_controller = ProjectController()
        self.project_path = self.project_controller.get_project_path(project_id=self.project_id)
    
    def get_file_extension(self, filename: str) -> str:
        return os.path.splitext(filename)[1].lower()
    
    
    def process_file(self, file_path: str, chunk_size: int, overlap_size: int, do_reset: int):
        # Implement your file processing logic here
        # For example, you can read the file in chunks and process each chunk
        # You can also handle the overlap between chunks if needed
        # The do_reset parameter can be used to reset any state if required
        pass