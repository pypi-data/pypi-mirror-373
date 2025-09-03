# function_parser/function_parser.py

Serializes callables into a `SerializedFunction` schema by combining signature/annotations with parsed docstrings.

## Key APIs

- `get_base_function(func) -> (base_func, preset_args, preset_kwargs)`: Resolves nested `functools.partial` chains.
- `get_resolved_signature(func, class_member_attributes=None) -> (Signature, base_func)`: Drops preset args/kwargs and class receivers (default `self`, `cls`).
- `function_method_parser(func) -> SerializedFunction`: Main entry; builds inputs/outputs and merges docstring data.

## Inputs Construction

- Parameters are inspected from the resolved signature.
- Types: From `typing.get_type_hints`; missing annotations default to `Any` with a warning.
- Defaults: JSON‑serializable; non‑serializable defaults are coerced to names/strings.
- Positionality/optional: Computed from kind/defaults; rest refined by docstrings.

## Outputs Construction

- Return annotation:
  - `None` → no outputs.
  - `Tuple[...]` → `out0`, `out1`, ...
  - other → single `out`.
- Docstrings can replace/enrich outputs by name or position.

## Docstring Merge

- For inputs: fill missing description/type/default; adjust optional/positional based on defaults.
- For outputs: if none inferred, take docstring ones; otherwise merge by name (`out` vs `out0`) when applicable.

## Result Shape

```json
{
  "name": str,
  "input_params": List[FunctionInputParam],
  "output_params": List[FunctionOutputParam],
  "docstring": DocstringParserResult | None
}
```

