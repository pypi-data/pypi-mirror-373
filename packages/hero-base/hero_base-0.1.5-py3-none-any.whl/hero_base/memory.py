from dataclasses import dataclass
import os
from typing import Any, List, overload

import dill

MEMORY_STORAGE_FILENAME = "memory.dill"

@dataclass
class MemoryHints:
    tool: str
    hint: str

class Memory:

    def __init__(self, log_dir: str, hints: List[MemoryHints]) -> None:
        
        self.__memory_dir = os.path.join(log_dir, MEMORY_STORAGE_FILENAME)
        self.hints = hints
        self.records = []

        self.__storage = {}
        if os.path.exists(self.__memory_dir):
            with open(self.__memory_dir, "rb") as f:
                self.__storage = dill.load(f)

    def set(self, key: str, value: Any):
        self.__storage.update({key: value})
        with open(self.__memory_dir, "wb") as f:
            dill.dump(self.__storage, f)

    @overload
    def get(self, key: str) -> Any: ...
    @overload
    def get[T](self, key: str, default: T) -> T: ...
    def get(self, key: str, default=None):
        return self.__storage.get(key, default)
