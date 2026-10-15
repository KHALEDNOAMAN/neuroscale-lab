# Mathematical methods

For an embedding order `m` and delay `τ`, each vector is
`(x_t, x_{t+τ}, ..., x_{t+(m-1)τ})`. Stable sorting maps it to an ordinal pattern. If `p(π)` is the empirical frequency of pattern `π`, permutation entropy is

`H = -Σπ p(π) log p(π)`.

The implementation reports `H / log(m!)` by default, so the finite-sample estimate lies in `[0, 1]` when valid. Ties are resolved by stable sample order. This is deterministic but not tie-invariant; tied data should therefore be interpreted cautiously. Signals shorter than `1 + τ(m−1)` return `NaN` rather than silently producing a biased estimate.

Multiscale permutation entropy coarse-grains a signal at scale `s` by non-overlapping block means, then applies the same estimator. Effective sample size is `floor(n/s)`, so higher scales can become invalid or unstable. The code exposes scales explicitly and does not hide this reduction.

Spectral features use SciPy's Welch estimator with Hann windows, constant detrending, 50% overlap, one-sided density scaling, and trapezoidal integration over fixed delta, theta, alpha, and beta bands. The default requested segment is two seconds, clipped to the available epoch. A one-second epoch therefore has approximately 1 Hz resolution at 250 Hz and only coarse delta-band support. The choices are baseline features, not claims of optimal neurophysiological bands for every task or reference scheme.

Tests currently cover bounds, constants, short signals, invalid parameters, and deterministic scale keys. Trusted-reference cross-checks and sensitivity analysis are not yet run.
