
import os
import sys
from p4utils.utils.helper import load_topo, NetworkGraph
from .controller import L2Controller
import typing
from .graph import draw_graph
from threading import Thread
import time
import traceback

def mute_stdout():
    """
    Remplace la sortie standard par /dev/null
    """
    f = open(os.devnull, 'w')
    sys.stdout = f
    
class CLI:
    """
    Classe gérant l'interface en ligne de commande
    """
    def __init__(self):
        """
        Initialise la CLI
        """
        self.topo: NetworkGraph = load_topo('topology.json')
        self.controllers: typing.Dict[str, L2Controller] = {}
        self.graph_pos = None
        self.draw_thread = None
        self.commands = {
            "reset": self.command_reset,
            "start": self.command_start,
            "stop": self.command_stop,
            "quit": self.command_quit,
            "info": self.command_info,
            "draw": self.command_draw,
            "priority": self.command_priority,
            "port": self.command_port,
            "cost": self.command_cost,
            "log": self.command_log,
        }

    def init_controllers(self):
        """
        Initialise les contrôleurs
        """
        for sw in self.topo.get_p4switches().keys():
            controller = L2Controller(sw, self.topo)
            controller.init()
            self.controllers[sw] = controller

    def command_reset(self):
        """
        Arête les contrôleurs et les réinitialise
        """
        self.command_stop()
        self.init_controllers()

    def command_start(self):
        """
        Démarre les contrôleurs
        """
        for controller in self.controllers.values():
            controller.loop()

    def command_stop(self):
        """
        Arête les contrôleurs
        """
        for controller in self.controllers.values():
            controller.stop()
        for controller in self.controllers.values():
            controller.join()

    def command_quit(self):
        """
        Arête les contrôleurs et quitte le programme
        """
        self.command_draw("stop")
        self.command_stop()
        sys.exit(0)

    def command_info(self, which="*"):
        """
        Affiche des infos sur le/les contrôleurs

        :param which: Contrôleur duquel afficher les informations
        """
        if which == "*":
            for controller in self.controllers.values():
                controller.print_debug(sys.stderr)
        else:
            self.controllers[which].print_debug(sys.stderr)
    
    def draw_func(self):
        """
        Dessine le graph
        """
        self.must_stop_drawing = False
        while not self.must_stop_drawing:
            draw_graph(self.topo, self.controllers, self.graph_pos)
            time.sleep(0.5)

    def command_draw(self, action=None):
        """
        Gère l'affichage du graphe

        :param action: Action à effectuer
        """
        if action == None or action == "once":
            draw_graph(self.topo, self.controllers, self.graph_pos)
        elif action == "start":
            self.draw_thread = Thread(target=self.draw_func)
            self.draw_thread.start()
        elif action == "stop":
            self.must_stop_drawing = True
            if self.draw_thread != None:
                self.draw_thread.join()
        elif action == "init":
            self.graph_pos = draw_graph(self.topo, self.controllers)

    def command_priority(self, bridge, prio):
        """
        Définie la priorité d'un switch

        :param bridge: Nom du switch
        :param prio: Nouvelle priorité du switch
        """
        priority = int(prio)
        self.controllers[bridge].set_bridge_priority(priority)

    def command_port(self, bridge, port, state):
        """
        Active ou désactive un port

        :param bridge: Nom du switch
        :param port: ID du port
        :param state: État (enable / disable)
        """
        if port == '*':
            for port in self.controllers[bridge].ports:
                if state== "enable":
                    self.controllers[bridge].enable_port(port)
                elif state == "disable":
                    self.controllers[bridge].disable_port(port)
        else:
            port = int(port)
            if state== "enable":
                self.controllers[bridge].enable_port(port)
            elif state == "disable":
                self.controllers[bridge].disable_port(port)

    def command_cost(self, bridge, port, cost):
        """
        Définie le coût d'un port

        :param bridge: Nom du switch
        :param port: ID du port
        :param cost: Nouveau coût du port
        """
        port = int(port)
        cost = int(cost)
        self.controllers[bridge].set_port_cost(port, cost)

    def command_log(self, bridge, type, visibility):
        """
        Active ou désactive le logging d'informations

        :param bridge: Nom du switch
        :param type: Informations à logger (bpdu/port)
        :param visibility: Visibilité de l'information (show/hide)
        """
        if type == "bpdu":
            self.controllers[bridge].log_bpdu = visibility == "show"
        elif type == "port":
            self.controllers[bridge].log_port_change = visibility == "show"
        else:
            print("Unknown type", type)

    def run(self):
        """
        Démarre l'interface en ligne de commande
        """
        mute_stdout()
        while True:
            print("> ", file=sys.stderr, end="")
            try:
                line = input()
                if len(line) > 0:
                    args = line.split(" ")
                    command = args[0]
                    args = args[1:]
                    if command in self.commands:
                        try:
                            self.commands[command](*args)
                        except TypeError:
                            print("Invalid arguments", file=sys.stderr)
                        except Exception as e:
                            print("An error occured:", e, file=sys.stderr)
                            traceback.print_exc(file=sys.stderr)
                    else:
                        print("Unknown command {}".format(command), file=sys.stderr)
                        print("Available commands: {}".format(", ".join(self.commands.keys())), file=sys.stderr)
            except (EOFError, KeyboardInterrupt):
                print(file=sys.stderr)
                self.command_quit()

if __name__ == "__main__":
    cli = CLI()
    cli.run()
