from rdworks import IonizedStates


def test_ionizedstate():    
    smiles = 'O=C(NCCCC)[C@H](CCC1)N1[C@@H](CC)C2=NN=C(CC3=CC=C(C)C=C3)O2'
    x = IonizedStates(smiles)

    assert x.count() == 7
    
    d = x.get_sites()
    print('sites:')
    for k, v in d.items():
        print(k, v)
    print()

    p = x.get_pairs()
    print('pairs:')
    for k in p:
        print(k)
    print()

    indices = d['CCCCNC(=O)[C@@H]1CCCN1[C@@H](CC)c1nnc(Cc2ccc(C)cc2)o1'][0]
    
    assert (11, 'B') in indices
    assert (16, 'B') in indices
    assert (17, 'B') in indices

    expected = ['CCCCNC(=O)[C@@H]1CCCN1[C@@H](CC)c1nnc(Cc2ccc(C)cc2)o1', 
                'CCCCNC(=O)[C@@H]1CCCN1[C@@H](CC)c1[nH+]nc(Cc2ccc(C)cc2)o1', 
                'CCCCNC(=O)[C@@H]1CCC[NH+]1[C@@H](CC)c1nnc(Cc2ccc(C)cc2)o1', 
                'CCCCNC(=O)[C@@H]1CCCN1[C@@H](CC)c1n[nH+]c(Cc2ccc(C)cc2)o1', 
                'CCCCNC(=O)[C@@H]1CCC[NH+]1[C@@H](CC)c1[nH+]nc(Cc2ccc(C)cc2)o1', 
                'CCCCNC(=O)[C@@H]1CCCN1[C@@H](CC)c1[nH+][nH+]c(Cc2ccc(C)cc2)o1', 
                'CCCCNC(=O)[C@@H]1CCC[NH+]1[C@@H](CC)c1n[nH+]c(Cc2ccc(C)cc2)o1']
    results = x.get_smiles()
    assert set(expected).intersection(set(results)) == set(expected)


# def test_gypsum_dl():
#     import gypsum_dl
#     smiles = 'O=C(NCCCC)[C@H](CCC1)N1[C@@H](CC)C2=NN=C(CC3=CC=C(C)C=C3)O2'
#     state_smiles = list(
#         gypsum_dl.GypsumDL(smiles,
#             min_ph=6.4,
#             max_ph=8.4,
#             pka_precision=1.0,
#             thoroughness=3,
#             max_variants_per_compound=5,
#             second_embed=False,
#             skip_optimize_geometry=False,
#             skip_alternate_ring_conformations=False,
#             skip_adding_hydrogen=False,
#             skip_making_tautomers=False,
#             skip_enumerate_chiral_mol=False,
#             skip_enumerate_double_bonds=False,
#             let_tautomers_change_chirality=False,
#             use_durrant_lab_filters=True,
#             job_manager='serial',
#             num_processors=1,
#             ))
#     for smi in state_smiles:
#         print(smi)
    
if __name__ == '__main__':
    test_ionizedstate()
    # test_gypsum_dl()