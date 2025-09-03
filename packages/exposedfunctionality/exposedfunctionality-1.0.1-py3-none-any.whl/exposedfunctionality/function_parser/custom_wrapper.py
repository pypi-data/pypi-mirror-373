from functools import partial
import sys
from typing import Callable, Sequence, Optional, Any, Set, Dict


def update_wrapper(
    wrapper: Callable[..., Any],
    wrapped: Callable[..., Any],
    update_name: bool = True,
    update_qualname: bool = True,
    update_module: bool = True,
    update_docstring: bool = True,
    update_annotations: bool = True,
    update_dict: bool = True,
    update_if_missing: Sequence[str] = (),
    update_if_empty: Sequence[str] = (),
    never_update: Sequence[str] = (),
    update_always: Sequence[str] = (),
    update_dicts: bool = True,
    wrapper_attribute: str = "__wrapped__",
) -> Callable[..., Any]:
    """
    Update a wrapper function to look more like the wrapped function.

    This function allows customization of which attributes from the wrapped function
    should be copied to the wrapper function. This can be useful when creating decorators
    that should retain certain metadata from the original function, like its name, module,
    or docstring.

    Parameters:
        wrapper (Callable): The function that wraps another function.
        wrapped (Callable): The original function being wrapped.
        update_name (bool): Whether to update the wrapper's `__name__` attribute. Default is True.
        update_qualname (bool): Whether to update the wrapper's `__qualname__` attribute. Default is True.
        update_module (bool): Whether to update the wrapper's `__module__` attribute. Default is True.
        update_docstring (bool): Whether to update the wrapper's `__doc__` attribute. Default is True.
        update_annotations (bool): Whether to update the wrapper's `__annotations__` attribute. Default is True.
        update_dict (bool): Whether to update the wrapper's `__dict__` attribute. Default is True.
        update_if_missing (Sequence[str]): Attributes to update if missing in the wrapper.
        update_if_empty (Sequence[str]): Attributes to update if empty in the wrapper.
        never_update (Sequence[str]): Attributes that should never be updated.
        update_always (Sequence[str]): Attributes that should always be updated.
        update_dicts (bool): Whether to update dictionary attributes instead of overwriting them. Default is True.
        wrapper_attribute (str): The attribute name to use for storing the wrapped function. Default is "__wrapped__".

    Returns:
        Callable: The wrapper function with updated attributes.
    """

    special_handling: Set[str] = {"__dict__"}

    update_if_missing_set: Set[str] = set(update_if_missing)
    update_if_empty_set: Set[str] = set(update_if_empty)
    never_update_set: Set[str] = set(never_update)
    update_always_set: Set[str] = set(update_always)

    # Define the standard attributes and their corresponding flags
    standard_attributes = [
        ("__name__", update_name),
        ("__qualname__", update_qualname),
        ("__module__", update_module),
        ("__doc__", update_docstring),
        ("__annotations__", update_annotations),
    ]

    for attr, flag in standard_attributes:
        if flag and getattr(wrapped, attr, None):
            update_always_set.add(attr)
        else:
            update_if_missing_set.add(attr)

    # Handle __dict__ separately based on update_dict flag
    if update_dict:
        update_always_set.add("__dict__")
    else:
        update_if_missing_set.add("__dict__")

    # Update never_update_set with wrapper_attribute and "__wrapped__"
    never_update_set.update({wrapper_attribute, "__wrapped__"})

    # Exclude never_update from update_if_empty and update_if_missing
    update_if_empty_set -= never_update_set
    update_if_missing_set = (
        update_if_missing_set - never_update_set
    ) | update_if_empty_set
    update_always_set -= never_update_set

    # Update attributes missing in the wrapper
    for attr in update_if_missing_set:
        if not hasattr(wrapper, attr):
            _try_update_attribute(wrapper, wrapped, attr)
        else:
            never_update_set.add(attr)

    # Update attributes empty in the wrapper
    for attr in update_if_empty_set:
        wvalue = getattr(wrapper, attr, None)
        if not wvalue and wvalue is not False and wvalue != 0:
            _try_update_attribute(wrapper, wrapped, attr)
        else:
            never_update_set.add(attr)

    # Always update specified attributes, excluding special handling
    for attr in update_always_set - special_handling:
        _try_update_or_merge_dict(wrapper, wrapped, attr, update_dicts)
        never_update_set.add(attr)

    # Special handling for __dict__
    if "__dict__" in update_always_set:
        _update_dict_special(wrapper, wrapped, never_update_set)

    # Associate the wrapped function with the wrapper function
    setattr(wrapper, wrapper_attribute, wrapped)
    return wrapper


def _try_update_attribute(
    wrapper: Callable[..., Any], wrapped: Callable[..., Any], attr: str
) -> None:
    """
    Attempt to update a single attribute from wrapped to wrapper.

    Parameters:
        wrapper (Callable): The function that wraps another function.
        wrapped (Callable): The original function being wrapped.
        attr (str): The name of the attribute to update.

    Returns:
        None
    """
    try:
        value = getattr(wrapped, attr)
        setattr(wrapper, attr, value)
    except AttributeError:
        pass


