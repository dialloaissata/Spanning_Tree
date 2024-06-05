
from scapy.all import Ether, Packet, MACField, ByteEnumField, ShortField, IntField, ByteField, bind_layers, ConditionalField, LongField

class BPDU(Packet):
    """
    Paquet contenant un BPDU
    """
    name = 'BPDU '
    fields_desc = [
        LongField('root_id', 0),
        IntField('root_cost', 0),
        LongField('bridge_id', 0),
        ShortField('port_id', 0)
    ]

class CPUPacket(Packet):
    """
    Paquet contenant des métadonnées à transmettre à/de la couche données
    """
    name = 'CPUPacket '
    fields_desc = [
        ShortField('out_port', 0),
        ShortField('type', 0)
    ]

bind_layers(Ether, BPDU, type=0x8042)
bind_layers(Ether, CPUPacket, type=0x8043)
bind_layers(CPUPacket, BPDU, type=0x8042)
