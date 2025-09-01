from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Union

ArrayLike = Union[np.ndarray, pd.Series, pd.DataFrame]

def _to_numpy(a: ArrayLike) -> np.ndarray:
    return a.values if isinstance(a, (pd.Series, pd.DataFrame)) else np.asarray(a)

def mse(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    yt, yp = _to_numpy(y_true), _to_numpy(y_pred)
    return float(np.mean((yt - yp) ** 2))

def mae(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    yt, yp = _to_numpy(y_true), _to_numpy(y_pred)
    return float(np.mean(np.abs(yt - yp)))

def pseudo_r2(y_true: ArrayLike, y_pred: ArrayLike, y_base: ArrayLike | None = None) -> float:
    yt, yp = _to_numpy(y_true), _to_numpy(y_pred)
    if y_base is None:
        yb = np.zeros_like(yt)
    else:
        yb = _to_numpy(y_base)

    sse_model = np.sum((yt - yp) ** 2)
    sse_base  = np.sum((yt - yb) ** 2)

    return float(1.0 - sse_model / sse_base) if sse_base > 0 else float('nan')
