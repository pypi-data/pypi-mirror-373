import sys
from pathlib import Path

from loguru import logger

class LogWrapper:
    def __init__(self, logs_dir: str = "logs", log_level: str = "DEBUG"):
        self.logger = logger
        self.logger.remove()

        Path(logs_dir).mkdir(parents=True, exist_ok=True)

        self.logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYYMMDD HH:mm:ss.SSS}</green> | "
                "{process.name} | "
                "{thread.name} | "
                "<cyan>{module}</cyan>.<cyan>{function}</cyan>:"
                "<cyan>{line}</cyan> | "
                "<level>{level}</level>: "
                "<level>{message}</level>"
            ),
            level=log_level
        )

        log_file_path = Path(logs_dir) / "{time:YYYY-MM-DD}.log"
        self.logger.add(
            log_file_path,
            level=log_level,
            format=(
                "{time:YYYYMMDD HH:mm:ss} - "
                "{process.name} | "
                "{thread.name} | "
                "{module}.{function}:{line} - {level} - {message}"
            ),
            rotation="10 MB",
            encoding="utf-8"
        )

    def get_logger(self):
        return self.logger


default_logger = LogWrapper()
logger = default_logger.get_logger()

# Convenience functions
def setup_logger(**kwargs) -> LogWrapper:
    """Create a new logger instance with custom configuration."""
    return LogWrapper(**kwargs)

def get_default_logger():
    """Get the default logger instance."""
    return logger