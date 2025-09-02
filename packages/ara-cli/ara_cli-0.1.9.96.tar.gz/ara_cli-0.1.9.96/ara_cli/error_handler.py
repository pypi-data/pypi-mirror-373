import sys
import traceback
from typing import Optional
from enum import Enum
from functools import wraps


RED = '\033[91m'
RESET = '\033[0m'


class ErrorLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AraError(Exception):
    """Base exception class for ARA CLI errors"""

    def __init__(
        self, message: str, error_code: int = 1, level: ErrorLevel = ErrorLevel.ERROR
    ):
        self.message = message
        self.error_code = error_code
        self.level = level
        super().__init__(self.message)


class AraValidationError(AraError):
    """Raised when validation fails"""

    def __init__(self, message: str):
        super().__init__(message, error_code=2, level=ErrorLevel.ERROR)


class AraConfigurationError(AraError):
    """Raised when configuration is invalid"""

    def __init__(self, message: str):
        super().__init__(message, error_code=4, level=ErrorLevel.ERROR)


class ErrorHandler:
    """Centralized error handler for ARA CLI"""

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode

    def handle_error(self, error: Exception, context: Optional[str] = None) -> None:
        """Handle any error with standardized output"""
        if isinstance(error, AraError):
            self._handle_ara_error(error, context)
        else:
            self._handle_generic_error(error, context)

    def _handle_ara_error(self, error: AraError, context: Optional[str] = None) -> None:
        """Handle ARA-specific errors"""
        self._report_ara_error(error, context)

        sys.exit(error.error_code)

    def _handle_generic_error(
        self, error: Exception, context: Optional[str] = None
    ) -> None:
        """Handle generic Python errors"""
        self._report_generic_error(error, context)

        sys.exit(1)


    def report_error(self, error: Exception, context: Optional[str] = None) -> None:
        """Report error with standardized formatting but don't exit"""
        if isinstance(error, AraError):
            self._report_ara_error(error, context)
        else:
            self._report_generic_error(error, context)


    def _report_ara_error(self, error: AraError, context: Optional[str] = None) -> None:
        """Report ARA-specific errors without exiting"""
        error_prefix = f"[{error.level.value}]"

        if context:
            print(f"{RED}{error_prefix} {context}: {error.message}{RESET}", file=sys.stderr)
        else:
            print(f"{RED}{error_prefix} {error.message}{RESET}", file=sys.stderr)

        if self.debug_mode:
            traceback.print_exc()


    def _report_generic_error(self, error: Exception, context: Optional[str] = None) -> None:
        """Report generic Python errors without exiting"""
        error_type = type(error).__name__

        if context:
            print(f"{RED}[ERROR] {context}: {error_type}: {str(error)}{RESET}", file=sys.stderr)
        else:
            print(f"{RED}[ERROR] {error_type}: {str(error)}{RESET}", file=sys.stderr)

        if self.debug_mode:
            traceback.print_exc()


    def validate_and_exit(
        self, condition: bool, message: str, error_code: int = 1
    ) -> None:
        """Validate condition and exit with error if false"""
        if not condition:
            raise AraValidationError(message)


def handle_errors(_func=None, context: Optional[str] = None, error_handler: Optional[ErrorHandler] = None):
    """Decorator to handle errors in action functions"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal error_handler
            if error_handler is None:
                error_handler = ErrorHandler()

            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(e, context or func.__name__)

        return wrapper

    if callable(_func):
        return decorator(_func)
    return decorator
