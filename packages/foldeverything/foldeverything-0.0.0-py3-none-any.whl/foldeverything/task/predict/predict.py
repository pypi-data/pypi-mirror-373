import os
from typing import List, Optional, Type, Union

import pytorch_lightning as pl
from pathlib import Path
import torch
from fsspec.core import url_to_fs
from hydra.utils import get_class
from omegaconf import OmegaConf, listconfig
from pytorch_lightning import LightningModule, Trainer
from pytorch_lightning.core.saving import (
    _load_state,
    load_hparams_from_tags_csv,
    load_hparams_from_yaml,
)
from pytorch_lightning.strategies import DDPStrategy
from pytorch_lightning.utilities.migration import pl_legacy_patch
from pytorch_lightning.utilities.migration.utils import _pl_migrate_checkpoint
from pytorch_lightning.utilities.rank_zero import rank_zero_warn

from foldeverything.task.predict.data_eval import EvalDataModule
from foldeverything.task.predict.writer import (
    DesignWriter,
    FoldEverythingWriter,
    SimpleWriter,
)
from foldeverything.task.task import Task


# Taken from Lightning codebase to handle dynamic EMA loading
def get_filesystem(path, **kwargs):
    fs, _ = url_to_fs(str(path), **kwargs)
    return fs


def pl_load(
    path_or_url,
    map_location=None,
    weights_only=False,
):
    if not isinstance(path_or_url, (str, Path)):
        # any sort of BytesIO or similar
        return torch.load(
            path_or_url,
            map_location=map_location,  # type: ignore[arg-type] # upstream annotation is not correct
            weights_only=weights_only,
        )
    if str(path_or_url).startswith("http"):
        return torch.hub.load_state_dict_from_url(
            str(path_or_url),
            map_location=map_location,  # type: ignore[arg-type]
            weights_only=weights_only,
        )
    fs = get_filesystem(path_or_url)
    with fs.open(path_or_url, "rb") as f:
        return torch.load(
            f,
            map_location=map_location,  # type: ignore[arg-type]
            weights_only=weights_only,
        )


def _load_from_checkpoint(
    cls,
    checkpoint_path,
    map_location="cpu",
    hparams_file=None,
    strict=None,
    use_ema=False,
    **kwargs,
):
    with pl_legacy_patch():
        checkpoint = pl_load(checkpoint_path, map_location=map_location)

    # convert legacy checkpoints to the new format
    checkpoint = _pl_migrate_checkpoint(
        checkpoint,
        checkpoint_path=(
            checkpoint_path if isinstance(checkpoint_path, (str, Path)) else None
        ),
    )

    if hparams_file is not None:
        extension = str(hparams_file).split(".")[-1]
        if extension.lower() == "csv":
            hparams = load_hparams_from_tags_csv(hparams_file)
        elif extension.lower() in ("yml", "yaml"):
            hparams = load_hparams_from_yaml(hparams_file)
        else:
            raise ValueError(".csv, .yml or .yaml is required for `hparams_file`")

        # overwrite hparams by the given file
        checkpoint[cls.CHECKPOINT_HYPER_PARAMS_KEY] = hparams

    # TODO: make this a migration:
    # for past checkpoint need to add the new key
    checkpoint.setdefault(cls.CHECKPOINT_HYPER_PARAMS_KEY, {})
    # override the hparams with values that were passed in
    checkpoint[cls.CHECKPOINT_HYPER_PARAMS_KEY].update(kwargs)

    if issubclass(cls, pl.LightningDataModule):
        return _load_state(cls, checkpoint, **kwargs)
    if issubclass(cls, pl.LightningModule):
        model = _load_state(cls, checkpoint, strict=strict, **kwargs)
        if use_ema and "ema" in checkpoint:
            state_dict = checkpoint["ema"]["ema_weights"]
        else:
            state_dict = checkpoint["state_dict"]
        if not state_dict:
            rank_zero_warn(
                f"The state dict in {checkpoint_path!r} contains no parameters."
            )
            return model

        device = next(
            (t for t in state_dict.values() if isinstance(t, torch.Tensor)),
            torch.tensor(0),
        ).device
        assert isinstance(model, pl.LightningModule)
        return model.to(device)

    raise NotImplementedError(f"Unsupported {cls}")


