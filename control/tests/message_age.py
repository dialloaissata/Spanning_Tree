import unittest
from ..bpdu import ConfigBPDU, Identifier
from .stubcontroller import StubSTPController

class MessageAgeTest(unittest.TestCase):
    def test_message_age(self):
        ctrl = StubSTPController(Identifier(1), [1, 2])
        ctrl.initialize()
        self.assertEqual(ctrl.message_age, 20)
        self.assertEqual(ctrl.port_info[1].message_age_expiry, 20)
        self.assertEqual(ctrl.port_info[2].message_age_expiry, 20)

        ctrl.handle_bpdu(ConfigBPDU(Identifier(0), 1, Identifier(0), 1), 1)
        ctrl.tick()
        self.assertEqual(ctrl.port_info[1].bpdu, ConfigBPDU(Identifier(0), 1, Identifier(0), 1))
        ctrl.the_time = 25
        ctrl.tick()
        self.assertEqual(ctrl.port_info[1].bpdu, ConfigBPDU(Identifier(1), 0, Identifier(1), 1))
