from abc import ABC, abstractmethod

class JobInterface(ABC):
    @abstractmethod
    def run(self):
        pass
