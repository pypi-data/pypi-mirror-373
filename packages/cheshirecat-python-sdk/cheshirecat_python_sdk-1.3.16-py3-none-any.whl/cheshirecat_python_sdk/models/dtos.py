from typing import Dict, List, Any
from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    output: str | None = None
    intermediate_steps: List[Dict[str, Any]] | None = Field(default_factory=list)
    return_direct: bool = False
    with_llm_error: bool = False


class Memory(BaseModel):
    declarative: List | None = Field(default_factory=list)
    procedural: List | None = Field(default_factory=list)


class MemoryPoint(BaseModel):
    content: str
    metadata: Dict[str, Any]


class MessageBase(BaseModel):
    text: str
    image: str | bytes | None = None


class Message(MessageBase):
    metadata: Dict[str, Any] | None = None


class SettingInput(BaseModel):
    name: str
    value: Dict[str, Any]
    category: str | None = None


class Why(BaseModel):
    input: str | None = None
    intermediate_steps: List | None = Field(default_factory=list)
    memory: Memory = Field(default_factory=Memory)
