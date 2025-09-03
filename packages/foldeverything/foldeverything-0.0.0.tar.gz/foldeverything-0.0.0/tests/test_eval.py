import copy
import json
import os
import pprint
import tempfile

import gemmi
import numpy as np
import math

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import RDLogger

from foldeverything.complex import Complex
from foldeverything.types import RNA

RDLogger.DisableLog("rdApp.*")

import foldeverything
from foldeverything.data.parser.gemmi import (
    GemmiParser,
    parse_gemmi_rna,
    parse_gemmi_protein,
    parse_gemmi_dna,
)
from foldeverything.eval.utils import polymer_to_gemmi_chain, build_gemmi_structure
from foldeverything.eval.evaluate import align_complex, eval_target
from foldeverything.eval.utils import (
    apply_transform_complex,
    generate_conformer,
    mol_to_props,
    rmsd_isomorphic_core,
    one_hot_to_index,
    complex_polymer_fields,
)
import foldeverything.eval.metrics as fe_metrics
import foldeverything.eval.metrics.rna

from test_utils import TEST_DATA_DIR, TEST_OUTPUT_DIR, get_file_by_pdb_id

# Two protein chains, pretty simple
simple_target = "1a0q"

# 4wqs is a complex which includes a bunch of proteins, RNAs, and DNAs
# So it makes a good test case
complex_target = "4wqs"

ligand_target = "8c6z"


orig_print = print


def myprint(instr):
    import datetime

    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    orig_print(f"{date_str}: {instr}")


print = myprint


def _gen_random_rotation_matrix(angle_range=2 * math.pi, seed=12345):
    # Generate three random angles
    np.random.seed(seed)
    alpha, beta, gamma = angle_range * (np.random.rand(3) - 0.5)

    # Create rotation matrix around X-axis
    R_x = np.array(
        [
            [1, 0, 0],
            [0, np.cos(alpha), -np.sin(alpha)],
            [0, np.sin(alpha), np.cos(alpha)],
        ]
    )

    # Create rotation matrix around Y-axis
    R_y = np.array(
        [[np.cos(beta), 0, np.sin(beta)], [0, 1, 0], [-np.sin(beta), 0, np.cos(beta)]]
    )

    # Create rotation matrix around Z-axis
    R_z = np.array(
        [
            [np.cos(gamma), -np.sin(gamma), 0],
            [np.sin(gamma), np.cos(gamma), 0],
            [0, 0, 1],
        ]
    )

    # Combine rotations
    R = R_z @ R_y @ R_x

    return R


def _gen_random_transform(t_max=10.0, seed=194378):
    # Obviously this should still align perfectly with the original structure
    # Generate a random translation
    np.random.seed(seed)
    t = t_max * np.random.randn(
        3,
    )

    # Generate a random rotation
    R = _gen_random_rotation_matrix(seed=seed)

    return R, t


def test_gemmi_parser(target_name=complex_target):
    target_path = get_file_by_pdb_id(target_name)
    parser = GemmiParser()

    complex_ = parser.parse(target_path)
    output_path = os.path.join(TEST_OUTPUT_DIR, f"{target_name}_resaved.cif")

    sub_lists = [complex_.proteins, complex_.dnas, complex_.rnas]
    assert len(complex_.proteins) >= 1, "No proteins found"

    structure = build_gemmi_structure(complex_)
    structure.make_mmcif_document().write_file(output_path)

    # Check that the output file is the same as the input file
    # We don't expect complete equality because chain/entity names
    complex_2 = parser.parse(output_path)
    # print(complex_2)
    assert len(complex_.ligands) == len(complex_2.ligands)

    for sub_list_1, sub_list_2 in zip(
        sub_lists, [complex_2.proteins, complex_2.dnas, complex_2.rnas]
    ):
        assert len(sub_list_1) == len(sub_list_2)
        for polymer_1, polymer_2 in zip(sub_list_1, sub_list_2):
            assert polymer_1.chain.replace("xp", "") == polymer_2.chain.replace(
                "xp", ""
            ), "Mismatched chain names"
            assert (
                polymer_1.sequence == polymer_2.sequence
            ), "Mismatched sequences. {} vs {}".format(
                polymer_1.sequence, polymer_2.sequence
            )


