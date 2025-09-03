import sys
from loguru import logger as loguru_logger


def setup_logger():
    loguru_logger.remove()
    loguru_logger.add(
        sys.stderr, level="INFO", format="{time} - {name} - {level} - {message}"
    )
    return loguru_logger


logger = setup_logger()  # type: ignore
