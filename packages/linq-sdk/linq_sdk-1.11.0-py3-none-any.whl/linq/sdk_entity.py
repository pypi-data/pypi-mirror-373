from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

OutputType = TypeVar("OutputType")
InputType = TypeVar("InputType")


@dataclass
class SDKEntity(ABC, Generic[InputType, OutputType]):
    @abstractmethod
    def to_api_input(self) -> InputType:
        ...
