#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple graph simulation solver
Extracted from system_graph_load.py main section
"""


import matplotlib.pyplot as plt
import os

from pyingraph import GraphLoader

# # For debugging the modified PyG_graph_load.py before packaging:
# # Set the current working directory to the script's folder
# import sys
# script_dir = os.path.dirname(os.path.abspath(__file__))
# os.chdir(script_dir)
# print(f"\033[1;36m📂 Working directory set to: {script_dir}\033[0m")
# sys.path.append('../src/pyingraph')
# from PyG_graph_load import GraphLoader

def main():
    # Specify the name of the JSON file that describes the graph
    # file_name = 'graph_simple_demo.json'
    file_name = 'pyingraph_export.json'
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Create path to JSON file relative to script location
    json_path = os.path.join(script_dir, file_name)
    
    # create a loader with the given json file
    loader = GraphLoader(json_path)
    
    # load graph
    loader.load()
    
    # get nx graph
    nx_graph = loader.get_nx_graph()
    # visualize the graph: it is necessary to
    # call loader.get_nx_graph() before visualization!
    loader.visualize_graph()
    plt.show()
    
    # debug print
    print("\033[1;32m🚀 Running graph ... \033[0m")
    
    # Calling the built-in simple node-traverse routine in loader is
    # the simplest way of running the graph
    loader.reset_graph_edges()
    loader.simple_traverse_graph(time=0.0)

if __name__ == '__main__':
    main()