from _typeshed import Incomplete
from langchain_core.runnables import RunnableConfig as RunnableConfig
from typing import Any

class HasInputsMixin:
    """Mixin class for steps that have inputs from multiple sources.

    This mixin provides functionality for handling inputs that can come from:
    - Pipeline state mapping
    - Runtime configuration mapping
    - Fixed/constant values

    It is used by steps that need to combine inputs from multiple sources into a single set of arguments.
    """
    input_state_map: Incomplete
    runtime_config_map: Incomplete
    fixed_args: Incomplete
    def __init__(self, input_state_map: dict[str, str] | None = None, runtime_config_map: dict[str, str] | None = None, fixed_args: dict[str, Any] | None = None) -> None:
        """Initializes the input handler.

        Args:
            input_state_map (dict[str, str] | None, optional): Mapping of input names to pipeline state keys.
                Defaults to None, in which case an empty dictionary is used.
            runtime_config_map (dict[str, str] | None, optional): Mapping of input names to runtime
                configuration keys. Defaults to None, in which case an empty dictionary is used.
            fixed_args (dict[str, Any] | None, optional): Constant inputs to be included in every execution.
                Defaults to None, in which case an empty dictionary is used.
        """
