from .BaseController import BaseController
from helpers.config import Settings, get_settings
from fastapi import UploadFile
from .ProjectController import ProjectController
import re
import os

class DataController(BaseController):

    def __init__(self):
        super().__init__()

    def validate_file_extension(self, file: UploadFile):

        allowed_types = self.app_settings.ALLOWED_FILE_TYPES

        if file.content_type not in allowed_types:
            return False

        max_size = self.app_settings.FILE_MAX_SIZE_MB * 1024 * 1024

        if file.size is not None and file.size > max_size:
            return False

        return True
    
    def generate_file_name(self, original_filename: str, project_id: str):
        random_file_name = self.generate_random_string()
        prject_path = ProjectController().get_project_path(project_id=project_id)
        clean_filename = self.get_clean_file_name(original_filename)
        new_file_path = os.path.join(prject_path, f"{random_file_name}_{clean_filename}")

        while os.path.exists(new_file_path):
            random_file_name = self.generate_file_name(original_filename, project_id)
            new_file_path = os.path.join(prject_path, f"{random_file_name}_{clean_filename}")
        return new_file_path
    
    def get_clean_file_name(self, original_filename: str):
        clean_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', original_filename)
        return clean_filename
