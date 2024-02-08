# Author: Matteo Serafino <m.serafi00@ccny.cuny.edu>, 
#
# License: GNU General Public License v3.0

import graph_tool.all as gt
import pandas as pd 
import networkx as nx
import numpy as np
from collections import Counter
import time

import pyximport
pyximport.install(setup_args={"script_args" : ["--verbose"]})


import sys 
sys.path.append('PATH TO CI ALGH')

import CIcython



def get_prop_type(value, key=None):
    """
    Performs typing and value conversion for the graph_tool PropertyMap class.
    If a key is provided, it also ensures the key is in a format that can be
    used with the PropertyMap. Returns a tuple, (type name, value, key)
    """
    # if isinstance(key, unicode):
    #     # Encode the key as ASCII
    #     key = key.encode('ascii', errors='replace')

    # Deal with the value
    if isinstance(value, bool):
        tname = 'bool'

    elif isinstance(value, int):
        tname = 'float'
        value = float(value)

    elif isinstance(value, float):
        tname = 'float'

    # elif isinstance(value, unicode):
    #     tname = 'string'
    #     value = value.encode('ascii', errors='replace')

    elif isinstance(value, dict):
        tname = 'object'

    else:
        tname = 'string'
        value = str(value)

    return tname, value, key
    
def add_CI_to_graph(graph,graph_file=None):
    for direction in [ 'out', 'in']:
        t0 = time.time()
        CIranks, CImap = CIcython.compute_graph_CI(graph, rad=2,
                                                   direction=direction,
                                                   verbose=False)
        graph.vp['CI_' + direction] = graph.new_vertex_property('int64_t', vals=0)
        graph.vp['CI_' + direction].a = CImap
    if graph_file:
        graph.save(graph_file.replace('gp','gt'))
    else:
        return graph

def build_CI_rank(graph ,wich='out',graph_file  = None):
    rst = {}
    if graph:
        g = graph
    else:
        print(f"------------------{graph_file}------------------")
        g = gt.load_graph(graph_file)
        
    if wich == 'out' or wich=='both':
        user_CI = {g.vp.id[v]: g.vp.CI_out[v] for v in g.vertices()}
        st_user_CI = sorted(user_CI.items(), key=lambda d: d[1], reverse=True)
        rst["out_id"] = st_user_CI
    
    if wich == 'in' or wich=='both':
        user_CI = {g.vp.id[v]: g.vp.CI_in[v] for v in g.vertices()}
        st_user_CI = sorted(user_CI.items(), key=lambda d: d[1], reverse=True)
        rst["in_id"] = st_user_CI
    return rst


def get_users_and_sources(category='all'):
    sources = pd.read_csv('OL Classification/sources_classified.csv')
    sources['User id'] = sources['User id'].astype(str)
    users = pd.read_csv('ol_pnas/top_influencers_by_ci.csv')
    users['User id'] = users['User id'].astype(str)
    ol = users[(users.OL==1) & (users.S==0)]['User id'].to_list()
    influencers = users[(users.OL==0) & (users.S==0)]['User id'].to_list()
    
    
    if category=='all':
        sources = sources['User id'].to_list()
    elif category=='left':
        sources = sources[sources['type'].isin(['left','left leaning'])]['User id'].to_list()
    elif category=='right':
        sources = sources[sources['type'].isin(['right','right leaning'])]['User id'].to_list()
    elif category=='all_2':
        sources = sources[sources['type'].isin(['right','right leaning','left','left leaning'])]['User id'].to_list()
    elif category=='fake_and_bias':
        sources = sources[sources['type'].isin(['extremely biased left','extremely biased right','fake'])]['User id'].to_list()
    return ol,influencers,sources


