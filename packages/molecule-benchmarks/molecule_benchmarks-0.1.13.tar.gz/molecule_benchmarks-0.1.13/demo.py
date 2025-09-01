#!/usr/bin/env python3
"""
Demo script for the molecule-benchmarks package.

This script demonstrates how to use the benchmark suite to evaluate
a molecular generation model.
"""

import json

from molecule_benchmarks import Benchmarker, SmilesDataset
from molecule_benchmarks.model import MoleculeGenerationModel


class DummyMoleculeGenerationModel(MoleculeGenerationModel):
    """A dummy model that generates a fixed set of SMILES strings for testing."""

    def __init__(self, mols: list[str | None]):
        """Initialize the dummy model with a predefined list of SMILES strings.

        Args:
            mols: A list of SMILES strings to use for generation.
        """
        self.mols = mols

    def generate_molecule_batch(self) -> list[str | None]:
        """Generate a batch containing all predefined molecules.

        Returns:
            The complete list of predefined molecules.
        """
        return self.mols.copy()


def main():
    """Run the demo benchmark."""
    print("🧪 Molecule Benchmarks Demo")
    print("=" * 50)

    # Load dataset
    print("\n📦 Loading QM9 dataset (subset)...")
    dataset = SmilesDataset.load_qm9_dataset(max_train_samples=100)
    print(f"   Training molecules: {len(dataset.train_smiles)}")
    print(f"   Validation molecules: {len(dataset.validation_smiles)}")

    # Create benchmarker
    print("\n⚙️  Setting up benchmarker...")
    benchmarker = Benchmarker(
        dataset=dataset,
        num_samples_to_generate=200,  # Small number for demo
        device="cpu",
    )

    # Create a diverse dummy model for demonstration
    print("\n🤖 Creating demonstration model...")
    demo_molecules = [
        "CCO",  # Ethanol
        "CC(=O)O",  # Acetic acid
        "c1ccccc1",  # Benzene
        "CC(C)O",  # Isopropanol
        "CCN",  # Ethylamine
        "CC(C)(C)O",  # tert-Butanol
        "c1cccnc1",  # Pyridine
        "CC(=O)N",  # Acetamide
        "c1ccc2ccccc2c1",  # Naphthalene
        "CC(C)N",  # Isopropylamine
        "CCCO",  # Propanol
        "c1ccoc1",  # Furan
        "CC(C)C",  # Isobutane
        "CCO[H]",  # Invalid SMILES
        None,  # Invalid molecule
    ]

    model = DummyMoleculeGenerationModel(demo_molecules)

    # Run benchmarks
    print("\n🏃 Running benchmarks...")
    print("   This may take a few minutes...")

    results = benchmarker.benchmark_model(model)

    # Display results
    print("\n📊 Benchmark Results")
    print("=" * 50)

    # Validity metrics
    print("\n🔍 Validity Metrics:")
    validity = results["validity"]
    print(f"   Total molecules generated: {validity['num_molecules_generated']}")
    print(
        f"   Valid molecules: {validity['valid_fraction']:.3f} ({validity['valid_fraction'] * 100:.1f}%)"
    )
    print(
        f"   Unique molecules: {validity['unique_fraction']:.3f} ({validity['unique_fraction'] * 100:.1f}%)"
    )
    print(
        f"   Valid & unique: {validity['valid_and_unique_fraction']:.3f} ({validity['valid_and_unique_fraction'] * 100:.1f}%)"
    )
    print(
        f"   Novel molecules: {validity['valid_and_unique_and_novel_fraction']:.3f} ({validity['valid_and_unique_and_novel_fraction'] * 100:.1f}%)"
    )

    # Moses metrics
    print("\n📈 Moses Metrics:")
    moses = results["moses"]
    print(
        f"   Passing Moses filters: {moses['fraction_passing_moses_filters']:.3f} ({moses['fraction_passing_moses_filters'] * 100:.1f}%)"
    )
    print(f"   SNN score: {moses['snn_score']:.3f}")
    print(f"   Internal diversity (p=1): {moses['IntDiv']:.3f}")
    print(f"   Internal diversity (p=2): {moses['IntDiv2']:.3f}")
    print(f"   Scaffold similarity: {moses['scaffolds_similarity']:.3f}")
    print(f"   Fragment similarity: {moses['fragment_similarity']:.3f}")

    # Distribution metrics
    print("\n📏 Distribution Metrics:")
    print(f"   KL divergence score: {results['kl_score']:.3f}")

    # FCD metrics
    print("\n🎯 FCD Metrics:")
    fcd = results["fcd"]
    print(f"   FCD score: {fcd['fcd']:.3f}")
    print(f"   FCD (valid only): {fcd['fcd_valid']:.3f}")
    print(f"   FCD normalized: {fcd['fcd_normalized']:.3f}")
    print(f"   FCD (valid) normalized: {fcd['fcd_valid_normalized']:.3f}")

    # Save results
    print("\n💾 Saving results to 'demo_results.json'...")
    with open("demo_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Demo completed successfully!")
    print("\nTo run this demo with your own model:")
    print("1. Implement the MoleculeGenerationModel protocol")
    print("2. Replace DummyMoleculeGenerationModel with your model")
    print("3. Adjust num_samples_to_generate as needed")
    print("4. Run the benchmark and analyze results")


if __name__ == "__main__":
    main()
