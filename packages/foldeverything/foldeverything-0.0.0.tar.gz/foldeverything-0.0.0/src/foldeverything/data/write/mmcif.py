import re
import string
from foldeverything.data import const
from foldeverything.data.data import Structure, elem_from_name
import gemmi


def to_mmcif(
    structure: Structure, write_fake_atoms: bool = False, poly_seq_scheme: bool = True
) -> str:
    """
    Convert a `Structure` object into an mmCIF-formatted string using Gemmi.

    Args:
        structure (Structure): Boltz Structure object.
        write_fake_atoms (bool): If True, includes fake atoms
        poly_seq_scheme (bool): If True, writes polymer sequence information into the
            `_pdbx_poly_seq_scheme` table.

    Returns:
        str: A string representation of the structure in mmCIF format.
    """

    gemmi_struct = gemmi.Structure()
    gemmi_struct.name = "model"
    model = gemmi.Model("1")

    chain_to_entity_id = {}
    sequence_to_entity_id = {}
    entity_counter = 1
    chain_names = [re.sub(r"\d+", "", c["name"]) for c in structure.chains]
    chain_id_pool = list(reversed(string.ascii_uppercase)) + list(
        reversed(string.digits)
    )
    used_names = []
    old_to_new_chainid = {}
    for chain in structure.chains:
        old_chainid = chain["name"].item()

        new_chainid = re.sub(r"\d+", "", old_chainid)
        if new_chainid in used_names:
            # Find next unused chain ID from the pool
            for candidate in chain_id_pool:
                if candidate not in chain_names and candidate not in used_names:
                    new_chainid = candidate
                    break
        old_to_new_chainid[old_chainid] = new_chainid
        used_names.append(new_chainid)

        residues = structure.residues[
            chain["res_idx"] : chain["res_idx"] + chain["res_num"]
        ]

        sequence = "".join([res["name"].item() for res in residues])
        chain_type = chain["mol_type"].item()
        if sequence not in sequence_to_entity_id:
            sequence_to_entity_id[sequence] = str(entity_counter)

            entity = gemmi.Entity(str(entity_counter))

            if chain_type == const.chain_type_ids["NONPOLYMER"]:
                entity.entity_type = gemmi.EntityType.NonPolymer
            else:
                entity.entity_type = gemmi.EntityType.Polymer
                if chain_type == const.chain_type_ids["DNA"]:
                    entity.polymer_type = gemmi.PolymerType.Dna
                elif chain_type == const.chain_type_ids["RNA"]:
                    entity.polymer_type = gemmi.PolymerType.Rna
                elif chain_type == const.chain_type_ids["PROTEIN"]:
                    entity.polymer_type = gemmi.PolymerType.PeptideL

                # Seqres that also contains residues with missing coordinates
                entity.full_sequence = [res["name"].item() for res in residues]

            gemmi_struct.entities.append(entity)
            entity_counter += 1

        chain_to_entity_id[new_chainid] = sequence_to_entity_id[sequence]

    for chain in structure.chains:
        old_chainid = chain["name"].item()
        chain_id = old_to_new_chainid[old_chainid]

        gemmi_chain = gemmi.Chain(chain_id)

        residues = structure.residues[
            chain["res_idx"] : chain["res_idx"] + chain["res_num"]
        ]

        for res in residues:
            # Missing residues are in the seqres but not in the residue table
            if not res["is_present"]:
                continue

            res_name = res["name"].item()
            seqid = gemmi.SeqId(res["res_idx"].item() + 1, " ")

            gemmi_res = gemmi.Residue()
            gemmi_res.name = res_name
            gemmi_res.seqid = seqid
            gemmi_res.label_seq = res["res_idx"].item() + 1
            gemmi_res.subchain = chain_id

            if chain_id in chain_to_entity_id:
                gemmi_res.entity_id = chain_to_entity_id[chain_id]

            atoms = structure.atoms[res["atom_idx"] : res["atom_idx"] + res["atom_num"]]
            coords = structure.coords["coords"][
                res["atom_idx"] : res["atom_idx"] + res["atom_num"]
            ]

            for atom, coord in zip(atoms, coords):
                # Skip missing atoms
                if not atom["is_present"]:
                    continue

                atom_name = atom["name"].item()
                element = elem_from_name(atom_name, res_name)

                # Skip fake atoms
                if not write_fake_atoms and (
                    const.fake_element.upper() in atom_name
                    or const.mask_element.upper() in atom_name
                ):
                    assert (
                        element == const.fake_element or element == const.mask_element
                    ), "Atom name not consistent with element for possible fake atom."
                    continue
                pos = gemmi.Position(coord[0], coord[1], coord[2])
                gemmi_atom = gemmi.Atom()
                gemmi_atom.name = atom_name
                gemmi_atom.pos = pos
                gemmi_atom.occ = 1.0
                gemmi_atom.b_iso = atom["bfactor"].item()
                gemmi_atom.element = gemmi.Element(element)
                gemmi_res.add_atom(gemmi_atom)
            gemmi_chain.add_residue(gemmi_res)
        model.add_chain(gemmi_chain)

    # Add covalent,Disulfide bonds to struct_conn
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

            p1_chain_id = old_to_new_chainid[chain1["name"].item()]
            p2_chain_id = old_to_new_chainid[chain2["name"].item()]
            p1_seq_id = res1["res_idx"].item() + 1
            p2_seq_id = res2["res_idx"].item() + 1

            p1_atom_name = atom1["name"].item()
            p2_atom_name = atom2["name"].item()

            con = gemmi.Connection()
            if p1_atom_name == "SG" and p2_atom_name == "SG":
                disulf_count += 1
                con.type = gemmi.ConnectionType.Disulf
                con.name = f"disulf{disulf_count}"
            else:
                cov_count += 1
                con.type = gemmi.ConnectionType.Covale
                con.name = f"covale{cov_count}"

            con.partner1 = gemmi.AtomAddress(
                p1_chain_id,
                gemmi.SeqId(str(p1_seq_id)),
                res1["name"].item(),
                p1_atom_name,
            )
            con.partner2 = gemmi.AtomAddress(
                p2_chain_id,
                gemmi.SeqId(str(p2_seq_id)),
                res2["name"].item(),
                p2_atom_name,
            )

            con.asu = gemmi.Asu.Same
            gemmi_struct.connections.append(con)

    gemmi_struct.add_model(model)
    doc = gemmi_struct.make_mmcif_document()
    block = doc.sole_block()

    struct_asym_loop = block.init_loop("_struct_asym.", ["id", "entity_id"])
    for chain_id, entity_id in sorted(chain_to_entity_id.items()):
        struct_asym_loop.add_row([chain_id, entity_id])

    # Include poly_seq_scheme table
    if poly_seq_scheme:
        add_poly_seq_scheme_cols(structure, block, chain_to_entity_id)

    # remove _chem_comp records because they are empty and then just cause problems with visualization softwares
    block_string = doc.as_string()
    pattern = r"(loop_\n_chem_comp[\s\S]*?)(?=loop_\n)"
    block_string = re.sub(pattern, "", block_string)

    return block_string


