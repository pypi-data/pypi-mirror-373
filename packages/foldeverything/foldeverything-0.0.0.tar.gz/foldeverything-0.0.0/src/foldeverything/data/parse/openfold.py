from pathlib import Path

import gemmi
import numpy as np
from Bio import SeqIO, SeqRecord

from foldeverything.data import const
from foldeverything.data.data import (
    PDB,
    Atom,
    Bond,
    Chain,
    Coords,
    Ensemble,
    Interface,
    Residue,
    Structure,
    convert_atom_name,
)
from foldeverything.data.parse.mmcif import (
    ParsedChain,
    parse_polymer,
)
from foldeverything.task.process.process import Resource


def parse_openfold(data: PDB, resource: Resource) -> Structure:
    """Parse the openfold data and returns a Structure object.

    Parameters
    ----------
        data (PDB): The PDB data to be parsed.
        resource (Resource): The resource object containing the components data.

    Returns
    -------
        Structure: The parsed structure.
    """
    # Set paths
    path = Path(data.path)
    pdb = path / "pdb" / f"{data.id}.pdb"
    msa = path / "a3m" / "uniclust30.a3m"

    # Read first sequence in the MSA
    with msa.open("r") as f:
        entry: SeqRecord = next(SeqIO.parse(f.name, format="fasta"))
        seq = [const.prot_letter_to_token[aa] for aa in str(entry.seq)]

    # Parse pdb structure
    polymer = gemmi.read_structure(str(pdb))
    polymer: ParsedChain = parse_polymer(
        polymer=polymer[0][0].get_polymer(),
        polymer_type=gemmi.PolymerType.PeptideL,
        sequence=seq,
        chain_id="A",
        entity="1",
        components=resource,
    )

    # Convert to table
    atom_data = []
    bond_data = []
    res_data = []
    coords_data = []

    atom_idx = 0
    for res_idx, res in enumerate(polymer.residues):
        res_data.append(
            (
                res.name,
                res.type,
                res_idx,
                atom_idx,
                len(res.atoms),
                atom_idx + res.atom_center,
                atom_idx + res.atom_disto,
                res.is_standard,
                res.is_present,
            )
        )

        for bond in res.bonds:
            chain_1 = 0
            chain_2 = 0
            res_1 = res_idx
            res_2 = res_idx
            atom_1 = atom_idx + bond.atom_1
            atom_2 = atom_idx + bond.atom_2
            bond_data.append(
                (
                    chain_1,
                    chain_2,
                    res_1,
                    res_2,
                    atom_1,
                    atom_2,
                    bond.type,
                )
            )

        for atom in res.atoms:
            atom_data.append(
                (
                    atom.name,
                    atom.coords,
                    atom.is_present,
                    0,
                    atom.bfactor,
                )
            )
            coords_data.append((atom.coords,))
            atom_idx += 1

    ensemble_data = [(0, atom_idx)]

    # Create chain data
    chain_data = [
        (
            "A",
            polymer.type,
            0,
            0,
            0,
            0,
            len(atom_data),
            0,
            len(res_data),
        )
    ]

    # Create structure
    return Structure(
        atoms=np.array(atom_data, dtype=Atom),
        bonds=np.array(bond_data, dtype=Bond),
        residues=np.array(res_data, dtype=Residue),
        chains=np.array(chain_data, dtype=Chain),
        interfaces=np.array([], dtype=Interface),
        mask=np.ones(len(chain_data), dtype=bool),
        ensemble=np.array(ensemble_data, dtype=Ensemble),
        coords=np.array(coords_data, dtype=Coords),
    )
