from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any

class ErrorContext(BaseModel):
    '''Standardized error context for pipeline steps.

    This model provides a structured way to represent error context information
    for pipeline steps, ensuring consistency in error messages across the pipeline.

    Attributes:
        exception (BaseException): The exception that was raised
        step_name (str): The name of the pipeline step where the error occurred
        step_type (str): The type of pipeline step where the error occurred
        state (dict[str, Any] | None): The pipeline state at the time of the error. Defaults to None.
        operation (str): Description of the operation being performed when the error occurred.
            Defaults to "execution".
        additional_context (str | None): Additional context to include in the error message.
            Defaults to None.
    '''
    model_config: Incomplete
    exception: BaseException
    step_name: str
    step_type: str
    state: dict[str, Any] | None
    operation: str
    additional_context: str | None

class ValidationError(Exception):
    """Exception raised for errors in state validation.

    This exception is raised when input validation fails in pipeline steps.
    It provides more specific error information than a generic RuntimeError.

    Attributes:
        message (str): The error message explaining the validation failure
    """
    message: Incomplete
    def __init__(self, message: str) -> None:
        """Initialize with an error message.

        Args:
            message (str): The error message explaining what validation failed
        """
