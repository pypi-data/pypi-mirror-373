from __future__ import annotations
from typing import Optional
import numpy as np
import pandas as pd
from .utils import build_lagged_matrix, ridge_solve, ridge_solve_weighted_per_equation

class VAR:
    '''
    Lightweight VAR(p) with optional L2 (ridge) shrinkage

    n_lags : int
    alpha : float
        Shrinkage for all lags
    include_const : bool
        Include an intercept (unpenalized)
    '''
    def __init__(self, n_lags: int, include_const: bool = True, alpha: float = 0.0):
        if n_lags < 1:
            raise ValueError('n_lags must be >= 1')
        if alpha < 0:
            raise ValueError('alpha must be >= 0')
        self.p = n_lags
        self.include_const = include_const
        self.alpha = float(alpha)
        self.columns_: Optional[pd.Index] = None
        self.K_: Optional[int] = None
        self.coef_: Optional[np.ndarray] = None          # (m, K)
        self.resid_cov_: Optional[np.ndarray] = None     # (K, K)
        self.in_sample_fitted_: Optional[pd.DataFrame] = None
        self._last_obs_: Optional[np.ndarray] = None     # (p, K)

    def fit(self, X: pd.DataFrame) -> 'VAR':
        if not isinstance(X, pd.DataFrame):
            raise TypeError('X must be a pandas DataFrame')

        Xv = np.asarray(X.values, dtype=float)
        Y, Z = build_lagged_matrix(Xv, self.p, self.include_const)
        self._last_obs_ = Xv[-self.p:, :].copy()

        B = ridge_solve(Y, Z, alpha=self.alpha, include_const=self.include_const)

        self.columns_ = X.columns
        self.K_ = Xv.shape[1]
        self.coef_ = B

        resid = Y - Z @ B
        N = Y.shape[0]
        dof = max(1, N - Z.shape[1])
        self.resid_cov_ = (resid.T @ resid) / dof

        fitted = Z @ B
        fitted_df = pd.DataFrame(
            np.vstack([np.full((self.p, self.K_), np.nan), fitted]),
            index=X.index, columns=X.columns
        )
        self.in_sample_fitted_ = fitted_df
        return self

    def _forecast_one_step(self, history: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise RuntimeError('Model is not fitted. Call fit() first')
        K = history.shape[1]
        z_parts = [history[-lag, :] for lag in range(1, self.p + 1)]
        z = np.concatenate(z_parts)
        if self.include_const:
            z = np.concatenate([z, np.array([1.0])])
        return z @ self.coef_

    def predict(self, steps: int) -> pd.DataFrame:
        if steps < 1:
            raise ValueError('steps must be >= 1')
        if self._last_obs_ is None:
            raise RuntimeError('Model is not fitted. Call fit() first')

        history = self._last_obs_.copy()
        K = history.shape[1]
        out = np.empty((steps, K), dtype=float)

        for t in range(steps):
            y_hat = self._forecast_one_step(history)
            out[t, :] = y_hat
            history = np.vstack([history[1:, :], y_hat.reshape(1, K)])

        idx = pd.RangeIndex(start=1, stop=steps + 1, name='step')
        return pd.DataFrame(out, index=idx, columns=self.columns_)

    @property
    def intercept_(self) -> Optional[np.ndarray]:
        if self.coef_ is None or not self.include_const:
            return None
        return self.coef_[-1, :]

    def coefficient_matrices(self) -> Optional[np.ndarray]:
        if self.coef_ is None:
            return None
        K = self.K_
        A = np.empty((self.p, K, K), dtype=float)
        for lag in range(self.p):
            block = self.coef_[lag * K:(lag + 1) * K, :]  # (K, K)
            A[lag, :, :] = block.T
        return A

class MinnesotaVAR:
    '''
    Minnesota-style ridge VAR(p) where a zero prior mean is akin to l2 regularization.
    Penalty weights per equation (target i):
        w_{i,j,lag} = (alpha_own if j == i else alpha_cross) * multiplier(lag)
    where multiplier(lag) grows with lag to shrink longer lags more:
        multiplier(lag) = (lag ** power)
    Intercept (if included) is never penalized

    n_lags : int
    alpha_own : float
        Shrinkage for own-variable lags
    alpha_cross : float
        Shrinkage for other-variables' lags
    include_const : bool
        Include an intercept (unpenalized)
    power : float
        Exponent controlling how quickly penalty grows with lag (default 2.0)
    '''

    def __init__(self, n_lags: int, alpha_own: float = 0.0, alpha_cross: float = 0.0, include_const: bool = True, power: float = 2.0):
        if n_lags < 1:
            raise ValueError('n_lags must be >= 1')
        if alpha_own < 0 or alpha_cross < 0:
            raise ValueError('alpha_own and alpha_cross must be >= 0')

        self.p = n_lags
        self.alpha_own = float(alpha_own)
        self.alpha_cross = float(alpha_cross)
        self.include_const = include_const
        self.power = float(power)
        self.columns_: Optional[pd.Index] = None
        self.K_: Optional[int] = None
        self.coef_: Optional[np.ndarray] = None        # (M, K)
        self.resid_cov_: Optional[np.ndarray] = None   # (K, K)
        self.in_sample_fitted_: Optional[pd.DataFrame] = None
        self._last_obs_: Optional[np.ndarray] = None   # (p, K)

    def _lag_multipliers(self) -> np.ndarray:
        raw = np.array([ (lag ** self.power) for lag in range(1, self.p + 1) ], dtype=float)
        return raw

    def _build_weights(self, K: int, M: int) -> list[np.ndarray]:
        '''
        Build per-equation diagonal penalty vectors w_i (length M)
        Column layout in Z: [lag1: K cols][lag2: K cols] ... [lag p: K cols][const]
        '''
        mult = self._lag_multipliers()  # length p
        W_list: list[np.ndarray] = []

        for i in range(K):  # equation index
            w = np.zeros(M, dtype=float)
            for lag in range(1, self.p + 1):
                factor = mult[lag - 1]
                start = (lag - 1) * K
                end = start + K
                for j_col in range(start, end):
                    j = j_col - start
                    w[j_col] = (self.alpha_own if j == i else self.alpha_cross) * factor
            if self.include_const:
                w[-1] = 0.0
            W_list.append(w)

        return W_list

    def fit(self, X: pd.DataFrame) -> 'MinnesotaVAR':
        if not isinstance(X, pd.DataFrame):
            raise TypeError('X must be a pandas DataFrame')

        Xv = np.asarray(X.values, dtype=float)
        Y, Z = build_lagged_matrix(Xv, self.p, self.include_const)
        self._last_obs_ = Xv[-self.p:, :].copy()

        self.columns_ = X.columns
        self.K_ = Xv.shape[1]
        M = Z.shape[1]

        # per-equation diagonal penalties w/Litterman prior-style shrinkage
        W_list = self._build_weights(self.K_, M)
        B = ridge_solve_weighted_per_equation(Y, Z, W_list)
        self.coef_ = B

        resid = Y - Z @ B
        N = Y.shape[0]
        dof = max(1, N - M)
        self.resid_cov_ = (resid.T @ resid) / dof

        fitted = Z @ B
        fitted_df = pd.DataFrame(
            np.vstack([np.full((self.p, self.K_), np.nan), fitted]),
            index=X.index,
            columns=X.columns,
        )
        self.in_sample_fitted_ = fitted_df
        return self

    def _forecast_one_step(self, history: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise RuntimeError('Model is not fitted. Call fit() first')
        K = history.shape[1]
        z_parts = [history[-lag, :] for lag in range(1, self.p + 1)]
        z = np.concatenate(z_parts)
        if self.include_const:
            z = np.concatenate([z, np.array([1.0])])
        return z @ self.coef_

    def predict(self, steps: int) -> pd.DataFrame:
        if steps < 1:
            raise ValueError('steps must be >= 1')
        if self._last_obs_ is None:
            raise RuntimeError('Model is not fitted. Call fit() first')

        history = self._last_obs_.copy()
        K = history.shape[1]
        out = np.empty((steps, K), dtype=float)

        for t in range(steps):
            y_hat = self._forecast_one_step(history)
            out[t, :] = y_hat
            history = np.vstack([history[1:, :], y_hat.reshape(1, K)])

        idx = pd.RangeIndex(start=1, stop=steps + 1, name='step')
        return pd.DataFrame(out, index=idx, columns=self.columns_)

    @property
    def intercept_(self) -> Optional[np.ndarray]:
        if self.coef_ is None or not self.include_const:
            return None
        return self.coef_[-1, :]

    def coefficient_matrices(self) -> Optional[np.ndarray]:
        if self.coef_ is None:
            return None
        K = self.K_
        A = np.empty((self.p, K, K), dtype=float)
        for lag in range(self.p):
            block = self.coef_[lag * K:(lag + 1) * K, :]  # (K, K)
            A[lag, :, :] = block.T
        return A
        