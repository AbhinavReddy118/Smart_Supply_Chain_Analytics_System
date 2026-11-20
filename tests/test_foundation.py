"""
test_foundation.py
------------------
Basic foundation tests for Phase 1:
- Verifies dynamic project root and dataset path resolution.
- Verifies integrity of centralized configuration settings.
- Verifies that existing Python modules can be imported cleanly.
- Verifies that dual-branch operational datasets can be resolved and read.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestConfiguration:
    """Verify configuration loading and path resolution."""

    def test_project_root_resolution(self):
        """PROJECT_ROOT must exist and contain requirements.txt and supply_chain_dataset1.xlsx."""
        from src.utils.config import PROJECT_ROOT, ROOT_DATASET_PATH
        assert PROJECT_ROOT.exists(), f"PROJECT_ROOT does not exist: {PROJECT_ROOT}"
        assert PROJECT_ROOT.is_dir(), f"PROJECT_ROOT is not a directory: {PROJECT_ROOT}"
        assert (PROJECT_ROOT / "requirements.txt").exists(), "requirements.txt missing from PROJECT_ROOT"
        assert ROOT_DATASET_PATH.exists(), f"Root operational dataset not found at: {ROOT_DATASET_PATH}"

    def test_dataset_paths_exist(self):
        """All curated dataset files must exist at resolved paths."""
        from src.utils.config import verify_dataset_paths
        path_status = verify_dataset_paths()
        for name, exists in path_status.items():
            assert exists, f"Required dataset path failed to resolve: '{name}'"

    def test_reconciliation_settings(self):
        """Reconciliation settings must maintain approved baseline values."""
        from src.utils.config import (
            RECONCILIATION_SIMILARITY_THRESHOLD,
            RANDOM_SEED,
            NOISE_INJECTION_RATE
        )
        assert RECONCILIATION_SIMILARITY_THRESHOLD == 85.0
        assert RANDOM_SEED == 42
        assert NOISE_INJECTION_RATE == 0.15

    def test_forecasting_settings(self):
        """Forecasting settings must specify expected target and split parameters."""
        from src.utils.config import (
            FORECAST_TARGET_COL,
            FORECAST_GRAIN_COLS,
            TRAIN_SPLIT_RATIO,
            LAG_WINDOWS
        )
        assert FORECAST_TARGET_COL == "Units_Sold"
        assert FORECAST_GRAIN_COLS == ["Date", "SKU_ID", "Warehouse_ID"]
        assert TRAIN_SPLIT_RATIO == 0.8
        assert 1 in LAG_WINDOWS


class TestModuleImports:
    """Verify that existing source modules can be imported without errors."""

    def test_import_utils(self):
        """src.utils and src.utils.config must be importable."""
        import src.utils
        import src.utils.config
        assert hasattr(src.utils.config, "PROJECT_ROOT")

    def test_import_forecasting_modules(self):
        """All existing modules in src.forecasting must be importable."""
        from src.forecasting import (
            load_branch_data,
            engineer_forecasting_features,
            split_chronological,
            NaiveBaselineForecaster,
            SeasonalNaiveBaselineForecaster,
            calculate_all_metrics,
            get_forecaster
        )
        assert callable(load_branch_data)
        assert callable(engineer_forecasting_features)
        assert callable(split_chronological)
        assert callable(calculate_all_metrics)


class TestDataIntegrity:
    """Verify that primary datasets can be read and exhibit valid structure."""

    def test_operational_branches_readable(self):
        """Verify that Raw and Reconciled branch CSVs exist and can be loaded."""
        from src.utils.config import RAW_BRANCH_PATH, RECONCILED_BRANCH_PATH
        
        # Read small sample to verify header and loadability without high memory overhead
        df_raw_head = pd.read_csv(RAW_BRANCH_PATH, nrows=5)
        df_rec_head = pd.read_csv(RECONCILED_BRANCH_PATH, nrows=5)
        
        expected_cols = [
            "Date", "SKU_ID", "Product_Name", "Category",
            "Warehouse_ID", "Warehouse_Name", "Region", "Warehouse_Capacity",
            "Supplier_ID", "Supplier_Name", "Units_Sold", "Inventory_Level",
            "Supplier_Lead_Time_Days", "Reorder_Point", "Order_Quantity",
            "Unit_Cost", "Unit_Price", "Promotion_Flag", "Stockout_Flag",
            "Demand_Forecast"
        ]
        
        assert list(df_raw_head.columns) == expected_cols
        assert list(df_rec_head.columns) == expected_cols

    def test_master_tables_readable(self):
        """Verify that canonical master tables can be loaded."""
        from src.utils.config import (
            PRODUCT_MASTER_PATH,
            SUPPLIER_MASTER_PATH,
            WAREHOUSE_MASTER_PATH
        )
        df_prod = pd.read_csv(PRODUCT_MASTER_PATH)
        df_supp = pd.read_csv(SUPPLIER_MASTER_PATH)
        df_wh = pd.read_csv(WAREHOUSE_MASTER_PATH)
        
        assert len(df_prod) == 50, f"Expected 50 SKUs, found {len(df_prod)}"
        assert len(df_supp) == 10, f"Expected 10 suppliers, found {len(df_supp)}"
        assert len(df_wh) == 5, f"Expected 5 warehouses, found {len(df_wh)}"
