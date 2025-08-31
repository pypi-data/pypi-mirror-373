from __future__ import annotations

from abc import ABC, abstractmethod

from frogml.core.inner.build_config.build_config_v1 import BuildConfigV1
from frogml.core.inner.build_logic.interface.build_logger_interface import BuildLogger
from frogml.core.inner.build_logic.interface.build_phase import BuildPhase
from frogml.core.inner.build_logic.interface.context_interface import Context


class Step(ABC):
    context: Context
    config: BuildConfigV1
    build_logger: BuildLogger
    build_phase: BuildPhase

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self) -> None:
        pass

    def set_logger(self, build_logger: BuildLogger) -> None:
        self.build_logger = build_logger
