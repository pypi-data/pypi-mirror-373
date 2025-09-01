import logging
from pathlib import Path


class Logger:
    @staticmethod
    def setup_logger(
        name: str,
        level: int = logging.INFO,
        log_file: str = None,
        run_debug: bool = False,
    ):
        """
        Setup a logger with the given name and level.

        Args:
            name: Name of the logger.
            level: Logging level. Default is logging.INFO.
            log_file: Path to a file where logs should be written. Defaults to None.
            run_debug: Sets level to debug; overwrites level argument

        Returns:
            logging.Logger: Configured logger.
        """
        if run_debug:
            level = logging.DEBUG
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Check if handlers already exist to avoid duplicate logging
        if not logger.handlers:
            formatter = logging.Formatter(
                fmt="[%(levelname)s] [%(asctime)s] (%(module)s:%(lineno)d) -> %(message)s",
                datefmt="%d-%m-%Y %H:%M:%S",
            )

            log_dir = Path.cwd() / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            if log_file is None:
                log_file = f"{log_dir}/combined.log"

            if log_file:
                file_handler = logging.FileHandler(log_file, mode="a+")
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger

    @staticmethod
    def add_file_handler(logger, log_file, level=logging.INFO, formatter=None):
        """
        Add a file handler to the logger.

        Args:
            logger (logging.Logger): The logger to add the handler to.
            log_file (str): Path to the log file.
            level (int, optional): Logging level. Default is logging.INFO.
            formatter (logging.Formatter, optional): Formatter for the log messages. Default is None.

        Returns:
            None
        """
        if formatter is None:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    @staticmethod
    def add_stream_handler(logger, level=logging.INFO, formatter=None):
        """
        Add a stream handler to the logger.

        Args:
            logger (logging.Logger): The logger to add the handler to.
            level (int, optional): Logging level. Default is logging.INFO.
            formatter (logging.Formatter, optional): Formatter for the log messages. Default is None.

        Returns:
            None
        """
        if formatter is None:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    @staticmethod
    def set_level(logger, level):
        """
        Set the logging level for the logger.

        Args:
            logger (logging.Logger): The logger to set the level for.
            level (int): Logging level.

        Returns:
            None
        """
        logger.setLevel(level)

    @staticmethod
    def create_formatter(fmt=None, datefmt=None):
        """
        Create a logging formatter.

        Args:
            fmt (str, optional): The format string for the log messages. Default is None.
            datefmt (str, optional): The format string for the date in the log messages. Default is None.

        Returns:
            logging.Formatter: The created formatter.
        """
        if fmt is None:
            fmt = "[%(levelname)s] [%(asctime)s] (%(module)s:%(lineno)d) -> %(message)s"
        return logging.Formatter(fmt=fmt, datefmt=datefmt)
