import warnings
from .error_handler import ErrorHandler


whitelisted_commands = ["RERUN", "SEND", "EXTRACT", "LOAD_IMAGE", "CHOOSE_MODEL", "CHOOSE_EXTRACTION_MODEL", "CURRENT_MODEL", "CURRENT_EXTRACTION_MODEL", "LIST_MODELS"]


error_handler = ErrorHandler()


# ANSI escape codes for coloring
YELLOW = '\033[93m'
RESET = '\033[0m'


def format_warning(message, category, *args, **kwargs):
    return f'{YELLOW}{category.__name__}: {message}{RESET}\n'


warnings.formatwarning = format_warning
