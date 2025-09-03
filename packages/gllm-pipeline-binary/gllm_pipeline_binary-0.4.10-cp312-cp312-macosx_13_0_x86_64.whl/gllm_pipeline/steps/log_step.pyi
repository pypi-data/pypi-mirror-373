from _typeshed import Incomplete
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_datastore.cache.cache import BaseCache as BaseCache
from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from langchain_core.runnables import RunnableConfig as RunnableConfig
from pydantic import BaseModel
from typing import Any

class LogStep(BasePipelineStep):
    """A specialized pipeline step for logging messages.

    This step uses the Messenger component to log messages during pipeline execution.
    It supports both plain text messages and template messages with placeholders for state variables.

    Attributes:
        name (str): A unique identifier for this pipeline step.
        messenger (Messenger): The messenger component used to format and send messages.
        emit_kwargs (dict[str, Any]): Additional arguments to pass to the event emitter.
        retry_policy (RetryPolicy | None): Configuration for retry behavior using LangGraph's RetryPolicy.
    """
    messenger: Incomplete
    emit_kwargs: Incomplete
    def __init__(self, name: str, message: str, is_template: bool = True, emit_kwargs: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, cache_store: BaseCache | None = None, cache_config: dict[str, Any] | None = None) -> None:
        '''Initializes a new LogStep.

        Args:
            name (str): A unique identifier for this pipeline step.
            message (str): The message to be logged, may contain placeholders enclosed in curly braces.
            is_template (bool, optional): Whether the message contains placeholders. Defaults to True.
            emit_kwargs (dict[str, Any] | None, optional): Additional arguments to pass to the event emitter.
                Defaults to None.
            retry_config (RetryConfig | None, optional): Configuration for retry behavior using
                GLLM Core\'s RetryConfig. Defaults to None, in which case no retry config is applied.
            cache_store ("BaseCache" | None, optional): Cache store to be used for caching.
                Defaults to None, in which case no cache store is used.
            cache_config (dict[str, Any] | None, optional): Cache configuration to be used for caching.
                Defaults to None, in which case no cache configuration is used.
        '''
    async def execute(self, state: dict[str, Any] | BaseModel, config: RunnableConfig) -> None:
        """Executes the log step by formatting and emitting the message.

        Args:
            state (dict[str, Any] | BaseModel): The current state of the pipeline, containing all data.
            config (RunnableConfig): Runtime configuration for this step's execution.

        Returns:
            None: This step does not modify the pipeline state.

        Raises:
            RuntimeError: If an error occurs during message emission.
        """
