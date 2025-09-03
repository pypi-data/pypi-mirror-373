import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from pytorch_lightning import Trainer, LightningModule


class Dataset(torch.utils.data.Dataset):
    def __init__(self):
        self.data = torch.randn(100, 10)
        self.labels = torch.randn(100, 10)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]


class Model(LightningModule):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 10)

    def forward(self, x):
        return self.fc(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = nn.functional.mse_loss(y_hat, y)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=0.01)


def main():
    train_dataset = Dataset()
    train_dataloader = DataLoader(train_dataset, batch_size=10)

    model = Model()
    model.cuda()
    trainer = Trainer(devices=8, accelerator="gpu", strategy="ddp_fork", max_epochs=2)
    trainer.fit(model, train_dataloader)

    print("hello")

    model2 = Model()
    model2.cuda()
    trainer2 = Trainer(devices=8, accelerator="gpu", strategy="ddp_fork", max_epochs=2)
    trainer2.fit(model2, train_dataloader)


if __name__ == "__main__":
    main()
