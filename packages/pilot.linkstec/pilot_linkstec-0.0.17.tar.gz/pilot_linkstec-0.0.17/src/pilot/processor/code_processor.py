from abc import ABC, abstractmethod
from typing import List


class CodeProcessor(ABC):
    @abstractmethod
    def process(self, lines: List[str]) -> List[str]:
        pass
