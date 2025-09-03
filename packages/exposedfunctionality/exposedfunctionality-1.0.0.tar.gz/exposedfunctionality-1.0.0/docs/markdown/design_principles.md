# Design Principles

- Minimal intrusion: Do not alter runtime behavior of user functions; attach metadata and flags only.
- Explicit over implicit: Users can override inferred metadata via `exposed_method(name=..., inputs=..., outputs=...)`.
- Progressive enhancement: Use annotations and docstrings if present; gracefully fall back to `Any` and empty docs.
- Serialization‑ready: Emit JSON‑friendly `SerializedFunction` with stringified types and serializable defaults.
- Safe wrapping: Preserve original metadata and prevent wrapper loops with controlled update/unwrap utilities.
- Extensible typing: Allow new type names and custom mappings via `add_type`, and robustly stringify complex `typing` constructs.
- Observable state: Exposed variables emit change events and support middleware for validation/normalization.

