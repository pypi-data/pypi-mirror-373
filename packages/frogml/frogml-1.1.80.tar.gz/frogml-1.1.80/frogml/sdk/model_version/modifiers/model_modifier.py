import logging

import libcst as cst

from frogml.sdk.model_version.finders.model_class_info import ModelClassInfo
from frogml.sdk.model_version.transformers.initialize_model_transformer import (
    InitializeModelTransformer,
)

_logger = logging.getLogger(__name__)


class ModelModifier:
    """Class responsible for modifying model files."""

    @staticmethod
    def modify_model_file(
        model_class_info: ModelClassInfo,
        repository: str,
        model_name: str,
        version: str,
        framework_name: str,
    ) -> None:
        """
        Modify the model file to update or add the initialize_model method.

        :param model_class_info: Information about the model class
        :param repository: Repository key to use in the template
        :param model_name: Model name to use in the template
        :param version: Version to use in the template
        :param framework_name: The name of the framework used to train the model
        """
        with open(model_class_info.file_path, "r") as file:
            content: str = file.read()

        # Parse the file
        module: cst.Module = cst.parse_module(content)

        # Create and apply the transformer
        transformer = InitializeModelTransformer(
            model_class_info.class_name,
            model_class_info.model_field_name,
            repository,
            model_name,
            version,
            framework_name,
        )
        modified_module: cst.Module = module.visit(transformer)

        # Only write back to the file if changes were made
        if transformer.is_modified:
            with open(model_class_info.file_path, "w") as file:
                file.write(modified_module.code)
        else:
            _logger.info(f"No changes were made to {model_class_info.file_path}")
