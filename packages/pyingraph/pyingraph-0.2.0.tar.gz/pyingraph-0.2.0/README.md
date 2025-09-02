# 🐷 PyG: PyInGraph 


```txt
🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷
+---------+     +---------+      +---------+
|   🐍 A  | --> |   🐍 B  | --> |   🐍 C  |
+---------+     +---------+      +---------+
     |                                |
     v                                v
+---------+                      +---------+
|   🐍 D  | <------------------  |   🐍 E  |
+---------+                      +---------+
🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷🐷
```

A Python framework for creating computational graphs where each node represents an algorithm block. Perfect for integrating multiple algorithms into a visual, executable workflow.

## GUI support
2025-07-09: A litegraph-based graphical editor, [LiteGraph-PyG](https://github.com/wdsys/litegraph-PyG), is introduced to support the graph editing and running in users' local python environments. See [LiteGraph-PyG on GitHub](https://github.com/wdsys/litegraph-PyG)

## Dependencies

- Python >= 3.7
- numpy, matplotlib, networkx
- httpimport, requests (for remote modules)


## Quick Start

### Installation

From PyPI (recommended):
```bash
pip install pyingraph
```

From source:
```bash
cd PyInGraph
pip install -e .
```

This demo loads a simple graph that adds two numbers using custom algorithm blocks.

### Accessing Examples After Installation

After installing PyInGraph via pip, you can easily access and copy examples to your working directory:

```python
# Copy all examples to current directory
from pyingraph import copy_examples
copy_examples('.')  # Creates 'pyingraph_examples' folder
```
Then try the demos:
```bash
cd pyingraph_examples
python demo_simple_add.py
```
Another demo for remote graph and modules:
```bash
python demo_control_system.py
```

Ohter utils in the examples are:

```python
# List all available examples
from pyingraph import list_examples
examples = list_examples()
for name, info in examples.items():
    print(f"{name}: {info['description']}")

# Copy all examples to current directory
from pyingraph import copy_examples
copy_examples('.')  # Creates 'pyingraph_examples' folder

# Copy a specific example
from pyingraph import copy_example
copy_example('demo_simple_add', '.')  # Copies demo and dependencies

# Get examples location in installed package
from pyingraph import get_examples_path
print(f"Examples located at: {get_examples_path()}")

# Show usage help
from pyingraph import show_example_usage
show_example_usage()
```

> [!TIP]
> Use `copy_examples('.')` to get all examples in a `pyingraph_examples` folder, then navigate there to run the demos.

## Key Features

- **Easy Workflow Integration**: Algorithms, with inputs/outputs/internal-states, can be easily integrated via a graph structure. This graph-based approach, besides being code-efficient, enables a broad category of usages, such as system simulation, AI workflows, and network analysis (e.g., connectivity, condensation, etc.).
- **Local & Remote Modules**: Load algorithms from files or HTTP repositories
- **Built-in Visualization**: See your computational graph with NetworkX
- **Parameter Management**: Configure algorithm parameters via JSON

## How It Works

### An Example Project Structure
```
your_project/
├── local_modules/
│   ├── mod_source_constant.py
│   └── mod_sink_print.py
├── graph_example.json
└── run_graph.py
```

### 1. Create Algorithm Blocks

Each algorithm is a Python class that inherits from `BlockBase`:

#### Block 1 of 2: `mod_source_constant.py`

```python
from pyingraph import BlockBase

class ConstantSource(BlockBase):
    """
    A constant source block that outputs a user-specified constant value.
    """
    def __init__(self):
        super().__init__()
        self.attrNamesArr = ["value"]  # Parameter name for the constant value
        self.value = 0.0  # Default value
    
    def read_inputs(self, inputs: list) -> None:
        pass
    
    def compute_outputs(self, time: float = None) -> list:
        return [self.value]
    
    def reset(self) -> None:
        pass
```

#### Block 2 of 2: `mod_sink_print.py`

```python
from pyingraph import BlockBase

class SinkPrint(BlockBase):
    """
    A print sink block that prints all inputs it receives.
    This is useful for debugging and monitoring data flow in the graph.
    """
    def __init__(self):
        super().__init__()
        self.attrNamesArr = []  # No parameters needed
    
    def read_inputs(self, inputs: list) -> None:
        self.inputs_received = inputs
    
    def compute_outputs(self, time: float = None) -> list:
        print(f"SinkPrint received: {self.inputs_received}")
        return []  # Sink blocks typically don't produce outputs
    
    def reset(self) -> None:
        self.inputs_received = None
```


### 2. Define Your Graph

Create a JSON file `graph_example.json` describing your computational graph:

```json
{
    "nodes": [
        {
            "id": "node1",
            "name": "Constant Source 1",
            "folder_url": "",
            "folder_path": "local_modules",
            "class_file": "mod_source_constant.py",
            "class_name": "ConstantSource",
            "parameters": {
                "value": 1.0
            }
        },
        {
            "id": "node2",
            "name": "Sink print",
            "folder_url": "",
            "folder_path": "local_modules",
            "class_file": "mod_sink_print.py",
            "class_name": "SinkPrint",
            "parameters": {}
        }
    ],
    "edges": [
        {
            "source_node_id": "node1",
            "target_node_id": "node2",
            "source_port_idx": 0,
            "target_port_idx": 0,
            "properties": {}
        }
    ]
}
```

### 3. Load and Run

Create a script `run_graph.py` to load and run your graph:


```python
from pyingraph import GraphLoader

loader = GraphLoader("graph_example.json", flag_remote=False)
loader.load()
nx_graph = loader.get_nx_graph()
loader.visualize_graph(block=True)  # See your graph
loader.reset_graph_edges() # init the output data or graph edges
loader.simple_traverse_graph()  # Execute the graph
```

Make sure the project structure and the graph json follows [the recommended structure](#an-example-project-structure), particularly the `folder_path` field in the graph json.

### JSON Schema Validation

PyInGraph includes a comprehensive JSON schema (`graph_schema.json`) to help you validate and understand the structure of graph configuration files. The schema provides:

- **Validation**: Ensure your JSON files are correctly formatted
- **IDE Support**: Get auto-completion and error checking in modern editors
- **Documentation**: Clear descriptions of all fields and their purposes
- **Examples**: Sample configurations for reference

## Examples Included

The `examples/` folder contains ready-to-run demos:

- **`demo_simple_add.py`**: Simple demo of a basic graph that adds two numbers, using local modules and graph
- **`demo_control_system.py`**: Control system simulation example, using remote modules and graph
- **`graph_simple_demo.json`**: Graph definition for the simple demo `demo_simple_add.py`
- **`local_modules/`**: Sample algorithm blocks:
  - `mod_source_constant.py`: Constant value source
  - `mod_summer.py`: Addition operation
  - `mod_sink_print.py`: Output print as display

## Remote Module Support

Load algorithm blocks from HTTP repositories by setting `flag_remote=True`:

```python
loader = GraphLoader("http://example.com/graph.json", flag_remote=True)
```

By default, `flag_remote=False`

## Support

Questions? Contact: bobobone@qq.com

## License

MIT License - see LICENSE file for details.