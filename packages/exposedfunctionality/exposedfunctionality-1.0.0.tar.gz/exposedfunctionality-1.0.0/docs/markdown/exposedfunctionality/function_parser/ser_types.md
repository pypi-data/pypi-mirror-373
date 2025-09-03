# function_parser/ser_types.py

Defines the typed, serializable schemas used across the package.

## Schemas

- `Endpoint`: Optional endpoint metadata, including `middleware: Optional[List[Callable[[Any], Any]]]`.
- `FunctionInputParam` (TypedDict):
  - `name: str`, `type: str`, `positional: bool`.
  - Optional: `default: Any`, `optional: bool`, `description: str`, `middleware: List[Callable]`, `endpoints: Dict[str, Endpoint]`.
- `FunctionOutputParam` (TypedDict):
  - `name: str`, `type: str`.
  - Optional: `description: Optional[str]`, `endpoints: Optional[Dict[str, Endpoint]]`.
- `DocstringParserResult` (TypedDict):
  - `original: Optional[str]`, `input_params: List[FunctionInputParam]`, `output_params: List[FunctionOutputParam]`, `summary: Optional[str]`, `exceptions: Dict[str, str]`.
- `SerializedFunction` (TypedDict):
  - `name: str`, `input_params: [...]`, `output_params: [...]`, `docstring: Optional[DocstringParserResult]`.
- `ExposedFunction[ReturnType]` (Protocol): Callable with `ef_funcmeta` and `_is_exposed_method`.

## Exceptions

- `FunctionParamError`: Base for parameter issues.
- `UnknownSectionError`: Raised on unknown docstring sections (from parsing helpers).
- `TypeNotFoundError`: Thrown when a type string/object cannot be resolved or stringified.

## Annotated Metadata

You can enrich inputs/outputs via `typing.Annotated` without changing callable semantics.

- `InputMeta`: Supports all input fields: `name`, `type` (string or typing type), `default`, `optional`, `positional`, `description`, `middleware`, `endpoints`.
- `OutputMeta`: Supports all output fields: `name`, `type` (string or typing type), `description`, `endpoints`.

Examples:

```python
from typing import Annotated, Optional
from exposedfunctionality import InputMeta, OutputMeta
from exposedfunctionality.function_parser import function_method_parser

def f(
    a: Annotated[int, InputMeta(description="Count of items", name="count", positional=True)],
    b: Annotated[Optional[str], InputMeta(description="Optional label", default=None, optional=True)]=None,
) -> Annotated[int, OutputMeta(description="Result value", name="result_type")]:
    return 1

ser = function_method_parser(f)
# ser["input_params"][0] includes name="count" and description
# ser["output_params"][0] includes name="result_type" and description

def g() -> tuple[
    Annotated[int, OutputMeta(description="first")],
    Annotated[str, OutputMeta(description="second")],
]:
    return 1, "x"
```

Notes:
- Annotated metadata edits serialization only; it does not change Python call semantics.
- Docstrings are still merged; Annotated metadata has highest precedence per field.
