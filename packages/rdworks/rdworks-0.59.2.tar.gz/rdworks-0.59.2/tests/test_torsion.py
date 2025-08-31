from rdworks.torsion import create_torsion_fragment
from rdworks import Mol, MolLibr
from pathlib import Path


datadir = Path(__file__).parent.resolve() / "data"
workdir = Path(__file__).parent.resolve() / "outfiles"

workdir.mkdir(exist_ok=True)


# Lahey, S.-L. J., Thien Phuc, T. N. & Rowley, C. N. 
# Benchmarking Force Field and the ANI Neural Network Potentials for the 
# Torsional Potential Energy Surface of Biaryl Drug Fragments. 
# J. Chem. Inf. Model. 60, 6258–6268 (2020)

torsion_dataset_smiles = [
    "C1(C2=CC=CN2)=CC=CC=C1",
    "C1(C2=NC=CN2)=CC=CC=C1",
    "C1(N2C=CC=C2)=NC=CC=N1",
    "C1(C2=NC=NC=N2)=CC=CC=C1",
    "C1(N2C=CC=C2)=CC=CC=C1",
    "O=C(N1)C=CC=C1C2=COC=C2",
    "C1(C2=NC=CC=N2)=NC=CC=N1",
    "O=C(N1)C=CC=C1C2=NC=CN2",
    ]

torsion_dataset_names=["07", "09","20", "39", "10", "23", "12", "29"]


def test_torsion_fragment():
    
    mol = Mol(molecule="CC(C)C1=C(C(=C(N1CC[C@H](C[C@H](CC(=O)O)O)O)C2=CC=C(C=C2)F)C3=CC=CC=C3)C(=O)NC4=CC=CC=C4",
              name="atorvastatin").make_confs(n=1)
    ta = mol.torsion_atoms()
    assert len(ta) == 12
    # {0: (0, 1, 3, 7),  1: (3, 4, 32, 33),  2: (4, 5, 26, 27),  3: (7, 6, 19, 20),
    # 4: (3, 7, 8, 9),  5: (7, 8, 9, 10),   6: (8, 9, 10, 18),   7: (18, 10, 11, 12),
    # 8: (10, 11, 12, 17),  9: (17, 12, 13, 14),   10: (12, 13, 14, 15),   11: (36, 35, 34, 32)}
    (frag, frag_ijkl, frag_created, wbo_filtered) = create_torsion_fragment(mol.confs[0].rdmol, ta[6])
    assert frag_ijkl == (5, 6, 7, 12)
    assert frag_created == True
    assert wbo_filtered == True

    mol2 = Mol(molecule='CC(=O)Nc1ccc(O)cc1', name='acetaminophen.3').make_confs(n=1)
    ta2 = mol2.torsion_atoms()
    # {0: (5, 4, 3, 1)}
    assert len(ta2) == 1

    (frag, frag_ijkl, frag_created, wbo_filtered) = create_torsion_fragment(mol2.confs[0].rdmol, ta2[0])
    # expects no fragmentation
    assert frag == mol2.confs[0].rdmol
    assert frag_ijkl == ta2[0]
    assert frag_created == False
    assert wbo_filtered == False


def test_torsion_fragment_from_conf():
    mol = Mol(molecule="CC(C)C1=C(C(=C(N1CC[C@H](C[C@H](CC(=O)O)O)O)C2=CC=C(C=C2)F)C3=CC=CC=C3)C(=O)NC4=CC=CC=C4",
              name="atorvastatin").make_confs(n=1)
    ref_conf = mol.confs[0]
    ta = ref_conf.torsion_atoms()
    assert len(ta) == 12
    # {0: (0, 1, 3, 7),  1: (3, 4, 32, 33),  2: (4, 5, 26, 27),  3: (7, 6, 19, 20),
    # 4: (3, 7, 8, 9),  5: (7, 8, 9, 10),   6: (8, 9, 10, 18),   7: (18, 10, 11, 12),
    # 8: (10, 11, 12, 17),  9: (17, 12, 13, 14),   10: (12, 13, 14, 15),   11: (36, 35, 34, 32)}
    frag, frag_ijkl, frag_created, wbo_filtered = create_torsion_fragment(ref_conf.rdmol, ta[6])
    assert frag_ijkl == (5, 6, 7, 12)
    assert frag_created == True
    assert wbo_filtered == True

    ref_conf = ref_conf.torsion_energies(calculator='MMFF94', torsion_key=6, interval=15)

    mol2 = Mol(molecule='CC(=O)Nc1ccc(O)cc1', name='acetaminophen.3').make_confs(n=1)
    ref_conf2 = mol2.confs[0]
    ta2 = ref_conf2.torsion_atoms()
    # {0: (5, 4, 3, 1)}
    assert len(ta2) == 1
    frag, frag_ijkl, frag_created, wbo_filtered = create_torsion_fragment(ref_conf2.rdmol, ta2[0])
    # expects no fragmentation
    assert frag == ref_conf2.rdmol
    assert frag_ijkl == ta2[0]
    assert frag_created == False
    assert wbo_filtered == False

    ref_conf2 = ref_conf2.torsion_energies(calculator='MMFF94', interval=15)
    ref_conf3 = ref_conf2.torsion_energies_one(calculator='MMFF94', indices=frag_ijkl)


def test_torsion_energies():
    libr = MolLibr(torsion_dataset_smiles, torsion_dataset_names)
    with open(workdir / 'test_torsion_energies.html', 'w', encoding='utf-8') as f:
        for mol in libr[:1]:
            mol = mol.make_confs().drop_confs(similar=True, similar_rmsd=0.3).sort_confs().rename()
            mol = mol.optimize_confs(calculator='MMFF94').torsion_energies(calculator='MMFF94', 
                                                                           interval=15)
            f.write(mol.to_html())
            print(mol.dumps('torsion', decimals=2))


def test_torsion_energies_batch():
    class Dummy_BatchOptimizer():
        def __init__(self, rdmols, **kwargs):
            self.rdmols = rdmols

        def __str__(self):
            return "Dummy_BatchOptimizer"

        def run(self):
            from collections import namedtuple
            Optimized = namedtuple('Optimized', ['mols',])
            for rdmol in self.rdmols:
                rdmol.SetProp('E_tot_init(kcal/mol)', '10.0')
                rdmol.SetProp('E_tot(kcal/mol)', '1.0')
                rdmol.SetProp('Converged', 'True')
            return Optimized(mols=self.rdmols)
    
    libr = MolLibr(torsion_dataset_smiles, torsion_dataset_names)
    with open(workdir / 'test_torsion_energies_batch.html', 'w', encoding='utf-8') as f:
        for mol in libr[:1]:
            mol = mol.make_confs().drop_confs(similar=True, similar_rmsd=0.3).sort_confs().rename()
            mol = mol.optimize_confs(calculator='MMFF94')
            mol = mol.torsion_energies(Dummy_BatchOptimizer, interval=15, batchsize_atoms=16384)
            f.write(mol.to_html())
            print(mol.dumps('torsion', decimals=2))
