from concurrent import futures
from typing import Any, Generator, List, Tuple

import grpc
import pytest

from frogml._proto.qwak.model_group.model_group_pb2_grpc import add_ModelGroupManagementServiceServicer_to_server
from frogml.core.inner.di_configuration import FrogmlContainer
from frogml._proto.jfml.model_version.v1.model_version_manager_service_pb2_grpc import (
    add_ModelVersionManagerServiceServicer_to_server,
)
from frogml._proto.qwak.administration.v0.authentication.authentication_service_pb2_grpc import (
    add_AuthenticationServiceServicer_to_server,
)
from frogml._proto.qwak.admiral.secret.v0.system_secret_service_pb2_grpc import (
    add_SystemSecretServiceServicer_to_server,
)
from frogml._proto.qwak.admiral.user_application_instance.v0.user_application_instance_service_pb2_grpc import (
    add_UserApplicationInstanceServiceServicer_to_server,
)
from frogml._proto.qwak.analytics.analytics_service_pb2_grpc import (
    add_AnalyticsQueryServiceServicer_to_server,
)
from frogml._proto.qwak.audience.v1.audience_api_pb2_grpc import (
    add_AudienceAPIServicer_to_server,
)
from frogml._proto.qwak.auto_scaling.v1.auto_scaling_service_pb2_grpc import (
    add_AutoScalingServiceServicer_to_server,
)
from frogml._proto.qwak.automation.v1.automation_management_service_pb2_grpc import (
    add_AutomationManagementServiceServicer_to_server,
)
from frogml._proto.qwak.batch_job.v1.batch_job_service_pb2_grpc import (
    add_BatchJobManagementServiceServicer_to_server,
)
from frogml._proto.qwak.build.v1.build_api_pb2_grpc import add_BuildAPIServicer_to_server
from frogml._proto.qwak.build_settings.build_settings_api_pb2_grpc import (
    add_BuildSettingsApiServicer_to_server,
)
from frogml._proto.qwak.builds.builds_orchestrator_service_pb2_grpc import (
    add_BuildsOrchestratorServiceServicer_to_server,
)
from frogml._proto.qwak.builds.internal_builds_orchestrator_service_pb2_grpc import (
    add_InternalBuildsOrchestratorServiceServicer_to_server,
)
from frogml._proto.qwak.data_versioning.data_versioning_service_pb2_grpc import (
    add_DataVersioningManagementServiceServicer_to_server,
)
from frogml._proto.qwak.deployment.alert_service_pb2_grpc import (
    add_AlertManagementServiceServicer_to_server,
)
from frogml._proto.qwak.deployment.deployment_service_pb2_grpc import (
    add_DeploymentManagementServiceServicer_to_server,
)
from frogml._proto.qwak.ecosystem.jfrog.v0.jfrog_tenant_info_service_pb2_grpc import \
    add_JFrogTenantInfoServiceServicer_to_server