class Predict(Task):
    """A task to run model inference."""

    def __init__(
        self,
        data: Union[EvalDataModule],
        writer: Union[FoldEverythingWriter, DesignWriter, SimpleWriter],
        cls: str,
        checkpoint: str,
        output: str,
        name: str,
        torch_hub_cache: str,
        recycling_steps: int,
        sampling_steps: int,
        diffusion_samples: int = 1,
        keys_dict_out: Optional[List] = None,
        keys_dict_batch: Optional[List] = None,
        slurm: bool = False,
        matmul_precision: Optional[str] = None,
        trainer: Optional[dict] = None,
        override: Optional[dict] = None,
        debug: bool = False,
        use_ema: bool = False,
        write_manifest: bool = False,
    ) -> None:
        """Initialize the task.

        Parameters
        ----------
        cls : str
            The class name of the
        checkpoint : str
            The path to the model checkpoint.
        output : str
            The path to save the inference results.
        torch_hub_cache : str
            The path to the torch hub cache.
        slurm : bool, optional
            Whether to run on SLURM, by default False
        matmul_precision : Optional[str], optional
            The matmul precision, by default None
        trainer : Optional[dict], optional
            The configuration for the trainer, by default None
        override : Optional[dict], optional
            The override configuration for the model, by default None

        """
        self.data = data
        self.cls = cls
        self.checkpoint = checkpoint
        self.output = output
        self.slurm = slurm
        self.torch_hub_cache = torch_hub_cache
        self.matmul_precision = matmul_precision
        self.trainer = trainer
        self.override = override if override is not None else {}
        self.predict_args = {
            "recycling_steps": recycling_steps,
            "sampling_steps": sampling_steps,
            "diffusion_samples": diffusion_samples,
        }
        if keys_dict_batch is not None:
            self.predict_args["keys_dict_batch"] = keys_dict_batch
        if keys_dict_out is not None:
            self.predict_args["keys_dict_out"] = keys_dict_out
        self.debug = debug
        self.use_ema = use_ema
        self.write_manifest = write_manifest
        self.writer = writer

    def run(self, config: OmegaConf = None, run_prediction=True) -> None:  # noqa: ARG002
        # Set no grad
        torch.set_grad_enabled(False)

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
            if isinstance(devices, int):
                devices = 1
            elif isinstance(devices, (list, listconfig.ListConfig)):
                devices = [devices[0]]
            self.trainer["devices"] = devices
            self.data.num_workers = 0

        # slurm
        if self.slurm:
            self.trainer["devices"] = int(
                os.environ.get("SLURM_NTASKS_PER_NODE", "auto")
            )
            self.trainer["num_nodes"] = int(os.environ.get("SLURM_NNODES", 1))

        # Load model
        model_cls: Type[LightningModule] = get_class(self.cls)
        self.model_module: LightningModule = _load_from_checkpoint(
            model_cls,
            self.checkpoint,
            strict=False,
            use_ema=self.use_ema,
            map_location="cpu",
            predict_args=self.predict_args,
            **self.override,
        )
        self.model_module.eval()

        # Set up trainer
        strategy = "auto"
        if (isinstance(devices, int) and devices > 1) or (
            isinstance(devices, (list, listconfig.ListConfig)) and len(devices) > 1
        ):
            strategy = DDPStrategy()

        self.lightning_trainer = Trainer(
            default_root_dir=self.output,
            strategy=strategy,
            callbacks=[self.writer],
            **self.trainer,
        )

        if run_prediction:
            # Run training
            self.lightning_trainer.predict(
                self.model_module, datamodule=self.data, return_predictions=False
            )
            del self.model_module
