
from ..spanningtree import STPController, PortRole, PortState
from ..bpdu import ConfigBPDU

class StubSTPController(STPController):
    def __init__(self, bridge_id, ports):
        self.emitted = []
        self.the_time = 0

        super().__init__(bridge_id, ports)

    def send_bpdu(self, config: ConfigBPDU, port_id: int):
        self.emitted.append((port_id, config))

    def update_port_state(self, port_id: int, state: PortState, role: PortRole):
        pass

    def stub_reset(self):
        self.emitted = []
        self.the_time = 0
    
    def time(self):
        return self.the_time
