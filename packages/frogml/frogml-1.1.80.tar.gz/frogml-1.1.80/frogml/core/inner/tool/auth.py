from typing import Optional, Union, cast
from urllib.parse import urljoin

import requests
from requests import Response

from frogml.storage.authentication.models import AuthConfig, BearerAuth
from frogml.storage.authentication.utils import get_credentials
from requests.auth import AuthBase
from typing_extensions import Self

from frogml.core.exceptions import FrogmlLoginException


class FrogMLAuthClient:
    __MIN_TOKEN_LENGTH: int = 64

    def __init__(self: Self, auth_config: Optional[AuthConfig] = None):
        self.auth_config: Optional[AuthConfig] = auth_config
        self._token: Optional[str] = None
        self._tenant_id: Optional[str] = None

    def get_token(self: Self) -> str:
        if not self._token:
            self.login()

        return cast(str, self._token)

    def get_base_url(self) -> str:
        artifactory_url, _ = get_credentials(self.auth_config)
        return self.__remove_artifactory_path_from_url(artifactory_url)

    def get_tenant_id(self: Self) -> str:
        if not self._tenant_id:
            self.login()

        return cast(str, self._tenant_id)

    def login(self: Self):
        artifactory_url, auth = get_credentials(self.auth_config)

        if isinstance(auth, BearerAuth):  # For BearerAuth
            self.validate_token(auth.token)
            self._token = auth.token

        self.__get_tenant_id(artifactory_url, auth)

    def get_auth(self: Self) -> Union[AuthBase]:
        return get_credentials(self.auth_config)[1]

    def __get_tenant_id(self: Self, artifactory_url: str, auth: AuthBase):
        login_exception = FrogmlLoginException(
            "Failed to authenticate with JFrog. Please check your credentials"
        )

        base_url: str = self.__remove_artifactory_path_from_url(artifactory_url)
        url: str = urljoin(base_url, "/ui/api/v1/system/auth/screen/footer")

        try:
            response: Response = requests.get(url, timeout=15, auth=auth)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            response_data: dict = response.json()

            if "serverId" in response_data:
                self._tenant_id = response_data["serverId"]
            else:
                self.__get_jpd_id(base_url)

        except (requests.exceptions.RequestException, ValueError) as exc:
            raise login_exception from exc

    def __get_jpd_id(self, base_url: str):
        url: str = urljoin(base_url, "/jfconnect/api/v1/system/jpd_id")
        headers: dict = {"Authorization": f"Bearer {self._token}"}
        response = requests.get(url=url, headers=headers, timeout=15)

        if response.status_code == 200:
            self._tenant_id = response.text
        elif response.status_code == 401:
            raise FrogmlLoginException(
                "Failed to authenticate with JFrog. Please check your credentials"
            )
        else:
            raise FrogmlLoginException(
                "Failed to authenticate with JFrog. Please check your artifactory configuration"
            )

    def validate_token(self: Self, token: Optional[str]):
        if token is None or len(token) <= self.__MIN_TOKEN_LENGTH or token.isspace():
            raise FrogmlLoginException(
                "Authentication with JFrog failed: Only JWT Access Tokens are supported. "
                "Please ensure you are using a valid JWT Access Token."
            )

    @staticmethod
    def __remove_artifactory_path_from_url(artifactory_url: str) -> str:
        # Remove '/artifactory' from the URL
        base_url: str = artifactory_url.replace("/artifactory", "", 1)
        # Remove trailing slash if exists
        return base_url.rstrip("/")
