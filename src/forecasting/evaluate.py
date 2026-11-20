"""
evaluate.py
-----------
Evaluation metrics and benchmark comparisons for the Demand Forecasting Module.
"""

import numpy as np
import pandas as pd
from typing import Dict, Union


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error."""
    return float(np.mean(np.abs(y_true - y_pred)))


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error."""
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Mean Absolute Percentage Error on positive actual demand (y_true > 0).
    Avoids division by zero on intermittent/zero-demand days.
    """
    mask = y_true > 0
    if np.sum(mask) == 0:
        return 0.0
    return float(np.mean(np.abs(y_true[mask] - y_pred[mask]) / y_true[mask]) * 100.0)


def calculate_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Weighted Absolute Percentage Error (sum of abs error / sum of actual).
    Highly recommended for supply chain inventory and demand forecasting.
    """
    total_actual = np.sum(y_true)
    if total_actual == 0:
        return 0.0
    return float((np.sum(np.abs(y_true - y_pred)) / total_actual) * 100.0)


def calculate_all_metrics(y_true: Union[np.ndarray, pd.Series], y_pred: Union[np.ndarray, pd.Series]) -> Dict[str, float]:
    """Compute standard forecasting evaluation metrics."""
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    
    # Guard against NaN
    valid_mask = ~np.isnan(yt) & ~np.isnan(yp)
    yt = yt[valid_mask]
    yp = yp[valid_mask]
    
    return {
        "MAE": round(calculate_mae(yt, yp), 4),
        "RMSE": round(calculate_rmse(yt, yp), 4),
        "MAPE (%)": round(calculate_mape(yt, yp), 2),
        "WAPE (%)": round(calculate_wape(yt, yp), 2),
    }


def compare_raw_vs_reconciled_metrics(
    raw_metrics: Dict[str, float],
    reconciled_metrics: Dict[str, float]
) -> pd.DataFrame:
    """
    Format a standard comparative evaluation table displaying Raw vs Reconciled metrics
    and percentage change / improvement.
    """
    records = []
    for metric, raw_val in raw_metrics.items():
        rec_val = reconciled_metrics.get(metric, 0.0)
        # For error metrics (lower is better), improvement = (raw - rec) / raw * 100
        if raw_val != 0:
            pct_improvement = ((raw_val - rec_val) / raw_val) * 100.0
        else:
            pct_improvement = 0.0
        records.append({
            "Metric": metric,
            "Raw Branch": raw_val,
            "Reconciled Branch": rec_val,
            "Improvement (%)": round(pct_improvement, 2)
        })
    return pd.DataFrame(records)

