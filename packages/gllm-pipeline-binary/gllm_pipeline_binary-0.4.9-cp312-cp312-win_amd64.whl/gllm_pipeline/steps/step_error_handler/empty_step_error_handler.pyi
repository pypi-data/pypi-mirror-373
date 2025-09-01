from _typeshed import Incomplete
from gllm_pipeline.steps.step_error_handler.step_error_handler import BaseStepErrorHandler as BaseStepErrorHandler
from gllm_pipeline.utils.error_handling import ErrorContext as ErrorContext

class EmptyStepErrorHandler(BaseStepErrorHandler):
    """Strategy that replace the current state of the output states to None on error.

    Attributes:
        output_state (list[str]): Output key(s) to map input values to.
    """
    output_state: Incomplete
    def __init__(self, output_state: str | list[str]) -> None:
        """Initialize the strategy with optional output state mapping.

        Args:
            output_state (str | list[str]): Output key(s) to map input values to.
                Can be a single string, list of strings.
        """
