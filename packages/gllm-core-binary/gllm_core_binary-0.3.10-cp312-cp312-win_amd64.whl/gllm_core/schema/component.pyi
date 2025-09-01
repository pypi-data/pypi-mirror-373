import abc
from abc import ABC
from gllm_core.event.event_emitter import EventEmitter as EventEmitter
from gllm_core.utils.analyzer import MethodSignature as MethodSignature, ParameterInfo as ParameterInfo, ParameterKind as ParameterKind, RunAnalyzer as RunAnalyzer, RunProfile as RunProfile
from gllm_core.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any

class Component(ABC, metaclass=abc.ABCMeta):
    '''An abstract base class for all components used throughout the Gen AI applications.

    Every instance of Component has access to class-level `_default_log_level` and `_logger`, as detailed below.
    For components that require high observability, it is recommended to set `_default_log_level` to `logging.INFO`
    or higher.

    Example:
    ```python
    class MyComponent(Component):
        _default_log_level = logging.INFO

        def _run(self, **kwargs: Any) -> Any:
            return "Hello, World!"
    ```

    Attributes:
        run_profile (RunProfile): The profile of the `_run` method.
            This property is used by `Pipeline` to analyze the input requirements of the component.
            In most cases, unless you are working with `Pipeline` and `PipelineStep`s, you will not need to use this
            property.

            **Do not override this property in your subclass.**

            You also do not need to write this attribute in your component\'s docstring.
        _default_log_level (int): The default log level for the component. Defaults to DEBUG.
        _logger (logging.Logger): The logger instance for the component.
    '''
    async def run(self, **kwargs: Any) -> Any:
        """Runs the operations defined for the component.

        This method emits the provided input arguments using an EventEmitter instance if available, executes a process
        defined in the `_run` method, and emits the resulting output if the EventEmitter is provided.

        Args:
            **kwargs (Any): A dictionary of arguments to be processed. May include an `event_emitter`
                key with an EventEmitter instance.

        Returns:
            Any: The result of the `_run` method.
        """
    @property
    def run_profile(self) -> RunProfile:
        """Analyzes the `_run` method and retrieves its profile.

        This property method analyzes the `_run` method of the class to generate a `RunProfile` object.
        It also updates the method signatures for methods that fully utilize the arguments.

        Returns:
            RunProfile: The profile of the `_run` method, including method signatures for full-pass argument usages.
        """
