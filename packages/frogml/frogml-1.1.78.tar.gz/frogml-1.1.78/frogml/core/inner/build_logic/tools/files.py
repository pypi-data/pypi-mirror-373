import fnmatch
import os
import re
import shutil
from pathlib import Path
from typing import Iterable, List, Optional

from frogml.core.exceptions import FrogmlGeneralBuildException
from frogml.core.inner.build_logic.constants.temp_dir import TEMP_LOCAL_MODEL_DIR
from frogml.core.inner.build_logic.interface.build_logger_interface import BuildLogger
from frogml.core.inner.build_logic.interface.step_inteface import Step
from frogml.core.inner.build_logic.tools.dependencies_tools import DEPS_MANAGER_FILE_MAP

# Hidden directories setting
HIDDEN_FILES_PREFIX = "."
HIDDEN_DIRS_TO_INCLUDE = [".dvc"]
IGNORED_PATTERNS_FOR_UPLOAD = [r"\..*", r"__pycache__"]
FROGML_IGNORE_FILE_NAME = ".frogmlignore"


def copytree(
    src,
    dst,
    symlinks=False,
    ignore=None,
    ignore_dangling_symlinks=False,
    dirs_exist_ok=False,
):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst, exist_ok=dirs_exist_ok)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.islink(srcname):
                linkto = os.readlink(srcname)
                if symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code with a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    os.symlink(linkto, dstname)
                    shutil.copystat(srcname, dstname, follow_symlinks=not symlinks)
                else:
                    # ignore dangling symlink if the flag is on
                    if not os.path.exists(linkto) and ignore_dangling_symlinks:
                        continue
                    # otherwise let the copy occurs. copy2 will raise an error
                    if os.path.isdir(srcname):
                        copytree(srcname, dstname, symlinks, ignore)
                    else:
                        shutil.copy2(srcname, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        # Copying file access times may fail on Windows
        if getattr(why, "winerror", None) is None:
            errors.append((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)
    return dst


def get_possible_dependency_lock_paths(dependency_path: Path):
    paths = []
    for _, dependency_file_object in DEPS_MANAGER_FILE_MAP.items():
        if dependency_file_object.lock_file_name:
            lock_file_path = (
                dependency_path.parent / dependency_file_object.lock_file_name
            )
            paths.append(lock_file_path)
    return paths


def get_files_to_ignore(directory: Path, patterns: Iterable[str] = ()):
    def ignore_hidden(file: Path, exclusions: List[str]):
        name = os.path.basename(os.path.abspath(file))
        is_hidden = name.startswith(HIDDEN_FILES_PREFIX) and (
            name != FROGML_IGNORE_FILE_NAME and name not in exclusions
        )
        return is_hidden

    def is_ignore_by_pattern(file: Path):
        return (
            len(
                [
                    pattern
                    for pattern in patterns
                    if re.search(fnmatch.translate(pattern), str(file))
                ]
            )
            != 0
        )

    return [
        file.name
        for file in Path(directory).rglob("*")
        if is_ignore_by_pattern(file)
        or ignore_hidden(file, exclusions=HIDDEN_DIRS_TO_INCLUDE)
    ]


def _replace_large_files_with_too_large_file_message(
    filtered_model: Path, max_bytes: Optional[int]
):
    def does_exceed_size(file: Path):
        file_size = file.lstat().st_size
        return file_size > max_bytes, file.lstat().st_size

    if max_bytes is None:
        return

    for root, dirs, files in os.walk(filtered_model):
        for file in files:
            file_path = Path(os.path.join(root, file))
            replace_content, file_size = does_exceed_size(file_path)
            if replace_content:
                Path(file_path).write_text(
                    f"File is too big to display. Size: {file_size} bytes"
                )


def zip_model(
    build_dir: Path,
    dependency_file: Path,
    dirs_to_include: List[str],
    zip_name: str,
    ignored_patterns: Iterable[str],
    max_bytes: Optional[int] = None,
    deps_lock_file: Optional[Path] = None,
):
    try:
        filtered_model = build_dir / zip_name
        ignored_patterns = get_files_to_ignore(
            directory=build_dir / TEMP_LOCAL_MODEL_DIR, patterns=ignored_patterns
        )

        for included_dir in dirs_to_include:
            dir_to_copy = build_dir / TEMP_LOCAL_MODEL_DIR / included_dir
            if dir_to_copy.is_dir():
                copytree(
                    src=build_dir / TEMP_LOCAL_MODEL_DIR / included_dir,
                    dst=filtered_model / included_dir,
                    ignore=shutil.ignore_patterns(*ignored_patterns),
                    dirs_exist_ok=True,
                )

        deps_file = build_dir / TEMP_LOCAL_MODEL_DIR / dependency_file
        shutil.copy(deps_file, filtered_model / dependency_file)

        if deps_lock_file:
            deps_lock_file_full_path = build_dir / TEMP_LOCAL_MODEL_DIR / deps_lock_file
            shutil.copy(deps_lock_file_full_path, filtered_model / deps_lock_file)

        _replace_large_files_with_too_large_file_message(filtered_model, max_bytes)

        zip_path = Path(
            shutil.make_archive(
                base_name=str(filtered_model),
                format="zip",
                root_dir=filtered_model,
            )
        )

        shutil.rmtree(filtered_model)
        return zip_path

    except Exception as e:
        raise FrogmlGeneralBuildException(
            message="Unable to zip model before upload",
            src_exception=e,
        )


class UploadInChunks(object):
    def __init__(
        self,
        file: Path,
        build_logger: BuildLogger,
        all_files_size_to_upload: int,
        read_so_far: int = 0,
        chunk_size_bytes: int = 1 << 13,
    ):
        self._file = file
        self._chunk_size = chunk_size_bytes
        self._total_size = self._file.stat().st_size
        self._read_so_far = read_so_far
        self._build_logger = build_logger
        self._all_files_size_to_upload = (
            all_files_size_to_upload  # Used for calculating percentage for both files
        )
        self._last_percent_update = 0

    def __iter__(self):
        with self._file.open("rb") as file:
            while True:
                data = file.read(self._chunk_size)
                if not data:
                    break
                self._read_so_far += len(data)
                percent = self._read_so_far * 1e2 / self._all_files_size_to_upload
                msg = "{percent:3.0f}%".format(percent=percent)
                if int(percent / 10) > self._last_percent_update:
                    self._build_logger.info(
                        msg
                    )  # Updating only after 10 percent change
                    self._last_percent_update = int(percent / 10)
                if hasattr(self._build_logger, "spinner_text"):
                    self._build_logger.spinner_text(line=msg)
                yield data

    def __len__(self):
        return self._total_size


def cleaning_up_after_build(step: Step):
    if os.getenv("FROGML_DEBUG") != "true":
        step.build_logger.debug("Removing Frogml temp artifacts directory")
        shutil.rmtree(step.context.host_temp_local_build_dir, ignore_errors=True)
