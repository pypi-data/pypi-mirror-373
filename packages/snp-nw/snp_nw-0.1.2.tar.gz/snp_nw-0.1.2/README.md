# SNP-Python: Stepwise Noise Peeling for Nadaraya–Watson Regression

The **SNP-Python** package implements the Stepwise Noise Peeling algorithm for efficient bandwidth selection in Nadaraya–Watson regression with Gaussian kernels. SNP provides a scalable alternative to Direct Generalized Cross-Validation (DGCV) by converting continuous bandwidth optimization into discrete iteration selection.

## Installation

Install from PyPI (recommended):

```bash
pip install snp-nw
```

Or install the latest development version from GitHub:

```bash
pip install git+https://github.com/bistoonh/SNP-Python.git
```

## Quick Start

```python
import numpy as np
import matplotlib.pyplot as plt
from snp import SNP, DGCV

# Generate sample data
np.random.seed(123)
n = 2000
x = np.sort(np.random.rand(n))
y = np.sin(2*np.pi*x) + np.random.normal(0, 0.1, size=n)

# Apply SNP smoothing
snp_result = SNP(x, y)

# Compare with DGCV
dgcv_result = DGCV(x, y)

# Print performance comparison
print("SNP:  h_start=%.4f, k_opt=%d, time=%.4fs" %
      (snp_result["h_start"], snp_result["k_opt"], snp_result["time_elapsed"]))
print("DGCV: h_opt=%.4f, time=%.4fs" %
      (dgcv_result["h_opt_gcv"], dgcv_result["time_elapsed"]))

# Plot results
plt.scatter(x, y, s=8, c="gray", label="Data")
plt.plot(x, snp_result["y_k_opt"], c="red", lw=2, label="SNP")
plt.plot(x, dgcv_result["y_h_opt"], c="blue", lw=2, label="DGCV")
plt.legend()
plt.title("SNP vs DGCV Comparison")
plt.show()
```

## Key Features

- ⚡ **Fast**: Orders of magnitude faster than DGCV for large datasets  
- 📊 **Accurate**: Statistically equivalent results to DGCV  
- 🎯 **Adaptive**: Automatically adjusts bandwidth through iterative process  
- 🔧 **Robust**: Handles edge cases and various data sizes  
- 📖 **Well-documented**: Comprehensive help files and examples  

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Issues

Found a bug? Have a feature request? Please [open an issue](https://github.com/bistoonh/SNP-Python/issues) on GitHub.
