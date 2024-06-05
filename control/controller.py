from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from scapy.all import sniff, sendp, Ether, raw
import sys
import time
from threading import Thread
from time import sleep
from p4utils.utils.helper import NetworkGraph
import typing

from .bpdu import ConfigBPDU, Identifier
from .spanningtree import STPController, PortState, PortRole
from .mac import MAC

# wireshark pcap/s1-eth1_out.pcap -X lua_script:dissector.lua

class L2Controller(STPController):
    """
    Contrôleur STP pour un switch P4
    """
    def __init__(self, sw_name: str, topo: NetworkGraph):
        """
        Initialise le contrôleur

        :param sw_name: Nom du switch
        :param topo: Topologie du réseau
        """
        self.topo = topo
        self.sw_name = sw_name

        sw_addr: str = list(self.get_intf_data(['addr']).values())[0]
        
        id: Identifier = Identifier(32768, MAC(sw_addr))
        ports: typing.List[int] = list(self.get_intf_data().values())
        super().__init__(id, ports)

        self.thrift_port: int = self.topo.get_thrift_port(sw_name)
        self.cpu_port: int =  self.topo.get_cpu_port_index(self.sw_name)
        self.controller: SimpleSwitchThriftAPI = SimpleSwitchThriftAPI(self.thrift_port)

        self.t1 = None
        self.t2 = None

        self.log_bpdu = False
        self.log_port_change = False

    def init(self):
        """
        Initialise les états du contrôleur
        """
        self.controller.reset_state()
        self.add_mirror()
        self.initialize()
        self.init_mcast_groups()
        self.init_tables()

    def time(self):
        return time.time()

    def add_mirror(self):
        """
        Ajoute un mirroir. Il permet de cloner les paquets entrants
        vers le CPU
        """
        if self.cpu_port:
            self.controller.mirroring_add(100, self.cpu_port)

    def init_mcast_groups(self):
        """
        Initialise les groupes de multicast
        """
        for port_id in self.ports:
            self.controller.mc_mgrp_create(port_id)
            handle = self.controller.mc_node_create(port_id, [])
            self.controller.mc_node_associate(port_id, handle)
            self.port_info[port_id].custom_data["mcast_handle"] = handle

    def get_intf_data(self, fields=['port']):
        """
        Récupère les informations liés aux interfaces du switch
        """
        interfaces_to_port = self.topo.get_node_intfs(fields=fields)[self.sw_name].copy()
        interfaces_to_port.pop('lo', None)
        interfaces_to_port.pop(self.topo.get_cpu_port_intf(self.sw_name), None)
        return interfaces_to_port

    def get_mcast_ports_list(self, port_id):
        """
        Récupère la liste des ports présents dans un groupe multicast
        """
        ports = []

        for p in self.ports:
            if p != port_id and self.port_info[p].state == PortState.FORWARDING:
                ports.append(p)
        return ports

    def init_tables(self):
        """
        Initialise les match-action-table du switch
        """
        cpu_port = self.topo.get_cpu_port_index(self.sw_name)
        self.controller.table_add("send_to_control", "forward_to_cpu", [str(0x8042)], [str(cpu_port)])

        cpu_port = self.topo.get_cpu_port_index(self.sw_name)
        self.controller.table_add("handle_cpu", "handle_cpu_packet", [str(cpu_port)], [])

        for port_id in self.ports:
            self.port_info[port_id].custom_data["handle_cpu_handle"] = self.controller.table_add("handle_cpu", "NoAction", [str(port_id)], [])
            self.port_info[port_id].custom_data["dispatch_handle"] = self.controller.table_add("dispatch", "drop", [str(port_id)], [])

    def update_port_state(self, port_id: int, state: PortState, role: PortRole):
        """
        Mets à jour les match-action-table du switch en fonction de l'état d'un port

        :param port_id: ID du port
        :param state: Nouvel état du port
        :param rorle: Nouveau rôle du port
        """
        for port_no in self.ports:
            self.controller.mc_node_update(self.port_info[port_no].custom_data["mcast_handle"], self.get_mcast_ports_list(port_no))
        
        if self.log_port_change:
            print(self.sw_name, port_id, state, role, file=sys.stderr)
        
        if state == PortState.DISABLED:
            self.controller.table_modify("handle_cpu", "drop", self.port_info[port_id].custom_data["handle_cpu_handle"], [])
            self.controller.table_modify("dispatch", "NoAction", self.port_info[port_id].custom_data["dispatch_handle"], [])
        elif state in (PortState.BLOCKING, PortState.LISTENING, PortState.LEARNING):
            self.controller.table_modify("handle_cpu", "NoAction", self.port_info[port_id].custom_data["handle_cpu_handle"], [])
            self.controller.table_modify("dispatch", "drop", self.port_info[port_id].custom_data["dispatch_handle"], [])
        elif state == PortState.FORWARDING:
            self.controller.table_modify("handle_cpu", "NoAction", self.port_info[port_id].custom_data["handle_cpu_handle"], [])
            self.controller.table_modify("dispatch", "set_mcast_grp", self.port_info[port_id].custom_data["dispatch_handle"], [str(port_id)])

    def recv_msg_cpu(self, pkt):
        """
        Reçois un message sur le port CPU

        :param pkt: Paquet reçu
        """
        packet = Ether(raw(pkt))
        bpdu, port = ConfigBPDU.from_packet(packet)
        if bpdu != None:
            if self.log_bpdu:
                print(self.sw_name, port, bpdu, file=sys.stderr)
            self.handle_bpdu(bpdu, port)

    def send_bpdu(self, config: ConfigBPDU, port_id: int):
        """
        Envoi un BPDU sur le port CPU du switch

        :param config: BPDU à envoyer
        :param port_id: ID du port
        """
        cpu_port_intf = str(self.topo.get_cpu_port_intf(self.sw_name).replace("eth0", "eth1"))
        sendp(config.to_cpu_packet(str(self.bridge_id.mac), port_id), iface=cpu_port_intf, verbose=False)

    def run_cpu_port_loop(self):
        """
        Démarre la boucle d'écoute sur le port CPU
        """
        cpu_port_intf = str(self.topo.get_cpu_port_intf(self.sw_name).replace("eth0", "eth1"))
        while not self.must_stop:
            sniff(iface=cpu_port_intf, filter="inbound", timeout=2, prn=self.recv_msg_cpu)

    def run_broadcast_loop(self):
        """
        Démarre la boucle d'émission des BPDU
        """
        while not self.must_stop:
            sleep(1)
            self.tick()

    def loop(self):
        """
        Démarre les deux boucles dans deux threads différents
        """
        self.must_stop = False
        t2 = Thread(target=self.run_broadcast_loop)
        t2.start()
        self.t2 = t2
        t1 = Thread(target=self.run_cpu_port_loop)
        t1.start()
        self.t1 = t1

    def stop(self):
        """
        Demande au contrôleur de s'arrêter
        """
        self.must_stop = True

    def join(self):
        """
        Join les deux threads du contrôleur
        """
        if self.t1 != None:
            self.t1.join()
        if self.t2 != None:
            self.t2.join()
