# function_parser/types.py

Stringification and resolution for Python/typing types, plus safe casting.

## Core APIs

- `add_type(type_: type, name: str) -> type`: Registers a custom type mapping both ways.
- `string_to_type(string: str) -> type`: Resolves names like `List[int]`, `Union[str, int]`, or fully‑qualified `module.Type`.
- `type_to_string(t: Union[type, str]) -> str`: Produces stable string names for builtins, generics, and registered types.
- `cast_to_type(value: Any, type_) -> Any`: Best‑effort cast including `Union`/`Optional` handling.
- `split_type_string(string: str) -> List[str]`: Splits comma‑separated type strings respecting nested brackets.

## Features

- Built‑ins and aliases are pre‑registered (e.g., `int`, `integer`, `number`).
- Supports `typing` generics: `List[T]`, `Dict[K, V]`, `Tuple[...]`, `Union[...]`, `Literal[...]`, `Set[T]`, `Sequence[T]`, `Type[T]`.
- Imports for fully‑qualified names are validated and cached; unresolved names raise `TypeNotFoundError`.
- Optional detection: treats strings containing `optional` as `Optional[...]`.

## Notes

- `type_to_string` may register new computed names for generics to preserve round‑tripability.
- `cast_to_type` tries all branches for `Union`, returns `None` for empty `Optional`, or re‑raises combined errors.

