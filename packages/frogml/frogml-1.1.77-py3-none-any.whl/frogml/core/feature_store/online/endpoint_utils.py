import os
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from frogml._proto.qwak.administration.account.v1.account_pb2 import AccountType
from frogml._proto.qwak.ecosystem.v0.ecosystem_pb2 import (
    AuthenticatedUnifiedUserContext,
)
from frogml.core.exceptions import FrogmlException

_ONLINE_SERVING_ENDPOINT_OVERRIDE_ENV_VAR = "ONLINE_SERVING_ENDPOINT"
_default_endpoint_url = "fs-serving-webapp.frogml.svc.cluster.local:6577/com.frogml.ai.feature.store.serving.api.ServingService"


@dataclass
class EndpointConfig:
    endpoint_url: str
    metadata: Optional[Sequence[Tuple[str, str]]]
    enable_ssl: Optional[bool]


def _get_direct_endpoint(
    user_context: AuthenticatedUnifiedUserContext,
) -> EndpointConfig:
    endpoint_url: str = os.environ.get(
        _ONLINE_SERVING_ENDPOINT_OVERRIDE_ENV_VAR, _default_endpoint_url
    )
    # As of time of writing, feature-store is single env!
    metadata = (
        ("frogml-user-id", user_context.user_id),
        ("frogml-account-id", user_context.account_details.id),
        ("frogml-environment-id", user_context.account_details.default_environment_id),
    )

    return EndpointConfig(
        endpoint_url=endpoint_url, metadata=metadata, enable_ssl=False
    )


def _get_edge_services_endpoint(
    user_context: AuthenticatedUnifiedUserContext,
) -> EndpointConfig:
    environment_id: str = user_context.account_details.default_environment_id

    if environment_id not in user_context.account_details.environment_by_id:
        raise FrogmlException(
            f"Configuration for environment [{environment_id}] was not found"
        )

    endpoint_url: str = user_context.account_details.environment_by_id[
        environment_id
    ].configuration.edge_services_url

    return EndpointConfig(endpoint_url=endpoint_url, metadata=None, enable_ssl=None)


def get_config_by_account_type(
    user_context: AuthenticatedUnifiedUserContext,
) -> EndpointConfig:
    user_account_type: AccountType = user_context.account_details.type

    if user_account_type == AccountType.HYBRID and "K8S_POD_NAME" in os.environ:
        return _get_direct_endpoint(user_context)
    else:
        return _get_edge_services_endpoint(user_context)
