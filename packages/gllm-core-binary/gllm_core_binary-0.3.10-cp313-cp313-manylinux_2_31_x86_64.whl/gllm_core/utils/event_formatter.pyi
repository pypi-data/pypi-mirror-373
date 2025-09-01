from _typeshed import Incomplete
from gllm_core.schema import Chunk as Chunk
from gllm_core.schema.chunk import MAX_PREVIEW_LENGTH as MAX_PREVIEW_LENGTH

TEMPLATE_VALIDATOR_REGEX: Incomplete

def format_chunk_message(chunk: Chunk, rank: int = None, include_score: bool = True, include_metadata: bool = True) -> str:
    """Formats a log to display a single chunk.

    Args:
        chunk (Chunk): The chunk to be formatted.
        rank (int, optional): The optional rank of the formatted chunk. Defaults to None.
        include_score (bool, optional): Whether to include the score in the formatted message. Defaults to True.
        include_metadata (bool, optional): Whether to include the metadata in the formatted message. Defaults to True.

    Returns:
        str: A formatted log message that displays information about the logged chunk.
    """
def get_placeholder_keys(template: str) -> list[str]:
    """Extracts keys from a template string based on a regex pattern.

    This function searches the template for placeholders enclosed in single curly braces `{}` and ignores
    any placeholders within double curly braces `{{}}`. It returns a list of the keys found.

    Args:
        template (str): The template string containing placeholders.

    Returns:
        list[str]: A list of keys extracted from the template.
    """
