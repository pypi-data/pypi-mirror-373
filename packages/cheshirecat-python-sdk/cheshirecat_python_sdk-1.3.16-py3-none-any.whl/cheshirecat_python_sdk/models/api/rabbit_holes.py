from typing import List
from pydantic import BaseModel


class UploadSingleFileResponse(BaseModel):
    filename: str
    content_type: str
    info: str


class UploadUrlResponse(BaseModel):
    url: str
    info: str


class AllowedMimeTypesOutput(BaseModel):
    allowed: List[str]