def _try_update_or_merge_dict(
    wrapper: Callable[..., Any],
    wrapped: Callable[..., Any],
    attr: str,
    update_dicts: bool,
) -> None:
    """
    Update or merge dictionaries if specified.

    If `update_dicts` is True, dictionary attributes will be merged instead of replaced.

    Parameters:
        wrapper (Callable): The function that wraps another function.
        wrapped (Callable): The original function being wrapped.
        attr (str): The name of the dictionary attribute to update.
        update_dicts (bool): Whether to merge dictionary attributes.

    Returns:
        None
    """
    try:
        value = getattr(wrapped, attr)
        if update_dicts and hasattr(wrapper, attr) and isinstance(value, dict):
            getattr(wrapper, attr).update(value)
        else:
            setattr(wrapper, attr, value)
    except AttributeError:
        pass


def _update_dict_special(
    wrapper: Callable[..., Any], wrapped: Callable[..., Any], never_update_set: Set[str]
) -> None:
    """
    Special handling for updating the `__dict__` attribute.

    This function updates the `__dict__` of the wrapper with entries from the
    wrapped function, excluding those that should never be updated.

    Parameters:
        wrapper (Callable): The function that wraps another function.
        wrapped (Callable): The original function being wrapped.
        never_update_set (Set[str]): Set of attributes that should not be updated.

    Returns:
        None
    """
    try:
        wrapped_dict = getattr(wrapped, "__dict__")
        filtered_dict = {
            k: v for k, v in wrapped_dict.items() if k not in never_update_set
        }
        wrapper_dict = getattr(wrapper, "__dict__")
        if isinstance(wrapper_dict, dict):
            wrapper_dict.update(filtered_dict)
    except AttributeError:
        pass


def controlled_wrapper(
    wrapped: Callable[..., Any],
    update_name: bool = True,
    update_qualname: bool = True,
    update_module: bool = True,
    update_docstring: bool = True,
    update_annotations: bool = True,
    update_dict: bool = True,
    update_if_missing: Sequence[str] = (),
    update_if_empty: Sequence[str] = (),
    never_update: Sequence[str] = (),
    update_always: Sequence[str] = (),
    update_dicts: bool = True,
    wrapper_attribute: str = "__wrapped__",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Returns a decorator that updates a wrapper function to look more like the wrapped function.

    This function returns a partial application of `update_wrapper`, allowing you to customize
    the behavior of a decorator in terms of which attributes of the wrapped function should be
    propagated to the wrapper function.

    Parameters:
        wrapped (Callable): The original function being wrapped.
        update_name (bool): Whether to update the wrapper's `__name__` attribute. Default is True.
        update_qualname (bool): Whether to update the wrapper's `__qualname__` attribute. Default is True.
        update_module (bool): Whether to update the wrapper's `__module__` attribute. Default is True.
        update_docstring (bool): Whether to update the wrapper's `__doc__` attribute. Default is True.
        update_annotations (bool): Whether to update the wrapper's `__annotations__` attribute. Default is True.
        update_dict (bool): Whether to update the wrapper's `__dict__` attribute. Default is True.
        update_if_missing (Sequence[str]): Attributes to update if missing in the wrapper.
        update_if_empty (Sequence[str]): Attributes to update if empty in the wrapper.
        never_update (Sequence[str]): Attributes that should never be updated.
        update_always (Sequence[str]): Attributes that should always be updated.
        update_dicts (bool): Whether to merge dictionary attributes instead of overwriting them. Default is True.
        wrapper_attribute (str): The attribute name to use for storing the wrapped function. Default is "__wrapped__".

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: A decorator that can be used to wrap functions.
    """
    return partial(
        update_wrapper,
        wrapped=wrapped,
        update_name=update_name,
        update_qualname=update_qualname,
        update_module=update_module,
        update_docstring=update_docstring,
        update_annotations=update_annotations,
        update_dict=update_dict,
        update_if_missing=update_if_missing,
        update_if_empty=update_if_empty,
        never_update=never_update,
        update_always=update_always,
        update_dicts=update_dicts,
        wrapper_attribute=wrapper_attribute,
    )


def controlled_unwrap(
    func: Callable[..., Any],
    *,
    return_memo: bool = False,
    wrapper_attribute: str = "__wrapped__",
    stop: Optional[Callable[[Callable[..., Any]], bool]] = None,
) -> Any:
    """
    Unwrap a function wrapping chain, optionally stopping at a given condition.

    This function traverses the chain of wrapped functions (created by decorators) to retrieve
    the original function. You can also stop the unwrapping process based on a condition provided
    via the `stop` parameter.

    Parameters:
        func (Callable): The function to unwrap.
        return_memo (bool): Whether to return the memo dictionary along with the unwrapped function.
                            The memo dictionary maps function IDs to their respective functions in the wrapping chain.
                            Default is False.
        wrapper_attribute (str): The attribute name used to store the wrapped function. Default is "__wrapped__".
        stop (Optional[Callable[[Callable[..., Any]], bool]]): A callable that takes a function and returns True if
                                                               unwrapping should stop at that function. Default is None.

    Returns:
        Any: The unwrapped function, or a tuple of the unwrapped function and the memo dictionary if `return_memo` is True.

    Raises:
        ValueError: If a wrapper loop is detected (i.e., a function is found more than once in the chain).
    """

    def _is_wrapper(f: Callable[..., Any]) -> bool:
        return hasattr(f, wrapper_attribute) and (stop is None or not stop(f))

    memo: Dict[int, Callable[..., Any]] = {id(func): func}
    recursion_limit = sys.getrecursionlimit()
    original_func = func

    while _is_wrapper(func):
        func = getattr(func, wrapper_attribute)
        if id(func) in memo or len(memo) >= recursion_limit:
            raise ValueError(f"wrapper loop when unwrapping {original_func!r}")
        memo[id(func)] = func

    if return_memo:
        return func, memo
    return func
