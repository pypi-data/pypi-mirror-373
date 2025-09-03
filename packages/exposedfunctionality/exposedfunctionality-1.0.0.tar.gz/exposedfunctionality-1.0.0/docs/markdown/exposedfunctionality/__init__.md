# exposedfunctionality/__init__.py

Re‑exports the public API from submodules to provide a convenient package surface. It consolidates:

- Function exposure: `exposed_method`, `expose_method`, `get_exposed_methods`, `is_exposed_method`, `assure_exposed_method`, and schema types like `SerializedFunction`, `FunctionInputParam`, `FunctionOutputParam`.
- Docstring/type parsing: `function_parser`, `serialize_type`, `add_type`, `SerializedType`.
- Wrapper utilities: `controlled_wrapper`, `controlled_unwrap`, `update_wrapper`.
- Variables: `ExposedValue`, `add_exposed_value`, `get_exposed_values`.

## Version and Exports

- `__version__`: Current package version.
- `__all__`: Declares the public symbols exported at package import.

## Usage

- Prefer importing from `exposedfunctionality` directly for stable names.
- Submodules remain importable for advanced use (e.g., `function_parser.types`).

