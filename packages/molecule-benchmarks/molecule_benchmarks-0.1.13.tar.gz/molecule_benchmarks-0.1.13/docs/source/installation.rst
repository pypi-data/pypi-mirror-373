Installation
============

Requirements
------------

* Python 3.11 or higher
* pip package manager


Dependencies
------------

Molecule Benchmarks automatically installs the following dependencies:

Core Dependencies
~~~~~~~~~~~~~~~~~

* **rdkit** (>=2025.3.3) - Core cheminformatics library
* **pandas** (>=2.3.0) - Data manipulation and analysis
* **numpy** - Numerical computing (installed with pandas)
* **scipy** (>=1.16.0) - Scientific computing
* **tqdm** (>=4.67.1) - Progress bars
* **requests** (>=2.32.4) - HTTP library for dataset downloads

Machine Learning Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **fcd** (>=1.2.2) - Fréchet ChemNet Distance calculation
* **torch** - PyTorch (installed with fcd)
* **torchmetrics** (>=1.0.0) - Machine learning metrics for PyTorch

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

For advanced chemical property calculations:

* **psi4** - Quantum chemistry calculations (optional, for conditional metrics)

Installation Methods
--------------------

PyPI (Recommended)
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install molecule-benchmarks

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

For development or to get the latest features:

.. code-block:: bash

   git clone https://github.com/peteole/molecule_benchmarks.git
   cd molecule_benchmarks
   pip install -e .

With Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/peteole/molecule_benchmarks.git
   cd molecule_benchmarks
   pip install -e ".[dev]"

Verification
------------

Verify your installation by running:

.. code-block:: python

   import molecule_benchmarks
   print(molecule_benchmarks.__version__)



GPU Support
-----------

For faster FCD calculations, ensure PyTorch is installed with CUDA support:

.. code-block:: bash

   # Install PyTorch with CUDA (adjust version as needed)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   
   # Then install molecule-benchmarks
   pip install molecule-benchmarks

Compatibility Issues
~~~~~~~~~~~~~~~~~~~~

If you experience compatibility issues:

1. Check your Python version: ``python --version``
2. Update pip: ``pip install --upgrade pip``
3. Try installing in a fresh virtual environment:

   .. code-block:: bash

      python -m venv molecule_benchmarks_env
      source molecule_benchmarks_env/bin/activate  # On Windows: molecule_benchmarks_env\Scripts\activate
      pip install molecule-benchmarks

Docker Installation
-------------------

For a containerized environment:

.. code-block:: dockerfile

   FROM python:3.12-slim

   RUN pip install molecule-benchmarks

   WORKDIR /app
   COPY . .

   CMD ["python", "your_script.py"]

