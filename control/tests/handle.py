import unittest
from ..bpdu import ConfigBPDU, Identifier
from ..spanningtree import PortData, PortRole
from .stubcontroller import StubSTPController

class UpdateConfigTest(unittest.TestCase):
    def test_update(self):
        a = ConfigBPDU(Identifier(23), 10, Identifier(45), 2)
        b = ConfigBPDU(Identifier(21), 10, Identifier(45), 2)
        c = ConfigBPDU(Identifier(20), 10, Identifier(45), 2)

        ctrl = StubSTPController(Identifier(0), [1])
        ctrl.initialize()

        ctrl.port_info[1].bpdu = a
        ctrl.port_info[1].update_config(b)
        self.assertEqual(ctrl.port_info[1].bpdu, b)
        ctrl.port_info[1].bpdu = c
        ctrl.port_info[1].update_config(a)
        self.assertEqual(ctrl.port_info[1].bpdu, c)

class PortAssignationTest(unittest.TestCase):
    def test_root_switch(self):
        ctrl = StubSTPController(Identifier(32768), [1, 2])
        ctrl.initialize()
        ctrl.port_assignation()
        self.assertEqual(ctrl.port_info[1].role, PortRole.DESIGNATED)
        self.assertEqual(ctrl.port_info[2].role, PortRole.DESIGNATED)

    def test_root_port(self):
        ctrl = StubSTPController(Identifier(32768), [1, 2])
        ctrl.initialize()
        
        config = ConfigBPDU(Identifier(0), 0, Identifier(0), 0)
        ctrl.port_info[1].update_config(config)
        ctrl.port_assignation()

        self.assertEqual(ctrl.port_info[1].role, PortRole.ROOT)
        self.assertEqual(ctrl.port_info[2].role, PortRole.DESIGNATED)

    def test_blocking_port(self):
        ctrl = StubSTPController(Identifier(32768), [1, 2])
        ctrl.initialize()
        
        config = ConfigBPDU(Identifier(0), 0, Identifier(0), 0)
        ctrl.port_info[1].update_config(config)

        config = ConfigBPDU(Identifier(0), 0, Identifier(12), 0)
        ctrl.port_info[2].update_config(config)

        ctrl.port_assignation()

        self.assertEqual(ctrl.port_info[1].role, PortRole.ROOT)
        self.assertEqual(ctrl.port_info[2].role, PortRole.BLOCKING)

class HandleTest(unittest.TestCase):
    def test_handle(self):
        ctrl = StubSTPController(Identifier(32768), [1, 2])
        ctrl.initialize()
        
        config = ConfigBPDU(Identifier(0), 0, Identifier(0), 0)
        
        ctrl.handle_bpdu(config, 1)

        self.assertEqual(ctrl.port_info[1].role, PortRole.ROOT)
        self.assertEqual(ctrl.port_info[2].role, PortRole.DESIGNATED)
