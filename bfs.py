# Author: Matteo Serafino <m.serafi00@ccny.cuny.edu>, 
#
# License: GNU General Public License v3.0


from  utilities import build_CI_rank,get_classes
import graph_tool.all as gt

import numpy as np
import networkx as nx
import pickle
import pandas as pd 
import glob
import json

results_path = 'PATH TO STORE RESULTS'
validated_path = 'PATH TO VALIDATED NETWORKS'
validated_networks = ['Left.gt','Right.gt','Full.gt']

def create_dataframe(skeleton):
    to_df = []

    for s in skeleton:
        for ss in skeleton[s]:
            to_df.append([s, ss[0], ss[1], ss[2], ss[3]])

    df = pd.DataFrame(to_df, columns=['Steps', 'Sources', 'Targets', 'Connections', 'Weights'])
    return df



def load_and_process_graph(v_path, category='all', 
                           validated_path = validated_path,
                           results_path=results_path,
                           return_=False,print_=True):
    
    V = gt.load_graph(validated_path + v_path)
    
    OL, OLI, I, A, S = get_classes(V, category=category, top=1000)
    
    vertex_labels = V.vertex_properties["id"]
    # Get weights of all edges
    weights = V.edge_properties["weight"]

    step = 1
    skeleton, skeleton_users = {}, {}
    all_explored_set = set()
    
    skeleton[step - 1] = []
    skeleton_users[step] = {}

    # Create a hashed graph for faster edge removal
    connections_all = list(V.edges())

    def process_targets(targets, targets_name, sources_name, weights, connections):
        if targets_name not in skeleton_users[step]:  
            skeleton_users[step][targets_name] = set()
            
        if not connections:
            skeleton[step - 1].append([sources_name.split('_')[-1], targets_name, len(connections), 0])
            skeleton_users[step][targets_name].update(set())
            return

        # Get weights
        weights_ = sum([weights[i] for i in connections])
        # Get targets names
        targets_names = set([vertex_labels[i] for i in set(np.concatenate([(i.source(), i.target()) for i in connections]))])
        skeleton_users[step][targets_name].update(targets_names)
        skeleton[step - 1].append([sources_name.split('_')[-1], targets_name, len(connections), weights_])
        if print_:
            print(sources_name.split('_')[-1], targets_name, len(connections), weights_)

    # Initial step
    for targets, targets_name in zip([OL, OLI, I, A], ['OL', 'OLI', 'I', 'A']):
        sources_name = 'S'
        connections = [i for i in connections_all if (vertex_labels[i.source()] in S and vertex_labels[i.target()] in targets)]
        # Consider only retweet with weight at et least 2
        connections = [i for i in connections if weights[i]>1]
        
        process_targets(targets, targets_name, sources_name, weights, connections)
        all_explored_set.update(skeleton_users[step][ targets_name])
    
    print(len(all_explored_set))
    step += 1

    # Following steps
    while True:
        skeleton[step - 1] = []
        skeleton_users[step] = {}
        sources = skeleton_users[step - 1]
        for targets, targets_name in zip([OL, OLI, I, A], ['OL', 'OLI', 'I', 'A']):
            for sources_name in sources:
                S_ = skeleton_users[step - 1][sources_name]
                connections = [i for i in connections_all if
                               (vertex_labels[i.source()] in S_ and
                                vertex_labels[i.target()] in targets and
                                vertex_labels[i.target()] not in all_explored_set)]
                process_targets(targets, targets_name, sources_name, weights, connections)

        
        new_users = sum([len(i) for i in skeleton_users[step].values()])
        if new_users == 0:
            break

        # Update visited per step
        for value in skeleton_users[step].values():
            all_explored_set.update(value)

        step += 1

        print(len(all_explored_set))
        
    df = create_dataframe(skeleton)
    # Save results
    df.to_csv(results_path+v_path.replace('.gt','_bfs.csv'),index=False)
    
    with open(results_path+v_path.replace('.gt','_bfs_nodes.txt'),'wb') as file:
        pickle.dump(skeleton_users, file)
        
    if return_: 
        return skeleton, skeleton_users


if __name__ == "__main__":
        
    # BFS
    for G,category in zip(validated_networks,['left','right','all','all_2']):
        print(G,category)
        load_and_process_graph(G,category=category,validated_path=validated_path)
        print('SBF created for', G)
