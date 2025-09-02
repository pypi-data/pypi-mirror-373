# typed-sentinels

Statically-typed sentinel objects with singleton qualities.

## Installation

```bash
pip install typed-sentinels
```

## Quick Start

- `Sentinel` instances are useful for creating unique, type-annotated placeholders, typically used
    when a default value other than `None` is desirable. Only a single instance of `Sentinel` may
    exist for a given type.

```python
from typed_sentinels import Sentinel

# Annotate with the type the sentinel should appear to be to the type-checker
SENTINEL_STR: str = Sentinel(str)


def process_data(value: str = SENTINEL_STR) -> str:
    # Sentinels are always falsy
    if not value:
        return 'No value provided'
    return f'Processing: {value}'


# Type-safe usage
result = process_data()  # "No value provided"
result = process_data('demo123')  # "Processing: demo123"
```

- The `Sentinel` class is particularly well-suited for use with types requiring parameters which are
    only available at runtime, where creating a default instance of the type may not be possible in
    advance, but the structural contract of the type is otherwise guaranteed to be fulfilled once present.

```python
from typed_sentinels import Sentinel


class Custom:
    @property
    def value(self) -> str:
        return self._value

    def __init__(self, required: str, /) -> None:
        self._value = required


# Appears to the type-checker as an instance of `Custom`
CUSTOM: Custom = Sentinel(Custom)


def func(c: Custom = CUSTOM) -> str:
    if c is not CUSTOM:
        return c.value
    return 'c was not provided'
```

- `Sentinel` instances have singleton qualities, but remain distinct as specific to the type they represent:

```python
S1 = Sentinel(dict[str, Any])
S2 = Sentinel(dict[str, Any])
S3 = Sentinel(dict[str, bytes])

assert S1 is S2  # True
assert S2 is not S3  # True
```

- In the simplest form, supposing you don't want or need a distinct instance for different types,
    you could use the `Sentinel` without parameterization or arguments, and the type-checker will
    still be happy:

```python
class Custom:
    def __init__(self, arg1: str, arg2: int, arg3: bool) -> None: ...


# This appears to the type-checker as an actual instance of Custom
CUSTOM: Custom = Sentinel()
reveal_type(CUSTOM)  # Runtime type is 'Sentinel'
```

![Example of Sentinel class mimicking parameterized type](./images/sentinel.png)
