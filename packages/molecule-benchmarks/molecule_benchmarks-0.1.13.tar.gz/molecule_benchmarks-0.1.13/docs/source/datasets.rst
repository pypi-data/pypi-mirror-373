Datasets
========

The Molecule Benchmarks package provides several built-in datasets commonly used in molecular generation research, as well as support for custom datasets.

Built-in Datasets
------------------

QM9 Dataset
~~~~~~~~~~~

The QM9 dataset consists of small organic molecules with up to 9 heavy atoms (C, N, O, F).

**Characteristics:**
- **Size**: ~134,000 molecules
- **Atom types**: C, H, N, O, F
- **Heavy atoms**: Up to 9
- **Properties**: Quantum mechanical properties available
- **Use case**: Initial testing, small molecule generation

**Usage:**

.. code-block:: python

   from molecule_benchmarks import SmilesDataset

   # Load full dataset
   dataset = SmilesDataset.load_qm9_dataset()

   # Load subset for faster processing
   dataset = SmilesDataset.load_qm9_dataset(max_train_samples=10000)

**Example molecules:**
- ``C`` (Methane)
- ``CO`` (Formaldehyde) 
- ``CCO`` (Ethanol)
- ``c1ccccc1`` (Benzene)

Moses Dataset
~~~~~~~~~~~~~

The Moses dataset contains drug-like molecules from the ZINC database, commonly used for benchmarking molecular generation models.

**Characteristics:**
- **Training size**: ~1.58 million molecules
- **Test size**: ~176,000 molecules
- **Source**: ZINC database
- **Molecular weight**: 250-350 Da
- **LogP**: -1 to 3.5
- **Use case**: Drug-like molecule generation

**Usage:**

.. code-block:: python

   # Load full dataset
   dataset = SmilesDataset.load_moses_dataset()

   # Load fraction for faster processing
   dataset = SmilesDataset.load_moses_dataset(max_train_samples=1000)

**Example molecules:**
- ``Cc1ccc(cc1)S(=O)(=O)N2CCOCC2`` (Drug-like compound)
- ``COc1ccc(cc1)C(=O)Nc2ccccc2`` (Pharmaceutical scaffold)

GuacaMol Dataset
~~~~~~~~~~~~~~~~

The GuacaMol dataset is designed for benchmarking molecular generation models, focusing on drug-like properties.

**Characteristics:**
- **Training size**: ~1.36 million molecules
- **Validation size**: ~60,000 molecules
- **Source**: ChEMBL database
- **Focus**: Drug-like molecules
- **Use case**: Pharmaceutical applications

**Usage:**

.. code-block:: python

   # Load full dataset
   dataset = SmilesDataset.load_guacamol_dataset()

   # Load fraction for memory efficiency
   dataset = SmilesDataset.load_guacamol_dataset(max_train_samples=1000)

Custom Datasets
---------------

From Files
~~~~~~~~~~

You can create datasets from your own SMILES files:

.. code-block:: python

   dataset = SmilesDataset(
       train_smiles="path/to/train_smiles.txt",
       validation_smiles="path/to/validation_smiles.txt"
   )

