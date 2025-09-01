"""
BustAPI Smart Colorful Logging

FastAPI-style colorful logging with enhanced features for BustAPI.
"""

import logging
import sys
import time
from typing import Optional

try:
    import colorama
    from colorama import Back, Fore, Style

    colorama.init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    # Fallback without colors
    class _MockColor:
        def __getattr__(self, name):
            return ""

    Fore = Back = Style = _MockColor()
    HAS_COLORAMA = False


class ColoredFormatter(logging.Formatter):
    """Colorful log formatter similar to FastAPI."""

    # Color mapping for different log levels
    COLORS = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    # HTTP status code colors
    STATUS_COLORS = {
        "1": Fore.CYAN,  # 1xx Informational
        "2": Fore.GREEN,  # 2xx Success
        "3": Fore.YELLOW,  # 3xx Redirection
        "4": Fore.RED,  # 4xx Client Error
        "5": Fore.MAGENTA,  # 5xx Server Error
    }

    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and HAS_COLORAMA

    def format(self, record: logging.LogRecord) -> str:
        if not self.use_colors:
            return self._format_plain(record)

        # Get color for log level
        level_color = self.COLORS.get(record.levelname, "")

        # Format timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        timestamp_colored = f"{Fore.BLUE}{timestamp}{Style.RESET_ALL}"

        # Format log level
        level_colored = f"{level_color}{record.levelname:8}{Style.RESET_ALL}"

        # Format logger name
        logger_name = record.name
        if logger_name.startswith("bustapi"):
            logger_name_colored = f"{Fore.MAGENTA}{logger_name}{Style.RESET_ALL}"
        else:
            logger_name_colored = f"{Fore.CYAN}{logger_name}{Style.RESET_ALL}"

        # Format message
        message = record.getMessage()

        # Special formatting for HTTP requests
        if hasattr(record, "method") and hasattr(record, "path"):
            method = record.method
            path = record.path
            status_code = getattr(record, "status_code", "200")
            duration_formatted = getattr(record, "duration_formatted", "N/A")
            error = getattr(record, "error", None)

            # Color method
            method_colors = {
                "GET": Fore.BLUE,
                "POST": Fore.GREEN,
                "PUT": Fore.YELLOW,
                "DELETE": Fore.RED,
                "PATCH": Fore.CYAN,
                "HEAD": Fore.MAGENTA,
                "OPTIONS": Fore.WHITE,
            }
            method_colored = f"{method_colors.get(method, '')}{method}{Style.RESET_ALL}"

            # Color status code
            status_first_digit = str(status_code)[0] if status_code else "2"
            status_color = self.STATUS_COLORS.get(status_first_digit, Fore.WHITE)
            status_colored = f"{status_color}{status_code}{Style.RESET_ALL}"

            # Color path
            path_colored = f"{Fore.WHITE}{path}{Style.RESET_ALL}"

            # Color duration based on time
            duration_color = Fore.GREEN  # Default fast
            if hasattr(record, "duration") and record.duration:
                duration = record.duration
                if duration >= 1.0:
                    duration_color = Fore.RED  # >= 1s = Red (slow)
                elif duration >= 0.5:
                    duration_color = Fore.YELLOW  # >= 500ms = Yellow (medium)
                elif duration >= 0.1:
                    duration_color = Fore.CYAN  # >= 100ms = Cyan (ok)
                else:
                    duration_color = Fore.GREEN  # < 100ms = Green (fast)

            duration_colored = f"{duration_color}{duration_formatted}{Style.RESET_ALL}"

            # Build message
            message = f"{method_colored} {path_colored} - {status_colored} - {duration_colored}"

            # Add error if present
            if error:
                error_colored = f"{Fore.RED}ERROR: {error}{Style.RESET_ALL}"
                message += f" - {error_colored}"

        # Special formatting for startup messages
        elif "starting" in message.lower() or "listening" in message.lower():
            message = f"{Fore.GREEN}{Style.BRIGHT}{message}{Style.RESET_ALL}"

        # Special formatting for error messages
        elif record.levelname in ["ERROR", "CRITICAL"]:
            message = f"{Fore.RED}{message}{Style.RESET_ALL}"

        # Build final log line
        log_line = (
            f"{timestamp_colored} {level_colored} {logger_name_colored:20} {message}"
        )

        # Add exception info if present
        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"

        return log_line

    def _format_plain(self, record: logging.LogRecord) -> str:
        """Plain formatting without colors."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        level = record.levelname.ljust(8)
        logger_name = record.name.ljust(20)
        message = record.getMessage()

        log_line = f"{timestamp} {level} {logger_name} {message}"

        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"

        return log_line


class BustAPILogger:
    """BustAPI logger with smart colorful output."""

    def __init__(self, name: str = "bustapi", use_colors: bool = True):
        self.logger = logging.getLogger(name)
        self.use_colors = use_colors
        self._setup_logger()

    def _setup_logger(self):
        """Setup logger with colored formatter."""
        if self.logger.handlers:
            return  # Already configured

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)

        # Set colored formatter
        formatter = ColoredFormatter(use_colors=self.use_colors)
        handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

    def info(self, message: str, **kwargs):
        """Log info message with optional extra data."""
        self.logger.info(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional extra data."""
        self.logger.debug(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with optional extra data."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with optional extra data."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with optional extra data."""
        self.logger.critical(message, extra=kwargs)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: Optional[float] = None,
        error: Optional[str] = None,
        **kwargs,
    ):
        """Log HTTP request with colored formatting and smart time units."""
        # Format duration with appropriate time unit
        duration_str = (
            self._format_duration(duration) if duration is not None else "N/A"
        )

        # Create log message
        message = f"{method} {path} - {status_code} - {duration_str}"
        if error:
            message += f" - ERROR: {error}"

        # Choose log level based on status code and error
        if error or (status_code >= 500):
            log_level = "error"
        elif status_code >= 400:
            log_level = "warning"
        else:
            log_level = "info"

        # Log with appropriate level
        getattr(self, log_level)(
            message,
            extra={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": duration,
                "duration_formatted": duration_str,
                "error": error,
                **kwargs,
            },
        )

    def _format_duration(self, duration: float) -> str:
        """Format duration with appropriate time unit (s, ms, μs, ns)."""
        if duration >= 1.0:
            return f"{duration:.3f}s"
        elif duration >= 0.001:
            return f"{duration * 1000:.3f}ms"
        elif duration >= 0.000001:
            return f"{duration * 1000000:.3f}μs"
        else:
            return f"{duration * 1000000000:.3f}ns"

    def log_startup(self, message: str, **kwargs):
        """Log startup message with special formatting."""
        self.info(f"🚀 {message}", **kwargs)

    def log_shutdown(self, message: str, **kwargs):
        """Log shutdown message with special formatting."""
        self.info(f"🛑 {message}", **kwargs)


# Global logger instance
logger = BustAPILogger()


# Simple interface - just import logging and use these
def setup(level: str = "INFO", use_colors: bool = True):
    """Simple setup function."""
    return setup_logging(level, use_colors)


def info(message: str, **kwargs):
    """Simple info logging."""
    logger.info(message, **kwargs)


def debug(message: str, **kwargs):
    """Simple debug logging."""
    logger.debug(message, **kwargs)


def warning(message: str, **kwargs):
    """Simple warning logging."""
    logger.warning(message, **kwargs)


def error(message: str, **kwargs):
    """Simple error logging."""
    logger.error(message, **kwargs)


def request(
    method: str, path: str, status_code: int, duration: float = None, error: str = None
):
    """Simple request logging."""
    logger.log_request(method, path, status_code, duration, error)


def setup_logging(
    level: str = "INFO", use_colors: bool = True, logger_name: str = "bustapi"
) -> BustAPILogger:
    """
    Setup BustAPI logging with colorful output.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_colors: Whether to use colored output
        logger_name: Name of the logger

    Returns:
        Configured BustAPILogger instance
    """
    # Create logger
    bustapi_logger = BustAPILogger(name=logger_name, use_colors=use_colors)

    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    bustapi_logger.logger.setLevel(log_level)

    return bustapi_logger


def get_logger(name: str = "bustapi") -> BustAPILogger:
    """Get a BustAPI logger instance."""
    return BustAPILogger(name=name)


# Convenience functions
def log_info(message: str, **kwargs):
    """Log info message using global logger."""
    logger.info(message, **kwargs)


def log_debug(message: str, **kwargs):
    """Log debug message using global logger."""
    logger.debug(message, **kwargs)


def log_warning(message: str, **kwargs):
    """Log warning message using global logger."""
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs):
    """Log error message using global logger."""
    logger.error(message, **kwargs)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration: Optional[float] = None,
    error: Optional[str] = None,
    **kwargs,
):
    """Log HTTP request using global logger."""
    logger.log_request(method, path, status_code, duration, error, **kwargs)


def log_startup(message: str, **kwargs):
    """Log startup message using global logger."""
    logger.log_startup(message, **kwargs)


def log_shutdown(message: str, **kwargs):
    """Log shutdown message using global logger."""
    logger.log_shutdown(message, **kwargs)


def request_logging_middleware(app_logger: Optional[BustAPILogger] = None):
    """
    Decorator to add automatic request logging to route handlers.

    Args:
        app_logger: Optional logger instance to use

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            import time

            from .request import request

            # Use provided logger or global logger
            req_logger = app_logger or logger

            # Get request info
            method = getattr(request, "method", "UNKNOWN")
            path = getattr(request, "path", "/unknown")

            # Start timing
            start_time = time.perf_counter()

            try:
                # Execute the route handler
                result = func(*args, **kwargs)

                # Calculate duration
                duration = time.perf_counter() - start_time

                # Determine status code
                if isinstance(result, tuple):
                    status_code = result[1] if len(result) > 1 else 200
                else:
                    status_code = 200

                # Log successful request
                req_logger.log_request(
                    method=method, path=path, status_code=status_code, duration=duration
                )

                return result

            except Exception as e:
                # Calculate duration for error case
                duration = time.perf_counter() - start_time

                # Log error request
                req_logger.log_request(
                    method=method,
                    path=path,
                    status_code=500,
                    duration=duration,
                    error=str(e),
                )

                # Re-raise the exception
                raise

        return wrapper

    return decorator


# Example usage
if __name__ == "__main__":
    # Demo the colorful logging
    demo_logger = setup_logging(level="DEBUG", use_colors=True)

    demo_logger.log_startup("BustAPI server starting...")
    demo_logger.info("Server configuration loaded")
    demo_logger.debug("Debug information")
    demo_logger.warning("This is a warning")
    demo_logger.error("This is an error")

    # Demo HTTP request logging with different time units
    demo_logger.log_request("GET", "/api/fast", 200, 0.000045)  # 45μs - very fast
    demo_logger.log_request("GET", "/api/quick", 200, 0.0023)  # 2.3ms - quick
    demo_logger.log_request("POST", "/api/users", 201, 0.123)  # 123ms - ok
    demo_logger.log_request("GET", "/api/medium", 200, 0.456)  # 456ms - medium
    demo_logger.log_request("GET", "/api/slow", 200, 1.234)  # 1.234s - slow
    demo_logger.log_request("GET", "/api/users/999", 404, 0.012)  # 12ms - not found
    demo_logger.log_request(
        "POST", "/api/error", 500, 0.089, "Database connection failed"
    )  # With error

    demo_logger.log_shutdown("BustAPI server shutting down...")
