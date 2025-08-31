"""
@author: Roy Gonzalez-Aleman                            [roy_gonzalez@fq.uh.cu]
@author: Daniel Platero Rochart                      [daniel.platero@gmail.com]
"""
from collections import deque, OrderedDict
from typing import Tuple, Optional

import numpy as np
import pandas as pd

from bitarray import util as bu
from bitarray import bitarray as ba

from ..autograph.centroid import centroid_medoid



def convert_to_bitarr_matrix(rmsdMatrix:np.array, cutoff:float) -> OrderedDict:
    """
    Convert RMSD binary-encoded square matrix.
    Pairwise similarity is saved in RAM as bits (dict of bitarrays), not floats.
    Returns:
        matrix : collections.OrderedDict. dict of bitarrays.
    """
    N = rmsdMatrix.shape[0]
    cutoff = np.full(N, cutoff, dtype=np.float32)
    # numpy.full(shape, fill_value, dtype=None, order='C', *, like=None)
    # Return a new array of given shape and type, filled with fill_value.
    matrix = OrderedDict()
    to_explore = range(N)
    for i in to_explore:
        rmsd_ = rmsdMatrix[i,:]
        # mdtraj.rmsd(target, reference, frame=0, atom_indices=None, parallel=True, precentered=False)
        # Compute RMSD of all conformations in target to a reference conformation. Note, this will center the conformations in place.
        vector_np = np.less_equal(rmsd_, cutoff)
        # Return the truth value of (x1 <= x2) element-wise.
        bitarr = ba()
        bitarr.pack(vector_np.tobytes())
        bitarr.fill()
        matrix.update({i: bitarr})
    return matrix



def calc_matrix_degrees(unclustered_bit, matrix):
    """
    Calculate number of neighbors (degree) of unclustered nodes in matrix.

    Parameters
    ----------
    unclustered_bit : bitarray.bitarray
        bitarray with indices of unclustered nodes turned on.
    matrix : collections.OrderedDict
        dict of bitarrays.

    Returns
    -------
    degrees : numpy.ndarray
        array containing each node degree. Clustered nodes have degree = 0.

    """
    one = ba('1')
    degrees = np.zeros(len(unclustered_bit), dtype=np.int32)
    for node in unclustered_bit.itersearch(one):
        try:
            degrees[node] = matrix[node].count()
        except KeyError:
            pass
    return degrees


def colour_matrix(degrees, matrix):
    """
    Greedy coloring of bit-encoded RMSD matrix.

    Parameters
    ----------
    degrees : numpy.ndarray
        array containing each node degree. Clustered nodes have degree = 0.
    matrix : collections.OrderedDict
        dict of bitarrays.

    Returns
    -------
    colors : numpy.ndarray
        array of colors assigned to each node of the matrix.
    """
    # Constants ---------------------------------------------------------------
    N = degrees.size
    m = len(matrix)
    one = ba('1')
    xcolor = 0
    # Initialize containers ---------------------------------------------------
    ordered_by_degrees = iter((-degrees[:m]).argsort())
    colors = np.zeros(N, dtype=np.int32)
    colored = ba(N)
    colored.setall(0)
    seen = set()
    while True:
        # Retrieve the max-degree node ----------------------------------------
        max_node = next(ordered_by_degrees)
        if max_node in seen:
            continue
        seen.add(max_node)
        xcolor += 1
        not_neighbors = ~ matrix[max_node]
        not_colored = ~colored
        candidates = not_neighbors & not_colored
        # Nodes passing conditions (not-neighb, not-colored, not-neighb) ------
        passed = [max_node]
        for candidate in candidates.itersearch(one):
            passed.append(candidate)
            try:
                candidates &= ~matrix[candidate]
            except KeyError:
                continue
            if not candidates.any():
                break
        seen.update(passed)
        # Deliver a color class to passed nodes -------------------------------
        colors[passed] = xcolor
        colored = ba()
        colored.pack(colors.astype(np.bool_).tobytes())
        if colored.count(0) == 0:
            break
    return colors


