from rdworks import Mol
from rdworks.conf import prep_confs_batches
from rdkit import Chem


class Dummy_BatchSingplePoint():
    def __init__(self, rdmols, **kwargs):
        self.rdmols = rdmols

    def __str__(self):
        return "Dummy_BatchSinglePoint"

    def run(self):
        from collections import namedtuple
        Calculated = namedtuple('Calculated', ['mols',])
        for rdmol in self.rdmols:
            rdmol.SetProp('E_tot(kcal/mol)', '1.0')
        return Calculated(mols=self.rdmols)


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


def test_prep_confs_batches():
    mol = Mol("N=C1O[C@@H](CN1)CN2C[C@H](O[C@H](C2)C)C", "stereoisomer")
    mol = mol.make_confs(n=50, method='ETKDG')
    batches = prep_confs_batches(mol.confs)
    assert isinstance(batches, list)
    assert len(batches) > 0
    assert isinstance(batches[0].rdmols, list)
    assert isinstance(batches[0].rdmols[0], Chem.Mol)
    assert isinstance(batches[0].size, int)
    assert batches[0].size > 0
    assert isinstance(batches[0].num_atoms, int)
    assert batches[0].num_atoms > 0


def test_singlepoint_batch():
    mol = Mol("N=C1O[C@@H](CN1)CN2C[C@H](O[C@H](C2)C)C", "stereoisomer")
    mol = mol.make_confs(n=10, method='ETKDG')
    mol = mol.singlepoint(calculator=Dummy_BatchSingplePoint, batchsize_atoms=16384)
    assert all([_.props.get('E_tot(kcal/mol)') is not None for _ in mol.confs])


def test_optimize_confs_batch():
    mol = Mol("N=C1O[C@@H](CN1)CN2C[C@H](O[C@H](C2)C)C", "stereoisomer")
    mol = mol.make_confs(n=50, method='ETKDG')
    mol = mol.optimize_confs(calculator=Dummy_BatchOptimizer, batchsize_atoms=16384)
    assert all([_.props.get('E_tot_init(kcal/mol)') is not None for _ in mol.confs])
    assert all([_.props.get('E_tot(kcal/mol)') is not None for _ in mol.confs])
    assert all([_.props.get('Converged') is not None for _ in mol.confs])
