import datetime
import os
import random
import string
import warnings
from pathlib import Path
import time
from typing import Optional
import pytorch_lightning as pl
import torch
import torch.multiprocessing
from omegaconf import OmegaConf, listconfig
from pytorch_lightning import LightningModule
from pytorch_lightning.callbacks.model_checkpoint import ModelCheckpoint
from pytorch_lightning.loggers import WandbLogger
from pytorch_lightning.strategies import DDPStrategy

from foldeverything.task.task import Task
from foldeverything.task.train.data import DataConfig, FoldEverythingDataModule


class Training(Task):
    """Training configuration."""

    def __init__(
        self,
        data: DataConfig,
        model: LightningModule,
        output: str,
        name: str,
        torch_hub_cache: str,
        trainer: Optional[dict] = None,
        resume: Optional[str] = None,
        pretrained: Optional[str] = None,
        load_affinity_from_trunk: Optional[bool] = False,
        wandb: Optional[dict] = None,
        disable_checkpoint: bool = False,
        slurm: bool = False,
        sharing_strategy: Optional[str] = None,
        matmul_precision: Optional[str] = None,
        find_unused_parameters: Optional[bool] = False,
        ddp_timeout_seconds: Optional[int] = 6400,
        save_every_n_train_steps: Optional[int] = None,
        save_top_k: Optional[int] = 1,
        validation_only: bool = False,
        debug: bool = False,
        strict_loading: bool = True,
        decoy_sampling: bool = False,
        new_sampling: bool = False,
        metric_mode: str = "max",
    ) -> None:
        """Initialize training configuration.

        Parameters
        ----------
        data : DataConfig
            The data configuration.
        model : LightningModule
            The model.
        output : str
            The output directory.
        name : str
            The output subdirectory and wandb run name.
        torch_hub_cache : str
            The torch hub cache directory.
        trainer : Optional[dict], optional
            The trainer configuration, by default None.
        resume : Optional[str], optional
            The resume checkpoint, by default None
        pretrained : Optional[str], optional
            The pretrained model, by default None
        wandb : Optional[dict], optional
            The wandb configuration, by default None
        disable_checkpoint : bool, optional
            Disable checkpoint, by default False

        """
        if not isinstance(data, DataConfig):
            data = DataConfig(**data)

        self.data = data
        self.model = model
        self.output = output
        self.name = name
        self.torch_hub_cache = torch_hub_cache
        self.trainer = trainer
        self.resume = resume
        self.pretrained = pretrained
        self.wandb = wandb
        self.disable_checkpoint = disable_checkpoint
        self.slurm = slurm
        self.sharing_strategy = sharing_strategy
        self.matmul_precision = matmul_precision
        self.find_unused_parameters = find_unused_parameters
        self.ddp_timeout_seconds = ddp_timeout_seconds
        self.save_every_n_train_steps = save_every_n_train_steps
        self.save_top_k = save_top_k
        self.validation_only = validation_only
        self.debug = debug
        self.load_affinity_from_trunk = load_affinity_from_trunk
        self.strict_loading = strict_loading
        self.decoy_sampling = decoy_sampling
        self.checkpoint_monitor_val_group = data.checkpoint_monitor_val_group
        self.new_sampling = new_sampling
        self.metric_mode = metric_mode

    def run(self, config: OmegaConf) -> None:
        """Run training.

        Parameters
        ----------
        config : OmegaConf
            The configuration for the task, for bookkeeping.

        """
        # Disable some warnings
        warnings.filterwarnings(
            "ignore", ".*when logging on epoch level in distributed setting.*"
        )

        if self.sharing_strategy is not None:
            torch.multiprocessing.set_sharing_strategy(self.sharing_strategy)

        # Set torch.hub cache
        torch.hub.set_dir(self.torch_hub_cache)

        # Experiment with this during training (high or medium)
        if self.matmul_precision is not None:
            torch.set_float32_matmul_precision(self.matmul_precision)

        # Create trainer dict
        if self.trainer is None:
            self.trainer = {}

        # Flip some arguments in debug mode
        devices = self.trainer.get("devices", 1)

        if self.debug:
            self.slurm = False
            if isinstance(devices, int):
                devices = 1
            elif isinstance(devices, (list, listconfig.ListConfig)):
                devices = [devices[0]]
            self.trainer["devices"] = devices
            self.data.num_workers = 0
            if self.wandb:
                self.wandb = None

        # slurm
        if self.slurm:
            self.trainer["devices"] = int(
                os.environ.get("SLURM_NTASKS_PER_NODE", "auto")
            )
            self.trainer["num_nodes"] = int(os.environ.get("SLURM_NNODES", 1))

        # Create objects
        data_module = FoldEverythingDataModule(self.data)
        model_module = self.model

        if self.pretrained and not self.resume:
            if self.load_affinity_from_trunk:
                checkpoint = torch.load(self.pretrained, map_location="cpu")

                # Modify parameter names in the state_dict
                new_state_dict = {}
                for key, value in checkpoint["state_dict"].items():
                    if not key.startswith("structure_module") and not key.startswith(
                        "distogram_module"
                    ):
                        new_key = "affinity_module." + key
                        new_state_dict[new_key] = value
                new_state_dict.update(checkpoint["state_dict"])

                # Update the checkpoint with the new state_dict
                checkpoint["state_dict"] = new_state_dict

                # Save the modified checkpoint
                random_string = "".join(
                    random.choices(string.ascii_lowercase + string.digits, k=10)
                )
                file_path = (
                    os.path.dirname(self.pretrained) + "/" + random_string + ".ckpt"
                )
                print(
                    f"Saving modified checkpoint to {file_path} created by broadcasting trunk of {self.pretrained} to affinity module."
                )
                torch.save(checkpoint, file_path)
            else:
                file_path = self.pretrained

            print(f"Loading model from {file_path}")
            model_module = type(model_module).load_from_checkpoint(
                file_path, map_location="cpu", strict=False, **(model_module.hparams)
            )

            if self.load_affinity_from_trunk:
                os.remove(file_path)

        # Create checkpoint callback
        callbacks = self.trainer.get("callbacks", [])
        dirpath = f"{self.output}/{self.name}"
        os.makedirs(dirpath, exist_ok=True)

        if not self.disable_checkpoint:
            if self.slurm:
                jobid = os.environ.get("SLURM_JOB_ID", "")
                dirpath = Path(self.output) / jobid
                dirpath.mkdir(parents=True, exist_ok=True)
                print(
                    "Configuring ModelCheckpoint for SLURM to directory: ", str(dirpath)
                )
            mc = ModelCheckpoint(
                monitor=self.checkpoint_monitor_val_group,
                save_top_k=self.save_top_k,
                save_last=True,
                mode=self.metric_mode,
                every_n_epochs=1,
            )
            callbacks.append(mc)

        # Create wandb logger
        loggers = []
        if self.wandb:
            extra = {}
            if self.slurm:
                ckpt_path = (
                    "hpc"
                    if len([f for f in os.listdir(dirpath) if f.startswith("hpc")])
                    else None
                )
                extra = {"resume": "must"} if ckpt_path else {}

            wdb_logger = WandbLogger(
                name=self.name,
                group=self.wandb["group"],
                save_dir=dirpath,
                dir=f".tmp_wandb/{time.time()}",
                project=self.wandb["project"],
                entity=self.wandb["entity"],
                log_model=False,
                id=os.environ.get("SLURM_JOB_ID", None) if self.slurm else None,
                **extra,
            )
            loggers.append(wdb_logger)
            # Save the config to wandb
            # This fails when not on rank0, so just catching
            try:
                config_out = Path(wdb_logger.experiment.dir) / "run.yaml"
                with Path.open(config_out, "w") as f:
                    OmegaConf.save(config, f)
                wdb_logger.experiment.save(str(config_out))
            except Exception:  # noqa: BLE001, S110
                pass

        # Set up trainer
        strategy = "auto"
        if (isinstance(devices, int) and devices > 1) or (
            isinstance(devices, (list, listconfig.ListConfig)) and len(devices) > 1
        ):
            strategy = DDPStrategy(
                find_unused_parameters=self.find_unused_parameters,
                timeout=datetime.timedelta(seconds=self.ddp_timeout_seconds),
            )

        trainer = pl.Trainer(
            default_root_dir=str(dirpath),
            strategy=strategy,
            callbacks=callbacks,
            logger=loggers,
            enable_checkpointing=not self.disable_checkpoint,
            reload_dataloaders_every_n_epochs=1,
            **self.trainer,
        )

        # Run training
        if self.slurm:
            # If we are on SLURM, we need to check if we have a checkpoint for this job
            ckpt_path = (
                "hpc"
                if len([f for f in os.listdir(dirpath) if f.startswith("hpc")])
                else None
            )
            # If none check with we have a resume checkpoint passed in
            if ckpt_path is None:
                ckpt_path = self.resume
        else:
            ckpt_path = self.resume

        if not self.strict_loading:
            model_module.strict_loading = False

        if self.validation_only:
            trainer.validate(
                model_module,
                datamodule=data_module,
                ckpt_path=ckpt_path,
            )
        else:
            trainer.fit(
                model_module,
                datamodule=data_module,
                ckpt_path=ckpt_path,
            )
