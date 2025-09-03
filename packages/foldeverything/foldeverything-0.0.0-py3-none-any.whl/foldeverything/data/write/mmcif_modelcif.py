import io
import string
from typing import Iterator, Optional
import re
from typing import Dict, Iterator, List, Union

import ihm
from modelcif import Assembly, AsymUnit, Entity, System, dumper
from modelcif.model import AbInitioModel, Atom, ModelGroup
from torch import Tensor

from foldeverything.data import const
from foldeverything.data.data import Structure, elem_from_name
from foldeverything.data.write.utils import generate_tags


def to_mmcif(
    structure: Structure,
    write_fake_atoms=False,
) -> str:
    """Write a structure into an MMCIF file.

    Parameters
    ----------
    structure : Structure
        The input structure
    plddts: Tensor
        Plddts of size len(structure.atoms)
    ensemble_idx : int

    Returns
    -------
    str
        the output MMCIF file

    """
    system = System()

    # Merge chains with same sequence into the same entity
    sequence_to_entity = {}
    for chain in structure.chains:
        # Get the sequence
        res_start = chain["res_idx"]
        res_end = chain["res_idx"] + chain["res_num"]
        residues = structure.residues[res_start:res_end]
        str_sequence = "".join([str(res["name"]) for res in residues])
        if str_sequence in sequence_to_entity.keys():
            chain["entity_id"] = sequence_to_entity[str_sequence]
        else:
            sequence_to_entity[str_sequence] = chain["entity_id"]

    # Map entities to chain_ids
    entity_to_chains = {}
    entity_to_moltype = {}

    for chain in structure.chains:
        entity_id = chain["entity_id"]
        mol_type = chain["mol_type"]
        entity_to_chains.setdefault(entity_id, []).append(chain)
        entity_to_moltype[entity_id] = mol_type

    # Check same entity id have same number of atoms
    if not all(
        len({chain["atom_num"] for chain in chains}) == 1
        for entity, chains in entity_to_chains.items()
    ):
        print(
            "Warning in to_mmcif(): There are two chains with the same entity_id, but with a different number of atoms."
        )

    # Map entities to sequences
    sequences = {}
    for entity in entity_to_chains:
        # Get the first chain
        chain = entity_to_chains[entity][0]

        # Get the sequence
        res_start = chain["res_idx"]
        res_end = chain["res_idx"] + chain["res_num"]
        residues = structure.residues[res_start:res_end]
        sequence = [str(res["name"]) for res in residues]
        sequences[entity] = sequence

    # Create entity objects
    lig_entity = None
    entities_map = {}
    for entity, sequence in sequences.items():
        mol_type = entity_to_moltype[entity]

        if mol_type == const.chain_type_ids["PROTEIN"]:
            alphabet = ihm.LPeptideAlphabet()

            def chem_comp(x):
                return ihm.LPeptideChemComp(id=x, code=x, code_canonical="X")  # noqa: E731
        elif mol_type == const.chain_type_ids["DNA"]:
            alphabet = ihm.DNAAlphabet()

            def chem_comp(x):
                return ihm.DNAChemComp(id=x, code=x, code_canonical="N")  # noqa: E731
        elif mol_type == const.chain_type_ids["RNA"]:
            alphabet = ihm.RNAAlphabet()

            def chem_comp(x):
                return ihm.RNAChemComp(id=x, code=x, code_canonical="N")  # noqa: E731
        elif len(sequence) > 1:
            alphabet = {}

            def chem_comp(x):
                return ihm.SaccharideChemComp(id=x)  # noqa: E731
        else:
            alphabet = {}

            def chem_comp(x):
                return ihm.NonPolymerChemComp(id=x)  # noqa: E731

        # Handle smiles
        if len(sequence) == 1 and (sequence[0] == "LIG"):
            if lig_entity is None:
                seq = [chem_comp(sequence[0])]
                lig_entity = Entity(seq)
            model_e = lig_entity
        else:
            seq = [
                alphabet[item] if item in alphabet else chem_comp(item)
                for item in sequence
            ]
            model_e = Entity(seq)

        for chain in entity_to_chains[entity]:
            chain_idx = chain["asym_id"]
            entities_map[chain_idx] = model_e

    # We don't assume that symmetry is perfect, so we dump everything
    # into the asymmetric unit, and produce just a single assembly
    chain_names = [re.sub(r"\d+", "", c["name"]) for c in structure.chains]
    chain_id_pool = list(reversed(string.ascii_uppercase)) + list(
        reversed(string.digits)
    )
    used_names = []
    asym_unit_map = {}
    chain_name_map = {}
    for chain in structure.chains:
        # Define the model assembly
        chain_idx = chain["asym_id"]
        chain_tag = re.sub(r"\d+", "", chain["name"].item())
        if chain_tag in used_names:
            # Find next unused chain ID from the pool
            for candidate in chain_id_pool:
                if candidate not in chain_names and candidate not in used_names:
                    chain_tag = candidate
                    break
        chain_name_map[chain["name"].item()] = chain_tag
        used_names.append(chain_tag)
        asym = AsymUnit(
            entities_map[chain_idx],
            details=f"Model subunit {chain_tag}",
            id=chain_tag,
        )
        asym_unit_map[chain_idx] = asym
    modeled_assembly = Assembly(asym_unit_map.values(), name="Modeled assembly")

    class _MyModel(AbInitioModel):
        def __init__(self, assembly, name):
            super().__init__(assembly, name)

        def get_atoms(self) -> Iterator[Atom]:
            # Add all atom sites.
            res_num = 0
            atom_idx = 0
            for chain in structure.chains:
                # We rename the chains in alphabetical order
                het = chain["mol_type"] == const.chain_type_ids["NONPOLYMER"]
                chain_idx = chain["asym_id"]
                res_start = chain["res_idx"]
                res_end = chain["res_idx"] + chain["res_num"]

                residues = structure.residues[res_start:res_end]
                for residue in residues:
                    res_name = residue["name"]
                    atom_start = residue["atom_idx"]
                    atom_end = residue["atom_idx"] + residue["atom_num"]
                    atoms = structure.atoms[atom_start:atom_end]
                    atom_coords = structure.coords[atom_start:atom_end]["coords"]

                    for i, atom in enumerate(atoms):
                        biso = round(atom["bfactor"], 1)
                        atom_idx += 1

                        if not atom["is_present"]:
                            continue

                        # Get element
                        atom_name = str(atom["name"])
                        element = elem_from_name(atom_name, res_name)

                        if not write_fake_atoms and (
                            const.fake_element.upper() in atom_name
                            or const.mask_element.upper() in atom_name
                        ):
                            assert (
                                element == const.fake_element
                                or element == const.mask_element
                            ), (
                                "Atom name not consistent with element for possible fake atom."
                            )
                            continue

                        residue_index = residue["res_idx"] + 1

                        pos = atom_coords[i]
                        yield Atom(
                            asym_unit=asym_unit_map[chain_idx],
                            type_symbol=element,
                            seq_id=residue_index,
                            atom_id=atom_name,
                            x=f"{pos[0]:.5f}",
                            y=f"{pos[1]:.5f}",
                            z=f"{pos[2]:.5f}",
                            het=het,
                            biso=biso,
                            occupancy=1,
                        )
                    res_num += 1

    model = _MyModel(assembly=modeled_assembly, name=f"Model_0")

    model_group = ModelGroup([model], name=f"All models")
    system.model_groups.append(model_group)
    fh = io.StringIO()

    dumper.write(fh, [system])
    cif_string = fh.getvalue()

    # Add covalent bonds to struct_conn
    conn_lines = [
        "loop_",
        "_struct_conn.id",
        "_struct_conn.conn_type_id",
        "_struct_conn.ptnr1_label_asym_id",
        "_struct_conn.ptnr1_label_comp_id",
        "_struct_conn.ptnr1_label_seq_id",
        "_struct_conn.ptnr1_label_atom_id",
        "_struct_conn.pdbx_ptnr1_label_alt_id",
        "_struct_conn.ptnr1_auth_asym_id",
        "_struct_conn.ptnr1_auth_seq_id",
        "_struct_conn.pdbx_ptnr1_PDB_ins_code",
        "_struct_conn.ptnr1_symmetry",
        "_struct_conn.ptnr2_label_asym_id",
        "_struct_conn.ptnr2_label_comp_id",
        "_struct_conn.ptnr2_label_seq_id",
        "_struct_conn.ptnr2_label_atom_id",
        "_struct_conn.pdbx_ptnr2_label_alt_id",
        "_struct_conn.ptnr2_auth_asym_id",
        "_struct_conn.ptnr2_auth_seq_id",
        "_struct_conn.pdbx_ptnr2_PDB_ins_code",
        "_struct_conn.ptnr2_symmetry",
        "_struct_conn.details",
        "_struct_conn.pdbx_dist_value",
    ]
    cov_count = 0
    disulf_count = 0
    for bond in structure.bonds:
        if bond["type"] == const.bond_type_ids["COVALENT"]:
            res1 = structure.residues[bond["res_1"]]
            res2 = structure.residues[bond["res_2"]]
            chain1 = structure.chains[bond["chain_1"]]
            chain2 = structure.chains[bond["chain_2"]]
            atom1 = structure.atoms[bond["atom_1"]]
            atom2 = structure.atoms[bond["atom_2"]]

            p1_chain_id = chain_name_map[chain1["name"].item()]
            p2_chain_id = chain_name_map[chain2["name"].item()]
            p1_seq_id = res1["res_idx"].item() + 1
            p2_seq_id = res2["res_idx"].item() + 1

            p1_atom_name = atom1["name"].item()
            p2_atom_name = atom2["name"].item()

            if p1_atom_name == "SG" and p2_atom_name == "SG":
                disulf_count += 1
                line = f"disulf{disulf_count} "  # "_struct_conn.id",
                line += f"disulf "  # "_struct_conn.conn_type_id",
            else:
                cov_count += 1
                line = f"covale{cov_count} "  # "_struct_conn.id",
                line += f"covale "  # "_struct_conn.conn_type_id",
            line += f"{p1_chain_id} "  # "_struct_conn.ptnr1_label_asym_id",
            # "_struct_conn.ptnr1_label_comp_id",
            line += f"{res1['name'].item()} "
            line += f"{p1_seq_id} "  # "_struct_conn.ptnr1_label_seq_id",
            line += f"{p1_atom_name} "  # "_struct_conn.ptnr1_label_atom_id",
            line += f"? "  # "_struct_conn.pdbx_ptnr1_label_alt_id",
            line += f"{p1_chain_id} "  # "_struct_conn.ptnr1_auth_asym_id",
            line += f"{p1_seq_id} "  # "_struct_conn.ptnr1_auth_seq_id",
            line += f"? "  # "_struct_conn.pdbx_ptnr1_PDB_ins_code",
            line += f"1_555 "  # "_struct_conn.ptnr1_symmetry",
            line += f"{p2_chain_id} "  # "_struct_conn.ptnr2_label_asym_id",
            # "_struct_conn.ptnr2_label_comp_id",
            line += f"{res2['name'].item()} "
            line += f"{p2_seq_id} "  # "_struct_conn.ptnr2_label_seq_id",
            line += f"{p2_atom_name} "  # "_struct_conn.ptnr2_label_atom_id",
            line += f"? "  # "_struct_conn.pdbx_ptnr2_label_alt_id",
            line += f"{p2_chain_id} "  # "_struct_conn.ptnr2_auth_asym_id",
            line += f"{p2_seq_id} "  # "_struct_conn.ptnr2_auth_seq_id",
            line += f"? "  # "_struct_conn.pdbx_ptnr2_PDB_ins_code",
            line += f"1_555 "  # "_struct_conn.ptnr2_symmetry",
            line += f"? "  # "_struct_conn.details",
            line += f"? "  # "_struct_conn.pdbx_dist_value",
            conn_lines.append(line)

    if cov_count > 0:
        cif_string = cif_string + "\n\n" + "\n".join(conn_lines)

    return cif_string
