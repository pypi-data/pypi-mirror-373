from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FileSystemConfiguration(ABC):
    @abstractmethod
    def _to_proto(self):
        pass

    @abstractmethod
    def _from_proto(self, proto):
        pass
