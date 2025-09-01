from gllm_core.schema import Component
from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_pipeline.pipeline.pipeline import Pipeline as Pipeline
from gllm_pipeline.steps.component_step import ComponentStep as ComponentStep
from gllm_pipeline.steps.conditional_step import ConditionType as ConditionType, ConditionalStep as ConditionalStep, DEFAULT_BRANCH as DEFAULT_BRANCH
from gllm_pipeline.steps.guard_step import GuardStep as GuardStep
from gllm_pipeline.steps.log_step import LogStep as LogStep
from gllm_pipeline.steps.map_reduce_step import MapReduceStep as MapReduceStep
from gllm_pipeline.steps.no_op_step import NoOpStep as NoOpStep
from gllm_pipeline.steps.parallel_step import ParallelStep as ParallelStep
from gllm_pipeline.steps.pipeline_step import BasePipelineStep as BasePipelineStep
from gllm_pipeline.steps.state_operator_step import StateOperatorStep as StateOperatorStep
from gllm_pipeline.steps.step_error_handler.step_error_handler import BaseStepErrorHandler as BaseStepErrorHandler
from gllm_pipeline.steps.subgraph_step import SubgraphStep as SubgraphStep
from gllm_pipeline.steps.terminator_step import TerminatorStep as TerminatorStep
from typing import Any, Callable

def step(component: Component, input_state_map: dict[str, str], output_state: str | list[str] | None = None, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, emittable: bool = True, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None, name: str | None = None) -> ComponentStep:
    '''Create a ComponentStep with a concise syntax.

    This function creates a ComponentStep, which wraps a component and manages its inputs and outputs within the
    pipeline.

    Usage example 1:
    ```python
    retriever = Retriever()
    retriever_step = step(retriever, {"query": "input_query"}, "retrieved_data")
    ```
    This will cause the step to execute the Retriever component with the following behavior:
    1. It will pass the `input_query` from the pipeline state to the `query` argument of the Retriever.
    2. It will store the `retrieved_data` from the Retriever result in the pipeline state.

    Usage example 2:
    ```python
    retriever = Retriever()
    custom_emitter = CustomEventEmitter()
    retriever_step = step(
        retriever, {"query": "input_query"}, "retrieved_data", {"top_k": "top_k"}, {"event_emitter": custom_emitter}
    )
    ```
    This will cause the step to execute the Retriever component with the following behavior:
    1. It will pass the `input_query` from the pipeline state to the `query` argument of the Retriever.
    2. It will pass the `top_k` from the runtime configuration to the `top_k` argument of the Retriever.
    3. It will pass the `custom_emitter` to the `event_emitter` argument of the Retriever without modification.
    4. It will store the `retrieved_data` from the Retriever result in the pipeline state.

    Args:
        component (Component): The component to be executed in this step.
        input_state_map (dict[str, str]): Mapping of component input arguments to pipeline state keys.
        output_state (str | list[str] | None, optional): Key(s) to extract from the component result and add to the
            pipeline state. If None, the component is executed but no state updates are performed. Defaults to None.
        runtime_config_map (dict[str, str] | None, optional): Mapping of component arguments to runtime
            configuration keys. Defaults to None, in which case an empty dictionary is used.
        fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the component. Defaults to None,
            in which case an empty dictionary is used.
        emittable (bool, optional): Whether an event emitter should be passed to the component, if available in the
            state and not explicitly provided in any of the arguments. Defaults to True.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
            Defaults to None, in which case the RaiseStepErrorHandler is used.
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None, in which case the
            name will be the component\'s class name followed by a unique identifier.

    Returns:
        ComponentStep: An instance of ComponentStep configured with the provided parameters.
    '''
