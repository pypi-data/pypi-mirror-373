# regularized-var

Vector Autoregression (VAR) with l2 regularization, optional Minnesota prior, error metrics, and walk-forward validation.

## Install
```bash
pip install regularized-var
```

## Quickstart

```python
import pandas as pd
from regularized_var import VAR, MinnesotaVAR, mse, WalkForward, WalkForwardValidator

# Data
df = pd.DataFrame(...)

# VAR
model = VAR(n_lags=2, alpha=0.1).fit(df)
print(model.predict(steps=5))

# MinnesotaVAR
mvar = MinnesotaVAR(n_lags=3, alpha_own=1.0, alpha_cross=2.0).fit(df)
print(mvar.predict(steps=3))

# Walk-forward validation
splitter = WalkForward(train_size=1000, min_train_size=500, horizon=5)
wf = WalkForwardValidator(VAR, {"n_lags": 2, "alpha": 0.1}, splitter, metric=mse)
wf.run(df)
print(wf.overall_score_)
```

## Mathematical Formulation

### Ridge-regularized VAR
The baseline `VAR` class solves a ridge-penalized least squares problem:

![Equation 0](images/equation0.jpg)

where Y are the responses, Z is the lagged design matrix,
and the intercept (if present) is excluded from the penalty.

This is equivalent to multivariate ridge regression (scikit-learn’s `Ridge`) applied equation-by-equation, but solved in closed form for all equations at once.

### MinnesotaVAR as Weighted Ridge
The *Minnesota prior* (see [Litterman, 1986: "Forecasting with Bayesian Vector Autoregressions — Five Years of Experience"](https://www.minneapolisfed.org/research/sr/sr115.pdf)) is a Bayesian shrinkage approach that imposes beliefs about how coefficients in a VAR should behave:

- Own-lag coefficients are shrunk toward 0 (for stationary/differenced data: growth rates, returns, etc.)
- Cross-lag coefficients (other variables) are shrunk more heavily toward 0
- Higher lags are shrunk more strongly than shorter lags

In practice, this leads to a **ridge-style penalty** on the coefficient matrix:

![Equation 1](images/equation1.jpg)

with weights

![Equation 2](images/equation2.jpg)

- \(i\): target equation index  
- \(j\): predictor variable index  
- \(l\): lag index  

This weighted ℓ₂ penalty reproduces a structure similar to the **Minnesota prior**, where:
- own lags are shrunk mildly,
- cross-variable lags are shrunk more heavily,
- higher-order lags are shrunk progressively more.

Thus, `MinnesotaVAR` can be seen as a **structured ridge regression** equivalent of the Minnesota Bayesian prior.
