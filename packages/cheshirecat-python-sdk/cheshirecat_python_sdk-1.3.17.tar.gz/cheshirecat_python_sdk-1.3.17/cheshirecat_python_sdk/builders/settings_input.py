from typing import Dict, Any

from cheshirecat_python_sdk.builders.base import BaseBuilder
from cheshirecat_python_sdk.models.dtos import SettingInput


class SettingInputBuilder(BaseBuilder):
    def __init__(self):
        self.name: str = ""
        self.value: Dict[str, Any] = {}
        self.category: str | None = None

    @staticmethod
    def create():
        return SettingInputBuilder()

    def set_name(self, name: str):
        self.name = name
        return self

    def set_value(self, value: Dict[str, Any]):
        self.value = value
        return self

    def set_category(self, category: str):
        self.category = category
        return self

    def build(self):
        return SettingInput(self.name, self.value, self.category)
