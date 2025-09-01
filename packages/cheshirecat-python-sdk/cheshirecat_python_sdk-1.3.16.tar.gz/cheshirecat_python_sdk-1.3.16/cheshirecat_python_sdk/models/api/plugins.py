from typing import List, Any
from pydantic import BaseModel, Field

from cheshirecat_python_sdk.models.api.nested.plugins import PluginSettingsOutput


class FilterOutput(BaseModel):
    query: str | None = None



class HookOutput(BaseModel):
    name: str
    priority: int


class ToolOutput(BaseModel):
    name: str



class FormOutput(BaseModel):
    name: str


class EndpointOutput(BaseModel):
    name: str
    tags: List[str]


class PluginItemOutput(BaseModel):
    id: str
    name: str
    description: str | None = None
    author_name: str | None = None
    author_url: str | None = None
    plugin_url: str | None = None
    tags: str | None = None
    thumb: str | None = None
    version: str | None = None
    active: bool
    hooks: List[HookOutput]
    tools: List[ToolOutput]
    forms: List[FormOutput]
    endpoints: List[EndpointOutput]

    def __init__(self, /, **data: Any) -> None:
        # if tags is a list, convert it to a comma-separated string
        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = ", ".join(data["tags"])
        super().__init__(**data)


class PluginCollectionOutput(BaseModel):
    filters: FilterOutput
    installed: List[PluginItemOutput] = Field(default_factory=list)
    registry: List["PluginItemRegistryOutput"] = Field(default_factory=list)


class PluginItemRegistryOutput(BaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    author_name: str | None = None
    author_url: str | None = None
    plugin_url: str | None = None
    tags: str | None = None
    thumb: str | None = None
    version: str | None = None
    url: str | None = None

    def __init__(self, /, **data: Any) -> None:
        # if tags is a list, convert it to a comma-separated string
        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = ", ".join(data["tags"])
        super().__init__(**data)


class PluginsSettingsOutput(BaseModel):
    settings: List[PluginSettingsOutput]


class PluginToggleOutput(BaseModel):
    info: str
