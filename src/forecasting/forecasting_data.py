"""
forecasting_data.py
-------------------
Data preparation, time-series feature engineering, and chronological splitting
for the Demand Forecasting Module of the Smart Supply Chain Analytics System.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Optional


def load_branch_data(file_path: str) -> pd.DataFrame:
    """
    Load operational branch dataset (Raw or Reconciled) and convert Date.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Branch data file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"])
    # Sort strictly by series identifier and chronological date
    df = df.sort_values(["SKU_ID", "Warehouse_ID", "Date"]).reset_index(drop=True)
    return df


def engineer_forecasting_features(
    df: pd.DataFrame,
    target_col: str = "Units_Sold",
    group_cols: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Generate time-series lag and rolling statistics strictly without future leakage.
    
    Features created:
    - lag_1, lag_7, lag_14, lag_30
    - rolling_mean_7, rolling_mean_14, rolling_mean_30 (using shift(1) to exclude current t)
    - day_of_week, month, week_of_year
    - promotion_flag
    """
    if group_cols is None:
        group_cols = ["SKU_ID", "Warehouse_ID"]
        
    df = df.copy()
    
    # Verify proper sorting
    df = df.sort_values(group_cols + ["Date"]).reset_index(drop=True)
    
    # 1. Calendar Time-based Features
    df["day_of_week"] = df["Date"].dt.dayofweek
    df["month"] = df["Date"].dt.month
    df["week_of_year"] = df["Date"].dt.isocalendar().week.astype(int)
    
    # 2. Promotional Indicator
    if "Promotion_Flag" in df.columns:
        df["promotion_flag"] = df["Promotion_Flag"].astype(int)
    else:
        df["promotion_flag"] = 0
        
    # 3. Lag Features (strictly from historical observations)
    grouped = df.groupby(group_cols)[target_col]
    df["lag_1"] = grouped.shift(1)
    df["lag_7"] = grouped.shift(7)
    df["lag_14"] = grouped.shift(14)
    df["lag_30"] = grouped.shift(30)
    
    # 4. Rolling Mean Statistics (strictly excluding current observation t via shift(1))
    df["rolling_mean_7"] = grouped.transform(lambda s: s.shift(1).rolling(window=7, min_periods=1).mean())
    df["rolling_mean_14"] = grouped.transform(lambda s: s.shift(1).rolling(window=14, min_periods=1).mean())
    df["rolling_mean_30"] = grouped.transform(lambda s: s.shift(1).rolling(window=30, min_periods=1).mean())
    
    return df


def split_chronological(
    df: pd.DataFrame,
    train_ratio: float = 0.8
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, str]]:
    """
    Perform strict chronological train/test split based on unique dates.
    Guarantees no future leakage and identical date cutoffs across branches.
    """
    unique_dates = np.sort(df["Date"].unique())
    n_total_dates = len(unique_dates)
    n_train_dates = int(n_total_dates * train_ratio)
    
    train_dates = unique_dates[:n_train_dates]
    test_dates = unique_dates[n_train_dates:]
    
    train_df = df[df["Date"].isin(train_dates)].copy().reset_index(drop=True)
    test_df = df[df["Date"].isin(test_dates)].copy().reset_index(drop=True)
    
    split_info = {
        "train_start_date": pd.to_datetime(train_dates[0]).strftime("%Y-%m-%d"),
        "train_end_date": pd.to_datetime(train_dates[-1]).strftime("%Y-%m-%d"),
        "test_start_date": pd.to_datetime(test_dates[0]).strftime("%Y-%m-%d"),
        "test_end_date": pd.to_datetime(test_dates[-1]).strftime("%Y-%m-%d"),
        "total_dates": str(n_total_dates),
        "train_dates_count": str(len(train_dates)),
        "test_dates_count": str(len(test_dates)),
        "train_records": str(len(train_df)),
        "test_records": str(len(test_df)),
    }
    
    return train_df, test_df, split_info


def prepare_tabular_matrices(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    target_col: str = "Units_Sold"
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Extract feature matrices X and target vectors y for tabular ML models (XGBoost, LightGBM).
    Drops initial warm-up rows with NaN in lags (e.g. first 30 days) from the training set.
    """
    if feature_cols is None:
        feature_cols = [
            "lag_1", "lag_7", "lag_14", "lag_30",
            "rolling_mean_7", "rolling_mean_14", "rolling_mean_30",
            "day_of_week", "month", "week_of_year", "promotion_flag"
        ]
        
    # Drop rows in train where lag_30 is NaN to ensure full feature history
    clean_train = train_df.dropna(subset=feature_cols).copy().reset_index(drop=True)
    # For test set, because lag features were generated on full continuous panel,
    # test set has no NaNs if test starts after day 30.
    clean_test = test_df.dropna(subset=feature_cols).copy().reset_index(drop=True)
    
    X_train = clean_train[feature_cols]
    y_train = clean_train[target_col]
    X_test = clean_test[feature_cols]
    y_test = clean_test[target_col]
    
    return X_train, y_train, X_test, y_test

