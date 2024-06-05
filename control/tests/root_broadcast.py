import unittest
from ..bpdu import ConfigBPDU, Identifier
from .stubcontroller import StubSTPController

class RootBroadcastTest(unittest.TestCase):
    def test_root(self):
        ctrl = StubSTPController(Identifier(0), [1, 2])
        ctrl.initialize()
        ctrl.port_info[1].path_cost = 1
        ctrl.port_info[2].path_cost = 1
        ctrl.the_time = 5
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

    def test_not_root(self):
        ctrl = StubSTPController(Identifier(1), [1, 2])
        ctrl.initialize()
        ctrl.port_info[1].path_cost = 1
        ctrl.port_info[2].path_cost = 1
        ctrl.port_info[1].update_config(ConfigBPDU(Identifier(0), 1, Identifier(0), 1))
        ctrl.tick()
        self.assertEqual(len(ctrl.emitted), 0)

class HandleBroadcastTest(unittest.TestCase):
    def test_handle_root_port(self):
        ctrl = StubSTPController(Identifier(1), [1, 2])
        ctrl.initialize()
        ctrl.port_info[1].path_cost = 1
        ctrl.port_info[2].path_cost = 1
        ctrl.port_info[1].update_config(ConfigBPDU(Identifier(0), 1, Identifier(0), 1))
        ctrl.port_assignation()
        ctrl.the_time = 5
        ctrl.handle_bpdu(ConfigBPDU(Identifier(2), 1, Identifier(0), 1), 1)
        self.assertEqual(len(ctrl.emitted), 2)

        self.assertIn((1, ConfigBPDU(
            Identifier(0),
            2,
            Identifier(1),
            1
        )), ctrl.emitted)
        self.assertIn((2, ConfigBPDU(
            Identifier(0),
            2,
            Identifier(1),
            2
        )), ctrl.emitted)

    def test_handle_other_port(self):
        ctrl = StubSTPController(Identifier(1), [1, 2])
        ctrl.initialize()
        ctrl.port_info[1].path_cost = 1
        ctrl.port_info[2].path_cost = 1
        ctrl.port_info[1].update_config(ConfigBPDU(Identifier(0), 1, Identifier(0), 1))

        ctrl.handle_bpdu(ConfigBPDU(Identifier(2), 1, Identifier(0), 1), 2)
        self.assertEqual(len(ctrl.emitted), 0)
