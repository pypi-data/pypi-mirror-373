import unittest

from edri.utility.storage import Storage


class TestStorage(unittest.TestCase):

    def test_initialization(self) -> None:
        storage: Storage[int] = Storage()
        self.assertIsInstance(storage, Storage)

    def test_unique_key_generation(self) -> None:
        storage: Storage[int] = Storage()
        keys = {storage._get_unique_key() for _ in range(1000)}
        self.assertEqual(len(keys), 1000)

    def test_append_with_no_key(self) -> None:
        storage: Storage[str] = Storage()
        key = storage.append("Test")
        self.assertIn(key, storage)
        self.assertEqual(storage[key], "Test")

    def test_append_with_specific_key(self) -> None:
        storage: Storage[str] = Storage()
        key = "customKey"
        storage.append("Test", key)
        self.assertIn(key, storage)
        self.assertEqual(storage[key], "Test")

    def test_key_already_exists_exception(self) -> None:
        storage: Storage[str] = Storage()
        key = "customKey"
        storage.append("Test", key)
        with self.assertRaises(KeyError):
            storage.append("New Test", key)

    def test_type_storage(self) -> None:
        storage: Storage[any] = Storage()
        storage.append(1)
        storage.append("string")
        storage.append([1, 2, 3])
        self.assertEqual(len(storage), 3)
