import networkx as nx
from TopologyManager import get_graph, get_graph_test
from simulation import Simulation
from algorithm import algorithm


def main():
    # graph = get_graph_test()
    # filename = 'nsfnet.txt'
    filename = 'usbnet.txt'
    graph = get_graph(filename)
    print "1: create graph"
    total_time = 10
    arrive_rate = 2
    max_bandwidth = 200
    print " the initial graph %s" % graph.edges(data=True)

    print "2: begin simulation"
    sim = Simulation(algorithm, graph, total_time, arrive_rate, max_bandwidth)
    sim.run()

if __name__ == "__main__":
    main()