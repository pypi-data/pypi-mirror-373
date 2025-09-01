from typing import Dict, List, Any
from pydantic import BaseModel


class SettingDeleteOutput(BaseModel):
    deleted: str


class SettingOutputItem(BaseModel):
    setting: Dict


class SettingsOutputCollection(BaseModel):
    settings: List[Dict]
