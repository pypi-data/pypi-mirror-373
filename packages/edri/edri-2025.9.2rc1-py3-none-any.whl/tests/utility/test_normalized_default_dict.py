import unittest
from edri.utility import NormalizedDefaultDict


class TestNormalizedDefaultDict(unittest.TestCase):

    def test_default_normalization(self):
        ndd = NormalizedDefaultDict()
        ndd['KeyOne'] = 'value1'
        ndd['KEYTWO'] = 'value2'

        self.assertEqual(ndd['keyone'], 'value1')
        self.assertEqual(ndd['keytwo'], 'value2')
        self.assertEqual(ndd['KEYONE'], 'value1')
        self.assertEqual(ndd['KeyTwo'], 'value2')

    def test_custom_normalization(self):
        def reverse_string(key: str) -> str:
            return key.upper()

        nd = NormalizedDefaultDict(normalization=reverse_string)
        nd['abc'] = 'value1'
        nd['def'] = 'value2'

        self.assertEqual(nd['ABC'], 'value1')
        self.assertEqual(nd['DeF'], 'value2')

    def test_update_method(self):
        nd = NormalizedDefaultDict()
        nd.update({'KeyOne': 'value1', 'KEYTWO': 'value2'})

        self.assertEqual(nd['keyone'], 'value1')
        self.assertEqual(nd['keytwo'], 'value2')

    def test_initialization_with_arguments(self):
        nd = NormalizedDefaultDict(int)
        nd['KeyOne'] += 1
        nd['KEYTWO'] += 2

        self.assertEqual(nd['keyone'], 1)
        self.assertEqual(nd['keytwo'], 2)

    def test_missing_key(self):
        nd = NormalizedDefaultDict()
        with self.assertRaises(KeyError):
            _ = nd['missingKey']

    def test_default_factory_behavior(self):
        nd = NormalizedDefaultDict(int)
        self.assertEqual(nd['keyone'], 0)
        nd['keytwo'] += 3
        self.assertEqual(nd['keytwo'], 3)

    def test_custom_normalization_with_update(self):
        def reverse_string(key: str) -> str:
            return key.upper()

        nd = NormalizedDefaultDict(normalization=reverse_string)
        nd.update({'abc': 'value1', 'DeF': 'value2'})

        self.assertEqual(nd['aBc'], 'value1')
        self.assertEqual(nd['def'], 'value2')

    def test_setitem_normalization(self):
        nd = NormalizedDefaultDict()
        nd['Key'] = 'value'
        nd['key'] = 'new_value'

        self.assertEqual(len(nd), 1)
        self.assertEqual(nd['key'], 'new_value')

    def test_getitem_normalization(self):
        nd = NormalizedDefaultDict()
        nd['Key'] = 'value'

        self.assertEqual(nd['key'], 'value')
        self.assertEqual(nd['KEY'], 'value')