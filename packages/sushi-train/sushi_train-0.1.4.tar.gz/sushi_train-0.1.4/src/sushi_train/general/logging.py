import os
import logging
import logging.handlers
import json
import datetime


def format_json(record):
    """Format log record as simplified JSON string"""
    log_entry = {
        "time": datetime.datetime.fromtimestamp(record.created).isoformat(),
        "logger": record.name,
        "level": record.levelname,
        "message": record.getMessage(),
        "line": record.lineno,
    }
    if record.exc_info:
        log_entry["exception"] = logging._defaultFormatter.formatException(
            record.exc_info
        )
    return json.dumps(log_entry)


def rotating_logger_json():
    """Setup logging with simplified JSON format and file rotation"""
    formatter = logging.Formatter()
    formatter.format = format_json

    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)   # ensure folder exists
    log_file = os.path.join(log_dir, "application.log")

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=2 * 1024 * 1024, backupCount=1
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger("json_logger")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger