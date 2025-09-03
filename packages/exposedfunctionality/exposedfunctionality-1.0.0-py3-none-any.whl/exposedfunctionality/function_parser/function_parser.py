from __future__ import annotations


import warnings
import inspect
from functools import partial
import json
from .docstring_parser import parse_docstring
from typing import get_type_hints, Callable, get_origin, get_args, Annotated
from .types import (
    type_to_string,
    Optional,
    Any,
    List,
    Tuple,
    NoneType,
    Dict,
)

from .ser_types import (
    FunctionInputParam,
    SerializedFunction,
    ReturnType,
    DocstringParserResult,
    InputMeta,
    OutputMeta,
)


def get_base_function(func: Callable) -> Callable:
    """
    Get the base function of a callable. If the callable is a functools.partial
    instance, it returns the base function.

    Parameters:
    - func: A callable whose base function needs to be obtained.

    Returns:
    - Callable: The base function of the callable.

    Examples:
    ```python
    from functools import partial

    def example(a, b, c=3, d=4):
        pass

    p = partial(example, 1, d=5)
    print(get_base_function(p))  # Returns: example
    ```
    """
    base_func = func
    preset_args = []
    preset_kwargs: Dict[str, Any] = {}
    if isinstance(base_func, partial):
        while isinstance(base_func, partial):
            preset_kwargs = {**base_func.keywords, **preset_kwargs}
            preset_args = list(base_func.args) + preset_args
            base_func = base_func.func
    return base_func, preset_args, preset_kwargs


def get_resolved_signature(
    func: Callable[..., ReturnType], class_member_attributes: Optional[List[str]] = None
) -> Tuple[inspect.Signature, Callable[..., ReturnType]]:
    """
    Get the resolved signature of a callable. If the callable is a functools.partial
    instance, it resolves the signature by excluding parameters that have already
    been set in the partial. Nested partials are also supported.

    Parameters:
    - func: A callable whose signature needs to be resolved.
    - class_member_attributes: A list of attributes that are considered class members
      and should be ignored when resolving the signature and occur as the first
      parameter in the signature. Defaults to ["self", "cls"].

    Returns:
    - Signature: The resolved signature of the callable.

    Examples:
    ```python
    from functools import partial

    def example(a, b, c=3, d=4):
        pass

    p = partial(example, 1, d=5)
    print(get_resolved_signature(p)[0])  # Returns: (b, c=3)
    ```

    """
    base_func, preset_args, preset_kwargs = get_base_function(func)
    if class_member_attributes is None:
        class_member_attributes = ["self", "cls"]

    # Resolve the base function and collect preset arguments
    # from any nested partials.

    # Obtain the original signature
    sig = inspect.signature(base_func, follow_wrapped=False)

    params = list(sig.parameters.values())

    # Remove the preset positional arguments from the front
    if preset_args:
        params = params[len(preset_args) :]

    # Remove the preset keyword arguments
    params = [p for p in params if p.name not in preset_kwargs]

    # Create a new signature
    new_sig = sig.replace(parameters=params)

    # in case its a class method, remove the first argument
    if inspect.ismethod(func) or inspect.isfunction(func):
        if len(list(new_sig.parameters.values())) > 0:
            if list(new_sig.parameters.values())[0].name in class_member_attributes:
                params = list(new_sig.parameters.values())[1:]
                new_sig = new_sig.replace(parameters=params)

    return new_sig, base_func


def function_method_parser(
    func: Callable,
) -> SerializedFunction:
    """
    Parses a given function or method and serializes its signature, type annotations,
    and docstring into a structured dictionary.

    Parameters:
    - func (Callable): The function or method to parse. If the callable is an instance of `functools.partial`,
                       the parser will resolve the signature excluding parameters that have
                       already been set in the partial.

    Returns:
    - SerializedFunction: A dictionary containing:
      * name (str): The name of the function or method.
      * input_params (list[FunctionInputParam]): A list of dictionaries, each representing an input parameter with:
        - name (str): Name of the parameter.
        - default (Any, optional): Default value of the parameter if specified. Omitted if no default is provided.
        - type (type): Type hint of the parameter. Defaults to `Any` if no type hint is provided.
        - positional (bool): True if the parameter is positional or can be passed as a keyword argument,
          otherwise False.
        - optional (bool, optional): True if the parameter is optional, otherwise False.
        - description (str, optional): Description of the parameter extracted from the function's
          docstring (if present).
      * output_params (list[FunctionOutputParam]): A list of dictionaries, each representing an
        output parameter (or return type) with:
        - name (str): Name of the output. It can be "out" or "outX" (where X is an index) depending on the return type.
        - type (type): Type hint of the output.
        - description (str, optional): Description of the output extracted from the function's docstring (if present).
      * docstring (str): The docstring of the function or method.

    Raises:
    - FunctionParamError: If an input parameter has an unserializable default value.

    Notes:
    - The function uses the `get_resolved_signature` to handle callables that are instances of `functools.partial`.
    - The parser assumes that the function or method follows standard Python conventions for naming and annotations.

    Examples:
    ```python
    def example_function(a: int, b: str = "default") -> Tuple[int, str]:
        '''This is an example function.'''
        return a, b

    result = function_method_parser(example_function)
    # The result would be a dictionary with the serialized structure of example_function.
    ```
    """
    input_params = []
    base_func, preset_args, preset_kwargs = get_base_function(func)
    docs = inspect.getdoc(base_func)
    parsed_ds: Optional[DocstringParserResult] = None
    if docs is not None:
        parsed_ds = parse_docstring(docs)

    # Collect annotated metadata containers so they exist across branches
    annotated_input_meta: Dict[str, Dict[str, Any]] = {}

    try:
        # include_extras=True keeps typing.Annotated metadata
        th = get_type_hints(base_func, include_extras=True)
    except TypeError as exe:
        th = {}
    try:
        sig, base_func = get_resolved_signature(func)

        def _extract_meta_from_annotation(annotation, *, is_input: bool):
            """Return (base_type, meta_dict) from possibly Annotated annotation."""
            origin = get_origin(annotation)
            if origin is Annotated:
                args = list(get_args(annotation))
                base = args[0]
                metas = args[1:]
                md: Dict[str, Any] = {}
                for m in metas:
                    # Supported: InputMeta/OutputMeta instances or plain dicts
                    if is_input and isinstance(m, InputMeta):
                        # full set of fields
                        if m.name is not None:
                            md["name"] = m.name
                        if m.type is not None:
                            md["type"] = m.type
                        if m.default is not None:
                            md["default"] = m.default
                        if m.optional is not None:
                            md["optional"] = m.optional
                        if m.positional is not None:
                            md["positional"] = m.positional
                        if m.description is not None:
                            md["description"] = m.description
                        if m.middleware is not None:
                            md["middleware"] = m.middleware
                        if m.endpoints is not None:
                            md["endpoints"] = m.endpoints
                    elif (not is_input) and isinstance(m, OutputMeta):
                        if m.name is not None:
                            md["name"] = m.name
                        if m.type is not None:
                            md["type"] = m.type
                        if m.description is not None:
                            md["description"] = m.description
                        if m.endpoints is not None:
                            md["endpoints"] = m.endpoints
                    elif isinstance(m, dict):
                        # Filter to allowed keys
                        keys = (
                            {
                                "name",
                                "type",
                                "default",
                                "optional",
                                "positional",
                                "description",
                                "middleware",
                                "endpoints",
                            }
                            if is_input
                            else {"name", "type", "description", "endpoints"}
                        )
                        for k in keys:
                            if k in m:
                                md[k] = m[k]
                return base, md
            return annotation, {}

        for i, p in sig.parameters.items():
            n = i
            if p.kind == p.VAR_POSITIONAL:
                n = "*" + n
            if p.kind == p.VAR_KEYWORD:
                n = "**" + n

            param_dict: FunctionInputParam = {
                "name": n,
                "default": p.default,
                "type": th[i] if i in th else p.empty,
                "positional": (
                    p.kind == p.POSITIONAL_ONLY
                    or p.kind == p.POSITIONAL_OR_KEYWORD
                    or p.kind == p.VAR_POSITIONAL
                )
                and (p.default == p.empty),
            }

            if param_dict["type"] is p.empty:
                module = None
                try:
                    module = base_func.__module__
                except Exception:
                    pass
                if module is not None:
                    funcdesc = f"{module}.{base_func.__name__}"
                else:
                    funcdesc = f"{base_func.__name__}"
                warnings.warn(
                    f"input {i} of {funcdesc} has no type type, using Any as type",
                )
                param_dict["type"] = Any

            # Extract Annotated metadata for inputs before serializing type
            if param_dict["type"] is not p.empty:
                base_type, meta = _extract_meta_from_annotation(
                    param_dict["type"], is_input=True
                )
                param_dict["type"] = base_type
                # collect all meta for later final application
                if meta:
                    annotated_input_meta[n] = meta

            if param_dict["default"] is not p.empty:
                try:
                    json.dumps(param_dict["default"])
                except TypeError as exe:
                    try:
                        param_dict["default"] = param_dict["default"].__name__
                    except AttributeError:
                        param_dict["default"] = str(param_dict["default"])
                        # raise FunctionParamError(
                        #     f"input {i} has unserializable default value '{param_dict['default']}'"
                        # ) from exe
            else:
                del param_dict["default"]

            param_dict["type"] = type_to_string(param_dict["type"])

            input_params.append(param_dict)
    except ValueError as exe:
        if parsed_ds is not None:
            input_params = parsed_ds["input_params"]

    output_params = []
    annotated_return_meta: Dict[str, Any] = {}
    annotated_return_tuple_meta: List[Dict[str, Any]] = []
    if "return" in th:
        # Extract Annotated metadata for outputs
        rtype, rmeta = (lambda ann: _extract_meta_from_annotation(ann, is_input=False))(
            th["return"]
        )
        if rmeta:
            annotated_return_meta = rmeta
        # chek if return type is None Type
        if rtype == NoneType:
            output_params = []
        elif getattr(rtype, "__origin__", None) is tuple:
            output_params = []
            annotated_return_tuple_meta = []
            for i, t in enumerate(get_args(rtype)):
                _bt, _m = _extract_meta_from_annotation(t, is_input=False)
                output_params.append({"name": f"out{i}", "type": type_to_string(_bt)})
                annotated_return_tuple_meta.append(_m)

        else:
            output_params = [{"name": "out", "type": type_to_string(rtype)}]
            # single return meta will be applied later

    if parsed_ds is not None:
        # update input params
        for p in input_params:
            for parsed_ip in parsed_ds["input_params"]:
                if p["name"] != parsed_ip["name"]:
                    continue

                if ("description" not in p) and "description" in parsed_ip:
                    p["description"] = parsed_ip["description"]
                # optinoanl should be set by the parser
                # if ("optional" not in p) and "optional" in parsed_ip:
                #     p["optional"] = parsed_ip["optional"]

                if (
                    ("default" not in p)
                    and "default" in parsed_ip
                    and p.get("optional", False)
                ):
                    p["default"] = parsed_ip["default"]

                if (
                    "type" not in p
                    or p["type"] is None
                    or p["type"] == "Any"
                    or p["type"] is Any
                ) and "type" in parsed_ip:
                    p["type"] = parsed_ip["type"]

                # Infer optional/positional unless explicitly provided via Annotated
                if "optional" not in p:
                    if annotated_input_meta.get(p["name"], {}).get("optional") is None:
                        p["optional"] = "default" in p
                if "positional" not in p:
                    if (
                        annotated_input_meta.get(p["name"], {}).get("positional")
                        is None
                    ):
                        p["positional"] = not ("default" in p)
                # possitional is always set
                # if (
                #    "positional" not in p or p["positional"] is None
                # ) and "positional" in parsed_ip:
                #    p["positional"] = parsed_ip["positional"]

                break

        # update output params
        if len(output_params) == 0:
            output_params.extend(parsed_ds["output_params"])
        if len(output_params) == 1 and len(parsed_ds["output_params"]) >= 1:
            output_params[0] = {**parsed_ds["output_params"][0], **output_params[0]}
        if len(output_params) > 1:
            for i, p in enumerate(output_params):
                for _dp in parsed_ds["output_params"]:
                    if p["name"] == _dp["name"] or (
                        p["name"] == "out0" and _dp["name"] == "out"
                    ):
                        output_params[i] = {**_dp, **output_params[i]}

    # Final application of Annotated metadata (highest precedence)
    def _apply_meta_to_input(p: Dict[str, Any], meta: Dict[str, Any]):
        # type override
        if "type" in meta:
            p["type"] = (
                type_to_string(meta["type"]) if meta["type"] is not None else p["type"]
            )
        # default handling like earlier (serialize if needed)
        if "default" in meta:
            dv = meta["default"]
            try:
                json.dumps(dv)
            except TypeError:
                try:
                    dv = dv.__name__  # type: ignore[attr-defined]
                except AttributeError:
                    dv = str(dv)
            p["default"] = dv
        # simple assignments
        for k in ("optional", "positional", "description", "middleware", "endpoints"):
            if k in meta:
                p[k] = meta[k]
        # rename last to avoid affecting lookups
        if "name" in meta and meta["name"] and meta["name"] != p.get("name"):
            p["_name"] = p["name"]
            p["name"] = meta["name"]

    for p in input_params:
        if p["name"] in annotated_input_meta:
            _apply_meta_to_input(p, annotated_input_meta[p["name"]])

    def _apply_meta_to_output(p: Dict[str, Any], meta: Dict[str, Any]):
        if not meta:
            return
        if "type" in meta and meta["type"] is not None:
            p["type"] = (
                type_to_string(meta["type"]) if meta["type"] is not None else p["type"]
            )
        for k in ("description", "endpoints"):
            if k in meta:
                p[k] = meta[k]
        if "name" in meta and meta["name"] and meta["name"] != p.get("name"):
            p["_name"] = p["name"]
            p["name"] = meta["name"]

    if output_params:
        if len(output_params) == 1:
            _apply_meta_to_output(output_params[0], annotated_return_meta)
        elif len(output_params) > 1 and annotated_return_tuple_meta:
            for i, m in enumerate(annotated_return_tuple_meta):
                if i < len(output_params):
                    _apply_meta_to_output(output_params[i], m)

    ser: SerializedFunction = {
        "name": base_func.__name__,
        "input_params": input_params,
        "output_params": output_params,
        "docstring": parsed_ds,
    }
    return ser
