# NUTMEG: Separating Signal From Noise in Annotator Disagreement
This repository contains the code related to the paper:

> Jonathan Ivey, Susan Gauch, and David Jurgens. 2025. NUTMEG: Separating Signal From Noise in Annotator Disagreement. *arXiv preprint*. ArXiv:2507.18890 [cs].

In this paper, we introduce **NUTMEG**, a tool to model annotator competence in subjective tasks. It reduces noise from unreliable annotators while retaining disagreement between user-specified subpopulations. This repository contains the code for an optimized implementation of NUTMEG that is ideal if you're just looking to use the model. If you want to replicate the experiments from the paper or you want a plain Python implementation, see the [original repository](https://github.com/jonathanivey/NUTMEG).


## Key Featuress

1. **Estimates different truth values for different groups** of annotators (i.e., subpopulations).
2. **Allows practitioners to decide the groupings**, so you can select which groups are relevant to your use case (e.g., you may expect different true values from Android users and iPhone users), or you can combine NUTMEG with unsupervised methods to cluster based on annotator behavior (as explained in the paper).

3. **Provides detailed outputs**, including the estimated truth label and probabilities of all truth labels for each item and the estimated competence for each annotator, so NUTMEG fits in many use cases (whether that's building an entire multi-task model or just filtering out low-quality annotators).

4. **Runs quickly**. In our tests, the Cython implementation takes an average of 3.4 seconds to estimate truths for a dataset with 10K items, so you can easily evaluate and iterate on your pipeline without waiting days for models to finish.

## Quick Start
### 1. Install the package
```sh
pip install nutmeg-cython
```

### 2. Format your input data

```python

# Example of the format for input data
df = pd.DataFrame({
    'task': ['T_1', 'T_1', 'T_1', 'T_1', 'T_2', 'T_2', 'T_2'],
    'worker': ['W_1', 'W_2', 'W_3', 'W_4', 'W_1', 'W_2', 'W_3'],
    'subpopulation': ['S_2', 'S_1', 'S_1', 'S_1', 'S_1', 'S_1', 'S_1'],
    'label': [0, 0, 1, 1, 0, 0, 0]
})
```

### 3. Import and fit the model
```python
from nutmeg.nutmeg_cython import NUTMEG

# Instantiate NUTMEG
nutmeg = NUTMEG()

# Fit to our data
nutmeg.fit(df)
```

### 4. Access the results

```python
nutmeg.labels_      # Predicted labels
nutmeg.probas_      # Predicted label probabilities
nutmeg.spamming_    # Annotator competence
```

## Input Data Format

Your input DataFrame must contain the following columns:

- `task`: Identifier for the item being annotated
- `worker`: Annotator ID
- `subpopulation`: Annotator's group/subpopulation
- `label`: Annotator's label for the item

Each row represents a single annotation.

## Parameters

When instantiating [`NUTMEG`](NUTMEG/nutmeg.py), you can specify:

- `n_restarts`: Number of optimization runs
- `n_iter`: Maximum iterations per run
- `smoothing`: Smoothing parameter for normalization
- `default_noise`: Default noise for initialization
- `alpha`, `beta`: Beta prior parameters for competence
- `random_state`: Random seed
- `verbose`: Progress bar verbosity (0, 1, or 2)

## Outputs

- `.labels_`: Predicted labels for each item/subpopulation
- `.probas_`: Predicted label probabilities
- `.spamming_`: Annotator competence and spamming rates


Note that the plain Python implementation of NUTMEG has a slightly different output format to simplify the reproducibility of the results.

## Reference

If you use NUTMEG in your research, please cite:
```
misc{ivey2025nutmegseparatingsignalnoise,
      title={NUTMEG: Separating Signal From Noise in Annotator Disagreement}, 
      author={Jonathan Ivey and Susan Gauch and David Jurgens},
      year={2025},
      eprint={2507.18890},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2507.18890}, 
}
```