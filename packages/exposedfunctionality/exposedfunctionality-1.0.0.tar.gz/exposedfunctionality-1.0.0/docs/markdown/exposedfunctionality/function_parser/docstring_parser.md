# function_parser/docstring_parser.py

Parses function/method docstrings into a normalized `DocstringParserResult` supporting reStructuredText, Google, and NumPy styles.

## Core Concepts

- Normalization: `_unify_parser_results` ensures consistent fields and formatting across styles (inputs, outputs, exceptions, summary, original).
- Style detection: `select_extraction_function` picks the best parser based on content heuristics.
- Fallback: `parse_docstring` returns a minimal result with a `summary` when no structure is detected.

## Supported Styles

- reStructuredText (Sphinx): `:param name: ...`, `:type name: ...`, `:raises E: ...`, `:return: ...`, `:rtype: ...`.
- Google: `Args:`, `Returns:`, `Raises:` with `name (type): description` entries and multiline support.
- NumPy: Sectioned `Parameters`, `Returns`, `Examples` with underlines and indentation rules.

## Behavior Highlights

- Cleans and compacts descriptions; appends periods; extracts implicit defaults like “defaults to X”.
- Infers optionality/positionality from defaults and style semantics.
- Converts type strings via `string_to_type` and renders via `type_to_string`.
- Merges multiline parameter descriptions and maps multiple names like `a, b : int`.
- Captures exceptions as a dict `{ExceptionName: description}`.

## Usage

- `parse_docstring(docstring) -> DocstringParserResult`: unified entry point.
- Direct style functions can be used for testing/validation if needed.

