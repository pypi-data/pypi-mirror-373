import ast
from _typeshed import Incomplete
from enum import StrEnum
from pydantic import BaseModel
from typing import Any

class ParameterKind(StrEnum):
    """Enum representing the different kinds of parameters a method can have."""
    POSITIONAL_ONLY = 'positional_only'
    POSITIONAL_OR_KEYWORD = 'positional_or_keyword'
    VAR_POSITIONAL = 'var_positional'
    KEYWORD_ONLY = 'keyword_only'
    VAR_KEYWORD = 'var_keyword'

class ParameterInfo(BaseModel):
    """Model representing information about a method parameter.

    Attributes:
        kind (ParameterKind): The kind of the parameter.
        default (str): The default value of the parameter, if any.
        annotation (str): The type annotation of the parameter, if any.
    """
    kind: ParameterKind
    default: str | None
    annotation: str | None

class MethodSignature(BaseModel):
    """Model representing the signature of a method.

    Attributes:
        parameters (dict[str, ParameterInfo]): A dictionary of parameter names to their information.
        is_async (bool): Whether the method is asynchronous.
    """
    parameters: dict[str, ParameterInfo]
    is_async: bool

class ArgUsages(BaseModel):
    """Model representing the different types of argument usage in a run.

    Attributes:
        required (list[str]): A list of argument names that are required.
        optional (list[str]): A list of argument names that are optional.
    """
    required: list[str]
    optional: list[str]

class RunArgumentUsageType(StrEnum):
    """Enum representing the different types of argument usage in a run."""
    FULL_PASS = 'full_pass'
    REQUIRED = 'required'
    OPTIONAL = 'optional'

class RunProfile(BaseModel):
    """Model representing the profile of a run.

    Attributes:
        arg_usages (ArgUsages): A dictionary mapping argument usage types to lists of
            argument names.
        full_pass_methods (list[str]): A list of method names that fully pass the kwargs.
        method_signatures (dict[str, MethodSignature]): A dictionary mapping method names to their signatures.
    """
    arg_usages: ArgUsages
    full_pass_methods: list[str]
    method_signatures: dict[str, MethodSignature]
    def __init__(self, **data: Any) -> None:
        """Initialize the RunProfile with the given data.

        This is to circumvent Pylint false positives due to the usage of Field(default_factory=...).
        """

class RunAnalyzer(ast.NodeVisitor):
    """AST NodeVisitor that analyzes a class to build a RunProfile.

    The run analyzer visits the AST nodes of a class to analyze the _run method and build a RunProfile.
    It will look for the usage of the **kwargs parameter in method calls and subscript expressions.
    The traversal result is stored as a RunProfile object.

    Attributes:
        cls (type): The class to analyze.
        profile (RunProfile): The profile of the run being analyzed.
    """
    cls: Incomplete
    profile: Incomplete
    def __init__(self, cls) -> None:
        """Initialize the RunAnalyzer with a class.

        Args:
            cls (type): The class to analyze.
        """
    def visit_Call(self, node: ast.Call) -> None:
        """Visit a Call node in the AST.

        This node represents a function call in the source code.
        Here, we are looking for calls to methods that fully pass the kwargs.

        Args:
            node (ast.Call): The Call node to visit.
        """
    def visit_Subscript(self, node: ast.Subscript) -> None:
        '''Visit a Subscript node in the AST.

        The Subscript node represents a subscripted value in the source code.
        Example: kwargs["key"]

        Args:
            node (ast.Subscript): The Subscript node to visit.
        '''
