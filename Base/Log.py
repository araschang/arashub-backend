import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

def configure_logging():
    log_level = logging.INFO  # Set the desired log level
    log_format = '%(asctime)s %(levelname)s: %(message)s'
    log_file = './log/log.log'  # Specify the log file path
    log_max_size = 1024 * 1024  # Set the max size of each log file (e.g., 1MB)
    log_backup_count = 5  # Set the number of backup log files to keep

    # Create the logger
    logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger()

    # Create a RotatingFileHandler for log file rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=log_max_size,
        backupCount=log_backup_count
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Remove any existing handlers from the logger
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger
