import unittest
from ..bpdu import ConfigBPDU, Identifier
from .stubcontroller import StubSTPController

class TransmitTest(unittest.TestCase):
    def test_disabled(self):
        ctrl = StubSTPController(Identifier(0), [1])
        ctrl.initialize()
        ctrl.port_info[1].disable()
        ctrl.transmit_config(1)
        self.assertEqual(len(ctrl.emitted), 0)

    def test_root(self):
        ctrl = StubSTPController(Identifier(0), [1, 2])
        ctrl.initialize()
        ctrl.port_info[1].path_cost = 1
        ctrl.port_info[2].path_cost = 1
        ctrl.the_time = 3
        ctrl.transmit_config(1)
        self.assertEqual(len(ctrl.emitted), 1)
        self.assertEqual(ctrl.emitted[0], (1,
            ConfigBPDU(
            Identifier(0),
            1,
            Identifier(0),
            1
        )))

    def test_not_root(self):
        ctrl = StubSTPController(Identifier(1), [1, 2])
        ctrl.initialize()

        ctrl.port_info[1].update_config(ConfigBPDU(
            Identifier(0),
            1,
            Identifier(0),
            1
        ))

        ctrl.port_info[1].path_cost = 1
        ctrl.port_info[2].path_cost = 3
        ctrl.the_time = 3
        ctrl.transmit_config(2)
        self.assertEqual(len(ctrl.emitted), 1)
        self.assertEqual(ctrl.emitted[0], (2,
            ConfigBPDU(
            Identifier(0),
            4,
            Identifier(1),
            2
        )))

    def test_broadcast(self):
        ctrl = StubSTPController(Identifier(0), [1, 2])
        ctrl.initialize()
        ctrl.port_info[1].path_cost = 1
        ctrl.port_info[2].path_cost = 1
        ctrl.the_time = 3
        ctrl.broadcast_config()
        self.assertEqual(len(ctrl.emitted), 2)
        self.assertIn((1,
            ConfigBPDU(
            Identifier(0),
            1,
            Identifier(0),
            1
        )), ctrl.emitted)
        self.assertIn((2,
            ConfigBPDU(
            Identifier(0),
            1,
            Identifier(0),
            2
        )), ctrl.emitted)

