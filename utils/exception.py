import sys
import logging
from utils.logger import get_logger
from omegaconf import DictConfig

class CustomException(Exception):
    """
    Custom exception class to capture and format detailed error information.
    Automatically logs the error using a configured logger.
    """
    def __init__(self, error_message, error_detail: sys, cfg: DictConfig = None):
        super().__init__(error_message)
        # Initialize logger (fall back to default if no cfg provided)
        self.logger = get_logger("ExceptionHandler", cfg) if cfg else logging.getLogger("DefaultLogger")
        
        # Format the detailed error message
        self.error_message = self.error_message_detail(error_message, error_detail)
        
        # Log the error directly
        self.logger.error(self.error_message)

        # Optionally log Hydra context for debugging
        if cfg:
            self.logger.debug(f"Hydra configuration context: {cfg}")

    def error_message_detail(self, error, error_detail: sys):
        """
        Extracts detailed error information, including traceback.
        Handles cases where traceback is unavailable.
        """
        exc_info = error_detail.exc_info()
        if exc_info[2] is None:
            return f"Error occurred: [{str(error)}] (No traceback available)"

        _, _, exc_tb = exc_info
        file_name = exc_tb.tb_frame.f_code.co_filename
        error_message = (
            f"Error occurred in python script [{file_name}] at line [{exc_tb.tb_lineno}] "
            f"with message: [{str(error)}]"
        )
        return error_message

    def __str__(self):
        """
        Returns the formatted error message for display.
        """
        return self.error_message
