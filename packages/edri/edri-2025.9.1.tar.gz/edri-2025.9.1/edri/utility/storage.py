from random import choice
from string import ascii_letters, digits
from typing_extensions import LiteralString


class Storage[T](dict[str, T]):
    """
    A generic storage class that extends a dictionary to hold items of any type,
    identified by unique string keys. It provides functionality to automatically
    generate unique keys for items if not provided.

    :Type Parameters:
        T: The type of the items to be stored in the dictionary.

    :Examples:

        >>> storage = Storage[int]()
        >>> key1 = storage.append(100)
        >>> key2 = storage.append(200, key="custom_key")
        >>> storage[key1]
        100
        >>> storage["custom_key"]
        200

    :Note:
        - The `Storage` class ensures that all keys are unique. If a key is not provided,
          it automatically generates a unique key composed of random letters and digits.
        - The default key length is 16 characters, but this can be customized during initialization.
    """

    def __init__(
            self,
            choices: LiteralString = ascii_letters + digits,
            length: int = 16,
    ) -> None:
        """
        Initializes the storage with an empty dictionary and sets up key generation parameters.

        :param choices: A string of characters to use for generating unique keys.
                        Defaults to a combination of ASCII letters and digits.
        :type choices: LiteralString, optional
        :param length: The length of the automatically generated unique keys.
                       Defaults to 16 characters.
        :type length: int, optional
        """
        super().__init__()
        self.choices = choices
        self.length = length

    def _get_unique_key(self) -> str:
        """
        Generates a unique key composed of random letters and digits.

        This method repeatedly generates random keys until it finds one that is not
        already present in the storage.

        :return: A unique string key of specified length.
        :rtype: str

        :Examples:

            >>> storage = Storage[int]()
            >>> unique_key = storage._get_unique_key()
            >>> len(unique_key)
            16
            >>> unique_key.isalnum()
            True
        """
        while True:
            key = ''.join(choice(self.choices) for _ in range(self.length))
            if key not in self:
                return key

    def append(self, item: T, key: str | None = None) -> str:
        """
        Adds an item to the storage with an automatically generated or specified key.

        If the key already exists in the storage, a `KeyError` is raised to prevent
        overwriting existing items.

        :param item: The item to be stored.
        :type item: T
        :param key: The key under which to store the item. If `None`, a unique key
                    is generated automatically.
        :type key: str, optional
        :return: The key used to store the item in the dictionary.
        :rtype: str
        :raises KeyError: If the specified key already exists in the storage.

        :Examples:

            >>> storage = Storage[str]()
            >>> generated_key = storage.append("apple")
            >>> storage[generated_key]
            'apple'
            >>> custom_key = storage.append("banana", key="fruit_1")
            >>> storage["fruit_1"]
            'banana'
            >>> storage.append("cherry", key="fruit_1")
            Traceback (most recent call last):
                ...
            KeyError: 'Key already exists: fruit_1'
        """
        if key is None:
            key = self._get_unique_key()
        elif key in self:
            raise KeyError(f"Key already exists: {key}")
        self[key] = item
        return key