def bitarray_to_np(bitarr):
    """
    Convert from bitarray.bitarray to numpy.ndarray efficiently.

    Parameters
    ----------
    bitarr : bitarray.bitarray
        a bitarray.

    Returns
    -------
    numpy.ndarray
        boolean bitarray equivalent to the binary bitarray input object.
    """
    return np.unpackbits(bitarr).astype(np.bool_)


def do_bit_cascade(big_node, degrees, colors, matrix, max_):
    """
    Perform succesive AND operations between an initial bitarray and subsequent
    bitarray candidates to search for a clique.

    Parameters
    ----------
    big_node : int
        node whose bitarray will start the operations.
    degrees : numpy.ndarray
        array containing each node degree. Clustered nodes have degree = 0.
    colors : numpy.ndarray
        array of colors assigned to each node of the matrix.
    clustered_bit : bitarray.bitarray
        bitarray with indices of clustered nodes turned on.
    matrix : collections.OrderedDict
        dict of bitarrays.
    max_ : int
        Stop iterative AND operations after the initial bitarray has max_
        bits turned on.

    Returns
    -------
    init_cascade : bitarray.bitarray
        initial bitarray before any AND operation.
    ar : numpy.ndarray
        array of nodes forming a clique.
    """
    init_cascade = matrix[big_node]
    # .... recovering neighbors and their information .........................
    neighb = bitarray_to_np(init_cascade).nonzero()[0]
    neighb_colors = colors[neighb]
    if len(set(neighb_colors.tolist())) <= max_:
        return None
    neighb_degrees = degrees[neighb]
    g = np.bincount(neighb_colors)
    neighb_g = g[neighb_colors]
    # .... ordering neighbors by g ---> colors ---> degrees ...................
    idx = np.lexsort([-neighb_degrees, neighb_colors, neighb_g])
    candidates_info = zip(neighb[idx], neighb_colors[idx])

    # .... BitCascade considering divergence ..................................
    counter = 0
    seen = set()
    for candidate, color in candidates_info:
        if (color in seen) or (not init_cascade[candidate]):
            continue
        seen.add(color)
        init_cascade = matrix[candidate] & init_cascade
        counter += 1
        COUNT = init_cascade.count()
        if (COUNT <= max_):
            return None
        if counter >= COUNT:
            break
    ar = np.nonzero(np.unpackbits(init_cascade).astype(np.bool_))[0]
    return init_cascade, ar


def set_to_bitarray(set_, N):
    """
    Convert from python set to bitarray.bitarray.

    Parameters
    ----------
    set_ : set
        a python set.
    N : int
        lenght of the desired bitarray. It must be greater than the maximum
        value of indices present in set.

    Returns
    -------
    bitarr : bitarray.bitarray
        bitarray of lenght N with indices present in set turned on.
    """
    zero_arr = np.zeros(N, dtype=np.bool_)
    zero_arr[list(set_)] = 1
    bitarr = ba()
    bitarr.pack(zero_arr.tobytes())
    return bitarr


def get_cluster_stats(clusters):
    """
    Get "cluster_statistics.txt" containing clusterID, cluster_size, and
    cluster percentage from trajectory.

    Parameters
    ----------
    clusters : numpy.ndarray
        array of clusters ID.
    outdir : str
        Path where to create the VMD visualization .log.

    Returns
    -------
    clusters_df : pandas.DataFrame
        dataframe with cluster_statistics info.
    """
    clusters_df = pd.DataFrame(columns=['cluster_id', 'size', 'percent'])
    clusters_df['cluster_id'] = list(range(0, clusters.max() + 1))
    sizes = []
    for x in clusters_df.cluster_id:
        sizes.append(len(np.where(clusters == x)[0]))
    clusters_df['size'] = sizes

    sum_ = clusters_df['size'].sum()
    percents = [round(x / sum_ * 100, 4) for x in clusters_df['size']]
    clusters_df['percent'] = percents

    return clusters_df


