from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str
    chunk_size: Optional[int] = 1024 * 1024  # Default chunk size of 1MB
    overlap_size: Optional[int] = 10  # Default overlap size of 0 bytes
    do_reset: Optional[int] = 0  # Default is not to reset the process