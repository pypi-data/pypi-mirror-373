from dataclasses import is_dataclass, asdict
from enum import Enum
from json import JSONEncoder
from pathlib import Path
from typing import Any
from uuid import UUID


class CustomJSONEncoder(JSONEncoder):
    """
    Custom JSON encoder that extends Python's built-in JSONEncoder to handle additional Python types
    and custom serialization logic.

    Supported types and custom behaviors:
    - Objects with a `to_json()` method: Serialized using that method.
    - Datetime-like objects with `isoformat()`: Serialized to ISO 8601 format.
    - `Path` objects: Serialized as POSIX-style strings.
    - `bytes` and `bytearray`: Encoded as hexadecimal strings.
    - `Enum` members: Serialized using their `.value`.
    - `UUID` instances: Serialized as hexadecimal strings.
    - `Exception` instances: Serialized as a dictionary with type, message, and args.
    - Dataclass instances: Converted to dictionaries via `asdict`.

    Args:
        skipkeys (bool): Whether to skip keys not of a basic type (str, int, float, bool, None).
        ensure_ascii (bool): If True, escapes all non-ASCII characters in output.
        check_circular (bool): If True, checks for circular references and raises an error if found.
        allow_nan (bool): If True, allows NaN and Infinity values (JavaScript-compatible).
        sort_keys (bool): If True, output dictionary keys are sorted.
        indent (int or None): If specified, pretty-prints output with given number of spaces.
        separators (tuple or None): Tuple of (item_separator, key_separator) for customizing output.
        default (callable or None): A fallback function for unsupported objects.
        context (dict or None): Optional context dictionary for passing extra encoding parameters.
    """

    def __init__(self, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, default=None, context=None):
        super().__init__(
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
            default=default,
        )
        self.context = context

    def default(self, data: Any) -> Any:
        """
        Serializes unsupported data types into JSON-compatible formats.

        Custom serialization behavior:
        - If object has `to_json()` method: Calls and returns its result.
        - If object has `isoformat()` method (e.g., datetime): Uses its ISO 8601 representation.
        - If object is a `Path`: Returns its POSIX-style path string.
        - If object is `bytes` or `bytearray`: Returns a hex-encoded string.
        - If object is an `Enum`: Returns its `.value`.
        - If object is a `UUID`: Returns its hexadecimal string.
        - If object is an `Exception`: Returns a dict with type, message, and args.
        - If object is a dataclass: Converts to a dictionary via `asdict()`.

        Args:
            data (Any): The object to be serialized.

        Returns:
            Any: A JSON-serializable object.
        """
        if hasattr(data, "to_json"):
            return data.to_json()
        elif hasattr(data, "isoformat"):
            return data.isoformat()
        elif isinstance(data, Path):
            return data.as_posix()
        elif isinstance(data, (bytes, bytearray)):
            return data.hex()
        elif isinstance(data, Enum):
            return data.value
        elif isinstance(data, UUID):
            return str(data)
        elif isinstance(data, Exception):
            return {
                'type': type(data).__name__,
                'message': str(data),
                'args': data.args
            }
        elif is_dataclass(data):
            return asdict(data)
        else:
            return super().default(data)
