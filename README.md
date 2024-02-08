# Analysis of flows in social media uncovers a new multi-step model of information spread

Analysis codes to reproduce the results of the paper:
"Analysis of flows in social media uncovers a new multi-step model of information spread" authored by M. Serafino, G.V. Clemente, J. Flaminio, B. K. Szymanskici, O. Lizardo and H.A. Makse.

By using this code, you agree with the following points:

The code is provided without any warranty or conditions of any kind. We assume no responsibility for errors or omissions in the results and interpretations following from applications of the code.

You commit to cite our paper (above) in publications where you use this code.

The dataset containing the retweet networks and the tweet ids of the tweets used in the article is available here: https://osf.io/e395q/.

Below are listed the steps and the corresponding codes followed to reproduce the results proposed in the reference paper.

1. The first step involves constructing the retweet network. The codes related to this step are contained in the Notebook/retweet_network.ipynb.
 
2. Subsequently, once the retweet network is constructed, link validation is performed considering the weights associated with each connection. The code related to this step is contained in py_files/validation.py, and described in the notebook Notebook/Validating Connections.ipynb.
 
3. Next, we conducted the classification of influencers using the code contained in py_files/compute_ci.py. This allowed us to associate a CI value with each node, enabling us to identify those we have defined as influencers.

4. The final step involves the application of BFS algorithm. The code defining this algorithm is contained in py_files/bfs.py, and the reference notebook is Notebook/BFS.ipynb.


Moreover in the folder OL classication/ we include the list of classified OL, as well as categories and list of sources. 

Please refer to the paper for further clarifications regarding the steps just described. 

# Collective Influence algorithm
To compute the Collective Influence ranking of nodes in the retweet networks, you must first compile the cython code with : python setup.py build_ext --inplace

Check https://github.com/alexbovet/information_diffusion
