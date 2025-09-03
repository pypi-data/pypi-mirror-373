from pathlib import Path

from frogml.core.inner.build_logic.interface.build_logger_interface import BuildLogger


def load_patterns_from_ignore_file(build_logger: BuildLogger, ignore_file_path: Path):
    if Path(ignore_file_path).is_file():
        build_logger.info("Found a FrogML ignore file - will ignore listed patterns")

        with open(ignore_file_path, "r") as igonre_file:
            patterns_to_ignore = [
                pattern.strip() for pattern in igonre_file.readlines()
            ]
            build_logger.debug(
                f"Patterns from FrogML igonre file detected - {str(patterns_to_ignore)}"
            )
            return patterns_to_ignore

    build_logger.debug("no FrogML ignore file was found, skipping")
    return []
