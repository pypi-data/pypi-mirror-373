"""
Molecule generation model interface.

This module defines the protocol that molecular generation models must implement
to be compatible with the benchmark suite.
"""

from abc import abstractmethod
from typing import Protocol

from tqdm import tqdm


class MoleculeGenerationModel(Protocol):
    """Protocol for molecular generation models.

    Any model that implements this protocol can be benchmarked using the
    molecule_benchmarks suite. The model only needs to implement the
    generate_molecule_batch method.

    Example:
        >>> class MyModel(MoleculeGenerationModel):
        ...     def generate_molecule_batch(self) -> list[str | None]:
        ...         # Your generation logic here
        ...         return ["CCO", "CC(=O)O", None]  # None for invalid molecules
        ...
        >>> model = MyModel()
        >>> molecules = model.generate_molecules(100)
    """

    @abstractmethod
    def generate_molecule_batch(self) -> list[str | None]:
        """Generate a batch of molecules.

        This method will be called repeatedly until the desired number of
        molecules is generated. The batch size can be decided by the
        implementation and may vary between calls.

        Returns:
            A list of SMILES strings representing the generated molecules.
            If a sample cannot be converted to SMILES or is invalid,
            it should return None for that sample.

        Note:
            - Return None for invalid molecules rather than invalid SMILES strings
            - The batch size is flexible and can be optimized for your model
            - This method will be called multiple times to generate the required number of molecules
        """
        pass

    def generate_molecules(self, num_molecules: int) -> list[str | None]:
        """Generate a specified number of molecules.

        This method repeatedly calls generate_molecule_batch() until enough
        molecules are generated. You typically don't need to override this method.

        Args:
            num_molecules: The number of molecules to generate.

        Returns:
            A list of SMILES strings representing the generated molecules.
            If a sample cannot be converted to SMILES, it returns None for that sample.
            The list will contain exactly `num_molecules` elements.
        """
        smiles_list: list[str | None] = []
        with tqdm(total=num_molecules, desc="Generating molecules") as pbar:
            while len(smiles_list) < num_molecules:
                batch = self.generate_molecule_batch()
                smiles_list.extend(batch)
                if len(smiles_list) > num_molecules:
                    smiles_list = smiles_list[:num_molecules]
                pbar.update(
                    min(len(batch), num_molecules - len(smiles_list) + len(batch))
                )
        return smiles_list


class DummyMoleculeGenerationModel(MoleculeGenerationModel):
    """A dummy model that generates a fixed set of SMILES strings for testing.

    This model is useful for testing the benchmark suite and as an example
    of how to implement the MoleculeGenerationModel protocol.

    Example:
        >>> model = DummyMoleculeGenerationModel(["CCO", "CC(=O)O"])
        >>> molecules = model.generate_molecules(10)
        >>> len(molecules)
        10
    """

    def __init__(self, mols: list[str | None] | None = None):
        """Initialize the dummy model with a predefined list of SMILES strings.

        Args:
            mols: A list of SMILES strings to use for generation. If None,
                  uses a default set of common molecules.
        """
        if mols is None:
            mols = [
                "C1=CC=CC=C1",  # Benzene
                "C1=CC=CN=C1",  # Pyridine
                "C1=CC=CO=C1",  # Furan
                "CCO",  # Ethanol
                "CC(=O)O",  # Acetic acid
                None,  # Invalid SMILES placeholder
            ]
        self.mols = mols

    def generate_molecule_batch(self) -> list[str | None]:
        """Generate a batch containing all predefined molecules.

        Returns:
            The complete list of predefined molecules.
        """
        return self.mols.copy()