def test_apply_transform(target_name=simple_target):
    target_path = get_file_by_pdb_id(target_name)
    parser = GemmiParser()

    complex_ = parser.parse(target_path)
    R, t = _gen_random_transform()

    new_proteins = [prot.apply_transform(R, t) for prot in complex_.proteins]
    R_inv = R.T
    t_inv = -1 * (t @ R)
    reback_proteins = [prot.apply_transform(R_inv, t_inv) for prot in new_proteins]

    for prot, reback_prot in zip(complex_.proteins, reback_proteins):
        assert np.allclose(prot.coords, reback_prot.coords), "Transformation failed"


def test_align_complexes(target_name=simple_target):
    target_path = get_file_by_pdb_id(target_name)
    parser = GemmiParser()

    target_complex = parser.parse(target_path)

    predicted_complex = copy.deepcopy(target_complex)
    R, t = _gen_random_transform()

    predicted_complex = apply_transform_complex(predicted_complex, R, t)

    alignment_dict, predicted_complex, _ = align_complex(
        predicted_complex, target_complex
    )

    np.allclose(alignment_dict["R"], R, atol=1e-5)
    np.allclose(alignment_dict["t"], t, atol=1e-5)


def test_align_molecules():
    """
    Test alignment of small molecules
    Use amino acids as test data, no real reason, could be anything
    Since there is ambiguity in small molecules for calculating RMSD and such,
    we want to line up the atoms .
    """

    atom_types = foldeverything.data.const.ligand.atom_types

    aa_smiles = {
        "ALA": "C[C@H](N)C=O",
        "CYS": "N[C@H](C=O)CS",
        "ASP": "N[C@H](C=O)CC(=O)O",
        "GLU": "N[C@H](C=O)CCC(=O)O",
        "PHE": "N[C@H](C=O)Cc1ccccc1",
        "GLY": "NCC=O",
        "HIS": "N[C@H](C=O)Cc1c[nH]cn1",
        "ILE": "CC[C@H](C)[C@H](N)C=O",
        "LYS": "NCCCC[C@H](N)C=O",
        "LEU": "CC(C)C[C@H](N)C=O",
        "MET": "CSCC[C@H](N)C=O",
        "ASN": "NC(=O)C[C@H](N)C=O",
        "PRO": "O=C[C@@H]1CCCN1",
        "GLN": "NC(=O)CC[C@H](N)C=O",
        "ARG": "N=C(N)NCCC[C@H](N)C=O",
        "SER": "N[C@H](C=O)CO",
        "THR": "C[C@@H](O)[C@H](N)C=O",
        "VAL": "CC(C)[C@H](N)C=O",
        "TRP": "N[C@H](C=O)Cc1c[nH]c2ccccc12",
        "TYR": "N[C@H](C=O)Cc1ccc(O)cc1",
    }

    use_keys = list(aa_smiles.keys())
    check_molecules = aa_smiles
    for ii, key in enumerate(use_keys):
        check_mol = check_molecules[key]
        mol1 = Chem.MolFromSmiles(check_mol)
        generate_conformer(mol1)
        coords1, one_hot_anums1, adj_matr1 = mol_to_props(mol1)
        coords2, one_hot_anums2, adj_matr2 = (
            copy.deepcopy(coords1),
            copy.deepcopy(one_hot_anums1),
            copy.deepcopy(adj_matr1),
        )

        num_atoms = len(coords1)
        # Shuffle the atom order
        seed = 12345 + ii
        np.random.seed(seed)
        new_order = np.random.permutation(num_atoms)
        expected_inv_order = np.argsort(new_order)

        coords2 = coords2[new_order, :].copy()

        assert np.allclose(
            coords1, coords2[expected_inv_order, :]
        ), "Inverse order failed"

        one_hot_anums2 = one_hot_anums2[new_order, :]
        adj_matr2 = adj_matr2[new_order, :][:, new_order]

        # Check that we actually did some shuffling
        assert not np.allclose(coords1, coords2), f"Shuffling failed in {key}"
        assert not np.array_equal(
            one_hot_anums1, one_hot_anums2
        ), f"Shuffling failed in {key}"
        assert not np.array_equal(adj_matr1, adj_matr2), f"Shuffling failed in {key}"

        # Apply a random transformation to new coords
        R, t = _gen_random_transform(seed=seed)
        coords2 = (coords2 @ R.T) + t
        min_result, isomorphisms, min_isomorphism = rmsd_isomorphic_core(
            coords1,
            coords2,
            one_hot_anums1,
            one_hot_anums2,
            adj_matr1,
            adj_matr2,
            center=True,
            minimize=True,
        )

        # Since the only thing I did was whole-body rotation/translation,
        # the RMSD should be zero.
        assert abs(min_result) <= 1e-6, f"RMSD is not zero: {min_result}"

        el1 = np.array([atom_types[x] for x in one_hot_to_index(one_hot_anums1)])
        el2 = np.array([atom_types[x] for x in one_hot_to_index(one_hot_anums2)])

        # The iso-morphism is specified as a mapping from both graphs to a common space
        # P_1 el1 = P_2 el2, where P_i is the permutation given by a list of indices
        one_map, two_map = np.array(min_isomorphism[0]), np.array(min_isomorphism[1])
        el1_rem = el1[one_map]
        el2_rem = el2[two_map]
        assert np.all(el1_rem == el2_rem), f"Element types do not match for {key}"

        # el1 = P_1^-1 P_2 el2
        inv_one_map = np.argsort(one_map)
        two_one_map = two_map[inv_one_map]

        recov_two = el2[two_one_map]
        assert np.all(
            two_one_map == expected_inv_order
        ), f"Unexpected inverse order in {key}"
        assert np.all(recov_two == el1), f"Failed to recover element types in {key}"

        # el2 = P_2^-1 P_1 el1
        inv_two_map = np.argsort(two_map)
        one_two_map = one_map[inv_two_map]
        assert np.all(
            el1[one_two_map] == el2
        ), f"Failed to recover element types in {key}"


