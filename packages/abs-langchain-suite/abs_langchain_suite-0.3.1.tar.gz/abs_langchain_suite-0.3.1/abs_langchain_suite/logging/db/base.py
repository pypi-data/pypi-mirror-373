from abc import ABC, abstractmethod

class BaseDBClient(ABC):
    @abstractmethod
    def write(self, table: str, data: dict):
        """Write data to the target database."""
        pass
