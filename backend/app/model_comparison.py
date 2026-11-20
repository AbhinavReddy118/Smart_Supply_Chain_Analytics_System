import pandas as pd
import numpy as np
import tensorflow as tf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, GRU, Conv1D, Dense, Dropout

from lightgbm import LGBMRegressor
from xgboost import XGBRegressor

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler


# ==========================================================
# 1. SETTINGS
# ==========================================================

FILE_PATH = "supply_chain_dataset1.xlsx"

SEQUENCE_LENGTH = 14
TEST_DAYS = 30

np.random.seed(42)
tf.random.set_seed(42)


# ==========================================================
# 2. LOAD DATASET
# ==========================================================

df = pd.read_excel(FILE_PATH)

df["Date"] = pd.to_datetime(df["Date"])

print("\nORIGINAL DATASET")
print("----------------")
print("Records :", len(df))
print("Columns :", len(df.columns))


# ==========================================================
# 3. PREPARE DAILY DEMAND
# ==========================================================

demand = (
    df.groupby(
        ["Date", "SKU_ID", "Warehouse_ID"]
    )["Units_Sold"]
    .sum()
    .reset_index()
)

demand = demand.sort_values(
    ["SKU_ID", "Warehouse_ID", "Date"]
).reset_index(drop=True)


print("\nDAILY DEMAND DATA")
print("-----------------")
print("Records :", len(demand))


# ==========================================================
# 4. CREATE TABULAR FEATURES
# ==========================================================

def create_features(data):

    data = data.copy()

    groups = ["SKU_ID", "Warehouse_ID"]

    data["Day"] = data["Date"].dt.day
    data["Month"] = data["Date"].dt.month
    data["DayOfWeek"] = data["Date"].dt.dayofweek

    data["Lag_1"] = (
        data.groupby(groups)["Units_Sold"]
        .shift(1)
    )

    data["Lag_7"] = (
        data.groupby(groups)["Units_Sold"]
        .shift(7)
    )

    data["Lag_14"] = (
        data.groupby(groups)["Units_Sold"]
        .shift(14)
    )

    data["Rolling_7"] = (
        data.groupby(groups)["Units_Sold"]
        .transform(
            lambda x: x.shift(1).rolling(7).mean()
        )
    )

    return data


demand_features = create_features(demand)

demand_features = (
    demand_features
    .dropna()
    .reset_index(drop=True)
)


# ==========================================================
# 5. CHRONOLOGICAL TRAIN / TEST SPLIT
# ==========================================================

max_date = demand["Date"].max()

cutoff_date = (
    max_date
    - pd.Timedelta(days=TEST_DAYS)
)


# Use the SAME cutoff date for every model

train = demand_features[
    demand_features["Date"] <= cutoff_date
].copy()

test = demand_features[
    demand_features["Date"] > cutoff_date
].copy()


print("\nDATA SPLIT")
print("----------")
print("Training records:", len(train))
print("Testing records :", len(test))
print("Cutoff date     :", cutoff_date.date())


# ==========================================================
# 6. TABULAR DATA FOR XGBOOST AND LIGHTGBM
# ==========================================================

features = [
    "Day",
    "Month",
    "DayOfWeek",
    "Lag_1",
    "Lag_7",
    "Lag_14",
    "Rolling_7"
]

X_train = train[features]
y_train = train["Units_Sold"]

X_test = test[features]
y_test = test["Units_Sold"]


# ==========================================================
# 7. EVALUATION FUNCTION
# ==========================================================

def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(
        actual,
        predicted
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted
        )
    )

    non_zero = actual != 0

    if non_zero.sum() > 0:

        mape = np.mean(
            np.abs(
                (
                    actual[non_zero]
                    - predicted[non_zero]
                )
                / actual[non_zero]
            )
        ) * 100

    else:

        mape = 0

    return mae, rmse, mape


# ==========================================================
# 8. XGBOOST
# ==========================================================

print("\nRunning: XGBoost")

xgb_model = XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1
)

xgb_model.fit(
    X_train,
    y_train
)

