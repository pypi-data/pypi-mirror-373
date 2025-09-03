import collections
from dataclasses import asdict, replace
import fcntl
import json
import queue
import time
from typing import Dict, List, Optional, Type, Union
import pandas as pd
from pathlib import Path
import torch
import torch.multiprocessing as mp
from torch.multiprocessing import Queue, Process
import os
from hydra.utils import get_class
from omegaconf import OmegaConf
from pytorch_lightning import LightningModule

from foldeverything.data import const
from foldeverything.data.data import Atom
from foldeverything.data.parse.schema import get_conformer

from foldeverything.data.write.mmcif import to_mmcif
from foldeverything.data.write.pdb import to_pdb
from foldeverything.task.hallucination.binder_hallucinator import BinderHallucination, BinderHallucinationConfig
from foldeverything.task.hallucination.coordinate_trajectory import pdb_strings_to_aligned_trajectory

from foldeverything.task.predict.data_eval import (
    EvalDataModule,
)
from foldeverything.task.predict.predict import _load_from_checkpoint
from foldeverything.task.task import Task
import wandb
import numpy as np
from foldeverything.data.mol import load_canonicals, load_molecules
from foldeverything.task.predict.data_ligands import collate

# TODO put this function somewhere else?
def get_atoms(res_name, ref_mol):
    # ref_mol = AllChem.RemoveHs(ref_mol, sanitize=False)
    ref_conformer = get_conformer(ref_mol)

    # Only use reference atoms set in constants
    ref_name_to_atom = {a.GetProp("name"): a for a in ref_mol.GetAtoms()}
    ref_atoms = [ref_name_to_atom[a] for a in const.ref_atoms[res_name]]

    # Iterate, always in the same order
    atoms: list[tuple] = []

    for ref_atom in ref_atoms:
        # Get atom name
        atom_name = ref_atom.GetProp("name")
        idx = ref_atom.GetIdx()

        # Get conformer coordinates
        ref_coords = ref_conformer.GetAtomPosition(idx)
        ref_coords = (ref_coords.x, ref_coords.y, ref_coords.z)

        # Add atom to list
        atoms.append((atom_name, ref_coords, True, 0, 1))
    atoms = np.array(atoms, dtype=Atom)
    return atoms


