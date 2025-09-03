import os
import re
from typing import List, Optional, Union

from frogml.storage.constants import FROG_ML_MAX_CHARS_FOR_NAME
from frogml.storage.exceptions.validation_error import FrogMLValidationError
from frogml.storage.logging import logger


def user_input_validation(
    entity_name: Optional[str],
    namespace: Optional[str],
    version: Optional[str],
    properties: Optional[dict[str, str]] = None,
) -> None:
    for arg_name, arg_value in {
        "entity_name": entity_name,
        "namespace": namespace,
        "version": version,
    }.items():
        _validate_user_input(field_value=arg_value, field_name=arg_name)

        _validate_user_input_dict(user_input=properties)


def _validate_user_input_dict(user_input: Optional[dict[str, str]]) -> None:
    if user_input is None:
        return

    valid_characters_pattern_with_slash: str = r"^[a-zA-Z0-9_-]+([./][a-zA-Z0-9_-]+)*$"
    for key, value in user_input.items():
        _validate_user_input(field_value=key, field_name="properties")
        _validate_user_input(
            field_value=value,
            field_name="properties",
            valid_characters_pattern=valid_characters_pattern_with_slash,
        )


def is_not_none(arg_name: str, arg_value: Optional[object]) -> bool:
    if arg_value is None:
        raise FrogMLValidationError(f"{arg_name} can't be 'None'.")
    return True


def _validate_user_input(
    field_value: Optional[str],
    field_name: str,
    valid_characters_pattern: Optional[str] = None,
) -> None:
    if field_value is None:
        return
    _validate_user_input_length(field_value=field_value, field_name=field_name)
    _validate_user_input_characters(
        field_value=field_value,
        field_name=field_name,
        valid_characters_pattern=valid_characters_pattern,
    )


def _validate_user_input_length(field_value: str, field_name: str) -> None:
    if len(str(field_value)) > FROG_ML_MAX_CHARS_FOR_NAME:
        raise FrogMLValidationError(
            f"Max length for {field_name.capitalize()} is 60 characters."
        )


def _validate_user_input_characters(
    field_value: str, field_name: str, valid_characters_pattern: Optional[str] = None
) -> None:
    if not valid_characters_pattern:
        valid_characters_pattern = r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*$"

    compiled_valid_characters_pattern: re.Pattern[str] = re.compile(
        valid_characters_pattern
    )
    if not re.match(compiled_valid_characters_pattern, str(field_value)):
        raise FrogMLValidationError(
            f"Invalid characters detected at {field_name.capitalize()}: {field_value}"
        )


def is_valid_thread_number(thread_count: str) -> bool:
    try:
        int_thread_count = int(thread_count)
        cpu_count = os.cpu_count()
        if int_thread_count <= 0 or (
            cpu_count is not None and int_thread_count >= cpu_count
        ):
            raise ValueError(
                f"Invalid thread count: {thread_count}. The default value will be used."
            )
        return True
    except ValueError as e:
        logger.warning(f"Thread count {thread_count}: {e}")
        return False
    except Exception:
        logger.debug("Thread count not configured. The default value will be used.")
        return False


def validate_not_folder_paths(paths: Union[Optional[List[str]], Optional[str]]) -> bool:
    if paths is not None:
        if isinstance(paths, List):
            for path in paths:
                __validate_not_folder_path(path)
        else:
            __validate_not_folder_path(paths)
    return True


def __validate_not_folder_path(path: str) -> bool:
    if os.path.isdir(path):
        raise FrogMLValidationError(
            f"file '{path}' must be a file, but is a directory."
        )
    return True


def validate_path_exists(path: str) -> bool:
    if not os.path.exists(path):
        raise ValueError(f"Provided path does not exists : '{path}'")
    return True