xgb_predictions = xgb_model.predict(
    X_test
)

xgb_mae, xgb_rmse, xgb_mape = calculate_metrics(
    y_test,
    xgb_predictions
)


# ==========================================================
# 9. LIGHTGBM
# ==========================================================

print("Running: LightGBM")

lgbm_model = LGBMRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.05,
    num_leaves=31,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbosity=-1
)

lgbm_model.fit(
    X_train,
    y_train
)

lgbm_predictions = lgbm_model.predict(
    X_test
)

lgbm_mae, lgbm_rmse, lgbm_mape = calculate_metrics(
    y_test,
    lgbm_predictions
)


# ==========================================================
# 10. CREATE SEQUENCES
# ==========================================================

def create_sequences(data, sequence_length):

    X = []
    y = []
    dates = []

    groups = data.groupby(
        ["SKU_ID", "Warehouse_ID"],
        sort=False
    )

    for _, group in groups:

        group = group.sort_values("Date")

        values = group["Units_Sold"].values
        group_dates = group["Date"].values

        for i in range(
            sequence_length,
            len(values)
        ):

            X.append(
                values[
                    i - sequence_length:i
                ]
            )

            y.append(
                values[i]
            )

            dates.append(
                group_dates[i]
            )

    return (
        np.array(X),
        np.array(y),
        np.array(dates)
    )


X_sequence, y_sequence, sequence_dates = (
    create_sequences(
        demand,
        SEQUENCE_LENGTH
    )
)


# ==========================================================
# 11. SPLIT NEURAL NETWORK DATA
# ==========================================================

train_mask = (
    sequence_dates <= np.datetime64(cutoff_date)
)

test_mask = (
    sequence_dates > np.datetime64(cutoff_date)
)


X_seq_train = X_sequence[
    train_mask
]

y_seq_train = y_sequence[
    train_mask
]

X_seq_test = X_sequence[
    test_mask
]

y_seq_test = y_sequence[
    test_mask
]


print("\nSEQUENCE DATA")
print("-------------")
print(
    "Training sequences:",
    len(X_seq_train)
)

print(
    "Testing sequences :",
    len(X_seq_test)
)


# ==========================================================
# 12. SCALE NEURAL NETWORK DATA
# ==========================================================

scaler = MinMaxScaler()

# Fit scaler ONLY on training demand
scaler.fit(
    y_seq_train.reshape(-1, 1)
)


# Scale training sequences
X_seq_train_scaled = scaler.transform(
    X_seq_train.reshape(-1, 1)
)

X_seq_train_scaled = (
    X_seq_train_scaled.reshape(
        X_seq_train.shape
    )
)


# Scale testing sequences
X_seq_test_scaled = scaler.transform(
    X_seq_test.reshape(-1, 1)
)

X_seq_test_scaled = (
    X_seq_test_scaled.reshape(
        X_seq_test.shape
    )
)


# Scale training target
y_seq_train_scaled = scaler.transform(
    y_seq_train.reshape(-1, 1)
)


# ==========================================================
# 13. RESHAPE FOR LSTM / GRU / CNN-LSTM
# ==========================================================

X_seq_train_scaled = (
    X_seq_train_scaled.reshape(
        X_seq_train_scaled.shape[0],
        SEQUENCE_LENGTH,
        1
    )
)

X_seq_test_scaled = (
    X_seq_test_scaled.reshape(
        X_seq_test_scaled.shape[0],
        SEQUENCE_LENGTH,
        1
    )
)


# ==========================================================
# 14. LSTM
# ==========================================================

print("Running: LSTM")

lstm_model = Sequential([
    Input(
        shape=(
            SEQUENCE_LENGTH,
            1
        )
    ),

    LSTM(32),

    Dropout(0.2),

    Dense(1)
])


lstm_model.compile(
    optimizer="adam",
    loss="mse"
)


lstm_model.fit(
    X_seq_train_scaled,
    y_seq_train_scaled,
    epochs=10,
    batch_size=64,
    verbose=0
)


