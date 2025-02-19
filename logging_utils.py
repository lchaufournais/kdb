# logging_utils.py

import logging
import logging.config
from config import LOG_CONFIG

logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)

class ConsoleColor:
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    PURPLE = "\033[95m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def colored_message(message: str, color: str) -> str:
    return f"{color}{message}{ConsoleColor.RESET}"

def log_message(message: str, level: str = "info", color: str = ConsoleColor.RESET, session_id: str = None):
    if session_id:
        message = f"[Session {session_id}] {message}"
    colored_msg = colored_message(message, color)
    if level.lower() == "info":
        logger.info(colored_msg)
    elif level.lower() == "error":
        logger.error(colored_msg)
    elif level.lower() == "warning":
        logger.warning(colored_msg)
    else:
        logger.info(colored_msg)

def trace(func):
    """Decorator to log function entry, exit, and exceptions."""
    def wrapper(*args, **kwargs):
        log_message(f"Entering {func.__name__} with args: {args} kwargs: {kwargs}", 
                    level="info", color=ConsoleColor.BLUE)
        try:
            result = func(*args, **kwargs)
            log_message(f"Exiting {func.__name__} with result: {result}", 
                        level="info", color=ConsoleColor.GREEN)
            return result
        except Exception as e:
            log_message(f"Exception in {func.__name__}: {e}", 
                        level="error", color=ConsoleColor.RED)
            raise
    return wrapper
