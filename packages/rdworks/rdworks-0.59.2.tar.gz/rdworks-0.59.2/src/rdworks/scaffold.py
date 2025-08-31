
"""
This module provides functions to break a molecule into scaffolds.
"""

import collections
import operator
import itertools

from typing import Any, Optional, List, Tuple

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit.Chem import BRICS, AllChem

from .std import desalt_smiles


def remove_exocyclic(rdmol:Chem.Mol) -> Chem.Mol:
    """Removes exocyclic chains or all terminal side chains.

    It is equivalent to the `MurckoScaffold.GetScaffoldForMol(mol)`.
    Args:
        rdmol (Chem.Mol): input molecule.

    Returns:
        Chem.Mol: output molecule.
    """
    
    # all bonds between cyclic and acyclic atoms (single bond)
    bis = rdmol.GetSubstructMatches(Chem.MolFromSmarts('[!R][R]'))
    
    # bond indexes to cut
    xbs = []
    for bi in bis:
        b  = rdmol.GetBondBetweenAtoms(bi[0],bi[1])
        fg_smi = Chem.MolToSmiles(
            Chem.FragmentOnBonds(rdmol,[b.GetIdx()],addDummies=False)).split(".")
        fg_mol = [Chem.MolFromSmiles(x) for x in fg_smi]
        # ring count
        fg_rc  = [rdMolDescriptors.CalcNumRings(g) for g in fg_mol]
        if 0 in fg_rc: # if one of the fragmented parts has no ring system
            xbs.append(b.GetIdx())
    fg_smi = Chem.MolToSmiles(
        Chem.FragmentOnBonds(rdmol,xbs,addDummies=False)).split(".")
    fg_mol = [Chem.MolFromSmiles(x) for x in fg_smi]
    fg_rc  = [rdMolDescriptors.CalcNumRings(g) for g in fg_mol]
    res = sorted(zip(fg_mol, fg_rc), key=lambda x: x[1], reverse=True)
    molframe = res[0][0]
    
    return molframe


def get_attached_linkers(mol:Chem.Mol) -> Any:
    """Get linkers (connected non-ring atoms) between rings.

    Args:
        mol (Chem.Mol): input molecule.

    Returns:
        Any: linkers.
    """
    
    # convert a tuple of tuples to a list
    non_ring_atoms = [t[0] for t in mol.GetSubstructMatches(Chem.MolFromSmarts('[!R]'))]
    non_ring_atoms_attached = mol.GetSubstructMatches(Chem.MolFromSmarts('[!R][R]'))
    attached_linkers = []
    for (aj,ai),(ak,aii) in list(itertools.combinations(non_ring_atoms_attached,2)):
        try:
            jk = Chem.GetShortestPath(mol, aj, ak) #tuple
        except:
            continue
        # all atoms along the path should be non ring atoms
        if sum([1 for i in jk if i not in non_ring_atoms]) == 0:
            attached_linkers.append( (ai,) + jk + (aii,) )
    return attached_linkers


