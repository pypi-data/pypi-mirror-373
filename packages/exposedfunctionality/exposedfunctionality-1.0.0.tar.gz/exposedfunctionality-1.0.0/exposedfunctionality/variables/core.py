import asyncio
import json

from ..function_parser.types import Optional, Dict, Union, Type, Any, List
from typing import Callable


nonetype = object()

OnChangeEvent = Callable[[Any, Any], None]


class ExposedValueData:
    def __init__(self, **kwargs) -> None:
        self._data = kwargs
        try:
            self.changeevent = asyncio.Event()
        except RuntimeError:
            # if we are not in an event loop, no event
            self.changeevent = None
        self._on_change_callbacks: List[OnChangeEvent] = []

    def add_on_change_callback(
        self,
        callback: OnChangeEvent,
    ):
        """Adds a callback to be called when the value changes

        Args:
            callback (Callable[[new_value:Any, old_value:Any], None]): Callback to be called when the value changes

        """

        self._on_change_callbacks.append(callback)

    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except AttributeError as exc:
            try:
                return self._data[__name]
            except KeyError:
                raise exc  # pylint: disable=raise-missing-from

    def call_on_change_callbacks(
        self,
        new_value: Any,
        old_value: Any,
    ) -> List[asyncio.Task]:
        tasks = []

        for callback in self._on_change_callbacks:
            if asyncio.iscoroutinefunction(callback):
                tasks.append(asyncio.create_task(callback(new_value, old_value)))
            else:
                callback(new_value, old_value)

        return tasks


ValueChecker = Callable[[Any, ExposedValueData], Any]
"""Type for value checkers that can be added to ExposedValue instances.
Value checkers are called when the value of an ExposedValue is set, and can be used to modify the value or raise an error.
The value checker should take two arguments: the new value and the ExposedValueData object, and return the new value.

"""


class ExposedValue:
    """
    Descriptor for type-safe attributes with default values.

    Attributes are exposed with a default value and can optionally enforce a specific type.
    This allows for safer attribute handling with type enforcement, and default value
    provisioning if the attribute has not been explicitly set.
    An additonal

    Attributes:
        name (str): Name of the attribute.
        default (Any): Default value for the attribute.
        type (Type): Expected type of the attribute.
        kwargs (Dict[str, Any]): Additional keyword arguments.
    """

    def __init__(
        self,
        name: str,
        default: Any = nonetype,
        type_: Optional[Type] = nonetype,
        valuechecker: Optional[List[ValueChecker]] = None,
        **kwargs,
    ):
        """
        Initialize an ExposedValue instance.

        Args:
            name (str): Name of the attribute.
            default (Any): Default value for the attribute.
            type_ (Optional[Type], optional): Expected type of the attribute.
                If not provided, the type of the default value is used. If None is provided, no type checking is performed.
            valuechecker (Optional[List[ValueChecker]], optional): List of value checkers to be called when the value is set.
                Can be used to modify the value or raise an error. Defaults to None.
            **kwargs: Additional keyword arguments, must be json serializable.
        """
        self.name = name
        if type_ is nonetype:
            type_ = type(default)
        self.type = type_
        if valuechecker is None:
            valuechecker = []
        self._valuechecker = valuechecker

        if self.type is not None and default is not nonetype:
            if not isinstance(default, self.type):
                # check if default can be converted to type without loss of information
                try:
                    if not default == type(default)(self.type(default)):
                        raise TypeError(
                            f"Can convert default value of type {type(default)} to {self.type}, and back again, "
                            "but not without loss of information."
                        )
                    default = self.type(default)
                except Exception as exc:
                    raise TypeError(
                        f"Expected default value of type {self.type}, got {type(default)}"
                    ) from exc

        self.default = default
        self._jskwargs = json.dumps(kwargs)
        self._dataname = f"_{self.name}__data"

    def get_object_data(self, instance: Any) -> ExposedValueData:
        """
        Get the ExposedValueData object associated with this ExposedValue instance.

        Args:
            instance (Any): The instance from which the attribute is accessed.

        Returns:
            ExposedValueData: The ExposedValueData object associated with this ExposedValue instance.
        """
        self._check_instance_var_initialized(instance)
        return instance.__dict__[self._dataname]

    def _check_instance_var_initialized(self, instance: Any) -> None:
        """
        Check if the instance variable has been initialized.
        If not, initialize it with the default value.

        Args:
            instance (Any): The instance to check.
        """
        if self._dataname not in instance.__dict__:
            if self.default is not nonetype:
                instance.__dict__[self.name] = self.default
            data: ExposedValueData = ExposedValueData(**json.loads(self._jskwargs))

            instance.__dict__[self._dataname] = data

    def __get__(self, instance: Any, owner: Type) -> Any:
        """
        Get the attribute value. If the attribute is not set, return the default value.
        If called on a class, return the ExposedValue instance itself.

        Args:
            instance (Any): The instance from which the attribute is accessed.
            owner (Type): Owner class.

        Returns:
            Any: Attribute value.
        """
        if instance is None:
            return self

        self._check_instance_var_initialized(instance)

        return instance.__dict__[self.name]

    def __set__(self, instance: Any, value: Any) -> None:
        """
        Set the attribute value.

        Args:
            instance (Any): The instance on which the attribute is set.
            value (Any): The value to set.

        Raises:
            TypeError: If the value type does not match the expected type.
        """
        dataobj: ExposedValueData = self.get_object_data(instance)
        self._check_instance_var_initialized(instance)
        for vc in self._valuechecker:
            value = vc(value, dataobj)
        if self.type is not None and not isinstance(value, self.type):
            try:
                value = self.type(value)
            except Exception as exc:
                raise TypeError(
                    f"Expected value of type {self.type}, got {type(value)}"
                ) from exc

        old_value = instance.__dict__.get(self.name, self.default)

        instance.__dict__[self.name] = value

        if dataobj.changeevent:
            dataobj.changeevent.set()
            dataobj.changeevent.clear()
        if old_value != nonetype:
            dataobj.call_on_change_callbacks(value, old_value)

    def __delete__(self, instance: Any) -> None:
        """
        Prevent deleting the attribute.

        Args:
            instance (Any): The instance from which the attribute is deleted.

        Raises:
            AttributeError: Always raised to prevent deletion.
        """
        raise AttributeError("Can't delete exposed attribute")

    def __repr__(self) -> str:
        return f"ExposedValue({self.name})"


