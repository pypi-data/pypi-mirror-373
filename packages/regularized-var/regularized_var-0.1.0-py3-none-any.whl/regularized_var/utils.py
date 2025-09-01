from __future__ import annotations
import numpy as np
from typing import Tuple

def build_lagged_matrix(X: np.ndarray, p: int, include_const: bool) -> Tuple[np.ndarray, np.ndarray]:
    '''
    Build target Y and regressor matrix Z for a VAR(p)
    X: (T, K) array; returns Y: (T-p, K), Z: (T-p, p*K + int(include_const))
    '''
    T, K = X.shape
    if T <= p:
        raise ValueError(f'Need at least n_lags+1 rows. Got T={T}, n_lags={p}')

    rows = T - p
    cols = K * p + (1 if include_const else 0)
    Z = np.empty((rows, cols), dtype=float)

    col = 0
    for lag in range(1, p + 1):
        Z[:, col:col + K] = X[p - lag:T - lag, :]
        col += K

    if include_const:
        Z[:, -1] = 1.0

    Y = X[p:, :]
    return Y, Z


def ridge_solve(Y: np.ndarray, Z: np.ndarray, alpha: float, include_const: bool) -> np.ndarray:
    '''
    Solve B = argmin_B (1/(2n))||Y - ZB||_F^2 + alpha * ||B||_F^2, excluding the intercept column from the penalty if present
    Returns B with shape (m, K), where m = Z.shape[1], K = Y.shape[1]
    '''
    n = Y.shape[0]
    m = Z.shape[1]
    ZZ = (Z.T @ Z) / n
    ZY = (Z.T @ Y) / n

    # penalty mask (no penalty on intercept)
    P = np.eye(m)
    if include_const:
        P[-1, -1] = 0.0

    A = ZZ + (2.0 * alpha) * P  # 2*alpha due to 1/(2n) normalization (comparable to sklearn Ridge implementation)

    jitter = 1e-10 * np.eye(m)
    try:
        return np.linalg.solve(A + jitter, ZY)
    except np.linalg.LinAlgError:
        return np.linalg.pinv(A) @ ZY


def ridge_solve_weighted_per_equation(Y: np.ndarray, Z: np.ndarray, W_list: list[np.ndarray]) -> np.ndarray:
    '''
    Solve K independent weighted ridge problems.
    For equation i (column i of Y):
        minimize (1/(2n)) * ||y_i - Z b||^2 + b' diag(w_i) b

    Y : (N, K)   targets
    Z : (N, M)   design matrix
    W_list : list of length K; each w_i is (M,) penalties for equation i.
        (intercept penalty set to 0 outside this function if Z has a constant)
    '''
    N, K = Y.shape
    M = Z.shape[1]
    if len(W_list) != K:
        raise ValueError('W_list length must equal number of equations K')

    ZZ = (Z.T @ Z) / N
    ZT = Z.T / N
    I = np.eye(M)
    B = np.empty((M, K), dtype=float)

    for i in range(K):
        w = np.asarray(W_list[i], dtype=float).reshape(-1)
        if w.shape[0] != M:
            raise ValueError('Each w_i must have length equal to number of columns in Z')
        D = np.diag(w)
        A = ZZ + 2.0 * D           # 2 comes from 1/(2n) scaling in the loss, consistent with sklearn Ridge implementation
        rhs = (ZT @ Y[:, i])       # zero prior mean; no offset term
        try:
            b_i = np.linalg.solve(A + 1e-10 * I, rhs)
        except np.linalg.LinAlgError:
            b_i = np.linalg.pinv(A) @ rhs
        B[:, i] = b_i

    return B
