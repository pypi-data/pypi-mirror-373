from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    TypeVar,
)
from typing_extensions import TypedDict
from pydantic import BaseModel, ConfigDict


class Endpoint(TypedDict):
    """
    Type definition for an endpoint.

    Attributes:
        middleware (Optional[List[Callable[[Any], Any]]]): A list of middleware functions for the endpoint.
    """

    middleware: Optional[List[Callable[[Any], Any]]]


class FunctionInputParam(TypedDict):
    """
    Type definition for a function parameter.

    Attributes:
        name (str): The name of the parameter, required.
        type (str): The type of the parameter, required.
        positional (bool): Whether the parameter is positional, required.
        default (Any): The default value of the parameter, optional.
        optional (bool): Whether the parameter is optional, optional.
        description (str): The description of the parameter, optional.
        middleware (List[Callable[[Any], Any]]): A list of functions that can be
            used to transform the parameter value, optional.
        endpoints (Dict[str, Endpoint]): A dictionary of endpoints that can be
            used to represent the parameter value in different contexts, optional.
    """

    name: str
    type: str
    positional: bool
    default: Any = None
    optional: bool = False
    description: str = ""
    middleware: List[Callable[[Any], Any]]
    endpoints: Dict[str, Endpoint]


class FunctionOutputParam(TypedDict):
    """
    Type definition for an output parameter.

    Attributes:
        name (str): The name of the parameter, required.
        type (str): The type of the parameter, required.
        description (Optional[str]): The description of the parameter, optional.
        endpoints (Optional[Dict[str, Endpoint]]): A dictionary of endpoints that can be used to represent the parameter value in different contexts, optional.
    """

    name: str
    type: str
    description: Optional[str] = None
    endpoints: Optional[Dict[str, Endpoint]] = None


class DocstringParserResult(TypedDict):
    """
    Type definition for a standardized parsed docstring.

    Attributes:
        original (Optional[str]): The original docstring.
        input_params (List[FunctionInputParam]): The input parameters of the function as parsed from the docstring.
        output_params (List[FunctionOutputParam]): The output parameters of the function as parsed from the docstring.
        summary (Optional[str]): The summary of the function as parsed from the docstring.
        exceptions (Dict[str, str]): The exceptions of the function as parsed from the docstring.
    """

    original: Optional[str] = None
    input_params: List[FunctionInputParam]
    output_params: List[FunctionOutputParam]
    summary: Optional[str] = None
    exceptions: Dict[str, str]


class SerializedFunction(TypedDict):
    """
    Type definition for a serialized function.

    Attributes:
        name (str): The name of the function.
        input_params (List[FunctionInputParam]): The input parameters of the function.
        output_params (List[FunctionOutputParam]): The output parameters of the function.
        docstring (Optional[DocstringParserResult]): The parsed docstring of the function.
    """

    name: str
    input_params: List[FunctionInputParam]
    output_params: List[FunctionOutputParam]
    docstring: Optional[DocstringParserResult]


ReturnType = TypeVar("ReturnType")


class ExposedFunction(Protocol[ReturnType]):
    """
    Protocol for exposed functions.

    Attributes:
        ef_funcmeta (SerializedFunction): Metadata about the exposed function.
        _is_exposed_method (bool): Indicates if the function is exposed.

    Methods:
        __call__(*args: Any, **kwargs: Any) -> ReturnType: The method signature for the function call.
    """

    ef_funcmeta: SerializedFunction
    _is_exposed_method: bool

    def __call__(self, *args: Any, **kwargs: Any) -> ReturnType: ...


class FunctionParamError(Exception):
    """Base class for function parameter errors."""

    pass


class UnknownSectionError(Exception):
    """Exception raised when an unknown section is encountered in parsing."""

    pass


class TypeNotFoundError(Exception):
    """
    Exception raised when a type cannot be found.

    Attributes:
        type_name (str): The name of the type that was not found.
    """

    def __init__(self, type_name: str):
        self.type_name = type_name
        super().__init__(f"Type '{type_name}' not found.")


# Lightweight metadata containers for typing.Annotated usage


class InputMeta(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
    """Metadata for input parameters used with typing.Annotated.

    Example:
        def fn(a: Annotated[int, InputMeta(description="count of items")]): ...

    Only non-semantic metadata is honored (e.g., description, middleware, endpoints).
    Callable semantics such as defaults/positionality are not changed by metadata.
    """

    # core fields
    name: Optional[str] = None
    type: Optional[Any] = None  # may be a string or typing type
    default: Any = None
    optional: Optional[bool] = None
    positional: Optional[bool] = None
    # metadata
    description: Optional[str] = None
    middleware: Optional[List[Callable[[Any], Any]]] = None
    endpoints: Optional[Dict[str, Endpoint]] = None


class OutputMeta(BaseModel):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)
    """Metadata for output parameters used with typing.Annotated.

    Example:
        def fn() -> Annotated[int, OutputMeta(description="result value")]: ...

    For tuple returns, annotate each element:
        def fn() -> tuple[
            Annotated[int, OutputMeta(description="first")],
            Annotated[str, OutputMeta(description="second")],
        ]: ...
    """

    # core fields
    name: Optional[str] = None
    type: Optional[Any] = None  # may be a string or typing type
    # metadata
    description: Optional[str] = None
    endpoints: Optional[Dict[str, Endpoint]] = None
