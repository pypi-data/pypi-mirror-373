import logging
import csv
import os
from enum import Enum


class LogType(Enum):
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10

class PointrLogger:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PointrLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, logfile_path: str="logs.csv"):
        if not hasattr(self, "initialized"):
            self.logfile_path = logfile_path
            self.log_format = '"%(asctime)s" , %(levelname)s , %(message)s'
            self.csv_headers = ["Timestamp", "LogType", "ActiveUser", "Message"]
            self._create_log_directory()  # Create directory if it doesn't exist
            self.logger = self._prepare_log_file()
            self.initialized = True

    def _create_log_directory(self):
        # Ensure the directory for the logfile exists
        log_dir = os.path.dirname(self.logfile_path)
        if log_dir:  # Only create directory if there's a specified directory path
            os.makedirs(log_dir, exist_ok=True)

    def _prepare_log_file(self):
        # Create a custom logger for LogPointr
        logger = logging.getLogger(f"LogPointrLogger_{self.logfile_path}")
        logger.setLevel(logging.INFO)
        
        # Check if the logger already has handlers to avoid adding multiple handlers
        if not logger.handlers:
            # Create a handler for the CSV file
            csv_handler = logging.FileHandler(self.logfile_path, mode="a")
            csv_handler.setLevel(logging.INFO)
            csv_handler.setFormatter(logging.Formatter(self.log_format))
            logger.addHandler(csv_handler)

            
            # Write CSV headers to the file if the file is empty
            with open(self.logfile_path, mode="a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                if csvfile.tell() == 0:
                    csv_writer.writerow(self.csv_headers)

        return logger

    def log_message(self, message: str, log_type: LogType = LogType.INFO, active_user: str = "N/A"):
        log_message = f'{active_user}, "{message}"'
        # Logging to the custom logger
        if log_type == LogType.WARNING:
            self.logger.warning(log_message)
        elif log_type == LogType.DEBUG:
            self.logger.debug(log_message)
        elif log_type == LogType.ERROR:
            self.logger.error(log_message)
        else:
            self.logger.info(log_message) 