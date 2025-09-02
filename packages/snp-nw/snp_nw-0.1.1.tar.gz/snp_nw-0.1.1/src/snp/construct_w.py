import numpy as np
import warnings

def construct_W(x, h):
    """Construct Normalized Gaussian Kernel Weight Matrix"""
    x = np.asarray(x, dtype=float).reshape(-1)
    if np.any(np.isnan(x)):
        raise ValueError("x cannot contain NA values")
    if not (np.isscalar(h) and float(h) > 0.0):
        raise ValueError("h must be a positive scalar")

    dist_mat = x[:, None] - x[None, :]
    K_mat = 0.3989423 * np.exp(-0.5 * (dist_mat / h) ** 2)
    row_sums = K_mat.sum(axis=1, keepdims=True)
    zero_rows = (row_sums == 0.0).ravel()
    if np.any(zero_rows):
        warnings.warn("Some rows have zero sum. This may indicate bandwidth is too small.")
        row_sums[zero_rows, 0] = 1.0
    W = K_mat / row_sums
    return W
