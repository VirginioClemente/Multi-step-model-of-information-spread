# Author: Matteo Serafino <m.serafi00@ccny.cuny.edu>, 
#
# License: GNU General Public License v3.0


import glob
import networkx as nx
import time
from  utilities import nx2gt,add_CI_to_graph

import graph_tool.all as gt

path = 'PATH TO VALIDATED NETWORK'
validated_networks = ['Right.gt','Full.gt','Left.gt']


for file in validated_networks:
    print('Adding CI to ',file)
    G=  gt.load_graph(path+file)
    #graph = nx.read_graphml(path + file)
    
    #convert to gt
    #G = nx2gt(graph)
    # Add ci
    G_ = add_CI_to_graph(G)

    # Save gt version 
    G_.save(path + file.replace('graphml','gt'))
    print('CI added to ',file)
  


