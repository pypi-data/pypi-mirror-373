# variables/core.py

Type‑safe, observable attributes via the `ExposedValue` descriptor and helpers.

## `ExposedValueData`

- Holds auxiliary data (`_data`), an optional `asyncio.Event` (`changeevent`), and registered `on_change` callbacks.
- `add_on_change_callback(callback)`: Registers sync/async callbacks.
- `call_on_change_callbacks(new_value, old_value) -> List[asyncio.Task]`: Invokes callbacks; async ones are scheduled.
- Transparent `.__getattribute__` fallback into `_data` for additional metadata (e.g., `min`, `max`).

## `ExposedValue`

Descriptor for attributes with:

- `name`, `default`, `type` (optional; inferred from default when not provided; `None` disables checking).
- `valuechecker`: Optional list of validators/normalizers: `Callable[[Any, ExposedValueData], Any]`.

Behavior:

- Get: On first access, if unset, installs default (coerced to `type` if compatible) and returns it.
- Set: Runs value checkers, enforces/coerces `type` when set, triggers `changeevent` and callbacks when value changes.
- Delete: Forbidden (`AttributeError`).

## Helpers

- `add_exposed_value(instance_or_cls, name, default, type_)`:
  - For classes: simply sets a new `ExposedValue` attribute.
  - For instances: creates a dynamic subclass copying existing `ExposedValue`s, assigns the new one, and rebinds the instance.
  - Initializes the default by accessing the attribute once.
- `get_exposed_values(obj) -> Dict[str, ExposedValue]`: Collects declared `ExposedValue` descriptors on a class/instance.

## Notes

- Defaults must match `type` or be safely convertible without information loss; otherwise a `TypeError` is raised.
- `changeevent` is only created when an event loop is present; absence is handled gracefully.

