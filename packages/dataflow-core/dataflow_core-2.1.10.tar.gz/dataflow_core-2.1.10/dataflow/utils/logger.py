import logging
import sys

class CustomLogger:
    """
    Custom logger class for configuring and using console-based logging functionality.
    """
    def __init__(self):
        self._configure_handler()

    def _configure_handler(self):
        """
        Configure the console handler once.
        """
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)

    def get_logger(self, name=None):
        """
        Retrieve a configured logger instance with a dynamic name.

        Args:
            name (str): The name of the logger. Defaults to 'dataflow_logger'.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger_name = name or "dataflow_logger"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        # Prevent duplicate handlers if logger already configured
        if not logger.handlers:
            logger.addHandler(self.console_handler)

        return logger