def BitQT(rmsdMatrix:np.array, cutoff:float, min_clust_size:int=2, nclust:Optional[int]=None) -> Tuple:
    """BitQT clustering
    Returns:
        (cluster_assignment, centroid_indices)
    """
    matrix = convert_to_bitarr_matrix(rmsdMatrix, cutoff)
    # ++++ Tracking clust/uNCLUSTERed bits to avoid re-computations +++++++++++
    N = len(matrix[0])
    m = len(matrix)
    unclust_bit = ba(N)
    unclust_bit.setall(1)
    clustered_bit = unclust_bit.copy()
    clustered_bit.setall(0)
    zeros = np.zeros(N, dtype=np.int32)
    # ++++ Save clusters in an array (1 .. N) +++++++++++++++++++++++++++++++++
    clusters_array = np.zeros(N, dtype=np.int32)
    NCLUSTER = 0
    clustered = set()
    nmembers = []
    # ++++ Coloring ordered vertices (1 .. N) +++++++++++++++++++++++++++++++++
    degrees = calc_matrix_degrees(unclust_bit, matrix)
    ordered_by_degs = degrees.argsort()[::-1]
    colors = colour_matrix(ordered_by_degs, matrix)
    # colors[np.frombuffer(clustered_bit.unpack(), dtype=np.bool)] = 0

    # =========================================================================
    # 2. Main algorithm: BitQT !
    # =========================================================================
    while any(degrees):
        NCLUSTER += 1
        # ++++ Find a big clique early ++++++++++++++++++++++++++++++++++++++++
        big_node = degrees.argmax()
        bit_clique, big_clique = do_bit_cascade(big_node, degrees, colors,
                                                matrix, 0)
        big_clique_size = big_clique.size
        # ++++ Find promising nodes +++++++++++++++++++++++++++++++++++++++++++
        biggers = degrees > big_clique_size
        biggers[big_clique] = False
        cluster_colors = colors[big_clique]
        biggers_colors = colors[biggers]
        promising_colors = np.setdiff1d(biggers_colors, cluster_colors)
        promising_nodes = deque()
        for x in promising_colors:
            promising_nodes.extend(((colors == x) & biggers).nonzero()[0])
        # ++++ Explore all promising nodes ++++++++++++++++++++++++++++++++++++
        cum_found = big_clique
        while promising_nodes:
            node = promising_nodes.popleft()
            try:
                bit_clique, clique = do_bit_cascade(node, degrees, colors,
                                                    matrix, big_clique_size)
                CLIQUE_SIZE = len(clique)
            except TypeError:
                CLIQUE_SIZE = 0
            # ++++ Cumulative update only if biggers candidates are found +++++
            if CLIQUE_SIZE > big_clique_size:
                big_node = node
                big_clique = clique
                big_clique_size = big_clique.size
                # ++++ Repeat previous condition ++++++++++++++++++++++++++++++
                cum_found = np.concatenate((cum_found, big_clique))
                biggers = degrees > big_clique_size
                biggers[cum_found] = False
                cluster_colors = colors[big_clique]
                biggers_colors = colors[biggers]
                promising_colors = np.setdiff1d(biggers_colors, cluster_colors)
                promising_nodes = deque()
                for x in promising_colors:
                    promising_nodes.extend(((colors == x) & biggers).nonzero()[0])
        nmembers.append(big_clique_size)

        if (big_clique_size < min_clust_size) or (nclust and NCLUSTER == nclust):
            break

        # ++++ Save new cluster & update NCLUSTER +++++++++++++++++++++++++++++
        clusters_array[big_clique] = NCLUSTER
        # ++++ Update (un)clustered_bit +++++++++++++++++++++++++++++++++++++++
        clustered.update(big_clique)
        clustered_bit = set_to_bitarray(clustered, N)
        unclust_bit = ~clustered_bit
        # ++++ Hard erasing of clustered frames from matrix +++++++++++++++++++
        degrees = zeros.copy()
        for x in unclust_bit[:m].itersearch(ba('1')):
            degrees[x] = matrix[x].count()
            if bu.count_and(matrix[x], clustered_bit):
                matrix[x] &= (matrix[x] ^ clustered_bit)

    # =========================================================================
    # 3. Output
    # =========================================================================
    # cluster_stats = get_cluster_stats(clusters_array[:m], args.outdir)

    cluster_assignment = list(clusters_array[:m])
    centroid_indices = centroid_medoid(cluster_assignment, rmsdMatrix)

    return cluster_assignment, centroid_indices