Contributing
============

We welcome contributions to the Molecule Benchmarks project! This guide will help you get started with contributing code, documentation, or other improvements.

Getting Started
---------------

Development Setup
~~~~~~~~~~~~~~~~~

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   .. code-block:: bash

      git clone https://github.com/yourusername/molecule_benchmarks.git
      cd molecule_benchmarks

3. **Create a virtual environment**:

   .. code-block:: bash

      python -m venv molecule_benchmarks_dev
      source molecule_benchmarks_dev/bin/activate  # On Windows: molecule_benchmarks_dev\Scripts\activate

4. **Install in development mode**:

   .. code-block:: bash

      pip install -e ".[dev]"

5. **Install additional development tools**:

   .. code-block:: bash

      pip install pre-commit
      pre-commit install

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

The development dependencies include:

- **pytest**: Testing framework
- **ruff**: Linting and formatting
- **types-requests**: Type hints for requests
- **pre-commit**: Git hooks for code quality

You can install these with:

.. code-block:: bash

   pip install pytest ruff types-requests pre-commit

Making Changes
--------------

Code Style
~~~~~~~~~~

We use **Ruff** for linting and formatting. The configuration is in ``pyproject.toml``.

Before submitting code:

.. code-block:: bash

   # Format code
   ruff format .

   # Check for linting issues
   ruff check .

   # Fix auto-fixable issues
   ruff check --fix .

Type Hints
~~~~~~~~~~

We use type hints throughout the codebase. Please add type hints to new functions:

.. code-block:: python

   def process_molecules(smiles: list[str]) -> list[str | None]:
       """Process a list of SMILES strings.
       
       Args:
           smiles: List of SMILES strings to process
           
       Returns:
           List of processed SMILES or None for invalid molecules
       """
       processed = []
       for s in smiles:
           try:
               processed.append(canonicalize_smiles(s))
           except Exception:
               processed.append(None)
       return processed

Documentation
~~~~~~~~~~~~~

All public functions and classes should have docstrings:

.. code-block:: python

   class NewBenchmarkMetric:
       """A new metric for evaluating molecular generation models.
       
       This metric calculates... and is useful for...
       
       Args:
           parameter1: Description of parameter1
           parameter2: Description of parameter2
           
       Example:
           >>> metric = NewBenchmarkMetric(param1="value")
           >>> score = metric.calculate(molecules)
           >>> print(f"Score: {score:.3f}")
       """
       
       def __init__(self, parameter1: str, parameter2: int = 10):
           self.parameter1 = parameter1
           self.parameter2 = parameter2
       
       def calculate(self, molecules: list[str]) -> float:
           """Calculate the metric score.
           
           Args:
               molecules: List of SMILES strings
               
           Returns:
               Metric score between 0 and 1
           """
           # Implementation here
           pass

Testing
-------

Writing Tests
~~~~~~~~~~~~~

All new functionality should include tests. We use **pytest** for testing.

Test file structure:

.. code-block:: text

   tests/
   ├── test_benchmarker.py      # Tests for benchmarker module
   ├── test_datasets.py         # Tests for dataset module
   ├── test_moses.py           # Tests for Moses metrics
   └── test_new_feature.py     # Tests for your new feature

Example test:

.. code-block:: python

   import pytest
   from molecule_benchmarks import Benchmarker, SmilesDataset

   def test_new_metric():
       """Test the new metric calculation."""
       # Setup
       dataset = SmilesDataset.load_dummy_dataset()
       benchmarker = Benchmarker(dataset, num_samples_to_generate=10)
       
       test_smiles = ["CCO", "CC(=O)O", "c1ccccc1", None]
       
       # Test
       results = benchmarker.benchmark(test_smiles)
       
       # Assertions
       assert "new_metric" in results
       assert 0 <= results["new_metric"] <= 1
       assert isinstance(results["new_metric"], float)

   def test_edge_cases():
       """Test edge cases and error handling."""
       dataset = SmilesDataset.load_dummy_dataset()
       benchmarker = Benchmarker(dataset, num_samples_to_generate=5)
       
       # Test with empty list
       with pytest.raises(ValueError):
           benchmarker.benchmark([])
       
       # Test with all None values
       results = benchmarker.benchmark([None] * 5)
       assert results["validity"]["valid_fraction"] == 0.0

Running Tests
~~~~~~~~~~~~~

Run the full test suite:

.. code-block:: bash

   pytest

Run specific tests:

.. code-block:: bash

   pytest tests/test_benchmarker.py::test_benchmarker
   pytest tests/test_new_feature.py

Run with coverage:

.. code-block:: bash

   pytest --cov=molecule_benchmarks --cov-report=html

Types of Contributions
----------------------

Bug Fixes
~~~~~~~~~~

1. **Create an issue** describing the bug
2. **Reference the issue** in your commit message
3. **Add tests** that reproduce the bug
4. **Fix the bug** and ensure tests pass

Example commit message:

