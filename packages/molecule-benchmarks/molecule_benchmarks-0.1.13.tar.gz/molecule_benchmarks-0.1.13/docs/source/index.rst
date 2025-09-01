Welcome to Molecule Benchmarks Documentation
============================================

**Molecule Benchmarks** is a comprehensive benchmark suite for evaluating generative models for molecules. This package provides standardized metrics and evaluation protocols for assessing the quality of molecular generation models in drug discovery and cheminformatics.

.. image:: https://badge.fury.io/py/molecule-benchmarks.svg
   :target: https://badge.fury.io/py/molecule-benchmarks
   :alt: PyPI version

.. image:: https://img.shields.io/badge/python-3.11+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.11+

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

Features
--------

* **Comprehensive Metrics**: Validity, uniqueness, novelty, diversity, and similarity metrics
* **Standard Benchmarks**: Implements metrics from Moses, GuacaMol, and FCD papers
* **Easy Integration**: Simple interface for integrating with any generative model
* **Direct SMILES Evaluation**: Benchmark pre-generated SMILES lists without implementing a model interface
* **Multiple Datasets**: Built-in support for QM9, Moses, and GuacaMol datasets
* **Efficient Computation**: Optimized for large-scale evaluation with multiprocessing support

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install molecule-benchmarks

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from molecule_benchmarks import Benchmarker, SmilesDataset

   # Load a dataset
   dataset = SmilesDataset.load_qm9_dataset(subset_size=10000)

   # Initialize benchmarker
   benchmarker = Benchmarker(
       dataset=dataset,
       num_samples_to_generate=10000,
       device="cpu"  # or "cuda" for GPU
   )

   # Your generated SMILES
   generated_smiles = [
       "CCO",           # Ethanol
       "CC(=O)O",       # Acetic acid
       "c1ccccc1",      # Benzene
       # ... more molecules
   ]

   # Run benchmarks
   results = benchmarker.benchmark(generated_smiles)
   print(results)

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   examples
   api_reference
   datasets
   metrics
   contributing
   changelog

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
