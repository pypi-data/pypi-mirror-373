import unittest
import json
import datetime
from enum import Enum
from pathlib import Path
from uuid import uuid4
from dataclasses import dataclass

from edri.utility.json_encoder import CustomJSONEncoder


class SampleEnum(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclass
class SampleData:
    name: str
    age: int


class HasToJson:
    def to_json(self):
        return {"custom": "serialized"}


class TestCustomJSONEncoder(unittest.TestCase):

    def test_to_json_method(self):
        obj = HasToJson()
        result = json.dumps(obj, cls=CustomJSONEncoder)
        self.assertEqual(result, '{"custom": "serialized"}')

    def test_datetime_serialization(self):
        dt = datetime.datetime(2024, 4, 1, 12, 30, 45)
        result = json.dumps(dt, cls=CustomJSONEncoder)
        self.assertEqual(result, f'"{dt.isoformat()}"')

    def test_path_serialization(self):
        path = Path("some/dir/file.txt")
        result = json.dumps(path, cls=CustomJSONEncoder)
        self.assertEqual(result, '"some/dir/file.txt"')

    def test_bytes_serialization(self):
        b = b"hello"
        result = json.dumps(b, cls=CustomJSONEncoder)
        self.assertEqual(result, f'"{b.hex()}"')

    def test_enum_serialization(self):
        color = SampleEnum.RED
        result = json.dumps(color, cls=CustomJSONEncoder)
        self.assertEqual(result, '"red"')

    def test_uuid_serialization(self):
        uid = uuid4()
        result = json.dumps(uid, cls=CustomJSONEncoder)
        self.assertEqual(result, f'"{str(uid)}"')

    def test_exception_serialization(self):
        try:
            raise ValueError("Invalid input")
        except ValueError as e:
            result = json.dumps(e, cls=CustomJSONEncoder)
            obj = json.loads(result)
            self.assertEqual(obj["type"], "ValueError")
            self.assertEqual(obj["message"], "Invalid input")
            self.assertEqual(obj["args"], ["Invalid input"])

    def test_dataclass_serialization(self):
        data = SampleData(name="Alice", age=30)
        result = json.dumps(data, cls=CustomJSONEncoder)
        self.assertEqual(json.loads(result), {"name": "Alice", "age": 30})

    def test_builtin_types_pass_through(self):
        obj = {"key": "value", "num": 42}
        result = json.dumps(obj, cls=CustomJSONEncoder)
        self.assertEqual(result, '{"key": "value", "num": 42}')

    def test_context_initialization(self):
        encoder = CustomJSONEncoder(context={"foo": "bar"})
        self.assertEqual(encoder.context, {"foo": "bar"})


if __name__ == '__main__':
    unittest.main()
