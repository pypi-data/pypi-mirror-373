from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from langchain_core.runnables import RunnableConfig as RunnableConfig
from langgraph.graph import StateGraph as StateGraph
from langgraph.types import RetryPolicy as RetryPolicy
from pydantic import BaseModel as BaseModel
from typing import Any

class TerminatorStep(BasePipelineStep):
    '''A step that connects previous steps to the END node.

    This step is useful when you want to explicitly terminate a branch or the entire pipeline.
    It has no processing logic and simply acts as a connection point to the END node.

    Example:
    ```python
    pipeline = (
        step_a
        | ConditionalStep(
            name="branch",
            branches={
                "terminate": TerminatorStep("early_end"),
                "continue": step_b
            },
            condition=lambda x: "terminate" if x["should_stop"] else "continue"
        )
        | step_c
    )
    ```

    Attributes:
        name (str): A unique identifier for this pipeline step.
        retry_policy (RetryPolicy | None): Configuration for retry behavior using LangGraph\'s RetryPolicy.
    '''
    def add_to_graph(self, graph: StateGraph, previous_endpoints: list[str], retry_policy: RetryPolicy | None = None) -> list[str]:
        """Adds this step to the graph and connects it to the END node.

        This method is used by `Pipeline` to manage the pipeline's execution flow.
        It should not be called directly by users.

        Args:
            graph (StateGraph): The graph to add this step to.
            previous_endpoints (list[str]): The endpoints from previous steps to connect to.
            retry_policy (RetryPolicy | None): Configuration for retry behavior using LangGraph's RetryPolicy.
                If None, the retry policy of the step is used. If the step is not a retryable step,
                this parameter is ignored.

        Returns:
            list[str]: Empty list as this step has no endpoints (it terminates the flow).
        """
    async def execute(self, state: dict[str, Any] | BaseModel, config: RunnableConfig) -> None:
        """Executes this step, which does nothing but pass through the state.

        Args:
            state (dict[str, Any] | BaseModel): The current pipeline state.
            config (RunnableConfig): The runtime configuration.
        """