from frogml._proto.qwak.ecosystem.v0.ecosystem_runtime_service_pb2_grpc import (
    add_QwakEcosystemRuntimeServicer_to_server as add_FrogmlEcosystemRuntimeServicer_to_server,
)
from frogml._proto.qwak.execution.v1.execution_service_pb2_grpc import (
    add_FeatureStoreExecutionServiceServicer_to_server,
)
from frogml._proto.qwak.feature_store.entities.entity_service_pb2_grpc import (
    add_EntityServiceServicer_to_server,
)
from frogml._proto.qwak.feature_store.features.feature_set_service_pb2_grpc import (
    add_FeatureSetServiceServicer_to_server,
)
from frogml._proto.qwak.feature_store.jobs.v1.job_service_pb2_grpc import (
    add_JobServiceServicer_to_server,
)
from frogml._proto.qwak.feature_store.sources.data_source_service_pb2_grpc import (
    add_DataSourceServiceServicer_to_server,
)
from frogml._proto.qwak.features_operator.v3.features_operator_async_service_pb2_grpc import (
    add_FeaturesOperatorAsyncServiceServicer_to_server,
)
from frogml._proto.qwak.file_versioning.file_versioning_service_pb2_grpc import (
    add_FileVersioningManagementServiceServicer_to_server,
)
from frogml._proto.qwak.instance_template.instance_template_service_pb2_grpc import (
    add_InstanceTemplateManagementServiceServicer_to_server,
)
from frogml._proto.qwak.integration.integration_service_pb2_grpc import (
    add_IntegrationManagementServiceServicer_to_server,
)
from frogml._proto.qwak.jfrog.gateway.v0.repository_service_pb2_grpc import (
    add_RepositoryServiceServicer_to_server,
)
from frogml._proto.qwak.kube_deployment_captain.kube_deployment_captain_service_pb2_grpc import (
    add_KubeDeploymentCaptainServicer_to_server,
)
from frogml._proto.qwak.logging.log_reader_service_pb2_grpc import (
    add_LogReaderServiceServicer_to_server,
)
from frogml._proto.qwak.models.models_pb2_grpc import (
    add_ModelsManagementServiceServicer_to_server,
)
from frogml._proto.qwak.monitoring.v0.alerting_channel_management_service_pb2_grpc import (
    add_AlertingChannelManagementServiceServicer_to_server,
)
from frogml._proto.qwak.offline.serving.v1.offline_serving_async_service_pb2_grpc import (
    add_FeatureStoreOfflineServingAsyncServiceServicer_to_server,
)
from frogml._proto.qwak.projects.projects_pb2_grpc import (
    add_ProjectsManagementServiceServicer_to_server,
)
from frogml._proto.qwak.secret_service.secret_service_pb2_grpc import (
    add_SecretServiceServicer_to_server,
)
from frogml._proto.qwak.self_service.user.v1.user_service_pb2_grpc import (
    add_UserServiceServicer_to_server,
)
from frogml._proto.qwak.service_discovery.service_discovery_location_service_pb2_grpc import (
    add_LocationDiscoveryServiceServicer_to_server,
)
from frogml_services_mock.mocks.alert_manager_service_api import (
    AlertManagerServiceApiMock,
)
from frogml_services_mock.mocks.alert_registry_service_api import (
    AlertsRegistryServiceApiMock,
)
from frogml_services_mock.mocks.analytics_api import AnalyticsApiMock
from frogml_services_mock.mocks.audience_service_api import AudienceServiceApiMock
from frogml_services_mock.mocks.authentication_service import AuthenticationServiceMock
from frogml_services_mock.mocks.automation_management_service import (
    AutomationManagementServiceMock,
)
from frogml_services_mock.mocks.autoscaling_service_api import AutoscalingServiceApiMock
from frogml_services_mock.mocks.batch_job_manager_service import BatchJobManagerService
from frogml_services_mock.mocks.build_orchestrator_build_api import (
    BuildOrchestratorBuildApiMock,
)
from frogml_services_mock.mocks.build_orchestrator_build_settings_api import (
    BuildOrchestratorBuildSettingsApiMock,
)
from frogml_services_mock.mocks.build_orchestrator_service_api import (
    BuildOrchestratorServiceApiMock,
)
from frogml_services_mock.mocks.data_versioning_service import DataVersioningServiceMock
from frogml_services_mock.mocks.deployment_management_service import (
    DeploymentManagementServiceMock,
)
from frogml_services_mock.mocks.ecosystem_service_api import EcoSystemServiceMock
from frogml_services_mock.mocks.execution_management_service import (
    ExecutionManagementServiceMock,
)
from frogml_services_mock.mocks.feature_store_data_sources_manager_api import (
    DataSourceServiceMock,
)
from frogml_services_mock.mocks.feature_store_entities_manager_api import (
    EntityServiceMock,
)
from frogml_services_mock.mocks.feature_store_feature_set_manager_api import (
    FeatureSetServiceMock,
)
from frogml_services_mock.mocks.features_operator_v3_service import (
    FeaturesOperatorV3ServiceMock,
)
from frogml_services_mock.mocks.file_versioning_service import FileVersioningServiceMock
from frogml_services_mock.mocks.frogml_mocks import FrogmlMocks
from frogml_services_mock.mocks.fs_offline_serving_service import (
    FsOfflineServingServiceMock,
)
from frogml_services_mock.mocks.instance_template_management_service import (
    InstanceTemplateManagementServiceMock,
)
from frogml_services_mock.mocks.integration_management_service import (
    IntegrationManagementServiceMock,
)
from frogml_services_mock.mocks.internal_build_orchestrator_service import (
    InternalBuildOrchestratorServiceMock,
)
from frogml_services_mock.mocks.jfrog_tenant_info_service_mock import JFrogTenantInfoServiceMock
from frogml_services_mock.mocks.job_registry_service_api import (
    JobRegistryServiceApiMock,
)
from frogml_services_mock.mocks.kube_captain_service_api import (
    KubeCaptainServiceApiMock,
)
from frogml_services_mock.mocks.location_discovery_service_api import (
    LocationDiscoveryServiceApiMock,
)
from frogml_services_mock.mocks.logging_service import LoggingServiceApiMock
from frogml_services_mock.mocks.model_group_management_service import ModelGroupManagementServiceMock
from frogml_services_mock.mocks.model_management_service import (
    ModelsManagementServiceMock,
)
from frogml_services_mock.mocks.model_version_manager_service import (
    ModelVersionManagerServiceMock,
)
from frogml_services_mock.mocks.project_manager_service import ProjectManagerServiceMock
from frogml_services_mock.mocks.repository_service_mock import RepositoryServiceMock
from frogml_services_mock.mocks.secret_service import SecretServiceMock
from frogml_services_mock.mocks.self_service_user_service import (
    SelfServiceUserServiceMock,
)
from frogml_services_mock.mocks.system_secret_service import SystemSecretServiceMock
from frogml_services_mock.mocks.user_application_instance_service_api import (
    UserApplicationInstanceServiceApiMock,
)
from frogml_services_mock.utils.service_utils import find_free_port


