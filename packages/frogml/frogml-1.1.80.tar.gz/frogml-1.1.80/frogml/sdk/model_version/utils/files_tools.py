import importlib.resources
import logging
import os
import shutil
from importlib.abc import Traversable
from pathlib import Path
from typing import List, Optional

from frogml.core.exceptions import FrogmlException
from frogml.sdk.model_version.constants import (
    FROGML_LOG_LEVEL_ENVAR_NAME,
)
from frogml.sdk.model_version.utils.dependencies_tools import _copy_dependencies
from frogml.sdk.model_version.utils.model_log_config import ModelLogConfig

_logger = logging.getLogger(__name__)
_logger.setLevel(os.getenv(FROGML_LOG_LEVEL_ENVAR_NAME) or logging.INFO)


DEFAULT_ZIP_NAME = "code"
DEFAULT_ZIP_FORMAT = "zip"
IGNORED_PATTERNS_FOR_UPLOAD = [r"\..*", r"__pycache__"]
HIDDEN_DIRS_TO_INCLUDE = [".dvc"]
HIDDEN_FILES_PREFIX = "."
TEMPLATE_FILES: str = "template_files"


def _zip_dir(
    root_dir: str,
    dir_to_zip: str,
    zip_name: str = DEFAULT_ZIP_NAME,
) -> Optional[str]:
    """
    Zip model code directory
    :param root_dir: The root directory to put the zip into
    :param dir_to_zip: The directory to zip
    :param zip_name: Name of the zipped file
    :return: return str object of the zipped file
    """
    try:
        zip_file_path = os.path.join(root_dir, zip_name)
        zip_path = Path(
            shutil.make_archive(
                base_name=zip_file_path,
                format=DEFAULT_ZIP_FORMAT,
                root_dir=dir_to_zip,
            )
        )

        return zip_path.absolute().as_posix()

    except Exception as e:
        raise FrogmlException(f"Unable to zip model: {e}") from e


def _copy_dir_without_ignored_files(source_dir: str, dest_dir: str) -> str:
    """
    Copy directory to target directory

    :param source_dir: Source directory
    :param dest_dir: destination directory

    :return: Copied directory path
    """
    source_dir: str = os.path.abspath(source_dir)
    main_dir: str = os.path.join(dest_dir, "main")
    ignored_files: List[str] = _get_files_to_ignore(directory=Path(source_dir))
    shutil.copytree(
        src=source_dir,
        dst=main_dir,
        ignore=shutil.ignore_patterns(*ignored_files),
        dirs_exist_ok=True,
    )

    return dest_dir


def _copy_template_files(template_file_dir: str, dest_dir: str) -> None:
    """
    Copy template files from the temporary directory to the main directory within the 'dest_dir' path.
    :param template_file_dir: The template file directory.
    :param dest_dir: Destination directory where the template files will be copied.
    """
    main_dir: str = os.path.join(dest_dir, "main")
    shutil.copytree(src=template_file_dir, dst=main_dir, dirs_exist_ok=True)


def _get_files_to_ignore(directory: Path) -> List[str]:
    def ignore_hidden(file: Path, exclusions: List[str]):
        name = os.path.basename(os.path.abspath(file))
        is_hidden = name.startswith(HIDDEN_FILES_PREFIX) and name not in exclusions
        return is_hidden

    return [
        file.name
        for file in Path(directory).rglob("*")
        if ignore_hidden(file, exclusions=HIDDEN_DIRS_TO_INCLUDE)
    ]


def _get_full_model_path(target_dir: str, model_name: str, serialized_type: str) -> str:
    return os.path.join(target_dir, f"{model_name}.{serialized_type}")


def _remove_dir(dir_path: str):
    """
    Remove a directory
    :param dir_path: The directory's path
    """
    shutil.rmtree(dir_path, ignore_errors=True)


