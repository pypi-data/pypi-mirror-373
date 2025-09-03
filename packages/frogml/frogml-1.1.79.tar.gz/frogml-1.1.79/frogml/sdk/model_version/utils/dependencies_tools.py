import logging
import os
import re
import shutil
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union, Dict

from pydantic import BaseModel, Field

_VERSION_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+==[a-zA-Z0-9_.-]+$")

_logger = logging.getLogger(__name__)


class DependencyManagerType(Enum):
    UNKNOWN = 0
    PIP = 1
    POETRY = 2
    CONDA = 3


class DependencyFileObject(BaseModel):
    dep_file_name: List[str] = Field(
        min_length=1, description="List of dependency file names"
    )
    lock_file_name: str = Field(
        default="", description="Lock file name for the dependency manager"
    )


DEPS_MANAGER_FILE_MAP: Dict[DependencyManagerType, DependencyFileObject] = {
    DependencyManagerType.PIP: DependencyFileObject(dep_file_name=["requirements.txt"]),
    DependencyManagerType.POETRY: DependencyFileObject(
        dep_file_name=["pyproject.toml"], lock_file_name="poetry.lock"
    ),
    DependencyManagerType.CONDA: DependencyFileObject(
        dep_file_name=["conda.yml", "conda.yaml"]
    ),
}


def _dependency_files_handler(
    dependencies: Optional[List[str]], target_dir: Union[Path, str]
) -> Optional[List[str]]:
    """
    Check if dependencies is list of version and create requirements.txt file
    :param dependencies: list of dependencies
    :param target_dir: temporary directory for explicit versions
    :return: List of dependencies if dependencies is not None else None
    """
    if not dependencies:
        return None

    is_conda: bool = _validate_conda(dependencies)
    is_poetry: bool = _validate_poetry(dependencies)
    is_requirements: bool = _validate_requirements(dependencies)
    _logger.debug(
        f"with the dependencies: {dependencies}, we have {is_conda=}, {is_poetry=}, {is_requirements=}"
    )

    if not is_conda and not is_poetry and not is_requirements:
        return _create_requirements_file(
            dependencies=dependencies, target_dir=target_dir
        )

    return dependencies


def _create_requirements_file(
    dependencies: List[str], target_dir: Union[Path, str]
) -> List[str]:
    """
    Create requirements file from list of explicit versions
    :param dependencies:
    :return: requirements file path
    """
    requirements_path = os.path.join(target_dir, "requirements.txt")
    with open(requirements_path, "w") as file:
        for package in dependencies:
            if _VERSION_PATTERN.match(package):
                file.write(package + "\n")
            else:
                _logger.info(f"Invalid package format: {package}")
        _logger.debug(f"Requirements file created at: {requirements_path}")
        return [requirements_path]


def _validate_conda(dependencies: List[str]) -> bool:
    """
    Validate if dependencies is conda type
    :param dependencies: list of conda files
    :return: true if all conda files are existing else false
    """

    conda_deps_manager: DependencyFileObject = DEPS_MANAGER_FILE_MAP.get(
        DependencyManagerType.CONDA
    )
    is_single_dependency_file: bool = len(dependencies) == 1
    is_valida_conda_file_path = False

    if is_single_dependency_file:
        file_path: str = dependencies[0]
        file_path = os.path.expanduser(file_path)
        for conda_dep_file in conda_deps_manager.dep_file_name:
            if (conda_dep_file in file_path) and os.path.exists(file_path):
                is_valida_conda_file_path = True

    return is_valida_conda_file_path


def _validate_poetry(dependencies: List[str]) -> bool:
    """
    Validate if dependencies is poetry type
    :param dependencies: list of poetry files
    :return: true if all poetry files are existing else false
    """

    poetry_deps_manager: DependencyFileObject = DEPS_MANAGER_FILE_MAP.get(
        DependencyManagerType.POETRY
    )

    is_toml_file_validate: bool = False
    is_lock_file_validate: bool = False

    for dependency in dependencies:
        dependency = os.path.expanduser(dependency)
        if (poetry_deps_manager.dep_file_name[0] in dependency) and os.path.exists(
            dependency
        ):
            is_toml_file_validate = True
        elif (poetry_deps_manager.lock_file_name in dependency) and os.path.exists(
            dependency
        ):
            is_lock_file_validate = True

    is_only_toml_dependency_validate: bool = (
        is_toml_file_validate and len(dependencies) == 1
    )
    is_toml_and_lock_dependencies_validate: bool = (
        is_toml_file_validate and is_lock_file_validate and len(dependencies) == 2
    )
    return is_only_toml_dependency_validate or is_toml_and_lock_dependencies_validate


def _validate_requirements(dependencies: List[str]) -> bool:
    """
    Validate if dependencies is requirements type
    :param dependencies:
    :return: true if all requirements files are existing else false
    """

    pip_deps_manager: DependencyFileObject = DEPS_MANAGER_FILE_MAP.get(
        DependencyManagerType.PIP
    )
    is_single_dependency_file: bool = len(dependencies) == 1

    if is_single_dependency_file:
        dependency: str = dependencies[0]
        dependency = os.path.expanduser(dependency)
        if (pip_deps_manager.dep_file_name[0] in dependency) and os.path.exists(
            dependency
        ):
            return True

    return False


def _validate_versions(packages: List[str]):
    """
    Validate if packages are in the correct format
    :param packages: list of packages
    :return: True if all packages are in the correct format else False
    """
    return all(_VERSION_PATTERN.match(pkg) for pkg in packages)


def _copy_dependencies(dependencies: list[str], target_directory: str) -> None:
    """
    Copy dependency file to the specified destination directory.

    :param dependencies: Path to dependency files
    :param target_directory: Target directory where files will be copied
    """
    for dependency_file_path in dependencies:
        if not os.path.exists(dependency_file_path):
            _logger.warning(
                f"Dependency file not found: {dependency_file_path}. Skipping."
            )
            return
        try:
            shutil.copy(dependency_file_path, target_directory)
        except shutil.Error as e:
            _logger.warning(
                f"Could not copy {dependency_file_path} to {target_directory}. Error: {e}"
            )
