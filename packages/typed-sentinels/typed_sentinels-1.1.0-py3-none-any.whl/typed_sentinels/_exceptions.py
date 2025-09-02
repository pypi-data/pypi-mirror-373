from typing import Any


class SentinelError(TypeError):
    """Base class from which all `typed_sentinels` `Exception` objects inherit."""


class InvalidHintError(SentinelError):
    """Argument for `hint` must not be `Sentinel`, `Ellipsis`, `True`, `False`, `None`, or a `Sentinel` instance."""

    def __init__(self, hint: Any, /) -> None:
        """Initialize `InvalidHintError`.

        Parameters
        ----------
        hint : Any
            The invalid argument for `hint` as provided to the `Sentinel` class constructor.
        """
        msg = 'Argument for `hint` must not be `None`\n'
        if hint is not None:
            msg = 'Argument for `hint` must not be any of: '
            msg += '`Sentinel`, `Ellipsis`, `True`, `False`, `None`, or a `Sentinel` instance\n'
        msg += f"Received argument for hint: '{hint!r}'"
        super().__init__(msg)


class SubscriptedTypeError(SentinelError):
    """Subscripted type and `hint` must match."""

    def __init__(self, hint: Any, subscripted: Any) -> None:
        """Initialize `SubscriptedTypeError`.

        Parameters
        ----------
        hint : Any
            Provided argument for `hint`.
        subscripted : Any
            Type provided via subscription notation to the `Sentinel` class object.
        """
        msg = 'Subscripted type and `hint` must match\n'
        msg += f'   Subscripted type: {subscripted!r}\n'
        msg += f'               Hint: {hint!r}'
        super().__init__(msg)
