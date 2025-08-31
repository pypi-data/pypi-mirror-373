import numpy as np
import math
import operator
import gzip
import base64

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from rdkit import Chem

from rdworks.autograph.centroid import centroid_medoid


def compress_string(text: str) -> str:
    """compress string to base64-encoded string.

    Args:
        text (str): original string.

    Returns:
        str: base64-encoded compressed string.
    """
    compressed_bytes = gzip.compress(text.encode('utf-8'))
    return base64.b64encode(compressed_bytes).decode('utf-8')


def decompress_string(compressed_text: str) -> str:
    """decompress base64-encoded string to original string.

    Args:
        compressed_text (str): base64-encoded compressed string.

    Returns:
        str: original string.
    """
    compressed_bytes = base64.b64decode(compressed_text)
    decompressed_text = gzip.decompress(compressed_bytes).decode('utf-8')
    return decompressed_text


def compute(fn:Callable, largs: list, **kwargs) -> list:
    max_workers = kwargs.get('max_workers', 1)
    chunksize   = kwargs.get('chunksize', 10)
    progress    = kwargs.get('progress', False)
    desc = kwargs.get('desc', 'Progress')
    n = len(largs)
    if max_workers > 1:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            if progress:
                results = list(tqdm(executor.map(fn, largs, chunksize=chunksize), desc=desc, total=n))
            else:
                results = list(executor.map(fn, largs, chunksize=chunksize))
    else:
        if progress:
            results = [ fn(*larg) for larg in tqdm(largs, desc=desc, total=n) ]
        else:
            results = [ fn(*larg) for larg in largs ]
    return results



def precheck_path(path:str | Path) -> Path:
    """Prechecks filename or path and returns a string for the pathlib.PosixPath.

    Args:
        path (Union[str, PosixPath]): filename or path.
        origin (str): origin of data.

    Raises:
        FileNotFoundError: if the path is not found.

    Returns:
        str: a string for the path.
    """
    if isinstance(path, Path):
        pass
    elif isinstance(path, str):
        path = Path(path)
    if path.exists() and path.is_file():
        return path
    else:
        raise FileNotFoundError(f"File path {path.as_posix()} does not exist.")
    


def guess_mol_id(lprops:list[dict]) -> tuple[str, int, int]:
    """Guesses molecular ID from SDF properties.

    Molecular ID is guessed by the coverage(=count of unique values divided by total count).
    A property suitable for ID should have coverage of 1.0.

    Args:
        lprops (List[dict]): a list of properties.

    Returns:
        Tuple[str, int, int]: (property, count of unique values, total count)
    """
    f = {} # unique occurrence
    for props in lprops:
        for k in props:
            v = props[k]
            # float is not suitable for molecular id
            if isinstance(v, float): 
                continue 
            if not (k in f): 
                f[k] = set()
            # str(int) is acceptable for molecular id
            if isinstance(v, int): 
                f[k].add(str(v))
            elif isinstance(v, str):
                f[k].add(v)
    r = [(k, len(f[k]), -max([len(x) for x in f[k]])) for k in f]
    r = sorted(r, key=operator.itemgetter(1,2))
    try:
        (property_key, count, total) = (r[-1][0], r[-1][1], len(lprops))
    except IndexError:
        (property_key, count, total) = (None, 0, 0)
    return (property_key, count, total)


def dict_to_simplenamespace(data):
    if isinstance(data, dict):
        return SimpleNamespace(**{k: dict_to_simplenamespace(v) for k, v in data.items()})
    elif isinstance(data, list):
        return [dict_to_simplenamespace(item) for item in data]
    else:
        return data
    

def recursive_round(data:Any, decimals:int=2) -> Any:
    """Recursively round float values to a given decimal places.

    Args:
    data: The input data, which can be a list, dictionary, or any
            other data type. It can contain nested lists and dictionaries.
    decimals: number of decimal places.
    """
    if not isinstance(decimals, int) or decimals < 0:
        raise ValueError("decimals must be a non-negative integer.")

    def _recursive_round(current_item):
        if isinstance(current_item, float):
            return round(current_item, decimals)
        elif isinstance(current_item, np.float64):
            return round(float(current_item), decimals)
        elif isinstance(current_item, list):
            return [_recursive_round(item) for item in current_item]
        elif isinstance(current_item, dict):
            return {key: _recursive_round(value) for key, value in current_item.items()}
        else:
            return current_item

    return _recursive_round(data)


def fix_decimals_in_list(in_list:list, decimals:int=2) -> list:
    """Fixes the decimal places of all float values in a list.

    Args:
        list: The list to fix.
        decimals (int): The number of decimal places to fix the float values to.

    Returns:
        list: a list with the float values fixed to the specified number of decimal places.
    """

    out_list = []
    for item in in_list:
        if isinstance(item, float):
            out_list.append(round(item, decimals))
        elif isinstance(item, dict):
            out_list.append(fix_decimals_in_dict(item, decimals))
        elif isinstance(item, list) or isinstance(item, tuple):
            out_list.append(fix_decimals_in_list(item, decimals))
        else:
            out_list.append(item)
    return out_list


