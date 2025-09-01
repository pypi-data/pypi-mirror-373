import numpy as np


def solve_symmetric_ode_system_linsolve(Lambda, F):
    """
    実対称行列の発展方程式 F = dLambda + [H, Lambda] を、
    H と dLambda の独立成分に関する連立一次方程式として厳密に解く。

    Args:
        Lambda (np.ndarray): n x n の対角固有値行列。
        F (np.ndarray): n x n の対称行列 (Q^T * dA * Q)。

    Returns:
        tuple[np.ndarray, np.ndarray]: (H, dLambda_diag) のタプル。
                                       H は歪対称行列。
                                       dLambda_diag は固有値の変化率（対角成分のみのベクトル）。
    """
    n = Lambda.shape[0]

    # 1. 未知数の数を定義
    num_h_unknowns = n * (n - 1) // 2
    num_dlambda_unknowns = n
    total_unknowns = num_h_unknowns + num_dlambda_unknowns

    # 2. 連立一次方程式 M*x = b を構成
    M = np.zeros((total_unknowns, total_unknowns))
    b = np.zeros(total_unknowns)

    lambdas = np.diag(Lambda)

    # Numpyのインデックス機能を使い、手動ループを避ける
    # eq_indices は上三角部分(対角含む)のインデックス (r, c) r<=c
    # h_indices は厳密に上三角部分のインデックス (r, c) r<c
    eq_indices_r, eq_indices_c = np.triu_indices(n)
    h_indices_r, h_indices_c = np.triu_indices(n, k=1)

    # b ベクトルを構成 (Fの上三角成分)
    b[:num_dlambda_unknowns] = np.diag(F)  # 対角成分 (n個)
    b[num_dlambda_unknowns:] = F[h_indices_r, h_indices_c]  # 非対角成分 (n(n-1)/2個)

    # 係数行列 M を構成 (Mは対角行列になる)
    # dLambdaに対応するブロック (係数は常に1)
    M_diag = np.ones(total_unknowns)

    # Hに対応するブロック (係数は lambda_j - lambda_i)
    lambda_diffs = lambdas[h_indices_c] - lambdas[h_indices_r]
    M_diag[num_dlambda_unknowns:] = lambda_diffs

    np.fill_diagonal(M, M_diag)

    # 3. 連立一次方程式を解く
    # lstsq は悪条件（固有値の接近）に対して頑健
    # x, residuals, rank, s = np.linalg.lstsq(M, b, rcond=None)
    x = np.linalg.lstsq(M, b, rcond=None)[0]

    # 4. 解ベクトル x を H と dLambda に再構成
    dLambda_diag = x[:num_dlambda_unknowns]
    H_upper_vals = x[num_dlambda_unknowns:]

    H = np.zeros((n, n))
    H[h_indices_r, h_indices_c] = H_upper_vals
    H[h_indices_c, h_indices_r] = -H_upper_vals

    return H, dLambda_diag


def symmetric_ode_derivative(t, y, n, dA_func):
    """
    solve_ivp に渡すための微分方程式の右辺 f(t, y) を定義する。
    y は [Q.flatten(), diag(Lambda)] を連結したベクトル。
    """
    # 1. 状態ベクトルを行列 Q と対角行列 Lambda に復元
    Q = y[: n * n].reshape((n, n))
    lambdas = y[n * n :]
    Lambda = np.diag(lambdas)

    # 2. dA/dt と F を計算
    dA = dA_func(t)
    F = Q.T @ dA @ Q

    # 3. H と dLambda を計算
    H, dLambda_diag = solve_symmetric_ode_system_linsolve(Lambda, F)

    # 4. dQ/dt を計算
    dQ = Q @ H

    # 5. 結果を平坦化して単一のベクトルとして返す
    dydt = np.concatenate([dQ.flatten(), dLambda_diag])
    return dydt
