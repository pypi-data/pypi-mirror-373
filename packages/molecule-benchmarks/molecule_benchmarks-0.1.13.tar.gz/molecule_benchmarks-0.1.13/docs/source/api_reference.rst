
API Reference
=============

.. currentmodule:: molecule_benchmarks

This section documents all public functions in the Molecule Benchmarks package.

.. autofunction:: molecule_benchmarks.benchmarker.canonicalize_smiles_without_stereochemistry

.. autofunction:: molecule_benchmarks.dataset.canonicalize_smiles_list

.. autofunction:: molecule_benchmarks.utils.remove_duplicates
.. autofunction:: molecule_benchmarks.utils.canonicalize
.. autofunction:: molecule_benchmarks.utils.canonicalize_list
.. autofunction:: molecule_benchmarks.utils.smiles_to_rdkit_mol
.. autofunction:: molecule_benchmarks.utils.split_charged_mol
.. autofunction:: molecule_benchmarks.utils.initialise_neutralisation_reactions
.. autofunction:: molecule_benchmarks.utils.neutralise_charges
.. autofunction:: molecule_benchmarks.utils.filter_and_canonicalize
.. autofunction:: molecule_benchmarks.utils.calculate_internal_pairwise_similarities
.. autofunction:: molecule_benchmarks.utils.calculate_pairwise_similarities
.. autofunction:: molecule_benchmarks.utils.get_fingerprints_from_smileslist
.. autofunction:: molecule_benchmarks.utils.get_fingerprints
.. autofunction:: molecule_benchmarks.utils.get_mols
.. autofunction:: molecule_benchmarks.utils.highest_tanimoto_precalc_fps
.. autofunction:: molecule_benchmarks.utils.continuous_kldiv
.. autofunction:: molecule_benchmarks.utils.discrete_kldiv
.. autofunction:: molecule_benchmarks.utils.calculate_pc_descriptors
.. autofunction:: molecule_benchmarks.utils.parse_molecular_formula
.. autofunction:: molecule_benchmarks.utils.is_valid_smiles
.. autofunction:: molecule_benchmarks.utils.filter_valid_smiles
.. autofunction:: molecule_benchmarks.utils.download_with_cache
.. autofunction:: molecule_benchmarks.utils.available_cpu_count
.. autofunction:: molecule_benchmarks.utils.mapper
.. autofunction:: molecule_benchmarks.utils.get_mol

.. autofunction:: molecule_benchmarks.moses_metrics.average_agg_tanimoto
.. autofunction:: molecule_benchmarks.moses_metrics.fingerprints
.. autofunction:: molecule_benchmarks.moses_metrics.fingerprint
.. autofunction:: molecule_benchmarks.moses_metrics.fraction_passes_filters
.. autofunction:: molecule_benchmarks.moses_metrics.get_filters
.. autofunction:: molecule_benchmarks.moses_metrics.mol_passes_filters
.. autofunction:: molecule_benchmarks.moses_metrics.internal_diversity
.. autofunction:: molecule_benchmarks.moses_metrics.compute_scaffolds
.. autofunction:: molecule_benchmarks.moses_metrics.get_n_rings
.. autofunction:: molecule_benchmarks.moses_metrics.compute_scaffold
.. autofunction:: molecule_benchmarks.moses_metrics.cos_similarity
.. autofunction:: molecule_benchmarks.moses_metrics.fragmenter
.. autofunction:: molecule_benchmarks.moses_metrics.compute_fragments

.. autofunction:: molecule_benchmarks.__init__.main
