import networkx as nx
import json
import numpy as np
with open("initial_edges.json","r") as f:
    graph_topology = json.load(f)
    graph_topology = np.array(graph_topology['initial_edges'[:]])
    print(graph_topology)
