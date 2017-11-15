import networkx as nx
from TopologyManager import get_graph
from simulation import Simulation
from algorithm import algorithm

graph = nx.DiGraph()
def main():
    graph = get_graph()
    total_time = 100
    arrive_rate = 5
    max_bandwidth = 200

    sim = Simulation(algorithm, graph, total_time, arrive_rate, max_bandwidth)
    sim.run()

if __name__ == "__main__":
    main()