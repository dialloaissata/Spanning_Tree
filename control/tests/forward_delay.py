import unittest
from ..bpdu import ConfigBPDU, Identifier
from .stubcontroller import StubSTPController
from ..spanningtree import PortState

class ForwardDelayTest(unittest.TestCase):
    def test_forward_delay(self):
        ctrl = StubSTPController(Identifier(1), [1, 2])
        ctrl.initialize()
        self.assertEqual(ctrl.forward_delay, 15)
        self.assertEqual(ctrl.port_info[1].forward_delay_expiry, 15)
        self.assertEqual(ctrl.port_info[2].forward_delay_expiry, 15)

        self.assertEqual(ctrl.port_info[1].state, PortState.BLOCKING)

        ctrl.port_info[1].make_designated()
        ctrl.the_time = 16
        ctrl.tick()

        self.assertEqual(ctrl.port_info[1].state, PortState.LEARNING)
        ctrl.the_time = 32
        ctrl.tick()

        self.assertEqual(ctrl.port_info[1].state, PortState.FORWARDING)
