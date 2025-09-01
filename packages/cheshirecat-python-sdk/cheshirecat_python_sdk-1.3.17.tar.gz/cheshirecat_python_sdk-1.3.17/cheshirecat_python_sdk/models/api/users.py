from typing import Dict, List
from pydantic import BaseModel


class UserOutput(BaseModel):
    username: str
    permissions: Dict[str, List[str]]
    id: str
