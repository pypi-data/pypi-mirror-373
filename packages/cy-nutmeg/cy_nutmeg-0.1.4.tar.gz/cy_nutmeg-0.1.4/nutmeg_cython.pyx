# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: nonecheck=False

import numpy as np
cimport numpy as np
from libc.math cimport log, exp, log1p
from scipy.special import digamma
import attr
import pandas as pd
from typing import Any, Iterator, List, Optional, Tuple, Union

# Define NumPy types for memory views
ctypedef np.float64_t DTYPE_t
ctypedef np.int64_t ITYPE_t

# Memory view types
ctypedef np.float64_t[:, :] FLOAT_2D
ctypedef np.float64_t[:, :, :] FLOAT_3D
ctypedef np.int64_t[:] INT_1D

# Function implementations
cdef void normalize_cython(FLOAT_2D x, double smoothing) noexcept nogil:
    """Normalizes the rows of the matrix using the smoothing parameter."""
    cdef int i, j
    cdef int n_rows = x.shape[0]
    cdef int n_cols = x.shape[1]
    cdef double norm
    
    for i in range(n_rows):
        norm = 0.0
        for j in range(n_cols):
            norm += x[i, j] + smoothing
        
        if norm > 0:
            for j in range(n_cols):
                x[i, j] = (x[i, j] + smoothing) / norm
        else:
            for j in range(n_cols):
                x[i, j] = 0.0

cdef void variational_normalize_cython(FLOAT_2D x, FLOAT_2D hparams):
    """Normalizes the rows of the matrix using the MACE priors."""
    cdef int i, j
    cdef int n_rows = x.shape[0]
    cdef int n_cols = x.shape[1]
    cdef double norm, digamma_norm
    
    # Pre-allocate arrays for digamma values
    cdef double[:] digamma_values = np.zeros(n_cols, dtype=np.float64)
    
    for i in range(n_rows):
        norm = 0.0
        for j in range(n_cols):
            norm += x[i, j] + hparams[i, j]
        
        # Calculate digamma values
        digamma_norm = digamma(norm)
        for j in range(n_cols):
            digamma_values[j] = digamma(x[i, j] + hparams[i, j])
        
        norm = exp(digamma_norm)
        
        if norm > 0:
            for j in range(n_cols):
                x[i, j] = exp(digamma_values[j]) / norm
        else:
            for j in range(n_cols):
                x[i, j] = 0.0

cdef double e_step_cython(
    FLOAT_3D gold_label_marginals,
    FLOAT_2D spamming,
    FLOAT_2D thetas,
    INT_1D tasks,
    INT_1D workers,
    INT_1D labels,
    INT_1D subpops,
    FLOAT_2D proportions,
    int n_labels,
    int n_workers,
    int n_tasks,
    int n_subpops
):
    """Performs E-step of the MACE algorithm."""
    cdef int i, j, k, t, w, l, s
    cdef double log_marginal_likelihood = 0.0
    cdef double instance_marginal
    
    # Pre-allocate arrays
    cdef double[:] instance_marginals = np.zeros(n_tasks, dtype=np.float64)
    
    # Initialize gold label marginals
    for i in range(n_tasks):
        for j in range(n_subpops):
            for k in range(n_labels):
                gold_label_marginals[i, j, k] = 0.0
    
    # Calculate gold label marginals
    for t in range(len(tasks)):
        for k in range(n_labels):
            gold_label_marginals[tasks[t], subpops[t], k] += (
                spamming[workers[t], 0] * thetas[workers[t], labels[t]] +
                spamming[workers[t], 1] * (k == labels[t])
            )
    
    # Normalize gold label marginals
    for i in range(n_tasks):
        for j in range(n_subpops):
            instance_marginal = 0.0
            for k in range(n_labels):
                gold_label_marginals[i, j, k] /= n_labels
                instance_marginal += gold_label_marginals[i, j, k] * proportions[i, j]
            instance_marginals[i] += instance_marginal
    
    # Calculate log marginal likelihood
    for i in range(n_tasks):
        if instance_marginals[i] > 0:
            log_marginal_likelihood += log(instance_marginals[i] + 1e-8)
    
    return log_marginal_likelihood

