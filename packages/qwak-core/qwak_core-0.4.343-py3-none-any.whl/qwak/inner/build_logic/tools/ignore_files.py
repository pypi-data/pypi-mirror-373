from pathlib import Path

from qwak.inner.build_logic.interface.build_logger_interface import BuildLogger


def load_patterns_from_ignore_file(build_logger: BuildLogger, ignore_file_path: Path):
    if Path(ignore_file_path).is_file():
        build_logger.info("Found a Qwak ignore file - will ignore listed patterns")

        with open(ignore_file_path, "r") as igonre_file:
            patterns_to_ignore = [
                pattern.strip() for pattern in igonre_file.readlines()
            ]
            build_logger.debug(
                f"Patterns from Qwak igonre file detected - {str(patterns_to_ignore)}"
            )
            return patterns_to_ignore

    build_logger.debug("no Qwak ignore file was found, skipping")
    return []
