import os
import re
from typing import Optional

import requests

from frogml.core.clients.model_management.client import ModelsManagementClient
from frogml.core.exceptions import FrogmlException

TAG_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")


def validate_tag(tag: str) -> bool:
    """
    Check if tag exists.

    Args:
        tag: tag to check

    Returns: If tag is valid
    """
    return re.match(TAG_REGEX, tag) is not None


def fetch_model_id() -> Optional[str]:
    """
    Get model id from environment.

    Returns: model id if found.

    Notes:
        1. Checking if called inside a model - then model id saved as environment variable.
    """
    # Checking if called inside a model - then model id saved as environment variable
    return os.getenv("QWAK_MODEL_ID", None)


def validate_model(model_id: str) -> str:
    """
    Validate a model ID validity and existence
    """
    if not model_id:
        model_id = fetch_model_id()
        if not model_id:
            raise FrogmlException("Failed to determined model ID.")

    try:
        ModelsManagementClient().get_model(model_id=model_id)
    except Exception:
        raise FrogmlException("Failed to find model.")

    return model_id


def fetch_build_id() -> Optional[str]:
    """
    Get Build id from environment

    Returns: Build id if found

    Notes:
        1. Checking if called inside a model - then build id saved as environment variable.
    """
    # Checking if called inside a model - then model id saved as environment variable
    return os.getenv("QWAK_BUILD_ID", None)


def upload_data(
    upload_url: str,
    data: bytes,
    headers: dict,
    content_type: str = "text/plain",
):
    """
    Upload data
    :param upload_url: the url to upload to.
    :param data: the data to upload
    :param headers: authentication details for upload data
    :param content_type: Uploaded content-type
    """
    try:
        headers["Content-Type"] = content_type
        http_response = requests.put(  # nosec B113
            upload_url,
            data=data,
            headers=headers,
        )

        if http_response.status_code not in [200, 201]:
            raise FrogmlException(
                f"Failed to upload data. "
                f"Status: [{http_response.status_code}], "
                f"reason: [{http_response.reason}]"
            )
    except Exception as e:
        raise FrogmlException(f"Failed to upload data. Error is {e}")
