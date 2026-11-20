"""
config.py
---------
Centralized configuration module for the Smart Supply Chain Analytics System.
Defines dynamic cross-platform paths, reconciliation parameters, random seeds,
and forecasting configuration placeholders.
"""

from pathlib import Path
from typing import Dict, List, Any

# ==============================================================================
# 1. DYNAMIC REPOSITORY & DIRECTORY PATHS
# ==============================================================================
# Resolves root dynamically: file is at <PROJECT_ROOT>/src/utils/config.py
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

# Data storage tiers
DATA_DIR: Path = PROJECT_ROOT / "data"
ORIGINAL_DATA_DIR: Path = DATA_DIR / "original"
MASTER_DATA_DIR: Path = DATA_DIR / "master"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
RECONCILED_DATA_DIR: Path = DATA_DIR / "reconciled"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"

# Source code and presentation tiers
SRC_DIR: Path = PROJECT_ROOT / "src"
DASHBOARD_DIR: Path = PROJECT_ROOT / "dashboard"
TESTS_DIR: Path = PROJECT_ROOT / "tests"
DOCS_DIR: Path = PROJECT_ROOT / "docs"

# ==============================================================================
# 2. DATASET FILE PATHS
# ==============================================================================
# Primary operational dataset (immutable reference)
ORIGINAL_DATASET_PATH: Path = ORIGINAL_DATA_DIR / "supply_chain_dataset1.xlsx"
ROOT_DATASET_PATH: Path = PROJECT_ROOT / "supply_chain_dataset1.xlsx"

# Master data tables
PRODUCT_MASTER_PATH: Path = MASTER_DATA_DIR / "product_master.csv"
SUPPLIER_MASTER_PATH: Path = MASTER_DATA_DIR / "supplier_master.csv"
WAREHOUSE_MASTER_PATH: Path = MASTER_DATA_DIR / "warehouse_master.csv"
GROUND_TRUTH_MAPPING_PATH: Path = MASTER_DATA_DIR / "ground_truth_mapping.csv"

# Dual-branch operational datasets (91,250 records each)
RAW_BRANCH_PATH: Path = RAW_DATA_DIR / "raw_branch.csv"
RECONCILED_BRANCH_PATH: Path = RECONCILED_DATA_DIR / "reconciled_branch.csv"

# Master entity feeds
RAW_MASTER_DATA_PATH: Path = RAW_DATA_DIR / "raw_master_data.csv"
RECONCILED_MASTER_DATA_PATH: Path = RECONCILED_DATA_DIR / "reconciled_master_data.csv"

# Audit, profile, and prepared operational data
RECONCILIATION_REPORT_PATH: Path = PROCESSED_DATA_DIR / "reconciliation_report.csv"
FORECASTING_AUDIT_REPORT_PATH: Path = PROCESSED_DATA_DIR / "forecasting_audit_report.csv"
DATA_PROFILE_REPORT_PATH: Path = PROCESSED_DATA_DIR / "data_profile_report.md"
PREPARED_OPERATIONAL_DATA_PATH: Path = PROCESSED_DATA_DIR / "prepared_operational_data.csv"

# ==============================================================================
# 3. MASTER DATA RECONCILIATION SETTINGS
# ==============================================================================
# Reproducibility seed for all stochastic operations
RANDOM_SEED: int = 42

# Similarity threshold (0.0 to 100.0) required to accept a canonical match
RECONCILIATION_SIMILARITY_THRESHOLD: float = 85.0

# Injected inconsistency rate in raw operational branch (15% of records)
NOISE_INJECTION_RATE: float = 0.15

# ==============================================================================
# 4. DEMAND FORECASTING SETTINGS
# ==============================================================================
# Primary target variable
FORECAST_TARGET_COL: str = "Units_Sold"

# Composite grain defining each independent time-series
FORECAST_GRAIN_COLS: List[str] = ["Date", "SKU_ID", "Warehouse_ID"]

# Chronological train/test split ratio (80% train / 20% test)
TRAIN_SPLIT_RATIO: float = 0.8

# Time-series feature engineering windows
LAG_WINDOWS: List[int] = [1, 7, 14, 30]
ROLLING_WINDOWS: List[int] = [7, 14, 30]

# Deep learning sequence length (for LSTM / GRU / CNN-LSTM architectures)
SEQUENCE_LENGTH: int = 14

# ==============================================================================
# 5. INVENTORY & WAREHOUSE PLANNING PLACEHOLDERS
# ==============================================================================
DEFAULT_SERVICE_LEVEL: float = 0.95  # 95% service level for safety stock (z ≈ 1.65)
DEFAULT_WAREHOUSE_CAPACITY: int = 50000  # Canonical facility capacity in units


# ==============================================================================
# 6. PATH VERIFICATION UTILITY
# ==============================================================================
def get_dataset_paths() -> Dict[str, Path]:
    """Return dictionary of all registered dataset paths."""
    return {
        "original_dataset": ORIGINAL_DATASET_PATH,
        "root_dataset": ROOT_DATASET_PATH,
        "product_master": PRODUCT_MASTER_PATH,
        "supplier_master": SUPPLIER_MASTER_PATH,
        "warehouse_master": WAREHOUSE_MASTER_PATH,
        "ground_truth_mapping": GROUND_TRUTH_MAPPING_PATH,
        "raw_branch": RAW_BRANCH_PATH,
        "reconciled_branch": RECONCILED_BRANCH_PATH,
        "raw_master_data": RAW_MASTER_DATA_PATH,
        "reconciled_master_data": RECONCILED_MASTER_DATA_PATH,
        "reconciliation_report": RECONCILIATION_REPORT_PATH,
        "forecasting_audit_report": FORECASTING_AUDIT_REPORT_PATH,
    }


def verify_dataset_paths() -> Dict[str, bool]:
    """Check existence of all registered dataset paths."""
    return {name: path.exists() for name, path in get_dataset_paths().items()}
