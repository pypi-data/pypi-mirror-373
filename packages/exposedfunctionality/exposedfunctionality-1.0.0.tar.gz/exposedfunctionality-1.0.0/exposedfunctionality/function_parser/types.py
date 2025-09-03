from __future__ import annotations
from enum import Enum
import importlib
import re
import ast
from typing import (
    Union,
    Type,
    Tuple,
    Set,
    Optional,
    Dict,
    Any,
    List,
    Literal,
    Sequence,
    get_origin,
    get_args,
)

try:  # Python 3.10+
    from types import UnionType as PyUnionType  # type: ignore
except Exception:  # pragma: no cover - older Python
    PyUnionType = None  # type: ignore
import collections
from .ser_types import TypeNotFoundError

from typing_extensions import TypedDict


try:
    from typing import NoneType  # type: ignore # pylint: disable=unused-import
except ImportError:
    NoneType = type(None)


ALLOWED_BUILTINS = {
    "int": int,
    "float": float,
    "str": str,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "bool": bool,
    "bytes": bytes,
    "bytearray": bytearray,
    "complex": complex,
    "frozenset": frozenset,
    "memoryview": memoryview,
    "range": range,
    "slice": slice,
    "type": type,
    "Any": Any,
    "Optional": Optional,
    "Union": Union,
    "Type": Type,
    "List": list,
    "Sequence": Sequence,
    "Dict": dict,
    "Tuple": tuple,
    "Literal": Literal,
    "Set": set,
    "None": type(None),
}


_TYPE_GETTER: Dict[str, type] = {}
_STRING_GETTER: Dict[type, str] = {}


def add_type(type_: type, name: str):
    """
    Add a type to the list of allowed types.

    Parameters:
    - type_: The type to add.
    - name: The name of the type.

    Raises:
    - ValueError if the type is already in the list.
    """
    if name not in _TYPE_GETTER:
        _TYPE_GETTER[name] = type_

    if type_ not in _STRING_GETTER:
        _STRING_GETTER[type_] = name

    return _TYPE_GETTER[name]


for k, v in ALLOWED_BUILTINS.items():
    add_type(v, k)

for k, v in {
    "integer": int,
    "floating": float,
    "string": str,
    "boolean": bool,
    "number": Union[int, float],
}.items():
    add_type(v, k)


def split_type_string(string: str):
    """splits a comma seperated type string into its parts, while reserving nested types
    e.g. "int, str" -> ["int", "str"]
    e.g. "List[int], str" -> ["List[int]", "str"]
    eg. "int, union[str, int]" -> ["int", "Union[str, int]"]
    """
    parts = []
    level = 0
    current = ""
    for c in string:
        if c == "," and level == 0:
            parts.append(current)
            current = ""
        else:
            if c == "[":
                level += 1
            elif c == "]":
                level -= 1
            current += c
    parts.append(current)
    return parts


