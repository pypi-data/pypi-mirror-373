import abc
from abc import ABC
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from gllm_pipeline.steps.step_error_handler.step_error_handler import BaseStepErrorHandler as BaseStepErrorHandler
from gllm_pipeline.utils.error_handling import ErrorContext as ErrorContext
from gllm_pipeline.utils.mermaid import combine_mermaid_diagrams as combine_mermaid_diagrams, extract_step_diagrams as extract_step_diagrams
from langgraph.graph import StateGraph as StateGraph
from langgraph.types import RetryPolicy as RetryPolicy

class BaseCompositeStep(BasePipelineStep, ABC, metaclass=abc.ABCMeta):
    """Base class for all composite pipeline steps.

    Attributes:
        name (str): A unique identifier for the pipeline step.
        retry_policy (RetryPolicy | None): Configuration for retry behavior using LangGraph's RetryPolicy.
    """
    def __init__(self, name: str, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None) -> None:
        """Initialize the composite step.

        Args:
            name (str): A unique identifier for the pipeline step.
            retry_config (RetryConfig | None, optional): Configuration for retry behavior. Defaults to None.
            error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
        """
    def add_to_graph(self, graph: StateGraph, previous_endpoints: list[str], retry_policy: RetryPolicy | None = None) -> list[str]:
        """Template method: Add this composite step to the graph.

        Args:
            graph (StateGraph): The graph to add this step to.
            previous_endpoints (list[str]): Endpoints from previous steps to connect to.
            retry_policy (RetryPolicy | None, optional): Retry policy to use for this step and propagate to child steps.
                If provided, takes precedence over the step's own retry policy.
                Defaults to None, in which case the step's own retry policy is used.

        Returns:
            list[str]: Exit points after adding all child steps
        """
    def get_mermaid_diagram(self) -> str:
        """Template method: Generate complete mermaid diagram.

        Returns:
            str: Complete mermaid diagram representation.
        """
