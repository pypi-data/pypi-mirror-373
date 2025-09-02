# Changelog

## [0.1.1] - 2025-09-01
### Changed
- Public API: stop re-exporting symbols at the package root. 
  Import explicitly from submodules:
  - `from regularized_var.var import VAR, MinnesotaVAR`
  - `from regularized_var.metrics import mse, mae, pseudo_r2`
  - `from regularized_var.model_selection import WalkForward, WalkForwardValidator`
- README: badges added; Minnesota prior hyperlinks fixed; equations switched to image links
  (PyPI-friendly)

### Notes
- This is a small breaking change for users who previously did `from regularized_var import VAR`.  
  Use the submodule imports above.

## [0.1.0] - 2025-08-31
### Added
- **Core Models**
  - `VAR`: Vector Autoregression with optional ridge (L2) parameter shrinkage
  - `MinnesotaVAR`: Minnesota-style VAR with own-variable vs. cross-variable shrinkage weights, and shrinkage strength by lag number

- **Utilities**
  - `build_lagged_matrix`: construct design and target matrices for VAR(p)
  - `ridge_solve`: ridge regression solver
  - `ridge_solve_weighted_per_equation`: per-equation weighted ridge solver

- **Metrics**
  - `mse`, `mae`, `pseudo_r2`.

- **Model Selection**
  - `WalkForward`: rolling/expanding window train-test splitter
  - `WalkForwardValidator`: walk-forward evaluation with normalization and scoring
