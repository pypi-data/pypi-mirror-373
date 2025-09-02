from enum import Enum


class StrEnum(str, Enum):
    """
    A string enum that serializes to its value.
    Do not confuse with python 3.11 `StrEnum` which is very similar but doesn't
    serialize to string.

    Note: when the library doesn't support versions prior to 3.11, we can use
    the native `StrEnum`, implementing the `__str__` method.

    >>> class MyEnum(StrEnum):
    ...     foo = "bar"
    >>> MyEnum.foo == "bar"
    True
    >>> str(MyEnum.foo)
    'bar'
    >>> import json; json.dumps({"item": MyEnum.foo})
    '{"item": "bar"}'
    """

    def __str__(self) -> str:
        """Method used for serialization."""
        return self.value
