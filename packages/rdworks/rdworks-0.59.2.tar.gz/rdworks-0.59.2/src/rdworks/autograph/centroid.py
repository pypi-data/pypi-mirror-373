import pandas as pd
import numpy as np


def centroid_medoid(communityAssignment, rmsdMatrix) -> list:
    """returns a list of centroids based on medoids

    Medoids are representative objects of a data set or a cluster within a data set 
    whose sum of dissimilarities to all the objects in the cluster is minimal.

    Args:
        communityAssignment: (list) list of community assignment correspoinding to the index of fileList
        rmsdMatrix: (numpy array) Matrix containing pairwise atomic RMSD between all conformers
    
    Returns:
        a list of centroids
    """
    N = rmsdMatrix.shape[0]
    community_indices = list(set(communityAssignment))
    centroids = []
    for C in community_indices:
        C_members = [x for x in range(N) if communityAssignment[x] == C]
        community_submatrix = rmsdMatrix[C_members, :][:, C_members]
        dist_sum = np.sum(community_submatrix, axis = 1)
        centroids.append(C_members[np.argmin(dist_sum)])
    return centroids


def diekstra(filtered_rmsd_matrix_community, i):
    '''Use Dijkstra's algorithm to find shortest path from index i to all other nodes'''
    # initialize lists
    visited = []
    unvisited = [x for x in range(filtered_rmsd_matrix_community.shape[0])]
    record = [np.inf for x in range(filtered_rmsd_matrix_community.shape[0])]#{x: np.inf for x in range(graph.shape[0])}
    record[i] = 0
    lastNode = [-1 for x in record]
    # repeat until all nodes have been visited
    while len(unvisited) > 0:
        visit_index = unvisited[np.argmin([record[x] for x in unvisited])]
        unvisited_neighbors = [x for x in unvisited if filtered_rmsd_matrix_community[visit_index, x] > 0]
        # Calculate distance to unvisited neighbor. If value is shorter than recorded, update distance.
        updateDist = filtered_rmsd_matrix_community[visit_index, :] + record[visit_index]
        for j in unvisited_neighbors:
            record[j] = np.min([updateDist[j], record[j]])
            if updateDist[j] < record[j]:
                lastNode[j] = visit_index
        # update visited/unvisited node list
        unvisited.remove(visit_index)
        visited.append(visit_index)
    return record, lastNode


def centroid_betweenness(num, communityAssignment, filtered_rmsd_matrix):
    # Provided with list of conformers assigned to communities, choose representative centroid by conformers of maximum in community betweenness
    # inputs
    # fileList: (list) names of xyz files for each conformer
    # communityAssignment: (list) list of community assignment correspoinding to the index of fileList
    # filtered_rmsd_matrix: {np.array) RMSD matrix between conformers, except assigning distances above threshold to zero
    communityList = list(set(communityAssignment))
    centralNodes = []
    comm_size = []
    for C in communityList:
        C_members = [x for x in range(num) if communityAssignment[x] == C]
        C_member_files = [x for x in C_members]
        comm_size.append(len(C_members))
        community_subgraph = filtered_rmsd_matrix[C_members, :][:, C_members]
        community_betweenness = np.zeros(len(C_members))
        for i in range(len(C_member_files)):
            record, lastnode = diekstra(community_subgraph, i)
            for j in range(len(C_member_files)):
                previous_node = lastnode[j]
                while previous_node != -1:
                    community_betweenness[previous_node] += 1
                    previous_node = lastnode[previous_node]
        max_betweenness_index = np.argmax(community_betweenness)
        centralNodes.append(C_member_files[max_betweenness_index])

    # Sort centers by size of clusters in descending order
    centralDf = pd.DataFrame({'size': comm_size}, index = centralNodes)
    centralDf.sort_values(by = 'size', ascending = False, inplace = True)

    return list(centralDf.index)


def centroid_autograph(N, communityAssignment, rmsdMatrix, threshold, centroid_selection='betweenness', filteredAffinityMatrix=None):
    '''Return file names of conformers designated as centroids. If energy is provided, find lowest energy conformers in each cluster. Otherwise choose by maximum in-cluster weighted degree'''
    if centroid_selection == 'betweenness':
        return centroid_betweenness(N, communityAssignment, rmsdMatrix * rmsdMatrix < np.sqrt(-np.log(threshold))) # add filtered rmsd matrix
    else:
        print('centroid criterion not recognized. Use keywords "degree", "eccentricity", or "betweenness" for centroid_selection or provide an energy output to base the selection')