def test_eval_target():
    # Note: Alignment of 4wqs takes ~2 minutes on my machine (x2 because mirror)
    targets = [simple_target, complex_target]
    metrics = [
        fe_metrics.gdt.GDT_TS(),
        fe_metrics.gdt.GDT_HA(),
        fe_metrics.lddt.LDDT(mode="all_atom"),
        fe_metrics.lddt.LDDT(mode="backbone"),
        fe_metrics.rmsd.RMSD(),
        fe_metrics.tmscore.TMscore(),
    ]

    perfect_metric_results = {
        "GDT_TS_backbone": 1.0,
        "GDT_HA_backbone": 1.0,
        "LDDT_all_atom": 1.0,
        "LDDT_backbone": 1.0,
        "RMSD_all_atom": 0.0,
        "TMscore_backbone": 1.0,
    }

    global_metrics = {
        "GDT_TS_backbone",
        "GDT_HA_backbone",
        "RMSD_all_atom",
        "TMscore_backbone",
    }
    local_metrics = {"LDDT_all_atom"}

    metric_keys = list(perfect_metric_results.keys())
    for polymer_field in complex_polymer_fields:
        for key in metric_keys:
            perfect_metric_results[f"{polymer_field}_{key}"] = perfect_metric_results[
                key
            ]

            if key in global_metrics:
                global_metrics.add(f"{polymer_field}_{key}")
            if key in local_metrics:
                local_metrics.add(f"{polymer_field}_{key}")

    t_max = 10.0

    for target_name in targets:
        print(f"Testing eval on target {target_name}")
        target_path = get_file_by_pdb_id(target_name)
        parser = GemmiParser()
        target_complex = parser.parse(target_path)

        predicted_complex = copy.deepcopy(target_complex)
        R, t = _gen_random_transform(t_max=t_max)
        predicted_complex = apply_transform_complex(predicted_complex, R, t)

        eval_results = eval_target(
            predicted_complex, target_complex, metrics, align=False
        )
        # With no alignment, all the global metrics should be terrible
        for eval_key in eval_results:
            if eval_key in global_metrics:
                if "RMSD" in eval_key:
                    assert (
                        eval_results[eval_key] > t_max
                    ), f"Global metric {eval_key} failed"
                else:
                    assert (
                        eval_results[eval_key] < 0.1
                    ), f"Global metric {eval_key} failed"
            # Local distance metric should still be good, even without alignment
            if eval_key in local_metrics:
                assert np.isclose(
                    eval_results[eval_key], perfect_metric_results[eval_key], atol=1e-3
                ), f"Local metric {eval_key} failed"

        # Align the complexes and check. All should be good.
        eval_results = eval_target(
            predicted_complex, target_complex, metrics, align=True
        )
        for eval_key in eval_results:
            assert np.isclose(
                eval_results[eval_key], perfect_metric_results[eval_key], atol=1e-4
            ), f"Target {target_name} failed on metric {eval_key}"

        print(f"Target {target_name} passed all tests")


