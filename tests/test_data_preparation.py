"""
test_data_preparation.py
------------------------
Automated tests for Phase 2:
- Successful dataset loading from source.
- Expected schema and column verification.
- Data-type validation and conversion behavior.
- Quality-report generation and rule assessment.
- Preprocessing behavior (sorting, type enforcement).
- Preservation of original source dataset (zero mutation).
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import ORIGINAL_DATASET_PATH, PREPARED_OPERATIONAL_DATA_PATH
from src.utils.profiler import profile_dataset, assess_data_quality, generate_profile_report_markdown
from src.utils.data_preparation import (
    load_source_dataset,
    validate_dataset_schema,
    preprocess_operational_data,
    EXPECTED_OPERATIONAL_COLUMNS
)


@pytest.fixture
def sample_small_df():
    """Create a minimal synthetic supply chain DataFrame for fast unit testing."""
    return pd.DataFrame({
        "Date": ["2024-01-02", "2024-01-01"],
        "SKU_ID": ["SKU_1", "SKU_1"],
        "Warehouse_ID": ["WH_1", "WH_1"],
        "Supplier_ID": ["SUP_1", "SUP_1"],
        "Region": ["North", "North"],
        "Units_Sold": [15, 20],
        "Inventory_Level": [500, 520],
        "Supplier_Lead_Time_Days": [7, 7],
        "Reorder_Point": [300, 300],
        "Order_Quantity": [0, 50],
        "Unit_Cost": [10.5, 10.5],
        "Unit_Price": [15.0, 15.0],
        "Promotion_Flag": [0, 1],
        "Stockout_Flag": [0, 0],
        "Demand_Forecast": [16.2, 19.8]
    })


class TestDatasetLoadingAndSchema:
    """Tests for dataset loading and column structure."""

    def test_load_source_dataset(self):
        """Source dataset must load successfully and return a non-empty DataFrame."""
        df = load_source_dataset(ORIGINAL_DATASET_PATH)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 91250, f"Expected 91,250 rows, got {len(df)}"

    def test_expected_columns(self):
        """Operational dataset must contain all 15 expected columns."""
        df = load_source_dataset(ORIGINAL_DATASET_PATH)
        schema_status = validate_dataset_schema(df)
        assert schema_status["is_valid"] is True
        assert schema_status["missing_columns"] == []
        assert schema_status["column_count"] == 15


class TestDataQualityProfiler:
    """Tests for data profiling and quality rule assessment."""

    def test_profile_dataset_structure(self, sample_small_df):
        """profile_dataset must return expected dictionary keys and metrics."""
        profile = profile_dataset(sample_small_df)
        assert "dimensions" in profile
        assert profile["dimensions"]["num_rows"] == 2
        assert profile["dimensions"]["num_columns"] == 15
        assert "column_details" in profile
        assert "numerical_summary" in profile

    def test_assess_data_quality_clean(self, sample_small_df):
        """assess_data_quality on clean data must report no confirmed errors."""
        quality = assess_data_quality(sample_small_df)
        assert quality["is_structurally_valid"] is True
        assert len(quality["confirmed_errors"]) == 0

    def test_assess_data_quality_detects_errors(self, sample_small_df):
        """assess_data_quality must catch negative quantities, non-binary flags, and negative margins."""
        corrupted = sample_small_df.copy()
        corrupted.loc[0, "Units_Sold"] = -5
        corrupted.loc[0, "Promotion_Flag"] = 99
        corrupted.loc[0, "Unit_Cost"] = 25.0  # Unit_Cost > Unit_Price (15.0)
        
        quality = assess_data_quality(corrupted)
        assert quality["is_structurally_valid"] is False
        assert len(quality["confirmed_errors"]) >= 3

    def test_report_markdown_generation(self, sample_small_df):
        """generate_profile_report_markdown must produce formatted markdown string."""
        md = generate_profile_report_markdown(sample_small_df, "sample_test")
        assert "# Data Profile and Quality Assessment Report" in md
        assert "Units_Sold" in md


class TestPreprocessingBehavior:
    """Tests for preprocessing transformations and type enforcement."""

    def test_preprocessing_types_and_sorting(self, sample_small_df):
        """preprocess_operational_data must cast Date, int64, float64 and sort chronologically."""
        processed, audit = preprocess_operational_data(sample_small_df)
        
        # Check types
        assert pd.api.types.is_datetime64_any_dtype(processed["Date"])
        assert pd.api.types.is_integer_dtype(processed["Units_Sold"])
        assert pd.api.types.is_float_dtype(processed["Unit_Cost"])
        assert pd.api.types.is_string_dtype(processed["SKU_ID"]) or pd.api.types.is_object_dtype(processed["SKU_ID"])
        
        # Check chronological sorting: 2024-01-01 should come before 2024-01-02
        assert processed.loc[0, "Date"] == pd.Timestamp("2024-01-01")
        assert processed.loc[1, "Date"] == pd.Timestamp("2024-01-02")
        
        # Check audit record
        assert audit["rows_preserved"] is True
        assert audit["num_transformations"] > 0

    def test_preservation_of_source_data(self):
        """Preprocessing must never mutate the input DataFrame or overwrite original files."""
        df_original = load_source_dataset(ORIGINAL_DATASET_PATH)
        df_copy = df_original.copy(deep=True)
        
        processed, _ = preprocess_operational_data(df_original)
        
        # Original DataFrame in memory must be completely unchanged
        pd.testing.assert_frame_equal(df_original, df_copy)
        
        # Values in processed must match original (aside from chronological sort)
        original_sorted = df_copy.sort_values(["SKU_ID", "Warehouse_ID", "Date"]).reset_index(drop=True)
        assert (processed["Units_Sold"].values == original_sorted["Units_Sold"].values).all()
        assert (processed["Inventory_Level"].values == original_sorted["Inventory_Level"].values).all()

    def test_prepared_dataset_exists(self):
        """The prepared processed dataset must exist and match expected dimensions."""
        assert PREPARED_OPERATIONAL_DATA_PATH.exists(), f"Prepared dataset not found at {PREPARED_OPERATIONAL_DATA_PATH}"
        df_prep = pd.read_csv(PREPARED_OPERATIONAL_DATA_PATH)
        assert len(df_prep) == 91250
        assert len(df_prep.columns) == 15
