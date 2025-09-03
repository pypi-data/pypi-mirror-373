from _typeshed import Incomplete
from gllm_core.schema import Component
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_datastore.cache.cache import BaseCache as BaseCache
from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from gllm_pipeline.steps.step_error_handler.step_error_handler import BaseStepErrorHandler as BaseStepErrorHandler
from gllm_pipeline.utils.error_handling import ErrorContext as ErrorContext
from gllm_pipeline.utils.has_inputs_mixin import HasInputsMixin as HasInputsMixin
from langchain_core.runnables import RunnableConfig as RunnableConfig
from pydantic import BaseModel
from typing import Any

class ComponentStep(BasePipelineStep, HasInputsMixin):
    """A pipeline step that executes a specific component.

    This step wraps a component, manages its inputs and outputs, and integrates it into the pipeline.

    Attributes:
        name (str): A unique identifier for this pipeline step.
        component (Component): The component to be executed in this step.
        input_state_map (dict[str, str]): Mapping of component input arguments to pipeline state keys.
        output_state (str | list[str] | None): Key(s) to extract from the component result and add to the pipeline
            state. If None, the component is executed but no state updates are performed.
        runtime_config_map (dict[str, str] | None): Mapping of component input arguments to runtime configuration keys.
        fixed_args (dict[str, Any] | None): Fixed arguments to be passed to the component.
        retry_policy (RetryPolicy | None): Configuration for retry behavior using LangGraph's RetryPolicy.
        error_handler (BaseStepErrorHandler | None): Strategy to handle errors during execution.
    """
    component: Incomplete
    output_state: Incomplete
    def __init__(self, name: str, component: Component, input_state_map: dict[str, str], output_state: str | list[str] | None = None, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None, cache_store: BaseCache | None = None, cache_config: dict[str, Any] | None = None) -> None:
        '''Initializes a new ComponentStep.

        Args:
            name (str): A unique identifier for this pipeline step.
            component (Component): The component to be executed in this step.
            input_state_map (dict[str, str]): Mapping of component input arguments to pipeline state keys.
                Keys are input arguments expected by the component, values are corresponding state keys.
            output_state ((str | list[str]) | None, optional): Key(s) to extract from the component result and add to
                the pipeline state. If None, the component is executed but no state updates are performed.
                Defaults to None.
            runtime_config_map (dict[str, str] | None, optional): Mapping of component input arguments to runtime
                configuration keys.
                Keys are input arguments expected by the component, values are runtime configuration keys.
                Defaults to None.
            fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the component.
                Defaults to None.
            retry_config (RetryConfig | None, optional): Configuration for retry behavior using
                GLLM Core\'s RetryConfig. Defaults to None, in which case no retry config is applied.
            error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
                Defaults to None, in which case the RaiseStepErrorHandler is used.
            cache_store ("BaseCache" | None, optional): Cache store to be used for caching.
                Defaults to None, in which case no cache store is used.
            cache_config (dict[str, Any] | None, optional): Cache configuration to be used for caching.
                Defaults to None, in which case no cache configuration is used.
        '''
    async def execute(self, state: dict[str, Any] | BaseModel, config: RunnableConfig) -> dict[str, Any] | None:
        """Executes the component and processes its output.

        This method validates inputs, prepares data, executes the component, and formats the output for integration
        into the pipeline state.

        Args:
            state (dict[str, Any] | BaseModel): The current state of the pipeline, containing all data.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            dict[str, Any] | None: The update to the pipeline state after this step's operation, or None if
                output_state is None. When not None, this includes new or modified data produced by the component,
                not the entire state.

        Raises:
            RuntimeError: If an error occurs during component execution.
            TimeoutError: If the component execution times out.
            asyncio.CancelledError: If the component execution is cancelled.
        """
