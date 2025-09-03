from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import ModelFramework


def _validate_string(s: str) -> None:
    """
    Validate if string is not empty
    :param s: string
    :return: None if validation pass successfully else raise error
    """
    if not s:
        raise FrogmlException("String is empty")


def _validate_load_model(
    repository: str,
    model_name: str,
    version: str,
    model_framework_stored: str,
    model_framework: ModelFramework,
) -> None:
    """
    Private method that validate user input
    :param repository: repository name
    :param model_name: The model's name
    :param version: The model's version
    :param model_framework_stored: The model framework stored files/catboost etc.
    :param model_framework: The model framework files/catboost etc.
    :return: None if validation passed successfully
    """

    _validate_string(repository)

    _validate_string(model_name)
    _validate_string(version)
    if model_framework_stored != model_framework.value:
        raise FrogmlException(
            f"The Model: {model_name} in Repository: {repository} - is not a {model_framework} model"
        )
