from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Optional, Tuple, Union

from frogml.core.inner.build_logic.interface.build_logger_interface import BuildLogger
from frogml.core.inner.build_logic.tools.ignore_files import (
    load_patterns_from_ignore_file,
)

_IGNORED_PATTERNS = [r"\..*", r"__pycache__"]
FROGML_IGNORE_FILE_NAME: str = ".frogmlignore"


def get_ignore_pattern(
    src: str, main_dir: str, build_logger: BuildLogger
) -> Tuple[Callable[[Any, list[str]], set[str]], list[str]]:
    if (Path(src) / main_dir / FROGML_IGNORE_FILE_NAME).is_file():
        ignore_file_path: Path = Path(src) / main_dir / FROGML_IGNORE_FILE_NAME
    else:
        ignore_file_path: Path = Path(src) / FROGML_IGNORE_FILE_NAME

    ignored_patterns = (
        load_patterns_from_ignore_file(
            build_logger=build_logger, ignore_file_path=ignore_file_path
        )
        + _IGNORED_PATTERNS
    )

    return shutil.ignore_patterns(*ignored_patterns), ignored_patterns


class Strategy(ABC):
    def __init__(self, build_logger: BuildLogger):
        self.build_logger = build_logger

    @abstractmethod
    def fetch(
        self,
        src: Union[str, Path],
        dest: str,
        git_branch: str,
        git_credentials: str,
        model_id: str,
        build_id: str,
        custom_dependency_path: Optional[str],
    ) -> Optional[str]:
        pass