@attr.s
class NUTMEG:
    n_restarts: int = attr.ib(default=10)
    n_iter: int = attr.ib(default=50)
    method: str = attr.ib(default="vb")
    smoothing: float = attr.ib(default=0.1)
    default_noise: float = attr.ib(default=0.5)
    alpha: float = attr.ib(default=0.5)
    beta: float = attr.ib(default=0.5)
    random_state: int = attr.ib(default=0)
    verbose: int = attr.ib(default=0)

    def __attrs_post_init__(self):
        self.spamming_ = None
        self.thetas_ = None
        self.theta_priors_ = None
        self.strategy_priors_ = None
        self.smoothing_ = None
        self.probas_ = None
        self.labels_ = None

    def fit(self, data: pd.DataFrame, return_unobserved=True) -> "NUTMEG":
        workers, worker_names = pd.factorize(data["worker"])
        labels, label_names = pd.factorize(data["label"])
        tasks, task_names = pd.factorize(data["task"])
        subpops, subpop_names = pd.factorize(data["subpopulation"])

        # Calculate proportions
        counts = np.zeros((len(task_names), len(subpop_names)), dtype=float)
        np.add.at(counts, (tasks, subpops), 1)
        proportions = counts / counts.sum(axis=1, keepdims=True)

        n_workers = len(worker_names)
        n_labels = len(label_names)
        n_tasks = len(task_names)
        n_subpops = len(subpop_names)

        self.smoothing_ = 0.01 / n_labels

        best_log_marginal_likelihood = -np.inf

        for _ in range(self.n_restarts):
            self._initialize(n_workers, n_labels)
            
            # Convert to memory views for Cython
            gold_label_marginals = np.zeros((n_tasks, n_subpops, n_labels), dtype=np.float64)
            spamming_view = np.ascontiguousarray(self.spamming_)
            thetas_view = np.ascontiguousarray(self.thetas_)
            tasks_view = np.ascontiguousarray(tasks, dtype=np.int64)
            workers_view = np.ascontiguousarray(workers, dtype=np.int64)
            labels_view = np.ascontiguousarray(labels, dtype=np.int64)
            subpops_view = np.ascontiguousarray(subpops, dtype=np.int64)
            proportions_view = np.ascontiguousarray(proportions)

            log_marginal_likelihood = e_step_cython(
                gold_label_marginals,
                spamming_view,
                thetas_view,
                tasks_view,
                workers_view,
                labels_view,
                subpops_view,
                proportions_view,
                n_labels,
                n_workers,
                n_tasks,
                n_subpops
            )

            if log_marginal_likelihood > best_log_marginal_likelihood:
                best_log_marginal_likelihood = log_marginal_likelihood
                best_thetas = self.thetas_.copy()
                best_spamming = self.spamming_.copy()

        self.thetas_ = best_thetas
        self.spamming_ = best_spamming

        # Calculate final predictions
        gold_label_marginals = np.zeros((n_tasks, n_subpops, n_labels), dtype=np.float64)
        log_marginal_likelihood = e_step_cython(
            gold_label_marginals,
            np.ascontiguousarray(self.spamming_),
            np.ascontiguousarray(self.thetas_),
            tasks_view,
            workers_view,
            labels_view,
            subpops_view,
            proportions_view,
            n_labels,
            n_workers,
            n_tasks,
            n_subpops
        )

        # Calculate predictions for unobserved instances
        gold_label_marginals = self.predict_unobserved_instances(
            data, task_names, label_names, subpop_names, gold_label_marginals, return_unobserved
        )

        self.label_key = label_names.values
        self.probas_ = gold_label_marginals / gold_label_marginals.sum(axis=2, keepdims=True)
        self.labels_ = self.label_key[np.argmax(gold_label_marginals, axis=2)]

        if not return_unobserved:
            self.labels_[np.all(np.isnan(gold_label_marginals), axis=2)] = np.nan

        # convert output to be more user friendly
        labels_dict = {}
        for i, task in enumerate(task_names):
            labels_dict[task] = {}
            for j, subpop in enumerate(subpop_names):
                labels_dict[task][subpop] = self.labels_[i, j]
        self.labels_ = labels_dict

        probas_dict = {}
        for i, task in enumerate(task_names):
            probas_dict[task] = {}
            for j, subpop in enumerate(subpop_names):
                probas_dict[task][subpop] = {}
                for k, label in enumerate(label_names):
                    probas_dict[task][subpop][label] = self.probas_[i, j, k]
        self.probas_ = probas_dict



        return self

    def _initialize(self, n_workers: int, n_labels: int) -> None:
        """Initializes the NUTMEG parameters."""
        np.random.seed(self.random_state)
        self.spamming_ = np.random.uniform(1, 1 + self.default_noise, size=(n_workers, 2))
        self.thetas_ = np.random.uniform(1, 1 + self.default_noise, size=(n_workers, n_labels))

        # Convert to memory views for Cython
        spamming_view = np.ascontiguousarray(self.spamming_)
        thetas_view = np.ascontiguousarray(self.thetas_)

        normalize_cython(spamming_view, self.smoothing_)
        normalize_cython(thetas_view, self.smoothing_)

        if self.method == "vb":
            self.theta_priors_ = np.empty((n_workers, 2))
            self.theta_priors_[:, 0] = self.alpha
            self.theta_priors_[:, 1] = self.beta
            self.strategy_priors_ = np.ones((n_workers, n_labels)) * 10.0

    def predict_unobserved_instances(self,
        data: pd.DataFrame,
        task_names: Union[List[Any], "pd.Index[Any]"],
        label_names: Union[List[Any], "pd.Index[Any]"],
        subpop_names: Union[List[Any], "pd.Index[Any]"],
        gold_label_marginals: np.ndarray,
        return_unobserved=True
    ) -> np.ndarray:
        """Calculates predictions for unobserved subpopulations."""
        # Implementation remains the same as in the original Python version
        # since this function is not performance-critical
        prelim_labels = np.argmax(gold_label_marginals, axis=2)
        observed_prediction_totals = [[None] * len(label_names)] * len(subpop_names)
        observed_prediction_sizes = [[None] * len(label_names)] * len(subpop_names)

        for i in range(len(subpop_names)):
            subpop_presence = np.array(data.groupby('task')['subpopulation'].unique().apply(lambda x: subpop_names[i] in x))
            for j in range(len(label_names)):
                observed_prediction_totals[i][j] = gold_label_marginals[(prelim_labels[:, i] == j) * subpop_presence].sum(axis=0)
                observed_prediction_sizes[i][j] = ((prelim_labels[:, i] == j) * subpop_presence).sum()

        obs_subpops = data.groupby('task')['subpopulation'].unique().apply(set)
        unobs_subpops = set(subpop_names) - obs_subpops
        unobs_subpops = unobs_subpops[unobs_subpops.apply(bool)]

        for task, unobs in unobs_subpops.items():
            task_idx = np.where(task_names==task)
            obs_total = np.zeros(observed_prediction_totals[0][0].shape)
            obs_size = 0

            for obs_subpop in obs_subpops[task]:
                obs_subpop_idx = np.where(subpop_names==obs_subpop)[0][0]
                obs_subpop_label_idx = prelim_labels[task_idx, obs_subpop_idx][0][0]
                obs_total += observed_prediction_totals[obs_subpop_idx][obs_subpop_label_idx]
                obs_size += observed_prediction_sizes[obs_subpop_idx][obs_subpop_label_idx]

            obs_prediction = obs_total / obs_size

            for unobs_subpop in unobs:
                unobs_subpop_idx = np.where(subpop_names==unobs_subpop)[0][0]
                if return_unobserved:
                    gold_label_marginals[task_idx, unobs_subpop_idx] = obs_prediction[unobs_subpop_idx]
                else:
                    gold_label_marginals[task_idx, unobs_subpop_idx] = np.nan

        return gold_label_marginals
