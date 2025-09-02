#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple graph simulation solver
Extracted from system_graph_load.py main section
"""

from pyingraph import GraphLoader

import numpy as np

def main():
    # create a loader with the remote json file
    graph_url = 'https://dev.wiseverds.com/api/projects/2541/files/algorithms/graph_looped.json'
    loader = GraphLoader(graph_url,flag_remote=True)
    # load graph
    loader.load()
    
    # get nx graph
    nx_graph = loader.get_nx_graph()
    
    # visualize the graph
    loader.visualize_graph()
    
    # return
    
    # debug print
    print("\033[1;32m🚀 Before Traverse: \033[1;33mStarting Graph Simulation\033[0m")
    
    # simulation (dynamic!)
    time_start, time_end, time_step = 0, 20, 0.02
    loader.reset_graph_edges()
    for time in np.arange(time_start, time_end, time_step):
        # traverse the graph with a built-in, simple algorithm
        loader.simple_traverse_graph(time=time)
    
    # visualize simulation results
    # find all nodes whose instance has method 'show_final_plot()'
    nodes_with_plot = []
    for node_id, node_data in nx_graph.nodes(data=True):
        if hasattr(node_data['instance'], 'show_final_plot'):
            nodes_with_plot.append(node_id)
    # call show_final_plot() for each node
    for node_id in nodes_with_plot:
        node_inst = nx_graph.nodes[node_id]['instance']
        node_inst.show_final_plot()

if __name__ == '__main__':
    main()