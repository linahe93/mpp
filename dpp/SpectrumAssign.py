import math
import copy

total_slots = 10  # the number of total slots
uni_slot_size = 12.5  # the size of uni slot(GHz)

def routing_and_spectrum(graph, paths, required_bandwidth):
    slots_num = get_slots_num(required_bandwidth)
    print "the number of slots is %s" % slots_num
    print "shortest path %s" %paths
    sorted_paths = sort_all_k_shortest_paths(paths, graph)
    print "sorted paths ",
    print sorted_paths

    central_frequency_list = []
    paths_occupied_spectrum = []

    #allocate the slots to multiple path
    backup = False
    for path in sorted_paths:
        central_frequency, path_occupied_spectrum = assign_spectrum(graph, path, slots_num, backup)
        print "central frequency %s" % central_frequency
        if central_frequency is None:
            break
        else:
            backup = True
            paths_occupied_spectrum.append(path_occupied_spectrum)
            central_frequency_list.append(central_frequency)

    if len(paths_occupied_spectrum) <= 3:
        print "the number of routing path is %d" % len(paths_occupied_spectrum)
    return paths_occupied_spectrum

def get_slots_num(required_bandwidth):
    """
        Calculate the number of slots for required bandwidth
        the guard band is 1.
    """
    slots_num = math.ceil(required_bandwidth / uni_slot_size) + 1
    return int(slots_num)


def assign_spectrum(graph, path, slots_num, backup):
    path_slots_list = get_spectrum_slots_list(path, graph)

    print "the slot lists of the path",
    print path_slots_list

    slot_list = [sum(x) for x in zip(*path_slots_list)]
    print "the sum of the slot lists of the path",
    print slot_list

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

    start_localization = localization - slots_num

    central_frequency = get_central_frequency(start_localization, slots_num)
    set_links_slots(path, start_localization, slots_num, graph, backup)
    path_occupied_spectrum = (path, start_localization, slots_num)

    if localization is not None:
        return central_frequency, path_occupied_spectrum
    else:
        return None


def get_central_frequency(localization, slots_num):
    return 193.11 + (localization + slots_num) * 6.25


def set_links_slots(path, localization, slots_num, graph, backup=False):
    hops = len(path)
    for n in slots_num:
        for i in range(hops - 1):
            if backup:
                graph[path[i]][path[i + 1]]['spectrum_slots'][localization + n] = 2
            else:
                graph[path[i]][path[i + 1]]['spectrum_slots'][localization + n] = 1

def sort_all_k_shortest_paths(shortest_paths, graph):
    """
        Sort k paths
    """
    sorted_metric_paths = []
    sorted_shortest_paths = []
    for path in shortest_paths:
        print "path %s" % path
        metric = get_metric(path, graph)
        print "metric %s" % metric
        metric_path = (metric, path)
        sorted_metric_paths.append(metric_path)
    sorted(sorted_metric_paths)

    for element in sorted_metric_paths:
        sorted_shortest_paths.append(element[1])
    return sorted_shortest_paths


def get_metric(path, graph):
    hops = len(path)
    # print("hops %s" %hops)
    free_spectrum = 0
    path_slots_list = get_spectrum_slots_list(path, graph)
    for slots_of_edge in path_slots_list:
        free_spectrum += total_slots - sum(slots_of_edge)

    if free_spectrum is not None:
        return (free_spectrum / (hops - 1))
    else:
        print "No free spectrum"

def get_spectrum_slots_list(path, graph):
    path_slots_list = []
    for i in range(len(path) - 1):
        path_slots_list.append(graph[path[i]][path[i+1]]['spectrum_slots'])
    return path_slots_list