def breakup(parents:Any, maxChildren:Optional[int]=None, verbose:bool=False) -> List:
    """Breaks up parents recursively and return a list of scaffolds.
    
    Examples:
        >>> [(rdmol, 'O=C(CCCc1ccccc1)N1CCn2cnnc2C1', 3, ((6, 7, 8, 9, 10, 5), (12, 13, 14, 18, 19, 11), (15, 14, 18, 17, 16)), ()), ..]
    
    Args:
        parents (Any): Chem.Mol object at first but changes during recursive calls
        maxChildren (int, optional): max number of children
            maxChildren = None --> scaffold network methods
            maxChildren = 1    --> scaffold tree methods
        verbose: print out children info

    Returns:
        [(rdmol, smiles, nr, rings_indices, other_info), ... ]
    """

    if not isinstance(parents, list) : # at initial call
        if isinstance(parents, Chem.Mol):
            parent = Chem.Mol(parents)
        try:
            # remove exocyclic group(s)
            parent = MurckoScaffold.GetScaffoldForMol(parent)
            # isomericSmiles = False
            #   (1) enables robust canonicalization in RDKit
            #   (2) removes stereochemistry to make offsprings non-chiral
            #       because preserving correct stereochemistry during breaking up
            #       is difficult and appears to have no/little meaning
            smiles = Chem.MolToSmiles(parent, canonical=True, isomericSmiles=False)

            # parent molecule reflects the SMILES
            # all children will be affected by this
            parent = Chem.MolFromSmiles(smiles)

            rings = parent.GetRingInfo().AtomRings()
            nr = len(rings)
            priority = ()

            # return empty list if molecule has no ring
            if nr == 0:
                return []

            if verbose:
                print((nr,smiles,))

            parents = [(parent,smiles,nr,rings,priority)]

        except:
            return []

    children= []
    for parent,smiles,nr,rings,priority in parents:
        # terminate recursion if parents have only one ring or more than 10 rings
        if nr == 1 or nr > 10 :
            return parents
        # flatten atom index in all rings
        atomsInRings = [ai for ring in rings for ai in ring]
        # avoid removing atoms shared between two or more rings
        atomsShared = [ai for ai, count in collections.Counter(atomsInRings).items() if count > 1]
        fused_rings = sum([1 for ring in rings if len(set(ring).intersection(atomsShared)) > 0])
        # terminate if parents have only one big fused ring system such that
        # every ring has at least one shared atom
        remove_linker_enforced = False
        if nr > 5 :
            if nr == fused_rings: # all rings are fused
                return parents
            else:
                remove_linker_enforced = True
        # number of aromatic rings
        nar= sum([1 for ring in rings if parent.GetAtomWithIdx(ring[0]).GetIsAromatic()])
        # linkers that are attached to rings
        attached_linkers = get_attached_linkers(parent)

        for ring in rings:

            removed_ring_size = len(ring)
            if removed_ring_size == 3:
                removed_ring_3  = 1
            else:
                removed_ring_3  = 0
            if removed_ring_size in [3,5,6]:
                removed_ring_356 = 1
            else:
                removed_ring_356 = 0
            if removed_ring_size >= 12:
                removed_macrocycle = 1
            else:
                removed_macrocycle = 0

            atomsToRemain = [ai for ai in ring if ai in atomsShared ]
            atomsToRemove = [ai for ai in ring if ai not in atomsToRemain]

            # there is nothing to do when there is no atoms to remove
            # no child will be added to children
            # retain bridged rings, spiro rings, and nolinear ring fusion patterns
            if not atomsToRemove:
                continue

            # Rule 3 - choose the parent scaffold having the smallest number of acyclic linker bonds
            # if isolated ring is to be removed
            if len(atomsToRemove) == removed_ring_size:
                # linker has two ring atoms at both ends
                removed_linker_size_list = [
                    len(l)-2 for l in attached_linkers if l[0] in ring or l[-1] in ring
                    ]
                removed_linkers = len(removed_linker_size_list)
                if removed_linkers == 1:
                    removed_linker_size = removed_linker_size_list[0]
                elif removed_linkers > 1:
                    continue # it will break the molecule
                else :
                    removed_linker_size = 0
            else:
                removed_linker_size  = -1
                if remove_linker_enforced:
                    continue

            # heteroatom count
            removed_ring_hac = sum([1 for ai in ring if parent.GetAtomWithIdx(ai).GetSymbol() not in ["C","H"]])

            # get exocyclic double bonded atom index
            exo = []
            for ai in atomsToRemove:
                for b in parent.GetAtomWithIdx(ai).GetBonds():
                    if b.GetBondType() == Chem.BondType.DOUBLE:
                        # one of two indexes should be i (ring atom)
                        # and should be removed
                        # remove exocyclic double bonded atoms together
                        # unless these atoms belong to another ring
                        if ai == b.GetBeginAtomIdx():
                            if b.GetEndAtomIdx() not in atomsInRings:
                                exo += [ b.GetEndAtomIdx() ]
                        else:
                            if b.GetBeginAtomIdx() not in atomsInRings:
                                exo += [ b.GetBeginAtomIdx() ]
            # remove exocyclic double bonded atoms as well
            atomsToRemove += exo
            # make sure to remove an atom with bigger index number first
            # python sort function works as an in-place modifier
            # RDKit will renumber after every RemoveAtom() so
            # remove from highest to lowest atom index.
            atomsToRemove.sort(reverse=True)

            # use Chem.RWMol to preserve the original parent
            rwmol = Chem.RWMol(parent)

            explictHs = []
            for ai in atomsToRemain:
                for b in parent.GetAtomWithIdx(ai).GetBonds():
                    j,k = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
                    if j in atomsToRemove or k in atomsToRemove:
                        explictHs.append(rwmol.GetAtomWithIdx(ai))

            # Rule 1 - remove heterocycles of size 3 first
            # the fusion bond connecting the three-membered ring with other rings is
            # converted into a double bond
            # Rule 2 - do not remove rings with >= 12 atoms if there are still smaller rings to remove
            # Rule 6 - remove rings of sizes 3, 5, and 6 first
            # Rule 10 - smaller rings are removed first
            if removed_ring_size == 3 and len(atomsToRemove) == 1 and \
                parent.GetAtomWithIdx(atomsToRemove[0]).GetSymbol() in ["O","N"] :
                # fused three-membered ring, epoxides and aziridines
                # removing an atom changes atom indexes
                # so it should be done at the end
                rwmol.RemoveBond(atomsShared[0],atomsShared[1])
                rwmol.AddBond(atomsShared[0],atomsShared[1],order=Chem.BondType.DOUBLE)
                rwmol.RemoveAtom(atomsToRemove[0])
            else:
                for ai in atomsToRemove:
                    rwmol.RemoveAtom(ai)
                for a in explictHs:
                    a.SetNumExplicitHs(1)

            try:
                # get the modified molecule
                child = rwmol.GetMol()
                # ring removal should not break a molecule into pieces
                child_smiles = Chem.MolToSmiles(child, canonical=True, isomericSmiles=False)
                assert "." not in child_smiles
            except:
                continue

            try:
                Chem.SanitizeMol(child)
            except:
                continue

            try:
                # discard all the exocyclic groups of the child
                child = MurckoScaffold.GetScaffoldForMol(child)
                child_smiles = Chem.MolToSmiles(child, canonical=True, isomericSmiles=False)
                assert child_smiles
                # keep only non-redundant child
                assert sum([1 for c in children if c[1] == child_smiles]) == 0
            except:
                continue

            child_getRings = child.GetRingInfo()
            child_rings = child_getRings.AtomRings()
            child_nr = len(child_rings)
            child_atomsInRings = [ai for child_ring in child_rings for ai in child_ring]
            child_atomsShared = [ai for ai, count in collections.Counter(child_atomsInRings).items() if count > 1]
            child_fused_rings = sum([1 for child_ring in child_rings if len(set(child_ring).intersection(child_atomsShared)) > 0])

            #bridged compounds have two or more rings (a ring system) that
            # contains a bridge—a single atom or an unbranched chain of atoms
            #fused ring compounds have two rings linked by two adjacent atoms
            #spiro compounds have two rings linked by a single atom
            if nr == fused_rings and child_nr == child_fused_rings :
                # Rule 4 - retain bridged rings, spiro rings,
                #          and nonlinear ring fusion patterns with preference
                # Rule 5 - Bridged ring systems are retained with preference
                #          over spiro ring systems
                child_ring_bonds = child_getRings.BondRings()
                # flatten bond index in all rings
                child_bondsInRings = [bi for child_bonds in child_ring_bonds for bi in child_bonds]
                # bond shared between two or more rings
                # the more bridges or nonlinear ring fusions there are, the higher the nrrb
                # nrrb decreases if there are spiro connected ring systems
                child_bondsShared = [bi for bi, count in collections.Counter(child_bondsInRings).items() if count > 1]
                child_nrrb = len(child_bondsShared)
                child_delta = child_nrrb -(child_nr-1)
                child_delta_abs = abs(child_delta)
            else:
                child_delta = 0
                child_delta_abs = 0

            # Rule 7 - a fully aromatic ring system must not be dissected
            #           in a way that the resulting system is not aromatic any more
            # Rule 11 - for mixed aromatic/non-aromatic ring systems,
            #           retain non-aromatic rings with priority

            # number of aromatic rings
            child_nar= sum([1 for child_ring in child_rings if child.GetAtomWithIdx(child_ring[0]).GetIsAromatic()])

            if nr == nar:
                if child_nr == child_nar:
                    removed_aromaticity = 0
                else:
                    removed_aromaticity = 1
            else:
                removed_aromaticity = 0

            # Rule 12 - remove rings first where the linker is attached to
            #          a ring heteroatom at either end of the linker
            # Rule 8 - remove rings with the least number of heteroatoms first
            # Rule 9 - if the number of heteroatoms is equal,
            #          the priority of heteroatoms to retain is N > O > S
            try:
                child_ring_hetatom = max([ ord(child.GetAtomWithIdx(ai).GetSymbol())
                            for child_ring in child_rings for ai in child_ring
                                if child.GetAtomWithIdx(ai).GetSymbol() in ["N","O","S"]])
            except:
                child_ring_hetatom = ord("X")

            children.append((child,  #0
                             child_smiles, #1
                             child_nr,  #2
                             child_rings,  #3
                             ( #4
                                 removed_ring_3,  #rule 1
                                 -removed_macrocycle,  #rule 2
                                 removed_linker_size,  #rule 3
                                 child_delta_abs,  #rule 4
                                 child_delta,  #rule 5
                                 removed_ring_356,  #rule 6
                                 -removed_aromaticity,  #rule 7
                                 -removed_ring_hac,  #rule 8
                                 -child_ring_hetatom, #rule 9
                                 -child_nar, #rule 11
                                 child_smiles,  #rule 12 - tie breaker
                                 ),
                             ))
    if children:
        children = sorted(children, key=operator.itemgetter(4), reverse=True)
        if verbose:
            for d in children:
                print(d[2],d[1],d[-1])
            print("-"*40)
        # limit the number of children if needed
        # maxChildren = None --> scaffold network methods
        # maxChildren = 1    --> scaffold tree methods
        children = children[:maxChildren]
        # do this recursively until one ring remains
        return parents + breakup(children, maxChildren, verbose)
    else:
        # terminate when there is nothing to break up
        return parents
    

