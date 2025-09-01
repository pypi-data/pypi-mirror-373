# Quality Data Extractor (QDE)

[![PyPI](https://img.shields.io/pypi/v/qde.svg)](https://pypi.org/project/qde/)
[![Python Versions](https://img.shields.io/pypi/pyversions/qde.svg)](https://pypi.org/project/qde/)
[![License](https://img.shields.io/pypi/l/qde.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.1109/ACCESS.2025.3603435-blue)](https://doi.org/10.1109/ACCESS.2025.3603435)

**QDE (Quality Data Extractor)** is a Python framework for **post-generation filtration of synthetic data**.  

It introduces two filtering strategies:

- **CES (Comprehensive Extraction Strategy)**
- **OES (Optimal Extraction Strategy)**

These strategies help researchers and practitioners filter synthetic datasets to retain samples that improve downstream model accuracy.

📄 Published in *IEEE Access* (2025):  
[Sachdeva, P., Malhotra, A., & Gupta, K. — *Quality Data Extractor (QDE): Elevating Synthetic Data Augmentation through Post-Generation Filtration*](https://doi.org/10.1109/ACCESS.2025.3603435)

---

## 🚀 Installation

From **PyPI**:

```bash
pip install qde
```

---

## 🔧 Quick Start

```python
import qde
from qde import QDE
from sklearn.naive_bayes import GaussianNB
from sklearn.datasets import load_iris
import numpy as np

# Example: use Iris dataset
X, y = load_iris(return_X_y=True)
train_X, train_y = X[:80], y[:80]
synth_X, synth_y = X[80:110], y[80:110]   # pretend this is synthetic
test_X,  test_y  = X[110:], y[110:]

# Initialize QDE with CES
q = QDE(default_strategy="ces")
q.fit(train_X, train_y, synth_X, synth_y, test_X, test_y, encode_labels=True)

# Extract filtered synthetic samples
result, X_sel, y_sel = q.extract(estimator=GaussianNB())
print("Selected indices:", result.indices)
print("Filtered accuracy:", result.meta["filtered-accuracy"])
```
---
## 🖥️ Command-Line Interface (CLI)

QDE also ships a CLI:

```bash
qde strategies
# -> ces
# -> oes

qde run --train train.csv --synth synth.csv --test test.csv --target target --strategy ces

```
---
## 📖 Documentation

- **CES**  
  Adds synthetic samples one by one, retaining only those that do not reduce baseline accuracy.

- **OES**  
  Selects samples using distance-based neighborhood filtering (configurable with `--k-neighbors` and `--distance-mode`).

#### ✅ Each run outputs

- `SelectionResult.indices` → indices of accepted synthetic samples  
- `meta` → metadata (strategy, accuracy metrics, etc.)

## 🛠️ Development

Clone the repo and install in editable mode:

``` bash
git clone https://github.com/pragatischdv/quality-data-extractor
cd quality-data-extractor
pip install -e .
```

## 📄 Citation

If you use QDE in your research, please cite:

```
@ARTICLE{11142788,
  author={Sachdeva, Pragati and Malhotra, Amarjit and Gupta, Karan},
  journal={IEEE Access}, 
  title={Quality Data Extractor (QDE): Elevating Synthetic Data Augmentation through Post-Generation Filtration}, 
  year={2025},
  doi={10.1109/ACCESS.2025.3603435}}
```


