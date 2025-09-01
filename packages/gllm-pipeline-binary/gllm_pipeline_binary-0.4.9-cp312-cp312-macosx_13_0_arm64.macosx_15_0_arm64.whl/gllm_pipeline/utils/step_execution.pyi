from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from langchain_core.runnables import RunnableConfig as RunnableConfig
from typing import Any

async def execute_sequential_steps(steps: list[BasePipelineStep], state: dict[str, Any], config: RunnableConfig) -> dict[str, Any] | None:
    """Execute a sequence of steps sequentially and return accumulated state updates.

    Each step will receive the updated state from the previous step. In the end, all state updates
    will be merged into a single update dictionary.

    Args:
        steps (list[BasePipelineStep]): The steps to run sequentially.
        state (dict[str, Any]): The initial state to pass to the first step.
        config (RunnableConfig): Runtime configuration for step execution.

    Returns:
        dict[str, Any] | None: The accumulated state updates from all steps, or None if no updates.
    """
