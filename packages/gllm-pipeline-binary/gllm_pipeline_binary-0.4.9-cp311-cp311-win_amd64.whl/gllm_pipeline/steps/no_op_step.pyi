from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from langchain_core.runnables import RunnableConfig as RunnableConfig
from typing import Any

class NoOpStep(BasePipelineStep):
    '''A step that does nothing.

    This step is useful when you want to add a step that does not perform any processing.
    For example, you can use this step to implement a toggle pattern for a certain component.

    Example:
    ```python
    pipeline = (
        step_a
        | ConditionalStep(
            name="branch",
            branches={
                "execute": step_b,
                "continue": NoOpStep("no_op")
            },
            condition=lambda x: "execute" if x["should_execute"] else "continue"
        )
        | step_c
    )
    ```

    Attributes:
        name (str): A unique identifier for this pipeline step.
    '''
    async def execute(self, state: dict[str, Any], config: RunnableConfig) -> None:
        """Executes this step, which does nothing.

        Args:
            state (dict[str, Any]): The current state of the pipeline.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            None: This step does not modify the pipeline state.
        """