.. code-block:: text

   Fix FCD calculation with empty molecule lists (#42)
   
   - Handle edge case when no valid molecules are generated
   - Add comprehensive tests for empty inputs
   - Improve error messages for better debugging

New Features
~~~~~~~~~~~~

1. **Discuss the feature** in an issue first
2. **Design the API** considering consistency with existing code
3. **Implement with tests** and documentation
4. **Update relevant documentation**

Feature implementation checklist:

- [ ] Implementation with type hints
- [ ] Comprehensive tests including edge cases
- [ ] Docstrings with examples
- [ ] Update API documentation if needed
- [ ] Add to changelog

New Metrics
~~~~~~~~~~~

When adding new metrics:

1. **Research the metric** and cite relevant papers
2. **Implement in appropriate module** (likely ``benchmarker.py``)
3. **Add to result types** (update TypedDict definitions)
4. **Include in comprehensive examples**
5. **Document interpretation** in metrics documentation

Example metric implementation:

.. code-block:: python

   def _compute_new_metric(self, generated_smiles: list[str | None]) -> float:
       """Compute the new metric for generated SMILES.
       
       This metric measures... based on the paper:
       Author et al. "Title" Journal (Year)
       
       Args:
           generated_smiles: List of generated SMILES strings
           
       Returns:
           Metric score between 0 and 1, higher is better
       """
       valid_smiles = [s for s in generated_smiles if s is not None]
       
       if not valid_smiles:
           return 0.0
       
       # Metric calculation
       score = calculate_metric_score(valid_smiles, self.dataset.train_smiles)
       
       return float(score)

Documentation Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

Documentation contributions are very welcome:

- **Fix typos or unclear explanations**
- **Add more examples**
- **Improve API documentation**
- **Add tutorials for specific use cases**

To build documentation locally:

.. code-block:: bash

   cd docs
   make html
   open build/html/index.html  # On macOS
   # Or navigate to docs/build/html/index.html in your browser

Dataset Support
~~~~~~~~~~~~~~~

Adding support for new datasets:

1. **Add class method** to ``SmilesDataset`` 
2. **Handle data download and processing**
3. **Add tests** with small sample data
4. **Document the dataset** in datasets.rst

Example dataset method:

.. code-block:: python

   @classmethod
   def load_new_dataset(cls, fraction: float = 1.0):
       """Load the New Dataset.
       
       Dataset description, source, and characteristics.
       
       Args:
           fraction: Fraction of dataset to load (for memory efficiency)
           
       Returns:
           SmilesDataset instance
       """
       # Download and process data
       train_smiles = download_and_process_train_data(fraction)
       validation_smiles = download_and_process_validation_data(fraction)
       
       return cls(train_smiles=train_smiles, validation_smiles=validation_smiles)

Pull Request Process
--------------------

Before Submitting
~~~~~~~~~~~~~~~~~

1. **Run tests**: ``pytest``
2. **Check linting**: ``ruff check .``
3. **Format code**: ``ruff format .``
4. **Update documentation** if needed
5. **Add entry to CHANGELOG.md**

Submitting
~~~~~~~~~~

1. **Create a descriptive pull request title**
2. **Fill out the pull request template**
3. **Reference related issues**
4. **Request review from maintainers**

Pull request template:

.. code-block:: text

   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement

   ## Testing
   - [ ] All tests pass
   - [ ] Added new tests for changes
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] Changelog updated

Review Process
~~~~~~~~~~~~~~

- **Maintainers will review** your pull request
- **Feedback may be provided** for improvements
- **CI checks must pass** before merging
- **Reviews may take a few days** depending on complexity

Code of Conduct
---------------

This project follows a code of conduct to ensure a welcoming environment:

- **Be respectful** of differing opinions and experiences
- **Provide constructive feedback**
- **Focus on what's best** for the community
- **Show empathy** towards other contributors

Getting Help
------------

If you need help contributing:

1. **Check existing issues** for similar questions
2. **Create a new issue** with the "question" label
3. **Join discussions** in existing issues
4. **Read the documentation** thoroughly

Resources
---------

Development Resources
~~~~~~~~~~~~~~~~~~~~~

- **GitHub repository**: https://github.com/peteole/molecule_benchmarks
- **Issue tracker**: https://github.com/peteole/molecule_benchmarks/issues
- **Documentation**: https://molecule-benchmarks.readthedocs.io/

External Resources
~~~~~~~~~~~~~~~~~~

- **RDKit documentation**: https://www.rdkit.org/docs/
- **Moses paper**: https://arxiv.org/abs/1811.12823
- **GuacaMol paper**: https://arxiv.org/abs/1811.09621
- **FCD paper**: https://arxiv.org/abs/1803.09518

Common Development Tasks
------------------------

Adding a New Metric
~~~~~~~~~~~~~~~~~~~

1. Implement the metric calculation
2. Add to benchmark results TypedDict
3. Update the benchmarker to include the metric
4. Add comprehensive tests
5. Document the metric

Example structure:

.. code-block:: python

   # In benchmarker.py
   def _compute_my_metric(self, generated_smiles: list[str | None]) -> float:
       # Implementation
       pass

   # Update benchmark method to include metric
   def benchmark(self, generated_smiles: list[str | None]) -> BenchmarkResults:
       # ... existing code ...
       my_metric_score = self._compute_my_metric(generated_smiles)
       
       return {
           # ... existing results ...
           "my_metric": my_metric_score,
       }

Release Process
---------------

For maintainers, the release process involves:

1. **Update version** in ``pyproject.toml``
2. **Update CHANGELOG.md** with release notes
3. **Create release tag** on GitHub
4. **CI automatically publishes** to PyPI
5. **Update documentation** if needed

Version numbering follows semantic versioning:
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

Thank You!
----------

Thank you for contributing to Molecule Benchmarks! Your contributions help make molecular generation research more accessible and reproducible for the entire community.
