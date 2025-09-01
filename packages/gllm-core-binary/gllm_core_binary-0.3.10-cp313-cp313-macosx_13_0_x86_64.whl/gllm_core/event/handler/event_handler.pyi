import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from gllm_core.schema import Event as Event

class BaseEventHandler(ABC, metaclass=abc.ABCMeta):
    """An abstract base class for all event handlers used throughout the Gen AI applications.

    Attributes:
        name (str): The name assigned to the event handler.
    """
    name: Incomplete
    def __init__(self, name: str = None) -> None:
        """Initializes a new instance of the BaseEventHandler class.

        Args:
            name (str, optional): The name assigned to the event handler. Defaults to the class name.
        """
    @abstractmethod
    async def emit(self, event: Event) -> None:
        """Emits the given event.

        This abstract method must be implemented by subclasses to define how an event is emitted.

        Args:
            event (Event): The event to be emitted.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
    async def close(self) -> None:
        """Closes the event handler.

        By default, this method does nothing. Subclasses can override this method to perform cleanup tasks
        (e.g., closing connections or releasing resources) when needed. Event handlers that do not require
        cleanup can inherit this default behavior without any changes.

        Returns:
            None
        """
