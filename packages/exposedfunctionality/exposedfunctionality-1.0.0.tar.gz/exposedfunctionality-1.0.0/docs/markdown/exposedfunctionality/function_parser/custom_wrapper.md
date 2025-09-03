# function_parser/custom_wrapper.py

Metadata‑preserving wrapping utilities for decorators and safe unwrapping.

## `update_wrapper(...) -> Callable`

Customizable alternative to `functools.update_wrapper` with fine‑grained control over which attributes to copy or merge:

- Controls: name, qualname, module, docstring, annotations, dict, and arbitrary attributes.
- Strategies: update if missing/empty, never update, always update, merge dicts.
- Special handling for `__dict__` and support for custom wrapper attribute names (default `"__wrapped__"`).

Useful when building decorators that must retain important metadata while avoiding overwrites.

## `controlled_wrapper(...) -> decorator`

Returns a decorator preconfigured with `update_wrapper` options, making it easy to define wrappers that inherit selected metadata from the wrapped function.

## `controlled_unwrap(func, return_memo=False, wrapper_attribute='__wrapped__', stop=None)`

Safely unwraps decorator chains:

- Returns the original function or `(func, memo)` when `return_memo=True`.
- Detects wrapper loops and raises `ValueError`.
- Respects a `stop` predicate to halt unwrapping at specific layers.

## Notes

- Helps avoid metadata loss that can break signature or docstring parsing downstream.
- Integrates with `function_parser` expectations around `follow_wrapped=False` when inspecting.