def log(message: str, is_template: bool = True, emit_kwargs: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, name: str | None = None) -> LogStep:
    '''Create a specialized step for logging messages.

    This function creates a LogStep that logs messages within a pipeline.
    It can be used to log status updates, debugging information, or any other text during pipeline execution.

    The message can be a plain string or a template with placeholders for state variables.

    Usage example 1 (plain message):
    ```python
    log_step = log("Processing document", is_template=False)
    ```

    Usage example 2 (template message with state variables):
    ```python
    log_step = log("Processing query: {query} with model: {model_name}")
    ```

    Args:
        message (str): The message to be logged. May contain placeholders in curly braces for state variables.
        is_template (bool, optional): Whether the message is a template with placeholders. Defaults to True.
        emit_kwargs (dict[str, Any] | None, optional): Additional keyword arguments to pass to the event emitter.
            Defaults to None.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        name (str | None, optional): A unique identifier for this pipeline step. If None, a name will be
            auto-generated with the prefix "log_". Defaults to None.

    Returns:
        LogStep: A specialized pipeline step for logging messages.
    '''
def if_else(condition: ConditionType | Callable[[dict[str, Any]], bool], if_branch: BasePipelineStep | list[BasePipelineStep], else_branch: BasePipelineStep | list[BasePipelineStep], input_state_map: dict[str, str] | None = None, output_state: str | None = None, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None, name: str | None = None) -> ConditionalStep:
    '''Create a simple ConditionalStep with two branches.

    This function creates a ConditionalStep that executes one of two branches based on a condition.

    The condition can be either:
    1. A Component that must return exactly "true" or "false"
    2. A callable that returns a string ("true" or "false", case insensitive)
    3. A callable that returns a boolean (will be converted to "true"/"false")

    For boolean conditions and string conditions, True/true/TRUE maps to the if_branch
    and False/false/FALSE maps to the else_branch.

    Usage example with a Callable condition:
    ```python
    # Using a Callable condition - receives merged state and config directly
    condition = lambda data: data["input"] > data["threshold"]

    if_branch = step(PositiveComponent(), {"input": "input"}, "output")
    else_branch = step(NegativeComponent(), {"input": "input"}, "output")

    if_else_step = if_else(
        condition,
        if_branch,
        else_branch,
        # input_state_map and runtime_config_map are ignored for Callable conditions,
        # but can still be specified (they will have no effect)
        output_state="condition_result",
        fixed_args={"threshold": 0}  # This will be merged with state and config
    )
    ```
    This will cause the step to execute the PositiveComponent if the `input` in the pipeline state is greater than the
    threshold (0), and the NegativeComponent otherwise. The result of the condition will be stored in the pipeline state
    under the key `condition_result`.

    Usage example with a Component condition:
    ```python
    # Using a Component condition - requires input_state_map and runtime_config_map
    threshold_checker = ThresholdChecker()  # A Component that returns "true" or "false"

    if_branch = step(PositiveComponent(), {"input": "input"}, "output")
    else_branch = step(NegativeComponent(), {"input": "input"}, "output")

    if_else_step = if_else(
        threshold_checker,
        if_branch,
        else_branch,
        input_state_map={"value": "input"},  # Maps pipeline state to component input
        output_state="condition_result",
        runtime_config_map={"threshold": "threshold_config"},  # Maps runtime config to component input
        fixed_args={"strict_mode": True}  # Fixed arguments passed directly to component
    )
    ```
    This will cause the step to execute the ThresholdChecker component with the `input` from the pipeline state
    as its `value` parameter and the `threshold_config` from runtime configuration as its `threshold` parameter.
    Based on the component\'s result ("true" or "false"), it will execute either the PositiveComponent or
    the NegativeComponent.

    Args:
        condition (ConditionType | Callable[[dict[str, Any]], bool]): The condition to evaluate.
        if_branch (BasePipelineStep | list[BasePipelineStep]): Step(s) to execute if condition is true.
        else_branch (BasePipelineStep | list[BasePipelineStep]): Step(s) to execute if condition is false.
        input_state_map (dict[str, str] | None, optional): Mapping of condition input arguments to pipeline state keys.
            This is only used if the condition is a `Component`. If the condition is a `Callable`, it receives
            a merged dictionary of the pipeline\'s state and config directly, and this parameter is ignored.
            Defaults to None.
        output_state (str | None, optional): Key to store the condition result in the pipeline state. Defaults to None.
        runtime_config_map (dict[str, str] | None, optional): Mapping of condition input arguments to runtime
            configuration keys. This is only used if the condition is a `Component`. If the condition is a `Callable`,
            it receives a merged dictionary of the pipeline\'s state and config directly, and this parameter is ignored.
            Defaults to None, in which case an empty dictionary is used.
        fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the condition. Defaults to None,
            in which case an empty dictionary is used.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
            Defaults to None, in which case the RaiseStepErrorHandler is used.
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None, in which case the
            name will be "IfElse" followed by the condition\'s function name and a unique identifier.

    Returns:
        ConditionalStep: An instance of ConditionalStep configured with the provided parameters.
    '''
