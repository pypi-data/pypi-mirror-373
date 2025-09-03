import numpy as np
from torch.utils.data import Dataset, DataLoader


class RandomDataset(Dataset):
    def __getitem__(self, index):
        rng = np.random.default_rng()
        return rng.random()

    def __len__(self):
        return 16


def main():
    import multiprocessing

    print(multiprocessing.get_start_method())

    dataset = RandomDataset()
    dataloader = DataLoader(dataset, batch_size=1, num_workers=4, shuffle=True)
    for batch in dataloader:
        print(batch)


if __name__ == "__main__":
    main()
