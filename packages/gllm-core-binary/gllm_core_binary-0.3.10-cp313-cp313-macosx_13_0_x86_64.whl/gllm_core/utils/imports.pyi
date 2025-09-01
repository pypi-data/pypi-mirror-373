from typing import Callable

def check_optional_packages(packages: str | list[str], error_message: str | None = None, install_instructions: str | None = None, extras: str | list[str] | None = None) -> None:
    """Check if optional packages are available and raise ImportError if not.

    Args:
        packages (str | list[str]): Package name or list of package names to check.
        error_message (str | None, optional): Custom error message. If None, a default message is used.
            Defaults to None.
        install_instructions (str | None, optional): Installation instructions. If None, generates poetry install
            command. Defaults to None.
        extras (str | list[str] | None, optional): Poetry extras that contain the required packages. If provided,
            generates specific installation instructions. If install_instructions is None, it will create
            default instructions based on the extras. If install_instructions is not None, it will use the
            provided instructions directly and ignore this argument. Defaults to None.

    Raises:
        ImportError: If any of the required packages are not installed.
    """
def deprecated(deprecated_in: str, removed_in: str, current_version: str | None = None, details: str = '') -> Callable:
    '''Decorator to mark functions as deprecated.

    This is currently implemented as a thin wrapper around deprecation.deprecated for consistency, since deprecation
    may be deprecated when we move into Python 3.13, where @warnings.deprecated will be available.

    Usage example:

    ```python
    @deprecated(deprecated_in="0.1.0", removed_in="0.2.0", current_version="0.1.1")
    def old_function():
        pass
    ```

    Args:
        deprecated_in (str): The version when the function was deprecated.
        removed_in (str): The version when the function will be removed.
        current_version (str | None, optional): The current version of the package. Defaults to None.
        details (str, optional): Additional details about the deprecation. Defaults to an empty string.

    Returns:
        Callable: The decorated function.
    '''
