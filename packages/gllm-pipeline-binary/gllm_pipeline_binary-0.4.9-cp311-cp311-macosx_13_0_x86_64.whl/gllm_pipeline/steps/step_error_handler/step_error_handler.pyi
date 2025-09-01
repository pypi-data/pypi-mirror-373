import abc
from _typeshed import Incomplete
from abc import ABC
from gllm_pipeline.utils.error_handling import ErrorContext as ErrorContext
from typing import Any

class BaseStepErrorHandler(ABC, metaclass=abc.ABCMeta):
    """Abstract base class for error handling strategies.

    Attributes:
        log_level (int): The logging level to use when logging errors.
        logger (logging.Logger): The logger to use when logging errors.
    """
    log_level: Incomplete
    logger: Incomplete
    def __init__(self, log_level: int = ...) -> None:
        """Initialize the error handler with a specific log level.

        Args:
            log_level (int): The logging level to use when logging errors.
                Defaults to logging.ERROR. Common values:
                1. logging.DEBUG: Detailed information for debugging.
                2. logging.INFO: General information messages.
                3. logging.WARNING: Warning messages.
                4. logging.ERROR: Error messages (default).
                5. logging.CRITICAL: Critical error messages.
        """
    def handle(self, error: Exception, state: dict[str, Any], config: dict[str, Any], context: ErrorContext) -> dict[str, Any] | None:
        """Handle an error that occurred during pipeline step execution.

        This method logs the error first, then delegates to the concrete implementation.

        Args:
            error (Exception): The exception that was raised.
            state (dict[str, Any]): The current pipeline state when the error occurred.
            config (dict[str, Any]): Runtime configuration for this step's execution.
            context (ErrorContext): Additional context about the error.

        Returns:
            dict[str, Any] | None: State updates to apply, or None if no updates needed.

        Raises:
            Exception: May raise exceptions based on the strategy implementation.
        """
