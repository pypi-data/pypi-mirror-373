from typing import Any, Callable

class MergerMethod:
    """A collection of merger methods."""
    @staticmethod
    def concatenate(delimiter: str = '-') -> Callable[[list[Any]], str]:
        '''Creates a function that concatenates a list of values with a delimiter.

        Args:
            delimiter (str, optional): The delimiter to use when concatenating the values. Defaults to "-".

        Returns:
            Callable[[list[Any]], str]: A function that concatenates a list of values with the delimiter.
        '''
    @staticmethod
    def pick_first(values: list[Any]) -> Any:
        """Picks the first value from a list of values.

        Args:
            values (list[Any]): The values to pick from.

        Returns:
            Any: The first value from the list.
        """
    @staticmethod
    def pick_last(values: list[Any]) -> Any:
        """Picks the last value from a list of values.

        Args:
            values (list[Any]): The values to pick from.

        Returns:
            Any: The last value from the list.
        """
    @staticmethod
    def merge_overlapping_strings(delimiter: str = '\n') -> Callable[[list[str]], str]:
        '''Creates a function that merges a list of strings, handling common prefixes and overlaps.

        The created function will:
        - Identify and remove any common prefix shared by the strings.
        - Process each pair of adjacent strings to remove overlapping strings.
        - Join the cleaned strings together, including the common prefix at the beginning.

        Args:
            delimiter (str, optional): The delimiter to use when merging the values. Defaults to "\\n".

        Returns:
            Callable[[list[str]], str]: A function that merges a list of strings, handling common prefixes and overlaps.
        '''
