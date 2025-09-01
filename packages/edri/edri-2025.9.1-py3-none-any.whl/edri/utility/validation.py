from datetime import date, datetime, time
from re import Pattern


class StringValidation(str):
    """
    A string type that performs validation on initialization.

    This class validates the string against optional constraints:
    - A regular expression pattern.
    - Minimum and maximum allowed lengths.

    Args:
        data (str): The input string to validate.
        maximum_length (int, optional): Maximum allowed length of the string.
        minimum_length (int, optional): Minimum required length of the string.
        regex (Pattern, optional): A compiled regex pattern the string must match.
    Raises:
        ValueError: If the string does not match the regex,
                    or its length is outside the allowed bounds.

    Example:
        >>> StringValidation("hello", minimum_length=3, maximum_length=10)
        'hello'
    """

    def __new__(cls, value, /, *,
                maximum_length: int = None,
                minimum_length: int = None,
                regex: Pattern | None = None,
                ):

        value = super().__new__(cls, value)
        if regex is not None:
            if not regex.match(value):
                raise ValueError(f"Invalid data provided. Data '{value}' not match pattern '{regex.pattern}'")
        if minimum_length is not None and len(value) < minimum_length:
            raise ValueError(f"Invalid data provided. Data '{value}' is too short")
        if maximum_length is not None and len(value) > maximum_length:
            raise ValueError(f"Invalid data provided. Data '{value}' is too long")

        return value


class IntegerValidation(int):
    """
    An integer type that performs validation on initialization.

    This class validates the integer against optional constraints:
    - Minimum and maximum allowed values.

    Args:
        data (int): The input integer to validate.
        minimum (int, optional): Minimum allowed value.
        maximum (int, optional): Maximum allowed value.

    Raises:
        ValueError: If the value is less than `minimum` or greater than `maximum`.

    Example:
        >>> IntegerValidation(5, minimum=1, maximum=10)
        5
    """

    def __new__(cls, value, /, *, minimum: int | None = None, maximum: int | None = None):
        value = super().__new__(cls, value)
        if minimum is not None and value < minimum:
            raise ValueError(f"Invalid data provided. Data '{value}' is too small")
        if maximum is not None and value > maximum:
            raise ValueError(f"Invalid data provided. Data '{value}' is too big")
        return value


class FloatValidation(float):
    """
    A float type that performs validation on initialization.

    This class validates the float against optional constraints:
    - Minimum and maximum allowed values.

    Args:
        data (float): The input float to validate.
        minimum (float, optional): Minimum allowed value.
        maximum (float, optional): Maximum allowed value.

    Raises:
        ValueError: If the value is less than `minimum` or greater than `maximum`.

    Example:
        >>> FloatValidation(3.14, minimum=1.0, maximum=5.0)
        3.14
    """

    def __new__(cls, value, minimum: float | None = None, maximum: float | None = None):
        value = super().__new__(cls, value)
        if minimum is not None and value < minimum:
            raise ValueError(f"Invalid data provided. Data '{value}' is too small")
        if maximum is not None and value > maximum:
            raise ValueError(f"Invalid data provided. Data '{value}' is too big")
        return value


class DateValidation(date):
    """
    A date type that performs validation on initialization.

    This class validates the date against optional constraints:
    - Minimum allowed date.
    - Maximum allowed date.

    Args:
        year (int): Year component of the date.
        month (int): Month component of the date.
        day (int): Day component of the date.
        minimum_date (date, optional): The earliest valid date.
        maximum_date (date, optional): The latest valid date.

    Raises:
        ValueError: If the date is outside the allowed bounds.

    Example:
        >>> DateValidation(2024, 3, 28, minimum_date=date(2024, 1, 1))
        datetime.date(2024, 3, 28)
    """

    def __new__(cls, year, month=None, day=None, /, *,
                minimum_date: date | None = None,
                maximum_date: date | None = None):

        value = super().__new__(cls, year, month, day)

        if minimum_date and value < minimum_date:
            raise ValueError(f"Date '{value}' is earlier than minimum allowed '{minimum_date}'")
        if maximum_date and value > maximum_date:
            raise ValueError(f"Date '{value}' is later than maximum allowed '{maximum_date}'")

        return value


class TimeValidation(time):
    """
    A time type that performs validation on initialization.

    This class validates the time against optional constraints:
    - Minimum allowed time.
    - Maximum allowed time.

    Args:
        hour (int): Hour component of the time.
        minute (int): Minute component of the time.
        second (int, optional): Second component (default is 0).
        microsecond (int, optional): Microsecond component (default is 0).
        minimum_time (time, optional): The earliest valid time.
        maximum_time (time, optional): The latest valid time.

    Raises:
        ValueError: If the time is outside the allowed bounds.

    Example:
        >>> TimeValidation(12, 30, maximum_time=time(20, 0))
        datetime.time(12, 30)
    """

    def __new__(cls, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, /, *,
                minimum_time: time | None = None,
                maximum_time: time | None = None):

        value = super().__new__(cls, hour, minute, second, microsecond, tzinfo)

        if minimum_time and value < minimum_time:
            raise ValueError(f"Time '{value}' is earlier than minimum allowed '{minimum_time}'")
        if maximum_time and value > maximum_time:
            raise ValueError(f"Time '{value}' is later than maximum allowed '{maximum_time}'")

        return value


class DateTimeValidation(datetime):
    """
    A datetime type that performs validation on initialization.

    This class validates the datetime against optional constraints:
    - Minimum allowed datetime.
    - Maximum allowed datetime.

    Args:
        year (int): Year component.
        month (int): Month component.
        day (int): Day component.
        hour (int, optional): Hour component (default is 0).
        minute (int, optional): Minute component (default is 0).
        second (int, optional): Second component (default is 0).
        microsecond (int, optional): Microsecond component (default is 0).
        minimum_datetime (datetime, optional): The earliest valid datetime.
        maximum_datetime (datetime, optional): The latest valid datetime.

    Raises:
        ValueError: If the datetime is outside the allowed bounds.

    Example:
        >>> DateTimeValidation(2024, 3, 28, 15, 45,
        ...     minimum_datetime=datetime(2024, 3, 1))
        datetime.datetime(2024, 3, 28, 15, 45)
    """

    def __new__(cls, year, month=None, day=None, hour=0, minute=0, second=0, microsecond=0, tzinfo=None, /, *,
                minimum_datetime: datetime | None = None,
                maximum_datetime: datetime | None = None):

        instance = super().__new__(cls, year, month, day, hour, minute, second, microsecond, tzinfo)

        if minimum_datetime and instance < minimum_datetime:
            raise ValueError(f"Datetime '{instance}' is earlier than minimum allowed '{minimum_datetime}'")
        if maximum_datetime and instance > maximum_datetime:
            raise ValueError(f"Datetime '{instance}' is later than maximum allowed '{maximum_datetime}'")

        return instance
