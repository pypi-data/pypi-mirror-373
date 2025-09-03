from gllm_core.utils.retry import RetryConfig as RetryConfig
from langgraph.types import RetryPolicy

def retry_config_to_langgraph_policy(retry_config: RetryConfig | None) -> RetryPolicy | None:
    """Convert RetryConfig to LangGraph's RetryPolicy.

    This function maps the GLLM Core's RetryConfig parameters to LangGraph's RetryPolicy format.

    Args:
        retry_config (RetryConfig | None, optional): The GLLM Core's retry configuration.
            Defaults to None, in which case no retry config is applied.

    Returns:
        RetryPolicy | None: The equivalent LangGraph retry policy, or None if retry_config is None.

    Note:
        The conversion maps the following parameters:
        1. max_retries + 1 -> max_attempts (LangGraph counts the first attempt as 1).
        2. base_delay -> initial_interval.
        3. max_delay -> max_interval.
        4. exponential_base -> backoff_factor (using 2.0 as per SDK validation).
        5. jitter -> jitter.
        6. retry_on_exceptions -> retry_on.
        7. timeout is not directly supported by LangGraph's RetryPolicy.
    """
