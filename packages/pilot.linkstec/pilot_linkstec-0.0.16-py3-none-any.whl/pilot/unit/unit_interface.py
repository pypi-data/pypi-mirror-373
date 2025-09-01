from abc import ABC, abstractmethod

class UnitInterface(ABC):
    @abstractmethod
    def run(self):
        pass

    def job_not_run(self):
        pass

