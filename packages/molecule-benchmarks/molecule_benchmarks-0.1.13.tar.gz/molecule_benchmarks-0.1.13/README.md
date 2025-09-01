# Molecule Benchmarks

[![PyPI version](https://badge.fury.io/py/molecule-benchmarks.svg)](https://badge.fury.io/py/molecule-benchmarks)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive benchmark suite for evaluating generative models for molecules. This package provides standardized metrics and evaluation protocols for assessing the quality of molecular generation models in drug discovery and cheminformatics.

## Features

- **Comprehensive Metrics**: Validity, uniqueness, novelty, diversity, and similarity metrics
- **Standard Benchmarks**: Implements metrics from Moses, GuacaMol, and FCD papers
- **Easy Integration**: Simple interface for integrating with any generative model
- **Direct SMILES Evaluation**: Benchmark pre-generated SMILES lists without implementing a model interface
- **Multiple Datasets**: Built-in support for QM9, Moses, and GuacaMol datasets
- **Efficient Computation**: Optimized for large-scale evaluation with multiprocessing support

## Installation

```bash
pip install molecule-benchmarks
```

## Quick Start

You can use the benchmark suite in two ways:

### Option 1: Direct SMILES Evaluation (Simplified)

If you already have generated SMILES strings, you can benchmark them directly. Just ensure you have at least the number of samples specified in `num_samples_to_generate`.

```python
from molecule_benchmarks import Benchmarker, SmilesDataset

# Load a dataset
dataset = SmilesDataset.load_qm9_dataset(subset_size=10000)

# Initialize benchmarker
benchmarker = Benchmarker(
    dataset=dataset,
    num_samples_to_generate=10000,# You need to generate at least this many samples
    device="cpu"  # or "cuda" for GPU
)

# Your generated SMILES (replace with your actual generated molecules)
generated_smiles = [
    "CCO",           # Ethanol
    "CC(=O)O",       # Acetic acid
    "c1ccccc1",      # Benzene
    "CC(C)O",        # Isopropanol
    "CCN",           # Ethylamine
    None,            # Invalid molecule (use None for failures)
    # ... more molecules up to num_samples_to_generate
]

# Run benchmarks directly on the SMILES list
results = benchmarker.benchmark(generated_smiles)
print(results)
```

### Option 2: Model-Based Evaluation

To use the benchmark suite with a generative model, implement the `MoleculeGenerationModel` protocol. This will generate the required number of samples and run the benchmarks.

```python
from molecule_benchmarks.model import MoleculeGenerationModel

class MyGenerativeModel(MoleculeGenerationModel):
    def __init__(self, model_path):
        # Initialize your model here
        self.model = load_model(model_path)
    
    def generate_molecule_batch(self) -> list[str | None]:
        """Generate a batch of molecules as SMILES strings.
        
        Returns:
            List of SMILES strings. Return None for invalid molecules.
        """
        # Your generation logic here
        batch = self.model.generate(batch_size=100)
        return [self.convert_to_smiles(mol) for mol in batch]

# Initialize your model
model = MyGenerativeModel("path/to/model")

# Run benchmarks using the model
results = benchmarker.benchmark_model(model)
print(results)
```

### 3. Analyze Results

The benchmark returns comprehensive metrics:

```python
# Validity metrics
print(f"Valid molecules: {results['validity']['valid_fraction']:.3f}")
print(f"Valid & unique: {results['validity']['valid_and_unique_fraction']:.3f}")
print(f"Valid & unique & novel: {results['validity']['valid_and_unique_and_novel_fraction']:.3f}")

# Diversity and similarity metrics
print(f"Internal diversity: {results['moses']['IntDiv']:.3f}")
print(f"SNN score: {results['moses']['snn_score']:.3f}")

# Chemical property distribution similarity
print(f"KL divergence score: {results['kl_score']:.3f}")

# Fréchet ChemNet Distance
print(f"FCD score: {results['fcd']['fcd']:.3f}")
```

## Complete Examples

### Example 1: Direct SMILES Benchmarking (Recommended for Simplicity)

```python
from molecule_benchmarks import Benchmarker, SmilesDataset

# Load dataset
print("Loading dataset...")
dataset = SmilesDataset.load_qm9_dataset(max_train_samples=1000)

# Create benchmarker
benchmarker = Benchmarker(
    dataset=dataset,
    num_samples_to_generate=100,
    device="cpu"
)

# Your generated SMILES (replace with your actual generated molecules)
generated_smiles = [
    "CCO",           # Ethanol
    "CC(=O)O",       # Acetic acid
    "c1ccccc1",      # Benzene
    "CC(C)O",        # Isopropanol
    "CCN",           # Ethylamine
    None,            # Invalid molecule
    # ... add more molecules up to 100 total
] + [None] * (100 - 6)  # Pad with None to reach desired count

# Run benchmarks directly
print("Running benchmarks...")
results = benchmarker.benchmark(generated_smiles)

# Print results (same as below)
print("\n=== Validity Metrics ===")
print(f"Valid molecules: {results['validity']['valid_fraction']:.3f}")
print(f"Unique molecules: {results['validity']['unique_fraction']:.3f}")
print(f"Valid & unique: {results['validity']['valid_and_unique_fraction']:.3f}")
print(f"Novel molecules: {results['validity']['valid_and_unique_and_novel_fraction']:.3f}")

print("\n=== Moses Metrics ===")
print(f"Passing Moses filters: {results['moses']['fraction_passing_moses_filters']:.3f}")
print(f"SNN score: {results['moses']['snn_score']:.3f}")
print(f"Internal diversity (p=1): {results['moses']['IntDiv']:.3f}")
print(f"Internal diversity (p=2): {results['moses']['IntDiv2']:.3f}")

print("\n=== Distribution Metrics ===")
print(f"KL divergence score: {results['kl_score']:.3f}")
print(f"FCD score: {results['fcd']['fcd']:.3f}")
print(f"FCD (valid only): {results['fcd']['fcd_valid']:.3f}")
```

### Example 2: Model-Based Benchmarking

Here's a complete example using the built-in dummy model:

```python
from molecule_benchmarks import Benchmarker, SmilesDataset
from molecule_benchmarks.model import DummyMoleculeGenerationModel

# Load dataset
print("Loading dataset...")
dataset = SmilesDataset.load_qm9_dataset(max_train_samples=1000)

# Create benchmarker
benchmarker = Benchmarker(
    dataset=dataset,
    num_samples_to_generate=100,
    device="cpu"
)

# Create a dummy model (replace with your model)
model = DummyMoleculeGenerationModel([
    "CCO",           # Ethanol
    "CC(=O)O",       # Acetic acid
    "c1ccccc1",      # Benzene
    "CC(C)O",        # Isopropanol
    "CCN",           # Ethylamine
    None,            # Invalid molecule
])

# Run benchmarks using the model
print("Running benchmarks...")
results = benchmarker.benchmark_model(model)

# Print results
print("\n=== Validity Metrics ===")
print(f"Valid molecules: {results['validity']['valid_fraction']:.3f}")
print(f"Unique molecules: {results['validity']['unique_fraction']:.3f}")
print(f"Valid & unique: {results['validity']['valid_and_unique_fraction']:.3f}")
print(f"Novel molecules: {results['validity']['valid_and_unique_and_novel_fraction']:.3f}")

print("\n=== Moses Metrics ===")
print(f"Passing Moses filters: {results['moses']['fraction_passing_moses_filters']:.3f}")
print(f"SNN score: {results['moses']['snn_score']:.3f}")
print(f"Internal diversity (p=1): {results['moses']['IntDiv']:.3f}")
print(f"Internal diversity (p=2): {results['moses']['IntDiv2']:.3f}")

print("\n=== Distribution Metrics ===")
print(f"KL divergence score: {results['kl_score']:.3f}")
print(f"FCD score: {results['fcd']['fcd']:.3f}")
print(f"FCD (valid only): {results['fcd']['fcd_valid']:.3f}")
```

## Supported Datasets

The package includes several built-in datasets:

```python
from molecule_benchmarks import SmilesDataset

# QM9 dataset (small molecules)
dataset = SmilesDataset.load_qm9_dataset(subset_size=10000)

# Moses dataset (larger, drug-like molecules)
dataset = SmilesDataset.load_moses_dataset(fraction=0.1)

# GuacaMol dataset
dataset = SmilesDataset.load_guacamol_dataset(fraction=0.1)

# Custom dataset from files
dataset = SmilesDataset(
    train_smiles="path/to/train.txt",
    validation_smiles="path/to/valid.txt"
)
```

## Metrics Explained

### Validity Metrics

- **Valid fraction**: Percentage of generated molecules that are chemically valid
- **Unique fraction**: Percentage of generated molecules that are unique
- **Novel fraction**: Percentage of generated molecules not seen in training data

### Moses Metrics

Based on the [Moses paper](https://arxiv.org/abs/1811.12823):

- **SNN score**: Similarity to nearest neighbor in training set
- **Internal diversity**: Average pairwise Tanimoto distance within generated set
- **Scaffold similarity**: Similarity of molecular scaffolds to training set
- **Fragment similarity**: Similarity of molecular fragments to training set

### Distribution Metrics

- **KL divergence score**: Measures similarity of molecular property distributions
- **FCD score**: Fréchet ChemNet Distance, measures distribution similarity in learned feature space

## Advanced Usage

### Direct SMILES Evaluation

For most use cases, directly evaluating a list of generated SMILES is the simplest approach:

```python
# Custom number of samples and device
benchmarker = Benchmarker(
    dataset=dataset,
    num_samples_to_generate=50000,
    device="cuda"  # Use GPU for faster computation
)

# Your generated SMILES list (with None for invalid generations)
my_generated_smiles = [
    "CCO", "c1ccccc1", "CC(=O)O", None, "invalid_smiles", 
    # ... up to 50000 molecules
]

# Run benchmarks directly
results = benchmarker.benchmark(my_generated_smiles)

# Access specific metric computations
validity_scores = benchmarker._compute_validity_scores(my_generated_smiles)
fcd_scores = benchmarker._compute_fcd_scores(my_generated_smiles)
```

### Model-Based Evaluation

For integration with generative models:

```python
class BatchedModel(MoleculeGenerationModel):
    def generate_molecule_batch(self) -> list[str | None]:
        # Generate larger batches for efficiency
        return self.model.sample(batch_size=1000)

# Use the model with benchmarker
results = benchmarker.benchmark_model(BatchedModel())
```

### Important Notes

- **SMILES format**: Use None for molecules that failed to generate or are invalid
- **Batch size**: The `num_samples_to_generate` parameter determines how many molecules will be evaluated
- **Validation**: Invalid SMILES are automatically detected and handled in the metrics
- **Memory**: For large evaluations (>10k molecules), consider using GPU acceleration with `device="cuda"`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This benchmark suite implements and builds upon metrics from several important papers:

- [Moses: A Benchmarking Platform for Molecular Generation Models](https://arxiv.org/abs/1811.12823)
- [GuacaMol: Benchmarking Models for De Novo Molecular Design](https://arxiv.org/abs/1811.09621)
- [Fréchet ChemNet Distance: A Metric for Generative Models for Molecules](https://arxiv.org/abs/1803.09518)
