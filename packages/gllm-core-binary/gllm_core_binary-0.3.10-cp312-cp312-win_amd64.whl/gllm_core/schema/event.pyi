from datetime import datetime
from gllm_core.constants import EventLevel as EventLevel, EventType as EventType
from pydantic import BaseModel

class Event(BaseModel):
    """A data class to store an event attributes.

    Attributes:
        value (str): The value of the event.
        level (EventLevel): The severity level of the event. Defined through the EventLevel constants.
        type (EventType): The type of the event. Defined through the EventType constants.
        timestamp (datetime): The timestamp of the event. If not provided, the current timestamp is used.
    """
    value: str
    level: EventLevel
    type: EventType
    timestamp: datetime
    def serialize_level(self, level: EventLevel) -> str:
        """Serializes an EventLevel object into its string representation.

        This method serializes the given EventLevel object by returning its name as a string.

        Args:
            level (EventLevel): The EventLevel object to be serialized.

        Returns:
            str: The name of the EventLevel object.
        """
