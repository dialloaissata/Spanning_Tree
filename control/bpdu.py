
from scapy.all import Ether
from .packets import BPDU as BPDUPacket, CPUPacket

from .mac import MAC

class Identifier:
    """
    Classe représentant un identifiant de commutateur dans un BPDU (IEEE 802.1D - 8.5.1.4)
    """
    def __init__(self, priority: int = 32768, mac: MAC = MAC(0)):
        """
        Construit un identifiant

        :param priority: Priorité du commutateur
        :param mac: Adresse MAC du commutateur
        """
        self.priority = priority
        self.mac = mac

    @staticmethod
    def from_long(value: int):
        """
        Convertie un entier en identifiant

        :param value: Valeur à convertire
        :returns: Identifiant correspondant
        """
        prio = (value >> 48) & 0xFFFF
        mac = MAC(value & 0xFFFFFFFFFFFF)
        return Identifier(prio, mac)

    def __int__(self) -> int:
        """
        Renvoie une représentation entière de l'identifiant
        """
        return self.priority << 48 | int(self.mac)

    def __str__(self) -> str:
        """
        Renvoi une représentation en chaîne de caractère de l'identifiant
        """
        return str(self.priority) + "." + str(self.mac)

    def __repr__(self) -> str:
        """
        Renvoi une représentation de l'instance
        """
        return "<Identifier; Priority: " + str(self.priority) + ", MAC: " + repr(self.mac) + ">"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Identifier):
            return False
        return int(self) == int(other)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Identifier):
            raise TypeError()
        return int(self) < int(other)

    def __le__(self, other) -> bool:
        if not isinstance(other, Identifier):
            raise TypeError()
        return int(self) <= int(other)

class ConfigBPDU():
    """
    Classe représentant un BPDU
    """
    def __init__(self, root_id: Identifier = Identifier(), root_cost=0,
                 bridge_id: Identifier = Identifier(), port_id=0):
        """
        Iniialise le BPDU

        :param root_id: Identifiant du switch racine
        :param root_cost: Coût à la racine du switch
        :param bridge_id: Identifiant du switch
        :param port_id: Identifiant du port
        """
        self.root_id = root_id
        self.root_cost = root_cost
        self.bridge_id = bridge_id
        self.port_id = port_id

    @staticmethod
    def from_packet(packet):
        """
        Convertie un paquet en BPDU
        """
        if BPDUPacket in packet and CPUPacket in packet and packet.dst == '01:81:c2:00:00:00':
            bpdu = packet[BPDUPacket]
            port = packet[CPUPacket].out_port

            return ConfigBPDU(
                root_id=Identifier.from_long(bpdu.root_id), root_cost=bpdu.root_cost,
                bridge_id=Identifier.from_long(bpdu.bridge_id), port_id=bpdu.port_id
            ), port
        else:
            return None, None

    def to_cpu_packet(self, addr: MAC, port: int):
        """
        Convertie un BPDU en paquet

        :param addr: Adresse à utiliser comme source dans la trame Ethernet
        :param port: Port à utiliser comme out_port dans les infos CPU
        """
        return Ether(
            src=str(addr),
            dst='01:81:C2:00:00:00'
        ) / CPUPacket(
            out_port=port
        ) / BPDUPacket(
            root_id = int(self.root_id),
            root_cost = self.root_cost,
            bridge_id = int(self.bridge_id),
            port_id = self.port_id
        )
    
    def __eq__(self, other):
        if not isinstance(other, ConfigBPDU):
            return False
        
        return (self.root_id == other.root_id and self.root_cost == other.root_cost and
                self.bridge_id == other.bridge_id and self.port_id == other.port_id)

    def __lt__(self, other):
        if not isinstance(other, ConfigBPDU):
            raise TypeError()

        if self.root_id != other.root_id:
            return self.root_id < other.root_id
        elif self.root_cost != other.root_cost:
            return self.root_cost < other.root_cost
        elif self.bridge_id != other.bridge_id:
            return self.bridge_id < other.bridge_id
        else:
            return self.port_id < other.port_id
    
    def __repr__(self):
        return '<BPDU; root: {}, cost: {}, bridge: {}, port: {}>'.format(
            repr(self.root_id), self.root_cost, repr(self.bridge_id), self.port_id)

    def __str__(self):
        return 'Config BPDU ({}-{}-{}-{})'.format(str(self.root_id), self.root_cost, str(self.bridge_id), self.port_id)

    def winner(self, other):
        if not isinstance(other, ConfigBPDU):
            raise TypeError()

        return self if self < other else other
