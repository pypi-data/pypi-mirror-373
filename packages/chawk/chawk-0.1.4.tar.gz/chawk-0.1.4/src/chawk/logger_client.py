import logging


class Logger:
    """
    A wrapper for the built-in logging package.
    """

    def __init__(self, log_filename="chawk.log"):
        """
        Initialize the Logger instance.

        :param log_filename: Name of the log file (default: 'chawk.log')
        """
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        self.set_output_file(log_filename)

    def set_output_file(self, filename: str):
        """
        Change the output file for logging.
        """
        # Remove all existing handlers
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)

        # Add the new file handler with the specified filename
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(
            logging.Formatter(
                "%(levelname)s: %(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S"
            )
        )
        self._logger.addHandler(file_handler)

    def info(self, msg: str):
        self._logger.info(msg)

    def debug(self, msg: str):
        self._logger.debug(msg)

    def warning(self, msg: str):
        self._logger.warning(msg)

    def error(self, msg: str):
        self._logger.error(msg)

    def critical(self, msg: str):
        self._logger.critical(msg)
        raise Exception(f"{msg}")

    def get_file_path(self):
        """
        Get the current file path used for logging.
        """
        for handler in self._logger.handlers:
            if isinstance(handler, logging.FileHandler):
                return handler.baseFilename
        return None
