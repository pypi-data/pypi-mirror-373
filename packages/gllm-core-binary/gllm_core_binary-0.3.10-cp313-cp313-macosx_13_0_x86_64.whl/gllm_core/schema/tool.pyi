import inspect
from _typeshed import Incomplete
from pydantic import BaseModel
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec('P')
R = TypeVar('R')
TYPE_HINT_RETURN: str
ARGUMENTS_FIELDS: Incomplete
TERMINATING_FIELDS: Incomplete

def tool(_func: Callable[P, R] | None = None, *, name: str | None = None, description: str | None = None, title: str | None = None) -> Callable[[Callable[P, R]], Callable[P, R]] | Callable[P, R]:
    '''Decorator to convert a function into a Tool.

    This decorator analyzes the function signature and type hints to generate
    the appropriate input_schema and output_schema for the tool.

    Note that the output_schema is derived from the function\'s return type.
    If the function is annotated with `-> None`, the output_schema will be empty.

    Args:
        name (str | None, optional): Optional name for the tool.
            Defaults to None, in which case the function name is used.
        description (str | None, optional): Optional description for the tool.
            Defaults to None, in which case the function\'s docstring is used.
        title (str | None, optional): Optional display title for the tool.
            Defaults to None, in which case the function name is used.

    Returns:
        Callable[[Callable[P, R]], Callable[P, R]] | Callable[P, R]:
            If _func is provided, returns a decorated function.
            Otherwise, returns a decorator that transforms a function into a Tool.

    Examples:
        ```python
        @tool(description="Get weather information")
        async def fetch_weather(location: str, units: str = "metric") -> dict:
            \'\'\'Get weather information for a location.\'\'\'
            # Implementation
            return {"temperature": 22.5, "conditions": "sunny"}

        # The function can be used normally
        result = await fetch_weather("New York", "imperial")
        ```

    The decorator returns an instance of `Tool` that is callable and preserves key function metadata
    (e.g., `__signature__`, `__doc__`). You can access the `Tool` attributes directly on the decorated
    function name:

    ```python
    # After decoration, `fetch_weather` is a Tool instance
    fetch_weather.name            # str: tool identifier (defaults to function name)
    fetch_weather.title           # str | None: display title if provided
    fetch_weather.description     # str | None: description (defaults to function docstring)
    fetch_weather.input_schema    # BaseModel: Constructed Pydantic model for input (derived from type hints)
    fetch_weather.output_schema   # BaseModel | None: Constructed Pydantic model for output (derived from return type)
    fetch_weather.is_async        # bool: whether the underlying function is async

    # You can call it directly (mirrors the original function semantics)
    result = await fetch_weather(location="Tokyo", units="metric")

    # Or use the unified invoke() helper (works for both sync and async implementations)
    result = await fetch_weather.invoke(location="Tokyo", units="metric")
    ```
    '''

class Tool(BaseModel):
    """Model Context Protocol (MCP)-style Tool definition.

    This class represents a tool that can be used by a language model to interact with the outside world,
    following the Model Context Protocol (MCP) specification. Tools are defined by their name, description,
    input and output schemas, and an optional function implementation.

    The Tool class supports flexible schema handling, accepting either:
    1. Dictionary-based JSON Schema objects
    2. Pydantic BaseModel classes

    When a Pydantic model is provided, it is automatically converted to a JSON Schema using
    Pydantic's model_json_schema() method.

    Supported use cases include:
    1. Creating a tool with dictionary schemas for input/output
    2. Creating a tool with Pydantic models for input/output
    3. Using the @tool decorator to create a tool from a function's type hints

    Attributes:
        name (str): A string identifier for the tool, used for programmatic access.
        description (str): A human-readable description of what the tool does.
        input_schema (dict[str, Any] | type[BaseModel]): JSON Schema object or Pydantic model defining the expected
            parameters.
        title (str | None): Optional display name for the tool.
        output_schema (dict[str, Any] | type[BaseModel] | None): Optional JSON Schema object or Pydantic model defining
            the structure of the output.
        annotations (dict[str, Any] | None): Optional additional tool information for enriching the tool definition.
            According to MCP, display name precedence is: title, annotations.title, then name.
        meta (dict[str, Any] | None): Optional additional metadata for internal use by the system.
            Unlike annotations which provide additional information about the tool for clients,
            meta is meant for private system-level metadata that shouldn't be exposed to end users.
        func (Callable): The callable function that implements this tool's behavior.
        is_async (bool): Whether the tool's function is asynchronous.
    """
    name: str
    input_schema: dict[str, Any] | type[BaseModel]
    description: str | None
    title: str | None
    output_schema: dict[str, Any] | type[BaseModel] | None
    annotations: dict[str, Any] | None
    meta: dict[str, Any] | None
    func: Callable | None
    is_async: bool
    model_config: Incomplete
    @classmethod
    def validate_input_schema(cls, v: Any):
        """Validate and convert input_schema to JSON Schema dict if it's a Pydantic model.

        Args:
            v (Any): The input schema value (dict or Pydantic model).

        Returns:
            dict: A JSON Schema dict.

        Raises:
            ValueError: If the input schema is not a dict or Pydantic model.
        """
    @classmethod
    def validate_output_schema(cls, v: Any):
        """Validate and convert output_schema to JSON Schema dict if it's a Pydantic model.

        Args:
            v (Any): The output schema value (dict, Pydantic model, or None).

        Returns:
            dict | None: A JSON Schema dict or None.

        Raises:
            ValueError: If the output schema is not None, dict, or Pydantic model.
        """
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the underlying function.

        Mirrors the original function's call semantics:
        1. If the underlying function is synchronous, returns the result directly.
        2. If asynchronous, returns a coroutine that must be awaited.

        Args:
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: Result or coroutine depending on the underlying function.

        Raises:
            ValueError: If no implementation function is defined.
        """
    @property
    def __signature__(self) -> inspect.Signature:
        """Expose the underlying function's signature for introspection.

        Returns:
            inspect.Signature: Signature of the underlying function, or an empty signature if missing.
        """
    async def invoke(self, **kwargs: Any) -> Any:
        """Executes the defined tool with the given parameters.

        This method handles both synchronous and asynchronous underlying functions.

        Args:
            **kwargs: The parameters to pass to the tool function.
                     These should match the input_schema definition.

        Returns:
            Any: The result of the tool execution.

        Raises:
            ValueError: If the tool function has not been defined.
            TypeError: If the provided parameters don't match the expected schema.
        """
