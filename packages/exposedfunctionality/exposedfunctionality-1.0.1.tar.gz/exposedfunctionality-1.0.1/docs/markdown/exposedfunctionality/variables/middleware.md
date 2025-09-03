# variables/middleware.py

Common middleware helpers for `ExposedValue` workflows.

## `min_max_clamp(value, valuedata, min=None, max=None)`

Clamps numeric `value` into the inclusive range `[min, max]`.

- If `min`/`max` are not provided, attempts to read them from `ExposedValueData` (e.g., `valuedata.min`, `valuedata.max`).
- Raises `ValueError` when `max < min`.
- Returns the clamped value; unchanged if already within bounds.

Useful as a `valuechecker` to enforce bounds on exposed numeric attributes.

