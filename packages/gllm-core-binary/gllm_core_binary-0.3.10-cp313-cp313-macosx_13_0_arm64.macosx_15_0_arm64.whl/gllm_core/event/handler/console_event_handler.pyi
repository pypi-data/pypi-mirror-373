from gllm_core.constants import EventType as EventType
from gllm_core.event.handler.event_handler import BaseEventHandler as BaseEventHandler
from gllm_core.schema import Event as Event

class ConsoleEventHandler(BaseEventHandler):
    """Defines an event handler class that prints events to the console.

    Attributes:
        name (str): The name assigned to the event handler.
    """
    async def emit(self, event: Event) -> None:
        """Emits the given event by printing it to the console.

        This method prints the event's value to the console:
        1. If the event type is `EventType.STATUS`, the event's level, timestamp, and value are printed in a formatted
           string.
        2. If the event type is `EventType.RESPONSE`, the value is printed without a newline.
        3. If the event type is `EventType.DATA`, the value is printed in a formatted string with specific
           prefix and suffix.

        Args:
            event (Event): The event to be emitted.

        Raises:
            ValueError: If the event type is invalid.
        """
