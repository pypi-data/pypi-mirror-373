import json
import importlib
import importlib.util # fix util missing
from typing import List, Dict, Any
import networkx as nx
import matplotlib.pyplot as plt
import httpimport


class GraphLoader:
    """
    Graph structure loader for loading nodes and edges from JSON description files
    """
    
    def __init__(self, graph_file_or_url: str, flag_remote=False):
        """
        Initialize the loader
        :param graph_file_or_url: Graph description file path or URL
        """
        self.graph_file = graph_file_or_url
        self.graph_data = None
        self.node_instances = []
        self.flag_remote = flag_remote
    
    def load(self) -> None:
        """Load and parse graph description json file"""
        if self.flag_remote:
            self.graph_data = self._load_graph_description_from_url(self.graph_file)
        else:
            self.graph_data = self._load_graph_description()
        self.node_instances = self._create_node_instances()
    
    def _load_graph_description(self) -> dict:
        """Load graph description JSON file"""
        with open(self.graph_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_graph_description_from_url(self, url: str) -> dict:
        """Load graph description JSON file from URL"""
        # Implementation for downloading JSON file from URL
        # Using requests library as an example
        import requests
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to download graph description from {url}")
        return json.loads(response.text)
    
    def _flexible_import(self, class_file):
        try:
            # Try standard package import first
            module_name = class_file.replace('.py', '').replace('/', '.').replace('\\', '.')
            return importlib.import_module(module_name)
        except ImportError:
            # Fallback to file-based import
            spec = importlib.util.spec_from_file_location(
                class_file.replace('.py', ''), 
                class_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    
    def _create_node_instances(self) -> List[Any]:
        """
        Create all node instances
        :return: List of node instances
        """
        instances = []
        
        for node in self.graph_data['nodes']:
            # dynamically import modules
            # if the node's field 'folder_path' is not None nor empty string, then the local module
            # has higher loading priority (flag_remote=False)
            has_folder_path = ('folder_path' in node and 
                               node['folder_path'] is not None and 
                               node['folder_path'].strip() != '')
            if self.flag_remote is False and has_folder_path: # local module
                # module = importlib.import_module(node['class_file'].replace('.py', ''))
                strPath = node['folder_path']
                strFile = node['class_file']
                fullPath = strPath + '/' + strFile
                # module = self._flexible_import(node['class_file'])
                module = self._flexible_import(fullPath)
            else: # remote module
                repo_folder_url = node['folder_url']
                with httpimport.remote_repo(repo_folder_url):
                    module = importlib.import_module(node['class_file'].replace('.py', ''))
            # Get class name
            if not hasattr(module, node['class_name']):
                raise ValueError(f"Class {node['class_name']} not found in module {node['class_file']}")
            class_name = node['class_name']
            # Create instance
            cls = getattr(module, class_name)
            instance = cls()
            # Read parameters
            instance.read_parameters(node['parameters'])
            # Add id and name attributes
            instance.id = node['id']
            instance.name = node['name']
            # Store instances in the array
            instances.append(instance)
        
        return instances
    
    def get_nodes(self) -> List[Any]:
        """Get all nodes' instances"""
        return self.node_instances
    
    def get_edges(self) -> List[dict]:
        """Get all edges' information"""
        return self.graph_data.get('edges', [])
    
    def get_nx_graph(self) -> nx.DiGraph:
        graph = nx.MultiDiGraph()
        
        # Fix: iterate over list instead of dictionary
        for node in self.node_instances:
            # graph.add_node(node['id'], instance=node['instance'])
            graph.add_node(node.id, instance=node, name=node.name)
            
        self._edges = self.get_edges()
        for edge in self._edges:
            graph.add_edge(
                edge['source_node_id'],
                edge['target_node_id'],
                key=f"{edge.get('id', '')}_src{edge.get('source_port_idx', 0)}_tgt{edge.get('target_port_idx', 0)}",
                source_port_idx=edge.get('source_port_idx', 0),
                target_port_idx=edge.get('target_port_idx', 0),
                source_node_id=edge.get('source_node_id', ''),
                target_node_id=edge.get('target_node_id', ''),
                **edge.get('properties', {})
            )
        self.graph = graph
        return graph
    
    # reset the 'data' field in all graph edges to None
    def reset_graph_edges(self):
        """
        Reset the 'data' field in all graph edges to None.
        """
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            data['data'] = None
    
    # traverse the graph: after init, each node copies the inputs from
    # input edges, compute outputs, and send outputs to the output edges
    def simple_traverse_graph(self, time: float = 0.0):
        """
        Traverse the multi-digraph and execute node computations
        :param nx_graph: NetworkX MultiDiGraph
        :param time: Current simulation time
        """
        nx_graph = self.graph
        # # Step 1: Initialize all edges with data = None
        # for u, v, key, data in nx_graph.edges(keys=True, data=True):
        #     data['data'] = None
        
        # Step 2: Traverse nodes and execute once
        for node in nx_graph.nodes(data=True):
            node_inst = node[1]['instance']
            # collect all data on the input edges into an array
            input_data = []
            for u, v, key, data in nx_graph.in_edges(node[0], keys=True, data=True):
                # if any one of the node's inputs is None, skip this node 
                # if data['data'] is None:
                #     break
                input_data.append(data['data'])
            # for this node, read inputs
            node_inst.read_inputs(input_data)
            # compute outputs
            outputs = node_inst.compute_outputs(time)
            # save the outputs to the 'data' field in the output edges,
            # as there might be multiple output edges, the ouputs array
            # should be disassembled, and items are filled to different
            # output edges with the 'source_port_idx' for array indexing
            if outputs is not None:
                for i, output in enumerate(outputs):
                    for _, _, key, data in nx_graph.out_edges(node[0], keys=True, data=True):
                        if data['source_port_idx'] == i:
                            data['data'] = output
    
    def visualize_graph(self, figsize=(10, 8), node_size=2000, node_color='lightblue', 
                      edge_width=2, edge_color='gray', font_size=12, block=True):
        """
        Visualize graph structure
        
        Parameters:
            figsize: Figure size (width, height)
            node_size: Node size
            node_color: Node color
            edge_width: Edge width
            edge_color: Edge color
            font_size: Label font size
            block: Whether to block execution (True=block until window closed, False=non-blocking continue execution)
        """
       
        # import matplotlib.pyplot as plt
        in_graph = self.graph

        # Font settings - use more fonts for better display
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']  # Prioritize Microsoft YaHei
        plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display issue

        
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(in_graph)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            in_graph, pos, 
            node_size=node_size, 
            node_color=node_color
        )
        
        # Draw edges (ensure arrows are visible)
        nx.draw_networkx_edges(
            in_graph, pos,
            width=edge_width,
            edge_color=edge_color,
            arrows=True,
            arrowsize=20,
            arrowstyle='->',
            min_source_margin=25,
            min_target_margin=25
        )
        
        # Draw node labels (display ID and name)
        labels = {node.id: f"{node.id}\n{node.name}" 
                 for node in self.node_instances}
        nx.draw_networkx_labels(
            in_graph, pos,
            labels=labels,
            font_size=font_size,
            font_weight='bold'
        )
        
        # Draw edge labels (display port indices)
        edge_labels = {(u, v): f"{d.get('source_node_id', '')}:{d.get('source_port_idx', 0)} → {d.get('target_node_id', '')}:{d.get('target_port_idx', 0)}" 
                      for u, v, d in in_graph.edges(data=True)}
        nx.draw_networkx_edge_labels(in_graph, pos, edge_labels=edge_labels)
        
        plt.title('System Graph Structure')
        plt.axis('off')
        plt.tight_layout()
        
        if not block:
            plt.ion()  # Turn on interactive mode
            plt.show(block=False)
            plt.pause(0.001)  # Small pause to ensure plot is displayed
        else:
            # plt.show(block=False)  # Default blocking behavior
            plt.show(block=True)  # Default blocking behavior

if __name__ == '__main__':
    # Usage example
    # loader = GraphLoader('graph_description.json')
    loader = GraphLoader('https://dev.wiseverds.com/api/projects/2541/files/algorithms/graph_looped.json', flag_remote=True)
    loader.load()
    
    # Get nodes and edges
    nodes = loader.get_nodes()
    edges = loader.get_edges()
    
    # print(f"Loading completed: {len(nodes)} nodes, {len(edges)} edges")
    # for i, node in enumerate(nodes):
    #     print(f"Node{i+1}: class: {type(node).__name__}, name: {node.name}, id: {node.id}")
    
    # test nx graph
    nx_graph = loader.get_nx_graph()
    # print(nx_graph.nodes(data=True))
    # print(nx_graph.edges(data=True))
    
    # Visualize graph
    loader.visualize_graph(block=True)

    # Example usage: traverse the graph with time = 0.0
    # Colorful print with ANSI escape codes
    print("\033[1;36m" + "="*50 + "\033[0m")  # Cyan border
    print("\033[1;32m🚀 Before Traverse: \033[1;33mStarting Graph Simulation\033[0m")  # Green + Yellow
    print("\033[1;36m" + "="*50 + "\033[0m")  # Cyan border
    
    # for loop for different simulation times, from
    # time = 0 to time = 5, spacing = 0.02
    loader.reset_graph_edges()
    import numpy as np
    for time in np.arange(0, 5, 0.02):
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
    
    