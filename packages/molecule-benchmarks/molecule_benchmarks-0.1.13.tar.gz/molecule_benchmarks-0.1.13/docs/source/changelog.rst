Changelog
=========

All notable changes to the Molecule Benchmarks package are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Changelog
=========

All notable changes to the Molecule Benchmarks package are documented here.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[0.1.9] - 2025-07-04
---------------------

Changed
~~~~~~~

- Updated documentation to match current version
- Fixed version inconsistencies across project files

[0.1.8] - 2025-06-29
---------------------

Changed
~~~~~~~

- Unique fraction at 1000 benchmark metric
- Scores now match Moses benchmark scores except for scaffold similarity

[0.1.6] - 2025-06-28
---------------------

Changed
~~~~~~~

- Improved performance with multiprocessing

[0.1.2] - 2025-06-27
---------------------

Added
~~~~~

- Direct SMILES evaluation via ``Benchmarker.benchmark(generated_smiles)`` method
- Simplified API for benchmarking pre-generated SMILES lists without implementing model interface

Changed
~~~~~~~

- Enhanced documentation with examples for both direct SMILES and model-based evaluation approaches

[0.1.0] - 2025-06-27
---------------------

Added
~~~~~

- Initial release of molecule-benchmarks package
- Comprehensive benchmark suite for molecular generation models
- Support for multiple datasets (QM9, Moses, GuacaMol)
- Validity, uniqueness, novelty, and diversity metrics
- Moses benchmark metrics implementation
- FCD (Fréchet ChemNet Distance) scoring
- KL divergence scoring for molecular property distributions
- Simple MoleculeGenerationModel protocol interface
- Built-in dummy model for testing
- Comprehensive documentation and examples
- Demo script showcasing package capabilities
- Support for both CPU and GPU computation
- Multiprocessing support for efficient computation

Core Features
~~~~~~~~~~~~~

**Benchmarker Class**
  - Main benchmarking interface
  - Support for both direct SMILES evaluation and model-based evaluation
  - Configurable sample sizes and device selection
  - Comprehensive metric calculation

**Dataset Support**
  - ``SmilesDataset`` class for handling molecular datasets
  - Built-in loaders for QM9, Moses, and GuacaMol datasets
  - Support for custom datasets from files or lists
  - Automatic SMILES canonicalization and validation

**Metrics Implementation**
  - Validity metrics (valid, unique, novel fractions)
  - Moses benchmark metrics (SNN score, internal diversity, filter passage)
  - FCD scoring using pre-trained ChemNet
  - KL divergence for property distribution comparison
  - Scaffold and fragment similarity analysis

**Model Interface**
  - ``MoleculeGenerationModel`` protocol for easy integration
  - ``DummyMoleculeGenerationModel`` for testing
  - Flexible batch generation support

**Utilities**
  - SMILES canonicalization with multiprocessing
  - Molecular property calculation
  - Statistical analysis functions
  - Chemical filtering and validation

Technical Details
~~~~~~~~~~~~~~~~~

**Dependencies**
  - RDKit for cheminformatics operations
  - PyTorch for neural network computations (FCD)
  - Pandas for data manipulation
  - SciPy for statistical computations
  - Requests for dataset downloads

**Performance Optimizations**
  - Multiprocessing for SMILES canonicalization
  - GPU support for FCD calculations
  - Efficient batch processing
  - Progress tracking with tqdm

**Quality Assurance**
  - Comprehensive test suite
  - Type hints throughout codebase
  - Linting and formatting with Ruff
  - Continuous integration

Upcoming Features
-----------------

Future releases may include:

- Additional benchmark datasets
- More chemical property metrics
- Support for 3D molecular representations
- Conditional generation metrics
- Web interface for benchmarking
- Integration with popular ML frameworks

Version History Summary
-----------------------

.. list-table:: Version History
   :header-rows: 1
   :widths: 10 15 75

   * - Version
     - Date
     - Key Features
   * - 0.1.2
     - 2025-06-27
     - Direct SMILES evaluation, improved documentation
   * - 0.1.0
     - 2025-06-27
     - Initial release with full benchmark suite

Migration Guide
---------------

From 0.1.0 to 0.1.2
~~~~~~~~~~~~~~~~~~~~

The 0.1.2 release is fully backward compatible with 0.1.0. The main addition is the simplified direct SMILES evaluation:

**New in 0.1.2:**

.. code-block:: python

   # Direct SMILES evaluation (new)
   results = benchmarker.benchmark(generated_smiles)

**Still supported from 0.1.0:**

.. code-block:: python

   # Model-based evaluation (existing)
   results = benchmarker.benchmark_model(model)

No code changes are required when upgrading from 0.1.0 to 0.1.2.

Deprecation Policy
------------------

We follow semantic versioning and maintain backward compatibility within major versions:

- **Minor versions** (0.x.0): May add new features but won't break existing functionality
- **Patch versions** (0.0.x): Bug fixes and documentation improvements only
- **Major versions** (x.0.0): May include breaking changes with migration guide

Deprecated features will be marked as such for at least one minor version before removal.

Contributing to Changelog
--------------------------

When contributing to the project, please update this changelog:

1. Add entries under "Unreleased" section
2. Use the format: ``[Added/Changed/Deprecated/Removed/Fixed/Security]``
3. Include brief description of the change
4. Reference issue numbers when applicable

Example entry:

.. code-block:: text

   Added
   ~~~~~
   
   - New diversity metric based on molecular fingerprints (#123)
   - Support for custom molecular descriptors in KL divergence calculation
   
   Fixed
   ~~~~~
   
   - Handle edge case in FCD calculation when no valid molecules generated (#124)

For detailed contribution guidelines, see the :doc:`contributing` section.