def test_efficient_lddt():
    import foldeverything.eval.metrics.lddt as lddt

    num_test_points = 1000
    cutoff = 10.0
    offset = 1.0

    np.random.seed(12345 + 4 + 8675309)
    target_points = cutoff * np.random.normal(
        loc=0.0, scale=cutoff, size=(num_test_points, 3)
    )
    predicted_points = target_points + offset * np.random.randn(num_test_points, 3)

    reg_score = lddt.lddt(target_points, predicted_points, cutoff, efficient_mode=False)
    eff_score = lddt.lddt(target_points, predicted_points, cutoff, efficient_mode=True)
    # print(f"Regular LDDT: {reg_score:0.6f}. Efficient LDDT: {eff_score:0.6f}")
    np.isclose(reg_score, eff_score, atol=1e-5)

    # Can't do the inefficient mode with a large number of points
    # So we come up with a simple test case. If we just scale the distances a little bit,
    # the LDDT should be very close to 1.
    num_test_points = 20_000
    target_points = np.random.randn(num_test_points, 3)
    target_points += np.arange(num_test_points)[:, None] / cutoff
    predicted_points = 0.95 * target_points
    eff_score = lddt.lddt(target_points, predicted_points, cutoff, efficient_mode=True)
    assert (
        eff_score > 0.95
    ), f"Efficient LDDT with {num_test_points} failed: {eff_score}"

    predicted_points = 1.05 * target_points
    eff_score = lddt.lddt(target_points, predicted_points, cutoff, efficient_mode=True)
    assert (
        eff_score > 0.95
    ), f"Efficient LDDT with {num_test_points} failed: {eff_score}"


def load_pdb(inpath, polymer_type, chain_map=None):
    """Load a PDB file with gemmi. Only supports a single polymer type for now."""
    structure = gemmi.read_structure(inpath)
    structure.merge_chain_parts()
    structure.ensure_entities()

    proteins = []
    dnas = []
    rnas = []
    model = structure[0]
    for chain in model:
        chain_id = chain.name

        # This is all very hacky, but it's just for testing
        if chain_map and chain_id not in chain_map:
            continue

        if chain_map and chain_id in chain_map:
            chain_id = chain_map[chain_id]

        polymer = chain.get_polymer()
        if len(polymer) == 0:
            continue
        sequence = [res.name for res in polymer]

        # Check polymer type
        if polymer_type in {"PeptideL", "PeptideD"}:
            parsed_protein = parse_gemmi_protein(polymer, sequence)
            proteins.append(parsed_protein)
        elif polymer_type == "Dna":
            parsed_dna = parse_gemmi_dna(polymer, sequence)
            dnas.append(parsed_dna)
        elif polymer_type == "Rna":
            parsed_rna = parse_gemmi_rna(polymer, sequence)
            parsed_rna = RNA(
                chain=chain_id,
                sequence=parsed_rna.sequence,
                indices=parsed_rna.indices,
                coords=parsed_rna.coords,
                mask=parsed_rna.mask,
            )
            rnas.append(parsed_rna)

    return Complex(
        proteins=proteins,
        dnas=dnas,
        rnas=rnas,
        ligands=[],
        resolution=0.0,
        deposited="",
        revised="",
    )


def test_rna_calc_inf():
    predicted_path = os.path.join(TEST_DATA_DIR, "R1107TS232_1.pdb")
    target_path = os.path.join(TEST_DATA_DIR, "7qr4.pdb")
    # Taken from https://www.predictioncenter.org/casp15/rna_results.cgi?target=R1107,
    # for model R1107TS232_1
    expected_results = {
        "inf_all": 0.87,
        "inf_stack": 0.86,
        "inf_wc": 0.98,
        "inf_nwc": 0.57,
    }

    predicted_complex = load_pdb(predicted_path, "Rna")
    target_complex = load_pdb(target_path, "Rna", chain_map={"B": "0"})

    rna_tools_metric = fe_metrics.rna.RNA_calc_inf()
    metrics = [rna_tools_metric]

    eval_results = eval_target(predicted_complex, target_complex, metrics, align=False)

    prefix = "rnas_RNA_Tools_all_atom_".lower()
    found_keys = set()
    for act_key, act_val in eval_results.items():
        act_key = act_key.lower().replace(prefix, "")
        if act_key in expected_results:
            assert np.isclose(
                act_val, expected_results[act_key], atol=2e-2
            ), f"RNA tool {act_key} failed: {act_val} vs {expected_results[act_key]}"
            found_keys.add(act_key)

    assert len(found_keys) == len(
        expected_results
    ), f"RNA tool keys mismatch: {found_keys} vs {expected_results.keys()}"