def switch(condition: ConditionType, branches: dict[str, BasePipelineStep | list[BasePipelineStep]], input_state_map: dict[str, str] | None = None, output_state: str | None = None, default: BasePipelineStep | list[BasePipelineStep] | None = None, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None, name: str | None = None) -> ConditionalStep:
    '''Create a ConditionalStep with multiple branches.

    This function creates a ConditionalStep that can execute one of multiple branches based on a condition.

    Usage example with a Callable condition:
    ```python
    # Using a Callable condition - receives merged state and config directly
    def extract_command(data):
        # Access both state and config in a single dictionary
        query = data["query"]
        separator = data["separator"]  # From runtime config or state
        return query.split(separator)[0]

    branches = {
        "search": step(SearchComponent(), {"query": "query"}, "search_result"),
        "filter": step(FilterComponent(), {"query": "query"}, "filter_result"),
    }
    default = step(NoOpComponent(), {}, "no_op_result")

    switch_step = switch(
        extract_command,
        branches,
        # input_state_map and runtime_config_map are ignored for Callable conditions
        # but can still be specified (they will have no effect)
        output_state="command_type",
        default=default,
        fixed_args={"separator": " "}  # This will be merged with state and config
    )
    ```
    This will cause the step to execute the SearchComponent if the first part of the `query` in the pipeline state is
    "search", the FilterComponent if it is "filter", and the NoOpComponent otherwise. The separator is provided as a
    fixed argument. The result of the condition will be stored in the pipeline state under the key `command_type`.

    Usage example with a Component condition:
    ```python
    # Using a Component condition - requires input_state_map and runtime_config_map
    command_extractor = CommandExtractor()  # A Component that extracts command from query

    branches = {
        "search": step(SearchComponent(), {"query": "query"}, "search_result"),
        "filter": step(FilterComponent(), {"query": "query"}, "filter_result"),
        "sort": step(SortComponent(), {"query": "query"}, "sort_result"),
    }
    default = step(DefaultComponent(), {"query": "query"}, "default_result")

    switch_step = switch(
        command_extractor,
        branches,
        input_state_map={"text": "query"},  # Maps pipeline state to component input
        output_state="command_type",
        default=default,
        runtime_config_map={"delimiter": "separator_config"},  # Maps runtime config to component input
        fixed_args={"lowercase": True}  # Fixed arguments passed directly to component
    )
    ```
    This will cause the step to execute the CommandExtractor component with the `query` from the pipeline state
    as its `text` parameter and the `separator_config` from runtime configuration as its `delimiter` parameter.
    Based on the component\'s result (which should be one of "search", "filter", "sort", or something else),
    it will execute the corresponding branch component or the default component.

    Args:
        condition (ConditionType): The condition to evaluate for branch selection.
        branches (dict[str, BasePipelineStep | list[BasePipelineStep]]): Mapping of condition results to steps to
            execute.
        input_state_map (dict[str, str] | None, optional): Mapping of condition input arguments to pipeline state keys.
            This is only used if the condition is a `Component`. If the condition is a `Callable`, it receives
            a merged dictionary of the pipeline\'s state and config directly, and this parameter is ignored.
            Defaults to None.
        output_state (str | None, optional): Key to store the condition result in the pipeline state. Defaults to None.
        default (BasePipelineStep | list[BasePipelineStep] | None, optional): Default branch to execute if no
            condition matches. Defaults to None.
        runtime_config_map (dict[str, str] | None, optional): Mapping of condition input arguments to runtime
            configuration keys. This is only used if the condition is a `Component`. If the condition is a `Callable`,
            it receives a merged dictionary of the pipeline\'s state and config directly, and this parameter is ignored.
            Defaults to None.
        fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the condition. Defaults to None.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
            Defaults to None, in which case the RaiseStepErrorHandler is used.
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None, in which case the
            name will be "Switch" followed by the condition\'s function name and a unique identifier.

    Returns:
        ConditionalStep: An instance of ConditionalStep configured with the provided parameters.
    '''
