# function_parser/__init__.py

Public surface for function parsing utilities and types. Re‑exports:

- Docstrings: `parse_docstring`, module refs `docstring_parser`.
- Types: `serialize_type`, `string_to_type`, `type_to_string`, `add_type`, and module ref `types`.
- Schemas: `FunctionInputParam`, `FunctionOutputParam`, `SerializedFunction`, `DocstringParserResult`.
- Function parsing: `function_method_parser`, `get_resolved_signature`, module ref `function_parser`.
- Protocols/exceptions: `ExposedFunction`, `ReturnType`, `FunctionParamError`, `UnknownSectionError`, `TypeNotFoundError`.

Prefer importing these through `exposedfunctionality.function_parser` when you need direct access.

