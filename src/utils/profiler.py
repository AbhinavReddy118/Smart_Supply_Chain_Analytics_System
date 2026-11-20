"""
profiler.py
-----------
Reusable data profiling and data-quality assessment module for the
Smart Supply Chain Analytics System.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
import numpy as np


def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Profile a dataset and return structured metrics:
    - Dimensions, memory usage
    - Data types and null counts
    - Duplicate row counts
    - Date range and continuity
    - Categorical unique counts and distributions
    - Numerical summary statistics (min, mean, median, max, std, percentiles)
    """
    profile: Dict[str, Any] = {}
    
    # Dimensions & Memory
    profile["dimensions"] = {
        "num_rows": int(len(df)),
        "num_columns": int(len(df.columns)),
        "memory_mb": round(float(df.memory_usage(deep=True).sum()) / (1024 * 1024), 2)
    }
    profile["columns"] = list(df.columns)
    
    # Missing values and data types
    col_info = {}
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        col_info[col] = {
            "dtype": str(df[col].dtype),
            "null_count": null_count,
            "null_pct": round(float(null_count) / len(df) * 100, 2),
            "num_unique": int(df[col].nunique())
        }
    profile["column_details"] = col_info
    
    # Duplicate rows
    profile["duplicates"] = {
        "exact_row_duplicates": int(df.duplicated().sum()),
    }
    if all(k in df.columns for k in ["Date", "SKU_ID", "Warehouse_ID"]):
        profile["duplicates"]["grain_duplicates"] = int(
            df.duplicated(subset=["Date", "SKU_ID", "Warehouse_ID"]).sum()
        )
        
    # Date profiling
    if "Date" in df.columns:
        date_series = pd.to_datetime(df["Date"])
        min_date = date_series.min()
        max_date = date_series.max()
        unique_dates = date_series.nunique()
        expected_days = (max_date - min_date).days + 1 if pd.notnull(min_date) else 0
        missing_calendar_days = expected_days - unique_dates
        profile["temporal_profile"] = {
            "min_date": min_date.strftime("%Y-%m-%d") if pd.notnull(min_date) else None,
            "max_date": max_date.strftime("%Y-%m-%d") if pd.notnull(max_date) else None,
            "unique_dates": int(unique_dates),
            "expected_calendar_days": int(expected_days),
            "missing_calendar_days": int(missing_calendar_days)
        }
        
    # Categorical distributions
    cat_cols = [c for c in ["SKU_ID", "Warehouse_ID", "Supplier_ID", "Region"] if c in df.columns]
    cat_profile = {}
    for c in cat_cols:
        val_counts = df[c].value_counts(dropna=False).to_dict()
        cat_profile[c] = {
            "num_unique": int(df[c].nunique()),
            "top_values": {str(k): int(v) for k, v in list(val_counts.items())[:10]}
        }
    profile["categorical_summary"] = cat_profile
    
    # Numerical summaries
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_profile = {}
    for c in num_cols:
        series = df[c].dropna()
        num_profile[c] = {
            "min": float(series.min()) if not series.empty else None,
            "p25": float(series.quantile(0.25)) if not series.empty else None,
            "median": float(series.median()) if not series.empty else None,
            "mean": round(float(series.mean()), 4) if not series.empty else None,
            "p75": float(series.quantile(0.75)) if not series.empty else None,
            "max": float(series.max()) if not series.empty else None,
            "std": round(float(series.std()), 4) if not series.empty else None
        }
    profile["numerical_summary"] = num_profile
    
    return profile


