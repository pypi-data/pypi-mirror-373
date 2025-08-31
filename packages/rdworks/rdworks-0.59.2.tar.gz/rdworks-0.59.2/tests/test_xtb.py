from rdworks import Mol
from rdworks.xtb.wrapper import GFN2xTB
from rdworks.testdata import drugs

from pathlib import Path

import tempfile

# In ASE, the default energy unit is eV (electron volt).
# It will be converted to kcal/mol
# CODATA 2018 energy conversion factor
hartree2ev = 27.211386245988
hartree2kcalpermol = 627.50947337481
ev2kcalpermol = 23.060547830619026


datadir = Path(__file__).parent.resolve() / "data"
workdir = Path(__file__).parent.resolve() / "outfiles"

workdir.mkdir(exist_ok=True)

name = 'Atorvastatin'
testmol = Mol(drugs[name], name).make_confs(n=50).optimize_confs()
testmol = testmol.drop_confs(similar=True, verbose=True).sort_confs()


def test_xtb_wrapper():
    assert GFN2xTB.is_xtb_ready() == True
    assert GFN2xTB.is_cpx_ready() == True
    assert GFN2xTB.is_cpcmx_ready() == True
    assert GFN2xTB.is_ready() == True
    assert GFN2xTB.version() is not None


def test_singlepoint():        
    mol = testmol.copy()

    print("number of conformers=", mol.count())
    print("number of atoms=", mol.confs[0].natoms)

    gfn2xtb = GFN2xTB(mol.confs[0].rdmol)

    print("GFN2xTB.singlepoint()")
    outdict = gfn2xtb.singlepoint()
    print(outdict)
    print()

    print("GFN2xTB.singlepoint(water='gbsa')")
    outdict = gfn2xtb.singlepoint(water='gbsa')
    print(outdict)
    print()

    print("GFN2xTB.singlepoint(water='alpb')")
    outdict = gfn2xtb.singlepoint(water='alpb')
    print(outdict)
    print()

    print("GFN2xTB.singlepoint(water='cpcmx')")
    outdict = gfn2xtb.singlepoint(water='cpcmx')
    print(outdict)
    print()


def test_optimize():
    mol = testmol.copy()
    print("number of conformers=", mol.count())
    print("GFN2xTB.optimize()")
    outdict = GFN2xTB(mol.confs[0].rdmol).optimize(verbose=True)
    print(outdict)
    print()


if __name__ == '__main__':
    test_xtb_wrapper()
    # test_singlepoint()
    # test_optimize()