def string_to_type(
    string: str,
) -> type:
    """
    Convert a string to a class object.

    Parameters:
    - string: The full name of the class, including its module path, if any.

    Returns:
    - The class object.

    Raises:
    - TypeNotFoundError if the class is not found.
    - ImportError if there's a problem importing the module.
    """

    if isinstance(string, type) or (
        hasattr(string, "__origin__") and not isinstance(string, str)
    ):
        return string

    if not isinstance(string, str):
        raise TypeError(f"Expected str, got {type(string)}")

    string = string.strip().strip(".,").strip()

    # Helper function to handle parameterized types

    def handle_param_type(main_type: str, content: str):
        if main_type == "List":
            return List[string_to_type(content)]
        elif main_type == "Sequence":
            return Sequence[string_to_type(content)]
        elif main_type == "Dict":
            key, value = map(str.strip, split_type_string(content))
            return Dict[string_to_type(key), string_to_type(value)]
        elif main_type == "Tuple":
            items = tuple(map(string_to_type, split_type_string(content)))
            return Tuple[items]
        elif main_type == "Union":
            subtypes = tuple(map(string_to_type, split_type_string(content)))
            if len(subtypes) >= 2:
                return Union[subtypes]  # type: ignore # mypy doesn't like the splat operator
            else:
                return subtypes[0]
        elif main_type == "Optional":
            return Optional[string_to_type(content)]
        elif main_type == "Type":
            return Type[string_to_type(content)]
        elif main_type == "Set":
            return Set[string_to_type(content)]
        elif main_type == "Literal":
            items = [item.strip() for item in split_type_string(content)]
            items = [item for item in items if item]
            items = tuple([ast.literal_eval(item.strip()) for item in items])
            return Literal[items]  # type: ignore # mypy doesn't like the splat operator
        else:
            raise TypeNotFoundError(string)

    # Check if the string is a parameterized type (like List[int] or Dict[str, int])
    match = re.match(r"(\w+)\[(.*)\]$", string)
    if match:
        main_type, content = match.groups()
        _type = handle_param_type(main_type, content)
        backstring = type_to_string(_type)
        try:
            add_type(
                _type, backstring
            )  # since the backstring should be prioritized add it first
        except ValueError:
            pass
        try:
            add_type(_type, string)
        except ValueError:
            pass
        return _type

    exc = None
    if "." in string:
        # Split the module path from the class name
        module_name, class_name = string.rsplit(".", 1)

        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                cls = getattr(module, class_name)
                try:
                    add_type(cls, string)
                except ValueError:
                    pass
                return cls
        except ImportError as _exc:
            exc = _exc

    if string in _TYPE_GETTER:
        return _TYPE_GETTER[string]

    if "optional" in string.lower():
        string = string.replace("optional", "")
        string = string.replace("Optional", "")
        return Optional[string_to_type(string.strip())]

    if exc:
        raise TypeNotFoundError(string) from exc
    else:
        raise TypeNotFoundError(string)


def type_to_string(t: Union[type, str]):
    """
    Convert a class object to a string.

    Parameters:
    - t: The class object.

    Returns:
    - The full name of the class, including its module path, if any.
    """
    if isinstance(t, str):
        return t

    def get_by_typing(t):
        # Prefer typing.get_origin to support PEP 604 unions and PEP 585 generics
        origin = get_origin(t)
        if origin is None:
            origin = getattr(t, "__origin__", None)
        if origin:
            # Optional[T] is just Union[T, None] in disguise; handled via Union
            if origin in [list, List]:
                return f"List[{type_to_string(get_args(t)[0])}]"
            if origin in [Sequence, collections.abc.Sequence]:
                return f"Sequence[{type_to_string(get_args(t)[0])}]"
            elif origin in [dict, Dict]:
                args = get_args(t)
                key_type = type_to_string(args[0])
                value_type = type_to_string(args[1])
                return f"Dict[{key_type}, {value_type}]"
            elif origin in [tuple, Tuple]:
                return f"Tuple[{', '.join([type_to_string(subtype) for subtype in get_args(t)])}]"
            elif (origin is Union) or (
                PyUnionType is not None and origin is PyUnionType
            ):
                return f"Union[{', '.join([type_to_string(subtype) for subtype in get_args(t)])}]"
            elif origin in [Type, type]:
                args = get_args(t)
                if args:
                    return f"Type[{type_to_string(args[0])}]"
                # else: already handled by the simple "Type" entry
            elif origin in [set, Set]:
                return f"Set[{type_to_string(get_args(t)[0])}]"
            elif origin is Literal:
                return f"Literal[{str(tuple(get_args(t)))[1:-1]}]"

    #                return f"Literal[{', '.join(str(lit) for lit in t.__args__)}]"

    ans = get_by_typing(t)
    if ans is not None:
        try:
            add_type(t, ans)
        except ValueError:
            pass
        return ans

    if t in _STRING_GETTER:
        return _STRING_GETTER[t]
        # Handle common typing types

    if hasattr(t, "__name__") and hasattr(t, "__module__"):
        name = t.__name__
        module = t.__module__
        # check if name can be imported from module
        try:
            module_obj = importlib.import_module(module)
            if hasattr(module_obj, name):
                ans = f"{module}.{name}"
                try:
                    _t = add_type(t, ans)
                    return type_to_string(_t)
                except ValueError:
                    pass
                return ans
        except ImportError:
            pass

    raise TypeNotFoundError(t)


