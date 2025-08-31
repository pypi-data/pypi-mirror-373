from rdworks import Mol, MolLibr
from rdworks.stereoisomers import enumerate_stereoisomers, enumerate_ring_bond_stereoisomers
from rdkit import Chem
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers, StereoEnumerationOptions


def complete_stereoisomers(molecular_input: str | Chem.Mol | Mol, 
                           name: str | None = None, 
                           std: bool = False, 
                           override: bool = False, 
                           **kwargs) -> MolLibr:
    """Completes stereoisomers and returns a rdworks.MolLibr.

    Args:
        molecular_input (Union[Mol, str, Chem.Mol]): input molecule.
        name (Optional[str], optional): name of the molecule. Defaults to None.
        std (bool, optional): whether to standardize the input. Defaults to False.
        override (bool, optional): whether to override input stereoisomers. Defaults to False.

    Raises:
        TypeError: if `molecular_input` is not rdworks.Mol, SMILES, or rdkit.Chem.Mol object.

    Returns:
        MolLibr: a library of complete stereoisomers.
    """
    from rdworks import Mol, MolLibr
    
    if isinstance(molecular_input, Mol):
        if name:
            mol = molecular_input.rename(name)
        else:
            mol = molecular_input
    elif isinstance(molecular_input, str) or isinstance(molecular_input, Chem.Mol):
        mol = Mol(molecular_input, name, std)
    else:
        raise TypeError('complete_stereoisomers() expects rdworks.Mol, SMILES or rdkit.Chem.Mol object')
    
    ring_bond_stereo_info = mol.get_ring_bond_stereo()
    
    if override:
        mol = mol.remove_stereo()
    
    rdmols = enumerate_stereoisomers(mol.rdmol)
    # ring bond stereo is not properly enumerated
    # cis/trans information is lost if stereochemistry is removed,
    # which cannot be enumerated by EnumerateStereoisomers() function
    # so enumerate_ring_bond_stereoisomers() is introduced
    if len(ring_bond_stereo_info) > 0:
        ring_cis_trans = []
        for rdmol in rdmols:
            ring_cis_trans += enumerate_ring_bond_stereoisomers(rdmol,
                                                     ring_bond_stereo_info,
                                                     override=override)
        if len(ring_cis_trans) > 0:
            rdmols = ring_cis_trans
    
    if len(rdmols) > 1:
        libr = MolLibr(rdmols).unique().rename(mol.name, sep='.').compute(**kwargs)
    else:
        libr = MolLibr(rdmols).rename(mol.name).compute(**kwargs)
    
    for _ in libr:
        _.props.update(mol.props)
    
    return libr


def can_have_stereo(bond):
    """Check if a double bond can have E/Z stereochemistry"""
    atom1, atom2 = bond.GetBeginAtom(), bond.GetEndAtom()
    
    # Check if both atoms have at least 2 non-hydrogen neighbors
    for atom in [atom1, atom2]:
        non_h_neighbors = [n for n in atom.GetNeighbors() if n.GetAtomicNum() != 1]
        if len(non_h_neighbors) < 2:
            return False
    
    return True


def complete_tautomers(mol: Mol, **kwargs) -> MolLibr:
    """Returns a library of enumerated tautomers.

    Args:
        mol (Mol): input molecule.

    Returns:
        MolLibr: a library of enumerated tautomers.
    """
    enumerator = rdMolStandardize.TautomerEnumerator()
    enumerator.SetRemoveSp3Stereo(False)
    enumerator.SetRemoveBondStereo(False)  # Don't remove existing stereo
    tautomers = list(enumerator.Enumerate(mol.rdmol))
    
    all_stereoisomers = []
    
    for tautomer in tautomers:
        # Find unspecified double bonds that could have E/Z stereo
        unspecified_bonds = []
        for bond in tautomer.GetBonds():
            if (bond.GetBondType() == Chem.BondType.DOUBLE and 
                bond.GetStereo() == Chem.BondStereo.STEREONONE and
                can_have_stereo(bond)):
                unspecified_bonds.append(bond.GetIdx())
        
        if unspecified_bonds:
            # Enumerate all possible stereoisomers
            opts = StereoEnumerationOptions(onlyUnassigned=True, maxIsomers=50)
            stereoisomers = list(EnumerateStereoisomers(tautomer, options=opts))
            all_stereoisomers.extend(stereoisomers)
        else:
            all_stereoisomers.append(tautomer)
    
    if len(all_stereoisomers) > 1: 
        return MolLibr(all_stereoisomers).unique().rename(mol.name, sep='.').compute(**kwargs)
    
    return MolLibr(all_stereoisomers).compute(**kwargs)