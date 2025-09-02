import unittest
from datetime import date, time, datetime
from re import compile

from edri.utility.validation import StringValidation, IntegerValidation, FloatValidation, DateValidation, TimeValidation, DateTimeValidation


class TestStringValidation(unittest.TestCase):
    def test_valid_string(self):
        value = StringValidation('hello', minimum_length=3, maximum_length=10)
        self.assertEqual(value, 'hello')

    def test_too_short_string(self):
        with self.assertRaises(ValueError) as cm:
            StringValidation('hi', minimum_length=3)
        self.assertIn("too short", str(cm.exception))

    def test_too_long_string(self):
        with self.assertRaises(ValueError) as cm:
            StringValidation('this is a long string', maximum_length=10)
        self.assertIn("too long", str(cm.exception))

    def test_regex_match(self):
        pattern = compile(r'^[a-z]+$')
        value = StringValidation('hello', regex=pattern)
        self.assertEqual(value, 'hello')

    def test_regex_no_match(self):
        pattern = compile(r'^[a-z]+$')
        with self.assertRaises(ValueError) as cm:
            StringValidation('Hello123', regex=pattern)
        self.assertIn("not match", str(cm.exception))

    def test_all_constraints_pass(self):
        pattern = compile(r'^[a-z]+$')
        value = StringValidation('hello', minimum_length=3, maximum_length=10, regex=pattern)
        self.assertEqual(value, 'hello')

    def test_all_constraints_fail(self):
        pattern = compile(r'^[a-z]+$')
        with self.assertRaises(ValueError) as cm:
            StringValidation('Hi', minimum_length=3, maximum_length=4, regex=pattern)
        self.assertTrue(
            any(msg in str(cm.exception) for msg in ["not match", "too short", "too long"])
        )


class TestIntegerValidation(unittest.TestCase):
    def test_valid_integer_no_constraints(self):
        # No constraints applied should return the number as-is.
        value = IntegerValidation(10)
        self.assertEqual(value, 10)

    def test_valid_integer_with_constraints(self):
        # Valid integer within the specified range.
        value = IntegerValidation(5, minimum=1, maximum=10)
        self.assertEqual(value, 5)

    def test_integer_below_minimum(self):
        # Should raise a ValueError because 0 is below the minimum of 1.
        with self.assertRaises(ValueError) as cm:
            IntegerValidation(0, minimum=1)
        self.assertIn("too small", str(cm.exception))

    def test_integer_above_maximum(self):
        # Should raise a ValueError because 11 is above the maximum of 10.
        with self.assertRaises(ValueError) as cm:
            IntegerValidation(11, maximum=10)
        self.assertIn("too big", str(cm.exception))


class TestFloatValidation(unittest.TestCase):
    def test_valid_float_no_constraints(self):
        # No constraints applied should return the float as-is.
        value = FloatValidation(3.14)
        self.assertEqual(value, 3.14)

    def test_valid_float_with_constraints(self):
        # Valid float within the specified range.
        value = FloatValidation(3.14, minimum=1.0, maximum=5.0)
        self.assertEqual(value, 3.14)

    def test_float_below_minimum(self):
        # Should raise a ValueError because 0.5 is below the minimum of 1.0.
        with self.assertRaises(ValueError) as cm:
            FloatValidation(0.5, minimum=1.0)
        self.assertIn("too small", str(cm.exception))

    def test_float_above_maximum(self):
        # Should raise a ValueError because 6.0 is above the maximum of 5.0.
        with self.assertRaises(ValueError) as cm:
            FloatValidation(6.0, maximum=5.0)
        self.assertIn("too big", str(cm.exception))


class TestDateValidation(unittest.TestCase):

    def test_valid_date_no_constraints(self):
        d = DateValidation(2024, 3, 28)
        self.assertEqual(d, date(2024, 3, 28))

    def test_valid_date_within_constraints(self):
        d = DateValidation(2024, 3, 28,
                           minimum_date=date(2024, 1, 1),
                           maximum_date=date(2024, 12, 31))
        self.assertEqual(d, date(2024, 3, 28))

    def test_date_equal_to_minimum(self):
        d = DateValidation(2024, 1, 1, minimum_date=date(2024, 1, 1))
        self.assertEqual(d, date(2024, 1, 1))

    def test_date_equal_to_maximum(self):
        d = DateValidation(2024, 12, 31, maximum_date=date(2024, 12, 31))
        self.assertEqual(d, date(2024, 12, 31))

    def test_date_below_minimum_raises(self):
        with self.assertRaises(ValueError) as context:
            DateValidation(2023, 12, 31, minimum_date=date(2024, 1, 1))
        self.assertIn("earlier than minimum allowed", str(context.exception))

    def test_date_above_maximum_raises(self):
        with self.assertRaises(ValueError) as context:
            DateValidation(2025, 1, 1, maximum_date=date(2024, 12, 31))
        self.assertIn("later than maximum allowed", str(context.exception))

    def test_invalid_date_raises(self):
        with self.assertRaises(ValueError):
            DateValidation(2024, 2, 30)  # Invalid day in February