def scaffold_tree(rdmol:Chem.Mol) -> List[Chem.Mol]:
    """Returns scaffold tree.

    Args:
        rdmol (Chem.Mol): input molecule.

    Returns:
        List[Chem.Mol]: scaffold tree.
    """
    lmol = [rdmol]
    tree = breakup(rdmol, maxChildren=1)
    for (_rdmol, smiles, nr, ring_indices, other) in tree:
        lmol.append(_rdmol)
    return lmol


def scaffold_network(rdmol:Chem.Mol) -> List[Chem.Mol]:
    """Returns scaffold network.

    Args:
        rdmol (Chem.Mol): input molecule.

    Returns:
        List[Chem.Mol]: scaffold network.
    """
    lmol = [rdmol]
    network = breakup(rdmol, maxChildren=None)
    for (_rdmol, smiles, nr, ring_indices, other) in network:
        lmol.append(_rdmol)
    return lmol


def BRICS_fragmented(rdmol:Chem.Mol,
                     min_atoms:Optional[int]=None,
                     max_atoms:Optional[int]=None) -> List[Chem.Mol]:
    """Perform BRICKS decomposition and returns fragmented molecules.

    Args:
        rdmol (Chem.Mol): input molecule.
        min_atoms (Optional[int], optional): min number of atoms for a fragment. Defaults to None.
        max_atoms (Optional[int], optional): max number of atoms for a fragment. Defaults to None.

    Returns:
        List[Chem.Mol]: a list of fragmented molecules.
    """
    dummy = Chem.MolFromSmiles('*')
    hydro = Chem.MolFromSmiles('[H]')
    frag_smiles_set = BRICS.BRICSDecompose(Chem.Mol(rdmol))
    # ex. ['[14*]c1ccccn1', '[16*]c1cccc([16*])c1', '[3*]O[3*]', '[4*]CCC', '[4*]C[8*]']
    
    lfrag_rdmol = []
    for frag_smi in frag_smiles_set:
        (_, frag_rdmol) = desalt_smiles(frag_smi)
        # replace dummy atom(s) with [H]
        frag_rdmol_H= AllChem.ReplaceSubstructs(frag_rdmol, dummy, hydro, True)[0]
        frag_rdmol = Chem.RemoveHs(frag_rdmol_H)
        frag_smi = Chem.MolToSmiles(frag_rdmol)
        # filter out molecules which are too small or too big
        na = frag_rdmol.GetNumAtoms()
        if (min_atoms and na < min_atoms) or (max_atoms and na > max_atoms):
            continue
        lfrag_rdmol.append(frag_rdmol)
    return lfrag_rdmol


