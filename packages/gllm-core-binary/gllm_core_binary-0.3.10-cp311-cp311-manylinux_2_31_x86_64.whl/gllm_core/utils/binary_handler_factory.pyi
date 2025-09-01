from enum import StrEnum
from typing import Callable

class BinaryHandlingStrategy(StrEnum):
    """Enum for binary data handling options.

    Attributes:
        SKIP (str): Skip binary data.
        BASE64 (str): Encode binary data to base64.
        HEX (str): Encode binary data to hex.
        SHOW_SIZE (str): Show the size of binary data.
    """
    SKIP = 'skip'
    BASE64 = 'base64'
    HEX = 'hex'
    SHOW_SIZE = 'show_size'

def binary_handler_factory(handling_type: BinaryHandlingStrategy | str) -> Callable[[bytes], str | None]:
    """Factory function to create appropriate binary data handler.

    Args:
        handling_type (BinaryHandlingStrategy | str): The type of binary handling to use.

    Returns:
        Callable[[bytes], str | None]: A function that handles binary data according to specified type.
    """
def skip_handler(v: bytes) -> None:
    """Handler for skipping binary data.

    Args:
        v (bytes): The binary data to skip.

    Returns:
        None: The handler returns None.
    """
def base64_handler(v: bytes) -> str:
    """Handler for encoding binary data to base64.

    Args:
        v (bytes): The binary data to encode.

    Returns:
        str: The raw base64 encoded binary data.
    """
def hex_handler(v: bytes) -> str:
    """Handler for encoding binary data to hex.

    Args:
        v (bytes): The binary data to encode.

    Returns:
        str: The raw hex encoded binary data.
    """
def show_size_handler(v: bytes) -> str:
    """Handler for showing the size of binary data.

    Args:
        v (bytes): The binary data to show the size.

    Returns:
        str: The size of the binary data.
    """
