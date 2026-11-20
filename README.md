# Smart Supply Chain Analytics System

A data-quality-aware Decision Support System (DSS) designed to investigate the empirical question:

> **"Does improving supply-chain master-data quality through reconciliation produce measurable improvements in downstream demand forecasting, inventory optimization, and supply planning?"**

---

## 1. Project Overview

In real-world supply chain management, operational enterprise systems often suffer from poor master-data quality: inconsistent entity names, typographical variations, disparate naming conventions, and ambiguous product/supplier identifiers. Traditional analytical pipelines typically train forecasting and planning models directly on un-reconciled data or perform unprincipled ad-hoc cleaning.

This project implements a **rigorous dual-branch experimental framework**:
1. **Raw Data Branch:** Evaluates forecasting and planning on operational transactions joined with noisy, un-reconciled master data (15% controlled master-data variation).
2. **Reconciled Data Branch:** Evaluates the exact same downstream analytical models on data that has undergone algorithmic master-data reconciliation.
3. **Comparative Evaluation:** Measures the concrete delta in forecast errors (MAE, RMSE, MAPE), safety stock levels, stockout risks, and facility transfer recommendations.

---

## 2. Technology Stack

- **Language:** Python 3.11+
- **Numerical & Data Processing:** `pandas` (>=2.2.0), `numpy` (>=1.26.0), `openpyxl` (>=3.1.2)
- **Master Data Matching:** `rapidfuzz` (>=3.6.0)
- **Machine Learning & Metrics:** `scikit-learn` (>=1.4.0), `scipy` (>=1.12.0)
- **Forecasting Models (Candidate Architectures):** `xgboost` (>=2.0.3), `lightgbm` (>=4.3.0)
- **Testing & Verification:** `pytest` (>=8.0.0)
- **Environment Management:** `uv` / standard Python `venv`

---

## 3. Environment Setup & Dependency Installation

### Step 1: Clone or Navigate to the Repository
```bash
cd /path/to/supply-chain-dss
```

### Step 2: Activate the Virtual Environment
A local virtual environment `.venv` using Python 3.11 is included in the project:

```bash
# On macOS / Linux:
source .venv/bin/activate
```

*(Optional: If recreating the environment from scratch)*:
```bash
# Using uv (fastest):
uv venv .venv --python 3.11
source .venv/bin/activate

# Or using standard python:
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Foundation Dependencies
```bash
pip install -r requirements.txt
```
*(Or with `uv`: `uv pip install -r requirements.txt`)*

---

## 4. Current Project Structure

The codebase is organized into modular packages to isolate business logic, configuration, and data tiers:

```
supply-chain-dss/
├── data/                               # Multi-tier data storage
│   ├── original/                       # Immutable source dataset (supply_chain_dataset1.xlsx)
│   ├── master/                         # Canonical master tables & ground-truth mapping
│   ├── raw/                            # Raw master feed & raw branch (15% controlled noise)
│   ├── reconciled/                     # Reconciled master feed & reconciled branch
│   └── processed/                      # Audit reports and verification metrics
│
├── src/                                # Core analytical library
│   ├── __init__.py
│   ├── utils/                          # Centralized configuration & cross-platform paths
│   │   ├── __init__.py
│   │   └── config.py
│   ├── reconciliation/                 # Module 1: Master data reconciliation package
│   │   └── __init__.py
│   ├── forecasting/                    # Module 2: Demand forecasting pipeline
│   │   ├── __init__.py
│   │   ├── forecasting_data.py         # Zero-leakage lags, rolling stats, 80/20 chronological split
│   │   ├── baseline.py                 # Naive lag-1 baseline forecaster
│   │   ├── evaluate.py                 # MAE, RMSE, MAPE, WAPE metric calculations
│   │   └── train_models.py             # Candidate model wrappers (XGBoost, LightGBM, etc.)
│   ├── inventory/                      # Module 3: Inventory optimization (Planned)
│   │   └── __init__.py
│   ├── warehouse/                      # Module 4: Warehouse analysis (Planned)
│   │   └── __init__.py
│   ├── planning/                       # Module 5: Supply planning (Planned)
│   │   └── __init__.py
│   └── comparative/                    # Module 6: Raw vs. Reconciled comparative analysis (Planned)
│       └── __init__.py
│
├── dashboard/                          # Module 7: Analytics dashboard (Planned)
│   └── __init__.py
│
├── tests/                              # Automated test suite
│   ├── __init__.py
│   └── test_foundation.py              # Path resolution, configuration, and import tests
│
├── requirements.txt                    # Pinned, tested project dependencies
├── PROJECT_SPECIFICATION.md            # Foundational project requirements
├── PROJECT_STATUS.md                   # Real-time component tracking
└── README.md                           # This onboarding documentation
```

---

## 5. How to Run Existing Modules

### 1. Run Automated Foundation Tests
To verify that all cross-platform paths resolve, all configuration values load properly, and modules import cleanly:
```bash
pytest tests/test_foundation.py -v
```

### 2. Run the Naive Demand Forecasting Baseline
To inspect the baseline forecasting evaluation on both Raw and Reconciled test periods:
```bash
python -m src.forecasting.baseline
```
*Expected Output:*
- Train Period: `2024-01-01` to `2024-10-18` (80% chronological)
- Test Period: `2024-10-19` to `2024-12-30` (20% chronological)
- Naive Lag-1 Baseline: **MAE: 5.9231**, **RMSE: 7.4760**, **MAPE: 58.30%**, **WAPE: 40.81%**

---

## 6. Current Implementation Status

- **Phase 1: Foundation & Environment Setup:** **Completed**
- **Module 1: Master Data Reconciliation:** **Completed** (555 noisy variants reconciled with 100% recovery against ground truth).
- **Module 2: Demand Forecasting:** **In Progress** (Data pipeline, zero-leakage feature engineering, chronological split, and baseline implemented; model training pending Phase 2).
- **Modules 3–7:** **Planned** (Detailed specifications established in `Project_Specification.md`).