class HallucinationTask(Task):
    """Protein design / optimization by backpropagating through a soft sequence."""

    def __init__(
        self,
        name: str,
        cls: str,
        data: Union[EvalDataModule],
        checkpoint: str,
        output_dir: str,
        num_designs: int,
        moldir: str,
        hallucination_config: BinderHallucinationConfig,
        wandb: Optional[dict] = None,
        model_args: Optional[dict] = None,
        use_ema: bool = False,
        single_process: bool = False,
        run_info: Optional[dict] = None,
    ) -> None:
        self.cls = cls
        self.checkpoint = checkpoint
        self.output_dir = output_dir
        self.num_designs = num_designs
        self.model_args = model_args if model_args is not None else {}
        self.name = name
        self.use_ema = use_ema
        self.wandb = wandb
        self.moldir = moldir
        self.data = data
        self.hallucination_config = hallucination_config
        self.single_process = single_process

        if run_info is None:
            run_info = {}
        self.run_info = run_info
    
    def run(self, config: OmegaConf = None) -> None:  # noqa: ARG002
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        dataloader = self.data.predict_dataloader()
        batch_data = list(enumerate(dataloader))

        # Save config.
        config_output_path = Path(self.output_dir) / f"config.yaml"
        OmegaConf.save(config=config, f=config_output_path)
        print(f"Wrote config to {config_output_path}")

        stats_output_path = Path(self.output_dir) / f"stats.csv"
        if stats_output_path.exists():
            stats_output_path.unlink()

        # Get available GPUs
        assert torch.cuda.is_available(), "CUDA is not available"
        num_gpus = torch.cuda.device_count()
        print(f"Found {num_gpus} GPUs.")
        
        # Set multiprocessing start method to 'spawn' for CUDA compatibility
        if mp.get_start_method(allow_none=True) != 'spawn':
            mp.set_start_method('spawn', force=True)
                
        print(f"Preparing work items for {len(batch_data)} batches with {self.num_designs} designs each.")

        def task_config_generator():
            for (batch_num, features) in batch_data:
                for design_num in range(self.num_designs):
                    task_config = {
                        'batch_num': batch_num,
                        'design_num': design_num,
                        'features': features,
                        'stats_output_path': stats_output_path,
                        'cls': self.cls,
                        'checkpoint': self.checkpoint,
                        'model_args': self.model_args,
                        'use_ema': self.use_ema,
                        'moldir': self.moldir,
                        'hallucination_config': self.hallucination_config,
                        'wandb_config': self.wandb,
                        'name': self.name,
                        'output_dir': self.output_dir,
                        'num_designs': self.num_designs,
                    }
                    yield task_config
    
        def write_results_df(results: List[dict], stats_output_path: Path):
            df = pd.DataFrame.from_records(results)
            df.to_csv(stats_output_path, index=False)
            print(f"Wrote results to: {stats_output_path}")

        if self.single_process:
            print("Running in single process mode")
            if num_gpus > 1:
                print("WARNING: multiple GPUs available but single process mode is enabled. Only one GPU will be used.")

            constant_data = None
            results = []
            for task_config in task_config_generator():
                task_config['gpu_id'] = 0
                if constant_data is None:
                    constant_data = initialize_process(**task_config)
                task_config.update(constant_data)
                stats_row = do_design(**task_config)
                results.append(stats_row)
                write_results_df(results, stats_output_path)
        else:
            all_work_items = list(task_config_generator())
            total_designs = len(all_work_items)

            # Put work into queue
            work_queue = Queue()
            result_queue = Queue()
            for work_item in all_work_items:
                work_queue.put(work_item)
            for _ in range(num_gpus):
                work_queue.put(None)

            del all_work_items
            results = []

            print(f"Processing {total_designs} total designs across {num_gpus} GPUs")
            gpu_id_to_process = {}
            for gpu_id in range(num_gpus):
                p = Process(target=worker_process, args=(gpu_id, work_queue, result_queue))
                p.start()
                gpu_id_to_process[gpu_id] = p

            error = None
            while gpu_id_to_process:
                print(f"Waiting for results from {len(gpu_id_to_process)} processes")
                result = result_queue.get()
                if result["type"] == "result":
                    results.append(result["stats_row"])
                    write_results_df(results, stats_output_path)
                elif result["type"] == "error":
                    print(f"Error in worker process {result['process_id']}: {result['error']}")
                    error = result["error"]
                elif result["type"] == "finished":
                    process = gpu_id_to_process.pop(result["process_id"])
                    process.join()
            if error:
                raise error
            print(f"Completed all {total_designs} designs across {len(batch_data)} batches")
        print("Done!")


def worker_process(gpu_id, work_queue, result_queue, raise_on_error: bool = False):
    torch.cuda.set_device(gpu_id)
    torch.manual_seed(os.getpid() + time.time())
    
    print(f"Worker process {os.getpid()} started on GPU {gpu_id}")

    constant_data = None
    
    total_processed = 0
    try:
        while True:
            try:
                task_config = work_queue.get()
                if task_config is None:
                    break
                task_config['gpu_id'] = gpu_id
                if constant_data is None:
                    constant_data = initialize_process(**task_config)
                task_config.update(constant_data)
                stats_row = do_design(**task_config)
                result_queue.put({
                    "type": "result",
                    "process_id": gpu_id,
                    "stats_row": stats_row,
                })
                total_processed += 1
            except Exception as e:
                print(f"Error in worker process {os.getpid()} on GPU {gpu_id}: {e}")
                import traceback
                traceback.print_exc()
                result_queue.put({
                    "type": "error",
                    "process_id": gpu_id,
                    "error": e,
                })
                if raise_on_error:
                    raise
    finally:
        result_queue.put({
            "type": "finished",
            "process_id": gpu_id,
        })
        print(f"Worker process {os.getpid()} on GPU {gpu_id} finished, after processing {total_processed} designs")

