import os
import re
import subprocess
from collections.abc import MutableMapping
from os import PathLike
from pathlib import Path
import tempfile
from typing import Dict, List, Tuple, Optional

import gemmi
import numpy as np
import pandas as pd

# from minifold.utils.openfold import from_pdb_string, get_atom_coords_b, parse
from tqdm import tqdm

import foldeverything
import foldeverything.eval.utils
from foldeverything.complex import Complex
from foldeverything.data.const import protein as const
from foldeverything.types import Polymer, Protein, RNA, DNA
from foldeverything.eval.data.dataset import Dataset
from foldeverything.eval.metrics.metric import Metric
from foldeverything.eval.models.model import Model

# from foldeverything.eval.protein import Prediction, Protein, Target
from foldeverything.eval.utils import complex_polymer_fields

project_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../../.."))


def flatten(dictionary: Dict, parent_key: str = "", separator: str = "_") -> Dict:
    """Flatten a nested dictionary.

    Parameters
    ----------
    dictionary : Dict
        The dictionary to flatten
    parent_key : str
        The parent key
    separator : str
        The separator to use

    Returns
    -------
    Dict
        The flattened dictionary

    """
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


def __apply_alignment_old(prot: Protein, seq: str) -> Protein:
    """Apply the alignment to the protein.

    In some cases, unknown residues are not placed in the
    output prediction, which results in some misalignment
    with the target. We fix this by removing the unknown
    residues from the original target sequence and coords.
    In addition, we add zeros for the gapped residues.

    Parameters
    ----------
    prot : Protein
        The protein to fix
    seq : str
        The aligned sequence to match

    Returns
    -------
    Protein
        The fixed protein

    """
    # Initialize pointers
    i, j = 0, 0

    # Initialize outputs
    new_seq = ""
    new_coords = []
    new_mask = []
    num_atoms = len(prot.atoms)
    new_b_factors = []

    # We ge through both sequences, removing residues
    # that are not present in the aligned sequence
    while j < len(seq):
        # Handle alignment gaps
        if seq[j] == "-":
            new_seq += "-"
            new_coords.append(np.zeros((num_atoms, 3)))
            new_mask.append(np.zeros(num_atoms))
            new_b_factors.append(np.zeros(num_atoms))
            j += 1

        # If there is a mismatch, it comes from a deletion
        # in the aligned sequence, so we simply skip that.
        elif prot.sequence[i] != seq[j]:
            i += 1

        # Otherwise, we add the residue to the new sequence
        # but check that there is no mismatch
        else:
            new_seq += prot.sequence[i]
            new_coords.append(prot.coords[i])
            new_mask.append(prot.mask[i])
            new_b_factors.append(prot.b_factors[i])
            i += 1
            j += 1

    # Check that everything went according to plan
    assert new_seq == seq

    # Stack numpy arrays
    new_coords = np.array(new_coords)
    new_mask = np.array(new_mask).astype(bool)
    new_b_factors = np.array(new_b_factors)

    # Update the protein object
    prot = Protein(
        name=prot.name,
        sequence=new_seq,
        coords=new_coords,
        mask=new_mask,
        atoms=prot.atoms,
        b_factors=new_b_factors,
    )
    return prot


