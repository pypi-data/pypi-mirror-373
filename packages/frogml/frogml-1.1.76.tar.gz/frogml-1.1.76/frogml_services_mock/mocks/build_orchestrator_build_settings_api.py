from frogml._proto.qwak.build_settings.build_settings_api_pb2 import (
    GetBuildSettingsRequest,
    GetBuildSettingsResponse,
)
from frogml._proto.qwak.build_settings.build_settings_api_pb2_grpc import (
    BuildSettingsApiServicer,
)
from frogml._proto.qwak.build_settings.build_settings_pb2 import BuildSettings
from frogml_services_mock.mocks.utils.exception_handlers import (
    raise_internal_grpc_error,
)


class BuildOrchestratorBuildSettingsApiMock(BuildSettingsApiServicer):
    def __init__(self):
        self._build_settings = dict()

    def given_build_settings(self, environment_id: str, build_settings: BuildSettings):
        self._build_settings[environment_id] = build_settings

    def GetBuildSettings(
        self, request: GetBuildSettingsRequest, context
    ) -> GetBuildSettingsResponse:
        build_settings = self._build_settings.get(request.environment_id)
        if not build_settings:
            raise_internal_grpc_error(
                context,
                Exception(
                    f"Build settings for environment id {request.environment_id} doesn't exist"
                ),
            )
        return GetBuildSettingsResponse(build_settings=build_settings)
