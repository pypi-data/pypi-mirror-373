from typing import Callable, Any
from collections import defaultdict


class NormalizedDefaultDict[KT: str, VT](defaultdict[KT, VT]):
    """
    A defaultdict that normalizes keys upon insertion and retrieval.

    This class extends Python's built-in `defaultdict` by ensuring that all keys
    are normalized using a provided normalization function. By default, keys are
    converted to lowercase strings. This normalization helps maintain consistency
    in key formats, preventing duplicate entries that differ only in case or format.

    :param default_factory: A callable that provides the default value for a new key.
                            If `None`, the default factory is `None`, mirroring `defaultdict`.
    :type default_factory: Callable[[], VT] or None, optional
    :param normalization: A callable that takes a key and returns its normalized form.
                          If `None`, a default normalization function (lowercasing) is used.
    :type normalization: Callable[[Any], KT] or None, optional
    :param *args: Additional positional arguments passed to the `defaultdict` constructor.
    :param **kwargs: Additional keyword arguments passed to the `defaultdict` constructor.

    :raises TypeError: If the provided `default_factory` is not callable or `None`.
    :raises KeyError: If a non-trailing URL parameter is missing when using `format_url`.

    :Examples:

        >>> class Connection:
        ...     pass
        >>> d = NormalizedDefaultDict(default_factory=set, normalization=lambda x: x.lower())
        >>> conn = Connection()
        >>> d['EVENT_TYPE'].add(conn)
        >>> d['event_type']
        {<__main__.Connection object at 0x...>}

    :note:
        - The `NormalizedDefaultDict` ensures that all keys adhere to a consistent format,
          reducing the risk of key duplication due to inconsistent casing or formatting.
        - This class is particularly useful in scenarios where keys are derived from
          user input or external sources that may not enforce consistent key formats.
    """

    def __init__(
            self,
            default_factory: Callable[[], VT] | None = None,
            /,
            *args,
            normalization: Callable[[Any], KT] | None = None,
            **kwargs
    ) -> None:
        """
        Initializes the NormalizedDefaultDict with an optional normalization function.

        :param default_factory: A callable that provides the default value for a new key.
                                If `None`, the default factory is `None`.
        :type default_factory: Callable[[], VT] or None, optional
        :param normalization: A callable that normalizes keys. If `None`, a default
                              normalization function (lowercasing) is used.
        :type normalization: Callable[[Any], KT] or None, optional
        :param *args: Additional positional arguments for the `defaultdict` constructor.
        :param **kwargs: Additional keyword arguments for the `defaultdict` constructor.
        """
        self._normalization = normalization or self._default_normalization

        if args and isinstance(args[0], dict):
            normalized_dict = {self._normalization(k): v for k, v in args[0].items()}
            args = (normalized_dict, *args[1:])
        super().__init__(default_factory, *args, **kwargs)

    def __setitem__(self, key: KT, value: VT) -> None:
        """
        Sets the value for a key after normalizing the key.

        :param key: The key to set in the dictionary.
        :type key: KT
        :param value: The value to associate with the key.
        :type value: VT
        """
        normalized_key = self._normalization(key)
        super().__setitem__(normalized_key, value)

    def __getitem__(self, key: KT) -> VT:
        """
        Retrieves the value for a key after normalizing the key.

        :param key: The key to retrieve from the dictionary.
        :type key: KT
        :return: The value associated with the normalized key.
        :rtype: VT
        :raises KeyError: If the normalized key does not exist in the dictionary.
        """
        normalized_key = self._normalization(key)
        return super().__getitem__(normalized_key)

    @staticmethod
    def _default_normalization(key: KT) -> str:
        """
        Default normalization function that converts keys to lowercase.

        :param key: The key to normalize.
        :type key: KT
        :return: The normalized key as a lowercase string.
        :rtype: str
        """
        return key.lower()

    def update(self, *args, **kwargs) -> None:
        """
        Updates the dictionary with key-value pairs from other mappings or iterables,
        normalizing keys in the process.

        :param args: Additional positional arguments for updating the dictionary.
        :param kwargs: Additional keyword arguments for updating the dictionary.
        """
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
