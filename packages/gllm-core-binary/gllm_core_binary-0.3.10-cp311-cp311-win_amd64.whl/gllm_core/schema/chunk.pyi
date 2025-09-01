from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any, Generic, Iterable, TypeVar

MAX_PREVIEW_LENGTH: int
MAX_ITEMS_PREVIEW: int
T = TypeVar('T')

class _TruncatedIterable(Generic[T]):
    """Represents a truncated iterable with first and last elements visible.

    Attributes:
        items (Iterable[T]): The iterable to be truncated.
        max_items_preview (int): Maximum number of items to show before truncation.
    """
    items: Incomplete
    max_items_preview: Incomplete
    def __init__(self, items: Iterable[T], max_items_preview: int = ...) -> None:
        """Initialize a TruncatedIterable.

        Args:
            items (Iterable[T]): The iterable to be truncated.
            max_items_preview (int, optional): Maximum number of items to show before truncation.
                Defaults to MAX_ITEMS_PREVIEW.
        """

class Chunk(BaseModel, arbitrary_types_allowed=True):
    """Represents a chunk of content retrieved from a vector store.

    Attributes:
        id (str): A unique identifier for the chunk. Defaults to a random UUID.
        content (str | bytes): The content of the chunk, either text or binary.
        metadata (dict[str, Any]): Additional metadata associated with the chunk. Defaults to an empty dictionary.
        score (float | None): Similarity score of the chunk (if available). Defaults to None.
    """
    id: str
    content: str | bytes
    metadata: dict[str, Any]
    score: float | None
    @classmethod
    def validate_content(cls, value: str | bytes) -> str | bytes:
        """Validate the content of the Chunk.

        This is a class method required by Pydantic validators. As such, it follows its signature and conventions.

        Args:
            value (str | bytes): The content to validate.

        Returns:
            str | bytes: The validated content.

        Raises:
            ValueError: If the content is empty or not a string or bytes.
        """
    def is_text(self) -> bool:
        """Check if the content is text.

        Returns:
            bool: True if the content is text, False otherwise.
        """
    def is_binary(self) -> bool:
        """Check if the content is binary.

        Returns:
            bool: True if the content is binary, False otherwise.
        """
