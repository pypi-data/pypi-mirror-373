from _typeshed import Incomplete
from gllm_core.constants import DefaultChunkMetadata as DefaultChunkMetadata
from gllm_core.utils.merger_method import MergerMethod as MergerMethod
from typing import Any, Callable

class ChunkMetadataMerger:
    """A helper class to merge metadata from multiple chunks.

    Attributes:
        merger_func_map (dict[str, Callable[[list[Any]], Any]]): A mapping of metadata keys to merger functions.
        default_merger_func (Callable[[list[Any]], Any]): The default merger function for metadata keys that are not
            present in the merger_func_map.
        retained_keys (set[str] | None): The keys that should be retained in the merged metadata.
            If None, all intersection keys are retained.
    """
    merger_map: Incomplete
    default_merger: Incomplete
    retained_keys: Incomplete
    def __init__(self, merger_func_map: dict[str, Callable[[list[Any]], Any]] | None = None, default_merger_func: Callable[[list[Any]], Any] | None = None, retained_keys: set[str] | None = None) -> None:
        """Initializes a new instance of the ChunkMetadataMerger class.

        Args:
            merger_func_map (dict[str, Callable[[list[Any]], Any]] | None, optional): A mapping of metadata keys to
                merger functions. Defaults to None, in which case a default merger map is used. The default merger map:
                1. Picks the first value of the PREV_CHUNK_ID key.
                2. Picks the last value of the NEXT_CHUNK_ID key.
            default_merger_func (Callable[[list[Any]], Any] | None, optional): The default merger for metadata keys that
                are not present in the merger_func_map. Defaults to None, in which case a default merger that picks the
                first value is used.
            retained_keys (set[str] | None, optional): The keys that should be retained in the merged metadata. Defaults
                to None, in which case all intersection keys are retained.
        """
    def merge(self, metadatas: list[dict[str, Any]]) -> dict[str, Any]:
        """Merges metadata from multiple chunks.

        Args:
            metadatas (list[dict[str, Any]]): The metadata to merge.

        Returns:
            dict[str, Any]: The merged metadata.
        """
