import asyncio
from _typeshed import Incomplete
from gllm_core.event.handler.event_handler import BaseEventHandler as BaseEventHandler
from gllm_core.schema import Event as Event
from typing import AsyncGenerator

class StreamEventHandler(BaseEventHandler):
    """A class that manages an asynchronous stream of data using a queue.

    The StreamEventHandler class provides methods to manage an asynchronous stream, allowing data to be sent and
    retrieved in a non-blocking manner. The stream method yields items from the queue, and the emit method adds
    items to the queue. The stream can be closed by calling the close method, which ensures no further items
    are processed.

    Attributes:
        queue (asyncio.Queue): The queue used to manage an asynchronous stream.
    """
    queue: asyncio.Queue
    stream_delay: Incomplete
    def __init__(self, name: str = None, stream_delay: float = 0.01) -> None:
        """Initializes a new instance of the StreamEventHandler class.

        Args:
            name (str, optional): The name assigned to the event handler. Defaults to the class name.
            stream_delay (float, optional): The delay duration after each data stream. Needed in order for the stream
                manager to process the data stream properly. Defaults to 0.01.
        """
    async def emit(self, event: Event) -> None:
        """Emits the given event by sending it to the client via an asynchronous queue.

        This method serializes the event to a JSON and sends it to the client by adding it to an asynchronous
        queue. It also introduces a delay specified by `stream_delay` to make sure that the stream data can
        be processed properly.

        Args:
            event (Event): The event to be emitted.

        Returns:
            None
        """
    async def stream(self) -> AsyncGenerator:
        """Asynchronously yields items from the queue until a StopIteration item is encountered.

        This method continuously retrieves items from the queue and yields them. The iteration stops when a
        StopIteration item is encountered, at which point the method returns.

        Returns:
            AsyncGenerator: An asynchronous generator yielding items from the queue.
        """
    async def close(self) -> None:
        """Immediately stops the stream by placing a StopIteration item in the queue.

        This method inserts a StopIteration item into the queue without waiting, which signals the stream to stop
        processing further items.

        Returns:
            None
        """
