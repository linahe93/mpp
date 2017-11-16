import networkx as nx
import matplotlib.pyplot as plt

graph = nx.DiGraph()  # create graph
total_slots = 10
switches = [1, 2, 3, 4, 5, 6] #dpid
switch_pairs = {(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5), (4, 6),(5, 6)} # the connected switches pair

def get_graph():
    """
        Get the adjacency matrix from link_to_port
    """

    for pair in switch_pairs:
        slots_list = total_slots * [0]
        graph.add_edge(pair[0], pair[1], weight=1, spectrum_slots=slots_list)
        graph.add_edge(pair[1], pair[0], weight=1, spectrum_slots=slots_list)

        # print graph[pair[0]][pair[1]]['spectrum_slots']
        # print graph[pair[1]][pair[0]]['spectrum_slots']
    # graph[1][2]['spectrum_slots'][0] = 1
    # print graph[1][2]['spectrum_slots']
    # print graph[2][1]['spectrum_slots']
    return graph

def show_topology():
    print "the switches",
    print graph.nodes()
    print "the links",
    print graph.edges()
    nx.draw(graph)
    plt.savefig("simple_path.png")  # save as png
    plt.show()  # display

get_graph()