def transform(operation: Callable[[dict[str, Any]], Any], input_states: list[str], output_state: str | list[str], runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None, name: str | None = None) -> StateOperatorStep:
    '''Create a StateOperatorStep for transforming state data.

    This function creates a StateOperatorStep that applies a transformation operation to the pipeline state.
    Note that the function `operation` should accept a dictionary of input data and return the operation result.

    Usage example:
    ```python
    def sort(data: dict) -> dict:
        is_reverse = data["reverse"]
        data["chunk"] = sorted(data["chunk"], reverse=is_reverse)


    transform_step = transform(sort, ["chunk"], "output", runtime_config={"reverse": True})
    ```
    This will cause the step to execute the `sort` operation on the `chunk` in the pipeline state. The result will be
    stored in the pipeline state under the key `output`. The behavior is controlled by the runtime configuration key
    `reverse`.

    Args:
        operation (Callable[[dict[str, Any]], Any]): The operation to execute on the input data.
        input_states (list[str]): List of input state keys required by the operation.
        output_state (str | list[str]): Key(s) to store the operation result in the pipeline state.
        runtime_config_map (dict[str, str] | None, optional): Mapping of operation input arguments to runtime
            configuration keys. Defaults to None.
        fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the operation. Defaults to None.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
            Defaults to None, in which case the RaiseStepErrorHandler is used.
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None, in which case the
            name will be "Transform" followed by the operation\'s function name and a unique identifier.

    Returns:
        StateOperatorStep: An instance of StateOperatorStep configured with the provided parameters.
    '''
def bundle(input_states: list[str], output_state: str | list[str], retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None, name: str | None = None) -> StateOperatorStep:
    '''Create a StateOperatorStep to combine multiple state keys.

    This function creates a StateOperatorStep that combines multiple keys from the pipeline state into a single output
    without modifying the data.

    Usage example:
    ```python
    bundle_step = bundle(["input1", "input2"], "output")
    ```
    This will cause the step to bundle the values of `input1` and `input2` from the pipeline state into a single
    dictionary. The result will be stored in the pipeline state under the key `output`.

    Args:
        input_states (list[str]): List of input state keys to be bundled.
        output_state (str | list[str]): Key(s) to store the bundled data in the pipeline state.
        error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
            Defaults to None, in which case the RaiseStepErrorHandler is used.
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None, in which case the
            name will be "Bundle" followed by a unique identifier.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.

    Returns:
        StateOperatorStep: An instance of StateOperatorStep configured to bundle the input states.
    '''
def guard(condition: ConditionType | Callable[[dict[str, Any]], bool], success_branch: BasePipelineStep | list[BasePipelineStep], failure_branch: BasePipelineStep | list[BasePipelineStep] | None = None, input_state_map: dict[str, str] | None = None, output_state: str | None = None, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, name: str | None = None) -> GuardStep:
    '''Create a GuardStep with a concise syntax.

    This function creates a GuardStep that can terminate pipeline execution if a condition is not met.

    Usage example:
    ```python
    auth_check = lambda state: state["is_authenticated"]
    success_step = step(SuccessHandler(), {"input": "input"}, "output")
    error_step = step(ErrorHandler(), {"error": "auth_error"}, "error_message")

    guard_step = guard(
        auth_check,
        success_branch=success_step,
        failure_branch=error_step,
        input_state_map={"user_id": "current_user"},
        output_state="auth_result"
    )
    ```

    Args:
        condition (ConditionType | Callable[[dict[str, Any]], bool]): The condition to evaluate.
        success_branch (BasePipelineStep | list[BasePipelineStep]): Steps to execute if condition is True.
        failure_branch (BasePipelineStep | list[BasePipelineStep] | None, optional): Steps to execute if condition
            is False. If None, pipeline terminates immediately. Defaults to None.
        input_state_map (dict[str, str] | None, optional): Mapping of condition input arguments to pipeline state keys.
            Defaults to None.
        output_state (str | None, optional): Key to store the condition result in the pipeline state. Defaults to None.
        runtime_config_map (dict[str, str] | None, optional): Mapping of condition input arguments to runtime
            configuration keys. Defaults to None, in which case an empty dictionary is used.
        fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the condition. Defaults to None,
            in which case an empty dictionary is used.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None, in which case the
            name will be "Guard" followed by the condition\'s function name and a unique identifier.

    Returns:
        GuardStep: An instance of GuardStep configured with the provided parameters.
    '''
