from typing import Dict, List, Any
from pydantic import BaseModel


class FactoryObjectSettingOutput(BaseModel):
    name: str
    value: Dict[str, Any]
    scheme: Dict[str, Any] | None = None

    def __init__(self, /, **data: Any) -> None:
        # if tags is a list, convert it to a comma-separated string
        if "scheme" in data and isinstance(data["scheme"], Dict) and not data["scheme"]:
            data["scheme"] = None
        super().__init__(**data)


class FactoryObjectSettingsOutput(BaseModel):
    settings: List[FactoryObjectSettingOutput]
    selected_configuration: str