def frogml_container():
    free_port = find_free_port()
    container = FrogmlContainer(
        config={
            "grpc": {
                "core": {
                    "address": f"localhost:{free_port}",
                    "enable_ssl": False,
                },
                "builds": {
                    "internal_address": f"localhost:{free_port}",
                    "enable_ssl": False,
                },
                "authentication": {
                    "enable_ssl": False,
                },
            },
        },
    )
    from frogml.core.clients import kube_deployment_captain
    from frogml.core.clients import model_version_manager
    from frogml.core.clients import analytics
    from frogml.core.clients import autoscaling
    from frogml.core.clients import build_orchestrator
    from frogml.core.clients import batch_job_management
    from frogml.core.clients import instance_template
    from frogml.core.clients import feature_store
    from frogml.core.clients import deployment
    from frogml.core.clients import user_application_instance
    from frogml.core.clients import jfrog_gateway
    from frogml.core.clients import location_discovery
    from frogml.core.clients import alert_management
    from frogml.core.clients import model_management
    from frogml.core.clients import model_group_management
    from frogml.core.clients import audience
    from frogml.core.clients import data_versioning
    from frogml.core.clients import project
    from frogml.core.clients import logging_client
    from frogml.core.clients import automation_management
    from frogml.core.clients import file_versioning
    from frogml.core.clients import alerts_registry
    from frogml.core.clients import secret_service
    from frogml.core.clients.administration import eco_system
    from frogml.core.clients.administration import self_service
    from frogml.core.clients.administration import authentication
    from frogml.core.clients.integration_management import integration_manager_client
    from frogml.core.clients.system_secret import system_secret_client

    container.wire(
        packages=[
            authentication,
            alert_management,
            audience,
            automation_management,
            autoscaling,
            analytics,
            batch_job_management,
            build_orchestrator,
            data_versioning,
            deployment,
            instance_template,
            feature_store,
            file_versioning,
            kube_deployment_captain,
            logging_client,
            model_management,
            project,
            self_service,
            eco_system,
            user_application_instance,
            secret_service,
            alerts_registry,
            integration_manager_client,
            system_secret_client,
            model_group_management,
            model_version_manager,
            jfrog_gateway,
            location_discovery,
        ]
    )

    return free_port


def frogml_service_mock_creator(
    server, mocks: List[Tuple[Any, Any, Any]]
) -> FrogmlMocks:
    activated_mocks = {
        mock[0]: mock[1]() if callable(mock[1]) else mock[1] for mock in mocks
    }
    frogml_mocks = FrogmlMocks(**activated_mocks)
    for property_name, value, servicer in mocks:
        if servicer:
            servicer(getattr(frogml_mocks, property_name), server)

    return frogml_mocks


