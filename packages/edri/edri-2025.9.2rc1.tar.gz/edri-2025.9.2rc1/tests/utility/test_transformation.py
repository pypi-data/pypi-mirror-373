import unittest
from edri.utility.transformation import StringTransformer

class TestStringTransformer(unittest.TestCase):

    def test_lowercase_transformation(self):
        # Test lowercase transformation
        st = StringTransformer("Hello", lower=True)
        self.assertEqual(st, "hello")

    def test_uppercase_transformation(self):
        # Test uppercase transformation
        st = StringTransformer("Hello", upper=True)
        self.assertEqual(st, "HELLO")

    def test_reverse_transformation(self):
        # Test custom transformation (reverse string)
        st = StringTransformer("Hello", transform=lambda x: x[::-1])
        self.assertEqual(st, "olleH")

    def test_multiple_transformations(self):
        # Test applying multiple transformations (lowercase and reverse)
        st = StringTransformer("Hello", lower=True, transform=lambda x: x[::-1])
        self.assertEqual(st, "olleh")

    def test_no_transformation(self):
        # Test no transformations (should return the original string)
        st = StringTransformer("Hello")
        self.assertEqual(st, "Hello")

    def test_upper_and_lower_conflict(self):
        # Test when both lower and upper are True (upper should take precedence)
        st = StringTransformer("Hello", lower=True, upper=True)
        self.assertEqual(st, "HELLO")

    def test_custom_function(self):
        # Test with a more complex custom transformation
        st = StringTransformer("Hello", transform=lambda x: x.replace('l', 'x'))
        self.assertEqual(st, "Hexxo")

    def test_empty_string(self):
        # Test with an empty string
        st = StringTransformer("")
        self.assertEqual(st, "")

    def test_non_string_input(self):
        # Test non-string input (should handle it since the class itself accepts only a string)
        st = StringTransformer("12345", transform=lambda x: x[::-1])
        self.assertEqual(st, "54321")

    def test_special_characters(self):
        # Test with special characters in the string
        st = StringTransformer("Hello@123", transform=lambda x: x[::-1])
        self.assertEqual(st, "321@olleH")

    def test_none_input(self):
        # Test if None is passed as input (str allows None as input and converts it to 'None')
        st = StringTransformer(None)
        self.assertEqual(str(st), 'None')

    def test_transform_function_with_no_output(self):
        # Test if transform function does not alter the string
        st = StringTransformer("Hello", transform=lambda x: None)
        self.assertEqual(st, None)  # Since None will be returned when no transformation is applied

    def test_custom_function_with_edge_case(self):
        # Test with an empty string in a custom transform function
        st = StringTransformer("", transform=lambda x: x[::-1])
        self.assertEqual(st, "")