def __keep_valid(pred: Protein, target: Protein) -> Tuple[Protein, Protein]:
    """Select only valid residues from the aligned proteins.

    A residue is determined to be valid if it is not gapped
    and is not an ambiguous residue (X, B, J, Z).

    Parameters
    ----------
    pred : Protein
        The predicted protein
    target : Protein
        The target protein

    Returns
    -------
    Protein
        The predicted protein, with only valid residues
    Protein
        The target protein, with only valid residues

    """
    # Initialize outputs
    new_p_seq = ""
    new_t_seq = ""

    new_p_coords = []
    new_t_coords = []

    new_p_mask = []
    new_t_mask = []

    new_p_b_factors = []
    new_t_b_factors = []

    # Check that the sequences have the same length
    assert len(pred.sequence) == len(target.sequence)

    # We ge through both sequences, removing unknown or gapped
    # residues, ensuring that everything else matches correctly
    unknowns = {"X", "B", "J", "Z"}
    for i in range(len(pred.sequence)):
        # First case: gap in the prediction
        if (
            pred.sequence[i] == "-"
            or target.sequence[i] == "-"
            or pred.sequence[i] in unknowns
            or pred.sequence[i] != target.sequence[i]
        ):
            continue

        new_p_seq += pred.sequence[i]
        new_t_seq += target.sequence[i]

        new_p_coords.append(pred.coords[i])
        new_t_coords.append(target.coords[i])

        new_p_mask.append(pred.mask[i])
        new_t_mask.append(target.mask[i])

        new_p_b_factors.append(pred.b_factors[i])
        new_t_b_factors.append(target.b_factors[i])

    # Update the protein object
    pred = Protein(
        name=pred.name,
        sequence=new_p_seq,
        coords=np.array(new_p_coords),
        mask=np.array(new_p_mask).astype(bool),
        atoms=pred.atoms,
        b_factors=np.array(new_p_b_factors),
    )

    target = Protein(
        name=target.name,
        sequence=new_t_seq,
        coords=np.array(new_t_coords),
        mask=np.array(new_t_mask).astype(bool),
        atoms=target.atoms,
        b_factors=np.array(new_t_b_factors),
    )
    return pred, target


def run_USalign(predicted: Complex, target: Complex) -> Tuple[Dict, Dict]:
    exec_path = os.path.join(project_dir, "USalign", "USalign")

    with tempfile.TemporaryDirectory(delete=True) as temp_dir:
        work_dir = temp_dir
        # print(f"USalign working directory: {work_dir}")

        # Create temporary files
        predicted_path = os.path.join(work_dir, "predicted.cif")
        foldeverything.eval.utils.write_complex(predicted, predicted_path)

        target_path = os.path.join(work_dir, "target.cif")
        foldeverything.eval.utils.write_complex(target, target_path)

        cmd = [
            exec_path,
            predicted_path,
            target_path,
            "-ter",
            "0",
            "-mm",
            "1",
            "-outfmt",
            "1",
            "-m",
            "-",
        ]

        try:
            # Capture the output to read it
            output = subprocess.run(cmd, capture_output=True, check=True, cwd=work_dir)
            # print(f"Output:\n{output.stdout.decode()}")
            output = foldeverything.eval.utils.parse_USalign_output(
                output.stdout.decode(), mirror=False
            )

            # Try mirror
            cmd += ["-mirror", "1"]
            output_mirror = subprocess.run(
                cmd, capture_output=True, check=True, cwd=work_dir
            )
            output_mirror = foldeverything.eval.utils.parse_USalign_output(
                output_mirror.stdout.decode(), mirror=True
            )

            return output, output_mirror

        except Exception as e:
            # print(f"An error occurred while running USalign: {e}")
            import traceback

            traceback.print_exc()
            return {}, {}


def align_complex(predicted: Complex, target: Complex) -> Tuple[Dict, Complex, Complex]:
    """Perform a global alignment of two structures.

    Uses the USalign tool to perform the alignment, and
    returns the aligned protein and the reference as
    Complex objects, with the aligned coordinates and
    matched sequence residues only.

    Parameters
    ----------
    predicted : Complex
        Predicted structure to align to target.
    target : Complex
        Target structure to the target structure

    Raises
    ------
    ValueError
        If USalign not installed, or if an error occurs

    """

    output, output_mirror = run_USalign(predicted, target)
    assert output or output_mirror, "No alignment found"
    # Hopefully we only have one alignment, otherwise we take the longest chain
    # Maybe not the best plan
    longest_chain = max(output, key=lambda x: output[x]["L"])
    mirror_longest_chain = max(output_mirror, key=lambda x: output_mirror[x]["L"])

    # print(f"USalign Output keys: {output.keys()}. Longest chain: {longest_chain}")
    # print(f"USalign Output mirror keys: {output_mirror.keys()}. Longest chain: {mirror_longest_chain}")
    output = output[longest_chain]

    if longest_chain in output_mirror:
        output_mirror = output_mirror[longest_chain]
    else:
        output_mirror = output_mirror[mirror_longest_chain]

    if output_mirror["tm"] > output["tm"]:
        output = output_mirror

    transformed_predicted = foldeverything.eval.utils.apply_transform_complex(
        predicted, output["R"], output["t"], mirror=output["mirror"]
    )
    transformed_target = target

    return output, transformed_predicted, transformed_target


