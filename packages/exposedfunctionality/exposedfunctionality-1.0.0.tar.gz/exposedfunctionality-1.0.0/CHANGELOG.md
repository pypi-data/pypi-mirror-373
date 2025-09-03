# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2025-09-02

- Added Annotated metadata for full input/output serialization.
  - New `InputMeta` and `OutputMeta` classes.
  - All input fields configurable via annotation: `name`, `type`, `default`, `optional`, `positional`, `description`, `middleware`, `endpoints`.
  - All output fields configurable via annotation: `name`, `type`, `description`, `endpoints`.
  - Per-element tuple return metadata supported.
  - Annotated values merge with docstrings; Annotated has highest precedence.
  - Non-intrusive: call semantics (defaults, positionality) unchanged unless explicitly overridden in serialization via metadata.
- Documentation updated with examples in `docs/markdown/exposedfunctionality/function_parser/ser_types.md`.
- Tests added in `tests/test_annotated_metadata.py`.

