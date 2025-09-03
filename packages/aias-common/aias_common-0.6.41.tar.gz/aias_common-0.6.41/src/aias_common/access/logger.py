import logging
import os

from aias_common.logger import CustomLogger


class Logger(CustomLogger):
    logger_name = "access"
    level = os.getenv("ACCESS_LOGGER_LEVEL", logging.INFO)
