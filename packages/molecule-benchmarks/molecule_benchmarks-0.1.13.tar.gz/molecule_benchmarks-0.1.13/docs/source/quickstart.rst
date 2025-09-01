Quick Start Guide
=================

This guide will help you get started with Molecule Benchmarks in just a few minutes.

Basic Workflow
--------------

The typical workflow with Molecule Benchmarks involves three steps:

1. **Load a dataset** - Choose from built-in datasets or use your own
2. **Generate or provide molecules** - Either use a generative model or provide SMILES directly
3. **Run benchmarks** - Evaluate using comprehensive metrics

Option 1: Direct SMILES Evaluation (Recommended)
-------------------------------------------------

This is the simplest approach if you already have generated SMILES strings.

.. code-block:: python

   from molecule_benchmarks import Benchmarker, SmilesDataset

   # Step 1: Load a dataset
   dataset = SmilesDataset.load_qm9_dataset(subset_size=10000)

   # Step 2: Initialize benchmarker
   benchmarker = Benchmarker(
       dataset=dataset,
       num_samples_to_generate=10000,  # You need at least this many samples
       device="cpu"  # or "cuda" for GPU
   )

   # Step 3: Your generated SMILES (replace with your actual generated molecules)
   generated_smiles = [
       "CCO",           # Ethanol
       "CC(=O)O",       # Acetic acid
       "c1ccccc1",      # Benzene
       "CC(C)O",        # Isopropanol
       "CCN",           # Ethylamine
       None,            # Invalid molecule (use None for failures)
       # ... more molecules up to num_samples_to_generate
   ]

   # Step 4: Run benchmarks directly on the SMILES list
   results = benchmarker.benchmark(generated_smiles)
   print(results)

Option 2: Model-Based Evaluation
---------------------------------

If you want to integrate with a generative model, implement the ``MoleculeGenerationModel`` protocol:

.. code-block:: python

   from molecule_benchmarks import Benchmarker, SmilesDataset
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

Understanding the Results
-------------------------

The benchmark returns a comprehensive set of metrics:

.. code-block:: python

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

Available Datasets
------------------

Choose from several built-in datasets:

QM9 Dataset
~~~~~~~~~~~

Small molecules dataset, good for initial testing:

.. code-block:: python

   # Load full QM9 dataset
   dataset = SmilesDataset.load_qm9_dataset()
   
   # Load subset for faster testing
   dataset = SmilesDataset.load_qm9_dataset(subset_size=1000)

Moses Dataset
~~~~~~~~~~~~~

Larger dataset with drug-like molecules:

.. code-block:: python

   # Load full Moses dataset
   dataset = SmilesDataset.load_moses_dataset()
   
   # Load fraction for faster processing
   dataset = SmilesDataset.load_moses_dataset(fraction=0.1)

GuacaMol Dataset
~~~~~~~~~~~~~~~~

Benchmark dataset from the GuacaMol paper:

.. code-block:: python

   # Load full GuacaMol dataset
   dataset = SmilesDataset.load_guacamol_dataset()
   
   # Load fraction for faster processing
   dataset = SmilesDataset.load_guacamol_dataset(fraction=0.1)

Custom Dataset
~~~~~~~~~~~~~~

Use your own SMILES files:

.. code-block:: python

   dataset = SmilesDataset(
       train_smiles="path/to/train.txt",
       validation_smiles="path/to/valid.txt"
   )

   # Or from lists
   train_smiles = ["CCO", "CC(=O)O", "c1ccccc1"]
   valid_smiles = ["CC(C)O", "CCN"]
   dataset = SmilesDataset(train_smiles, valid_smiles)

Performance Tips
----------------

GPU Acceleration
~~~~~~~~~~~~~~~~

For faster FCD calculations, use GPU:

.. code-block:: python

   benchmarker = Benchmarker(
       dataset=dataset,
       num_samples_to_generate=10000,
       device="cuda"  # Requires CUDA-enabled PyTorch
   )

Batch Size Optimization
~~~~~~~~~~~~~~~~~~~~~~~

For model-based evaluation, optimize your batch size:

.. code-block:: python

   class OptimizedModel(MoleculeGenerationModel):
       def generate_molecule_batch(self) -> list[str | None]:
           # Generate larger batches for efficiency
           return self.model.sample(batch_size=1000)

Memory Management
~~~~~~~~~~~~~~~~~

For large evaluations, consider:

* Using smaller dataset subsets for initial testing
* Processing in smaller chunks
* Monitoring memory usage

Common Issues and Solutions
---------------------------

Invalid SMILES Handling
~~~~~~~~~~~~~~~~~~~~~~~~

Always use ``None`` for invalid molecules:

.. code-block:: python

   def safe_generate_smiles(mol):
       try:
           return mol_to_smiles(mol)
       except:
           return None  # Don't return invalid SMILES strings

Sample Size Requirements
~~~~~~~~~~~~~~~~~~~~~~~~

Ensure you have enough samples:

.. code-block:: python

   if len(generated_smiles) < benchmarker.num_samples_to_generate:
       raise ValueError(f"Need at least {benchmarker.num_samples_to_generate} samples")

Validation Checks
~~~~~~~~~~~~~~~~~

The benchmarker automatically:

* Canonicalizes SMILES strings
* Filters out invalid molecules
* Handles None values appropriately

Next Steps
----------

* Explore the :doc:`examples` for complete working examples
* Learn about specific :doc:`metrics` and their interpretations
* Check the :doc:`api_reference` for detailed API documentation
* See :doc:`datasets` for more information about available datasets
