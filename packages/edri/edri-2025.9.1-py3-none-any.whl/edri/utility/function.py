from typing import Iterable, Callable, Any, Optional

from edri.dataclass.injection import Injection


def camel2snake(title: str) -> str:
    """
    Converts a camelCase or PascalCase string to a snake_case string.

    :param title: The camelCase or PascalCase string to be converted.
    :type title: str
    :return: The converted snake_case string.
    :rtype: str

    :Examples:

        >>> camel2snake("camelCaseExample")
        'camel_case_example'
        >>> camel2snake("CamelCaseExample")
        'camel_case_example'
    """
    new_title = ""
    underscore = False
    for letter in title:
        if 65 <= ord(letter) <= 90:
            if underscore:
                new_title += '_'
                underscore = False
            new_title += chr(ord(letter) + 32)
        else:
            underscore = True
            new_title += letter
    return new_title


def snake2camel(title: str, /, *, exceptions: Optional[tuple[str, ...]] = None) -> str:
    """
    Converts a snake_case string to a camelCase string, with optional exceptions
    where the conversion should not be applied.

    :param title: The snake_case string to be converted.
    :type title: str
    :param exceptions: A tuple of strings that, when matched at the beginning of the title,
                       prevent conversion and return the title as is. Defaults to None.
    :type exceptions: Optional[Tuple[str, ...]]
    :return: The converted camelCase string if no exception is matched; otherwise, the original string.
    :rtype: str
    :raises KeyError: If a non-trailing URL parameter is missing and subsequent placeholders
                      are present.

    :Examples:

        >>> snake2camel("snake_case_example")
        'snakeCaseExample'
        >>> snake2camel("id_example", exceptions=("id_",))
        'id_example'
    """
    if exceptions is None:
        exceptions = ("id_",)
    if title.startswith(exceptions):
        return title
    title_list = title.split('_')
    if not title_list:
        return title
    title_list = [title_list[0]] + [word.capitalize() for word in title_list[1:]]
    return ''.join(title_list)


def partition[T](pred: Callable[[T], bool], iterable: Iterable[T]) -> tuple[list[T], list[T]]:
    """
    Splits an iterable into two lists based on a predicate function.

    :param pred: A function that takes an item and returns a boolean value.
                 Items for which this function returns True will go into the first list;
                 items for which it returns False will go into the second list.
    :type pred: Callable[[T], bool]
    :param iterable: The iterable to be partitioned.
    :type iterable: Iterable[T]
    :return: A tuple containing two lists:
             - The first list contains all items from the iterable for which `pred` returned True.
             - The second list contains all items from the iterable for which `pred` returned False.
    :rtype: Tuple[List[T], List[T]]

    :Examples:

        >>> partition(lambda x: x % 2 == 0, [1, 2, 3, 4])
        ([2, 4], [1, 3])
    """
    trues = []
    falses = []
    for item in iterable:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)
    return trues, falses


def format_url(url: str, **kwargs: Any) -> str:
    """
    Formats a URL string by replacing placeholders with keyword arguments. If a parameter is missing,
    it is considered optional only if it appears at the end of the URL or if all subsequent placeholders
    are also missing. Otherwise, raises a KeyError.

    :param url: The URL template containing placeholders in the format `{placeholder}`.
    :type url: str
    :param kwargs: Keyword arguments representing the replacement values for the placeholders in the URL.
    :type kwargs: Any
    :return: The formatted URL with all placeholders replaced by their corresponding values.
             If optional parameters are missing, trailing placeholders are removed.
    :rtype: str
    :raises KeyError: If a required URL parameter is missing, and it is not at the end of the URL,
                      or if other placeholders to the right are present.

    :Examples:

        >>> format_url('https://example.com/{user}/{id}', user='john', id=42)
        'https://example.com/john/42'

        >>> format_url('https://example.com/{user}/{id}', user='john')
        'https://example.com/john'

        >>> format_url('https://example.com/{user}/{id}/{page}', user='john')
        'https://example.com/john'

        >>> format_url('https://example.com/{user}/{id}/detail', user='john')
        Traceback (most recent call last):
            ...
        KeyError: 'Optional url parameter is missing: id'

        >>> format_url('https://example.com/{user}/{id}/{page}', user='john', page='home')
        Traceback (most recent call last):
            ...
        KeyError: 'Optional url parameter is missing: id'
    """

    class Helper(dict):
        def __init__(self, **kwargs) -> None:
            super().__init__(kwargs)
            self.missing = []

        def __missing__(self, key: str) -> str:
            self.missing.append(key)
            return f"{{{key}}}"

    kwargs_helper = Helper(**kwargs)
    formatted_url = url.format_map(kwargs_helper)
    for missing in reversed(kwargs_helper.missing):
        placeholder = f"{{{missing}}}"
        if formatted_url.endswith(placeholder):
            # Remove the trailing placeholder along with the preceding slash if present
            if len(formatted_url) > len(placeholder) and formatted_url[-len(placeholder) - 1] == '/':
                formatted_url = formatted_url[:-len(placeholder) - 1]
            else:
                formatted_url = formatted_url[:-len(placeholder)]
        else:
            raise KeyError(f"Optional url parameter is missing: {missing}")
    return formatted_url


def inject(*args, **kwargs) -> Injection:
    """
    Creates an `Injection` instance for a given class and its initialization parameters.

    This function is typically used to declaratively define dependency injections
    by specifying a class and any keyword arguments to pass to its constructor.

    Args:
        cls (T): The class type to be injected.
        **kwargs: Keyword arguments to be used as parameters for instantiation.

    Returns:
        Injection[T]: An `Injection` object wrapping the class and its parameters.

    Example:
        inject(MyService, config=..., db=...)
    """
    return Injection(classes=args, parameters=kwargs)
