import os

from .account import UserAccountConfiguration
from .containers import FrogmlContainer


def wire_dependencies():
    container = FrogmlContainer()

    default_config_file = os.path.join(os.path.dirname(__file__), "config.yml")
    container.config.from_yaml(default_config_file)

    from frogml.core.clients import (
        kube_deployment_captain,
        model_version_manager,
        analytics,
        system_secret,
        autoscaling,
        build_orchestrator,
        batch_job_management,
        instance_template,
        feature_store,
        deployment,
        user_application_instance,
        jfrog_gateway,
        alert_management,
        integration_management,
        model_management,
        audience,
        data_versioning,
        project,
        logging_client,
        automation_management,
        file_versioning,
        alerts_registry,
        administration,
        model_group_management,
    )

    container.wire(
        packages=[
            administration,
            alert_management,
            audience,
            automation_management,
            autoscaling,
            analytics,
            batch_job_management,
            build_orchestrator,
            data_versioning,
            deployment,
            file_versioning,
            instance_template,
            kube_deployment_captain,
            logging_client,
            model_management,
            project,
            feature_store,
            user_application_instance,
            alerts_registry,
            integration_management,
            system_secret,
            model_version_manager,
            jfrog_gateway,
            model_group_management,
        ]
    )

    return container
