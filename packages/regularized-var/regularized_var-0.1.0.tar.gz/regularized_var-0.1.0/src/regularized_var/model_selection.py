from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Iterator, List, Sequence, Tuple, Type, Any

import numpy as np
import pandas as pd
from tqdm import tqdm

MetricFn = Callable[[Any, Any], float]


# ------------------------- Splitter -------------------------

@dataclass
class WalkForward:
    '''
    Rolling walk-forward splitter

    Parameters
    ----------
    train_size : int
        Target number of observations in each training window (fixed-size rolling once reached)
    min_train_size : int
        First split happens when at least this many observations are available
        If min_train_size < train_size, the first splits use expanding windows until train_size is reached
    horizon : int
        Forecast horizon
    step : int
        Step between consecutive splits (default 1 = daily walk)
    '''
    train_size: int
    min_train_size: int
    horizon: int = 1
    step: int = 1

    def splits(self, X: pd.DataFrame | pd.Series | np.ndarray) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        n = len(X) if isinstance(X, (pd.DataFrame, pd.Series)) else np.asarray(X).shape[0]
        if self.train_size <= 0 or self.min_train_size <= 0 or self.horizon <= 0 or self.step <= 0:
            raise ValueError('train_size, min_train_size, horizon, and step must be positive integers.')
        t = self.min_train_size
        while t + self.horizon <= n:
            train_start = max(0, t - self.train_size)
            train_idx = np.arange(train_start, t, dtype=int)
            test_idx = np.arange(t, t + self.horizon, dtype=int)
            if len(train_idx) == 0 or len(test_idx) == 0:
                break
            yield train_idx, test_idx
            t += self.step


# ------------------------- Normalization helper -------------------------

class _TrainOnlyNormalizer:
    '''
    Train-only normalizer that:
      - de-means on the train window
      - scales by train std (ddof=0)
      - inverse_transform *does not* add back the mean by default (readd_mean=False) matching: StandardScaler(with_mean=False) on already de-meaned data

    This avoids assuming that the future baseline mean equals the train mean for cases like asset returns
    '''

    def __init__(self, readd_mean: bool = False, eps: float = 1e-12):
        self.readd_mean = readd_mean
        self.eps = eps
        self.mean_: pd.Series | None = None
        self.scale_: pd.Series | None = None

    def fit(self, X_train: pd.DataFrame) -> '_TrainOnlyNormalizer':
        self.mean_ = X_train.mean(axis=0)
        # std can be zero; guard to avoid divide-by-zero
        std = X_train.std(axis=0, ddof=0).replace(0.0, np.nan)
        self.scale_ = std.fillna(1.0)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.mean_ is None or self.scale_ is None:
            raise RuntimeError('Normalizer not fitted.')
        X_dm = X - self.mean_
        X_sc = X_dm / (self.scale_ + self.eps)
        return X_sc

    def inverse_transform(self, X_scaled: pd.DataFrame) -> pd.DataFrame:
        if self.mean_ is None or self.scale_ is None:
            raise RuntimeError('Normalizer not fitted.')
        X = X_scaled * (self.scale_ + self.eps)
        if self.readd_mean:
            X = X + self.mean_
        return X


# ------------------------- Walk-forward validator -------------------------

class WalkForwardValidator:
    '''
    Walk-forward validation that:
      - re-trains the estimator at each split on the training window
      - de-means + normalizes on the training window only (no leakage)
      - forecasts through the test window, then horizon-collapses (sum across the horizon)
      - inverse-normalizes predictions by re-scaling only (no mean add-back by default)
      - scores on the horizon-collapsed values

    estimator_class :
        Class with API: estimator_class(**params).fit(DataFrame) and .predict(steps)->DataFrame
    params :
        Dict of kwargs passed to estimator_class (e.g., {'n_lags':3, 'alpha':10.0, 'include_const':False})
    splitter :
        WalkForward instance
    metric :
        Callable(y_true, y_pred) -> float (lower is better), e.g., regularized_var.metrics.mse
    readd_mean_on_inverse :
        If True, inverse-normalization will add back the train mean
    aggregate :
        Aggregator over split scores (default: np.mean)
    '''

    def __init__(
        self,
        estimator_class: Type,
        params: Dict[str, Any],
        splitter: WalkForward,
        metric: MetricFn,
        readd_mean_on_inverse: bool = False,
        aggregate: Callable[[Sequence[float]], float] = np.mean,
        verbose: bool = False
    ):
        self.estimator_class = estimator_class
        self.params = params
        self.splitter = splitter
        self.metric = metric
        self.readd_mean_on_inverse = readd_mean_on_inverse
        self.aggregate = aggregate
        self.verbose = verbose
        self.split_scores_: List[float] = []
        self.overall_score_: float | None = None
        self.predictions_h_: List[pd.DataFrame] = []
        self.actuals_h_: List[pd.DataFrame] = []

    def run(self, X: pd.DataFrame) -> 'WalkForwardValidator':
        if not isinstance(X, pd.DataFrame):
            raise TypeError('X must be a pandas DataFrame')

        self.split_scores_.clear()
        self.predictions_h_.clear()
        self.actuals_h_.clear()

        # wrap generator in tqdm if verbose
        splits = self.splitter.splits(X)
        if self.verbose:
            splits = tqdm(list(splits), desc='Walk-forward splits')

        for i, (train_idx, test_idx) in enumerate(splits, start=1):
            X_train = X.iloc[train_idx]
            X_test = X.iloc[test_idx]

            # --- normalize on train only (de-mean + scale) 
            norm = _TrainOnlyNormalizer(readd_mean=self.readd_mean_on_inverse).fit(X_train)
            X_train_n = norm.transform(X_train)
            X_test_n = norm.transform(X_test)

            est = self.estimator_class(**self.params).fit(X_train_n)
            y_pred_n = est.predict(steps=len(X_test_n))

            y_pred_n.index = X_test.index

            # --- horizon actuals in original units
            y_true_h = X_test.sum(axis=0).to_frame().T
            y_true_h.index = X_test.index[-1:]

            # --- horizon predictions: inverse per-step then sum
            y_pred_steps = norm.inverse_transform(y_pred_n)
            y_pred_h = y_pred_steps.sum(axis=0).to_frame().T 
            y_pred_h.index = y_true_h.index

            # --- score errors
            score = float(self.metric(y_true_h, y_pred_h))
            self.split_scores_.append(score)
            self.predictions_h_.append(y_pred_h)
            self.actuals_h_.append(y_true_h)

        self.overall_score_ = float(self.aggregate(self.split_scores_)) if self.split_scores_ else np.nan
        return self

    def concatenated(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        '''
        Returns (pred_h, actual_h) concatenated over all splits,
        indexed by the horizon end-date, with same columns as X
        '''
        if not self.predictions_h_ or not self.actuals_h_:
            return (pd.DataFrame(), pd.DataFrame())
        pred = pd.concat(self.predictions_h_, axis=0).sort_index()
        true = pd.concat(self.actuals_h_, axis=0).sort_index()
        return pred, true