def attach_servicers(free_port, server):
    frogml_mocks = frogml_service_mock_creator(
        server,
        [
            (
                "integration_management_service",
                IntegrationManagementServiceMock,
                add_IntegrationManagementServiceServicer_to_server,
            ),
            (
                "system_secret_service",
                SystemSecretServiceMock,
                add_SystemSecretServiceServicer_to_server,
            ),
            (
                "autoscaling_service_mock",
                AutoscalingServiceApiMock,
                add_AutoScalingServiceServicer_to_server,
            ),
            (
                "build_orchestrator_build_api",
                BuildOrchestratorBuildApiMock,
                add_BuildAPIServicer_to_server,
            ),
            (
                "build_orchestrator_service_api",
                BuildOrchestratorServiceApiMock,
                add_BuildsOrchestratorServiceServicer_to_server,
            ),
            (
                "build_orchestrator_build_settings_api",
                BuildOrchestratorBuildSettingsApiMock,
                add_BuildSettingsApiServicer_to_server,
            ),
            (
                "internal_build_orchestrator_service",
                InternalBuildOrchestratorServiceMock,
                add_InternalBuildsOrchestratorServiceServicer_to_server,
            ),
            (
                "alert_manager_service_mock",
                AlertManagerServiceApiMock,
                add_AlertManagementServiceServicer_to_server,
            ),
            (
                "automation_management_service_mock",
                AutomationManagementServiceMock,
                add_AutomationManagementServiceServicer_to_server,
            ),
            (
                "ecosystem_client_mock",
                EcoSystemServiceMock,
                add_FrogmlEcosystemRuntimeServicer_to_server,
            ),
            (
                "job_registry_service_mock",
                JobRegistryServiceApiMock,
                add_JobServiceServicer_to_server,
            ),
            (
                "project_manager_service_mock",
                ProjectManagerServiceMock,
                add_ProjectsManagementServiceServicer_to_server,
            ),
            (
                "kube_captain_service_mock",
                KubeCaptainServiceApiMock,
                add_KubeDeploymentCaptainServicer_to_server,
            ),
            (
                "file_versioning_service_mock",
                FileVersioningServiceMock,
                add_FileVersioningManagementServiceServicer_to_server,
            ),
            (
                "data_versioning_service_mock",
                DataVersioningServiceMock,
                add_DataVersioningManagementServiceServicer_to_server,
            ),
            (
                "model_management_service_mock",
                ModelsManagementServiceMock,
                add_ModelsManagementServiceServicer_to_server,
            ),
            (
                "model_group_management_service_mock",
                ModelGroupManagementServiceMock,
                add_ModelGroupManagementServiceServicer_to_server,
            ),
            (
                "logging_service_mock",
                LoggingServiceApiMock,
                add_LogReaderServiceServicer_to_server,
            ),
            (
                "audience_api_mock",
                AudienceServiceApiMock,
                add_AudienceAPIServicer_to_server,
            ),
            (
                "self_service_user_service_mock",
                SelfServiceUserServiceMock,
                add_UserServiceServicer_to_server,
            ),
            (
                "analytics_api_mock",
                AnalyticsApiMock,
                add_AnalyticsQueryServiceServicer_to_server,
            ),
            (
                "deployment_management_service_mock",
                DeploymentManagementServiceMock,
                add_DeploymentManagementServiceServicer_to_server,
            ),
            (
                "batch_job_manager_service",
                BatchJobManagerService,
                add_BatchJobManagementServiceServicer_to_server,
            ),
            (
                "user_application_instance_service_mock",
                UserApplicationInstanceServiceApiMock,
                add_UserApplicationInstanceServiceServicer_to_server,
            ),
            (
                "secret_service_mock",
                SecretServiceMock,
                add_SecretServiceServicer_to_server,
            ),
            (
                "authentication_service_mock",
                AuthenticationServiceMock,
                add_AuthenticationServiceServicer_to_server,
            ),
            (
                "fs_entities_service",
                EntityServiceMock,
                add_EntityServiceServicer_to_server,
            ),
            (
                "fs_feature_sets_service",
                FeatureSetServiceMock,
                add_FeatureSetServiceServicer_to_server,
            ),
            (
                "fs_data_sources_service",
                DataSourceServiceMock,
                add_DataSourceServiceServicer_to_server,
            ),
            (
                "features_operator_service",
                FeaturesOperatorV3ServiceMock,
                add_FeaturesOperatorAsyncServiceServicer_to_server,
            ),
            (
                "fs_offline_serving_service",
                FsOfflineServingServiceMock,
                add_FeatureStoreOfflineServingAsyncServiceServicer_to_server,
            ),
            (
                "instance_templates_service",
                InstanceTemplateManagementServiceMock,
                add_InstanceTemplateManagementServiceServicer_to_server,
            ),
            (
                "alerts_registry_service",
                AlertsRegistryServiceApiMock,
                add_AlertingChannelManagementServiceServicer_to_server,
            ),
            (
                "execution_management_service",
                ExecutionManagementServiceMock,
                add_FeatureStoreExecutionServiceServicer_to_server,
            ),
            (
                "model_version_manager_service",
                ModelVersionManagerServiceMock,
                add_ModelVersionManagerServiceServicer_to_server,
            ),
            (
                "repository_service",
                RepositoryServiceMock,
                add_RepositoryServiceServicer_to_server,
            ),
            (
                "location_discovery_service",
                LocationDiscoveryServiceApiMock,
                add_LocationDiscoveryServiceServicer_to_server,
            ),
            (
                "jfrog_tenant_info_service",
                JFrogTenantInfoServiceMock,
                add_JFrogTenantInfoServiceServicer_to_server,
            ),
            ("port", free_port, None),
        ],
    )
    return frogml_mocks


@pytest.fixture
def frogml_services_mock() -> Generator[FrogmlMocks, None, None]:
    free_port = frogml_container()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    frogml_mocks: FrogmlMocks = attach_servicers(free_port, server)

    server.add_insecure_port(f"[::]:{free_port}")
    server.start()

    yield frogml_mocks

    server.stop(0)
