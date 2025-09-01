import torch

from molecule_benchmarks import Benchmarker
from molecule_benchmarks.dataset import SmilesDataset
from molecule_benchmarks.model import DummyMoleculeGenerationModel
from molecule_benchmarks.utils import download_with_cache

device = "cpu"
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"


def test_benchmarker():
    # Create a Benchmarker instance with some test SMILES
    ds = SmilesDataset.load_qm9_dataset(max_train_samples=10000)
    benchmarker = Benchmarker(ds, num_samples_to_generate=10000)
    # Test the benchmarker can handle only invalid SMILES
    benchmarker.benchmark(["C-H-C"] * 5000 + [None] * 5000)  # 10000 invalid SMILES

    model = DummyMoleculeGenerationModel(ds.train_smiles[:5000])

    # Test the validity score computation
    scores = benchmarker.benchmark_model(model)
    print(scores)
    validity_scores = scores["validity"]
    assert validity_scores["valid_fraction"] >= 0.99, (
        f"Expected valid fraction of almost 100% but got {validity_scores['valid_fraction']}"
    )
    assert validity_scores["valid_and_unique_fraction"] <= 5000 / 10000, (
        f"Got {validity_scores['valid_and_unique_fraction']}"
    )
    assert 0.49 <= validity_scores["unique_fraction"] <= 0.5, (
        f"Expected 5000/10000, but got {validity_scores['unique_fraction']}"
    )
    assert scores["kl_score"] > 0.95, (
        f"Expected KL score to be high, got {scores['kl_score']}"
    )
    assert scores["fcd"]["fcd"] < 0.3, (
        f"Expected FCD score to be low, got {scores['fcd']['fcd']}"
    )


def _test_moses_benchmarks_match(model_name: str, run: int, benchmarker: Benchmarker):
    """Test that Moses benchmarks match the values computed by the original implementation."""

    print(f"Testing Moses benchmarks for model {model_name} run {run}...")

    metrics_url = f"https://media.githubusercontent.com/media/molecularsets/moses/refs/heads/master/data/samples/{model_name}/metrics_{model_name}_{run}.csv"
    samples_url = f"https://media.githubusercontent.com/media/molecularsets/moses/refs/heads/master/data/samples/{model_name}/{model_name}_{run}.csv"

    metrics_content = download_with_cache(metrics_url, cache_dir="data")
    metrics = metrics_content.splitlines()
    metrics = metrics[1:]  # Skip header
    metrics_dict: dict[str, float] = {}
    for line in metrics:
        key, value = line.split(",")
        metrics_dict[key] = float(value)
    print(metrics_dict)  # Print metrics for debugging

    samples_content = download_with_cache(samples_url, cache_dir="data")
    samples = samples_content.splitlines()
    samples = samples[1:]  # Skip header
    print(samples[:5])  # Print first 5 samples for debugging
    print("Number of samples:", len(samples))

    scores = benchmarker.benchmark(samples)
    print(scores)  # Print scores for debugging
    all_scores_matched = True

    def compare_scores(
        name: str, precomputed: float, actual: float, tolerance: float = 0.01
    ):
        distance = abs(precomputed - actual)
        print(
            f"Comparing {name}: precomputed={precomputed:<.4f}, actual={actual:<.4f}, distance={distance:<.4f}"
        )
        if distance > tolerance:
            print(
                f"Score mismatch for {name}: precomputed={precomputed}, actual={actual}"
            )
            nonlocal all_scores_matched
            all_scores_matched = False

    compare_scores(
        "Novel fraction",
        metrics_dict["Novelty"],
        scores["validity"]["valid_and_unique_and_novel_fraction_of_valid_and_uniques"],
        tolerance=0.015,
    )
    compare_scores(
        "Fragment similarity",
        metrics_dict["Frag/Test"],
        scores["moses"]["fragment_similarity"],
    )
    compare_scores(
        "Scaffold similarity",
        metrics_dict["Scaf/Test"],
        scores["moses"]["scaffolds_similarity"],
    )
    compare_scores("SNN score", metrics_dict["SNN/Test"], scores["moses"]["snn_score"])
    compare_scores("IntDiv", metrics_dict["IntDiv"], scores["moses"]["IntDiv"])
    compare_scores("IntDiv2", metrics_dict["IntDiv2"], scores["moses"]["IntDiv2"])
    compare_scores(
        "Fraction passing Moses filters",
        metrics_dict["Filters"],
        scores["moses"]["fraction_passing_moses_filters"],
    )
    print("All scores matched:", all_scores_matched)
    assert all_scores_matched, "Some scores did not match the precomputed values."