lstm_predictions_scaled = (
    lstm_model.predict(
        X_seq_test_scaled,
        verbose=0
    )
)


lstm_predictions = (
    scaler.inverse_transform(
        lstm_predictions_scaled
    ).flatten()
)


lstm_mae, lstm_rmse, lstm_mape = (
    calculate_metrics(
        y_seq_test,
        lstm_predictions
    )
)


# ==========================================================
# 15. GRU
# ==========================================================

print("Running: GRU")

gru_model = Sequential([
    Input(
        shape=(
            SEQUENCE_LENGTH,
            1
        )
    ),

    GRU(32),

    Dropout(0.2),

    Dense(1)
])


gru_model.compile(
    optimizer="adam",
    loss="mse"
)


gru_model.fit(
    X_seq_train_scaled,
    y_seq_train_scaled,
    epochs=10,
    batch_size=64,
    verbose=0
)


gru_predictions_scaled = (
    gru_model.predict(
        X_seq_test_scaled,
        verbose=0
    )
)


gru_predictions = (
    scaler.inverse_transform(
        gru_predictions_scaled
    ).flatten()
)


gru_mae, gru_rmse, gru_mape = (
    calculate_metrics(
        y_seq_test,
        gru_predictions
    )
)


# ==========================================================
# 16. CNN-LSTM
# ==========================================================

print("Running: CNN-LSTM")

cnn_lstm_model = Sequential([
    Input(
        shape=(
            SEQUENCE_LENGTH,
            1
        )
    ),

    Conv1D(
        filters=32,
        kernel_size=2,
        activation="relu"
    ),

    LSTM(32),

    Dropout(0.2),

    Dense(1)
])


cnn_lstm_model.compile(
    optimizer="adam",
    loss="mse"
)


cnn_lstm_model.fit(
    X_seq_train_scaled,
    y_seq_train_scaled,
    epochs=10,
    batch_size=64,
    verbose=0
)


cnn_lstm_predictions_scaled = (
    cnn_lstm_model.predict(
        X_seq_test_scaled,
        verbose=0
    )
)


cnn_lstm_predictions = (
    scaler.inverse_transform(
        cnn_lstm_predictions_scaled
    ).flatten()
)


cnn_lstm_mae, cnn_lstm_rmse, cnn_lstm_mape = (
    calculate_metrics(
        y_seq_test,
        cnn_lstm_predictions
    )
)


# ==========================================================
# 17. MODEL COMPARISON
# ==========================================================

results = [

    {
        "Model": "XGBoost",
        "MAE": xgb_mae,
        "RMSE": xgb_rmse,
        "MAPE (%)": xgb_mape
    },

    {
        "Model": "LightGBM",
        "MAE": lgbm_mae,
        "RMSE": lgbm_rmse,
        "MAPE (%)": lgbm_mape
    },

    {
        "Model": "LSTM",
        "MAE": lstm_mae,
        "RMSE": lstm_rmse,
        "MAPE (%)": lstm_mape
    },

    {
        "Model": "GRU",
        "MAE": gru_mae,
        "RMSE": gru_rmse,
        "MAPE (%)": gru_mape
    },

    {
        "Model": "CNN-LSTM",
        "MAE": cnn_lstm_mae,
        "RMSE": cnn_lstm_rmse,
        "MAPE (%)": cnn_lstm_mape
    }
]


results_df = pd.DataFrame(results)


# ==========================================================
# 18. DISPLAY UNROUNDED RESULTS
# ==========================================================

print("\n==============================================")
print("FORECASTING MODEL COMPARATIVE ANALYSIS")
print("==============================================")

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ==========================================================
# 19. SELECT MODEL
# ==========================================================

selected_model = (
    results_df.loc[
        results_df["MAE"].idxmin(),
        "Model"
    ]
)


print(
    "\nModel selected based on lowest MAE:"
)

print(
    selected_model
)


# ==========================================================
# 20. SAVE RESULTS
# ==========================================================

results_df.to_csv(
    "model_comparison_results.csv",
    index=False
)


print(
    "\nResults saved to:"
)

print(
    "model_comparison_results.csv"
)