def get_classes(V,category = 'all', top=1000):
    ol_all, influencers_all, sources_all = get_users_and_sources(category=category)

    # Get top influencers based on betweenness centrality
    top_influencers = {i[0] for i in build_CI_rank(V)['out_id'][:top]}

    # Get all unique vertex labels in the graph
    vertex_labels = set(V.vertex_properties["id"])

    # Separate influencers into different classes
    I = top_influencers.intersection(influencers_all)
    OLI = set(ol_all).intersection(vertex_labels).intersection(top_influencers)
    OL = set(ol_all).intersection(vertex_labels).difference(OLI)
    S = set(sources_all).intersection(vertex_labels)

    # Calculate Adopters (A) as vertices not in any class
    A = vertex_labels.difference(I | OL | OLI | S)

    print('N° Influencers:', len(I))
    print('N° OL:', len(OL))
    print('N° OLI:', len(OLI))
    print('N° Sources:', len(S))
    print('N° Adopters:', len(A))

    if (len(I)+len(OL)+ len(OLI) + len(S) + len(A)) != V.num_vertices():
        print('Number of nodes does not sum to the total!')

    return OL, OLI, I, A, S

def nx2gt(nxG):
    """
    Converts a networkx graph to a graph-tool graph.
    """
    # Phase 0: Create a directed or undirected graph-tool Graph
    print("converting ...")
    gtG = gt.Graph(directed=nxG.is_directed())

    # Add the Graph properties as "internal properties"
    for key, value in nxG.graph.items():
        # Convert the value and key into a type for graph-tool
        tname, value, key = get_prop_type(value, key)

        prop = gtG.new_graph_property(tname)  # Create the PropertyMap
        gtG.graph_properties[key] = prop     # Set the PropertyMap
        gtG.graph_properties[key] = value    # Set the actual value

    # Phase 1: Add the vertex and edge property maps
    # Go through all nodes and edges and add seen properties
    # Add the node properties first
    nprops = set()  # cache keys to only add properties once
    for node, data in list(nxG.nodes(data=True)):

        # Go through all the properties if not seen and add them.
        for key, val in data.items():
            if key in nprops:
                continue  # Skip properties already added

            # Convert the value and key into a type for graph-tool
            tname, _, key = get_prop_type(val, key)

            prop = gtG.new_vertex_property(tname)  # Create the PropertyMap
            gtG.vertex_properties[key] = prop     # Set the PropertyMap

            # Add the key to the already seen properties
            nprops.add(key)

    # Also add the node id: in NetworkX a node can be any hashable type, but
    # in graph-tool node are defined as indices. So we capture any strings
    # in a special PropertyMap called 'id' -- modify as needed!
    gtG.vertex_properties['id'] = gtG.new_vertex_property('string')

    # Add the edge properties second
    eprops = set()  # cache keys to only add properties once
    for src, dst, data in list(nxG.edges(data=True)):

        # Go through all the edge properties if not seen and add them.
        for key, val in data.items():
            if key in eprops:
                continue  # Skip properties already added

            # Convert the value and key into a type for graph-tool
            tname, _, key = get_prop_type(val, key)

            prop = gtG.new_edge_property(tname)  # Create the PropertyMap
            gtG.edge_properties[key] = prop     # Set the PropertyMap

            # Add the key to the already seen properties
            eprops.add(key)

    # Phase 2: Actually add all the nodes and vertices with their properties
    # Add the nodes
    vertices = {}  # vertex mapping for tracking edges later
    for node, data in list(nxG.nodes(data=True)):

        # Create the vertex and annotate for our edges later
        v = gtG.add_vertex()
        vertices[node] = v

        # Set the vertex properties, not forgetting the id property
        data['id'] = str(node)
        for key, value in data.items():
            gtG.vp[key][v] = value  # vp is short for vertex_properties

    # Add the edges
    for src, dst, data in list(nxG.edges(data=True)):

        # Look up the vertex structs from our vertices mapping and add edge.
        e = gtG.add_edge(vertices[src], vertices[dst])

        # Add the edge properties
        for key, value in data.items():
            gtG.ep[key][e] = value  # ep is short for edge_properties

    # Done, finally!
    return gtG
