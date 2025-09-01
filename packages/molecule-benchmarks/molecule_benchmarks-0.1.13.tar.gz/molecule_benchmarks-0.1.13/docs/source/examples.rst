Examples
========

This section provides complete, runnable examples demonstrating various use cases of the Molecule Benchmarks package.

Example 1: Basic SMILES Evaluation
-----------------------------------

This example shows the simplest way to benchmark a list of generated SMILES strings.

.. code-block:: python

   from molecule_benchmarks import Benchmarker, SmilesDataset

   def basic_smiles_benchmark():
       """Basic example of benchmarking generated SMILES directly."""
       
       # Load dataset
       print("Loading QM9 dataset...")
       dataset = SmilesDataset.load_qm9_dataset(subset_size=1000)
       print(f"Training molecules: {len(dataset.train_smiles)}")
       print(f"Validation molecules: {len(dataset.validation_smiles)}")

       # Create benchmarker
       benchmarker = Benchmarker(
           dataset=dataset,
           num_samples_to_generate=100,
           device="cpu"
       )

       # Example generated SMILES (replace with your actual generated molecules)
       generated_smiles = [
           "CCO",           # Ethanol
           "CC(=O)O",       # Acetic acid
           "c1ccccc1",      # Benzene
           "CC(C)O",        # Isopropanol
           "CCN",           # Ethylamine
           "CC(C)(C)O",     # tert-Butanol
           "c1cccnc1",      # Pyridine
           "CC(=O)N",       # Acetamide
           "c1ccc2ccccc2c1", # Naphthalene
           "CC(C)N",        # Isopropylamine
           None,            # Invalid molecule
       ] + [None] * (100 - 11)  # Pad to reach desired count

       # Run benchmarks
       print("Running benchmarks...")
       results = benchmarker.benchmark(generated_smiles)

       # Print results
       print_results(results)

   def print_results(results):
       """Helper function to print benchmark results."""
       print("\n" + "="*50)
       print("BENCHMARK RESULTS")
       print("="*50)

       # Validity metrics
       print("\n🔍 Validity Metrics:")
       validity = results["validity"]
       print(f"   Total molecules: {validity['num_molecules_generated']}")
       print(f"   Valid: {validity['valid_fraction']:.3f} ({validity['valid_fraction']*100:.1f}%)")
       print(f"   Unique: {validity['unique_fraction']:.3f} ({validity['unique_fraction']*100:.1f}%)")
       print(f"   Valid & unique: {validity['valid_and_unique_fraction']:.3f}")
       print(f"   Novel: {validity['valid_and_unique_and_novel_fraction']:.3f}")

       # Moses metrics
       print("\n📊 Moses Metrics:")
       moses = results["moses"]
       print(f"   Passing filters: {moses['fraction_passing_moses_filters']:.3f}")
       print(f"   SNN score: {moses['snn_score']:.3f}")
       print(f"   Internal diversity (p=1): {moses['IntDiv']:.3f}")
       print(f"   Internal diversity (p=2): {moses['IntDiv2']:.3f}")
       print(f"   Scaffold similarity: {moses['scaffolds_similarity']:.3f}")
       print(f"   Fragment similarity: {moses['fragment_similarity']:.3f}")

       # Distribution metrics
       print("\n📈 Distribution Metrics:")
       print(f"   KL divergence score: {results['kl_score']:.3f}")
       print(f"   FCD score: {results['fcd']['fcd']:.3f}")
       print(f"   FCD (valid only): {results['fcd']['fcd_valid']:.3f}")

   if __name__ == "__main__":
       basic_smiles_benchmark()

Example 2: Model-Based Evaluation
----------------------------------

This example demonstrates how to integrate with a generative model using the ``MoleculeGenerationModel`` protocol.

