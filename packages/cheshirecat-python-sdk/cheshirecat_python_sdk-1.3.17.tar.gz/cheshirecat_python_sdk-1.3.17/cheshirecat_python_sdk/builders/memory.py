from typing import Dict, Any

from cheshirecat_python_sdk.builders.base import BaseBuilder
from cheshirecat_python_sdk.models.dtos import Memory, MemoryPoint


class MemoryBuilder(BaseBuilder):
    def __init__(self):
        self.declarative: Dict[str, Any] | None = None
        self.procedural: Dict[str, Any] | None = None

    @staticmethod
    def create():
        return MemoryBuilder()

    def set_declarative(self, declarative: Dict[str, Any] | None = None):
        self.declarative = declarative or {}
        return self

    def set_procedural(self, procedural: Dict[str, Any] | None = None):
        self.procedural = procedural or {}
        return self

    def build(self):
        memory = Memory()
        memory.declarative = self.declarative
        memory.procedural = self.procedural

        return memory


class MemoryPointBuilder(BaseBuilder):
    def __init__(self):
        self.content: str = ""
        self.metadata: Dict[str, Any] = {}

    @staticmethod
    def create():
        return MemoryPointBuilder()

    def set_content(self, content: str):
        self.content = content
        return self

    def set_metadata(self, metadata: Dict[str, Any]):
        self.metadata = metadata
        return self

    def build(self):
        return MemoryPoint(self.content, self.metadata)