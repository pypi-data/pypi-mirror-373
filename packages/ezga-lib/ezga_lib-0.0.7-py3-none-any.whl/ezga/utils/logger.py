# logger.py
import os
import logging
from ..core.interfaces import ILogger

class WorkflowLogger(ILogger):
    """
    Workflow logger for structured logging within workflows.

    This class provides a simple wrapper around Python's built-in logging
    system, ensuring that workflow-related messages are consistently formatted
    and written to a log file located at the specified output path.
    """
    def __init__(self, output_path:str = '.'):
        """
        Initialize the WorkflowLogger.

        Args:
            output_path (str): Path to the directory where the log file will be stored.
                               Defaults to the current directory '.'.
        """
        self.output_path = output_path or '.'

    @staticmethod
    def setup_logger(name: str, output_path: str) -> logging.Logger:
        """
        Configure and return a logger instance for the workflow.

        This method ensures that the logging directory exists, creates a file
        handler for persistent logging, and applies a standard log format.
        If the logger already has handlers, no additional handlers are added
        to prevent duplicate log entries.

        Args:
            name (str): The name of the logger instance.
            output_path (str): Directory where the log file will be stored.

        Returns:
            logging.Logger: Configured logger instance ready for use.
        """

        output_path = output_path or self.output_path

        # Ensure the output directory exists
        os.makedirs(output_path, exist_ok=True)

        # Create and configure logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Define log file location
        log_file = os.path.join(output_path, 'workflow.log')

        # Create file handler
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Avoid adding multiple handlers to the same logger
        if not logger.handlers:
            logger.addHandler(handler)

        return logger
