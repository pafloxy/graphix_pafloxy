from graphix.pattern import Pattern
import networkx as nx
import graphix
from graphix.gflow import flow
import numpy as np
import matplotlib.pyplot as plt


def process_layer_data(graph: nx.Graph, layer_map: dict):

    node_attributes = {}; max_l = max(set(layer_map.values()))
    layer_data = {n: set() for n in range(max_l +1 )}

    for v in graph.nodes():
        # print(v); print(layer_data[v])
        node_attributes[v] = {"layer" : layer_map[v]}
        layer_data[layer_map[v]].add(v)

    return {'attribute_data' : node_attributes, 'nodes_in_layers': layer_data, 'num_layers' : max_l  }


def get_nx_graph(pattern: graphix.Pattern):
    nodes, edges = pattern.get_graph()
    g = nx.Graph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)

    return g

def get_pos(pattern: graphix.Pattern, f:dict):

    num_output_nodes = len(pattern.output_nodes)
    flow = [[i] for i in range(num_output_nodes)]
    for i in range(num_output_nodes):
        contd = True
        val = i
        while contd:
            try:
                val = f[val]
                flow[i].append(val)
            except KeyError:
                contd = False
    longest = np.max([len(flow[i]) for i in range(num_output_nodes)])

    pos = dict()
    for i in range(num_output_nodes):
        length = len(flow[i])
        fac = longest / (length - 1)
        for j in range(len(flow[i])):
            pos[flow[i][j]] = (fac * j, -i)
    
    return pos, longest

# determine wheher or not a node will be measured in Pauli basis
def get_clr_list(pattern):
    nodes, edges = pattern.get_graph()
    meas_list = pattern.get_measurement_commands()
    g = get_nx_graph(pattern)
    clr_list = []
    for i in g.nodes:
        for cmd in meas_list:
            if cmd[1] == i:
                if cmd[3] in [-1, -0.5, 0, 0.5, 1]:
                    clr_list.append([0.5, 0.5, 0.5])
                else:
                    clr_list.append([1, 1, 1])
        if i in pattern.output_nodes:
            clr_list.append([0.8, 0.8, 0.8])
    return clr_list

def pretty_plot_pattern(pattern: graphix.Pattern, input_nodes : set):

    clr_list = get_clr_list(pattern)
    g = get_nx_graph(pattern)
    f, l_k = flow(g, input_nodes, set(pattern.output_nodes))
    
    assert isinstance(f, dict)
    pos, length = get_pos(pattern, f) ; layer_data = process_layer_data(g, l_k)
    
    nx.set_node_attributes(g, layer_data['attribute_data'])

    graph_params = {"with_labels": True, "node_size": 600, "node_color": get_clr_list(pattern), "edgecolors": "k"}
    pos = nx.multipartite_layout(g, subset_key= 'layer', align='vertical', scale= 100)

    plt.figure(figsize=(25,16))

    for layer in range(layer_data['num_layers']):   
        vertx_1 = next(iter(layer_data['nodes_in_layers'][layer])); xcoord_1 = pos[vertx_1][0]
        vertx_2 = next(iter(layer_data['nodes_in_layers'][layer + 1])); xcoord_2 = pos[vertx_2][0]
        xcoord = np.mean([xcoord_1, xcoord_2])
        plt.axvline(xcoord)
        plt.text(x= xcoord + 1.5, y= -18, s= 'l= ' + str(layer) )

    edge_color= []
    for u,v in g.edges():
        if( u not in pattern.output_nodes and v not in pattern.output_nodes ) :
            # print (u,v, u==f[v] or v== f[u])
            if u==f[v] or v== f[u] :
                edge_color.append('r')
            else :
                edge_color.append('g')


    nx.draw_networkx(g, pos= pos, **graph_params, edge_color = edge_color)

    
    

            