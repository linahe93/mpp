from __future__ import division

import random
import numpy as np
from Queue import PriorityQueue
from flow import Flow


class Simulation(object):
    def __init__(self, algorithm, graph, total_time, reciprocal_lambda, max_bandwidth):
        self.algorithm = algorithm
        self.graph = graph
        self.total_time = total_time
        self.reciprocal_lambda = reciprocal_lambda
        self.max_bandwidth = max_bandwidth
        # self.current_time = 0
        self.flows = self.create_flow_samples()

    def create_flow_samples(self):
        flows = []
        for current_time in range(self.total_time):
            flow_num = np.random.poisson(self.reciprocal_lambda, 1)
            flows_come_in_current_time = []
            for _ in range(flow_num):
                src_num, dst_num = self.generate_random_src_dst_pair()
                start_time = current_time
                finish_time = start_time + self.generate_random_exist_time()
                bandwidth = self.generate_random_bandwidth()

                flow = Flow(src_num, dst_num, start_time, finish_time, bandwidth)
                flows_come_in_current_time.append(flow)
            flows.append(flows_come_in_current_time)

        return flows

    def generate_random_src_dst_pair(self):
        node_num = self.graph.__len__()
        src_num = random.randint(1, node_num)
        dst_num = random.randint(1, node_num)
        while src_num == dst_num:
            dst_num = random.randint(1, node_num)

        return src_num, dst_num

    def generate_random_start_time(self):
        return random.randint(0, self.total_time)

    def generate_random_exist_time(self):
        # TODO still need to discuss
        return random.randint(0, 5)

    def generate_random_bandwidth(self):
        return random.randint(0, self.max_bandwidth)

    def run(self):
        rejected_flows = []
        current_flows = PriorityQueue()
        total_spectrum = self.get_total_spectrum()
        spectrum_utilization_per_sec = []

        for current_time in range(self.total_time):
            # process incoming flows
            for flow in self.flows[current_time]:
                paths = self.algorithm(self.graph, flow)
                if not paths:
                    rejected_flows.append(flow)
                else:
                    current_flows.put((flow.finish_time, paths, flow))
            # cleanup finished flows
            while not current_flows.empty() and current_flows.queue[0][0] == current_time:
                _, paths, flow = current_flows.get()
                self.remove_paths(paths, flow)
            # calculate spectrum utilization per round
            spectrum_utilization_per_sec.append(self.calculate_spectrum_utilization(total_spectrum))
        # calculate block rate
        block_rate = self.calculate_block_rate(rejected_flows)
        print('Block Rate: %f' % block_rate)
        print('Spectrum Utilization: '),
        print(spectrum_utilization_per_sec)
        for e in self.graph.edges(data=True):
            print(e)
        print(reduce(lambda x, y: x + len(y), self.flows, 0))
        print(len(rejected_flows))

    def remove_paths(self, paths, flow):
        self.remove_flows_attribute(paths[0], flow)

        for path, start_index, total_num in paths:
            for i in range(len(path) - 1):
                src_num, dst_num = path[i], path[i + 1]
                spectrum_slots = self.graph.get_edge_data(src_num, dst_num)['spectrum_slots']
                for j in range(start_index, start_index + total_num):
                    if spectrum_slots[j] == 1 or spectrum_slots[j] == 2:
                        spectrum_slots[j] = 0
                    else:
                        spectrum_slots[j] -= 1

    def remove_flows_attribute(self, path, flow):
        path, _, _ = path
        for i in range(len(path) - 1):
            src_num, dst_num = path[i], path[i + 1]
            # print('aaaaaaaaaaaaaaaaaaaaaaaaaa')
            # print(src_num)
            # print(dst_num)
            # print(self.graph.get_edge_data(src_num, dst_num)['flows'])
            # print(flow)
            self.graph.get_edge_data(src_num, dst_num)['flows'].remove(flow)

    def calculate_block_rate(self, rejected_flows):
        blocked_bandwidth = reduce(lambda x, y: x + y.bandwidth, rejected_flows, 0)
        total_bandwidth = 0
        for flows in self.flows:
            total_bandwidth = reduce(lambda x, y: x + y.bandwidth, flows, total_bandwidth)

        return blocked_bandwidth / total_bandwidth

    def get_total_spectrum(self):
        total_spectrum = reduce(lambda x, y: x + len(y[2]['spectrum_slots']), self.graph.edges(data=True), 0)
        # print total_spectrum

        return total_spectrum

    def calculate_spectrum_utilization(self, total_spectrum):
        occupied_spectrum = \
            reduce(lambda x, y: x + sum([1 for _ in y[2]['spectrum_slots'] if _ != 0]), self.graph.edges(data=True), 0)

        return occupied_spectrum / total_spectrum
