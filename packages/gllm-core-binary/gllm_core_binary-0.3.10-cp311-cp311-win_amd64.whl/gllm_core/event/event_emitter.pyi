from _typeshed import Incomplete
from gllm_core.constants import EventLevel as EventLevel, EventType as EventType
from gllm_core.event.handler.event_handler import BaseEventHandler as BaseEventHandler
from gllm_core.schema import Event as Event

class EventEmitter:
    """Handles events emitting using event handlers with various levels and types.

    The `EventEmitter` class is responsible for handling and emitting events using a list of event handlers.
    Events are processed based on their severity level and type, with the option to disable specific handlers.

    Attributes:
        handlers (list[BaseEventHandler]): A list of event handlers to process emitted events.
        severity (int): The minimum severity level of events to be processed.

    Raises:
        ValueError: If the event handlers list is empty.
        ValueError: If an invalid event level is provided.
    """
    handlers: Incomplete
    severity: Incomplete
    def __init__(self, handlers: list[BaseEventHandler], event_level: EventLevel = ...) -> None:
        """Initializes a new instance of the EventEmitter class.

        Args:
            handlers (list[BaseEventHandler]): A list of event handlers to process emitted events.
            event_level (EventLevel, optional): The minimum severity level of events to be processed.
                Defaults to EventLevel.INFO.
        """
    async def emit(self, value: str, event_level: EventLevel = ..., event_type: EventType = ..., disabled_handlers: list[str] = None) -> None:
        """Emits an event using the event handlers with the specified severity and type.

        This method emits an event by creating an `Event` object with the provided message, severity level,
        and event type. It then passes the event to the available handlers, unless they are listed in the disabled
        handlers. The event will only be processed if its severity is greater than or equal to the configured
        severity level of the `EventEmitter`.

        Args:
            value (str): The event message to be emitted.
            event_level (EventLevel, optional): The severity level of the event. Defaults to EventLevel.DEBUG.
            event_type (EventType, optional): The type of event (e.g., status, response). Defaults to EventType.STATUS.
            disabled_handlers (list[str], optional): The list of handler names to be disabled. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If the provided `event_level` is not a valid `EventLevel`.
            ValueError: If the provided `event_type` is not a valid `EventType`.
        """
    async def close(self) -> None:
        """Closes all handlers in the handler list.

        This method iterates through the list of handlers and calls the `close` method on each handler.

        Returns:
            None
        """
