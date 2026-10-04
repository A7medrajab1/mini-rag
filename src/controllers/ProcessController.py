from .BaseController import BaseController
from helpers.config import Settings, get_settings
from fastapi import UploadFile
from .ProjectController import ProjectController
import re
import os
from typing import List
from models import ProcessingEnum
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dataclasses import dataclass

@dataclass
class Document:
    page_content: str
    metadata: dict

class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_controller = ProjectController()
        self.project_path = self.project_controller.get_project_path(project_id=self.project_id)
    
    def get_file_extension(self, file_id: str) -> str:
        return os.path.splitext(file_id)[1].lower()
    
    def get_file_loader(self, file_id: str):
        file_extension = self.get_file_extension(file_id = file_id)
        file_path = os.path.join(self.project_path, file_id)

        if file_extension == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding='utf-8')
        elif file_extension == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id=file_id)
        documents = loader.load()
        return documents
    
    def file_content_text(self, file_id: str):
        documents = self.get_file_content(file_id=file_id)
        content_text = [doc.page_content for doc in documents]
        return content_text
    
    def file_content_metadata(self, file_id: str):
        documents = self.get_file_content(file_id=file_id)
        content_metadata = [doc.metadata for doc in documents]
        return content_metadata

    def process_file_content(self, file_id: str, chunk_size: int, overlap_size: int, do_reset: int):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )

        chunks = text_splitter.create_documents(
            self.file_content_text(file_id=file_id),
            metadatas=self.file_content_metadata(file_id=file_id)
        )
        # chunks = self.process_simpler_splitter(
        #     texts=self.file_content_text(file_id=file_id),
        #     metadatas=self.file_content_metadata(file_id=file_id),
        #     chunk_size=chunk_size,
        #     splitter_tag="\n"
        # )

        return chunks

    # def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        
    #     full_text = " ".join(texts)

    #     # split by splitter_tag
    #     lines = [ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1 ]

    #     chunks = []
    #     current_chunk = ""

    #     for line in lines:
    #         current_chunk += line + splitter_tag
    #         if len(current_chunk) >= chunk_size:
    #             chunks.append(Document(
    #                 page_content=current_chunk.strip(),
    #                 metadata={}
    #             ))

    #             current_chunk = ""

    #     if len(current_chunk) >= 0:
    #         chunks.append(Document(
    #             page_content=current_chunk.strip(),
    #             metadata={}
    #         ))

    #     return chunks