def add_boltzgen_metadata(structure, block, old_to_new_chainid):
    cols = [
        "asym_id",  # Chain ID
        "res_idx_in_this_mmcif",  # Reindexed res_idx found in this mmcif file
        "res_idx_physical",  # True res_idx
        "design_mask",  # 1 for designed residues 0 for non-designed residues
    ]
    custom_loop = block.init_loop("_boltzgen_metadata.", cols)

    for chain in structure.chains:
        chain_id = old_to_new_chainid[chain["name"].item()]
        residues = structure.residues[
            chain["res_idx"] : chain["res_idx"] + chain["res_num"]
        ]
        for res_idx, pysical_idx in enumerate(residues, 1):
            seq_id = res_idx + 1
            if not res["is_present"]:
                continue
            mon_id = res["name"].item()
            score = res.get("custom_score", 0.0)  # Example access to your metadata
            custom_loop.add_row(
                [
                    chain_id,
                    str(seq_id),
                    f"{score:.3f}",
                    mon_id,
                ]
            )


def add_poly_seq_scheme_cols(structure, block, chain_to_entity_id):
    poly_seq_scheme_cols = [
        "asym_id",
        "entity_id",
        "seq_id",
        "mon_id",
        "pdb_seq_num",
        "auth_seq_num",
        "pdb_mon_id",
        "auth_mon_id",
        "pdb_strand_id",
        "pdb_ins_code",
        "hetero",
    ]
    poly_seq_loop = block.init_loop("_pdbx_poly_seq_scheme.", poly_seq_scheme_cols)

    for chain in structure.chains:
        if chain["mol_type"].item() == const.chain_type_ids["NONPOLYMER"]:
            continue

        chain_name_str = re.sub(r"\d+", "", chain["name"].item())
        chain_id = chain_name_str
        entity_id = chain_to_entity_id[chain_id]

        residues = structure.residues[
            chain["res_idx"] : chain["res_idx"] + chain["res_num"]
        ]

        # Use enumerate to get the sequential 1-based seq_id
        for seq_id, res in enumerate(residues, 1):
            mon_id = res["name"].item()
            auth_seq_num = str(res["res_idx"].item() + 1)

            # For missing residues, many fields should be '?'
            if res["is_present"]:
                pdb_seq_num = auth_seq_num
                pdb_mon_id = mon_id
                auth_mon_id = mon_id
            else:
                pdb_seq_num = auth_seq_num
                pdb_mon_id = "?"
                auth_mon_id = "?"

            poly_seq_loop.add_row(
                [
                    chain_id,  # asym_id
                    entity_id,  # entity_id
                    str(seq_id),  # seq_id (the 1-based sequential index)
                    mon_id,  # mon_id
                    pdb_seq_num,  # pdb_seq_num (use auth if present)
                    auth_seq_num,  # auth_seq_num (your res_idx)
                    pdb_mon_id,  # pdb_mon_id
                    auth_mon_id,  # auth_mon_id
                    chain_id,  # pdb_strand_id
                    ".",  # pdb_ins_code
                    "n",  # hetero
                ]
            )
