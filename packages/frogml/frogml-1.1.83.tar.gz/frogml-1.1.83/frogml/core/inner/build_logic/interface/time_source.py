from abc import ABC, abstractmethod
from time import time


class TimeSource(ABC):
    @abstractmethod
    def current_epoch_time(self) -> int:
        pass


class Stopwatch:
    def __init__(self, time_source: TimeSource):
        self.time_source = time_source
        self.start_time = self.time_source.current_epoch_time()

    def elapsed_time_in_seconds(self) -> int:
        end_time = self.time_source.current_epoch_time()
        return end_time - self.start_time


class SystemClockTimeSource(TimeSource):
    def current_epoch_time(self) -> int:
        return int(time())
