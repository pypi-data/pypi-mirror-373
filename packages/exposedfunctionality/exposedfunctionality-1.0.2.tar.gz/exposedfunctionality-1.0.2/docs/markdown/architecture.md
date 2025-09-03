# Architecture

This package centers on serializing callable interfaces and exposed state into well‑defined, machine‑readable structures while remaining non‑intrusive to the original code.

## Components

- Function exposure (`exposedfunctionality/func.py`):
  - Adds `_is_exposed_method` flag and `ef_funcmeta: SerializedFunction` to functions.
  - Provides helpers to list or enforce exposed methods.

- Function parser (`exposedfunctionality/function_parser`):
  - `function_parser.py`: Introspects callables, resolves partials, inspects annotations, merges docstring info, and emits `SerializedFunction`.
  - `docstring_parser.py`: Parses reStructuredText, Google, and NumPy docstring styles into a normalized `DocstringParserResult`.
  - `types.py`: Converts between type objects and strings, resolves imports, handles `typing` constructs, and performs value casting.
  - `ser_types.py`: TypedDict/Protocol definitions for all serialized shapes.
  - `custom_wrapper.py`: Safer, configurable `update_wrapper` alternative and an `controlled_unwrap` utility.

- Exposed variables (`exposedfunctionality/variables`):
  - `core.py`: `ExposedValue` descriptor for typed attributes with defaults, change notifications, and optional value checkers.
  - `middleware.py`: Common value middlewares like clamping.

## Data Flow

1) You mark a function with `exposed_method()` or call `expose_method(func, ...)`.
2) The function is parsed by `function_method_parser(...)` into `SerializedFunction`.
3) Metadata is attached as `func.ef_funcmeta`, and `_is_exposed_method` is set.
4) Consumers read `ef_funcmeta` to drive UIs, forms, validation, and I/O semantics.
5) For state, `ExposedValue` fields expose typed attributes with change events and optional middleware.

## Design Choices

- Non‑copying exposure: metadata attaches to the original function.
- Robust parsing: tolerates missing annotations by defaulting to `Any` and merges docstring details.
- Serialization‑first: types and defaults are represented as strings/JSON‑safe values.
- Extensibility: allow custom types via `add_type` and custom value checkers/middleware.