.. code-block:: python

   from molecule_benchmarks import Benchmarker, SmilesDataset
   from molecule_benchmarks.model import MoleculeGenerationModel
   import random

   class SimpleRandomModel(MoleculeGenerationModel):
       """Example model that randomly samples from a predefined list."""
       
       def __init__(self, molecule_pool: list[str]):
           """Initialize with a pool of molecules to sample from.
           
           Args:
               molecule_pool: List of SMILES strings to randomly sample from
           """
           self.molecule_pool = molecule_pool
           self.batch_size = 50
           
       def generate_molecule_batch(self) -> list[str | None]:
           """Generate a batch by randomly sampling from the molecule pool."""
           batch = []
           for _ in range(self.batch_size):
               if random.random() < 0.1:  # 10% chance of failure
                   batch.append(None)
               else:
                   batch.append(random.choice(self.molecule_pool))
           return batch

   def model_based_benchmark():
       """Example of benchmarking using a model interface."""
       
       # Load dataset
       print("Loading Moses dataset...")
       dataset = SmilesDataset.load_moses_dataset(fraction=0.01)  # Small fraction for demo
       
       # Create a model with diverse molecules
       molecule_pool = [
           "CCO", "CC(=O)O", "c1ccccc1", "CC(C)O", "CCN",
           "CC(C)(C)O", "c1cccnc1", "CC(=O)N", "c1ccc2ccccc2c1",
           "CC(C)N", "CCCO", "c1ccoc1", "CC(C)C", "CCC(=O)O",
           "c1ccc(cc1)O", "CC(=O)OC", "c1ccc(cc1)N", "CCCN",
           "c1ccc(cc1)C", "CC(=O)NC", "c1ccc2[nH]ccc2c1",
           "CC(C)CC(=O)O", "c1ccc(cc1)S", "CCCCN", "c1cnc2ccccc2n1"
       ]
       
       model = SimpleRandomModel(molecule_pool)
       
       # Create benchmarker
       benchmarker = Benchmarker(
           dataset=dataset,
           num_samples_to_generate=500,
           device="cpu"
       )
       
       # Run benchmarks
       print("Running model-based benchmarks...")
       results = benchmarker.benchmark_model(model)
       
       print_results(results)

   if __name__ == "__main__":
       model_based_benchmark()

Example 3: Custom Dataset Usage
--------------------------------

This example shows how to use custom datasets from files or lists.

.. code-block:: python

   from molecule_benchmarks import Benchmarker, SmilesDataset
   import tempfile
   import os

   def custom_dataset_example():
       """Example using custom datasets from files and lists."""
       
       # Create temporary files with SMILES data
       train_smiles = [
           "CCO", "CC(=O)O", "c1ccccc1", "CC(C)O", "CCN",
           "CC(C)(C)O", "c1cccnc1", "CC(=O)N", "c1ccc2ccccc2c1",
           "CC(C)N", "CCCO", "c1ccoc1", "CC(C)C", "CCC(=O)O"
       ]
       
       valid_smiles = [
           "c1ccc(cc1)O", "CC(=O)OC", "c1ccc(cc1)N", "CCCN",
           "c1ccc(cc1)C", "CC(=O)NC"
       ]
       
       # Method 1: From lists directly
       print("Creating dataset from lists...")
       dataset_from_lists = SmilesDataset(
           train_smiles=train_smiles,
           validation_smiles=valid_smiles
       )
       
       # Method 2: From temporary files
       with tempfile.TemporaryDirectory() as temp_dir:
           train_file = os.path.join(temp_dir, "train.txt")
           valid_file = os.path.join(temp_dir, "valid.txt")
           
           # Write SMILES to files
           with open(train_file, 'w') as f:
               f.write('\n'.join(train_smiles))
           
           with open(valid_file, 'w') as f:
               f.write('\n'.join(valid_smiles))
           
           print("Creating dataset from files...")
           dataset_from_files = SmilesDataset(
               train_smiles=train_file,
               validation_smiles=valid_file
           )
       
       # Use the dataset
       benchmarker = Benchmarker(
           dataset=dataset_from_lists,
           num_samples_to_generate=20,
           device="cpu"
       )
       
       # Generate some test molecules
       generated_smiles = [
           "CCCO", "c1ccc(cc1)S", "CCCCN", "c1cnc2ccccc2n1",
           "CC(C)CC(=O)O", "c1ccc2[nH]ccc2c1", "CC(=O)NCCO",
           None, None, None  # Some failures
       ] * 2  # Repeat to get 20 samples
       
       results = benchmarker.benchmark(generated_smiles)
       print_results(results)

   if __name__ == "__main__":
       custom_dataset_example()

Example 4: Large-Scale Benchmarking
------------------------------------

This example demonstrates best practices for large-scale benchmarking with GPU acceleration.