def terminate(name: str | None = None, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None) -> TerminatorStep:
    '''Create a TerminatorStep to end pipeline execution.

    This function creates a TerminatorStep that explicitly terminates a branch or the entire pipeline.

    Usage example:
    ```python
    early_exit = terminate("early_exit")

    pipeline = (
        step_a
        | if_else(should_stop, early_exit, step_b)
        | step_c
    )
    ```

    Args:
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None, in which case the
            name will be "Terminator" followed by a unique identifier.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
            Defaults to None, in which case the RaiseStepErrorHandler is used.

    Returns:
        TerminatorStep: An instance of TerminatorStep.
    '''
def no_op(name: str | None = None) -> NoOpStep:
    '''Create a NoOpStep to add a step that does nothing.

    This function creates a PassThroughStep that does nothing.

    Args:
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None, in which case the
            name will be "NoOp" followed by a unique identifier.

    Returns:
        NoOpStep: An instance of NoOpStep.
    '''
def toggle(condition: ConditionType | Callable[[dict[str, Any]], bool] | str, if_branch: BasePipelineStep | list[BasePipelineStep], input_state_map: dict[str, str] | None = None, output_state: str | None = None, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None, name: str | None = None) -> ConditionalStep:
    '''Create a ConditionalStep that toggles between a branch and a no-op.

    This function creates a ConditionalStep that executes a branch if the condition is true,
    and does nothing (no-op) if the condition is false.

    The condition can be:
    1. A Component that must return exactly "true" or "false"
    2. A callable that returns a string ("true" or "false", case insensitive)
    3. A callable that returns a boolean (will be converted to "true"/"false")
    4. A string key that will be looked up in the merged state data (state + runtime config + fixed args).
        The value will be evaluated for truthiness - any non-empty, non-zero, non-False value will be considered True.

    Usage example with a Callable condition:
    ```python
    # Using a Callable condition - receives merged state and config directly
    condition = lambda data: data["feature_enabled"] and data["user_tier"] >= 2
    feature_step = step(FeatureComponent(), {"input": "input"}, "output")

    toggle_step = toggle(
        condition,
        feature_step,
        output_state="feature_status",
        fixed_args={"user_tier": 2}  # This will be merged with state and config
    )
    ```
    This will execute the FeatureComponent only if both `feature_enabled` is true and `user_tier` is at least 2.
    Otherwise, it will do nothing. The condition result will be stored in the pipeline state under the key
    `feature_status`.

    Usage example with a Component condition:
    ```python
    # Using a Component condition - requires input_state_map and runtime_config_map
    feature_checker = FeatureChecker()  # A Component that returns "true" or "false"
    feature_step = step(FeatureComponent(), {"input": "input"}, "output")

    toggle_step = toggle(
        feature_checker,
        feature_step,
        input_state_map={"user_id": "current_user"},  # Maps pipeline state to component input
        output_state="feature_status",
        runtime_config_map={"feature_name": "target_feature"},  # Maps runtime config to component input
        fixed_args={"check_permissions": True}  # Fixed arguments passed directly to component
    )
    ```
    This will cause the step to execute the FeatureChecker component with the `current_user` from the pipeline state
    as its `user_id` parameter and the `target_feature` from runtime configuration as its `feature_name` parameter.
    Based on the component\'s result ("true" or "false"), it will either execute the FeatureComponent or do nothing.

    Usage example with string key:
    ```python
    # Using a string key - looks up the value in the merged state and config
    feature_step = step(FeatureComponent(), {"input": "input"}, "output")
    toggle_step = toggle("feature_enabled", feature_step, runtime_config_map={"feature_enabled": "enable_feature"})
    ```
    This will execute the FeatureComponent only if the value at the key `feature_enabled` in the pipeline state
    (or `enable_feature` in the runtime config) evaluates to True. Otherwise, it will do nothing.

    Args:
        condition (ConditionType | Callable[[dict[str, Any]], bool] | str): The condition to evaluate.
        if_branch (BasePipelineStep | list[BasePipelineStep]): Step(s) to execute if condition is true.
        input_state_map (dict[str, str] | None, optional): Mapping of condition input arguments to pipeline state keys.
            Defaults to None.
        output_state (str | None, optional): Key to store the condition result in the pipeline state. Defaults to None.
        runtime_config_map (dict[str, str] | None, optional): Mapping of condition input arguments to runtime
            configuration keys. Defaults to None.
        fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the condition. Defaults to None.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
            Defaults to None, in which case the RaiseStepErrorHandler is used.
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None, in which case the
            name will be "Toggle" followed by a unique identifier.

    Returns:
        ConditionalStep: An instance of ConditionalStep configured with the provided parameters.
    '''
