from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Literal


@dataclass
class InputItem:
    type: Literal["text", "file", "image", "audio", "video"]
    value: str

type Input = str | list[InputItem]

@dataclass
class StartChunk:
    def __post_init__(self):
        self.type = "start"


@dataclass
class CompletedChunk:
    content: str
    reasoning_content: str

    def __post_init__(self):
        self.type = "completed"


@dataclass
class ReasoningChunk:
    content: str

    def __post_init__(self):
        self.type = "reasoning"


@dataclass
class ContentChunk:
    content: str

    def __post_init__(self):
        self.type = "message"


@dataclass
class UsageChunk:
    usage: dict

    def __post_init__(self):
        self.type = "usage"


type GenerationChunk = StartChunk | CompletedChunk | ContentChunk | ReasoningChunk | UsageChunk

class BasicModel(ABC):
    @abstractmethod
    def generate(self, system: str, input: Input, *args, **kwargs) ->  AsyncGenerator[GenerationChunk, None]:
        pass