def __align_complexes_old(
    predicted: Complex, target: Complex
) -> Tuple[Complex, Complex]:
    """Perform a global alignment of two structures.

    Uses the USalign tool to perform the alignment, and
    returns the aligned protein and the reference as
    Complex objects, with the aligned coordinates and
    matched sequence residues only.

    Parameters
    ----------
    predicted : Complex
        Predicted structure to align to target.
    target : Complex
        Target structure to the target structure

    Raises
    ------
    ValueError
        If USalign not installed, or if an error occurs

    """

    error = None

    # Create temporary files
    predicted_path = "predicted.cif"
    build_gemmi_structure(predicted, predicted_path).make_mmcif_document().write_file(
        predicted_path
    )

    target_path = "target.cif"
    build_gemmi_structure(target, target_path).make_mmcif_document().write_file(
        target_path
    )

    # Run USalign
    # TODO There are many possible parameters,
    # I have this set to a full complex alignment (-mm 1).
    # Sequence-based alignment much faster but obviously only works for polymers
    try:
        cmd = [
            "USalign",
            predicted_path,
            target_path,
            "-ter",
            "0",
            "-mm",
            "1",
            "-outfmt",
            "1",
            "-m",
            "-",
        ]
        # Capture the output to read it
        output = subprocess.run(cmd, capture_output=True, check=True)
        output = foldeverything.eval.utils.parse_USalign_output(output.stdout.decode())

        # Try mirror
        cmd += ["-mirror", "1"]
        output_mirror = subprocess.run(cmd, capture_output=True, check=True)
        output_mirror = foldeverything.eval.utils.parse_USalign_output(
            output_mirror.stdout.decode()
        )

        # When we align one complex to another, we can have multiple chains
        # Which alignment should we pick?
        if output_mirror["tm"] > output["tm"]:
            output = output_mirror
            output["mirror"] = True
        else:
            output["mirror"] = False

        # Read outputs
        p_seq = output["p_seq"]
        t_seq = output["t_seq"]
        t = output["t"]
        R = output["R"]
        mirror = output["mirror"]

    # Catch error so we close the temporary file
    except FileNotFoundError:
        error = "USalign not installed"
    except Exception as e:
        error = "An error occurred while running USalign: " + str(e)

    if error is not None:
        raise ValueError(error)

    # Load data from the prediction and target
    p_prot = load_data(path=predicted_path)
    t_prot = load_data(path=target_path)

    # Apply the alignment only if the sequences are different
    # as USAlign seems to make some mistakes on some sequences
    if p_prot.sequence != t_prot.sequence:
        p_prot = apply_alignment(p_prot, p_seq)
        t_prot = apply_alignment(t_prot, t_seq)

    # Remove gap and unknown residues from the sequences
    p_prot, t_prot = keep_valid(p_prot, t_prot)

    # Check that everything has the expected length now
    assert len(p_prot.sequence) == len(p_prot.coords)
    assert len(t_prot.sequence) == len(t_prot.coords)
    assert len(p_prot.sequence) == len(t_prot.sequence)
    assert len(p_prot.sequence) == len(p_prot.b_factors)

    # Apply the transformation to the prediction
    p_prot = apply_transform(p_prot, R, t, mirror)

    return p_prot, t_prot


def combine_polymers(polymers: List[Polymer]) -> Optional[Polymer]:
    """
    Combine multiple polymers into one polymer containing the full sequence and coordinates and such.
    Polymers must all be the same type (Protein or NA).
    """

    if len(polymers) == 0:
        return None

    types = {type(p) for p in polymers}
    assert len(types) == 1, f"All polymers must be of the same type. Found {types}"
    polymer_type = types.pop()

    # Combine chains
    chain = "_".join(p.chain for p in polymers)
    sequence = "".join(p.sequence for p in polymers)
    # Re-index?
    indices = np.concatenate([p.indices for p in polymers])
    coords = np.concatenate([p.coords for p in polymers], axis=0)
    mask = np.concatenate([p.mask for p in polymers], axis=0)

    return polymer_type(chain, sequence, indices, coords, mask)


