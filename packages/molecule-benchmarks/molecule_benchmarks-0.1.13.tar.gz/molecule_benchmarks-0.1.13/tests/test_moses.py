from molecule_benchmarks import moses_metrics as mm


def test_moses():
    # print(mm.fingerprint("CCO"))
    fps1 = mm.fingerprints(["CCO", "CCN"])
    fps2 = mm.fingerprints(["CCO", "CO"])
    # print(fps1)
    # print(fps2)
    print(mm.average_agg_tanimoto(fps1, fps2))
    print(mm.average_agg_tanimoto(fps1, fps1))


def test_filters():
    filters = mm.get_filters()
    assert len(filters) > 0, "No filters loaded"
    mol = mm.get_mol("CCO")
    print("mol passes filters?", mm.mol_passes_filters(mol, filters))
    # mol = mm.get_mol("C1=CC=CC=C1")
    # assert not mm.mol_passes_filters(mol, filters), "Benzene should not pass filters"
    # print("All tests passed for filters")