.. code-block:: python

   import torch
   from molecule_benchmarks import Benchmarker, SmilesDataset
   from molecule_benchmarks.model import MoleculeGenerationModel

   class EfficientBatchModel(MoleculeGenerationModel):
       """Example of an efficient model with large batch sizes."""
       
       def __init__(self, base_molecules: list[str], batch_size: int = 1000):
           self.base_molecules = base_molecules
           self.batch_size = batch_size
           
       def generate_molecule_batch(self) -> list[str | None]:
           """Generate large batches for efficiency."""
           import random
           
           batch = []
           for _ in range(self.batch_size):
               if random.random() < 0.05:  # 5% failure rate
                   batch.append(None)
               else:
                   # Add some variation to base molecules
                   base_mol = random.choice(self.base_molecules)
                   batch.append(base_mol)
           
           return batch

   def large_scale_benchmark():
       """Example of large-scale benchmarking with optimizations."""
       
       # Check if CUDA is available
       device = "cuda" if torch.cuda.is_available() else "cpu"
       print(f"Using device: {device}")
       
       # Load larger dataset
       print("Loading Moses dataset...")
       dataset = SmilesDataset.load_moses_dataset(fraction=0.1)
       print(f"Training set size: {len(dataset.train_smiles)}")
       
       # Create model with diverse molecules
       base_molecules = dataset.train_smiles[:1000]  # Use first 1000 as base
       model = EfficientBatchModel(base_molecules, batch_size=1000)
       
       # Create benchmarker with GPU support
       benchmarker = Benchmarker(
           dataset=dataset,
           num_samples_to_generate=10000,  # Large number of samples
           device=device
       )
       
       print("Running large-scale benchmarks...")
       print("This may take several minutes...")
       
       results = benchmarker.benchmark_model(model)
       
       # Print comprehensive results
       print_detailed_results(results)

   def print_detailed_results(results):
       """Print detailed results with additional metrics."""
       print("\n" + "="*60)
       print("DETAILED BENCHMARK RESULTS")
       print("="*60)
       
       validity = results["validity"]
       moses = results["moses"]
       fcd = results["fcd"]
       
       print(f"\n📊 Summary Scores:")
       print(f"   Overall Quality Score: {calculate_quality_score(results):.3f}")
       print(f"   Validity Score: {validity['valid_fraction']:.3f}")
       print(f"   Diversity Score: {moses['IntDiv']:.3f}")
       print(f"   Novelty Score: {validity['valid_and_unique_and_novel_fraction']:.3f}")
       
       print(f"\n🔬 Detailed Validity Analysis:")
       print(f"   Total generated: {validity['num_molecules_generated']:,}")
       print(f"   Valid molecules: {int(validity['valid_fraction'] * validity['num_molecules_generated']):,}")
       print(f"   Unique molecules: {int(validity['unique_fraction'] * validity['num_molecules_generated']):,}")
       print(f"   Novel molecules: {int(validity['valid_and_unique_and_novel_fraction'] * validity['num_molecules_generated']):,}")
       
       print(f"\n🎯 Moses Benchmark Analysis:")
       print(f"   Filter pass rate: {moses['fraction_passing_moses_filters']:.3f}")
       print(f"   Similarity to training (SNN): {moses['snn_score']:.3f}")
       print(f"   Internal diversity (Tanimoto): {moses['IntDiv']:.3f}")
       print(f"   Scaffold coverage: {moses['scaffolds_similarity']:.3f}")
       print(f"   Fragment coverage: {moses['fragment_similarity']:.3f}")
       
       print(f"\n📈 Distribution Similarity:")
       print(f"   KL divergence score: {results['kl_score']:.3f}")
       print(f"   FCD (all molecules): {fcd['fcd']:.2f}")
       print(f"   FCD (valid only): {fcd['fcd_valid']:.2f}")
       print(f"   FCD normalized: {fcd['fcd_normalized']:.3f}")

   def calculate_quality_score(results):
       """Calculate an overall quality score."""
       validity = results["validity"]["valid_fraction"]
       uniqueness = results["validity"]["unique_fraction"]
       novelty = results["validity"]["valid_and_unique_and_novel_fraction"]
       diversity = results["moses"]["IntDiv"]
       kl_score = results["kl_score"]
       
       # Weighted average of key metrics
       quality_score = (
           0.3 * validity +
           0.2 * uniqueness +
           0.2 * novelty +
           0.15 * diversity +
           0.15 * kl_score
       )
       return quality_score

   if __name__ == "__main__":
       large_scale_benchmark()

Example 5: Comparative Analysis
-------------------------------

This example shows how to compare multiple models or generation strategies.

