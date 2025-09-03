"""Create a mapping from structure and chain ID to MSA indices."""

import argparse
import multiprocessing
from pathlib import Path

import gemmi
from tqdm import tqdm


def extract_seqs(pdb_file: str) -> None:
    """Extract sequences from a PDB file."""
    pdb_file: Path = Path(pdb_file)
    pdb_id = pdb_file.stem.split(".")[0].lower()
    try:
        structure = gemmi.read_structure(str(pdb_file))
    except RuntimeError:
        print(f"Failed to read {pdb_file}")
        return [], [], [], []
    structure.merge_chain_parts()
    structure.remove_waters()
    structure.remove_hydrogens()
    structure.remove_empty_chains()

    prots, rnas, dnas, ligands = [], [], [], []
    for entity_id, entity in enumerate(structure.entities):
        entity: gemmi.Entity
        if entity.entity_type == gemmi.EntityType.Polymer and (
            entity.polymer_type.name in {"PeptideL", "Rna", "Dna"}
        ):
            # Fetch the sequence
            seq = entity.full_sequence
            seq = [gemmi.Entity.first_mon(item) for item in seq]
            seq = gemmi.one_letter_code(seq)
            subchains = ",".join(entity.subchains)

            # Store the sequence to the appropriate list
            if entity.polymer_type.name == "PeptideL":
                prots.append((pdb_id, entity_id, entity.name, subchains, seq))
            elif entity.polymer_type.name == "Rna":
                rnas.append((pdb_id, entity_id, entity.name, subchains, seq))
            elif entity.polymer_type.name == "Dna":
                dnas.append((pdb_id, entity_id, entity.name, subchains, seq))
        elif entity.entity_type in (
            gemmi.EntityType.NonPolymer,
            gemmi.EntityType.Branched,
        ):
            # Fetch the residues from the first subchain, if any
            if not entity.subchains:
                continue
            subchain_id = entity.subchains[0]
            subchain = next(
                c for c in structure[0].subchains() if c.subchain_id() == subchain_id
            )
            # Create a fake sequence by concatenating the residue names
            seq = "_".join([res.name for res in subchain])
            subchains = ",".join(entity.subchains)
            ligands.append((pdb_id, entity_id, entity.name, subchains, seq))

    return prots, rnas, dnas, ligands


def main(pdb_dir: Path, outdir: Path, num_processes: int, subfolders: bool = True) -> None:
    """Create mapping."""
    # Get all PDB files
    print("Looking for PDB files...")
    if subfolders:
        folders = [item for item in pdb_dir.iterdir() if item.is_dir()]
    else:
        folders = [pdb_dir]
    files = [str(item) for f in folders for item in f.glob("*.cif.gz")]

    print("len(files):", len(files))

    # Extract sequences
    all_prots, all_rnas, all_dnas, all_ligands = [], [], [], []
    num_processes = min(num_processes, multiprocessing.cpu_count())

    if num_processes == 1:
        for pdb_file in tqdm(files):
            prots, rnas, dnas, ligands = extract_seqs(pdb_file)
            all_prots.extend(prots)
            all_rnas.extend(rnas)
            all_dnas.extend(dnas)
            all_ligands.extend(ligands)
    else:
        with multiprocessing.Pool(num_processes) as pool:  # noqa: SIM117
            with tqdm(total=len(files)) as pbar:
                for prots, rnas, dnas, ligands in pool.imap_unordered(
                    extract_seqs, files
                ):
                    all_prots.extend(prots)
                    all_rnas.extend(rnas)
                    all_dnas.extend(dnas)
                    all_ligands.extend(ligands)
                    pbar.update()

    # Write sequences to fasta files
    outdir.mkdir(parents=True, exist_ok=True)

    # Create header format
    header = ">PDB={}_EntityID={}_EntityName={}_Subchains={}\n"

    with (outdir / "proteins.fasta").open("w") as f:
        for pdb_id, ent_id, ent_name, subchains, seq in all_prots:
            f.write(header.format(pdb_id, ent_id, ent_name, subchains))
            f.write(f"{seq}\n")

    with (outdir / "rnas.fasta").open("w") as f:
        for pdb_id, ent_id, ent_name, subchains, seq in all_rnas:
            f.write(header.format(pdb_id, ent_id, ent_name, subchains))
            f.write(f"{seq}\n")

    with (outdir / "dnas.fasta").open("w") as f:
        for pdb_id, ent_id, ent_name, subchains, seq in all_dnas:
            f.write(header.format(pdb_id, ent_id, ent_name, subchains))
            f.write(f"{seq}\n")

    with (outdir / "ligands.fasta").open("w") as f:
        for pdb_id, ent_id, ent_name, subchains, seq in all_ligands:
            f.write(header.format(pdb_id, ent_id, ent_name, subchains))
            f.write(f"{seq}\n")



