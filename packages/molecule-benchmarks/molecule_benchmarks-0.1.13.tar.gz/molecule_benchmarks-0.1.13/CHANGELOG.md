# [0.1.13] - 2025-08-31

### Changed

- API reference documentation now lists all public functions for clarity and simplicity.
- Fixed Sphinx/Docutils warnings and errors in `moses_metrics.py` docstrings for better documentation builds.
- Improved docstring formatting for `fingerprints` and `internal_diversity` functions.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.12] - 2025-07-08

### Changed

- Added `cache_dir` parameter to dataset loading methods to cache canonicalized smiles strings

## [0.1.10] - 2025-07-04

### Changed

- Fixed KL divergence computation to remove chirochemistry from the SMILES strings to perfectly match the guacamol benchmark scores

## [0.1.8] - 2025-06-29

### Changed

- Unique fraction at 1000 benchmark metric
- Scores now match Moses benchmark scores except for scaffold similarity

## [0.1.6] - 2025-06-28

### Changed

- Improved performance with multiprocessing

## [0.1.2] - 2025-06-27

### Added

- Direct SMILES evaluation via `Benchmarker.benchmark(generated_smiles)` method
- Simplified API for benchmarking pre-generated SMILES lists without implementing model interface

### Changed

- Enhanced documentation with examples for both direct SMILES and model-based evaluation approaches

## [0.1.0] - 2025-06-27

### Added

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
