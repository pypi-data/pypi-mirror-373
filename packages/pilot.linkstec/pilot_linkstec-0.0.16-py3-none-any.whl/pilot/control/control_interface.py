from abc import ABC, abstractmethod

class ControlInterface(ABC):
    @abstractmethod
    def run(self):
        pass