def initialize_process(gpu_id, use_ema, features, model_args, checkpoint, cls, moldir, **kwargs):
    torch.cuda.set_device(gpu_id)
    torch.manual_seed(os.getpid() + time.time())
    molecules = load_canonicals(moldir)
    atoms = {
        token: get_atoms(token, molecules[token])
        for token in const.canonical_tokens
    }
    model_cls: Type[LightningModule] = get_class(cls)
    boltz_model = _load_from_checkpoint(
        model_cls,
        checkpoint,
        strict=False,
        use_ema=use_ema,
        use_templates=False,
        max_seqs=1,
        max_tokens=features["token_pad_mask"].shape[-1],
        batch_size=1,
        **model_args,
    )
    boltz_model.to(torch.cuda.current_device())
    return {
        "molecules": molecules,
        "atoms": atoms,
        "boltz_model": boltz_model,
    }


def do_design(
    molecules: dict,
    atoms: dict,
    boltz_model: LightningModule,
    batch_num: int,
    design_num: int, 
    features: dict,
    stats_output_path: Path,
    gpu_id: int,
    cls: str,
    checkpoint: str,
    model_args: dict,
    use_ema: bool,
    moldir: str,
    hallucination_config,
    wandb_config: Optional[dict],
    name: str,
    output_dir: str,
    num_designs: int,
):
    # Initialize wandb for this worker process
    if wandb_config:
        # Create a unique run name for this worker process
        worker_run_name = f"{name}_batch{batch_num}_design{design_num}_gpu{gpu_id}"
        wandb.init(
            name=worker_run_name,
            group=name,  # Group runs together by experiment name
            job_type="design",
            **wandb_config
        )
        wandb.config.update({
            "total_designs": num_designs,
            "experiment_name": name,
            "gpu_id": gpu_id,
            "batch_num": batch_num,
            "design_num": design_num,
        })
    else:
        # Disable wandb for this process
        wandb.init(mode="disabled")
    
    stats_row = collections.OrderedDict()
    stats_row["batch_num"] = batch_num
    stats_row["design_num"] = design_num
    stats_row["gpu_id"] = gpu_id
    device = torch.device(f"cuda:{gpu_id}")
    features = {
        k: v.to(device) if isinstance(v, torch.Tensor) else v
        for k, v in features.items()
    }

    # Load non-protein molecules
    tokenized, = features["tokenized"]
    missing_molecules = set(tokenized.tokens["res_name"]) - set(molecules.keys())
    print("Loading missing molecules: ", missing_molecules)
    molecules.update(load_molecules(moldir, missing_molecules))

    print(f"{'=' * 80}")
    print(f"Starting design {design_num + 1}/{num_designs} on GPU {gpu_id}")
    print(f"{'=' * 80}")

    design_prefix = f"design_{design_num + 1:03d}"
    hallucinator = BinderHallucination(
        boltz_model,
        initial_features=features,
        config=hallucination_config,
        molecules=molecules,
        canonical_atoms=atoms,
        wandb_config=wandb_config,
        design_prefix=design_prefix,
    )
    print("+" * 80)
    print(f"DESIGN #{design_num + 1} of {num_designs}")
    print("Hallucinator: ", hallucinator)
    print("Design problem (initial features):")
    print(hallucinator.summarize_features(features))

    # Compute coordinate trajectory
    stats_row["initial_ptm"] = None
    stats_row["initial_iptm"] = None
    stats_row["initial_affinity_pred_value"] = None
    stats_row["initial_affinity_probability_binary"] = None
    coordinate_trajectory_result = hallucinator.forward()
    stats_row["initial_ptm"] = coordinate_trajectory_result.get("ptm", None)
    stats_row["initial_iptm"] = coordinate_trajectory_result.get("iptm", None)
    stats_row["initial_affinity_pred_value"] = coordinate_trajectory_result.get("affinity_pred_value", None)
    stats_row["initial_affinity_probability_binary"] = coordinate_trajectory_result.get("affinity_probability_binary", None)
    stats_row["initial_sequences"] = json.dumps(hallucinator.get_hard_sequences())
        
    print("*" * 80)
    print("First step features:")
    print(hallucinator.summarize_features())
    print("*" * 80)

    best_design = hallucinator.optimize()
    print(f"Finished optimization for design {design_num + 1}.")
    print(
        f"Best design: {best_design}"
    )
    
    # Log summary plots to wandb
    hallucinator.log_summary_plots()

    # Save the metadata.npz file
    metadata_output_path = Path(output_dir) / f"batch{batch_num}_sample{design_num}_rank0_{name}_metadata.npz"
    metadata = {}
    metadata["design_mask"] = hallucinator.design_mask.squeeze(0)
    metadata["token_resolved_mask"] = torch.ones_like(metadata["design_mask"])
    for key in list(metadata):
        if isinstance(metadata[key], torch.Tensor):
            metadata[key] = metadata[key].cpu().numpy()
    np.savez(metadata_output_path, **metadata)

    # Save a cif file for the design
    final_result = hallucinator.forward(
        res_type=hallucinator.get_res_type(best_design.designed_one_hot_sequence))
    final_structure = final_result.pop("structure")
    for key, value in final_result.items():
        if key not in ["pdistogram", "plddt"]:
            stats_row[f"final_{key}"] = value

    mmcif_contents = to_mmcif(final_structure)
    output_path = (
        Path(output_dir)
        / f"batch{batch_num}_sample{design_num}_rank0_{name}_gen.cif"
    )
    stats_row["output_cif"] = str(output_path)
    with open(output_path, "w") as f:
        f.write(mmcif_contents)
    print(f"Wrote design cif to {output_path}")
    if wandb_config:
        wandb.save(str(output_path))

    pdb_contents = to_pdb(final_structure)
    output_path = (
        Path(output_dir)
        / f"batch{batch_num}_sample{design_num}_rank0_{name}_gen.pdb"
    )
    stats_row["output_pdb"] = str(output_path)
    with open(output_path, "w") as f:
        f.write(pdb_contents)
    print(f"Wrote design pdb to {output_path}")
    if wandb_config:
        wandb.save(str(output_path))

    # Save the full trajectory info as a json file.
    trajectory_output_path = Path(output_dir) / f"batch{batch_num}_sample{design_num}_rank0_{name}_trajectory_info.json"
    trajectory_info = hallucinator.trajectory_info_as_df()
    trajectory_info.to_json(trajectory_output_path, orient="records")
    stats_row["trajectory_info_json"] = str(trajectory_output_path)
    print(f"Wrote trajectory info to {trajectory_output_path}")
    if wandb_config:
        wandb.save(str(trajectory_output_path))

    # Save the coordinate trajectory using MDTraj
    if "structure_pdb" in trajectory_info:
        try:
            import mdtraj
            traj = pdb_strings_to_aligned_trajectory(trajectory_info.structure_pdb)
            traj_output_path = Path(output_dir) / f"batch{batch_num}_sample{design_num}_rank0_{name}_trajectory.pdb"
            traj.save(traj_output_path)
            print(f"Wrote trajectory to {traj_output_path}")
            if wandb_config:
                wandb.save(str(traj_output_path))
        except ImportError:
            print("MDTraj is not installed, skipping trajectory saving")
            
    # Log the cif to wandb
    if wandb_config:
        wandb.save(str(output_path))
        wandb.log(
            {
                f"{design_prefix}/final_prediction_cif": wandb.Molecule(
                    str(output_path)
                )
            }
        )

    # Add final trjajectory row to stats_rows for items that are ints/floats/strings
    final_trajectory_state = hallucinator.get_current_trajectory_step_items()
    for key, value in final_trajectory_state.items():
        if isinstance(value, (int, float)) or (isinstance(value, str) and len(value) < 100):
            stats_row[f"final_{key}"] = value
    stats_row["best_sequences"] = json.dumps(hallucinator.get_hard_sequences())
    stats_row["num_attempts"] = len(hallucinator.trajectories)
    for key, value in asdict(best_design).items():
        if isinstance(value, (str, int, float)):
            stats_row[f"best_design_{key}"] = value
    stats_row["total_steps"] = len(hallucinator.trajectories)
    stats_row["wandb_url"] = wandb.run.url if wandb_config else None

    print("Stats:")
    for key, value in stats_row.items():
        value_str = str(value)
        if len(value_str) > 80:
            value_str = value_str[:77] + "..."
        print(f"\t{key:<50}: {value_str}")

    # Finish the wandb run for this worker process
    if wandb_config:
        wandb.finish()
    return stats_row
