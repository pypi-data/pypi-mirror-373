from enum import Enum, IntEnum, StrEnum

class EventLevel(IntEnum):
    """Defines event levels for the event emitter module."""
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5

class EventType(str, Enum):
    """Defines event types for the event emitter module."""
    STATUS = 'status'
    RESPONSE = 'response'
    DATA = 'data'

class DefaultChunkMetadata:
    """Defines constants for default chunk metadata keys."""
    CHUNK_ID: str
    PREV_CHUNK_ID: str
    NEXT_CHUNK_ID: str

class LogFormat(StrEnum):
    """Defines supported log formats for the SDK logging system."""
    TEXT = 'text'
    JSON = 'json'
