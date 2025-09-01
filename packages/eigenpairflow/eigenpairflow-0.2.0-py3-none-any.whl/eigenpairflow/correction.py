import numpy as np
import scipy.linalg
from scipy.optimize import linear_sum_assignment


def match_decompositions(
    predicted_eigvals, predicted_eigvecs, exact_eigvals, exact_eigvecs
):
    """
    正確な対角化分解を、予測された対角化分解にマッチさせる。

    この関数は、ハンガリー法を用いて固有値の最適な対応付け（並べ替え）を
    見つけ出し、その後、対応する固有ベクトル間の内積を計算して符号を揃える。
    これにより、`eigh`のような関数の出力順序や符号の任意性に起因する不連続性を
    解消し、時間積分の連続性を維持する。

    Args:
        predicted_eigvals (np.ndarray): 1D配列。予測された固有値。
        predicted_eigvecs (np.ndarray): 2D配列。予測された固有ベクトル（列ベクトル）。
        exact_eigvals (np.ndarray): 1D配列。正確に計算された固有値。
        exact_eigvecs (np.ndarray): 2D配列。正確に計算された固有ベクトル（列ベクトル）。

    Returns:
        tuple[np.ndarray, np.ndarray]:
            - matched_eigvals: `predicted_eigvals` の順序に並べ替えられた `exact_eigvals`。
            - matched_eigvecs: `predicted_eigvecs` の順序と符号に合わせられた `exact_eigvecs`。
    """
    # --- ステップ1: 固有値の最適な対応付け（並べ替え）を見つける ---
    # コスト行列を計算する。C[i, j]は i 番目の予測値と j 番目の正確な値の差。
    # このコストを最小化するようなペアリングを見つけることが目的。
    cost_matrix = np.abs(
        predicted_eigvals[:, np.newaxis] - exact_eigvals[np.newaxis, :]
    )

    # ハンガリー法（線形和割り当て問題）を解き、最適なペアリングを見つける
    # pred_indices[i] は、exact_indices[i] に対応する
    pred_indices, exact_indices = linear_sum_assignment(cost_matrix)

    # 並べ替えられた正確な値を格納する配列を準備
    matched_eigvals = np.zeros_like(exact_eigvals)
    matched_eigvecs = np.zeros_like(exact_eigvecs)

    # 見つかった対応付けに従って、正確な値を並べ替える
    # pred_indices は通常 0, 1, 2, ... となるので、exact_indices が置換を表す
    matched_eigvals = exact_eigvals[exact_indices]
    matched_eigvecs = exact_eigvecs[:, exact_indices]

    # --- ステップ2: 対応する固有ベクトルの符号を合わせる ---
    # 各々の対応するベクトル対の内積を計算する
    # 内積が負の場合、ベクトルは反対方向を向いているため、一方の符号を反転させる
    for i in range(predicted_eigvecs.shape[1]):
        dot_product = np.dot(predicted_eigvecs[:, i], matched_eigvecs[:, i])
        if dot_product < 0.0:
            matched_eigvecs[:, i] *= -1.0

    return matched_eigvals, matched_eigvecs


def correct_trajectory(A_func, t_eval, Qs_ode, Lambdas_ode):
    """
    ODEソルバーで追跡した固有値分解を、各時刻で正確に計算した分解に事後補正する。
    ODE結果をガイドとして、正確な分解を並べ替え・符号合わせする。

    Args:
        A_func (callable): 時刻 t を受け取り、真の行列 A(t) を返す関数。
        t_eval (np.ndarray): 評価時刻の1D配列。
        Qs_ode (list of np.ndarray): ODEソルバーから得られた固有ベクトル行列のリスト。
        Lambdas_ode (list of np.ndarray): ODEソルバーから得られた対角固有値行列のリスト。

    Returns:
        tuple[list[np.ndarray], list[np.ndarray]]:
            - corrected_Qs: 補正された固有ベクトル行列のリスト。
            - corrected_Lambdas: 補正された対角固有値行列のリスト。
    """
    corrected_Qs = []
    corrected_Lambdas = []

    for i, t in enumerate(t_eval):
        # 1. その時刻における真の行列 A_t を計算
        A_t = A_func(t)

        # 2. A_t の正確な固有値分解を計算
        exact_eigvals, exact_eigvecs = scipy.linalg.eigh(A_t)

        # 3. match_decompositions を用いて、正確な分解をODE結果にマッチさせる
        # ODE結果を「予測」、正確な計算を「正確」として渡す
        # Lambdas_ode は対角行列なので、固有値を取り出す
        predicted_eigvals = np.diag(Lambdas_ode[i])
        predicted_eigvecs = Qs_ode[i]

        matched_eigvals, matched_eigvecs = match_decompositions(
            predicted_eigvals, predicted_eigvecs, exact_eigvals, exact_eigvecs
        )

        # 4. 補正結果をリストに追加
        corrected_Qs.append(matched_eigvecs)
        corrected_Lambdas.append(np.diag(matched_eigvals))  # 対角行列に戻す

    return corrected_Qs, corrected_Lambdas
