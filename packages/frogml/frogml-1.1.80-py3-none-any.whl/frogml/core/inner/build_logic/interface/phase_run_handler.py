from abc import ABC, abstractmethod
from typing import Optional

from frogml.core.inner.build_logic.interface.build_logger_interface import BuildLogger
from frogml.core.inner.build_logic.interface.build_phase import BuildPhase
from frogml.core.inner.build_logic.phases.phases_pipeline import PhasesPipeline


class PhaseRunHandler(ABC):
    current_phase: PhasesPipeline
    build_logger: Optional[BuildLogger]

    @abstractmethod
    def handle_phase_in_progress(self, build_phase: BuildPhase):
        pass

    @abstractmethod
    def handle_phase_finished_successfully(
        self, build_phase: BuildPhase, duration_in_seconds: int
    ):
        pass

    @abstractmethod
    def handle_contact_support_error(
        self,
        build_id: str,
        build_phase: BuildPhase,
        ex: BaseException,
        duration_in_seconds: int,
    ):
        pass

    @abstractmethod
    def handle_remote_build_error(
        self,
        build_id: str,
        build_phase: BuildPhase,
        ex: BaseException,
        duration_in_seconds: int,
    ):
        pass

    @abstractmethod
    def handle_keyboard_interrupt(
        self, build_id: str, build_phase: BuildPhase, duration_in_seconds: int
    ):
        pass

    @abstractmethod
    def handle_pipeline_exception(
        self,
        build_id: str,
        build_phase: BuildPhase,
        ex: BaseException,
        duration_in_seconds: int,
    ):
        pass

    @abstractmethod
    def handle_pipeline_quiet_exception(
        self,
        build_id: str,
        build_phase: BuildPhase,
        ex: BaseException,
        duration_in_seconds: int,
    ):
        pass

    @abstractmethod
    def handle_current_phase(self, phase: PhasesPipeline):
        pass
