# SNP-Python

Python port of the **Stepwise Noise Peeling (SNP)** algorithm for Nadaraya–Watson regression.

Quick start:

```python
import numpy as np
from snp import SNP, DGCV

np.random.seed(123)
n = 1000
x = np.sort(np.random.rand(n))
y = np.sin(2*np.pi*x) + np.random.normal(0, 0.1, size=n)

snp_res = SNP(x, y)
dgcv_res = DGCV(x, y)

print("SNP:", snp_res["k_opt"], snp_res["h_start"])
print("DGCV:", dgcv_res["h_opt_gcv"])
```