def fix_decimals_in_dict(in_dict:dict, decimals:int=2) -> dict:
    """Fixes the decimal places of all float values in a dictionary.

    Args:
        dictionary: The dictionary to fix.
        decimals (int): The number of decimal places to fix the float values to.

    Returns:
        dict: a dictionary with the float values fixed to the specified number of decimal places.
    """
    out_dict = {}
    for k, v in in_dict.items():
        if isinstance(v, float):
            out_dict[k] = round(v, decimals)
        elif isinstance(v, list) or isinstance(v, tuple):
            out_dict[k] = fix_decimals_in_list(v, decimals)
        elif isinstance(v, dict):
            out_dict[k] = fix_decimals_in_dict(v, decimals)
        else:
            out_dict[k] = v
    return out_dict


def convert_tril_to_symm(lower_triangle_values:list) -> np.ndarray:
    """Converts lower triangle values to a symmetric full matrix.

    Args:
        lower_triangle_values (list): list of lower triangle matrix values.

    Returns:
        np.ndarray: numpy array of a symmetric full matrix.
    """
    n = math.ceil(math.sqrt(len(lower_triangle_values)*2))
    rmsd_matrix = np.zeros((n,n))
    rmsd_matrix[np.tril_indices(n, k=-1)] = lower_triangle_values
    symm_matrix = np.maximum(rmsd_matrix, rmsd_matrix.transpose())
    return symm_matrix


def convert_triu_to_symm(upper_triangle_values:list) -> np.ndarray:
    """Converts upper triangle values to a symmetric full matrix.

    Args:
        upper_triangle_values (list): list of upper triangle matrix values.

    Returns:
        np.ndarray: numpy array of a symmetric full matrix.
    """
    n = math.ceil(math.sqrt(len(upper_triangle_values)*2))
    rmsd_matrix = np.zeros((n,n))
    rmsd_matrix[np.triu_indices(n, k=1)] = upper_triangle_values
    symm_matrix = np.maximum(rmsd_matrix, rmsd_matrix.transpose())
    return symm_matrix


def _QT_diameter(rmsd_matrix:np.ndarray, A:list) -> float:
    """A subroutine for `QT()` to returns the maximum pairwise distance.

    Args:
        rmsd_matrix (np.ndarray): numpy array of rmsd.
        A (list): list of indexes.

    Returns:
        float: maximum pairwise distance.
    """
    return np.max(rmsd_matrix[A][:,A])


def _QT_clustering(rmsd_matrix:np.ndarray, G:set, threshold:float, clusters:list) -> list:
    """A subroutine for `QT()` to perform QTC algorithm.

    Args:
        rmsd_matrix (np.ndarray): pairwise rmsd matrix.
        G (set): set of indexes used for recursive calling.
        threshold (float): quality threshold (A).
        clusters (list): list of clusters used for recursive calling.

    Returns:
        list: a list of final clusters.
    """

    if len(G) <= 1:
        clusters.append(G)
        return
    C = [] # cluster candidates
    for i in G:
        flag = True
        A = [i]
        A_diameter = 0.0 # max of pairwise distances
        while flag and A != G:
            # find j that minimize diameter of A + [j]
            diameters = [(_QT_diameter(rmsd_matrix, A + [j]), j) for j in G if j not in A]
            if len(diameters) == 0:
                flag = False
            else:
                (min_diameter, min_j) = min(diameters, key=lambda x: x[0])
                if min_diameter > threshold:
                    flag = False
                else:
                    A += [min_j]
                    A_diameter = min_diameter
        C.append((A, A_diameter))
    C = sorted(C, key=lambda x: (len(x[0]), -x[1]), reverse=True)
    # if cardinality of C is tied, smaller diameter is picked
    largest_C = set(C[0][0])
    clusters.append(largest_C)
    _QT_clustering(rmsd_matrix, G-largest_C, threshold, clusters)


def QT(rmsd_matrix:np.ndarray, threshold:float) -> tuple:
    """Perform QT clustering.

    Args:
        rmsd_matrix (np.ndarray): pairwise rmsd matrix.
        threshold (float): quality threshold (A)

    Returns:
        tuple: (cluster assignment, centroid indices)
    """
    N = rmsd_matrix.shape[0]
    clusters = []
    _QT_clustering(rmsd_matrix, set(list(range(N))), threshold, clusters)
    # ex. clusters=  [{6, 7, 11}, {4, 5, 8}, {0}, {1}, {10}, {9}, {2}, {3}]
    cluster_assignment = [None,] * N
    for cluster_idx, indices in enumerate(clusters):
        for conf_idx in indices:
            cluster_assignment[conf_idx] = cluster_idx
    centroid_indices = centroid_medoid(cluster_assignment, rmsd_matrix)
    return cluster_assignment, centroid_indices


