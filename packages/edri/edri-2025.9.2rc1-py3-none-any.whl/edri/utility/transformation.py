from typing import Callable, Optional, Any


class StringTransformer(str):
    """
    A class that extends str and allows transformation on initialization.
    The transformation can be predefined (like lowercasing) or custom using a lambda function.
    The transformation settings are applied during object initialization.

    Args:
        transform (callable, optional): A function that takes a string and returns a transformed version.
        lower (bool, optional): If True, the string will be converted to lowercase.
        upper (bool, optional): If True, the string will be converted to uppercase.

    Example:
        >>> st = StringTransformer("Hello", lower=True)
        >>> print(st)
        'hello'

        >>> st = StringTransformer("Hello", transform=lambda x: x[::-1])
        >>> print(st)
        'olleH'
    """

    def __new__(cls, value: Any,
                transform: Optional[Callable[[str], str]] = None,
                lower: bool = False,
                upper: bool = False):
        value = super().__new__(cls, value)
        # Apply predefined transformations (lower/upper)
        if lower:
            value = value.lower()
        if upper:
            value = value.upper()

        # Apply the custom transformation function if provided
        if transform is not None:
            value = transform(value)

        # Return the transformed value as an instance of StringTransformer
        return value