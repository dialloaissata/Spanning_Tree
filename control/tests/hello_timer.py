import unittest
from ..bpdu import ConfigBPDU, Identifier
from .stubcontroller import StubSTPController

class HelloTimerTest(unittest.TestCase):
    def test_root(self):
        ctrl = StubSTPController(Identifier(0), [1, 2])
        ctrl.initialize()
        self.assertEqual(ctrl.hello_time, 2)
        self.assertEqual(ctrl.hello_timer_expiry, 2)

        ctrl.tick()
        self.assertEqual(len(ctrl.emitted), 0)
        ctrl.the_time = 3
        ctrl.tick()
        self.assertEqual(len(ctrl.emitted), 2)
        self.assertIn((1, ConfigBPDU(
            Identifier(0),
            1,
            Identifier(0),
            1
        )), ctrl.emitted)
        self.assertIn((2, ConfigBPDU(
            Identifier(0),
            1,
            Identifier(0),
            2
        )), ctrl.emitted)
        self.assertEqual(ctrl.hello_timer_expiry, 5)
        ctrl.tick()
        self.assertEqual(len(ctrl.emitted), 2)
