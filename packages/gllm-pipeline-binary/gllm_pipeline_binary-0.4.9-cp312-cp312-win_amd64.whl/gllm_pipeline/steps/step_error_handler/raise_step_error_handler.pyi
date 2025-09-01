from gllm_pipeline.steps.step_error_handler.step_error_handler import BaseStepErrorHandler as BaseStepErrorHandler
from gllm_pipeline.utils.error_handling import ErrorContext as ErrorContext

class RaiseStepErrorHandler(BaseStepErrorHandler):
    """Strategy that raises exceptions with enhanced context."""
    def __init__(self) -> None:
        """Initialize the raise error handler."""
