from molecule_benchmarks.benchmarker import Benchmarker
from molecule_benchmarks.dataset import SmilesDataset
from molecule_benchmarks.model import (
    DummyMoleculeGenerationModel,
    MoleculeGenerationModel,
)

__version__ = "0.1.12"
__all__ = [
    "Benchmarker",
    "SmilesDataset",
    "MoleculeGenerationModel",
    "DummyMoleculeGenerationModel",
]


def main() -> None:
    """Main entry point for the molecule-benchmarks CLI."""
    import sys

    print("🧪 Molecule Benchmarks v0.1.9")
    print("=" * 40)
    print("A comprehensive benchmark suite for molecular generation models")
    print()
    print("To get started:")
    print("1. Run the demo: python demo.py")
    print("2. Read the documentation: https://github.com/peteole/molecule-benchmarks")
    print("3. Implement your model using the MoleculeGenerationModel protocol")
    print()
    print("Example usage:")
    print("  from molecule_benchmarks import Benchmarker, SmilesDataset")
    print("  dataset = SmilesDataset.load_qm9_dataset()")
    print("  benchmarker = Benchmarker(dataset)")
    print("  results = benchmarker.benchmark(your_model)")
    print()

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("Running demo...")
        try:
            exec(open("demo.py").read())
        except FileNotFoundError:
            print("Demo file not found. Please run from the project root directory.")
    else:
        print("Use --demo flag to run the demonstration.")
