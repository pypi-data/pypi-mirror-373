from frogml.core.inner.build_config.build_config_v1 import BuildConfigV1
from frogml.core.inner.build_logic.interface.build_phase import BuildPhase
from frogml.core.inner.build_logic.phases.phase_010_fetch_model.fetch_model_step import (
    FetchModelStep,
)
from frogml.core.inner.build_logic.phases.phase_010_fetch_model.post_fetch_validation_step import (
    PostFetchValidationStep,
)
from frogml.core.inner.build_logic.phases.phase_010_fetch_model.pre_fetch_validation_step import (
    PreFetchValidationStep,
)
from frogml.core.inner.build_logic.phases.phase_010_fetch_model.set_version_step import (
    SetVersionStep,
)
from frogml.core.inner.build_logic.phases.phase_020_remote_register_frogml_build.cleanup_step import (
    CleanupStep,
)
from frogml.core.inner.build_logic.phases.phase_020_remote_register_frogml_build.start_remote_build_step import (
    StartRemoteBuildStep,
)
from frogml.core.inner.build_logic.phases.phase_020_remote_register_frogml_build.upload_step import (
    UploadStep,
)
from frogml.core.inner.build_logic.phases.phases_pipeline import PhasesPipeline
from frogml.core.inner.build_logic.trigger_build_context import TriggerBuildContext

FETCHING_MODEL_CODE_PHASE: str = "FETCHING_MODEL_CODE"
REGISTERING_FROGML_BUILD_PHASE: str = "REGISTERING_FROGML_BUILD"


def get_trigger_build_api_steps(
    config: BuildConfigV1, context: TriggerBuildContext
) -> PhasesPipeline:
    steps_root = PhasesPipeline(config=config, context=context)
    steps_root.add_phase(
        steps=[
            SetVersionStep(),
            PreFetchValidationStep(),
            FetchModelStep(),
            PostFetchValidationStep(),
        ],
        build_phase=BuildPhase(phase_id=FETCHING_MODEL_CODE_PHASE),
    )
    steps_root.add_phase(
        steps=[
            UploadStep(),
            StartRemoteBuildStep(),
            CleanupStep(),
        ],
        build_phase=BuildPhase(phase_id=REGISTERING_FROGML_BUILD_PHASE),
    )

    return steps_root
