import sys
from collections.abc import Callable
from decimal import Decimal
from importlib import import_module
from inspect import Parameter
from inspect import signature
from json import JSONEncoder
from typing import TypeVar

try:
    from typing import Self
except ImportError:
    from typing import Self

ZERO = Decimal(0)
DOT01 = Decimal("0.01")
DOT001 = Decimal("0.001")
DOT0001 = Decimal("0.0001")
ONE00 = Decimal("100.0")


def validate_no_required_arguments(func):
    if isinstance(func, staticmethod):
        func = func.__func__
    required = [param for param in signature(func).parameters.values() if param.default is Parameter.empty]
    if required:
        raise TypeError(f"{func} cannot have mandatory arguments: {required}")


RETURN_VALUE = TypeVar("RETURN_VALUE")


def singleton_memoize[RETURN_VALUE](func: Callable[[], RETURN_VALUE]) -> RETURN_VALUE:
    validate_no_required_arguments(func)

    unset = object()

    class Singleton:
        value = unset

        def __get__(self, instance, owner):
            return self

        def __call__(self):
            if self.value is unset:
                value = self.value = func()
            else:
                value = self.value
            return value

    return Singleton()


def cached_import(module_path, class_name, package):
    # Check whether module is loaded and fully initialized.
    spec = None
    if not (
        (module := sys.modules.get(module_path))
        and (spec := getattr(module, "__spec__", None))
        and getattr(spec, "_initializing", False) is False
    ):
        module = import_module(module_path, package)
    return getattr(module, class_name)


def import_string(dotted_path: str, current_module: str | None = None):
    """
    Variant of `django.utils.module_loading.import_string` that allows relative imports (if `package` is specified).
    """
    try:
        module_path, class_name = dotted_path.rsplit(".", 1)
    except ValueError as err:
        raise ImportError(f"{dotted_path!r} doesn't look like a module path.") from err

    if current_module:
        try:
            package, _ = current_module.rsplit(".", 1)
        except ValueError as err:
            raise ImportError(
                f"{current_module!r} doesn't look like a module name. Using `__name__` in an __init__.py file is not supported."
            ) from err
    else:
        package = None
    try:
        return cached_import(module_path, class_name, package)
    except AttributeError as err:
        raise ImportError(f"Module {module_path!r} does not define a {class_name!r} attribute/class.") from err


class lazy_import_classproperty:
    """
    A variant of django.utils.functional.classproperty that just imports something.
    """

    def __init__(self, target: str, current_module: str | None = None, *, abc: bool = False):
        """
        Args:
            dotted_path (str): The dotted path of the class to import.
            current_module (str | None): The current module for relative imports. You can use ``"__name__"``.
            abc (bool): Use ``True`` if this is set on an ABC class (import via class access will be disabled to prevent the ABC validator
                from importing the target).
        """
        self.abc = abc
        self.current_module = current_module
        self.name = None
        self.target = target

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
        elif name != self.name:
            raise TypeError(f"Cannot assign the same cached_property to two different names ({self.name!r} and {name!r}).")

    def __get__(self, instance, cls=None):
        if self.abc and instance is None:
            return self
        if self.name is None:
            raise TypeError("Cannot use lazy_import_classproperty instance without calling __set_name__ on it.")
        value = import_string(self.target, self.current_module)
        setattr(cls, self.name, value)
        return value


class cached_classproperty:
    """
    A variant of django.utils.functional.classproperty that also caches.

    Examples::

        @cached_classproperty(abc=True)
        def foo(self): ...
            # won't be called by abc's validator

        @cached_classproperty
        def bar(self): ...
    """

    def __init__(self, target: Callable | None = None, *, abc: bool = False, static: bool = False) -> None:
        """
        Args:
            target (callable): The function to be wrapped.
            abc (bool): Use ``True`` if this is set on an ABC class (import via class access will be disabled to prevent the ABC validator
                from calling the target).
            static (bool): Use ``True`` if this can be cached for all the subclasses.
        """
        self.abc = abc
        self.name = None
        self.static = static
        self.owner = None
        self.target = target

    def __call__(self, target: Callable) -> Self:
        if self.target is None:
            self.target = target
        else:
            raise TypeError("Cannot use same cached_classproperty twice.")
        return self

    def __set_name__(self, owner, name):
        if self.static:
            self.owner = owner
        else:
            name = f"__{owner.__name__}_{name}"
        if self.name is None:
            self.name = name
        elif name != self.name:
            raise TypeError(f"Cannot assign the same cached_property to two different names ({self.name!r} and {name!r}).")

    def __get__(self, instance, cls=None):
        if self.abc and instance is None:
            return self
        if self.name is None:
            raise TypeError("Cannot use cached_property instance without calling __set_name__ on it.")
        if self.owner is None:
            owner = cls
        else:
            owner = self.owner
        value = owner.__dict__.get(self.name, self)
        if value is self:
            value = self.target(owner)
            setattr(owner, self.name, value)
        return value


def convert_with_json_encoder(encoder: JSONEncoder, data):
    if isinstance(data, dict):
        return {convert_with_json_encoder(encoder, k): convert_with_json_encoder(encoder, v) for k, v in data.items()}
    elif isinstance(data, list | set | tuple):
        return [convert_with_json_encoder(encoder, v) for v in data]
    elif isinstance(data, str | int | float | bool | None):
        return data
    else:
        return encoder.default(data)
