# ExposedFunctionality — Overview

ExposedFunctionality provides lightweight primitives to expose Python functions and state to external callers (e.g., UIs, RPC layers) with structured metadata. It focuses on:

- Automatic function parsing (signature, types, docstrings) into a serializable schema.
- A simple decorator or helper to “expose” functions without changing their behavior.
- A descriptor for type‑safe, observable variables with optional middleware.
- Utilities for robust decorator wrapping/unwrapping and rich type serialization.

This documentation includes per‑file deep dives and overarching principles.

## Key Building Blocks

- `exposedfunctionality/func.py`: Expose functions and query exposed metadata.
- `exposedfunctionality/function_parser/*`: Parse signatures, docstrings, and types into a structured format.
- `exposedfunctionality/variables/*`: Expose state via descriptors with change events and middleware.
- `exposedfunctionality/function_parser/custom_wrapper.py`: Safer metadata‑preserving wrappers and unwrapping.

## Quick Start

- Decorate a function with `exposed_method()` (or call `expose_method(func, ...)`).
- Access `.ef_funcmeta` to read the serialized metadata (inputs, outputs, docstring).
- Use `get_exposed_methods(obj)` to list exposed methods on an instance or class.
- Define `ExposedValue` fields to expose and enforce typed state, with change notifications.

See per‑file docs in this folder for details.

