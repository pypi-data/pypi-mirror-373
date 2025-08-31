from rdkit.Chem import Descriptors, rdMolDescriptors, QED

rd_descriptor = {
    'QED'         : "Quantitative estimate of drug-likeness.",
    'MolWt'       : 'Molecular weight',
    'LogP'        : 'Predicted octanol/water partition coefficient',
    'TPSA'        : 'Topological polar surface area',
    'HBD'         : 'Number of hydrogen bonding donors',
    'HBA'         : 'Number of hydrogen bonding acceptors',
    'RotBonds'    : 'Number of rotatable bonds',
    'RingCount'   : 'Number of rings',
    'FCsp3'       : 'Fraction of SP3 carbons',
    'HAC'         : 'Number of heavy atoms',
    'Hetero'      : 'Number of hetero atoms (not H or C) [B,N,O,P,S,F,Cl,Br,I]',
    'LipinskiHBA' : 'Number of hydrogen bonding acceptors according to the Lipinski definition',
    'LipinskiHBD' : 'Number of hydrogen bonding donors according to the Lipinski definition',
}

rd_descriptor_f = {
    "QED"           : QED.qed,
    "MolWt"         : Descriptors.MolWt,
    "HAC"           : Descriptors.HeavyAtomCount,
    "LogP"          : Descriptors.MolLogP,                      # == Crippen.MolLogP
    "TPSA"          : Descriptors.TPSA,                         # == MolSurf.TPSA
    "HBA"           : rdMolDescriptors.CalcNumHBA,              # == Descriptors.NumHAcceptors
    "HBD"           : rdMolDescriptors.CalcNumHBD,              # == Descriptors.NumHDonors
    "RotBonds"      : rdMolDescriptors.CalcNumRotatableBonds,   # == Descriptors.NumRotatableBonds
    "RingCount"     : rdMolDescriptors.CalcNumRings,            # == Descriptors.RingCount
    "FCsp3"         : rdMolDescriptors.CalcFractionCSP3,        # == Descriptors.FractionCSP3
    "Hetero"        : rdMolDescriptors.CalcNumHeteroatoms,      # not (H or C) [B,N,O,P,S,F,Cl,Br,I]
    "LipinskiHBA"   : rdMolDescriptors.CalcNumLipinskiHBA,
    "LipinskiHBD"   : rdMolDescriptors.CalcNumLipinskiHBD,
    # "StereoCenters"     : rdMolDescriptors.CalcNumAtomStereoCenters,
    # props_dict[k] = rd_descriptor_f[k](self.rdmol)
    # ValueError: numStereoCenters called without stereo being assigned
}