def subgraph(subgraph: Pipeline, input_state_map: dict[str, str] | None = None, output_state_map: dict[str, str] | None = None, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, error_handler: BaseStepErrorHandler | None = None, name: str | None = None) -> SubgraphStep:
    '''Create a SubgraphStep that executes another pipeline as a subgraph.

    This function creates a SubgraphStep that allows for encapsulation and reuse of pipeline logic by treating
    another pipeline as a step. The subgraph can have its own state schema, and this step handles the mapping
    between the parent and subgraph states.

    The SubgraphStep gracefully handles missing state keys - if a key specified in input_state_map is not present
    in the parent state, it will be omitted from the subgraph input rather than causing an error. This allows
    for flexible composition of pipelines with different state schemas.

    Usage example:
    ```python
    from typing import TypedDict
    from gllm_pipeline.pipeline.pipeline import Pipeline

    # Define state schemas using TypedDict
    class SubgraphState(TypedDict):
        query: str
        retrieved_data: list
        reranked_data: list

    class ParentState(TypedDict):
        user_input: str
        query: str
        reranked: list
        response: str

    # Define a subgraph pipeline with its own state schema
    subgraph_pipeline = Pipeline(
        [
            step(Retriever(), {"query": "query"}, "retrieved_data"),
            step(Reranker(), {"data": "retrieved_data"}, "reranked_data")
        ],
        state_type=SubgraphState
    )

    # Use the subgraph in a parent pipeline
    parent_pipeline = Pipeline(
        [
            step(QueryProcessor(), {"input": "user_input"}, "query"),
            subgraph(
                subgraph_pipeline,
                {"query": "query"},  # Map parent state to subgraph input
                {"reranked": "reranked_data"},  # Map subgraph output to parent state
                runtime_config_map={"top_k": "retrieval_top_k"}
            ),
            step(ResponseGenerator(), {"data": "reranked"}, "response")
        ],
        state_type=ParentState
    )

    # When the parent pipeline runs:
    # 1. QueryProcessor processes user_input and produces query
    # 2. SubgraphStep creates a new state for the subgraph with query from parent
    # 3. Subgraph executes its steps (Retriever → Reranker)
    # 4. SubgraphStep maps reranked_data from subgraph to reranked in parent
    # 5. ResponseGenerator uses reranked to produce response
    ```

    Args:
        subgraph (Pipeline): The pipeline to be executed as a subgraph.
        input_state_map (dict[str, str] | None, optional): Mapping of subgraph input keys to parent pipeline state keys.
            Keys that don\'t exist in the parent state will be gracefully ignored. If None, all subgraph inputs will be
            passed as-is.
        output_state_map (dict[str, str] | None, optional): Mapping of parent pipeline state keys to subgraph
            output keys. If None, all subgraph outputs will be passed as-is.
        runtime_config_map (dict[str, str] | None, optional): Mapping of subgraph input keys to runtime
            configuration keys. Defaults to None, in which case an empty dictionary is used.
        fixed_args (dict[str, Any] | None, optional): Fixed arguments to be passed to the subgraph.
            Defaults to None, in which case an empty dictionary is used.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using the SDK\'s RetryConfig.
            If None, no retry policy is applied. Defaults to None.
        error_handler (BaseStepErrorHandler | None, optional): Strategy to handle errors during execution.
            Defaults to None, in which case the RaiseStepErrorHandler is used.
        name (str | None, optional): A unique identifier for this pipeline step. Defaults to None,
            in which case the name will be "Subgraph" followed by a unique identifier.

    Returns:
        SubgraphStep: An instance of SubgraphStep configured with the provided parameters.
    '''
