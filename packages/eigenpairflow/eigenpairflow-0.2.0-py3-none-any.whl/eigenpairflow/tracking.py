import numpy as np
import scipy.linalg
import scipy.integrate

from .ode import symmetric_ode_derivative
from .correction import correct_trajectory
from .types import EigenTrackingResults


def _track_symmetric_eigh(A_func, dA_func, t_span, t_eval, rtol, atol):
    """
    (internal) Tracks the eigenvalue decomposition of a symmetric matrix family A(t)
    using an ODE solver for the eigendecomposition (eigh).
    """
    t0 = t_span[0]
    A0 = A_func(t0)
    n = A0.shape[0]

    lambdas0, Q0 = scipy.linalg.eigh(A0)
    sort_indices = np.argsort(lambdas0)
    lambdas0 = lambdas0[sort_indices]
    Q0 = Q0[:, sort_indices]

    y0 = np.concatenate([Q0.flatten(), lambdas0])

    sol = scipy.integrate.solve_ivp(
        symmetric_ode_derivative,
        t_span,
        y0,
        method="DOP853",
        t_eval=t_eval,
        args=(n, dA_func),
        rtol=rtol,
        atol=atol,
        dense_output=True,
    )
    if not sol.success:
        raise RuntimeError(f"Integration failed. {sol.message=}")

    Qs = [sol_y[: n * n].reshape((n, n)) for sol_y in sol.y.T]
    Lambdas = [np.diag(sol_y[n * n :]) for sol_y in sol.y.T]

    return Qs, Lambdas, sol


def eigenpairtrack(
    A_func,
    dA_func,
    t_span,
    t_eval,
    matrix_type="symmetric",
    method="eigh",
    apply_correction=True,
    rtol=1e-13,
    atol=1e-12,
):
    """
    Tracks the eigen-decomposition of a parameter-dependent matrix A(t).

    This high-level interface dispatches to the appropriate solver based on the
    matrix type and desired decomposition method.

    Args:
        A_func (callable): Function that returns matrix A(t) for a given time t.
        dA_func (callable): Function that returns the derivative dA/dt for a given time t.
        t_span (tuple): Time interval for the tracking (t_start, t_end).
        t_eval (np.ndarray): Array of time points to evaluate the results.
        matrix_type (str): The type of the matrix. Currently only "symmetric" is supported.
        method (str): The decomposition method. Currently only "eigh" is supported.
        apply_correction (bool): Whether to apply post-hoc trajectory correction. Defaults to True.
        rtol (float): Relative tolerance for the ODE solver.
        atol (float): Absolute tolerance for the ODE solver.

    Returns:
        EigenTrackingResults: An object containing the results of the tracking and analysis.
    """
    if matrix_type != "symmetric" or method != "eigh":
        raise NotImplementedError(
            f"Tracking for matrix_type='{matrix_type}' and method='{method}' is not yet implemented."
        )

    # --- Dispatch to the appropriate low-level tracker ---
    try:
        Qs, Lambdas, sol = _track_symmetric_eigh(
            A_func, dA_func, t_span, t_eval, rtol=rtol, atol=atol
        )
        success = sol.success
        message = sol.message
    except RuntimeError as e:
        success = False
        message = f"Tracking failed: {e}"
        sol = None

    if not success:
        return EigenTrackingResults(
            t_eval=t_eval,
            Qs=None,
            Lambdas=None,
            norm_errors=None,
            success=success,
            message=message,
        )

    # --- Post-processing (correction and error calculation) ---
    if apply_correction:
        try:
            Qs, Lambdas = correct_trajectory(A_func, sol.t, Qs, Lambdas)
        except Exception as e:
            message += f" | Correction failed: {e}"

    # Calculate the final norm errors
    norm_errors = []
    for i, t in enumerate(sol.t):
        A_t = A_func(t)
        reconstructed_A = Qs[i] @ Lambdas[i] @ Qs[i].T
        error = np.linalg.norm(A_t - reconstructed_A, "fro")
        norm_errors.append(error)

    return EigenTrackingResults(
        t_eval=sol.t,
        Qs=Qs,
        Lambdas=Lambdas,
        norm_errors=norm_errors,
        success=success,
        message=message,
    )
