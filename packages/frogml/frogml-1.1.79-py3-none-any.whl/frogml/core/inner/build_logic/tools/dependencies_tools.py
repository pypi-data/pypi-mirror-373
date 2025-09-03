from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from frogml.core.inner.build_logic.dependency_manager_type import DependencyManagerType
from frogml.core.inner.build_logic.interface.build_logger_interface import BuildLogger


@dataclass
class DependencyFileObject:
    dep_file_name: List[str]
    lock_file_name: str = field(default="")


DEPS_MANAGER_FILE_MAP = {
    DependencyManagerType.PIP: DependencyFileObject(dep_file_name=["requirements.txt"]),
    DependencyManagerType.POETRY: DependencyFileObject(
        dep_file_name=["pyproject.toml"], lock_file_name="poetry.lock"
    ),
    DependencyManagerType.CONDA: DependencyFileObject(
        dep_file_name=["conda.yml", "conda.yaml"]
    ),
}


def find_dependency_files(model_uri, main_dir, build_logger: BuildLogger):
    dependency_manager_type = None
    model_relative_dependency_file = None
    model_relative_dependency_lock_file = None
    for dep_type, dependency_file_object in DEPS_MANAGER_FILE_MAP.items():
        for filename in dependency_file_object.dep_file_name:
            dep_file_path = find_file_location(model_uri, main_dir, filename)
            if dep_file_path:
                build_logger.info(
                    f"Found dependency type: {dep_type.name} by file: {dep_file_path}"
                )
                dependency_manager_type = dep_type
                model_relative_dependency_file = dep_file_path.relative_to(model_uri)
                if dependency_file_object.lock_file_name:
                    dep_lock_file_path = find_file_location(
                        model_uri,
                        main_dir,
                        dependency_file_object.lock_file_name,
                    )
                    if dep_lock_file_path:
                        build_logger.info(
                            f"Found dependency lock file {dep_lock_file_path}"
                        )
                        model_relative_dependency_lock_file = (
                            dep_lock_file_path.relative_to(model_uri)
                        )
                break

    return (
        dependency_manager_type,
        model_relative_dependency_file,
        model_relative_dependency_lock_file,
    )


def find_file_location(model_uri, main_dir, filename) -> Path:
    file_locations: List[Path] = [
        model_uri / filename,
        model_uri / main_dir / filename,
    ]
    for file in file_locations:
        if file.is_file():
            return file
