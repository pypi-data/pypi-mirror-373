# Changelog

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
