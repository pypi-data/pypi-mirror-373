from molecule_benchmarks.dataset import SmilesDataset


def test_guacamol():
    # Test loading the Guacamole  dataset
    dataset = SmilesDataset.load_guacamol_dataset(max_train_samples=100, cache_dir="data")
    assert len(dataset.train_smiles) > 10, "Guacamole dataset has no training SMILES"
    assert len(dataset.validation_smiles) > 5, (
        "Guacamole dataset has no validation SMILES"
    )


def test_moses():
    # Test loading the Moses dataset
    dataset = SmilesDataset.load_moses_dataset(max_train_samples=100, cache_dir="data")
    assert len(dataset.train_smiles) > 10, "Moses dataset has no training SMILES"
    assert len(dataset.validation_smiles) > 5, "Moses dataset has no validation SMILES"


def test_dummy():
    # Test loading the dummy dataset
    dataset = SmilesDataset.load_dummy_dataset()
    assert len(dataset.train_smiles) > 0, "Dummy dataset has no training SMILES"
    assert len(dataset.validation_smiles) > 0, "Dummy dataset has no validation SMILES"


def test_qm9():
    # Test loading the QM9 dataset
    dataset = SmilesDataset.load_qm9_dataset(max_train_samples=100, cache_dir="data")
    assert len(dataset.train_smiles) > 10, "QM9 dataset has no training SMILES"
    assert len(dataset.validation_smiles) > 10, "QM9 dataset has no validation SMILES"
