"""
baseline.py
-----------
Naive and seasonal baseline models for demand forecasting.
Baseline: Prediction for day t = actual demand from day t-1 (lag_1).
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Tuple

try:
    from src.forecasting.forecasting_data import (
        load_branch_data,
        engineer_forecasting_features,
        split_chronological
    )
    from src.forecasting.evaluate import calculate_all_metrics
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.forecasting.forecasting_data import (
        load_branch_data,
        engineer_forecasting_features,
        split_chronological
    )
    from src.forecasting.evaluate import calculate_all_metrics


class NaiveBaselineForecaster:
    """
    Standard Naive Lag-1 Forecaster:
    Prediction for day t = demand from day t - 1.
    """
    def __init__(self, lag_col: str = "lag_1"):
        self.lag_col = lag_col
        self.name = "Naive (Lag-1) Baseline"

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self.lag_col not in df.columns:
            raise KeyError(f"Required lag column '{self.lag_col}' not found in dataframe.")
        return df[self.lag_col].values


class SeasonalNaiveBaselineForecaster:
    """
    Seasonal Naive Lag-7 Forecaster:
    Prediction for day t = demand from day t - 7 (same day of previous week).
    """
    def __init__(self, lag_col: str = "lag_7"):
        self.lag_col = lag_col
        self.name = "Seasonal Naive (Lag-7) Baseline"

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self.lag_col not in df.columns:
            raise KeyError(f"Required lag column '{self.lag_col}' not found in dataframe.")
        return df[self.lag_col].values


def run_baseline_evaluation(
    raw_path: str = "data/raw/raw_branch.csv",
    reconciled_path: str = "data/reconciled/reconciled_branch.csv",
    train_ratio: float = 0.8
) -> Dict[str, Dict[str, float]]:
    """
    Run baseline evaluation on test sets of both Raw and Reconciled branches.
    """
    # 1. Load Raw branch
    df_raw = load_branch_data(raw_path)
    df_raw_feat = engineer_forecasting_features(df_raw)
    _, test_raw, split_info = split_chronological(df_raw_feat, train_ratio=train_ratio)
    
    # 2. Load Reconciled branch
    df_rec = load_branch_data(reconciled_path)
    df_rec_feat = engineer_forecasting_features(df_rec)
    _, test_rec, _ = split_chronological(df_rec_feat, train_ratio=train_ratio)
    
    forecaster = NaiveBaselineForecaster(lag_col="lag_1")
    
    # Predict on test sets
    raw_preds = forecaster.predict(test_raw)
    rec_preds = forecaster.predict(test_rec)
    
    raw_metrics = calculate_all_metrics(test_raw["Units_Sold"], raw_preds)
    rec_metrics = calculate_all_metrics(test_rec["Units_Sold"], rec_preds)
    
    return {
        "split_info": split_info,
        "raw_metrics": raw_metrics,
        "reconciled_metrics": rec_metrics
    }


if __name__ == "__main__":
    results = run_baseline_evaluation()
    print("Baseline Evaluation Results:")
    print("Train Period:", results["split_info"]["train_start_date"], "to", results["split_info"]["train_end_date"])
    print("Test Period :", results["split_info"]["test_start_date"], "to", results["split_info"]["test_end_date"])
    print("Raw Branch Metrics       :", results["raw_metrics"])
    print("Reconciled Branch Metrics:", results["reconciled_metrics"])

