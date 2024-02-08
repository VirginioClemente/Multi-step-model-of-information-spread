# Author: G. Virginio Clemente <g.V.Clemente@outlook.it>, 
#
# License: GNU General Public License v3.0


import numpy as np
import graph_tool.all as gt
from scipy.sparse import find 
from tqdm import tqdm

def Graph_validation(adj_weigh, ordered_ids, b_in, b_out):
    """
    Validates the links in a graph based on a statistical criterion.
    
    Parameters:
    - adj_weigh: The adjacency matrix of the graph, possibly sparse, where the weights of the edges are stored.
    - ordered_ids: A list of identifiers corresponding to the nodes in the graph, ordered by their position in the graph structure.
    - b_in: Model parameter, used in the validation process for incoming links.
    - b_out: Model parameter, used in the validation process for outgoing links.
    
    Returns:
    - A set of edges that meet the validation criterion.
    """
    
    # Number of nodes in the graph
    n_nodes = adj_weigh.shape[0]
    
    # Initialize an empty graph
    edge_set = set()

    # Find the indices (i, j) and values of non-zero elements in adj_weigh
    i, j, vals = find(adj_weigh)

    # Iterate over non-zero elements to validate edges
    for idx in tqdm(range(len(i))):
        row, col = i[idx], j[idx]
        # Calculate the expected value and the standard deviation based on the model parameters b_in and b_out
        expected_value = 1 / (b_in[row] + b_out[col])
        sigma = 1 / (b_in[row] + b_out[col])
        # Calculate the z-score for the edge n.b. standard deviation and expected value have the same value.
        z_score = (vals[idx] - expected_value) / sigma
        
        # If the z-score is within the acceptable range, add the edge to the set
        if np.absolute(z_score) <=1:
            edge_set.add((ordered_ids[col], ordered_ids[row],vals[idx]))

    # Return The set of edges
    return edge_set
