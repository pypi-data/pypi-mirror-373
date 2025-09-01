from typing import Any, Callable

async def execute_callable(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute a callable function, handling both synchronous and asynchronous functions.

    This utility function automatically detects whether the provided function is synchronous
    or asynchronous and executes it appropriately:
    1. For async functions: calls them directly with await
    2. For sync functions: runs them in a thread pool to avoid blocking the event loop

    Args:
        func (Callable[..., Any]): The function to execute. Can be either sync or async.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        Any: The result of the function execution.

    Raises:
        Exception: Any exception raised by the function execution.
    """
