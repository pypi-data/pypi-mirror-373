# exposedfunctionality/func.py

Provides the API to expose functions and retrieve their serialized metadata.

## Key APIs

- `exposed_method(name=None, inputs=None, outputs=None)`: Decorator that exposes a function. Delegates to `expose_method`.
- `expose_method(func, name=None, inputs=None, outputs=None) -> ExposedFunction`: Exposes an existing callable.
- `get_exposed_methods(obj) -> Dict[str, Tuple[Callable, SerializedFunction]]`: Lists exposed methods on an object/class.
- `is_exposed_method(obj) -> bool`: Checks whether a callable is exposed.
- `assure_exposed_method(obj, **kwargs) -> ExposedFunction`: Idempotently exposes a callable if not already exposed.

## Behavior

- Parsing: Uses `function_parser.function_method_parser` to compute `SerializedFunction` (inputs, outputs, docstring, name).
- Overrides: Provided `inputs`/`outputs` are merged by `nested_update`, preserving previous values under `_`‑prefixed keys if changed.
- Naming: If a new `name` is provided, the original name is saved to `ef_funcmeta["_name"]`.
- Marking: Sets `_is_exposed_method=True` on the function; attaches `ef_funcmeta` with the serialized structure.
- Immutability: If the target is read‑only, wraps it with a thin function to carry attributes without altering behavior.

## Types

- `ExposedFunction[ReturnType]`: Protocol for exposed callables with `ef_funcmeta` and `_is_exposed_method` attributes.
- `SerializedFunction`: Dict with `name`, `input_params`, `output_params`, `docstring`.
- `FunctionInputParam`/`FunctionOutputParam`: TypedDicts for parameter metadata.

## Example

```python
from exposedfunctionality import exposed_method, get_exposed_methods

@exposed_method(name="sum_two")
def add(a: int, b: int) -> int:
    """Adds two integers."""
    return a + b

print(add.ef_funcmeta["name"])         # "sum_two"
print(get_exposed_methods(globals())["add"][1]["input_params"])  # metadata
```

## Edge Cases

- Missing annotations: Inputs default to type `Any` with a warning, and docstrings may refine types.
- Partials/methods: Signatures are resolved to omit preset args and class receivers (e.g., `self`).
- Multiple outputs: Tuple returns are expanded to `out0`, `out1`, ... unless refined by docstrings.

