import matplotlib.pyplot as plt
import numpy as np

from .types import EigenTrackingResults


def plot_eigenvalue_trajectories(results: EigenTrackingResults, ax=None):
    """
    追跡された各固有値の軌跡を、パラメータ t の関数としてプロットする。
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        show_plot = True
    else:
        show_plot = False

    if results.Lambdas is not None and results.t_eval is not None:
        eigenvalues_traces = np.array([np.diag(L) for L in results.Lambdas])
        for i in range(eigenvalues_traces.shape[1]):
            ax.plot(results.t_eval, eigenvalues_traces[:, i], label=f"λ_{i+1}(t)")
        ax.set_title("Eigenvalue Trajectories")
        ax.set_xlabel("Parameter t")
        ax.set_xscale("log")
        ax.set_ylabel("Eigenvalues")
        ax.legend()
        ax.grid(True)

    if show_plot:
        plt.show()

    return ax


def plot_reconstruction_error(results: EigenTrackingResults, ax=None):
    """
    再構成誤差 ||A(t) - Q(t)Λ(t)Q(t)^T||_F の時間発展をプロットする。
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        show_plot = True
    else:
        show_plot = False

    if results.norm_errors is not None and results.t_eval is not None:
        ax.semilogy(
            results.t_eval,
            results.norm_errors,
            label="Reconstruction Norm Error",
            color="crimson",
        )
        ax.set_title("Reconstruction Error")
        ax.set_xlabel("Parameter t")
        ax.set_xscale("log")
        ax.set_ylabel(r"$||A(t) - Q(t)\Lambda(t)Q(t)^T||_F$ (log scale)")
        ax.legend()
        ax.grid(True)

    if show_plot:
        plt.show()

    return ax


def plot_tracking_results(results: EigenTrackingResults, axes=None):
    """
    固有値追跡の結果（軌跡、誤差）を一つの図にまとめてプロットする。
    """
    if axes is None:
        _, axes = plt.subplots(1, 2, figsize=(12, 6))
        show_plot = True
    else:
        show_plot = False

    plot_eigenvalue_trajectories(results, ax=axes[0])
    plot_reconstruction_error(results, ax=axes[1])

    plt.tight_layout()

    if show_plot:
        plt.show()

    return axes