def parallel(branches: list[BasePipelineStep | list[BasePipelineStep]], input_states: list[str] | None = None, squash: bool = True, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, name: str | None = None) -> ParallelStep:
    '''Create a ParallelStep that executes multiple branches concurrently.

    This function creates a ParallelStep that runs multiple branches in parallel and merges their results.
    Each branch can be a single step or a list of steps to execute sequentially.

    The step supports two execution modes controlled by the `squash` parameter:
    1. Squashed (default): Uses asyncio.gather() to run branches in parallel within a single LangGraph node. Use for:
       a. Better raw performance
       b. Simpler implementation
       c. Less overhead
       d. Less transparent for debugging and tracing
    2. Expanded (squash=False): Creates a native LangGraph structure with multiple parallel paths. Use for:
       a. More native LangGraph integration
       b. More transparent for debugging and tracing

    For memory optimization, you can specify input_states to pass only specific keys to branches.
    This is especially useful when the state is large but branches only need specific parts of it.
    If input_states is None (default), all state keys will be passed.

    Usage example:
    ```python
    parallel_step = parallel(
        branches=[
            step(ComponentA(), {"input": "query"}, "output_a"),
            [
                step(ComponentB1(), {"input": "query"}, "output_b1"),
                step(ComponentB2(), {"input": "output_b1"}, "output_b2")
            ],
            step(ComponentC(), {"input": "query"}, "output_c")
        ],
        input_states=["query"],  # Only \'query\' will be passed to branches
    )
    ```

    Important note about input_states:
    1. If input_states is provided, only the keys listed will be passed to the branches
    2. If input_states is None (default), all state keys will be passed to the branches
    3. Each branch is responsible for its own state management once execution begins
    4. For sequential branches (lists of steps), later steps in the branch can still
      access outputs from earlier steps in the same branch

    Args:
        branches (list[BasePipelineStep | list[BasePipelineStep]]):
            List of branches to execute in parallel. Each branch can be a single step
            or a list of steps to execute sequentially.
        input_states (list[str] | None, optional): Keys from the state to pass to branches.
            If None, all state keys will be passed. Defaults to None.
        squash (bool, optional): Whether to squash execution into a single node.
            If True, uses asyncio.gather() to run branches in parallel.
            If False, uses native LangGraph structures for parallelism.
            Defaults to True.
        runtime_config_map (dict[str, str] | None, optional): Mapping of input keys to runtime config keys.
            Defaults to None.
        fixed_args (dict[str, Any] | None, optional): Fixed arguments to include in the state passed to branches.
            Defaults to None.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        name (str | None, optional): A unique identifier for this parallel step.
            Defaults to None. In this case, a name will be auto-generated.

    Returns:
        ParallelStep: An instance of ParallelStep configured with the provided branches.
    '''