def depth_first_search(rdatom:Chem.Atom, origin_atom:Chem.Atom, 
                       end_idx:int, group:List[int], BRICS_bonds:List[Tuple[int,int]]) -> List[List[int]]:
    """Does recursive depth-first search.

    Args:
        rdatom (Chem.Atom): input atom.
        origin_atom (Chem.Atom): origin atom.
        end_idx (int): end index.
        group (List[int]): group to be appended by the function.
        BRICS_bonds (List[Tuple[int,int]]): list of bonds(tuple of two indexes)

    Returns:
        List[List[int]]: search output.
    """
    bonded_atoms = rdatom.GetNeighbors()
    if (len(bonded_atoms) == 1) and (bonded_atoms[0] == origin_atom):
        return
    for atom in bonded_atoms:
        idx = atom.GetIdx()
        if (idx == end_idx) or (idx in group) or (sorted([rdatom.GetIdx(), idx]) in BRICS_bonds):
            continue
        group.append(idx)
        depth_first_search(atom, rdatom, end_idx, group, BRICS_bonds)


def BRICS_fragment_indices(rdmol:Chem.Mol) -> List[List[int]]:
    """Returns BRICS fragment/scaffold atom indices.

    Args:
        rdmol (Chem.Mol): input molecule.

    Returns:
        List[List[int]]: fragment/scaffold atom indices.
    """
    BRICS_bonds = [sorted(x[0]) for x in list(BRICS.FindBRICSBonds(rdmol))]
    if BRICS_bonds:
        indices = []
        for bond in BRICS_bonds:
            for (start_idx, end_idx) in [(bond[0], bond[1]), (bond[1], bond[0])]:
                group = []
                origin_atom = rdmol.GetAtomWithIdx(start_idx)
                for atom in origin_atom.GetNeighbors():
                    idx = atom.GetIdx()
                    if (idx == end_idx):
                        continue
                    depth_first_search(atom, origin_atom, end_idx, group, BRICS_bonds)
                if sorted(group) not in indices:
                    indices.append(sorted(group))
    else: # all indices
        indices = [ [a.GetIdx() for a in rdmol.GetAtoms()] ]
    return sorted(indices, key=lambda x: len(x), reverse=True)


