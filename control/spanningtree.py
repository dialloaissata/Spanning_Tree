
from .bpdu import Identifier, ConfigBPDU
import typing
from enum import Enum
import sys

No_port = None

class PortState(Enum):
    """
    Énumération représentant les états d'un port
    """
    BLOCKING = 0,
    LISTENING = 1,
    LEARNING = 2,
    FORWARDING = 3,
    DISABLED = 4

class PortRole(Enum):
    """
    Énumération représentant les rôles d'un port
    """
    ROOT = 0,
    DESIGNATED = 1,
    BLOCKING = 2,
    DISABLED = 3

class PortData:
    """
    Données nécessaires au fonctionnement de STP, stocké par port
    """
    def __init__(self, ctrl, port_id: int, path_cost: int):
        """
        Initialise le port

        :param ctrl: Contrôleur STP
        :param port_id: ID du port
        :param path_cost: Coût de la traversée de ce port
        """
        self.ctrl = ctrl
        self.port_id = port_id
        self.path_cost = path_cost
        self.custom_data = {}

    def initialize(self):
        """
        Initialise les états du port
        """
        # TODO: Question 29
        #self.state: PortState = PortState.FORWARDING
        self.state: PortState = PortState.BLOCKING # Initialise l'état par défaut du port à Blocking
        self.role: PortRole = PortRole.DESIGNATED
        self.bpdu: ConfigBPDU = ConfigBPDU(self.ctrl.bridge_id, self.path_cost, self.ctrl.bridge_id, self.port_id)

        # TODO: Question 18
        # Initialisation de hold_timer_expiry
        self.hold_timer_expiry = self.ctrl.time() + self.ctrl.hold_time


        # TODO: Question 21
        # Initialisation de message_age_expiry
        self.message_age_expiry = self.ctrl.time() + self.ctrl.message_age


        # TODO: Question 26
        # Initialise le temporisateur forward delay
        self.forward_delay_expiry = self.ctrl.time() + self.ctrl.forward_delay

    def can_send(self):
        """
        Détemrine si le port est capable d'envoyer un BPDU ou non
        """
        if self.disabled() or self.blocking():
            return False
    
        # TODO: Question 19
        # Vérifier si le hold timer est expiré
        if self.ctrl.time() >= self.hold_timer_expiry:
            # Réinitialiser le temporisateur
            self.hold_timer_expiry = self.ctrl.time() + self.ctrl.hold_time
            return True
        else:
            return False


    def enable(self):
        """
        Active le port
        """
        self.initialize()

    def disable(self):
        """
        Désactive le port
        """
        self.make_designated()
        self.update_state(PortState.DISABLED, PortRole.DISABLED)

    def disabled(self):
        """
        Vérifie si le port est désactivé
        """
        return self.role == PortRole.DISABLED
    
    def blocking(self):
        """
        Vérifie si le port est bloqué
        """
        return self.role == PortRole.BLOCKING

    def update_config(self, config: ConfigBPDU):
        """
        Mets à jour la configuration du port à partir d'un BPDU entrant

        :param config: BPDU à partir duquel il faut appliquer la configuration
        """

        # TODO: Question 4
        #si le bpdu reçu est meilleur que celui qui est stocké, on le garde et on recalcule les états/rôles des ports
        if config < self.bpdu:
            self.bpdu = config
            self.ctrl.port_assignation()
                
        # TODO: Question 22
        # Réinitialisation du temporisateur "message age"
        self.message_age_expiry = self.ctrl.time() + self.ctrl.message_age
        # Effectuer l'assignation des ports après cette réinitialisation
        self.ctrl.port_assignation()
        

    def do_forward(self):
        """
        Change l'état du port en fonction de son état actuel et de l'expiration de son timer forward_delay
        """
        # TODO: Question 27
        # Vérifie si le temporisateur forward_delay a expiré
        if self.ctrl.time() >= self.forward_delay_expiry:
            if self.state == PortState.LISTENING:
                self.update_state(PortState.LEARNING, PortRole.DESIGNATED)
            elif self.state == PortState.LEARNING:
                self.update_state(PortState.FORWARDING, PortRole.DESIGNATED)
            # Réinitialise le temporisateur forward_delay
            self.forward_delay_expiry = self.ctrl.time() + self.ctrl.forward_delay


    def update_state(self, state: PortState, role: PortRole):
        """
        Mets à jour l'état et le rôle du port

        :param state: Nouvel état du port
        :param role: Nouveau rôle du port
        """
        self.state = state
        self.role = role

        # TODO: Question 23
        # Réinitialisation du temporisateur "message age"
        self.message_age_expiry = self.ctrl.time() + self.ctrl.message_age
        self.ctrl.update_port_state(self.port_id, self.state, self.role)

    def make_blocking(self):
        """
        Marque le port comme port bloquant
        """
        if self.disabled():
            return
        if self.state == PortState.BLOCKING and self.role == PortRole.BLOCKING:
            return
        self.update_state(PortState.BLOCKING, PortRole.BLOCKING)

    def make_root(self):
        """
        Marque le port comme port racine
        """
        if self.disabled():
            return
        if self.role == PortRole.ROOT and self.state != PortState.BLOCKING:
            return
        self.update_state(PortState.FORWARDING, PortRole.ROOT)

    def make_designated(self):
        """
        Marque le port comme port designé
        """
        if self.disabled():
            return
        if self.role == PortRole.DESIGNATED and self.state != PortState.BLOCKING:
            return
        self.update_state(PortState.LISTENING, PortRole.DESIGNATED)



