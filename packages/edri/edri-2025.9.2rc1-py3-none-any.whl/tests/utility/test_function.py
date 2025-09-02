import unittest

from edri.dataclass.injection import Injection
from edri.utility.function import camel2snake, snake2camel, partition
from edri.utility.transformation import StringTransformer


class MyClass:
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def __repr__(self):
        return f"MyClass(param1={self.param1}, param2={self.param2})"


class AnotherClass:
    def __init__(self, param1):
        self.param1 = param1

    def __repr__(self):
        return f"AnotherClass(param1={self.param1})"


class TestStringMethods(unittest.TestCase):

    def test_camel2snake(self) -> None:
        self.assertEqual(camel2snake("camelCaseExample"), "camel_case_example")
        self.assertEqual(camel2snake("CamelCaseExample"), "camel_case_example")
        self.assertEqual(camel2snake("camel"), "camel")
        self.assertEqual(camel2snake("Camel"), "camel")
        self.assertEqual(camel2snake("CamelCEO"), "camel_ceo")

    def test_snake2camel(self) -> None:
        self.assertEqual(snake2camel("snake_case_example"), "snakeCaseExample")
        self.assertEqual(snake2camel("id_example"), "id_example")
        self.assertEqual(snake2camel("id_example", exceptions=tuple()), "idExample")
        self.assertEqual(snake2camel("example"), "example")
        self.assertEqual(snake2camel("snake_ceo"), "snakeCeo")

    def test_partition_with_numbers(self) -> None:
        def is_even(n: int) -> bool:
            return n % 2 == 0

        result = partition(is_even, [1, 2, 3, 4, 5, 6])
        self.assertEqual(result, ([2, 4, 6], [1, 3, 5]))

    def test_partition_with_strings(self) -> None:
        def is_uppercase(s: str) -> bool:
            return s.isupper()

        result = partition(is_uppercase, ["Hello", "WORLD", "Test", "PYTHON"])
        self.assertEqual(result, (["WORLD", "PYTHON"], ["Hello", "Test"]))

    def test_partition_with_empty_iterable(self) -> None:
        def is_positive(n: int) -> bool:  # pragma: no cover
            return n > 0

        result = partition(is_positive, [])
        self.assertEqual(result, ([], []))

    def test_partition_with_mixed_types(self) -> None:
        def is_int(value) -> bool:
            return isinstance(value, int)

        result = partition(is_int, [1, "hello", 2, "world", 3, 4.5])
        self.assertEqual(result, ([1, 2, 3], ["hello", "world", 4.5]))

    def test_partition_with_custom_predicate(self) -> None:
        def is_long_string(s: str) -> bool:
            return len(s) > 5

        result = partition(is_long_string, ["short", "longer", "tiny", "lengthy"])
        self.assertEqual(result, (["longer", "lengthy"], ["short", "tiny"]))

    def test_initialization_valid(self):
        # Test with valid class (StringTransformer)
        injection = Injection(
            classes=(StringTransformer,),
            parameters={"transform": lambda x: x[::-1]}  # Reversing the string
        )
        self.assertEqual(injection.classes, (StringTransformer,))

    def test_iteration(self):
        injection = Injection(
            classes=(StringTransformer,),
            parameters={"transform": lambda x: x[::-1]}  # Reversing the string
        )

        # Test the callable functionality of iteration
        iter_objects = list(injection)

        # Check if the correct number of callables are yielded (should be 1 in this case)
        self.assertEqual(len(iter_objects), 1)

        # Create an instance using the yielded function and check the result
        instance = iter_objects[0]("hello")
        self.assertEqual(str(instance), "olleh")

    def test_repr(self):
        injection = Injection(
            classes=(StringTransformer,),
            parameters={"transform": lambda x: x[::-1]}  # Reversing the string
        )

        # Check if the string representation is correct
        repr_string = repr(injection)
        self.assertIn("StringTransformer(transform=<function", repr_string)
