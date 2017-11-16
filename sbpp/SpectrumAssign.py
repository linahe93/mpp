import math
import copy

uni_slot_size = 12.5  # the size of uni slot(GHz)


def routing_and_spectrum(graph, paths, required_bandwidth):
    slots_num = get_slots_num(required_bandwidth)
    print "the number of required slots is %s" % slots_num
    sorted_paths = sort_all_k_shortest_paths(paths, graph)
    print "sorted paths ",
    print sorted_paths

    central_frequency_list = []
    paths_occupied_spectrum = []
    working_path = None

    #allocate the slots to multiple path
    for path in sorted_paths:
        central_frequency, start_localization = assign_spectrum(graph, path, slots_num)
        print "central frequency %s" % central_frequency
        sorted_paths.remove(path)
        if central_frequency is None:
            continue
        else:
            working_path = path
            working_path_occupied_spectrum = (working_path, start_localization, slots_num)
            paths_occupied_spectrum.append(working_path_occupied_spectrum)
            central_frequency_list.append(central_frequency)
            break
    if working_path is None:
        return None

    _graph = copy.deepcopy(graph)
    inter_graph = modify_backup_path(_graph, working_path)
    print "sorted paths for backup path",
    print sorted_paths
    for path in sorted_paths:
        central_frequency, start_localization = assign_spectrum(inter_graph, path, slots_num, backup=True)
        print "central frequency %s" % central_frequency
        if central_frequency is None:
            continue
        else:
            backup_path_occupied_spectrum = (path, start_localization, slots_num)
            paths_occupied_spectrum.append(backup_path_occupied_spectrum)
            central_frequency_list.append(central_frequency)
            break

    if len(paths_occupied_spectrum) < 2:
        print "the number of routing path is %d" % len(paths_occupied_spectrum)
        return None

    set_links_slots(paths_occupied_spectrum, graph)
    return paths_occupied_spectrum


def modify_backup_path(graph, working_path):
    for i in range(len(working_path) - 1):
        if graph[working_path[i]][working_path[i+1]].get('flow') is not None:
            flows = graph[working_path[i]][working_path[i+1]]['flow']
            for flow in flows:
                paths_occupied_spectrum = flow.paths[1:]
                for path_occupied_spectrum in paths_occupied_spectrum:
                    path = path_occupied_spectrum[0]
                    loc = path_occupied_spectrum[1]
                    slots_num = path_occupied_spectrum[2]
                    for j in range(len(path) - 1):
                        for n in range(slots_num):
                            graph[path[j]][path[j+1]]['spectrum_slots'][loc + n] = 1
    print "aaaaaaaaaaassssssssssssss"
    print graph.edges(data=True)
    return graph


def get_slots_num (required_bandwidth):
    """
        Calculate the number of slots for required bandwidth
        the guard band is 1.
    """
    slots_num = math.ceil(required_bandwidth / uni_slot_size) + 1
    return int(slots_num)


def assign_spectrum(graph, path, slots_num, backup = False):
    path_slots_list = get_spectrum_slots_list(path, graph)

    if backup:
        slot_list = [sum([1 for _ in x if _ == 1]) for x in zip(*path_slots_list)]
    else:
        slot_list = [sum(x) for x in zip(*path_slots_list)]

    continous_slots = 0
    localization = 0
    for slot in slot_list:
        localization = localization + 1
        if slot == 0:
            continous_slots = continous_slots + 1
            if continous_slots == slots_num:
                break
        else:
            continous_slots = 0
    if continous_slots != slots_num:
        return None, None

    start_localization = localization - slots_num

    central_frequency = get_central_frequency(start_localization, slots_num)

    return central_frequency, start_localization


def get_central_frequency(localization, slots_num):
    return 193.11 + (localization + slots_num) * 6.25


def set_links_slots(paths_occupied_spectrum, graph):
    backup = False
    for path, localization, slots_num in paths_occupied_spectrum:
        hops = len(path)
        for n in range(slots_num):
            for i in range(hops - 1):
                if backup:
                    graph[path[i]][path[i + 1]]['spectrum_slots'][localization + n] = 2
                else:
                    graph[path[i]][path[i + 1]]['spectrum_slots'][localization + n] = 1
        backup = True

def sort_all_k_shortest_paths(shortest_paths, graph):
    """
        Sort k paths
    """
    print "4.1: sort the shortest path through the metric"
    sorted_metric_paths = []
    sorted_shortest_paths = []
    metrics = []
    for path in shortest_paths:
        metric = get_metric(path, graph)
        metric_path = (metric, path)
        sorted_metric_paths.append(metric_path)
    sorted_metric_paths.sort(key=lambda x: x[0], reverse=True)
    for element in sorted_metric_paths:
        sorted_shortest_paths.append(element[1])
        metrics.append(element[0])
    print "metrics are %s" % metrics
    return sorted_shortest_paths


def get_metric(path, graph):
    hops = len(path)
    # print("hops %s" %hops)
    free_spectrum = 0
    path_slots_list = get_spectrum_slots_list(path, graph)
    for slots_of_edge in path_slots_list:

        free_spectrum += len(slots_of_edge) - sum([1 for _ in slots_of_edge if _ != 0])

    if free_spectrum is not None:
        return (free_spectrum /(hops - 1))
    else:
        print "No free spectrum"


def get_spectrum_slots_list(path, graph):
    path_slots_list = []
    for i in range(len(path) - 1):
        path_slots_list.append(graph[path[i]][path[i+1]]['spectrum_slots'])
    return path_slots_list
