import logging
import os
from typing import Optional, Tuple, List

import libcst as cst

from frogml.sdk.model_version.finders.frogml_model_class_finder import (
    FrogMlModelClassFinder,
)
from frogml.sdk.model_version.finders.model_class_info import ModelClassInfo

_logger = logging.getLogger(__name__)


class ModelFinder:
    """This class is responsible for finding model classes in Python files."""

    @staticmethod
    def find_model_class(
        code_dir: str,
    ) -> Optional[ModelClassInfo]:
        """
        Find a class inheriting from FrogMlModel in the given directory.

        :param code_dir: Directory containing Python files to analyze
        :return: Tuple of (file_path, class_name, model_field_name, has_initialize_method) if found,
                 None otherwise model_field_name could be None if no model field is found
        """
        python_files: List[str] = ModelFinder.__get_python_files(code_dir)

        for file_path in python_files:
            try:
                module: Optional[cst.Module] = ModelFinder.__parse_file(file_path)

                if module is None:
                    continue

                class_info: Optional[Tuple[str, Optional[str]]] = (
                    ModelFinder.__find_model_class_in_module(module)
                )

                if class_info is not None:
                    return ModelClassInfo(
                        file_path=file_path,
                        class_name=class_info[0],
                        model_field_name=class_info[1],
                    )

            except Exception as e:
                _logger.error(f"Error processing file {file_path}: {e}")

        return None

    @staticmethod
    def __get_python_files(directory: str) -> List[str]:
        """
        Get all Python files in the given directory and its subdirectories.

        :param directory: Directory to search in
        :return: List of paths to Python files
        """
        python_files: List[str] = []

        for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith(".py"):
                    python_files.append(os.path.join(root, file_name))

        return python_files

    @staticmethod
    def __parse_file(file_path: str) -> Optional[cst.Module]:
        """
        Parse a Python file into a CST module.

        :param file_path: Path to the file to parse
        :return: CST of the file, or None if parsing failed
        """
        try:
            with open(file_path, "r") as file:
                content: str = file.read()

            return cst.parse_module(content)
        except Exception as e:
            _logger.error(f"Error parsing file {file_path}: {e}")
            return None

    @staticmethod
    def __find_model_class_in_module(
        module: cst.Module,
    ) -> Optional[Tuple[str, Optional[str]]]:
        """
        Find a class inheriting from FrogMlModel in the given CST.

        :param module: AST to search in
        :return: Tuple of (class_name, model_field_name) if found, None otherwise
        """
        class_finder = FrogMlModelClassFinder()
        module.visit(class_finder)

        if class_finder.found_class_name is not None:
            return class_finder.found_class_name, class_finder.found_model_field

        return None
