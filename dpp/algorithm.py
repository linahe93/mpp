from DisjointedNode import path_computing
from SpectrumAssign import routing_and_spectrum
import networkx as nx

def algorithm(graph, flow):
    src = flow.src_num
    dst = flow.dst_num
    required_bandwidth = flow.bandwidth
    shortest_paths = path_computing(graph, src, dst)
    print "shortest_paths for all switches pair %s" % shortest_paths
    paths = []
    for i in range(0, 3):
        paths.append(shortest_paths[src][dst][i])

    paths_occupied_spectrum = routing_and_spectrum(graph, paths, required_bandwidth)
    print "all routing path and occupied slots %s" % paths_occupied_spectrum

    return paths_occupied_spectrum

