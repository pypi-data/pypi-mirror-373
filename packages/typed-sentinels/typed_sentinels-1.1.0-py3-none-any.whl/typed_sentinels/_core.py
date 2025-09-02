from __future__ import annotations

from threading import Lock
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    NoReturn,
    SupportsIndex,
    TypeGuard,
    final,
)
from weakref import WeakValueDictionary

from ._exceptions import InvalidHintError, SubscriptedTypeError

if TYPE_CHECKING:
    from collections.abc import Callable

_OBJECT = object()


@final
class Sentinel:
    """Statically-typed sentinel object with singleton qualities.

    `Sentinel` instances provide unique placeholder objects that maintain singleton behavior for a given type. They are
    particularly well-suited for use with types requiring parameters which are only available at runtime, where creating
    a default instance of the type may not be possible in advance, but the structural contract of the type is otherwise
    guaranteed to be fulfilled once present.

    Examples
    --------
    Basic usage:

    ```
    from typed_sentinels import Sentinel


    SNTL = Sentinel()  # Same as `typing.Any`
    SNTL_BYTES = Sentinel(bytes)  # Same as `bytes`
    SNTL_TUPLE = Sentinel[tuple[str, ...]]()  # Same as `tuple[str, ...]`


    assert SNTL is not SNTL_BYTES  # True
    assert Sentinel() is SNTL  # True - `Sentinel` objects are singletons specific to the assigned type
    assert Sentinel(tuple[str, ...]) is SNTL_TUPLE  # True
    assert Sentinel(tuple[bytes, ...]) is not SNTL_TUPLE  # True
    ```


    `Sentinel` objects are indistinguishable from an instance of the assigned type to the type-checker:

    ```
    from typing import reveal_type


    class Custom:
        def __init__(self, req_str: str, req_bytes: bytes) -> None:
            if not req_str or not req_bytes:
                raise ValueError


    SNTL_CUSTOM = Sentinel(Custom)
    reveal_type(SNTL_CUSTOM)  # Revealed type is `Custom` -> Runtime type is `Sentinel`


    def example_func(b: bytes = SNTL_BYTES, c: Custom = SNTL_CUSTOM) -> Any:
        if not b:
            print('Sentinels are falsey so this check works')
        if not tup:
            ...
    ```

    This even works for complex types like `Callable`:

    ```
    # Note: It's incorrect to pass `Callable` directly to the constructor; instead, parameterize by subscription:
    SNTL_CALLABLE = Sentinel[Callable[..., str]]()
    reveal_type(SNTL_CALLABLE)  # Type of "SNTL_CALLABLE" is "(...) -> str"
    ```
    """

    __slots__ = ('__weakref__', '_hint')

    _cls_cache: ClassVar[WeakValueDictionary[tuple[str, Any], Sentinel[Any]]] = WeakValueDictionary()
    _cls_hint: ClassVar[Any] = _OBJECT
    _cls_lock: ClassVar[Lock] = Lock()

    _hint: Any

    @property
    def hint(self) -> Any:
        """Type associated with this `Sentinel` instance."""
        return self._hint

    def __new__(cls, hint: Any = _OBJECT, /) -> Any:
        """Create or retrieve a `Sentinel` instance for the given `hint` type.

        Parameters
        ----------
        hint : T, optional
            Type that this `Sentinel` should represent. If not provided, and if the class has not been otherwise
            parameterized by subscription, this defaults to `Any`.

        Returns
        -------
        T
            `Sentinel` object instance for the given `hint` type, either created anew or retrievd from the class-level
            `WeakValueDictionary` cache. The `Sentinel` instance will appear to type-checkers as an instance of `hint`.

        Raises
        ------
        InvalidHintError
            If `hint` is any of: `Sentinel`, `Ellipsis`, `True`, `False`, `None`, or a `Sentinel` instance.
        SubscriptedTypeError
            If provided both a subscripted type parameter and a direct type argument and the types should differ (e.g.,
            `Sentinel[A](B)` will raise `SubscriptedTypeError`).
        """
        if (_cls_hint := cls._cls_hint) is not _OBJECT:
            cls._cls_hint = _OBJECT
        if (hint is _OBJECT) and (_cls_hint is not _OBJECT):
            hint = _cls_hint
        if hint is _OBJECT:
            hint = Any

        key = (cls.__name__, hint)
        if (inst := cls._cls_cache.get(key)) is not None:
            return inst

        if hint not in (_OBJECT, Any) and (_cls_hint not in (_OBJECT, Any)):
            if (hint != _cls_hint) and (hint is not _cls_hint):
                raise SubscriptedTypeError(hint=hint, subscripted=_cls_hint)

        if isinstance(hint, Sentinel) or (hint in (Sentinel, Ellipsis, True, False, None)):
            raise InvalidHintError(hint)

        with cls._cls_lock:
            if (inst := cls._cls_cache.get(key)) is None:  # pragma: no cover
                inst = super().__new__(cls)
                super().__setattr__(inst, '_hint', hint)
                cls._cls_cache[key] = inst

        return inst

    def __class_getitem__(cls, key: Any) -> Any:
        """Set the class-level `_cls_hint` to `key` and return the class object.

        Parameters
        ----------
        key : T
            Type to be associated with the class and inherited by future instances.

        Returns
        -------
        T
            `Sentinel` class object.
        """
        cls._cls_hint = key
        return cls

    def __getitem__(self, key: Any) -> Any:
        """Return the `Sentinel` instance for indexing operations.

        Parameters
        ----------
        key : T
            Index or key (ignored in this implementation).

        Returns
        -------
        T
            `Sentinel` instance.
        """
        return self

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Return the `Sentinel` instance for callable operations.

        Parameters
        ----------
        *args : Any
            Positional arguments (ignored).
        **kwargs : Any
            Keyword arguments (ignored).

        Returns
        -------
        T
            `Sentinel` instance.
        """
        return self

    def __str__(self) -> str:
        """Return a string representation of the `Sentinel` instance.

        Returns
        -------
        str
            String value in the format of `<Sentinel: {hint!s}>`.
        """
        hint_str, hint_repr = str(self._hint), repr(self._hint)
        if ('[' in hint_repr) and ('.' not in hint_repr):
            hint_str = hint_repr
        elif hasattr(self._hint, '__name__'):
            hint_str = self._hint.__name__
        elif hasattr(self._hint, '__qualname__'):
            hint_str = self._hint.__qualname__
        if hint_str.startswith("<class '") and hint_str.endswith("'>"):  # pragma: no cover
            hint_str = hint_str[8:-2]
        return f'<Sentinel: {hint_str}>'

    def __repr__(self) -> str:
        """Return a detailed string representation of the `Sentinel` instance.

        Returns
        -------
        str
            String value in the format of `<Sentinel: {hint!r}>`.
        """
        return f'<Sentinel: {self._hint!r}>'

    def __hash__(self) -> int:
        """Return a hash value derived from the instance `__class__` and `hint`.

        Returns
        -------
        int
            Hash of the tuple `(self.__class__, self._hint)`.
        """
        return hash((self.__class__, self._hint))

    def __bool__(self) -> bool:
        """Return `False`, as `Sentinel` objects are always falsey.

        Returns
        -------
        Literal[False]
            Always `False`.
        """
        return False

    def __eq__(self, other: object) -> bool:
        """Check equality with another object.

        Parameters
        ----------
        other : object
            Object with which to compare.

        Returns
        -------
        bool
            - `True` if `other` is a `Sentinel` instance with the same `hint`.
            - `False` otherwise.
        """
        if not isinstance(other, self.__class__):
            return False
        return self.__class__ == other.__class__ and self._hint == other._hint

    def __copy__(self) -> Any:
        """Return the `Sentinel` instance for shallow copy operations.

        Returns
        -------
        Sentinel[T]
            `Sentinel` instance.
        """
        return self

    def __deepcopy__(self, memo: Any) -> Any:
        """Return the `Sentinel` instance for deep copy operations.

        Parameters
        ----------
        memo : Any
            Memo dictionary (ignored).

        Returns
        -------
        Sentinel[T]
            `Sentinel` instance.
        """
        return self

    def __reduce__(self) -> tuple[Callable[..., Sentinel], tuple[Any]]:
        """Support for pickle serialization.

        Returns
        -------
        tuple[Callable[..., Sentinel[T]], tuple[T]]
            Tuple containing the instance `__class__` and `hint` for reconstruction.
        """
        return (self.__class__, (self._hint,))

    def __reduce_ex__(self, protocol: SupportsIndex) -> tuple[Callable[..., Sentinel], tuple[Any]]:
        """Support for pickle serialization with protocol.

        Parameters
        ----------
        protocol : SupportsIndex
            The pickle protocol (ignored, delegates to `__reduce__`).

        Returns
        -------
        tuple[Callable[..., Sentinel[T]], tuple[T]]
            Tuple containing the instance `__class__` and `hint` for reconstruction.
        """
        return self.__reduce__()

    def __setattr__(self, name: str, value: Any) -> NoReturn:
        """Raise an error to prevent attribute modification.

        Parameters
        ----------
        name : str
            Attribute name (ignored).
        value : Any
            Value to be set (ignored).

        Raises
        ------
        AttributeError
            Always raised.
        """
        msg = f'Cannot modify attributes of {self!r}'
        raise AttributeError(msg)

    def __delattr__(self, name: str) -> NoReturn:
        """Raise an error to prevent attribute deletion.

        Parameters
        ----------
        name : str
            Attribute name (ignored).

        Raises
        ------
        AttributeError
            Always raised.
        """
        msg = f'Cannot delete attributes of {self!r}'
        raise AttributeError(msg)


def is_sentinel(obj: Any, typ: Any = None) -> TypeGuard[Sentinel]:
    """Return `True` if `obj` is a `Sentinel` instance, optionally further narrowed to be of `typ` type.

    Parameters
    ----------
    obj : Any
        Possible `Sentinel` instance.
    typ : T | None, optional
        Optional type to be used to further narrow the type of the `Sentinel`. If provided, and if `obj` is a `Sentinel`
        instance, this must match `obj.hint`.

    Returns
    -------
    TypeGuard[Sentinel[T]]
        - `True` if `obj` is a `Sentinel` instance.
        - `False` otherwise.
    """
    if typ is not None:
        if isinstance(obj, Sentinel) and hasattr(obj, 'hint'):  # pragma: no cover
            return obj.hint == typ
    return isinstance(obj, Sentinel)
