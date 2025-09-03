"""

Compute conformers for the whole CCD.

Requires downloading the components.cif file from
the PDB archive. Conformers are computed for all
molecules, and saved as a pickle dictionary from
molecule code (i.e name) to RDKit molecule.

"""

import argparse
import multiprocessing
import pickle
from functools import partial
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from tqdm import tqdm

import numpy as np
import pandas as pd
import rdkit
from pdbeccdutils.core import ccd_reader
from pdbeccdutils.core.component import ConformerType
from rdkit import Chem
from rdkit import RDLogger
from rdkit.Chem.rdchem import Conformer, Mol
from rdkit.Chem import AllChem
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.AllChem import MolSanitizeException

RDLogger.DisableLog("rdApp.*")


LARGEST_FRAGMENT_CHOOSER = rdMolStandardize.LargestFragmentChooser()


def standardize(smiles: str) -> Optional[str]:
    """Standardize a molecule and return its SMILES and a flag indicating whether the molecule is valid.
    This version has exception handling, which the original in mol-finder/data doesn't have. I didn't change the mol-finder/data
    since there are a lot of other functions that depend on it and I didn't want to break them.
    """
    mol = Chem.MolFromSmiles(smiles, sanitize=False)

    exclude = exclude_flag(mol, includeRDKitSanitization=False)

    if exclude:
        raise ValueError("Molecule is excluded")

    # Standardize with ChEMBL data curation pipeline. During standardization, the molecule may be broken
    # Choose molecule with largest component
    mol = LARGEST_FRAGMENT_CHOOSER.choose(mol)
    # Standardize with ChEMBL data curation pipeline. During standardization, the molecule may be broken
    mol = standardize_mol(mol)
    smiles = Chem.MolToSmiles(mol)

    # Check if molecule can be parsed by RDKit (in rare cases, the molecule may be broken during standardization)
    if Chem.MolFromSmiles(smiles) is None:
        raise ValueError("Molecule is broken")

    return smiles


def mol_from_smile(
    smiles: Dict[str, Mol], chembl_standardize: bool = False
) -> List[Mol]:
    """Load the smiles.

    Parameters
    ----------
    smiles : Dict[str, Mol]
        Dict of smiles.
    Returns
    -------
    List[Mol]

    """
    mols_processed = []
    failed = 0
    for cid, smile in tqdm(smiles.items()):
        try:
            if chembl_standardize:
                smile = standardize(smile)
            mol = AllChem.MolFromSmiles(smile)
            mol = AllChem.AddHs(mol)
            mol.SetProp("cid", str(int(cid)))
            canonical_order = Chem.CanonicalRankAtoms(mol)
            for atom, can_idx in zip(mol.GetAtoms(), canonical_order):
                atom.SetProp("name", atom.GetSymbol().upper() + str(can_idx + 1))
            mols_processed.append((mol, smile))
        except:
            failed += 1
            pass
    print(f"Failed to process {failed} molecules.")
    return mols_processed


def compute_3d(mol: Mol, version: str = "v3") -> bool:
    """Generate 3D coordinates using EKTDG method.

    Taken from `pdbeccdutils.core.component.Component`.

    Parameters
    ----------
    mol: Mol
        The RDKit molecule to process
    version: str, optional
        The ETKDG version, defaults ot v3

    Returns
    -------
    bool
        Whether computation was successful.

    """
    if version == "v3":
        options = rdkit.Chem.AllChem.ETKDGv3()
    elif version == "v2":
        options = rdkit.Chem.AllChem.ETKDGv2()
    else:
        options = rdkit.Chem.AllChem.ETKDGv2()

    options.clearConfs = False
    conf_id = -1

    try:
        conf_id = rdkit.Chem.AllChem.EmbedMolecule(mol, options)
        rdkit.Chem.AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=1000)

    except RuntimeError:
        pass  # Force field issue here
    except ValueError:
        pass  # sanitization issue here

    if conf_id != -1:
        conformer = mol.GetConformer(conf_id)
        conformer.SetProp("name", ConformerType.Computed.name)
        conformer.SetProp("coord_generation", f"ETKDG{version}")

        return True

    return False


