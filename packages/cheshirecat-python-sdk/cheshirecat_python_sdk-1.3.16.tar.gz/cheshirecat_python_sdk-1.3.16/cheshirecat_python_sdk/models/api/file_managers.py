from typing import List
from pydantic import BaseModel


class FileResponse(BaseModel):
    path: str
    name: str
    size: int
    last_modified: str


class FileManagerAttributes(BaseModel):
    files: List[FileResponse]
    size: int