class SetupTemplateFilesManager:
    """
    A class to manage the setup of template files for model logging.
    """

    def __init__(
        self, config: ModelLogConfig, dependencies: Optional[list[str]] = None
    ):
        """
        :param config: ModelLogConfig object containing the model data.
        :param dependencies: Optional list of file paths to dependency files to include in the template files.
        """
        self.config: ModelLogConfig = config
        self.dependencies: Optional[list[str]] = dependencies

    def setup_template_files(self) -> None:
        """
        Set up template files based on the provided configuration by copying them to the directory where they will be zipped.
        If the code directory is provided, it assumes that the predict file and dependencies are also supplied and sets up the template files accordingly.
        If the code directory is not provided, it sets up generic template files according to the model framework.
        """
        if self.config.code_dir:
            # We assume that if code_dir is provided, then also predict_file and dependencies are provided as well.
            _logger.info(
                "Code directory, predict file and dependencies are provided. Setup template files for model_name %s",
                self.config.model_name,
            )
            self.setup_template_files_when_user_data_is_provided()
        else:
            _logger.info(
                "Code directory, predict file and dependencies are not provided. Setup template files for model_name %s",
                self.config.model_name,
            )
            self.setup_template_files_when_user_data_is_not_provided()

    def setup_template_files_when_user_data_is_provided(self) -> None:
        try:
            template_files_path: str = (
                f"frogml.sdk.model_version.{self.config.model_framework}"
            )
            predict_dir_path: Traversable = (
                importlib.resources.files(template_files_path)
                / TEMPLATE_FILES
                / "predict_dir"
            )
            target_template_dir: str = os.path.join(
                self.config.target_dir, TEMPLATE_FILES
            )

            _logger.debug(f"Creating target template directory: {target_template_dir}")
            shutil.copytree(str(predict_dir_path), target_template_dir)
            _copy_dependencies(
                dependencies=self.dependencies,
                target_directory=target_template_dir,
            )
            self._add_parameters_model_file(template_dir=target_template_dir)
            self._add_path_to_predict_import(template_dir=target_template_dir)

            _logger.debug(
                f"Successfully set up template files from user data for {self.config.model_name} with version {self.config.version}"
            )
        except Exception as e:
            _logger.error(
                f"Error occurred while setting up template files from user data for {self.config.model_name} with version {self.config.version}: {e}"
            )
            raise FrogmlException(
                f"Unable to setup template files from user data for {self.config.model_name}: {e}"
            ) from e

    def setup_template_files_when_user_data_is_not_provided(self) -> None:
        """
        Copy the template files, based on the model framework, to the template directory and update the framework version in the requirements.txt file.
        """
        try:
            template_files_path: str = (
                f"frogml.sdk.model_version.{self.config.model_framework}"
            )
            build_dir_path: Traversable = (
                importlib.resources.files(template_files_path)
                / TEMPLATE_FILES
                / "build_dir"
            )
            target_template_dir: str = os.path.join(
                self.config.target_dir, TEMPLATE_FILES
            )

            _logger.debug(
                "Copying template files from %s to %s",
                build_dir_path,
                target_template_dir,
            )
            shutil.copytree(str(build_dir_path), target_template_dir)

            self._add_framework_version_to_requirements_file(
                template_dir=target_template_dir
            )
            self._add_parameters_model_file(template_dir=target_template_dir)

            _logger.debug(
                "Template setup successfully at: %s for model %s",
                self.config.target_dir,
                self.config.model_name,
            )

        except Exception as e:
            _logger.error("Failed to generate template for %s", self.config.model_name)
            raise FrogmlException(f"Template generation failed: {e}") from e

    def _add_framework_version_to_requirements_file(self, template_dir: str) -> None:
        """
        Add the framework version to the requirements.txt file in the template directory.
        :param template_dir: The template directory path.
        """
        self.__replace_template_variables(
            template_dir=template_dir,
            file_to_modify="requirements.txt",
            parameter_to_switch_to_parameter_val={
                "FRAMEWORK_VERSION": self.config.framework_version
            },
        )

    def _add_parameters_model_file(self, template_dir: str) -> None:
        """
        Add parameters to the load_models function in model.py file in the template directory.
        :param template_dir: The template directory path.
        """
        self.__replace_template_variables(
            template_dir=template_dir,
            file_to_modify="model.py",
            parameter_to_switch_to_parameter_val={
                "repositoryKey": self.config.repository,
                "modelName": self.config.model_name,
                "modelVersion": self.config.version,
            },
        )

    def _add_path_to_predict_import(self, template_dir: str) -> None:
        relative_path_to_predict_file_dot_notation: str = (
            self._construct_relative_path_to_predict_file()
        )
        self.__replace_template_variables(
            template_dir=template_dir,
            file_to_modify="model.py",
            parameter_to_switch_to_parameter_val={
                "path_to_predict_file": relative_path_to_predict_file_dot_notation,
            },
        )

    def _construct_relative_path_to_predict_file(self) -> str:
        predict_file_path: Path = Path(self.config.predict_file)
        code_dir_path: Path = Path(self.config.code_dir)
        relative_path_to_predict_file: Path = predict_file_path.relative_to(
            code_dir_path
        )
        return ".".join(relative_path_to_predict_file.with_suffix("").parts)

    def __replace_template_variables(
        self,
        template_dir: str,
        file_to_modify: str,
        parameter_to_switch_to_parameter_val: dict[str, str],
    ) -> None:
        """
        Replace template variables in a specified file within the template directory.
        :param template_dir: The directory containing the template files.
        :param file_to_modify: The name of the file to modify.
        :param parameter_to_switch_to_parameter_val: A dictionary mapping template variable names to their replacement values.
        """
        _logger.debug(
            "Replacing template variables in %s for model %s",
            file_to_modify,
            self.config.model_name,
        )

        try:
            file_to_modify_path: str = os.path.join(template_dir, file_to_modify)

            with open(file_to_modify_path) as f:
                content = f.read()
                for key, value in parameter_to_switch_to_parameter_val.items():
                    content = content.replace("${" + key + "}", value)

            with open(file_to_modify_path, "w") as f:
                f.write(content)

            _logger.debug("%s in %s has changed", file_to_modify, file_to_modify_path)
        except FileNotFoundError as e:
            raise FrogmlException(f"{file_to_modify} not found: {e}") from e
        except Exception as e:
            raise FrogmlException(
                f"Failed to add parameters to {file_to_modify}: {e}"
            ) from e
