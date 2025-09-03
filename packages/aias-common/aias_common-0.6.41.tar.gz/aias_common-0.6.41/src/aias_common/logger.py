import logging
import ecs_logging

from uvicorn.logging import DefaultFormatter


class CustomLogger:
    logger_name = "logger"
    level = logging.DEBUG
    __logger: logging.Logger = None

    @classmethod
    def init(cls):
        cls.__logger = logging.getLogger(cls.logger_name)
        cls.__logger.setLevel(cls.level)
        cls.__logger.propagate = False

        formatter = DefaultFormatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                     datefmt="%Y-%m-%d %H:%M:%S")

        console_handler = logging.StreamHandler()
        console_handler.setLevel(cls.level)
        console_handler.setFormatter(formatter)
        cls.__logger.addHandler(console_handler)

        handler = logging.StreamHandler()
        handler.setFormatter(ecs_logging.StdlibFormatter())
        cls.__logger.addHandler(handler)


    @classmethod
    @property
    def logger(cls):
        if cls.__logger is None:
            cls.init()
        return cls.__logger
