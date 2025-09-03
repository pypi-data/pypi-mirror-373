# foldeverything

## Installation

To install the repo, you may run:  
`pip install .`

To set up the repo for development:  
`pip install -e .[dev]`

## Training

Once you've implemented your new feature, write a new config under configs/ which includes the new objects you designed, and test your implementation using:

`python main.py configs/train/train.yaml --debug`

Once this passes, you can remove the `debug` flag, and run the full training.

## Evaluation 

After or while the model is training, you can evaluate it using the eval script. To use it:

`python eval.py --checkpoint [PATH_TO_CHECKPOINT]`

> Note that the config used for evaluation should be the same as the one used for training.


## Prediction 

When running inference, the files ending with _native.cif contain the structure of your design specification in case you want to double check that your specification worked as desired.


## Contributing

Anyone is welcome to contribute. To do so, you must create a new branch, work on some improvements, and demonstrate improved results for your branch to get merged.
When making a PR, please do your best to follow the syle guideline, specifically:

- Implement the relevant existing interfaces
- Add typing on all function inputs and outputs
- Add Numpy-style docstring to all new objects and functions

When developing, you are *strongly* encouraged to set up `Ruff` and `mypy` in your IDE. These will ensure that
you are respecting the typing and formatting rules, while also helping you avoid potential bugs early on.