def rigid_fragment_indices(rdmol:Chem.Mol) -> List[List[int]]:
    """Breaks a molecule at each rotatable bond and returns atom indices of fragments.
    Args:
        rdmol (Chem.Mol) : input molecule
    
    Returns:
        list of list (atom indices)
    """
    rotatable_bond_pattern = Chem.MolFromSmarts('[!$(*#*)&!D1]-&!@[!$(*#*)&!D1]')
    rotatable_bonds = [sorted(x) for x in list(rdmol.GetSubstructMatches(rotatable_bond_pattern))]
    if rotatable_bonds:
        indices = []
        for bond in rotatable_bonds:
            for (start_idx, end_idx) in [(bond[0], bond[1]), (bond[1], bond[0])]:
                group = []
                origin_atom = rdmol.GetAtomWithIdx(start_idx)
                for atom in origin_atom.GetNeighbors():
                    idx = atom.GetIdx()
                    if (idx == end_idx):
                        continue
                    depth_first_search(atom, origin_atom, end_idx, group, rotatable_bonds)
                if sorted(group) not in indices:
                    indices.append(sorted(group))
    else: # all indices
        indices = [ [a.GetIdx() for a in rdmol.GetAtoms()] ]
    # ignore H
    indices_noH = []
    for ii in indices:
        indices_noH.append([i for i in ii if rdmol.GetAtomWithIdx(i).GetAtomicNum() != 1 ])
    
    return sorted(indices_noH, key=lambda x: len(x), reverse=True)


