from contextlib import contextmanager
from logging import Logger

from frogml.core.exceptions import FrogmlException
from frogml.core.inner.build_logic.build_loggers.trigger_build_logger import (
    TriggerBuildLogger,
)
from frogml.core.inner.build_logic.constants.messages import (
    FAILED_CONTACT_FROGML_SUPPORT_PROGRAMMATIC,
)
from frogml.core.inner.build_logic.interface.build_phase import BuildPhase
from frogml.core.inner.build_logic.interface.phase_run_handler import PhaseRunHandler
from frogml.core.inner.build_logic.phases.phases_pipeline import PhasesPipeline


class ProgrammaticPhaseRunHandler(PhaseRunHandler):
    BUILD_IN_PROGRESS_FORMAT = "Build phase in progress: {}"
    BUILD_FINISHED_FORMAT = "Phase successfully finished: {} after {} seconds"
    BUILD_FAILURE_FORMAT = "Build phase failed: {} after {} seconds"

    def __init__(self, python_logger: Logger, verbose: int, json_logs: bool):
        self.build_logger = None
        self.python_logger = python_logger
        self.json_logs = json_logs
        self.verbose = verbose

    @contextmanager
    def handle_current_phase(self, phase: PhasesPipeline):
        self.build_logger = TriggerBuildLogger(
            self.python_logger,
            prefix="" if self.json_logs else phase.build_phase.description,
            build_phase=phase.build_phase,
        )
        yield

    def handle_phase_in_progress(self, build_phase: BuildPhase):
        logger = self.build_logger or self.python_logger
        logger.debug(f"Build phase in progress: {build_phase.name}")

    def handle_phase_finished_successfully(
        self, build_phase: BuildPhase, duration_in_seconds: int
    ):
        logger = self.build_logger or self.python_logger
        logger.debug(
            f"Phase successfully finished: {build_phase.name} after {duration_in_seconds} seconds"
        )

    def _report_failure(self, build_phase: BuildPhase, duration_in_seconds: int):
        logger = self.build_logger or self.python_logger
        logger.debug(
            self.BUILD_FAILURE_FORMAT.format(build_phase.name, duration_in_seconds)
        )

    def handle_contact_support_error(
        self,
        build_id: str,
        build_phase: BuildPhase,
        ex: BaseException,
        duration_in_seconds: int,
    ):
        print(
            FAILED_CONTACT_FROGML_SUPPORT_PROGRAMMATIC.format(
                build_id=build_id,
            )
        )
        self._report_failure(build_phase, duration_in_seconds)
        raise FrogmlException(str(ex))

    def handle_keyboard_interrupt(
        self, build_id: str, build_phase: BuildPhase, duration_in_seconds: int
    ):
        self._report_failure(build_phase, duration_in_seconds)
        raise FrogmlException("KeyboardInterrupt")

    def handle_pipeline_exception(
        self,
        build_id: str,
        build_phase: BuildPhase,
        ex: BaseException,
        duration_in_seconds: int,
    ):
        self._report_failure(build_phase, duration_in_seconds)
        raise FrogmlException(str(ex))

    def handle_pipeline_quiet_exception(
        self,
        build_id: str,
        build_phase: BuildPhase,
        ex: BaseException,
        duration_in_seconds: int,
    ):
        self._report_failure(build_phase, duration_in_seconds)

    def handle_remote_build_error(
        self,
        build_id: str,
        build_phase: BuildPhase,
        ex: BaseException,
        duration_in_seconds: int,
    ):
        self.handle_pipeline_exception(build_id, build_phase, ex, duration_in_seconds)
