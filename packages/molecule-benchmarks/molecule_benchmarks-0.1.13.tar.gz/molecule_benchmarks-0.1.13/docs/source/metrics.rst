
Valid, Unique, and Novel Fraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Definition**: Fraction of generated molecules that are simultaneously valid, unique, and novel (i.e., not present in the training set).

**Formula**: ``valid_and_unique_and_novel_fraction = n_valid_and_unique_and_novel / n_total``

**Range**: [0, 1], higher is better

**Interpretation**:
- 1.0: All generated molecules are valid, unique, and novel
- 0.0: No generated molecules meet all three criteria

This metric is a strict measure of generative quality, rewarding models that produce new, chemically valid, and non-duplicated molecules. It is especially useful for benchmarking generative models in de novo drug design and other applications where novelty and chemical correctness are both critical.
Metrics
=======

This section provides detailed explanations of all metrics used in the Molecule Benchmarks package. Understanding these metrics is crucial for interpreting benchmark results and comparing molecular generation models.

Overview
--------

The benchmark suite evaluates molecular generation models across multiple dimensions:

- **Validity**: Are the generated molecules chemically valid?
- **Uniqueness**: How many unique molecules are generated?
- **Novelty**: How many molecules are different from the training set?
- **Diversity**: How diverse are the generated molecules?
- **Distribution similarity**: How similar are the generated molecules to the reference distribution?

Validity Metrics
----------------

Valid Fraction
~~~~~~~~~~~~~~

**Definition**: Percentage of generated molecules that are chemically valid.

**Formula**: ``valid_fraction = n_valid / n_total``

**Range**: [0, 1], higher is better

**Interpretation**:
- 1.0: All generated molecules are chemically valid
- 0.5: Half of the generated molecules are valid
- 0.0: No valid molecules generated

**Code example**:

.. code-block:: python

   validity_score = results['validity']['valid_fraction']
   print(f"Valid molecules: {validity_score:.3f} ({validity_score*100:.1f}%)")

Unique Fraction
~~~~~~~~~~~~~~~

**Definition**: Percentage of generated molecules that are unique (no duplicates).

**Formula**: ``unique_fraction = n_unique / n_total``

**Range**: [0, 1], higher is better

**Interpretation**:
- 1.0: All generated molecules are unique
- 0.5: Half of the generated molecules are unique
- Low values indicate mode collapse or limited diversity

Valid and Unique Fraction
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Definition**: Percentage of molecules that are both chemically valid and unique.

**Formula**: ``valid_and_unique_fraction = n_valid_and_unique / n_total``

**Range**: [0, 1], higher is better

**Interpretation**: This is often considered the most important validity metric as it captures both chemical correctness and diversity.


Novel Fraction
~~~~~~~~~~~~~~

**Definition**: Percentage of generated molecules that are novel, i.e., not present in the training dataset. Novelty is typically measured among valid and unique molecules, but in this benchmark it is computed as the fraction of all generated molecules that are novel.

**Formula**: ``novel_fraction = n_novel / n_total``

**Range**: [0, 1], higher is better

**Interpretation**:
- High values indicate the model generates new molecules
- Low values suggest the model is memorizing training data

Unique Fraction at 1000
~~~~~~~~~~~~~~~~~~~~~~~

**Definition**: Fraction of unique molecules among the first 1000 generated molecules. If fewer than 1000 molecules are generated, the value is set to -1.

**Formula**: ``unique_fraction_at_1000 = n_unique_1000 / 1000``

**Range**: [0, 1] (or -1 if <1000 molecules), higher is better

**Interpretation**:
- 1.0: All of the first 1000 generated molecules are unique
- 0.5: Only 500 of the first 1000 are unique
- -1: Fewer than 1000 molecules were generated

This metric is useful for comparing models that generate a fixed number of molecules and for detecting early mode collapse.

Unique Fraction at 10000
~~~~~~~~~~~~~~~~~~~~~~~~

