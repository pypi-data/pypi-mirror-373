from collections import Counter
from functools import partial
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import torch
from rdkit import Chem
from rdkit.Chem import AllChem, MACCSkeys
from rdkit.Chem.AllChem import GetMorganFingerprintAsBitVect as Morgan
from rdkit.Chem.Scaffolds import MurckoScaffold
from scipy.spatial.distance import cosine as cos_distance

from molecule_benchmarks.utils import get_mol, mapper


def average_agg_tanimoto(
    stock_vecs, gen_vecs, batch_size=5000, agg="max", device="cpu", p=1
):
    """
    For each molecule in gen_vecs finds closest molecule in stock_vecs.
    Returns average tanimoto score for between these molecules

    Parameters:
        stock_vecs: numpy array <n_vectors x dim>
        gen_vecs: numpy array <n_vectors' x dim>
        agg: max or mean
        p: power for averaging: (mean x^p)^(1/p)
    """
    assert agg in ["max", "mean"], "Can aggregate only max or mean"
    agg_tanimoto = np.zeros(len(gen_vecs))
    total = np.zeros(len(gen_vecs))
    for j in range(0, stock_vecs.shape[0], batch_size):
        x_stock = torch.tensor(stock_vecs[j : j + batch_size]).to(device).float()
        for i in range(0, gen_vecs.shape[0], batch_size):
            y_gen = torch.tensor(gen_vecs[i : i + batch_size]).to(device).float()
            y_gen = y_gen.transpose(0, 1)
            tp = torch.mm(x_stock, y_gen)
            jac = (
                (tp / (x_stock.sum(1, keepdim=True) + y_gen.sum(0, keepdim=True) - tp))
                .cpu()
                .numpy()
            )
            jac[np.isnan(jac)] = 1
            if p != 1:
                jac = jac**p
            if agg == "max":
                agg_tanimoto[i : i + y_gen.shape[1]] = np.maximum(
                    agg_tanimoto[i : i + y_gen.shape[1]], jac.max(0)
                )
            elif agg == "mean":
                agg_tanimoto[i : i + y_gen.shape[1]] += jac.sum(0)
                total[i : i + y_gen.shape[1]] += jac.shape[0]
    if agg == "mean":
        agg_tanimoto /= total
    if p != 1:
        agg_tanimoto = (agg_tanimoto) ** (1 / p)
    return np.mean(agg_tanimoto)


def fingerprints(smiles_mols_array, n_jobs=None, already_unique=False, *args, **kwargs):
    """
    Computes fingerprints of smiles np.array/list/pd.Series with n_jobs workers.
    Example::

        fingerprints(smiles_mols_array, type='morgan', n_jobs=10)

    Inserts np.NaN to rows corresponding to incorrect smiles.
    IMPORTANT: if there is at least one np.NaN, the dtype would be float.

    Parameters
    ----------
    smiles_mols_array : list, array, or pd.Series
        List/array/Series of SMILES or already computed RDKit molecules.
    n_jobs : int, optional
        Number of parallel workers to execute.
    already_unique : bool, optional
        Flag for performance reasons, if smiles array is big and already unique. Its value is set to True if smiles_mols_array contains RDKit molecules already.
    """
    if isinstance(smiles_mols_array, pd.Series):
        smiles_mols_array = smiles_mols_array.values
    else:
        smiles_mols_array = np.asarray(smiles_mols_array)
    if not isinstance(smiles_mols_array[0], str):
        already_unique = True

    if not already_unique:
        smiles_mols_array, inv_index = np.unique(smiles_mols_array, return_inverse=True)

    fps = mapper(n_jobs, job_name="Computing Fingerprints")(
        partial(fingerprint, *args, **kwargs), smiles_mols_array
    )

    length = 1
    first_fp = None
    for fp in fps:
        if fp is not None:
            length = fp.shape[-1]
            first_fp = fp
            break
    if first_fp is None:
        return np.array([[]])
    fps = [
        fp if fp is not None else np.array([np.nan]).repeat(length)[None, :]
        for fp in fps
    ]
    if scipy.sparse.issparse(first_fp):
        fps = scipy.sparse.vstack(fps).tocsr()
    else:
        fps = np.vstack(fps)
    if not already_unique:
        return fps[inv_index]
    return fps


def fingerprint(
    smiles_or_mol,
    fp_type="maccs",
    dtype=None,
    morgan__r=2,
    morgan__n=1024,
    *args,
    **kwargs,
):
    """
    Generates fingerprint for SMILES
    If smiles is invalid, returns None
    Returns numpy array of fingerprint bits

    Parameters:
        smiles: SMILES string
        type: type of fingerprint: [MACCS|morgan]
        dtype: if not None, specifies the dtype of returned array
    """
    fp_type = fp_type.lower()
    molecule = get_mol(smiles_or_mol, *args, **kwargs)
    if molecule is None:
        return None
    if fp_type == "maccs":
        keys = MACCSkeys.GenMACCSKeys(molecule)
        keys = np.array(keys.GetOnBits())
        fingerprint = np.zeros(166, dtype="uint8")
        if len(keys) != 0:
            fingerprint[keys - 1] = 1  # We drop 0-th key that is always zero
    elif fp_type == "morgan":
        fingerprint = np.asarray(
            Morgan(molecule, morgan__r, nBits=morgan__n), dtype="uint8"
        )
    else:
        raise ValueError("Unknown fingerprint type {}".format(fp_type))
    if dtype is not None:
        fingerprint = fingerprint.astype(dtype)
    return fingerprint