def cast_to_type(value: Any, type_):
    try:
        return type_(value)
    except Exception:
        pass

    origin = get_origin(type_)

    ex = []
    if origin:
        args = get_args(type_)
        if origin is Union:
            for subtype in args:
                try:
                    return cast_to_type(value, subtype)
                except Exception as e:
                    ex.append(e)
        if origin is Optional:
            if value in (None, "", "None", "none"):
                return None
            else:
                return cast_to_type(value, args[0])

    ex.append(ValueError(f"Could not cast {value} to type {type_}"))

    # raise all ex from each other
    e = ex[-1]
    for _e in reversed(ex[:-1]):
        try:
            raise e from _e
        except Exception as ne:
            e = ne
    raise e


class AllOf(TypedDict):
    allOf: List[SerializedType]


class AnyOf(TypedDict):
    anyOf: List[SerializedType]


class ArrayOf(TypedDict):
    type: Literal["array"]
    items: SerializedType
    uniqueItems: bool


class DictOf(TypedDict):
    type: Literal["object"]
    keys: SerializedType
    values: SerializedType


class EnumOf(TypedDict):
    type: Literal["enum"]
    values: List[Union[int, float, str, bool, None]]
    keys: List[str]
    nullable: bool


class TypeOf(TypedDict):
    type: Literal["type"]
    value: SerializedType


SerializedType = Union[str, AllOf, AnyOf, ArrayOf, DictOf, EnumOf, TypeOf]


def serialize_type(type_: type) -> SerializedType:
    origin = get_origin(type_)
    args = get_args(type_)

    if origin is Union:
        hasNone = False
        if None in args or NoneType in args:
            hasNone = True
            args = [arg for arg in args if arg is not None and arg is not NoneType]

        subtypes = [serialize_type(subtype) for subtype in args]

        if hasNone:
            for st in subtypes:
                # make enums nullable
                if isinstance(st, dict) and "type" in st:
                    if st["type"] == "enum":
                        st["nullable"] = True
                        if len(subtypes) == 1:
                            return st

            nonestr = type_to_string(NoneType)
            if nonestr not in subtypes:
                subtypes.append(nonestr)
        if len(subtypes) == 1:
            return subtypes[0]
        seen = set()
        seen_add = seen.add
        return AnyOf(
            anyOf=[x for x in subtypes if not (str(x) in seen or seen_add(str(x)))]
        )

    elif origin is Optional:
        return serialize_type(Union[args + (None,)])
    elif origin in [tuple, Tuple]:
        return AllOf(
            allOf=[serialize_type(subtype) for subtype in args],
        )

    elif origin in [List, list, Sequence, collections.abc.Sequence]:
        return ArrayOf(
            type="array",
            uniqueItems=False,
            items=serialize_type(args[0]),
        )
    elif origin in [Dict, dict]:
        return DictOf(
            type="object",
            keys=serialize_type(args[0]),
            values=serialize_type(args[1]),
        )
    elif origin is Literal:
        typestrings = [item for item in args]
        nullable = False
        if None in typestrings:
            typestrings.remove(None)
            nullable = True
        return EnumOf(
            type="enum",
            values=typestrings,
            keys=[str(item) for item in typestrings],
            nullable=nullable,
        )

    elif origin in [Set, set]:
        return ArrayOf(
            type="array",
            uniqueItems=True,
            items=serialize_type(args[0]),
        )
    elif origin in [Type, type]:
        return TypeOf(
            type="type",
            value=serialize_type(args[0] if args else Any),
        )

    if (isinstance(type_, type) and issubclass(type_, Enum)) or isinstance(type_, Enum):
        return EnumOf(
            type="enum",
            values=[member.value for member in type_],
            keys=[member.name for member in type_],
            nullable=False,
        )

    return type_to_string(type_)