class TestTimeValidation(unittest.TestCase):

    def test_valid_time_no_constraints(self):
        t = TimeValidation(12, 30)
        self.assertEqual(t, time(12, 30))

    def test_valid_time_within_constraints(self):
        t = TimeValidation(14, 45,
                           minimum_time=time(12, 0),
                           maximum_time=time(20, 0))
        self.assertEqual(t, time(14, 45))

    def test_time_equal_to_minimum(self):
        t = TimeValidation(8, 0, minimum_time=time(8, 0))
        self.assertEqual(t, time(8, 0))

    def test_time_equal_to_maximum(self):
        t = TimeValidation(22, 0, maximum_time=time(22, 0))
        self.assertEqual(t, time(22, 0))

    def test_time_below_minimum_raises(self):
        with self.assertRaises(ValueError) as context:
            TimeValidation(6, 59, minimum_time=time(7, 0))
        self.assertIn("earlier than minimum allowed", str(context.exception))

    def test_time_above_maximum_raises(self):
        with self.assertRaises(ValueError) as context:
            TimeValidation(23, 1, maximum_time=time(23, 0))
        self.assertIn("later than maximum allowed", str(context.exception))

    def test_time_with_seconds_and_microseconds(self):
        t = TimeValidation(10, 15, 30, 500000)
        self.assertEqual(t, time(10, 15, 30, 500000))

    def test_time_with_timezone(self):
        tz = time(0, 0).tzinfo  # no tzinfo set, just testing the arg
        t = TimeValidation(10, 0, 0, 0, tz)
        self.assertEqual(t, time(10, 0))

    def test_invalid_hour_raises(self):
        with self.assertRaises(ValueError):
            TimeValidation(25, 0)  # hour out of range

    def test_invalid_minute_raises(self):
        with self.assertRaises(ValueError):
            TimeValidation(12, 60)  # minute out of range


class TestDateTimeValidation(unittest.TestCase):

    def test_valid_datetime_no_constraints(self):
        dt = DateTimeValidation(2024, 3, 28, 15, 30)
        self.assertEqual(dt, datetime(2024, 3, 28, 15, 30))

    def test_valid_datetime_within_constraints(self):
        dt = DateTimeValidation(
            2024, 3, 28, 12, 0,
            minimum_datetime=datetime(2024, 3, 1, 0, 0),
            maximum_datetime=datetime(2024, 12, 31, 23, 59)
        )
        self.assertEqual(dt, datetime(2024, 3, 28, 12, 0))

    def test_datetime_equal_to_minimum(self):
        dt = DateTimeValidation(
            2024, 3, 1, 0, 0,
            minimum_datetime=datetime(2024, 3, 1, 0, 0)
        )
        self.assertEqual(dt, datetime(2024, 3, 1, 0, 0))

    def test_datetime_equal_to_maximum(self):
        dt = DateTimeValidation(
            2024, 12, 31, 23, 59,
            maximum_datetime=datetime(2024, 12, 31, 23, 59)
        )
        self.assertEqual(dt, datetime(2024, 12, 31, 23, 59))

    def test_datetime_below_minimum_raises(self):
        with self.assertRaises(ValueError) as context:
            DateTimeValidation(
                2024, 2, 29, 23, 59,
                minimum_datetime=datetime(2024, 3, 1)
            )
        self.assertIn("earlier than minimum allowed", str(context.exception))

    def test_datetime_above_maximum_raises(self):
        with self.assertRaises(ValueError) as context:
            DateTimeValidation(
                2025, 1, 1, 0, 0,
                maximum_datetime=datetime(2024, 12, 31, 23, 59)
            )
        self.assertIn("later than maximum allowed", str(context.exception))

    def test_datetime_with_seconds_and_microseconds(self):
        dt = DateTimeValidation(2024, 3, 28, 12, 45, 30, 999999)
        self.assertEqual(dt, datetime(2024, 3, 28, 12, 45, 30, 999999))

    def test_invalid_datetime_raises(self):
        with self.assertRaises(ValueError):
            DateTimeValidation(2024, 2, 30, 12, 0)  # Invalid date

    def test_timezone_argument_is_applied(self):
        tz = datetime.now().astimezone().tzinfo
        dt = DateTimeValidation(2024, 3, 28, 10, 0, 0, 0, tz)
        self.assertEqual(dt.tzinfo, tz)
