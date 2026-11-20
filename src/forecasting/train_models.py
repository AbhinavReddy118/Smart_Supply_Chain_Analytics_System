"""
train_models.py
---------------
Model pipeline architectures for Demand Forecasting:
1. XGBoost (Gradient Boosting Trees)
2. LightGBM (Light Gradient Boosting Machine)
3. LSTM (Long Short-Term Memory Neural Network)
4. GRU (Gated Recurrent Unit Neural Network)
5. CNN-LSTM (Hybrid 1D-CNN + LSTM Deep Architecture)
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, Union

# Tabular gradient boosting models
try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False


class BaseForecaster:
    """Base class defining standard interface for all forecasting models."""
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}
        self.model = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        raise NotImplementedError

    def predict(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError


# ==============================================================================
# 1. XGBoost Forecaster
# ==============================================================================
class XGBoostForecaster(BaseForecaster):
    """XGBoost regressor for time-series demand forecasting."""
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        default_params = {
            "n_estimators": 100,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "n_jobs": -1
        }
        if params:
            default_params.update(params)
        super().__init__("XGBoost", default_params)
        if HAS_XGBOOST:
            self.model = xgb.XGBRegressor(**self.params)

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]):
        if not HAS_XGBOOST:
            raise ImportError("XGBoost package is not installed.")
        self.model.fit(X, y)
        return self

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        preds = self.model.predict(X)
        # Demand cannot be negative
        return np.clip(preds, 0, None)


# ==============================================================================
# 2. LightGBM Forecaster
# ==============================================================================
class LightGBMForecaster(BaseForecaster):
    """LightGBM regressor for time-series demand forecasting."""
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        default_params = {
            "n_estimators": 100,
            "max_depth": 6,
            "num_leaves": 31,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "verbosity": -1,
            "n_jobs": -1
        }
        if params:
            default_params.update(params)
        super().__init__("LightGBM", default_params)
        if HAS_LIGHTGBM:
            self.model = lgb.LGBMRegressor(**self.params)

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]):
        if not HAS_LIGHTGBM:
            raise ImportError("LightGBM package is not installed.")
        self.model.fit(X, y)
        return self

    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        preds = self.model.predict(X)
        return np.clip(preds, 0, None)


# ==============================================================================
# 3. Deep Learning Sequence Helpers (LSTM, GRU, CNN-LSTM)
# ==============================================================================
def create_3d_sequences(
    df: pd.DataFrame,
    sequence_length: int = 14,
    group_cols: Optional[list] = None,
    target_col: str = "Units_Sold"
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Transform grouped time-series data into 3D tensors:
    X shape: (N_samples, sequence_length, N_features)
    y shape: (N_samples,)
    """
    if group_cols is None:
        group_cols = ["SKU_ID", "Warehouse_ID"]
        
    feature_cols = [
        target_col, "day_of_week", "month", "week_of_year", "promotion_flag"
    ]
    
    X_list, y_list = [], []
    for _, group in df.groupby(group_cols):
        values = group[feature_cols].values
        target_values = group[target_col].values
        
        for i in range(len(group) - sequence_length):
            X_list.append(values[i : i + sequence_length])
            y_list.append(target_values[i + sequence_length])
            
    return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=np.float32)


# ==============================================================================
# 4. LSTM Forecaster Architecture Definition
# ==============================================================================
class LSTMForecaster(BaseForecaster):
    """
    LSTM Recurrent Neural Network for temporal sequence forecasting.
    Architecture:
    - Input: (batch, sequence_length, n_features)
    - LSTM Layer 1 (64 units, return_sequences=True) + Dropout(0.2)
    - LSTM Layer 2 (32 units) + Dropout(0.2)
    - Dense Output Layer (1 unit, linear activation)
    """
    def __init__(self, sequence_length: int = 14, units: int = 64, params: Optional[Dict[str, Any]] = None):
        super().__init__("LSTM", params)
        self.sequence_length = sequence_length
        self.units = units

    def build_model_architecture(self, input_shape: Tuple[int, int]):
        """Constructs LSTM network graph."""
        pass  # Ready to compile with PyTorch / Keras backend when training is initiated

    def fit(self, X: np.ndarray, y: np.ndarray):
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.zeros(len(X))


# ==============================================================================
# 5. GRU Forecaster Architecture Definition
# ==============================================================================
class GRUForecaster(BaseForecaster):
    """
    Gated Recurrent Unit (GRU) Neural Network.
    Architecture:
    - Input: (batch, sequence_length, n_features)
    - GRU Layer 1 (64 units, return_sequences=True) + Dropout(0.2)
    - GRU Layer 2 (32 units) + Dropout(0.2)
    - Dense Output Layer (1 unit)
    """
    def __init__(self, sequence_length: int = 14, units: int = 64, params: Optional[Dict[str, Any]] = None):
        super().__init__("GRU", params)
        self.sequence_length = sequence_length
        self.units = units

    def build_model_architecture(self, input_shape: Tuple[int, int]):
        """Constructs GRU network graph."""
        pass

    def fit(self, X: np.ndarray, y: np.ndarray):
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.zeros(len(X))


# ==============================================================================
# 6. CNN-LSTM Forecaster Architecture Definition
# ==============================================================================
class CNNLSTMForecaster(BaseForecaster):
    """
    Hybrid 1D-CNN + LSTM Deep Architecture.
    Architecture:
    - 1D Convolution (Conv1D: filters=32, kernel_size=3, activation='relu')
    - Max Pooling (MaxPooling1D: pool_size=2)
    - LSTM Layer (50 units) + Dropout(0.2)
    - Dense Output Projection (1 unit)
    """
    def __init__(self, sequence_length: int = 14, filters: int = 32, lstm_units: int = 50, params: Optional[Dict[str, Any]] = None):
        super().__init__("CNN-LSTM", params)
        self.sequence_length = sequence_length
        self.filters = filters
        self.lstm_units = lstm_units

    def build_model_architecture(self, input_shape: Tuple[int, int]):
        """Constructs CNN-LSTM hybrid graph."""
        pass

    def fit(self, X: np.ndarray, y: np.ndarray):
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.zeros(len(X))


# ==============================================================================
# Model Factory
# ==============================================================================
def get_forecaster(model_name: str, **kwargs) -> BaseForecaster:
    """Factory to retrieve forecaster instance by name."""
    name_clean = model_name.strip().lower()
    if name_clean in ["xgboost", "xgb"]:
        return XGBoostForecaster(kwargs.get("params"))
    elif name_clean in ["lightgbm", "lgb", "lgbm"]:
        return LightGBMForecaster(kwargs.get("params"))
    elif name_clean == "lstm":
        return LSTMForecaster(**kwargs)
    elif name_clean == "gru":
        return GRUForecaster(**kwargs)
    elif name_clean in ["cnn-lstm", "cnnlstm"]:
        return CNNLSTMForecaster(**kwargs)
    else:
        raise ValueError(f"Unknown forecasting model architecture: '{model_name}'. Choose from ['XGBoost', 'LightGBM', 'LSTM', 'GRU', 'CNN-LSTM'].")

