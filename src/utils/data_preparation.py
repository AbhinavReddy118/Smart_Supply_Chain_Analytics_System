"""
data_preparation.py
-------------------
Reusable data loading, validation, and preprocessing pipeline for operational
supply chain datasets in the Smart Supply Chain Analytics System.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

from src.utils.config import (
    ORIGINAL_DATASET_PATH,
    PROCESSED_DATA_DIR,
    FORECAST_TARGET_COL
)
from src.utils.profiler import profile_dataset, assess_data_quality


EXPECTED_OPERATIONAL_COLUMNS: List[str] = [
    "Date",
    "SKU_ID",
    "Warehouse_ID",
    "Supplier_ID",
    "Region",
    "Units_Sold",
    "Inventory_Level",
    "Supplier_Lead_Time_Days",
    "Reorder_Point",
    "Order_Quantity",
    "Unit_Cost",
    "Unit_Price",
    "Promotion_Flag",
    "Stockout_Flag",
    "Demand_Forecast"
]


def load_source_dataset(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load the operational supply chain dataset from the configured location.
    Preserves the original source data without modification.
    """
    path = file_path if file_path is not None else ORIGINAL_DATASET_PATH
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Source operational dataset not found at: {path}")
        
    ext = path.suffix.lower()
    if ext == ".xlsx":
        df = pd.read_excel(path)
    elif ext == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Expected .xlsx or .csv.")
        
    return df


def validate_dataset_schema(df: pd.DataFrame, expected_cols: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate dataset structure, presence of required columns, and basic dimensions.
    """
    if expected_cols is None:
        expected_cols = EXPECTED_OPERATIONAL_COLUMNS
        
    actual_cols = list(df.columns)
    missing_cols = [c for c in expected_cols if c not in actual_cols]
    extra_cols = [c for c in actual_cols if c not in expected_cols]
    
    is_valid = len(missing_cols) == 0 and len(df) > 0
    
    return {
        "is_valid": is_valid,
        "missing_columns": missing_cols,
        "extra_columns": extra_cols,
        "row_count": len(df),
        "column_count": len(actual_cols)
    }


def preprocess_operational_data(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Preprocess the operational supply-chain dataset with explicit transformation tracking:
    1. Cast 'Date' to datetime64[ns].
    2. Enforce standard integer types on discrete operational counts and flags.
    3. Enforce float64 on monetary amounts and continuous forecast metrics.
    4. Enforce string types on categorical identifiers without changing values.
    5. Sort chronologically by SKU_ID, Warehouse_ID, and Date to establish time-series order.
    
    Preserves all operational values without arbitrary deletion or normalization.
    """
    # Defensive copy to ensure zero modification to the input DataFrame
    processed = df.copy()
    transformations_applied: List[str] = []
    
    # 1. Date conversion
    if "Date" in processed.columns:
        processed["Date"] = pd.to_datetime(processed["Date"])
        transformations_applied.append("Casted 'Date' to datetime64[ns]")
        
    # 2. String casting for identifiers
    id_cols = ["SKU_ID", "Warehouse_ID", "Supplier_ID", "Region"]
    for col in id_cols:
        if col in processed.columns:
            processed[col] = processed[col].astype(str).str.strip()
            transformations_applied.append(f"Trimmed and casted '{col}' to clean string")
            
    # 3. Discrete counts and binary flags to integer
    int_cols = [
        "Units_Sold", "Inventory_Level", "Supplier_Lead_Time_Days",
        "Reorder_Point", "Order_Quantity", "Promotion_Flag", "Stockout_Flag"
    ]
    for col in int_cols:
        if col in processed.columns:
            processed[col] = processed[col].astype("int64")
            transformations_applied.append(f"Enforced int64 on '{col}'")
            
    # 4. Monetary and continuous numbers to float
    float_cols = ["Unit_Cost", "Unit_Price", "Demand_Forecast"]
    for col in float_cols:
        if col in processed.columns:
            processed[col] = processed[col].astype("float64")
            transformations_applied.append(f"Enforced float64 on '{col}'")
            
    # 5. Chronological sorting for balanced panel consistency
    sort_keys = [c for c in ["SKU_ID", "Warehouse_ID", "Date"] if c in processed.columns]
    if sort_keys:
        processed = processed.sort_values(sort_keys).reset_index(drop=True)
        transformations_applied.append(f"Chronologically sorted records by {sort_keys}")
        
    audit_record = {
        "num_transformations": len(transformations_applied),
        "transformations": transformations_applied,
        "input_shape": df.shape,
        "output_shape": processed.shape,
        "rows_preserved": len(processed) == len(df)
    }
    
    return processed, audit_record


def prepare_and_save_operational_data(
    source_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    report_path: Optional[Path] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Orchestrate full data preparation:
    1. Load source dataset.
    2. Validate schema.
    3. Preprocess data.
    4. Assess quality and generate report.
    5. Save processed output to separate location.
    """
    if source_path is None:
        source_path = ORIGINAL_DATASET_PATH
    if output_path is None:
        output_path = PROCESSED_DATA_DIR / "prepared_operational_data.csv"
    if report_path is None:
        report_path = PROCESSED_DATA_DIR / "data_profile_report.md"
        
    source_path = Path(source_path)
    output_path = Path(output_path)
    report_path = Path(report_path)
    
    # 1. Load source
    raw_df = load_source_dataset(source_path)
    
    # 2. Validate schema
    schema_status = validate_dataset_schema(raw_df)
    if not schema_status["is_valid"]:
        raise ValueError(f"Dataset schema invalid: missing {schema_status['missing_columns']}")
        
    # 3. Preprocess
    prepared_df, transform_audit = preprocess_operational_data(raw_df)
    
    # 4. Assess quality & generate report
    quality_summary = assess_data_quality(prepared_df)
    from src.utils.profiler import generate_profile_report_markdown
    report_content = generate_profile_report_markdown(prepared_df, dataset_name=source_path.name)
    
    # 5. Save outputs
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    prepared_df.to_csv(output_path, index=False)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    execution_summary = {
        "source_dataset": str(source_path),
        "prepared_dataset": str(output_path),
        "quality_report": str(report_path),
        "rows_processed": len(prepared_df),
        "columns_processed": len(prepared_df.columns),
        "transformations_count": transform_audit["num_transformations"],
        "quality_status": "VALID" if quality_summary["is_structurally_valid"] else "INVALID"
    }
    
    return prepared_df, execution_summary
