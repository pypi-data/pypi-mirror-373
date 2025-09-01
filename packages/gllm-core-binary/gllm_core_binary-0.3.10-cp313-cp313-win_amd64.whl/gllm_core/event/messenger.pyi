from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_core.schema import Component as Component
from gllm_core.utils import get_placeholder_keys as get_placeholder_keys
from typing import Any

class Messenger(Component):
    '''Emits a custom event message with possible access to the state variables.

    This component acts as an intermediary step, designed to be placed between other pipeline steps.
    It allows for event messaging operations to be performed outside individual components but still within
    the context of the pipeline execution.

    Attributes:
        message (str): The message to be sent, may contain placeholders enclosed in curly braces `{}`.
        is_template (bool): Whether the message is a template that can be injected with state variables.
            Defaults to True.
        variable_keys (list[str]): The keys of the message that can be injected with state variables.
            Only used if `is_template` is set to True.

    Plain string message example:
    ```python
    event_emitter = EventEmitter(handlers=[ConsoleEventHandler()])
    kwargs = {"event_emitter": event_emitter}

    messenger = Messenger("Executing component.", is_template=False)
    await messenger.run(**kwargs)
    ```

    Template message example:
    ```python
    event_emitter = EventEmitter(handlers=[ConsoleEventHandler()])
    state_variables = {"query": "Hi!", "top_k": 10}
    kwargs = {"event_emitter": event_emitter, "state_variables": state_variables}

    messenger = Messenger("Executing component for query {query} and top k {top_k}.")
    await messenger.run(**kwargs)
    ```
    '''
    message: Incomplete
    is_template: Incomplete
    variable_keys: Incomplete
    def __init__(self, message: str, is_template: bool = True) -> None:
        """Initializes a new instance of the Messenger class.

        Args:
            message (str): The message to be sent, may contain placeholders enclosed in curly braces `{}`.
            is_template (bool, optional): Whether the message is a template that can be injected with state variables.
                Defaults to True.

        Raises:
            ValueError: If the keys of the message does not match the provided keys.
        """
    async def send_message(self, event_emitter: EventEmitter, state_variables: dict[str, Any] | None = None, emit_kwargs: dict[str, Any] | None = None) -> None:
        """Emits the message to the event emitter.

        This method validates the variables, formats the message if required, and then emits the message using the
        event emitter.

        Args:
            event_emitter (EventEmitter): The event emitter instance to emit the message.
            state_variables (dict[str, Any] | None, optional): The state variables to be injected into the message
                placeholders. Can only be provided if `is_template` is set to True. Defaults to None.
            emit_kwargs (dict[str, Any] | None, optional): The keyword arguments to be passed to the event emitter's
                emit method. Defaults to None.
        """