def add_exposed_value(
    instance: Union[Any, Type], name: str, default: Any, type_: Type
) -> None:
    """
    Dynamically add an ExposedValue to an instance or class.
    Keep in mind that this will create a new class for the instance, so it is
    not possible to add ExposedValues to instances of built-in classes.
    If the instance is used to create other instances, the ExposedValues will be inherited.
    e.g.:
    >>> class A:
    ...     pass
    >>> a = A()
    >>> add_exposed_value(a, "attr", 10, int)
    >>> b = A()
    >>> b.attr
    AttributeError: 'A' object has no attribute 'attr'
    >>> b=a.__class__()
    >>> b.attr
    10
    >>> b.attr = 20
    >>> b.attr
    20
    >>> a.attr
    10
    >>> c = a.__class__()
    >>> c.attr
    10
    >>> add_exposed_value(c, "attr2", 20, int)
    >>> c.attr = 30
    >>> c.__dict__
    {'attr': 30, 'attr2': 20}
    >>> a.__dict__
    {'attr': 10}


    Args:
        instance (Union[Any, Type]): Instance or class to which the attribute is added.
        name (str): Name of the attribute.
        default (Any): Default value of the attribute.
        type_ (Type): Expected type of the attribute.

    Raises:
        AttributeError: If an attribute with the given name already exists.
    """
    if hasattr(instance, name):
        raise AttributeError(
            f"Instance {instance} already has an attribute with name {name}"
        )

    # if instance is a class, simply add the attribute
    if isinstance(instance, type):
        setattr(instance, name, ExposedValue(name, default, type_))
        return

    original_class = instance.__class__

    subclass = type(f"_{original_class.__name__}", (original_class,), {})

    for key, value in original_class.__dict__.items():
        if isinstance(value, ExposedValue):
            setattr(subclass, key, value)

    setattr(subclass, name, ExposedValue(name, default, type_))

    instance.__class__ = subclass

    # call get to set the default value
    getattr(instance, name)


def get_exposed_values(obj: Union[Any, Type]) -> Dict[str, ExposedValue]:
    """
    Get all ExposedValue attributes from an object (either instance or class).

    Args:
        obj (Union[Any, Type]): Object (instance or class) from which ExposedValues are fetched.

    Returns:
        Dict[str, ExposedValue]: Dictionary of attribute names to their ExposedValue instances.
    """
    source = obj if isinstance(obj, type) else obj.__class__
    return {
        attr_name: attr_value
        for attr_name, attr_value in vars(source).items()
        if isinstance(attr_value, ExposedValue)
    }