def fraction_passes_filters(gen, n_jobs: int | None = None):
    """
    Computes the fraction of molecules that pass filters:
    * MCF
    * PAINS
    * Only allowed atoms ('C','N','S','O','F','Cl','Br','H')
    * No charges
    """
    passes = mapper(n_jobs, job_name="Filtering Molecules")(mol_passes_filters, gen)
    return np.mean(passes)


def get_filters():
    _base_dir = Path(__file__).parent
    _mcf = pd.read_csv(_base_dir / "resources" / "mcf.csv")
    _pains = pd.read_csv(_base_dir / "resources" / "wehi_pains.csv")
    _filters = [
        Chem.MolFromSmarts(x)
        for x in pd.concat([_mcf, _pains], sort=True)["smarts"].values
    ]
    return _filters


_filters = get_filters()


def mol_passes_filters(mol: Chem.Mol | str | None, allowed=None, isomericSmiles=False):
    """
    Checks if mol
    * passes MCF and PAINS filters,
    * has only allowed atoms
    * is not charged
    """
    allowed = allowed or {"C", "N", "S", "O", "F", "Cl", "Br", "H"}
    mol = get_mol(mol)
    if mol is None:
        return False
    ring_info = mol.GetRingInfo()
    if ring_info.NumRings() != 0 and any(len(x) >= 8 for x in ring_info.AtomRings()):
        return False
    h_mol = Chem.AddHs(mol)
    if any(atom.GetFormalCharge() != 0 for atom in mol.GetAtoms()):
        return False
    if any(atom.GetSymbol() not in allowed for atom in mol.GetAtoms()):
        return False
    if any(h_mol.HasSubstructMatch(smarts) for smarts in _filters):
        return False
    smiles = Chem.MolToSmiles(mol, isomericSmiles=isomericSmiles)
    if smiles is None or len(smiles) == 0:
        return False
    if Chem.MolFromSmiles(smiles) is None:
        return False
    return True


def internal_diversity(
    gen: list[str], n_jobs=1, device="cpu", fp_type="morgan", gen_fps=None, p=1
):
    """
    Computes internal diversity as:

    .. code-block::

        1/|A|^2 sum_{x, y in AxA} (1-tanimoto(x, y))

    Returns a value in [0, 1].
    """
    if len(gen) == 0:
        return -1

    if gen_fps is None:
        gen_fps = fingerprints(gen, fp_type=fp_type, n_jobs=n_jobs)
    return (
        1
        - (
            average_agg_tanimoto(gen_fps, gen_fps, agg="mean", device=device, p=p)
        ).mean()
    )


def compute_scaffolds(mol_list, n_jobs: int | None = None, min_rings=2):
    """
    Extracts a scafold from a molecule in a form of a canonic SMILES
    """
    scaffolds = Counter()
    map_ = mapper(job_name="Computing Scaffolds")
    mol_list = [mol for mol in mol_list if mol is not None]  # Filter out None values
    scaffolds = Counter(map_(partial(compute_scaffold, min_rings=min_rings), mol_list))
    if None in scaffolds:
        scaffolds.pop(None)
    return scaffolds


def get_n_rings(mol: Chem.Mol) -> int:
    """
    Computes the number of rings in a molecule
    """
    return mol.GetRingInfo().NumRings()


def compute_scaffold(mol, min_rings=2):
    if mol is None:
        return None
    try:
        mol = get_mol(mol)
        if mol is None:
            return None
        scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    except (ValueError, RuntimeError):
        return None
    n_rings = get_n_rings(scaffold)
    scaffold_smiles = Chem.MolToSmiles(scaffold)
    if scaffold_smiles == "" or n_rings < min_rings:
        return None
    return scaffold_smiles


def cos_similarity(ref_counts, gen_counts):
    """
    Computes cosine similarity between
     dictionaries of form {name: count}. Non-present
     elements are considered zero:

     sim = <r, g> / ||r|| / ||g||
    """
    if len(ref_counts) == 0 or len(gen_counts) == 0:
        return np.nan
    keys = np.unique(list(ref_counts.keys()) + list(gen_counts.keys()))
    ref_vec = np.array([ref_counts.get(k, 0) for k in keys])
    gen_vec = np.array([gen_counts.get(k, 0) for k in keys])
    try:
        return 1 - cos_distance(ref_vec, gen_vec)
    except Exception as e:
        print(f"Error computing cosine similarity: {e}")
        return np.nan


def fragmenter(mol) -> list[str]:
    """
    fragment mol using BRICS and return smiles list
    """
    mol = get_mol(mol)
    if mol is None:
        return []
    fgs = AllChem.FragmentOnBRICSBonds(mol)
    fgs_smi = Chem.MolToSmiles(fgs).split(".")
    return fgs_smi


def compute_fragments(mol_list, n_jobs: int | None = None):
    """
    fragment list of mols using BRICS and return smiles list
    """
    fragments: Counter[str] = Counter()
    for mol_frag in mapper(n_jobs, "Computing fragments")(fragmenter, mol_list):
        fragments.update(mol_frag)
    return fragments
