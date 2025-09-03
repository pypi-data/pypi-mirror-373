# numpy-lite

**Ultra-light minimal NumPy 1.26.4 build** focused on core functionality only.  

This fork is designed for **AWS Lambda / serverless environments** with Python 3.12, removing heavy modules like BLAS, LAPACK, linalg, fft, polynomial, random, and f2py to reduce package size.

## Features

- Core array operations (`np.array`, `np.sum`, `np.mean`, indexing, slicing)
- Minimal footprint (~8MB)
- AWS Lambda / serverless ready
- Stub modules provide informative errors if removed modules are imported

## Installation

### Install via PYPI (recommended)

The easiest way to install:
```
pip install numpy-lite
```
###Install from GitHub (for development or contributions)

Clone or download the repository:

```bash
git clone https://github.com/JacquieAM/numpy-lite.git
cd numpy-lite
```

Install via pip:

```
pip install .
rm -rf build
```

Usage
```
import numpy as np

arr = np.array([1, 2, 3])
print(arr)
print(np.sum(arr))
```

Modules like np.linalg, np.fft, and np.random will raise informative ImportError if used.