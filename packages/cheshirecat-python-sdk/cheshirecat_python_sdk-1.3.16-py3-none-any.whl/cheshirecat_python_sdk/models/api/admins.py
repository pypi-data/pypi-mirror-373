from typing import Dict, List, Any
from pydantic import BaseModel

from cheshirecat_python_sdk.models.api.plugins import PluginToggleOutput


class AdminOutput(BaseModel):
    username: str
    permissions: Dict[str, List[str]]
    id: str


class CreatedOutput(BaseModel):
    created: bool


class PluginDeleteOutput(BaseModel):
    deleted: str


class PluginDetailsOutput(BaseModel):
    data: Dict[str, Any]


class PluginInstallFromRegistryOutput(PluginToggleOutput):
    url: str
    info: str


class PluginInstallOutput(PluginToggleOutput):
    filename: str
    content_type: str


class ResetOutput(BaseModel):
    deleted_settings: bool
    deleted_memories: bool
    deleted_plugin_folders: bool