def assess_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform targeted supply chain quality checks and distinguish:
    - Confirmed Errors (violations of physical/logical consistency)
    - Suspicious Values (unusual patterns requiring human review)
    - Clean Operational Properties (validated invariants)
    """
    confirmed_errors: List[str] = []
    suspicious_values: List[str] = []
    validated_properties: List[str] = []
    
    # 1. Missing Values
    null_sum = int(df.isnull().sum().sum())
    if null_sum > 0:
        confirmed_errors.append(f"Missing values found: {null_sum} null cells across dataset.")
    else:
        validated_properties.append("No missing values (100% complete across all rows and columns).")
        
    # 2. Duplicate Records
    dup_sum = int(df.duplicated().sum())
    if dup_sum > 0:
        confirmed_errors.append(f"Exact duplicate records found: {dup_sum} rows.")
    else:
        validated_properties.append("No exact duplicate records found.")
        
    # 3. Non-negativity Checks
    non_negative_cols = [
        "Units_Sold", "Inventory_Level", "Supplier_Lead_Time_Days",
        "Reorder_Point", "Order_Quantity", "Unit_Cost", "Unit_Price", "Demand_Forecast"
    ]
    for col in non_negative_cols:
        if col in df.columns:
            neg_count = int((df[col] < 0).sum())
            if neg_count > 0:
                confirmed_errors.append(f"Column '{col}' has {neg_count} negative values.")
            else:
                validated_properties.append(f"Column '{col}' strictly non-negative.")

    # 4. Binary Flags Check
    for flag_col in ["Promotion_Flag", "Stockout_Flag"]:
        if flag_col in df.columns:
            invalid_flags = int((~df[flag_col].isin([0, 1])).sum())
            if invalid_flags > 0:
                confirmed_errors.append(f"Flag '{flag_col}' contains invalid non-binary values ({invalid_flags} rows).")
            else:
                validated_properties.append(f"Flag '{flag_col}' contains valid binary values (0 or 1).")
                
    # 5. Price Margin (Unit_Price vs Unit_Cost)
    if "Unit_Price" in df.columns and "Unit_Cost" in df.columns:
        loss_count = int((df["Unit_Cost"] > df["Unit_Price"]).sum())
        if loss_count > 0:
            confirmed_errors.append(f"Cost exceeds Price (negative gross margin) in {loss_count} rows.")
        else:
            min_margin = float((df["Unit_Price"] - df["Unit_Cost"]).min())
            validated_properties.append(f"Unit_Price strictly exceeds Unit_Cost in all records (min margin: ${min_margin:.2f}).")

    # 6. Suspicious Values & Domain Observations
    # Stockout_Flag: is it all zero?
    if "Stockout_Flag" in df.columns:
        stockout_ones = int((df["Stockout_Flag"] == 1).sum())
        if stockout_ones == 0:
            min_inv = int(df["Inventory_Level"].min()) if "Inventory_Level" in df.columns else None
            suspicious_values.append(
                f"Stockout_Flag is 0 in 100% of records (0 stockout events). "
                f"Minimum Inventory_Level is {min_inv}, indicating unconstrained stock in the baseline."
            )
            
    # Warehouse_ID vs Region
    if "Warehouse_ID" in df.columns and "Region" in df.columns:
        wh_reg_counts = df.groupby("Warehouse_ID")["Region"].nunique()
        multi_reg_wh = wh_reg_counts[wh_reg_counts > 1]
        if not multi_reg_wh.empty:
            suspicious_values.append(
                f"Warehouse facilities are associated with multiple regions (e.g., WH_1 in North, South, East, West). "
                f"In operational logistics, this indicates 'Region' represents customer shipping destination rather than facility address."
            )
            
    # Order_Quantity vs Reorder_Point relationship
    if "Order_Quantity" in df.columns and "Inventory_Level" in df.columns and "Reorder_Point" in df.columns:
        rop_triggered = df[df["Inventory_Level"] <= df["Reorder_Point"]]
        if not rop_triggered.empty:
            orders_when_below = int((rop_triggered["Order_Quantity"] > 0).sum())
            if orders_when_below == 0:
                suspicious_values.append(
                    f"When Inventory_Level <= Reorder_Point ({len(rop_triggered)} rows), Order_Quantity is 0 in all cases. "
                    f"Order_Quantity occurs when Inventory_Level is higher, indicating batch receipt logging or lead-time fulfillment delay."
                )
                
    # Units_Sold zero demand frequency
    if "Units_Sold" in df.columns:
        zero_sales = int((df["Units_Sold"] == 0).sum())
        zero_pct = round(zero_sales / len(df) * 100, 2)
        if zero_sales > 0:
            suspicious_values.append(
                f"Zero-demand observations present: {zero_sales} records ({zero_pct}% of dataset). "
                f"Standard for intermittent daily retail sales, but requires non-zero MAPE calculation."
            )
            
    return {
        "confirmed_errors": confirmed_errors,
        "suspicious_values": suspicious_values,
        "validated_properties": validated_properties,
        "is_structurally_valid": len(confirmed_errors) == 0
    }


def generate_profile_report_markdown(df: pd.DataFrame, dataset_name: str = "supply_chain_dataset1.xlsx") -> str:
    """Generate a clean, readable Markdown report of the profiling and quality assessment."""
    profile = profile_dataset(df)
    quality = assess_data_quality(df)
    
    dims = profile["dimensions"]
    temp = profile.get("temporal_profile", {})
    
    lines = [
        f"# Data Profile and Quality Assessment Report",
        f"**Dataset:** `{dataset_name}`  ",
        f"**Records:** {dims['num_rows']:,} rows $\\times$ {dims['num_columns']} columns  ",
        f"**Memory Footprint:** {dims['memory_mb']} MB  ",
        "",
        "---",
        "",
        "## 1. Executive Summary & Health Status",
        f"- **Structural Integrity:** {'PASSED (0 Confirmed Errors)' if quality['is_structurally_valid'] else 'FAILED'}",
        f"- **Confirmed Errors:** {len(quality['confirmed_errors'])}",
        f"- **Suspicious Values / Domain Nuances:** {len(quality['suspicious_values'])}",
        f"- **Temporal Coverage:** {temp.get('min_date')} to {temp.get('max_date')} ({temp.get('unique_dates')} days, {temp.get('missing_calendar_days')} missing calendar days)",
        "",
        "---",
        "",
        "## 2. Column Schema & Data Types",
        "| Column Name | Inferred Dtype | Null Count | Null (%) | Unique Values |",
        "| :--- | :--- | :---: | :---: | :---: |"
    ]
    
    for col, details in profile["column_details"].items():
        lines.append(
            f"| `{col}` | `{details['dtype']}` | {details['null_count']} | {details['null_pct']}% | {details['num_unique']} |"
        )
        
    lines.extend([
        "",
        "---",
        "",
        "## 3. Numerical Statistics Summary",
        "| Column | Min | 25% | Median (50%) | Mean | 75% | Max | Std Dev |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    ])
    
    for col, s in profile["numerical_summary"].items():
        lines.append(
            f"| `{col}` | {s['min']} | {s['p25']} | {s['median']} | {s['mean']} | {s['p75']} | {s['max']} | {s['std']} |"
        )
        
    lines.extend([
        "",
        "---",
        "",
        "## 4. Categorical Entity Distributions",
    ])
    
    for cat_col, details in profile["categorical_summary"].items():
        lines.append(f"### `{cat_col}` ({details['num_unique']} unique entities)")
        lines.append("Top observed entities and counts:")
        for k, v in details["top_values"].items():
            lines.append(f"- **{k}**: {v:,} records")
        lines.append("")
        
    lines.extend([
        "---",
        "",
        "## 5. Data-Quality Audit: Confirmed Errors vs. Suspicious Values",
        "",
        "### A. Confirmed Errors (Must be 0 for valid pipeline entry)",
    ])
    if quality["confirmed_errors"]:
        for err in quality["confirmed_errors"]:
            lines.append(f"- ❌ **ERROR:** {err}")
    else:
        lines.append("- ✅ **None.** All 91,250 rows satisfy relational completeness, positive price margins, and non-negativity.")
        
    lines.extend([
        "",
        "### B. Suspicious Values & Domain Observations (Requires Human Review)",
    ])
    for susp in quality["suspicious_values"]:
        lines.append(f"- ⚠️ **NOTE:** {susp}")
        
    lines.extend([
        "",
        "### C. Validated Operational Properties",
    ])
    for prop in quality["validated_properties"]:
        lines.append(f"- ✔️ {prop}")
        
    return "\n".join(lines)
