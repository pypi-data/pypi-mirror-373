from typing import Dict, Any

from cheshirecat_python_sdk.builders.base import BaseBuilder
from cheshirecat_python_sdk.models.dtos import Memory, Why


class WhyBuilder(BaseBuilder):
    def __init__(self):
        self.input: str | None = None
        self.intermediate_steps: Dict[str, Any] | None = None
        self.memory: Memory | None = None

    @staticmethod
    def create() -> "WhyBuilder":
        return WhyBuilder()

    def set_input(self, input: str | None = None) -> "WhyBuilder":
        self.input = input
        return self

    def set_intermediate_steps(self, intermediate_steps: Dict[str, Any] | None = None) -> "WhyBuilder":
        self.intermediate_steps = intermediate_steps
        return self

    def set_memory(self, memory: Memory) -> "WhyBuilder":
        self.memory = memory
        return self

    def build(self) -> Why:
        return Why(
            input=self.input,
            intermediate_steps=self.intermediate_steps,
            memory=self.memory,
        )
