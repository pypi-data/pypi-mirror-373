from abc import ABC, abstractmethod
from typing import Any


class BaseBuilder(ABC):
    @staticmethod
    @abstractmethod
    def create():
        pass

    @abstractmethod
    def build(self) -> Any:
        pass