**File format:**
- One SMILES string per line
- No header required
- Empty lines are ignored
- Comments (starting with #) are supported

**Example file content:**

.. code-block:: text

   # Training molecules
   CCO
   CC(=O)O
   c1ccccc1
   CC(C)O
   
   # More molecules...

From Lists
~~~~~~~~~~

Create datasets directly from Python lists:

.. code-block:: python

   train_smiles = [
       "CCO",           # Ethanol
       "CC(=O)O",       # Acetic acid
       "c1ccccc1",      # Benzene
       "CC(C)O",        # Isopropanol
   ]
   
   validation_smiles = [
       "CCN",           # Ethylamine
       "c1cccnc1",      # Pyridine
   ]
   
   dataset = SmilesDataset(
       train_smiles=train_smiles,
       validation_smiles=validation_smiles
   )

From Mixed Sources
~~~~~~~~~~~~~~~~~~

You can mix different source types:

.. code-block:: python

   # Training from file, validation from list
   dataset = SmilesDataset(
       train_smiles="large_training_set.txt",
       validation_smiles=["CCO", "CC(=O)O", "c1ccccc1"]
   )

Dataset Properties
------------------

All datasets provide the following methods and properties:

.. code-block:: python

   # Access SMILES strings
   train_smiles = dataset.get_train_smiles()
   validation_smiles = dataset.get_validation_smiles()
   
   # Access RDKit molecule objects
   train_molecules = dataset.get_train_molecules()
   validation_molecules = dataset.get_validation_molecules()
   
   # Dataset sizes
   print(f"Training set size: {len(dataset.train_smiles)}")
   print(f"Validation set size: {len(dataset.validation_smiles)}")

Data Processing
---------------

Automatic Canonicalization
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All SMILES strings are automatically canonicalized using RDKit:

.. code-block:: python

   # Input SMILES (various representations)
   input_smiles = [
       "CCO",           # Already canonical
       "OCC",           # Non-canonical ethanol
       "c1ccccc1",      # Benzene
       "C1=CC=CC=C1",   # Non-canonical benzene
   ]
   
   dataset = SmilesDataset(
       train_smiles=input_smiles,
       validation_smiles=["CCN"]
   )
   
   # All SMILES are now canonical
   print(dataset.train_smiles)
   # Output: ['CCO', 'CCO', 'c1ccccc1', 'c1ccccc1']

Invalid Molecule Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~

Invalid SMILES are automatically filtered out:

.. code-block:: python

   input_smiles = [
       "CCO",           # Valid
       "invalid_smiles", # Invalid - will be removed
       "CC(=O)O",       # Valid
       "",              # Empty - will be removed
   ]
   
   dataset = SmilesDataset(
       train_smiles=input_smiles,
       validation_smiles=["CCN"]
   )
   
   print(len(dataset.train_smiles))  # Output: 2 (only valid molecules)

Dataset Statistics
------------------

You can analyze dataset properties:

.. code-block:: python

   from rdkit import Chem
   from rdkit.Chem import Descriptors
   
   def analyze_dataset(dataset):
       """Analyze basic properties of a dataset."""
       molecules = dataset.get_train_molecules()
       
       # Filter out None values (invalid molecules)
       valid_molecules = [mol for mol in molecules if mol is not None]
       
       # Calculate basic descriptors
       mol_weights = [Descriptors.MolWt(mol) for mol in valid_molecules]
       log_p_values = [Descriptors.MolLogP(mol) for mol in valid_molecules]
       
       print(f"Dataset size: {len(valid_molecules)}")
       print(f"Average molecular weight: {sum(mol_weights)/len(mol_weights):.2f}")
       print(f"Average LogP: {sum(log_p_values)/len(log_p_values):.2f}")
       
       # Atom count distribution
       atom_counts = [mol.GetNumAtoms() for mol in valid_molecules]
       print(f"Average atom count: {sum(atom_counts)/len(atom_counts):.2f}")

   # Analyze QM9 dataset
   dataset = SmilesDataset.load_qm9_dataset(max_train_samples=1000)
   analyze_dataset(dataset)

Best Practices
--------------

Dataset Selection
~~~~~~~~~~~~~~~~~

Choose datasets based on your application:

- **QM9**: Small molecules, initial testing, method development
- **Moses**: Drug-like molecules, pharmaceutical applications
- **GuacaMol**: Benchmark comparisons, drug discovery
- **Custom**: Domain-specific applications

Size Considerations
~~~~~~~~~~~~~~~~~~~

For development and testing:

.. code-block:: python

   # Start with small subsets
   dataset = SmilesDataset.load_qm9_dataset(max_train_samples=1000)
   
   # Scale up gradually
   dataset = SmilesDataset.load_moses_dataset(max_train_samples=10000)

For production benchmarking:

.. code-block:: python

   # Use full datasets for final evaluation
   dataset = SmilesDataset.load_moses_dataset()

Memory Management
~~~~~~~~~~~~~~~~~

For large datasets:

.. code-block:: python

   # Load in chunks or use fractions
   dataset = SmilesDataset.load_moses_dataset(max_train_samples=1000)
   
   # Monitor memory usage
   import psutil
   print(f"Memory usage: {psutil.virtual_memory().percent}%")


Dataset Splits
--------------

The built-in datasets use standard train/validation splits:

- **QM9**: 80% train, 20% validation
- **Moses**: Predefined train/test split from original paper
- **GuacaMol**: Predefined train/validation split

For custom datasets, consider:

.. code-block:: python

   import random
   
   def create_split(all_smiles, train_fraction=0.8):
       """Create train/validation split."""
       random.seed(42)  # For reproducibility
       random.shuffle(all_smiles)
       
       split_idx = int(len(all_smiles) * train_fraction)
       train_smiles = all_smiles[:split_idx]
       validation_smiles = all_smiles[split_idx:]
       
       return train_smiles, validation_smiles
   
   # Example usage
   all_molecules = ["CCO", "CC(=O)O", "c1ccccc1", "CC(C)O", "CCN"]
   train, validation = create_split(all_molecules)
   
   dataset = SmilesDataset(
       train_smiles=train,
       validation_smiles=validation
   )