# def rdmol_to_graph(rdmol:Chem.Mol) -> nx.Graph:
#     """Converts rdkit.Chem.Mol to a networkx graph object.

#     Args:
#         rdmol (Chem.Mol): input molecule.

#     Returns:
#         nx.Graph: networkx graph object.
#     """
#     G = nx.Graph()
#     for atom in rdmol.GetAtoms():
#         G.add_node(atom.GetIdx(), # 0-based index
#                    atomic_num=atom.GetAtomicNum(),
#                    formal_charge=atom.GetFormalCharge(),
#                    chiral_tag=atom.GetChiralTag(),
#                    hybridization=atom.GetHybridization(),
#                    num_explicit_hs=atom.GetNumExplicitHs(),
#                    is_aromatic=atom.GetIsAromatic())
#     for bond in rdmol.GetBonds():
#         G.add_edge(bond.GetBeginAtomIdx(),
#                    bond.GetEndAtomIdx(),
#                    bond_type=bond.GetBondType())
#     return G


# def rdmol_to_graph_(rdmol:Chem.Mol) -> nx.Graph:
#     """Converts rdkit.Chem.Mol to a networkx graph object (another implementation).

#     Args:
#         rdmol (Chem.Mol): input molecule.

#     Returns:
#         nx.Graph: networkx graph object.
#     """ 
#     atomic_nums = [atom.GetAtomicNum() for atom in rdmol.GetAtoms()]
#     formal_charges = [atom.GetFormalCharge() for atom in rdmol.GetAtoms()]
#     ad_matrix = Chem.GetAdjacencyMatrix(rdmol, useBO=True)
#     # useBO: (optional) toggles use of bond orders in calculating the matrix. Default value is 0.
#     # RETURNS: a Numeric array of floats containing the adjacency matrix
#     # [[0. 1. 0. 0. 0. 0. 0. 0. 0.]
#     # [1. 0. 1. 1. 1. 0. 0. 0. 0.]
#     # [0. 1. 0. 0. 0. 0. 0. 0. 0.]
#     # [0. 1. 0. 0. 0. 0. 0. 0. 0.]
#     # [0. 1. 0. 0. 0. 1. 0. 1. 0.]
#     # [0. 0. 0. 0. 1. 0. 2. 0. 0.]
#     # [0. 0. 0. 0. 0. 2. 0. 0. 0.]
#     # [0. 0. 0. 0. 1. 0. 0. 0. 2.]
#     # [0. 0. 0. 0. 0. 0. 0. 2. 0.]]
#     for i,(a_num,f_c) in enumerate(zip(atomic_nums, formal_charges)):
#         if f_c !=0:
#             ad_matrix[i,i] = a_num + f_c
#         else:
#             ad_matrix[i,i] = a_num
#     G = nx.from_numpy_array(ad_matrix)
#     return G


# def graph_to_rdmol(G:nx.Graph) -> Chem.Mol:
#     """Converts a networkx graph object to rdkit.Chem.Mol object.

#     Args:
#         G (nx.Graph): a networkx graph.

#     Returns:
#         Chem.Mol: rdkit.Chem.Mol object.
#     """
#     rdmol = Chem.RWMol()
#     atomic_nums = nx.get_node_attributes(G, 'atomic_num')
#     chiral_tags = nx.get_node_attributes(G, 'chiral_tag')
#     formal_charges = nx.get_node_attributes(G, 'formal_charge')
#     node_is_aromatics = nx.get_node_attributes(G, 'is_aromatic')
#     node_hybridizations = nx.get_node_attributes(G, 'hybridization')
#     num_explicit_hss = nx.get_node_attributes(G, 'num_explicit_hs')
#     node_to_idx = {}
#     for node in G.nodes():
#         a=Chem.Atom(atomic_nums[node])
#         a.SetChiralTag(chiral_tags[node])
#         a.SetFormalCharge(formal_charges[node])
#         a.SetIsAromatic(node_is_aromatics[node])
#         a.SetHybridization(node_hybridizations[node])
#         a.SetNumExplicitHs(num_explicit_hss[node])
#         idx = rdmol.AddAtom(a)
#         node_to_idx[node] = idx
#     bond_types = nx.get_edge_attributes(G, 'bond_type')
#     for edge in G.edges():
#         first, second = edge
#         ifirst = node_to_idx[first]
#         isecond = node_to_idx[second]
#         bond_type = bond_types[first, second]
#         rdmol.AddBond(ifirst, isecond, bond_type)
#     Chem.SanitizeMol(rdmol)
#     return rdmol