def flatten_complex_polymers(fe_complex: Complex) -> Complex:
    """
    Flatten all the polymers in a complex
    """

    kwargs = {
        "resolution": fe_complex.resolution,
        "deposited": fe_complex.deposited,
        "revised": fe_complex.revised,
    }
    for field in complex_polymer_fields:
        polymers = getattr(fe_complex, field)
        new_polymer = [combine_polymers(polymers)]
        kwargs[field] = new_polymer

    kwargs["ligands"] = fe_complex.ligands

    return Complex(**kwargs)


def eval_target(
    predicted: Complex,
    target: Complex,
    metrics: List[Metric],
    align: bool = True,
) -> Dict[str, float]:
    """Evaluate the predictor on the given target.

    Parameters
    ----------
    predicted : Complex
        Predicted complex.
    target : Complex
        Target (ie actual) complex
    metrics : List[Metric]
        List of metrics to evaluate.
    align : bool
        Whether to align the predicted complex to the target before running metrics.
        Generally only set to False for testing/debugging.

    Returns
    -------
    Result
        Evaluation results.

    """

    p_complex = predicted
    t_complex = target

    # Align prediction to target
    # USalign will align polymers to each other, and that will
    # presumably include ligand coordinates.
    # TODO Still need to make sure ligand atoms line up aka deal with permutation symmetry al spyrmsd
    # See utils:rmsd_isomorphic_core
    if align:
        alignment_dict, p_complex, t_complex = align_complex(predicted, target)

    # Run all metrics
    results = {}
    for polymer_field in complex_polymer_fields:
        p_polymers = getattr(p_complex, polymer_field)
        t_polymers = getattr(t_complex, polymer_field)
        assert len(p_polymers) == len(t_polymers), (
            f"Polymer type {polymer_field} mismatch."
            f"Found {len(p_polymers)} and {len(t_polymers)}"
        )
        if len(p_polymers) == 0:
            continue

        p_polymer = combine_polymers(p_polymers)
        t_polymer = combine_polymers(t_polymers)

        sub_results = {}
        for _metric in metrics:
            sub_results[_metric.name] = _metric(p_polymer, t_polymer)

        results[polymer_field] = sub_results

    # Flatten
    results = flatten(results, parent_key="", separator="_")

    return results


def evaluate(
    model: Model,
    datasets: List[Dataset],
    metrics: List[Metric],
    outdir: PathLike,
) -> pd.DataFrame:
    """Evaluate all models on all datasets with all metrics.

    Parameters
    ----------
    model : Predictor
        Predictor to evaluate.
    datasets : List[Dataset]
        List of datasets to evaluate on.
    metrics : List[Metric]
        List of metrics to evaluate.
    outdir : PathLike
        Path to the output directory, to store results.

    Returns
    -------
    pd.DataFrame
        Evaluation results.

    """
    data = []
    outdir = Path(outdir)
    Path.mkdir(outdir, parents=True, exist_ok=True)

    for dataset in datasets:
        print(f"Predicting {dataset.name}...")
        dataset_dir = outdir / dataset.name.lower()
        Path.mkdir(dataset_dir, exist_ok=True)
        preds = model.predict(dataset, dataset_dir)

        print(f"Evaluating {dataset.name}...")
        for pred, target in tqdm(zip(preds, dataset), total=len(dataset)):
            assert target.name == pred.name
            try:
                results = eval_target(pred, target, metrics)
            except Exception as e:
                print(f"Error evaluating {pred.name}: {e}")
                continue
            data.append(
                {
                    "Dataset": dataset.name,
                    "Target": target.name,
                    **results,
                }
            )

    data = pd.DataFrame(data)
    data.to_csv(outdir / "results.csv", index=False)
    return data
