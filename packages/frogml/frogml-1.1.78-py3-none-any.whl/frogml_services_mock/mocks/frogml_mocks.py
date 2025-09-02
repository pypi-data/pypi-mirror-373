import dataclasses

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


@dataclasses.dataclass
class FrogmlMocks:
    port: int
    build_orchestrator_build_api: BuildOrchestratorBuildApiMock
    build_orchestrator_service_api: BuildOrchestratorServiceApiMock
    build_orchestrator_build_settings_api: BuildOrchestratorBuildSettingsApiMock
    internal_build_orchestrator_service: InternalBuildOrchestratorServiceMock
    alert_manager_service_mock: AlertManagerServiceApiMock
    automation_management_service_mock: AutomationManagementServiceMock
    job_registry_service_mock: JobRegistryServiceApiMock
    project_manager_service_mock: ProjectManagerServiceMock
    kube_captain_service_mock: KubeCaptainServiceApiMock
    file_versioning_service_mock: FileVersioningServiceMock
    data_versioning_service_mock: DataVersioningServiceMock
    model_management_service_mock: ModelsManagementServiceMock
    model_group_management_service_mock: ModelGroupManagementServiceMock
    logging_service_mock: LoggingServiceApiMock
    autoscaling_service_mock: AutoscalingServiceApiMock
    audience_api_mock: AudienceServiceApiMock
    self_service_user_service_mock: SelfServiceUserServiceMock
    analytics_api_mock: AnalyticsApiMock
    deployment_management_service_mock: DeploymentManagementServiceMock
    batch_job_manager_service: BatchJobManagerService
    ecosystem_client_mock: EcoSystemServiceMock
    user_application_instance_service_mock: UserApplicationInstanceServiceApiMock
    secret_service_mock: SecretServiceMock
    authentication_service_mock: AuthenticationServiceMock
    features_operator_service: FeaturesOperatorV3ServiceMock
    fs_offline_serving_service: FsOfflineServingServiceMock
    fs_data_sources_service: DataSourceServiceMock
    fs_entities_service: EntityServiceMock
    fs_feature_sets_service: FeatureSetServiceMock
    instance_templates_service: InstanceTemplateManagementServiceMock
    alerts_registry_service: AlertsRegistryServiceApiMock
    execution_management_service: ExecutionManagementServiceMock
    system_secret_service: SystemSecretServiceMock
    integration_management_service: IntegrationManagementServiceMock
    model_version_manager_service: ModelVersionManagerServiceMock
    repository_service: RepositoryServiceMock
    location_discovery_service: LocationDiscoveryServiceApiMock
    jfrog_tenant_info_service: JFrogTenantInfoServiceMock
