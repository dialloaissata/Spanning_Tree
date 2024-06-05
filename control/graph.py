
from p4utils.utils.helper import NetworkGraph
from .spanningtree import PortState, PortRole, STPController
import networkx as nx
import matplotlib.pyplot as plt
import typing

def topo_get_connections(topo: NetworkGraph):
    intfs = topo.get_node_intfs(fields=['node', 'port', 'node_neigh', 'port_neigh']).copy()
    intfs.pop('sw-cpu', None)
    for sw in intfs.keys():
        intfs[sw].pop('lo', None)
        intfs[sw].pop(topo.get_cpu_port_intf(sw), None)
    
    out = []
    for intf in intfs.values():
        for val in intf.values():
            out.append(val)
    return out

def draw_graph(topo: NetworkGraph, controllers: typing.Dict[str, STPController], pos = None):
    G = nx.Graph()

    color_for_role = {
        PortRole.ROOT: "#0000FF",
        PortRole.DESIGNATED: "#00FF00",
        PortRole.BLOCKING: "#FFFF00",
        PortRole.DISABLED: "#FF0000"
    }

    color_for_state = {
        PortState.DISABLED: "#790000",
        PortState.LISTENING: "#6b68ff",
        PortState.LEARNING: "#68ffd9",
        PortState.FORWARDING: "#a2ff68",
        PortState.BLOCKING: "#ff3a3a",
    }

    connections = topo_get_connections(topo)

    for node, port, node_neigh, port_neigh in connections:
        if node in controllers:
            G.add_node("{}".format(node), color="#AAAAAA", size=50)
            G.add_node("{}-{}".format(node, port), color=color_for_role[controllers[node].port_info[port].role], size=10)

            G.add_edge("{}".format(node), "{}-{}".format(node, port), color=color_for_state[controllers[node].port_info[port].state])
            G.add_edge("{}-{}".format(node, port), "{}-{}".format(node_neigh, port_neigh), color="#000000")
        else:
            G.add_node("{}".format(node), color="#AAAAAA", size=50)
            G.add_node("{}-{}".format(node, port), color="#AAAAAA", size=10)

            G.add_edge("{}".format(node), "{}-{}".format(node, port), color="#000000")
            G.add_edge("{}-{}".format(node, port), "{}-{}".format(node_neigh, port_neigh), color="#000000")

    plt.cla()
    if pos == None:
        pos = nx.layout.spring_layout(G, iterations=1000)
    nx.draw(
        G,
        with_labels=True,
        node_size=list(map(lambda x: x[1]["size"], G.nodes.data())),
        width=0.5,
        font_size=6,
        pos=pos,
        node_color=list(map(lambda x: x[1]["color"], G.nodes.data())),
        edge_color=list(map(lambda x: x[2]["color"], G.edges.data()))
    )

    plt.savefig("path.png")
    return pos



