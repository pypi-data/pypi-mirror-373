import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_pipeline.pipeline.pipeline import Pipeline as Pipeline
from gllm_pipeline.steps.step_error_handler import RaiseStepErrorHandler as RaiseStepErrorHandler
from gllm_pipeline.steps.step_error_handler.step_error_handler import BaseStepErrorHandler as BaseStepErrorHandler
from gllm_pipeline.utils.error_handling import ErrorContext as ErrorContext
from gllm_pipeline.utils.retry_converter import retry_config_to_langgraph_policy as retry_config_to_langgraph_policy
from langchain_core.runnables import RunnableConfig as RunnableConfig
from langgraph.graph import StateGraph as StateGraph
from langgraph.pregel import RetryPolicy as RetryPolicy
from pydantic import BaseModel as BaseModel
from typing import Any

LANGGRAPH_CONFIG_PREFIX: str

class BasePipelineStep(ABC, metaclass=abc.ABCMeta):
    """The base class for all pipeline steps.

    A pipeline step represents a single operation or task within a larger processing pipeline.
    Each step must implement:
    1. execute() - to perform the actual operation
    2. add_to_graph() - to integrate with the pipeline structure (optional, default implementation provided)

    The default implementation of add_to_graph is suitable for steps that:
    1. Have a single entry point
    2. Have a single exit point
    3. Connect to all previous endpoints

    For more complex graph structures (e.g., conditional branching), steps should override add_to_graph.

    Attributes:
        name (str): A unique identifier for the pipeline step.
        retry_policy (RetryPolicy | None): Configuration for retry behavior using LangGraph's RetryPolicy.
    """
    name: Incomplete
    error_handler: Incomplete
    retry_policy: Incomplete
    def __init__(self, name: str, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None) -> None:
        """Initializes a new pipeline step.

        Args:
            name (str): A unique identifier for the pipeline step.
            retry_config (RetryConfig | None, optional): Configuration for retry behavior using
                GLLM Core's RetryConfig. Defaults to None, in which case no retry config is applied.
                The RetryConfig is automatically converted to LangGraph's RetryPolicy when needed for internal use.
                Note that `timeout` is not supported and will be ignored.
            error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
                Defaults to None, in which case the RaiseStepErrorHandler is used.
        """
    def add_to_graph(self, graph: StateGraph, previous_endpoints: list[str], retry_policy: RetryPolicy | None = None) -> list[str]:
        """Integrates this step into the pipeline's internal structure.

        This method is responsible for:
        1. Adding the step's node(s) to the graph if not already present
        2. Creating edges from previous endpoints to this step's entry points
        3. Returning this step's exit points (endpoints)

        This method provides a default implementation suitable for simple steps.
        Steps with more complex graph structures should override this method.

        This method is used by `Pipeline` to manage the pipeline's execution flow.
        It should not be called directly by users.

        Args:
            graph (StateGraph): The internal representation of the pipeline structure.
            previous_endpoints (list[str]): The endpoints from previous steps to connect to.
            retry_policy (RetryPolicy | None): Configuration for retry behavior using LangGraph's RetryPolicy.
                If None, the retry policy of the step is used. If the step is not a retryable step,
                this parameter is ignored.

        Returns:
            list[str]: The exit points (endpoints) of this step.
        """
    @abstractmethod
    async def execute(self, state: dict[str, Any] | BaseModel, config: RunnableConfig) -> dict[str, Any] | None:
        """Executes the operation defined for this pipeline step.

        This method should be implemented by subclasses to perform the actual processing or computation for this step.

        Args:
            state (dict[str, Any] | BaseModel): The current state of the pipeline, containing all data.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            dict[str, Any] | None: The update to the pipeline state after this step's operation.
                This should include new or modified data produced by this step, not the entire state.
                Returns None if no state update is needed.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
    async def execute_direct(self, state: dict[str, Any], config: RunnableConfig) -> dict[str, Any] | None:
        """Execute this step directly, bypassing graph-based execution.

        This method is used when a step needs to be executed directly, such as in parallel execution.
        The default implementation calls _execute_with_error_handling for consistent error handling.

        Args:
            state (dict[str, Any]): The current state of the pipeline.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            dict[str, Any] | None: Updates to apply to the pipeline state, or None if no updates.
        """
    def get_mermaid_diagram(self) -> str:
        """Generates a Mermaid diagram representation of the pipeline step.

        This method provides a default implementation that can be overridden by subclasses
        to provide more detailed or specific diagrams.

        It is recommended to implement this method for subclasses that have multiple connections to other steps.

        Returns:
            str: Empty string.
        """
    def __or__(self, other: BasePipelineStep | Pipeline) -> Pipeline:
        """Combines this step with another step or pipeline.

        This method allows for easy composition of pipeline steps using the | operator.

        Args:
            other (BasePipelineStep | Pipeline): Another step or pipeline to combine with this one.

        Returns:
            Pipeline: A new pipeline containing the combined steps.
        """
    def __lshift__(self, other: BasePipelineStep | Pipeline) -> Pipeline:
        """Combines this step with another step or pipeline using the '<<' operator.

        Args:
            other (BasePipelineStep | Pipeline): The step or pipeline to add after this step.

        Returns:
            Pipeline: A new pipeline with this step followed by the other step or pipeline.
        """
    def __rshift__(self, other: BasePipelineStep | Pipeline) -> Pipeline:
        """Combines this step with another step or pipeline using the '>>' operator.

        Args:
            other (BasePipelineStep | Pipeline): The step or pipeline to include this step in.

        Returns:
            Pipeline: A new pipeline with this step included in the other step or pipeline.
        """