.. code-block:: python

   from molecule_benchmarks import Benchmarker, SmilesDataset
   from molecule_benchmarks.model import MoleculeGenerationModel
   import random

   class StrategyModel(MoleculeGenerationModel):
       """Model that uses different generation strategies."""
       
       def __init__(self, strategy: str, base_molecules: list[str]):
           self.strategy = strategy
           self.base_molecules = base_molecules
           
       def generate_molecule_batch(self) -> list[str | None]:
           """Generate molecules using different strategies."""
           batch_size = 100
           batch = []
           
           for _ in range(batch_size):
               if self.strategy == "conservative":
                   # Low failure rate, less diversity
                   if random.random() < 0.02:
                       batch.append(None)
                   else:
                       batch.append(random.choice(self.base_molecules[:50]))
                       
               elif self.strategy == "diverse":
                   # Higher failure rate, more diversity
                   if random.random() < 0.15:
                       batch.append(None)
                   else:
                       batch.append(random.choice(self.base_molecules))
                       
               elif self.strategy == "novel":
                   # Focus on novel-like molecules
                   if random.random() < 0.08:
                       batch.append(None)
                   else:
                       # Modify existing molecules (simplified)
                       base = random.choice(self.base_molecules)
                       if "C" in base and random.random() < 0.3:
                           batch.append(base.replace("C", "N", 1))
                       else:
                           batch.append(base)
           
           return batch

   def comparative_analysis():
       """Compare different generation strategies."""
       
       # Load dataset
       dataset = SmilesDataset.load_qm9_dataset(subset_size=2000)
       base_molecules = dataset.train_smiles[:200]
       
       strategies = ["conservative", "diverse", "novel"]
       results_dict = {}
       
       for strategy in strategies:
           print(f"\nTesting {strategy} strategy...")
           
           model = StrategyModel(strategy, base_molecules)
           benchmarker = Benchmarker(
               dataset=dataset,
               num_samples_to_generate=1000,
               device="cpu"
           )
           
           results = benchmarker.benchmark_model(model)
           results_dict[strategy] = results
           
           print(f"   Validity: {results['validity']['valid_fraction']:.3f}")
           print(f"   Novelty: {results['validity']['valid_and_unique_and_novel_fraction']:.3f}")
           print(f"   Diversity: {results['moses']['IntDiv']:.3f}")
       
       # Compare results
       print_comparison(results_dict)

   def print_comparison(results_dict):
       """Print comparison across strategies."""
       print("\n" + "="*60)
       print("STRATEGY COMPARISON")
       print("="*60)
       
       strategies = list(results_dict.keys())
       
       print(f"\n{'Metric':<25} " + " ".join(f"{s:>12}" for s in strategies))
       print("-" * (25 + 13 * len(strategies)))
       
       metrics = [
           ("Validity", lambda r: r['validity']['valid_fraction']),
           ("Uniqueness", lambda r: r['validity']['unique_fraction']),
           ("Novelty", lambda r: r['validity']['valid_and_unique_and_novel_fraction']),
           ("Diversity (p=1)", lambda r: r['moses']['IntDiv']),
           ("SNN Score", lambda r: r['moses']['snn_score']),
           ("KL Score", lambda r: r['kl_score']),
           ("FCD Score", lambda r: r['fcd']['fcd']),
       ]
       
       for metric_name, metric_func in metrics:
           values = [metric_func(results_dict[s]) for s in strategies]
           print(f"{metric_name:<25} " + " ".join(f"{v:>12.3f}" for v in values))
       
       # Highlight best performing strategy for each metric
       print(f"\n🏆 Best Performance:")
       for metric_name, metric_func in metrics:
           values = [(s, metric_func(results_dict[s])) for s in strategies]
           if metric_name == "FCD Score":  # Lower is better for FCD
               best_strategy, best_value = min(values, key=lambda x: x[1])
           else:  # Higher is better for other metrics
               best_strategy, best_value = max(values, key=lambda x: x[1])
           print(f"   {metric_name}: {best_strategy} ({best_value:.3f})")

   if __name__ == "__main__":
       comparative_analysis()

Running the Examples
--------------------

To run these examples:

1. Save each example to a separate Python file (e.g., ``basic_example.py``)
2. Install molecule-benchmarks: ``pip install molecule-benchmarks``
3. Run the example: ``python basic_example.py``

Each example is self-contained and demonstrates different aspects of the benchmarking suite. You can modify the parameters, datasets, and generation strategies to suit your specific needs.

Performance Considerations
--------------------------

* **Start small**: Begin with small datasets and sample sizes for initial testing
* **Use GPU**: Enable CUDA for faster FCD calculations when available
* **Batch optimization**: Larger batch sizes generally improve efficiency
* **Memory monitoring**: Monitor memory usage for large-scale evaluations
* **Parallel processing**: The package automatically uses multiprocessing for some operations