def get_conformer(mol: Mol, c_type: ConformerType) -> Conformer:
    """Retrieve an rdkit object for a deemed conformer.

    Taken from `pdbeccdutils.core.component.Component`.

    Parameters
    ----------
    mol: Mol
        The molecule to process.
    c_type: ConformerType
        The conformer type to extract.

    Returns
    -------
    Conformer
        The desired conformer, if any.

    Raises
    ------
    ValueError
        If there are no conformers of the given tyoe.

    """
    for c in mol.GetConformers():
        try:
            if c.GetProp("name") == c_type.name:
                return c
        except KeyError:  # noqa: PERF203
            pass

    msg = f"Conformer {c_type.name} does not exist."
    raise ValueError(msg)


def process(mol: Tuple[Mol, str], output: str) -> Tuple[str, str]:
    """Process a molecule.

    Parameters
    ----------
    mol : Tuple[Mol, str]
        The molecule and smile to process
    output : str
        The directory to save the molecules

    Returns
    -------
    str
        The name of the molecule
    str
        The result of the conformer generation

    """
    # Parse the input
    mol, smile = mol

    # Get name
    name = mol.GetProp("cid")

    # Check if single atom
    if mol.GetNumAtoms() == 1:
        result = "single"
    else:
        # Get the 3D conformer
        try:
            # Try to generate a 3D conformer with RDKit
            success = compute_3d(mol, version="v3")
            if success:
                _ = get_conformer(mol, ConformerType.Computed)
                result = "computed"

            # Otherwise, default to the ideal coordinates
            else:
                _ = get_conformer(mol, ConformerType.Ideal)
                result = "ideal"
        except ValueError:
            result = "failed"

    # Remove non essential Hs
    mol = AllChem.RemoveHs(mol, sanitize=False)

    # Dump the molecule
    path = Path(output) / f"{name}.pkl"
    with path.open("wb") as f:
        pickle.dump(mol, f)

    # Output the results
    return name, smile, result


def main(args: argparse.Namespace) -> None:
    """Process conformers."""
    # Set property saving
    rdkit.Chem.SetDefaultPickleProperties(rdkit.Chem.PropertyPickleOptions.AllProps)
    RDLogger.DisableLog("rdApp.*")

    # Load the smiles
    with open(args.smiles, "rb") as f:
        smiles = pickle.load(f)

    # Create the molecules
    molecules = mol_from_smile(smiles, args.chembl_standardize)

    # shuffle molecules
    np.random.shuffle(molecules)

    # Setup processing function
    output = Path(args.output)
    mol_output = output / "mols"
    process_fn = partial(process, output=str(mol_output))

    # Process the files in parallel
    metadata = []
    num_processes = multiprocessing.cpu_count() // 2

    with (
        multiprocessing.Pool(processes=num_processes) as pool,
        tqdm(total=len(molecules)) as pbar,
    ):
        for name, smile, result in pool.imap_unordered(process_fn, molecules):
            metadata.append({"name": name, "smile": smile, "result": result})
            pbar.update()

    # Load and group outputs
    molecules = {}
    for item in tqdm(metadata, total=len(metadata)):
        if item["result"] == "failed":
            continue

        # Load the mol file
        path = mol_output / f"{item['name']}.pkl"
        with path.open("rb") as f:
            mol = pickle.load(f)  # noqa: S301
            molecules[item["name"]] = mol

    # Dump metadata
    path = output / "results.csv"
    metadata = pd.DataFrame.from_dict(metadata)
    metadata.to_csv(path)

    # Dump the molecules
    path = output / "conformers.pkl"
    with path.open("wb") as f:
        pickle.dump(molecules, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smiles",
        type=str,
        default="data/affinity/level_3_4_smiles.pkl",
    )
    parser.add_argument("--output", type=str, default="data/affinity/conformers")
    parser.add_argument("--chembl_standardize", action="store_true", default=False)

    args = parser.parse_args()
    main(args)
