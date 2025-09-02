import os

from loguru import logger


def setup_logging(file_path: str):
    logger.add(
        os.path.join(os.path.dirname(os.path.abspath(file_path)) + "/logs/" + os.path.basename(file_path) + ".log"),
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        backtrace=True,
        diagnose=True,
    )
    return logger