class STPController:
    """
    Contrôleur pour switch STP
    """
    def __init__(self, bridge_id: Identifier, ports: typing.List[int]):
        """
        Initialise le contrôleur

        :param bridge_id: Identifiant du switch
        :param ports: Liste des ports du switch
        """
        self.bridge_id = bridge_id
        self.ports = ports
        self.port_info: typing.Dict[int, PortData] = {}

        # TODO: Question 13
        # Initialisation la durée des temporisateurs
        self.timer_values = {
            "message_age": 20,
            "forward_delay": 15,
            "hold_timer": 1,
            "hello_timer": 2
        }
        # Initialisation des temporisateurs individuellement
        self.message_age = self.timer_values["message_age"]
        self.forward_delay = self.timer_values["forward_delay"]
        self.hold_time = self.timer_values["hold_timer"]
        self.hello_time = self.timer_values["hello_timer"]

        # TODO: Question 14
        # Initialisation de hello_timer_expiry
        self.hello_timer_expiry = self.time() + self.hello_time

    
    def initialize(self):
        """
        Initialise les états des ports du switch
        """
        for port_id in self.ports:
            self.port_info[port_id] = PortData(self, port_id, 1)
            self.port_info[port_id].initialize()
    
    def get_best_bpdu(self):
        """
        Renvoi le meilleur BPDU
        """
        return min(map(lambda x: x.bpdu, self.port_info.values()))

    def get_root_port(self) -> PortData:
        """
        Récupère le port racine
        """
        if self.get_best_bpdu().root_id == self.bridge_id:
            return None
        return min(self.port_info.values(), key=lambda x: x.bpdu)

    def transmit_config(self, port_id: int):
        """
        Transmet la configuration pour le port port_id

        :param port_id: Identifiant du port
        """

        port = self.port_info[port_id]
        if not port.can_send():
            return
        # TODO: Question 7
        else:
            if self.bridge_id == self.get_best_bpdu().root_id:
                # Si le switch est le pont racine
                best_bpdu = self.get_best_bpdu()
                bpdu_to_transmit = ConfigBPDU(
                    root_id=self.bridge_id,  # L'identifiant du pont local est utilisé comme identifiant du pont racine sur le port local
                    root_cost= best_bpdu.root_cost,  # Coût nul pour le port local
                    bridge_id=self.bridge_id,  # L'identifiant du pont local est utilisé comme identifiant du pont émetteur
                    port_id=port_id  # Identifiant du port
                )
            else:
                # Si le switch n'est pas le pont racine
                best_bpdu = self.get_best_bpdu()
                bpdu_to_transmit = ConfigBPDU(
                    root_id=best_bpdu.root_id,
                    root_cost=best_bpdu.root_cost + port.path_cost,
                    bridge_id=self.bridge_id,
                    port_id=port_id
                )
            # Utiliser la méthode send_bpdu pour envoyer le BPDU sur le port
            self.send_bpdu(bpdu_to_transmit, port_id)        


    def broadcast_config(self):
        """
        Transmet un BPDU sur tous les ports
        """

        # TODO: Question 7
        #Récupérer le meilleur BPDU actuel
        best_bpdu = self.get_best_bpdu()
        # Transmettre le BPDU sur tous les ports
        for port_id, port in self.port_info.items():
            # Construire le BPDU à transmettre sur ce port
            bpdu_to_transmit = ConfigBPDU(root_id=best_bpdu.root_id, root_cost=best_bpdu.root_cost, bridge_id=self.bridge_id, port_id=port_id)
            # Mettre à jour le BPDU stocké sur le port avec le BPDU à transmettre
            #port.update_config(bpdu_to_transmit)
            self.send_bpdu(bpdu_to_transmit, port_id)
        # TODO: Question 15
        # Vérifier si le hello timer est expiré
        current_time = self.time()
        if current_time >= self.hello_timer_expiry:
            # Réinitialiser la valeur de hello_timer_expiry
            self.hello_timer_expiry = current_time + self.hello_time

    def handle_bpdu(self, bpdu: ConfigBPDU, port_id: int):
        """
        Traîte un BPDU
        """
        # TODO: Question 11
        port = self.port_info[port_id] # Récupère les informations du port spécifié par port_id 
        for port_info in self.port_info.values():
            self.transmit_config(port_info.port_id)
        port.update_config(bpdu)        # Mets à jour la configuration du port à partir d'un BPDU entrant
        self.port_assignation()         # Calcule l'assignement des rôle et états des ports

    def port_assignation(self):
        """
        Calcule l'assignement des rôle et états des ports
        """
        # TODO: Question 5
        best_bpdu = self.get_best_bpdu()  # Obtenir le meilleur BPDU
        root_port = self.get_root_port()  # Obtenir le port racine du switch
        # Si le commutateur est la racine du réseau
        if self.bridge_id == best_bpdu.root_id:
            for port_id, port in self.port_info.items():
                # Générer un BPDU qui correspond à ce que le commutateur enverrait sur ce port
                temp_bpdu = ConfigBPDU(root_id=self.bridge_id, root_cost=0, bridge_id=self.bridge_id, port_id=port_id)
                # Si ce BPDU est meilleur ou égal au BPDU stocké pour le port, le port devient désigné, sinon le port devient bloqué
                if temp_bpdu < port.bpdu:
                    port.update_state(state=PortState.FORWARDING, role=PortRole.DESIGNATED)
                else:
                    port.update_state(state=PortState.BLOCKING, role=PortRole.BLOCKING)
        else:
            for port_id, port in self.port_info.items():
                if port_id == root_port.port_id:
                    port.update_state(state=PortState.FORWARDING, role=PortRole.ROOT)
                else:
                    # Générer un BPDU qui correspond à ce que le commutateur enverrait sur ce port
                    temp_bpdu = ConfigBPDU(root_id=root_port.bpdu.root_id, root_cost=root_port.bpdu.root_cost,
                                        bridge_id=self.bridge_id, port_id=port_id)
                    # Si ce BPDU est meilleur que le BPDU stocké pour le port, le port devient désigné, sinon le port devient bloqué
                    if temp_bpdu < port.bpdu:
                        port.update_state(state=PortState.FORWARDING, role=PortRole.DESIGNATED)
                    else:
                        port.update_state(state=PortState.BLOCKING, role=PortRole.BLOCKING)

    def tick(self):
        """
        Fonction appelée régulièrement pour faire fonctionner STP
        """

        # TODO: Question 11
        best_bpdu = self.get_best_bpdu()  # Obtenir le meilleur BPDU
        root_port = self.get_root_port()  # Obtenir le port racine du switch 
        # Si le commutateur est la racine du réseau, émettre les BPDU sur tous les ports
        if self.bridge_id == best_bpdu.root_id:
            # TODO: Question 16
            if self.time() >= self.hello_timer_expiry:
                self.broadcast_config()
                self.hello_timer_expiry = self.time() + self.hello_time
        else:
            # Transmettre le BPDU reçu sur le port racine
            if root_port:
                self.transmit_config(root_port.port_id)
        # Réinitialiser la valeur du hello timer_expiry
        for port_id in self.ports:
            port = self.port_info[port_id]
            # TODO: Question 28
            # Forward delay
            if self.time() >= port.forward_delay_expiry:
                if port.state == PortState.LISTENING:
                    port.update_state(PortState.LEARNING, PortRole.DESIGNATED)
                elif port.state == PortState.LEARNING:
                    port.update_state(PortState.FORWARDING, PortRole.DESIGNATED)
                port.forward_delay_expiry = self.time() + self.forward_delay  # Réinitialiser le forward delay timer
            # TODO: Question 24
            # Message age
            if self.time() >= port.message_age_expiry:
                port.bpdu = ConfigBPDU(self.bridge_id, 0, self.bridge_id, port_id)  # Réinitialiser le BPDU stocké dans le port                
                port.make_designated()  # Définir le rôle du port comme désigné
                port.update_state(PortState.LISTENING, PortRole.DESIGNATED)  # Définir l'état du port comme Listening
                port.message_age_expiry = self.time() + self.message_age  # Réinitialiser le message age timer
            # Hold timer
            if self.time() >= port.hold_timer_expiry:
                if port.can_send():
                    port.hold_timer_expiry = self.time() + self.hold_time

            
    def enable_port(self, port_no: int):
        """
        Active un port

        :param port_no: Port à activer
        """
        self.port_info[port_no].enable()
        self.port_assignation()

    def disable_port(self, port_no: int):
        """
        Désactive un port

        :param port_no: Port à désactiver
        """
        self.port_info[port_no].disable()
        self.port_assignation()

    def set_bridge_priority(self, priority: int):
        """
        Change la priorité du switch

        :param priority: Nouvelle priorité
        """
        self.bridge_id.priority = priority

        for port_id in self.ports:
            port = self.port_info[port_id]
            port.bpdu.root_id = self.bridge_id
            port.make_designated()
        self.port_assignation()

    def set_port_cost(self, port_no: int, cost: int):
        """
        Change le coût d'un port

        :param port_no: Port
        :param cost: Nouveau coût du port
        """
        self.port_info[port_no].path_cost = cost
        self.port_assignation()

    def print_debug(self, f):
        print(" === " + self.sw_name + " - " + str(self.bridge_id) + " === ", file=f)
        print(" Best BPDU: " + str(self.get_best_bpdu()), file=f)
        for port_id in self.ports:
            port = self.port_info[port_id]
            print("  - Port " + str(port_id) + ", role: " + str(port.role) + ", state: " + str(port.state), file=f)
            print("    bpdu: " + str(port.bpdu), file=f)

    # MÉTHODES ABSTRAITES
    def send_bpdu(self, config: ConfigBPDU, port_id: int):
        """
        Envoi un BPDU

        :param config: BPDU à envoyer
        :param port_id: Port sur lequel envoyer le BPDU
        """
        raise NotImplementedError()
    
    def update_port_state(self, port_id: int, state: PortState, role: PortRole):
        """
        Mets à jour l'état et le rôle d'un port dans le switch

        :param port_id: Port à mettre à jour
        :param state: Nouvel état du port
        :param role: Nouveau rôle du port
        """
        raise NotImplementedError()

    def time(self):
        raise NotImplementedError()