**Definition**: Fraction of unique molecules among the first 10000 generated molecules. If fewer than 10000 molecules are generated, the value is set to -1.

**Formula**: ``unique_fraction_at_10000 = n_unique_10000 / 10000``

**Range**: [0, 1] (or -1 if <10000 molecules), higher is better

**Interpretation**:
- 1.0: All of the first 10000 generated molecules are unique
- 0.5: Only 500 of the first 10000 are unique
- -1: Fewer than 10000 molecules were generated

This metric is useful for comparing models that generate a fixed number of molecules and for detecting early mode collapse.

Moses Metrics
-------------

The Moses metrics are based on the benchmarking suite from the paper "Molecular Sets (MOSES): A Benchmarking Platform for Molecular Generation Models" ([arXiv:1811.12823](https://arxiv.org/abs/1811.12823)).

Fraction Passing Moses Filters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Definition**: Percentage of molecules that pass a set of medicinal chemistry filters.

**Filters include**:
- Molecular weight: 150-500 Da
- LogP: -2 to 6
- Number of heavy atoms: 10-50
- Number of rings: ≤6
- PAINS (Pan Assay Interference) filters
- And more...

**Range**: [0, 1], higher is better

**Interpretation**: High values indicate drug-like molecules suitable for pharmaceutical applications.

**Code example**:

.. code-block:: python

   filter_score = results['moses']['fraction_passing_moses_filters']
   print(f"Drug-like molecules: {filter_score:.3f}")

SNN Score (Similarity to Nearest Neighbor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Definition**: Average similarity of generated molecules to their most similar molecule in the training set.

**Calculation**:
1. For each generated molecule, find the most similar training molecule
2. Calculate Tanimoto similarity using Morgan fingerprints
3. Average across all generated molecules

**Range**: [0, 1], optimal around 0.5-0.7

**Interpretation**:
- Too high (>0.8): Model is copying training data
- Too low (<0.3): Generated molecules are too different from training data
- Optimal range indicates good balance between novelty and drug-likeness

Internal Diversity (IntDiv)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Definition**: Average pairwise Tanimoto distance within the generated set.

**Variants**:
- **IntDiv**: Using p=1 (Manhattan distance)
- **IntDiv2**: Using p=2 (Euclidean distance)

**Formula**: ``IntDiv = 1 - average_pairwise_similarity``

**Range**: [0, 1], higher is better

**Interpretation**:
- High values indicate diverse molecular structures
- Low values suggest mode collapse or limited chemical space exploration

**Code example**:

.. code-block:: python

   diversity = results['moses']['IntDiv']
   print(f"Internal diversity: {diversity:.3f}")

Scaffold Similarity
~~~~~~~~~~~~~~~~~~~

**Definition**: Cosine similarity between scaffold distributions of generated and training molecules.

**Calculation**:
1. Extract Murcko scaffolds from molecules
2. Create frequency distributions
3. Calculate cosine similarity between distributions

**Range**: [0, 1], higher is better

**Interpretation**: Measures how well the model captures the scaffold diversity of the training set.

Fragment Similarity
~~~~~~~~~~~~~~~~~~~

**Definition**: Cosine similarity between fragment distributions of generated and training molecules.

**Calculation**:
1. Fragment molecules into substructures
2. Create frequency distributions
3. Calculate cosine similarity

**Range**: [0, 1], higher is better

**Interpretation**: Measures how well the model captures the chemical fragment space.

Distribution Metrics  
--------------------

KL Divergence Score
~~~~~~~~~~~~~~~~~~~

**Definition**: Measures similarity between molecular property distributions of generated and training sets.

**Properties evaluated**:
- BertzCT (molecular complexity)
- MolLogP (lipophilicity)
- MolWt (molecular weight)
- TPSA (topological polar surface area)
- NumHAcceptors (hydrogen bond acceptors)
- NumHDonors (hydrogen bond donors)
- NumRotatableBonds (rotatable bonds)
- NumAliphaticRings (aliphatic rings)
- NumAromaticRings (aromatic rings)

**Formula**: For each property, calculate ``KL(P_ref || P_gen)`` then average and transform: ``exp(-KL_avg)``

**Range**: [0, 1], higher is better

**Interpretation**:
- 1.0: Perfect match between distributions
- <0.5: Significant differences in molecular properties
- This metric captures how well the model reproduces the chemical property space

**Code example**:

.. code-block:: python

   kl_score = results['kl_score']
   print(f"Property distribution similarity: {kl_score:.3f}")

FCD Score (Fréchet ChemNet Distance)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Definition**: Measures similarity between generated and reference molecular distributions in a learned feature space.

**Calculation**:
1. Encode molecules using ChemNet (pre-trained neural network)
2. Calculate Fréchet distance between distributions
3. Lower scores indicate better similarity

**Variants**:
- **fcd**: Using all generated molecules
- **fcd_valid**: Using only valid generated molecules
- **fcd_normalized**: ``exp(-0.2 * fcd)`` for easier interpretation
- **fcd_valid_normalized**: ``exp(-0.2 * fcd_valid)``

**Range**: 
- **fcd**: [0, ∞], lower is better
- **fcd_normalized**: [0, 1], higher is better

**Interpretation**:
- FCD values <1: Excellent similarity
- FCD values 1-5: Good similarity  
- FCD values >10: Poor similarity

**Code example**:

.. code-block:: python

   fcd = results['fcd']['fcd']
   fcd_norm = results['fcd']['fcd_normalized']
   print(f"FCD score: {fcd:.2f} (normalized: {fcd_norm:.3f})")

Metric Interpretation Guidelines
--------------------------------

Quality Assessment
~~~~~~~~~~~~~~~~~~

**High-quality model characteristics**:
- Valid fraction > 0.9
- Valid and unique fraction > 0.8
- Novel fraction > 0.7
- SNN score: 0.5-0.7
- Internal diversity > 0.8
- KL score > 0.9
- FCD score < 2.0

**Warning signs**:
- Valid fraction < 0.5 (chemical knowledge issues)
- Unique fraction < 0.7 (mode collapse)
- Novel fraction < 0.3 (memorization)
- SNN score > 0.8 (copying training data)
- Internal diversity < 0.5 (limited diversity)

Model Comparison
~~~~~~~~~~~~~~~~

When comparing models, consider:

1. **Primary metrics**: Valid and unique fraction, SNN score, FCD score
2. **Secondary metrics**: Internal diversity, KL score, filter passage rate
3. **Application-specific**: Novel fraction for drug discovery, scaffold similarity for lead optimization

**Example comparison**:

.. code-block:: python

   def compare_models(results_dict):
       """Compare multiple model results."""
       for model_name, results in results_dict.items():
           validity = results['validity']['valid_and_unique_fraction']
           novelty = results['validity']['valid_and_unique_and_novel_fraction']
           diversity = results['moses']['IntDiv']
           similarity = results['moses']['snn_score']
           
           print(f"{model_name}:")
           print(f"  Quality: {validity:.3f}")
           print(f"  Novelty: {novelty:.3f}")  
           print(f"  Diversity: {diversity:.3f}")
           print(f"  Similarity: {similarity:.3f}")

Trade-offs
~~~~~~~~~~

Different metrics often involve trade-offs:

- **Validity vs. Novelty**: Higher novelty may reduce validity
- **Diversity vs. Quality**: More diverse generation may reduce average quality
- **Similarity vs. Novelty**: Optimal similarity range balances these factors

Statistical Significance
~~~~~~~~~~~~~~~~~~~~~~~~

For robust evaluation:

.. code-block:: python

   # Run multiple evaluations with different seeds
   results_list = []
   for seed in range(5):
       # Set random seed and run evaluation
       results = run_benchmark_with_seed(seed)
       results_list.append(results)
   
   # Calculate statistics
   import numpy as np
   
   validity_scores = [r['validity']['valid_fraction'] for r in results_list]
   mean_validity = np.mean(validity_scores)
   std_validity = np.std(validity_scores)
   
   print(f"Validity: {mean_validity:.3f} ± {std_validity:.3f}")

Advanced Metrics
----------------

For specialized applications, additional metrics can be computed:

Conditional Metrics
~~~~~~~~~~~~~~~~~~~

For property-conditioned generation:

- **MAE (Mean Absolute Error)**: Between target and generated properties
- **Conditional validity**: Validity rate for specific property ranges

**Code example**:

.. code-block:: python

   # Custom property analysis
   from rdkit.Chem import Descriptors
   
   def analyze_property_match(generated_smiles, target_logp):
       """Analyze LogP matching for conditional generation."""
       valid_mols = [Chem.MolFromSmiles(s) for s in generated_smiles if s]
       valid_mols = [m for m in valid_mols if m is not None]
       
       logp_values = [Descriptors.MolLogP(mol) for mol in valid_mols]
       mae = np.mean([abs(lp - target_logp) for lp in logp_values])
       
       return mae

Pharmacophore Metrics
~~~~~~~~~~~~~~~~~~~~~

For drug discovery applications:

- **Pharmacophore coverage**: Percentage of important pharmacophores covered
- **ADMET properties**: Drug metabolism and toxicity predictions

Scaffold Metrics
~~~~~~~~~~~~~~~~

For lead optimization:

- **Scaffold hopping**: Generation of molecules with different scaffolds but similar properties
- **Core preservation**: Maintaining key structural motifs

Best Practices
--------------

Comprehensive Evaluation
~~~~~~~~~~~~~~~~~~~~~~~~

Use multiple metrics for complete assessment:

.. code-block:: python

   def comprehensive_evaluation(results):
       """Print comprehensive metric analysis."""
       print("=== COMPREHENSIVE EVALUATION ===")
       
       # Validity
       v = results['validity']
       print(f"Validity: {v['valid_fraction']:.3f}")
       print(f"Uniqueness: {v['unique_fraction']:.3f}")
       print(f"Quality (V&U): {v['valid_and_unique_fraction']:.3f}")
       print(f"Novelty: {v['valid_and_unique_and_novel_fraction']:.3f}")
       
       # Moses
       m = results['moses']
       print(f"Drug-likeness: {m['fraction_passing_moses_filters']:.3f}")
       print(f"Training similarity: {m['snn_score']:.3f}")
       print(f"Diversity: {m['IntDiv']:.3f}")
       
       # Distribution
       print(f"Property match: {results['kl_score']:.3f}")
       print(f"Feature similarity: {results['fcd']['fcd']:.2f}")

Context-Aware Interpretation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Consider your application when interpreting metrics:

- **Early drug discovery**: Emphasize novelty and diversity
- **Lead optimization**: Focus on similarity and property matching
- **Chemical space exploration**: Prioritize diversity and coverage

Reporting Guidelines
~~~~~~~~~~~~~~~~~~~~

When publishing results:

1. Report all major metrics with confidence intervals
2. Provide dataset and evaluation details
3. Compare against established baselines
4. Discuss trade-offs and limitations
5. Include example molecules for qualitative assessment

**Example results table**:

.. code-block:: text

   Metric                    Model A    Model B    Baseline
   Valid fraction           0.95±0.02  0.88±0.03  0.92±0.01
   Valid & unique           0.87±0.03  0.82±0.04  0.85±0.02
   Novel fraction           0.76±0.04  0.69±0.05  0.71±0.03
   SNN score               0.63±0.02  0.58±0.03  0.61±0.02
   Internal diversity       0.84±0.02  0.89±0.02  0.82±0.03
   KL score                0.91±0.01  0.87±0.02  0.89±0.01
   FCD score               1.8±0.3    2.4±0.4    2.1±0.2
