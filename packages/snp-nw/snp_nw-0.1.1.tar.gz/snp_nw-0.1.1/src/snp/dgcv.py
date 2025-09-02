import time
import numpy as np
from .construct_w import construct_W

def DGCV(x, y, num_h_points=50):
    """Direct Generalized Cross-Validation for Nadaraya–Watson Regression"""
    start_time = time.process_time()
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    x = np.asarray(x, dtype=float).reshape(-1)
    y = np.asarray(y, dtype=float).reshape(-1)
    if np.any(np.isnan(x)) or np.any(np.isnan(y)):
        raise ValueError("x and y cannot contain NA values")

    n = len(x)
    h_s = 1.06 * np.std(x, ddof=1) * n ** (-1/5)
    h_min = 0.001 * h_s
    h_max = 1.0 * h_s
    h_candidates = np.linspace(h_min, h_max, num_h_points)

    yk_list = []
    gcv_h = np.zeros_like(h_candidates)
    for i, h in enumerate(h_candidates):
        W = construct_W(x, h)
        yhat = W @ y
        denom = (1 - np.trace(W) / n) ** 2
        gcv_h[i] = np.inf if denom <= 0 else np.sum((y - yhat) ** 2) / denom
        yk_list.append(yhat)

    idx = int(np.argmin(gcv_h))
    h_opt_gcv = float(h_candidates[idx])
    elapsed = time.process_time() - start_time

    return {
        "y_h_opt": np.asarray(yk_list[idx]).reshape(-1),
        "h_opt_gcv": h_opt_gcv,
        "gcv_h": gcv_h,
        "time_elapsed": float(elapsed),
    }