def test_moses_benchmarks():
    """Test that Moses benchmarks match the values computed by the original implementation."""
    ds = SmilesDataset.load_moses_dataset()
    benchmarker = Benchmarker(ds, num_samples_to_generate=30000, device=device)
    # Test for model 'aae'
    for seed in [1]:
        for model in ["vae", "aae", "char_rnn"]:
            _test_moses_benchmarks_match(model, seed, benchmarker)


def get_digress_scores(smiles_name: str, benchmarker: Benchmarker):
    digress_smiles_url = f"https://github.com/cvignac/DiGress/raw/refs/heads/main/generated_samples/{smiles_name}"
    digress_smiles_content = download_with_cache(digress_smiles_url, cache_dir="data")
    digress_smiles = digress_smiles_content.splitlines()
    digress_smiles_present = [s if s != "None" else None for s in digress_smiles]
    scores = benchmarker.benchmark(digress_smiles_present)
    print(scores)

    return scores


def test_digress_bencharks():
    # _test_digress_benchmark_match("digress_guacamol_smiles.txt")
    print("Testing DiGress benchmarks...")

    print("Testing DiGress benchmarks for GuacaMol...")
    ds_guacamol = SmilesDataset.load_guacamol_dataset()
    benchmarker = Benchmarker(ds_guacamol, num_samples_to_generate=10000, device=device)
    scores = get_digress_scores("digress_guacamol_smiles.txt", benchmarker)
    assert abs(scores["validity"]["valid_fraction"] - 0.852) < 0.01, (
        f"Expected valid fraction of 85.2% like in the original DiGress paper but got {scores['validity']['valid_fraction']}"
    )
    assert abs(scores["validity"]["unique_fraction_of_valids"] - 1.0) < 0.01, (
        f"Expected valid and unique fraction of 100% like in the original DiGress paper but got {scores['validity']['valid_and_unique_fraction']}"
    )
    assert (
        abs(scores["validity"]["unique_and_novel_fraction_of_valids"] - 0.999) < 0.01
    ), (
        f"Expected valid and unique and novel fraction of 99.9% like in the original DiGress paper but got {scores['validity']['unique_and_novel_fraction_of_valids']}"
    )
    assert abs(scores["fcd"]["fcd_normalized"] - 0.68) < 0.01, (
        f"Expected FCD score of 0.68 like in the original DiGress paper but got {scores['fcd']['fcd_normalized']}"
    )
    assert abs(scores["kl_score"] - 0.929) < 0.01, (
        f"Expected KL score of 92.9% like in the original DiGress paper but got {scores['kl_score']}"
    )

    print("Testing DiGress benchmarks for QM9 without H...")
    ds_qm9 = SmilesDataset.load_qm9_dataset()
    benchmarker = Benchmarker(ds_qm9, num_samples_to_generate=10000, device=device)
    scores = get_digress_scores("final_smiles_qm9_noH.txt", benchmarker)
    assert abs(scores["validity"]["valid_fraction"] - 0.99) < 0.01, (
        f"Expected valid fraction of 99% like in the original DiGress paper but got {scores['validity']['valid_fraction']}"
    )
    assert abs(scores["validity"]["unique_fraction"] - 0.962) < 0.01, (
        f"Expected valid and unique fraction of 96.2% like in the original DiGress paper but got {scores['validity']['valid_and_unique_fraction']}"
    )
    
def test_moses_benchmarker_on_train():
    ds = SmilesDataset.load_moses_dataset()
    benchmarker = Benchmarker(ds, num_samples_to_generate=15000, device=device)
    results = benchmarker.benchmark(ds.train_smiles)
    print(results)
    assert results["validity"]["valid_fraction"] > 0.99, (
        f"Expected valid fraction of almost 100% but got {results['validity']['valid_fraction']}"
    )
    assert results["validity"]["unique_fraction"] > 0.99, (
        f"Expected unique fraction of almost 100% but got {results['validity']['unique_fraction']}"
    )
    assert results["validity"]["valid_and_unique_fraction"] > 0.99, (
        f"Expected valid and unique fraction of almost 100% but got {results['validity']['valid_and_unique_fraction']}"
    )
    assert results["validity"]["unique_and_novel_fraction"] < 0.01, (
        f"Expected unique and novel fraction to be low, got {results['validity']['unique_and_novel_fraction']}"
    )
    assert results["fcd"]["fcd"] < 0.5, (
        f"Expected FCD score to be low, got {results['fcd']['fcd']}"
    )