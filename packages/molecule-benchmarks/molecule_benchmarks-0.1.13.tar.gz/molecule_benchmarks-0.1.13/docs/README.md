# Documentation for Molecule Benchmarks

This directory contains the documentation source files for the Molecule Benchmarks package.

## Building Documentation Locally

### Prerequisites

Install the documentation dependencies using uv:

```bash
# Install the package with documentation dependencies
uv sync --group docs

# Or install with development dependencies too
uv sync --group docs --group dev
```

### Building HTML Documentation

```bash
# Build HTML documentation
make html

# Or using sphinx-build directly with uv
uv run sphinx-build -b html source build/html
```

The documentation will be available in `build/html/index.html`.

### Live Development Server

For real-time updates while editing documentation:

```bash
# Start live server (sphinx-autobuild is included in docs dependencies)
make livehtml

# Or directly with uv
uv run sphinx-autobuild -b html source build/html
```

This will start a development server at `http://localhost:8000` that automatically rebuilds when you make changes.

### Other Output Formats

```bash
# Build PDF (requires LaTeX)
make latexpdf

# Build ePub
make epub

# Clean build directory
make clean
```

## Documentation Structure

```
docs/
├── source/
│   ├── _static/           # Static files (CSS, images)
│   ├── _templates/        # Custom templates
│   ├── conf.py           # Sphinx configuration
│   ├── index.rst         # Main documentation page
│   ├── installation.rst  # Installation guide
│   ├── quickstart.rst    # Quick start guide
│   ├── examples.rst      # Comprehensive examples
│   ├── api_reference.rst # API documentation
│   ├── datasets.rst      # Dataset documentation
│   ├── metrics.rst       # Metrics explanation
│   ├── contributing.rst  # Contribution guide
│   └── changelog.rst     # Version history
├── requirements.txt      # Documentation dependencies
├── Makefile             # Build commands (Unix)
└── make.bat            # Build commands (Windows)
```

## Writing Guidelines

### RestructuredText (RST)

The documentation uses RST format. Key syntax:

```rst
Title
=====

Subtitle
--------

**Bold text**
*Italic text*
``Inline code``

.. code-block:: python

   # Python code block
   import molecule_benchmarks

.. note::
   This is a note admonition

.. warning::
   This is a warning admonition
```

### Autodoc Integration

API documentation is automatically generated from docstrings:

```rst
.. autoclass:: module_name.ClassName
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: module_name.function_name
```

### Cross-References

Link to other sections:

```rst
See :doc:`installation` for setup instructions.
Reference :class:`molecule_benchmarks.Benchmarker` class.
Check :func:`molecule_benchmarks.dataset.load_smiles` function.
```

### Code Examples

Include runnable code examples:

```rst
.. code-block:: python

   from molecule_benchmarks import Benchmarker, SmilesDataset
   
   # Load dataset
   dataset = SmilesDataset.load_qm9_dataset()
   
   # Create benchmarker
   benchmarker = Benchmarker(dataset)
```

## Sphinx Configuration

Key configuration in `conf.py`:

- **Extensions**: autodoc, napoleon, sphinx_rtd_theme
- **Theme**: sphinx_rtd_theme (Read the Docs theme)
- **Autodoc**: Automatic API documentation generation
- **Napoleon**: Google/NumPy docstring support

## ReadTheDocs Integration

The documentation is automatically built and hosted on ReadTheDocs:

- **Configuration**: `.readthedocs.yaml` in project root
- **Requirements**: `requirements.txt` for RTD dependencies
- **Builds**: Triggered automatically on push to main branch

## Local Development Tips

1. **Use live reload**: `make livehtml` for real-time updates
2. **Check warnings**: Fix any Sphinx warnings for clean builds
3. **Test examples**: Ensure all code examples are runnable
4. **Preview locally**: Always test locally before pushing

## Common Issues

### RDKit Import Errors

If you encounter RDKit import errors during doc building:

```bash
# Install RDKit via conda if pip fails
conda install -c conda-forge rdkit
```

### Memory Issues

For large documentation builds:

```bash
# Increase memory limit
export SPHINXOPTS="-j 1"  # Use single process
make html
```

### Missing Dependencies

Install all required packages:

```bash
pip install -e ".[dev,docs]"
```

## Contributing to Documentation

1. **Edit source files** in `source/` directory
2. **Test locally** with `make html`
3. **Check for warnings** and fix them
4. **Preview in browser** before submitting
5. **Follow style guidelines** for consistency

See the main [Contributing Guide](source/contributing.rst) for more details.
