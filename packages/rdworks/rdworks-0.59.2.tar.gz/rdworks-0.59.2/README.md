# Rdworks - routine tasks made easy

Rdworks is designed to perform routine cheminformatics tasks easily. It is built on RDKit and other tools. 

## Install

```sh
$ pip install rdworks
```

## Getting started

```py
from rdworks import Mol

version = rdworks.__version__

mol = Mol('CC(=O)Nc1ccc(O)cc1', 'acetaminophen')

mol = mol.make_confs(n=5)
mol.to_sdf('acetaminophen.sdf')

torsion_dict = mol.torsion_atoms() 
# torsion_dict = {0: (5,4,3,1)}

mol = mol.torsion_energies(calculator='MMFF94', simplify=True)

mol.plot_torsion_energies(0, figsize=(6,4))

mol.to_png(300, 300, atom_index=True, highlight_atoms=torsion_dict.get(0))

serialized = mol.serialize(compress=True)
mol2 = Mol().deserialize(serialized, compress=True)

mol3 = mol.copy()
```
