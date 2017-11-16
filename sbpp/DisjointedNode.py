import copy
import networkx as nx

"""
Suurballe's algorithm 
"""


def path_computing(graph, src, dst, k = 3):
    _graph = copy.deepcopy(graph)
    shortest_paths = link_disjoint_paths(_graph, src, dst, k)
    return shortest_paths


def link_disjoint_paths(graph, src, dst, k):
    new_graph = copy.deepcopy(graph)
    shortest_path = nx.dijkstra_path(graph, src, dst, 'weight')
    # print shortest_path
    all_shortest_paths = nx.single_source_dijkstra_path(graph, src)
    # print all_shortest_paths
    nodes = nx.nodes(graph)
    tree_edges = get_tree_edge(nodes, all_shortest_paths)
    # print tree_edges

    shortest_paths_list = [shortest_path]

    for edge in graph.edges():
        # print "change the weight between"
        # print edge[0], edge[1]
        d_src_start = get_weight_sum(graph, edge[0], all_shortest_paths)
        d_src_end = get_weight_sum(graph, edge[1], all_shortest_paths)
        # print d_src_start, d_src_end, graph[edge[0]][edge[1]]['weight']
        new_graph[edge[0]][edge[1]]['weight'] = graph[edge[0]][edge[1]]['weight'] - d_src_end + d_src_start
        # print "the new weight %s" % new_graph[edge[0]][edge[1]]['weight']

    times = (k - 1)/2

    for i in range(times):
        residual_graph = create_residual_graph(new_graph, shortest_path)
        # print "residual_graph edges"
        # print residual_graph.edges()
        another_shortest_path = nx.dijkstra_path(residual_graph, src, dst, 'weight')
        # print "the second shortest path %s" % another_shortest_path
        shortest_paths_list.append(another_shortest_path)
        shortest_path = another_shortest_path

    subgraph = get_subgraph(shortest_paths_list)
    # print subgraph.edges(), src, dst

    generator = nx.all_simple_paths(subgraph, src, dst, 'weight')
    found_paths = []
    for path in generator:
        found_paths.append(path)

    # print "the found disjoint path %s" % found_paths
    return found_paths


def get_tree_edge(nodes, all_shortest_paths):
    tree_edges = set()
    for node in nodes:
        path = all_shortest_paths[node]
        for i in range(len(path)-1):
            tree_edges.add((path[i], path[i+1]))
    return tree_edges


def get_weight_sum(graph, node, all_shortest_paths):
    path = all_shortest_paths[node]
    sum = 0
    for i in range(len(path) - 1):
        sum = sum + graph[path[i]][path[i + 1]]['weight']
    #print "sum %s" %sum
    return sum


def create_residual_graph(graph, path):
    # print path
    edges = get_edges_of_path(path)
    # print edges
    for edge in edges:
        graph.remove_edge(edge[0], edge[1])
    return graph


def get_edges_of_path(path):
    edges = []
    for i in range(len(path)-1):
        edges.append((path[i], path[i+1]))
    return edges


def get_subgraph(shortest_path, another_shortest_path):
    subgraph = nx.DiGraph()
    overlapping_links = []
    edges_of_paths = get_edges_of_path(shortest_path) + get_edges_of_path(another_shortest_path)
    for edge in edges_of_paths:
        if subgraph.has_edge(edge[0], edge[1]):
            overlapping_links.append(edge)
        else:
            subgraph.add_edge(edge[0], edge[1], weight=1)

    for edge in overlapping_links:
        subgraph.remove_edge(edge[0], edge[1])
    return subgraph


def get_subgraph(paths):
    subgraph = nx.DiGraph()
    overlapping_links = []
    edges_of_paths = []
    for path in paths:
        edges = get_edges_of_path(path)
        edges_of_paths = edges_of_paths + edges

    for edge in edges_of_paths:
        if subgraph.has_edge(edge[0], edge[1]):
            overlapping_links.append(edge)
        else:
            subgraph.add_edge(edge[0], edge[1], weight=1)

    for edge in overlapping_links:
        subgraph.remove_edge(edge[0], edge[1])
    return subgraph
