import pytorch_lightning as pl
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Optional
from torch.utils.data import TensorDataset


class TestModel(pl.LightningModule):
    def __init__(self, lr: float = 0.001):
        super().__init__()
        self.save_hyperparameters()
        self.lr = lr
        self.fc = nn.Linear(10, 1)

    def forward(self, x):
        return self.fc(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = nn.functional.mse_loss(y_hat, y)
        self.log("train_loss", loss)
        middle_lr = self.trainer.optimizers[0].param_groups[0]["lr"]
        print(">>> middle_lr  ", middle_lr)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = nn.functional.mse_loss(y_hat, y)
        self.log("val_loss", loss)
        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer

    def on_load_checkpoint(self, checkpoint):
        for state in checkpoint["optimizer_states"]:
            for group in state["param_groups"]:
                group["lr"] = self.lr


class TestDataModule(pl.LightningDataModule):
    def __init__(self):
        super().__init__()

    def setup(self, stage: Optional[str] = None) -> None:
        self.data = torch.randn(100, 10)
        self.labels = torch.randn(100, 1)

    def train_dataloader(self):
        return DataLoader(TensorDataset(self.data, self.labels), batch_size=10)


model = TestModel(lr=0.00001)
data_module = TestDataModule()
trainer = pl.Trainer(default_root_dir=".", max_epochs=100, devices=1)
trainer.fit(
    model,
    data_module,
    ckpt_path="lightning_logs/version_1/checkpoints/epoch=9-step=20.ckpt",
)