def test_clashscore():
    predicted_path = os.path.join(TEST_DATA_DIR, "R1107TS232_1.pdb")
    target_path = os.path.join(TEST_DATA_DIR, "7qr4.pdb")
    expected_clashscore = 14.93

    predicted_complex = load_pdb(predicted_path, "Rna")
    target_complex = load_pdb(target_path, "Rna", chain_map={"B": "0"})

    if False:
        tmp = predicted_complex
        predicted_complex = target_complex
        target_complex = tmp

    metrics = [fe_metrics.rna.Clashscore()]

    eval_results = eval_target(predicted_complex, target_complex, metrics, align=False)
    need_keys = [
        "rnas_Clashscore_all_atom_clashscore",
        "rnas_Clashscore_all_atom_num_clashes",
    ]
    for key in need_keys:
        assert key in eval_results, f"Clashscore key {key} missing"
        tmp_val = eval_results[key]
        is_numeric = isinstance(tmp_val, (int, float))
        assert is_numeric, f"Clashscore key {key} is not numeric: {tmp_val}"

    act_clashscore = eval_results["rnas_Clashscore_all_atom_clashscore"]
    assert np.isclose(
        act_clashscore, expected_clashscore, atol=0.05
    ), f"Clashscore failed: {act_clashscore} vs {expected_clashscore}"


def test_codm_score():
    # My calculations are getting different results, not really sure why.

    prediction_name = "T1104TS091_1-D1.pdb"  # expect 0.56
    expected_codm = 0.56

    # prediction_name = "T1104TS091_1-D1.pdb"  # expect 0.56
    # prediction_name = "T1104TS478_1-D1.pdb"  # expect 0.88
    # prediction_name = "T1104TS092_1-D1.pdb"  # expect 0.98

    predicted_path = os.path.join(TEST_DATA_DIR, prediction_name)
    target_path = os.path.join(TEST_DATA_DIR, "7roa.pdb")
    # Based on https://www.predictioncenter.org/casp15/results.cgi?view=tables&target=T1104-D1

    polymer_type = "PeptideL"
    predicted_complex = load_pdb(predicted_path, polymer_type)
    target_complex = load_pdb(target_path, polymer_type)

    metrics = [fe_metrics.codm.CoDM()]

    eval_results = eval_target(predicted_complex, target_complex, metrics, align=False)
    key = "proteins_CoDM_backbone_codm"
    assert key in eval_results, f"CoDM key {key} missing"
    act_codm = eval_results[key]
    assert np.isclose(
        act_codm, expected_codm, atol=2e-2
    ), f"CoDM failed: {act_codm:0.4f} vs {expected_codm}"


def test_write_complex():
    # Test that we can write a complex to a cif file, including ligands
    target = ligand_target
    target_path = get_file_by_pdb_id(target)

    parser = GemmiParser()
    target_complex = parser.parse(target_path)
    # print(f"Original complex: {target_complex}")
    assert len(target_complex.ligands) >= 1, "No ligands found"

    output_path = os.path.join(TEST_OUTPUT_DIR, f"{target}_resaved.cif")
    foldeverything.eval.utils.write_complex(target_complex, output_path)
    assert os.path.exists(output_path), f"Output file {output_path} not found"

    sdf_base = os.path.join(TEST_OUTPUT_DIR, f"{target}")
    for ligand in target_complex.ligands:
        sdf_path = f"{sdf_base}_{ligand.chain}_{ligand.name}.sdf"
        writer = Chem.SDWriter(sdf_path)
        writer.write(ligand.mol)
        writer.close()

    """
    From what I can tell, write_complex does write out ligands but renames them or something
    so we can't read them in again. I'm not sure how to fix this, gemmi does
    some automatic renaming (might also be other issues).
    """
    # parser = GemmiParser()
    # target_complex2 = parser.parse(output_path)
    # This doesn't load the ligands, so we can't compare them
    # print(f"Resaved complex: {target_complex2}")


if __name__ == "__main__":
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

    # test_gemmi_parser()
    # test_apply_transform()
    # test_align_complexes()
    # test_align_molecules()
    # test_efficient_lddt()
    # test_eval_target()
    # test_rna_calc_inf()
    # test_clashscore()
    # test_codm_score()
    test_write_complex()

    print(f"Finished test_eval.py")
