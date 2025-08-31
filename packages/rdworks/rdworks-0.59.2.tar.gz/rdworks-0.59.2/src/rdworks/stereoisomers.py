from rdkit import Chem
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers, StereoEnumerationOptions


def enumerate_stereoisomers(rdmol: Chem.Mol) -> list[Chem.Mol]:
    """Returns enumerated stereoisomers.

    Args:
        rdmol (Chem.Mol): input molecule.

    Returns:
        List[Chem.Mol]: a list of enumerated stereoisomers.
    """
    return list(EnumerateStereoisomers(
        rdmol, 
        options=StereoEnumerationOptions(
            tryEmbedding=False,
            onlyUnassigned=True,
            maxIsomers=1024,
            rand=None,
            unique=True,
            onlyStereoGroups=False,
            )))


def enumerate_ring_bond_stereoisomers(rdmol: Chem.Mol, 
                                      ring_bond_stereo_info: list[tuple],
                                      override: bool = False) -> list[Chem.Mol]:
    """Enumerates unspecified double bond stereochemistry (cis/trans).

    <pre>
    a1        a4  a1
      \      /      \
       a2=a3         a2=a3 
                          \
                          a4
    </pre>

    Args:
        rdmol (Chem.Mol): input molecule.
        ring_bond_stereo_info (List[Tuple]): 
            ring_bond_stereo_info will be set when .remove_stereo() is called.
            bond_stereo_info = [(bond_idx, bond_stereo_descriptor), ..] where
            bond_stereo_descriptor is `Chem.StereoDescriptor.Bond_Cis` or
            `Chem.StereoDescriptor.Bond_Trans`, or `Chem.StereoDescriptor.NoValue`.
        override (bool, optional): _description_. Defaults to False.

    Returns:
        List[Chem.Mol]: list of enumerated stereoisomers.
    """
    isomers = []
    for bond_idx, bond_stereo_desc in ring_bond_stereo_info:
        if (bond_stereo_desc == Chem.StereoDescriptor.NoValue) or override:
            bond = rdmol.GetBondWithIdx(bond_idx)
            (a2,a3) = (bond.GetBeginAtom(), bond.GetEndAtom())
            a2_idx = a2.GetIdx()
            a3_idx = a3.GetIdx()
            a1_idx = sorted([(a.GetIdx(), a.GetAtomicNum()) for a in a2.GetNeighbors() if a.GetIdx() != a3_idx], key=lambda x: x[1], reverse=True)[0][0]
            a4_idx = sorted([(a.GetIdx(), a.GetAtomicNum()) for a in a3.GetNeighbors() if a.GetIdx() != a2_idx], key=lambda x: x[1], reverse=True)[0][0]
            bond.SetStereoAtoms(a1_idx, a4_idx) # need to set reference atoms
            # cis
            bond.SetStereo(Chem.BondStereo.STEREOCIS)
            isomers.append(Chem.Mol(rdmol))
            # trans
            bond.SetStereo(Chem.BondStereo.STEREOTRANS)
            isomers.append(Chem.Mol(rdmol))
    return isomers