from typing import TypeVar, Type, Callable, Any, overload
from typing_extensions import ParamSpec

__version__: str

T = TypeVar("T")
P = ParamSpec("P")

# Overloads for the singleton decorator to handle both @singleton and @singleton() usage
@overload
def singleton(cls: Type[T]) -> Type[T]:
    """
    Singleton decorator that preserves the original class type.
    Usage: @singleton
    """
    ...

@overload
def singleton(cls: None = None) -> Callable[[Type[T]], Type[T]]:
    """
    Singleton decorator factory that preserves the original class type.
    Usage: @singleton()
    """
    ...

class SingletonMeta(type):
    """
    Metaclass for singleton pattern.

    Usage:
    class MyClass(metaclass=SingletonMeta):
        ...
    """

    _instances: dict[Type[Any], Any]

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Create or return existing instance."""
        ...

# Export commonly used items
__all__ = ["singleton", "SingletonMeta"]
