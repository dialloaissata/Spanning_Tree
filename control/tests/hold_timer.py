import unittest
from ..bpdu import ConfigBPDU, Identifier
from .stubcontroller import StubSTPController

class HoldTimerTest(unittest.TestCase):
    def test_root(self):
        ctrl = StubSTPController(Identifier(0), [1, 2])
        ctrl.initialize()
        self.assertEqual(ctrl.hold_time, 1)
        self.assertEqual(ctrl.port_info[1].hold_timer_expiry, 1)
        self.assertEqual(ctrl.port_info[2].hold_timer_expiry, 1)

        ctrl.the_time = 3
        ctrl.tick()
        self.assertEqual(len(ctrl.emitted), 2)
        ctrl.the_time = 4
        ctrl.tick()
        self.assertEqual(len(ctrl.emitted), 2)