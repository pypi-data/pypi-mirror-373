import errno
import os
from dataclasses import dataclass
from typing import Optional

from frogml.storage.authentication.utils import get_credentials
from frogml.storage.authentication.login import frogml_login
from frogml.storage.constants import CONFIG_FILE_PATH

from frogml.core.exceptions import FrogmlLoginException
from frogml.core.inner.tool.auth import FrogMLAuthClient


@dataclass
class UserAccount:
    """
    User Account Configuration
    """

    # Assigned Token
    token: Optional[str] = None

    # Assigned username
    username: Optional[str] = None

    # Assigned password
    password: Optional[str] = None

    # Assigned URL
    url: Optional[str] = None

    # Anonymous login
    anonymous: bool = False

    # Interactive login
    is_interactive: bool = False

    # The unique server id
    server_id: Optional[str] = None


class UserAccountConfiguration:
    def __init__(
        self,
        config_file=CONFIG_FILE_PATH,
    ):
        self._config_file = config_file
        self._auth_client = FrogMLAuthClient()

    def configure_user(self, user_account: UserAccount):
        """
        Configure user authentication based on the authentication client type
        """

        # Use FrogML login flow
        success = frogml_login(
            url=user_account.url,
            username=user_account.username,
            password=user_account.password,
            token=user_account.token,
            anonymous=user_account.anonymous,
            is_interactive=user_account.is_interactive,
            server_id=user_account.server_id,
        )

        if not success:
            raise FrogmlLoginException("Failed to authenticate with JFrog")

        # Validate token
        token: Optional[str] = self._auth_client.get_token()
        self._auth_client.validate_token(token)

    @staticmethod
    def _mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if not (exc.errno == errno.EEXIST and os.path.isdir(path)):
                raise

    @staticmethod
    def _safe_open(path):
        UserAccountConfiguration._mkdir_p(os.path.dirname(path))
        return open(path, "w")

    @staticmethod
    def get_user_config() -> UserAccount:
        """
        Get persisted user account from config file
        :return:
        """
        return UserAccount()

    @staticmethod
    def get_user_token() -> str:
        """
        Get persisted user account from config file
        :return:
        """
        _, auth = get_credentials()

        try:
            return getattr(auth, "token")
        except AttributeError as e:
            raise FrogmlLoginException("Token is not configured") from e

    @staticmethod
    def retrieve_platform_url() -> str:
        """Returns the platform URL with the '/ui/ml' suffix based on the authentication client configuration."""
        try:
            return f"{FrogMLAuthClient().get_base_url()}/ui/ml"
        except ValueError:
            return ""
