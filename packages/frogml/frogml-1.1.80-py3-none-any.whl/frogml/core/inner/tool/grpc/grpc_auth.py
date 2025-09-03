from typing import TYPE_CHECKING, Callable, Optional, Tuple

import grpc

from frogml.core.inner.const import FrogMLConstants

if TYPE_CHECKING:
    from frogml.core.inner.tool.auth import FrogMLAuthClient

_SIGNATURE_HEADER_KEY = "authorization"


class FrogMLAuthMetadataPlugin(grpc.AuthMetadataPlugin):
    def __init__(self):
        self._auth_client: Optional["FrogMLAuthClient"] = None

    def __call__(
        self,
        context: grpc.AuthMetadataContext,
        callback: Callable[[Tuple[Tuple[str, str], Tuple[str, str]], None], None],
    ):
        """Implements authentication by passing metadata to a callback.

        Args:
            context: An AuthMetadataContext providing information on the RPC that
                the plugin is being called to authenticate.
            callback: A callback that accepts a tuple of metadata key/value pairs and a None
                parameter.
        """
        # Get token from FrogML client
        if not self._auth_client:
            from frogml.core.inner.tool.auth import FrogMLAuthClient

            self._auth_client = FrogMLAuthClient()

        token = self._auth_client.get_token()
        jfrog_tenant_id = self._auth_client.get_tenant_id()
        metadata = (
            (_SIGNATURE_HEADER_KEY, f"Bearer {token}"),
            (FrogMLConstants.JFROG_TENANT_HEADER_KEY.lower(), jfrog_tenant_id),
        )
        callback(metadata, None)
