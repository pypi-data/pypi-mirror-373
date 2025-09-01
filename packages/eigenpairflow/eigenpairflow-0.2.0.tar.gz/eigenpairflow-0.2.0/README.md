# EigenpairFlow
<img src="https://github.com/t-uda/eigenpairflow/raw/main/eigenpairflow-logo.png" alt="eigenpairflow-logo" width="256" />

[![CI](https://github.com/t-uda/EigenpairFlow/actions/workflows/ci.yml/badge.svg)](https://github.com/t-uda/EigenpairFlow/actions/workflows/ci.yml)

Continuous and stable tracking of eigendecomposition for parameter-dependent matrices.

## Installation

Install from PyPI:

```bash
pip install eigenpairflow
```

## Usage

Here is a minimal example of tracking the eigenpairs of a parameter-dependent matrix `A(t)`.

First, define the matrix-valued function `A(t)` and its derivative `dA(t)/dt`.

```python
import numpy as np
from eigenpairflow import eigenpairtrack

# Define a matrix function A(t)
def A_func(t):
  return np.array([[3 + np.cos(t), np.sin(t)], [np.sin(t), 3 - np.cos(t)]])

def dA_func(t):
  return np.array([[-np.sin(t), np.cos(t)], [np.cos(t), np.sin(t)]])
```

Then, call `eigenpairtrack` to solve the tracking problem over a given time interval.

```python
# Set the time interval and evaluation points
t_start, t_end = 0.0, 3.0
t_eval = np.linspace(t_start, t_end, 10)

# Track the eigenpairs
result = eigenpairtrack(A_func, dA_func, (t_start, t_end), t_eval)

# The results object contains the tracked eigenvalues (result.Lambdas)
# and eigenvectors (result.Qs) at each time point in t_eval.
print(result)
```

```
EigenTrackingResults Summary:
success: True
message: The solver successfully reached the end of the integration interval.
  t_eval: np.ndarray with shape (10,)
  Qs: list of 10 np.ndarray(s), first shape: (2, 2)
  Lambdas: list of 10 np.ndarray(s), first shape: (2, 2)
```

For more detailed examples, please see the [demonstration notebooks](https://github.com/t-uda/EigenpairFlow/blob/main/notebooks/toy_model_demonstration.ipynb).

## Supported Versions

This project is continuously tested against the following versions to ensure compatibility.

The project's dependencies are managed by Poetry, which resolves the most suitable NumPy v1.x version for each Python interpreter. Forward-compatibility with NumPy v2.x is also explicitly tested on newer Python versions.

| Python Version | Tested NumPy Series |
| :------------: | :-----------------: |
| 3.9            | 1.x                 |
| 3.10           | 1.x                 |
| 3.11           | 1.x & 2.x           |
| 3.12           | 1.x & 2.x           |
