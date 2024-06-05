import unittest
from ..bpdu import ConfigBPDU, Identifier

class CompareTest(unittest.TestCase):
    def test_eq(self):
        a = ConfigBPDU(Identifier(23), 10, Identifier(45), 2)
        b = ConfigBPDU(Identifier(23), 10, Identifier(45), 2)
        c = ConfigBPDU(Identifier(21), 2, Identifier(10), 1)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, None)
        self.assertNotEqual(a, 1)

    def test_lt(self):
        a = ConfigBPDU(Identifier(23), 10, Identifier(45), 2)
        b = ConfigBPDU(Identifier(21), 2, Identifier(10), 1)
        self.assertLess(b, a)
        self.assertGreater(a, b)

        with self.assertRaises(TypeError):
            _ = a < None
