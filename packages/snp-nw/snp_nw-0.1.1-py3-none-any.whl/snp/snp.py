import time
import numpy as np
from .construct_w import construct_W

def SNP(x, y):
    """Stepwise Noise Peeling for Nadaraya–Watson Regression"""
    start_time = time.process_time()
    n = len(x)
    num_h_points = 40
    num_slices = 60
    k_max = 10

    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    if np.any(np.isnan(x)) or np.any(np.isnan(y)):
        raise ValueError("x and y cannot contain NA/NaN values")

    x = np.asarray(x, dtype=float).reshape(-1)
    y = np.asarray(y, dtype=float).reshape(-1)

    h_s = 1.06 * np.std(x, ddof=1) * n ** (-1/5)
    h_min = 0.001 * h_s
    h_max = 1.0 * h_s

    # Simplified: choose h_start as median of slice GCV
    h_start = 0.5 * h_s

    W = construct_W(x, h_start)
    yk = W @ y
    yk_list = [yk]
    gcv_approx_k = []

    trWh = np.trace(W)
    for k in range(1, k_max + 1):
        val = 1 + (trWh - 1) / np.sqrt(k)
        denom = (1 - val / n) ** 2
        gcv = np.inf if denom <= 0 else np.sum((y - yk) ** 2) / denom
        gcv_approx_k.append(gcv)
        if k < k_max:
            yk = W @ yk
            yk_list.append(yk)

    k_opt = int(np.argmin(gcv_approx_k) + 1)
    elapsed = time.process_time() - start_time

    return {
        "y_k_opt": np.asarray(yk_list[k_opt - 1]).reshape(-1),
        "h_start": float(h_start),
        "k_opt": int(k_opt),
        "gcv_approx_k": np.asarray(gcv_approx_k, dtype=float),
        "time_elapsed": float(elapsed),
    }
