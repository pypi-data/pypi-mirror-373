import http
from typing import Optional

import requests
from requests.auth import AuthBase, HTTPBasicAuth

from frogml.storage.artifactory import ArtifactoryApi
from frogml.storage.authentication.models import BearerAuth, EmptyAuth
from frogml.storage.authentication.utils import (
    try_generate_access_token,
    save_auth_config,
    is_access_token_login,
    is_anonymous_login,
    is_username_password_login,
)
from frogml.storage.logging import logger
from frogml.storage.authentication.models import LoginArguments


def run(login_args: LoginArguments, anonymous: Optional[bool] = False) -> bool:
    if is_username_password_login(login_args, anonymous):
        connection_validation_result = __login_by_username_password(login_args)
    elif is_access_token_login(login_args, anonymous):
        connection_validation_result = __validate_server_connection(
            login_args, BearerAuth(login_args.access_token)
        )
    elif is_anonymous_login(login_args, anonymous):
        connection_validation_result = __validate_server_connection(
            login_args, EmptyAuth()
        )
    else:
        connection_validation_result = False

    if connection_validation_result:
        save_auth_config(login_args)
    return connection_validation_result


def __login_by_username_password(login_args: LoginArguments) -> bool:
    if login_args.username is not None and login_args.password is not None:
        auth_token = HTTPBasicAuth(login_args.username, login_args.password)
        connection_validation_result = __validate_server_connection(
            login_args, auth_token
        )
        if connection_validation_result:
            access_token = try_generate_access_token(
                login_args.artifactory_url, auth_token
            )
            if access_token is not None:
                login_args.access_token = access_token
                return True
    return False


def __validate_server_connection(
    login_args: LoginArguments, auth_token: AuthBase
) -> bool:
    success = False
    try:
        logger.debug("Attempting to ping artifactory")
        response = ArtifactoryApi(login_args.artifactory_url, auth_token).ping()
        if response.status_code == http.HTTPStatus.OK:
            success = True
        else:
            logger.debug(
                f"Expected {http.HTTPStatus.OK} status but got {response.status_code} "
                f"when using url {login_args.artifactory_url}"
            )
    except requests.exceptions.ConnectionError as e:
        logger.debug(f"Unable to connect to the provided url :{e}.")
    except requests.exceptions.MissingSchema as e:
        logger.debug(f"Invalid Artifactory URL provided: {e}.")
    except requests.exceptions.RequestException as e:
        logger.debug(f"Unexpected request exception: {e}.")

    return success
