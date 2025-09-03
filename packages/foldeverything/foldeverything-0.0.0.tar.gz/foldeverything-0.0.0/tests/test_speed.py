import pickle
import time
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from foldeverything.data.crop.multimer import MultimerCropper
from foldeverything.data.data import MSA, Input, Record, Structure
from foldeverything.data.feature.af3 import AF3Featurizer
from foldeverything.data.mol import get_symmetries
from foldeverything.data.tokenize.af3 import AF3Tokenizer

# Parameters
max_tokens = 384
max_seqs = 2048
training = False
symmetry_path = Path("/storage/casp/symmetry.pkl")
datadir = Path("/storage/casp/processed_new2/rcsb")

# Load symmetries
sym_data = pickle.load(Path(symmetry_path).open("rb"))
symmetries = get_symmetries(sym_data)

# Get a random subset of data
all_structures = sorted((datadir / "targets" / "records").glob("*.json"))
random = np.random.RandomState(42)
random.shuffle(all_structures)
all_structures = all_structures[:100]

# Initialize objects
tokenizer = AF3Tokenizer()
cropper = MultimerCropper(neighborhood_sizes=[40])
featurizer = AF3Featurizer()

dframe = []

for path in tqdm(all_structures):
    # Load record
    record: Record = Record.load(path)

    # Load structure
    start = time.time()
    total_start = start
    structure = Structure.load(datadir / "targets" / "structures" / f"{record.id}.npz")
    structure_time = time.time() - start

    # Load the relevant MSA's
    start = time.time()
    msas = {}
    for chain in record.chains:
        msa_id = chain.msa_id
        if msa_id != -1:
            msa = datadir / "msa" / f"{msa_id}.npz"
            msas[chain.chain_id] = MSA.load(msa)
    msa_time = time.time() - start

    # Create input data
    input_data = Input(structure, msas, {})

    # Tokenize structure
    start = time.time()
    tokenized = tokenizer.tokenize(input_data)
    token_time = time.time() - start

    # Compute crop
    start = time.time()
    tokenized = cropper.crop(
        tokenized,
        max_tokens=max_tokens,
        max_atoms=max_tokens * 9,
        random=np.random,
    )
    crop_time = time.time() - start

    # Compute features
    start = time.time()
    features = featurizer.process(
        tokenized,
        training=training,
        symmetries=symmetries,
        max_tokens=max_tokens if training else None,
        max_atoms=max_tokens * 9 if training else None,
        max_seqs=max_seqs if training else None,
        pad_to_max_seqs=training,
        compute_symmetries=not training,
    )
    feature_time = time.time() - start

    total_time = time.time() - total_start

    averages = {
        "Total": total_time,
        "Structure": structure_time / total_time,
        "MSA": msa_time / total_time,
        "Tokenize": token_time / total_time,
        "Crop": crop_time / total_time,
        "Features": feature_time / total_time,
    }
    dframe.append(averages)

# Compute average times
dframe = pd.DataFrame(dframe)
print("Average times:")
print(dframe.mean(axis=0))

print("Standard deviation:")
print(dframe.std(axis=0))

print("Maximum:")
print(dframe.max(axis=0))

print("Minimum:")
print(dframe.min(axis=0))