def map_reduce(input_state_map: dict[str, str], output_state: str, map_func: Component | Callable[[dict[str, Any]], Any], reduce_func: Callable[[list[Any]], Any] = ..., runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None, retry_config: RetryConfig | None = None, name: str | None = None) -> MapReduceStep:
    '''Create a MapReduceStep that maps a function over multiple inputs and reduces the results.

    This function creates a step that applies a mapping function to multiple inputs in parallel
    and combines the results using a reduction function.

    The `map_func` receives a dictionary for each item being processed. This dictionary contains:
    1. Values from `input_state_map` (with list inputs split into individual items).
    2. Values from `runtime_config_map` (if provided).
    3. Values from `fixed_args` (if provided).

    The `map_func` can be either:
    - A callable function that takes a dictionary as input and returns a result.
    - A `Component` instance, which will be executed with proper async handling.

    Important note on parallel execution:
    1. For true parallelism, the `map_func` MUST be an async function or a `Component`.
    2. Synchronous map functions will block the event loop and run sequentially.

    The step supports automatic broadcasting of scalar values and handles lists appropriately:
    1. If multiple list inputs are provided, they must be the same length.
    2. Scalar inputs are broadcasted to match list lengths.

    Usage Examples:
    Example 1: Processing a list of items with an async map function.
    ```python
    async def count_words(item):
        await asyncio.sleep(0.1)  # Simulate I/O operation
        return len(item["document"].split())

    process_docs = map_reduce(
        input_state_map={
            "document": "documents" # A list, e.g. ["doc1...", "doc2...", "doc3..."]
        },
        output_state="word_counts", # A list of word counts for each document
        map_func=count_words,
        reduce_func=lambda results: sum(results), # Sum word counts
    )

    # When executed with {"documents": ["doc1...", "doc2...", "doc3..."]},
    # returns {"word_counts": 60} (total word count)
    ```

    Example 2: Broadcasting scalar values to match list length
    ```python
    # Apply a common threshold to multiple values
    threshold_check = map_reduce(
        input_state_map={
            "value": "values",          # A list: [5, 10, 15]
            "threshold": "threshold",   # A scalar: 8 (will be broadcast)
        },
        output_state="above_threshold",
        map_func=lambda item: item["value"] > item["threshold"],
        reduce_func=lambda results: results  # Return list of boolean results
    )
    # When executed with {"values": [5, 10, 15], "threshold": 8},
    # returns {"above_threshold": [False, True, True]}
    ```

    Example 3: Multiple list inputs with the same length
    ```python
    similarity_step = map_reduce(
        input_state_map={
            "doc1": "documents_a",  # ["doc1", "doc2", "doc3"]
            "doc2": "documents_b",  # ["docA", "docB", "docC"]
        },
        output_state="similarity_scores",
        map_func=lambda item: calculate_similarity(item["doc1"], item["doc2"]),
        reduce_func=lambda results: sum(results) / len(results)  # Average similarity
    )
    # When executed with {"documents_a": ["doc1", "doc2", "doc3"], "documents_b": ["docA", "docB", "docC"]},
    # returns {"similarity_scores": 0.75}
    ```

    Example 4: Using a Component for complex processing instead of a map function
    ```python
    summarizer = TextSummarizer() # Subclass of Component
    summarize_step = map_reduce(
        input_state_map={
            "text": "documents",            # List of documents to summarize
            "max_length": "max_length",     # Scalar parameter (broadcasted)
        },
        output_state="summaries",
        map_func=summarizer,
        reduce_func=lambda results: [r["summary"] for r in results]
    )
    # When executed with {"documents": ["doc1...", "doc2..."], "max_length": 50},
    # returns {"summaries": ["summary1...", "summary2..."]}
    ```

    Args:
        input_state_map (dict[str, str]): Mapping of function arguments to pipeline state keys.
        output_state (str): Key to store the reduced result in the pipeline state.
        map_func (Component | Callable[[dict[str, Any]], Any]): Function to apply to each input item.
            The map function receives a dictionary containing the input values derived from input_state_map,
            runtime_config_map, and fixed_args.
        reduce_func (Callable[[list[Any]], Any], optional): Function to reduce the mapped results.
            Defaults to a function that returns the list of results as is.
        runtime_config_map (dict[str, str] | None, optional): Mapping of arguments to runtime config keys.
        fixed_args (dict[str, Any] | None, optional): Fixed arguments to pass to the functions.
        retry_config (RetryConfig | None, optional): Configuration for retry behavior using GLLM Core\'s RetryConfig.
            Defaults to None, in which case no retry config is applied.
        name (str | None, optional): A unique identifier for this step. Defaults to None, in which case the name will be
            "MapReduce" followed by the map function name.

    Returns:
        MapReduceStep: An instance of MapReduceStep configured with the provided parameters.
    '''
