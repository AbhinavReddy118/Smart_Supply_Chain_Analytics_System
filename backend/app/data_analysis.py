import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


# --------------------------------------------------
# 1. Load the dataset
# --------------------------------------------------

FILE_PATH = "supply_chain_dataset1.xlsx"

df = pd.read_excel(FILE_PATH)

df["Date"] = pd.to_datetime(df["Date"])

print("Original dataset")
print("----------------")
print("Number of records:", len(df))
print("Number of columns:", len(df.columns))


# --------------------------------------------------
# 2. Check the original data
# --------------------------------------------------

print("\nMissing values:", df.isnull().sum().sum())
print("Existing duplicate rows:", df.duplicated().sum())


# --------------------------------------------------
# 3. Split data into training and testing data
# --------------------------------------------------

cutoff_date = df["Date"].max() - pd.Timedelta(days=30)

train_original = df[
    df["Date"] <= cutoff_date
].copy()

test_data = df[
    df["Date"] > cutoff_date
].copy()

print("\nTraining records:", len(train_original))
print("Testing records:", len(test_data))


# --------------------------------------------------
# 4. Create RAW data by adding duplicate records
# --------------------------------------------------

np.random.seed(42)

duplicate_count = int(len(train_original) * 0.05)

duplicate_rows = train_original.sample(
    n=duplicate_count,
    random_state=42
)

raw_train = pd.concat(
    [train_original, duplicate_rows],
    ignore_index=True
)

print("\nRAW DATA")
print("--------")
print("Original training records:", len(train_original))
print("Duplicate records added:", duplicate_count)
print("Raw training records:", len(raw_train))


# --------------------------------------------------
# 5. Master Data Reconciliation
# --------------------------------------------------

reconciled_train = raw_train.drop_duplicates().copy()

duplicates_removed = (
    len(raw_train) - len(reconciled_train)
)

print("\nRECONCILIATION")
print("--------------")
print("Records before reconciliation:", len(raw_train))
print("Duplicate records removed:", duplicates_removed)
print("Records after reconciliation:", len(reconciled_train))


# --------------------------------------------------
# 6. Prepare daily demand data
# --------------------------------------------------

def prepare_demand_data(data):

    demand = (
        data.groupby(
            ["Date", "SKU_ID", "Warehouse_ID"]
        )["Units_Sold"]
        .sum()
        .reset_index()
    )

    demand = demand.sort_values(
        ["SKU_ID", "Warehouse_ID", "Date"]
    )

    return demand


# --------------------------------------------------
# 7. Create forecasting features
# --------------------------------------------------

def create_features(data):

    data = data.copy()

    data["Day"] = data["Date"].dt.day
    data["Month"] = data["Date"].dt.month
    data["DayOfWeek"] = data["Date"].dt.dayofweek

    group_columns = [
        "SKU_ID",
        "Warehouse_ID"
    ]

    # Demand from the previous day
    data["Lag_1"] = (
        data.groupby(group_columns)["Units_Sold"]
        .shift(1)
    )

    # Demand from 7 days earlier
    data["Lag_7"] = (
        data.groupby(group_columns)["Units_Sold"]
        .shift(7)
    )

    # Demand from 14 days earlier
    data["Lag_14"] = (
        data.groupby(group_columns)["Units_Sold"]
        .shift(14)
    )

    # Average demand from the previous 7 days
    data["Rolling_7"] = (
        data.groupby(group_columns)["Units_Sold"]
        .transform(
            lambda x: x.shift(1).rolling(7).mean()
        )
    )

    data = data.dropna()

    return data


# --------------------------------------------------
# 8. Forecasting function
# --------------------------------------------------

def run_forecast(train_data, test_data):

    train_demand = prepare_demand_data(train_data)

    test_demand = prepare_demand_data(test_data)

    combined = pd.concat(
        [train_demand, test_demand],
        ignore_index=True
    )

    combined = combined.sort_values(
        ["SKU_ID", "Warehouse_ID", "Date"]
    )

    combined = create_features(combined)

    train = combined[
        combined["Date"] <= cutoff_date
    ]

    test = combined[
        combined["Date"] > cutoff_date
    ]

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

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    # Avoid division by zero in MAPE
    non_zero = y_test != 0

    mape = np.mean(
        np.abs(
            (
                y_test[non_zero]
                - predictions[non_zero]
            )
            / y_test[non_zero]
        )
    ) * 100

    return mae, rmse, mape


# --------------------------------------------------
# 9. Run forecasting on RAW data
# --------------------------------------------------

raw_mae, raw_rmse, raw_mape = run_forecast(
    raw_train,
    test_data
)


# --------------------------------------------------
# 10. Run forecasting on RECONCILED data
# --------------------------------------------------

reconciled_mae, reconciled_rmse, reconciled_mape = (
    run_forecast(
        reconciled_train,
        test_data
    )
)


# --------------------------------------------------
# 11. Create comparison table
# --------------------------------------------------

results = pd.DataFrame({
    "Data Condition": [
        "Raw Data",
        "Reconciled Data"
    ],

    "MAE": [
        raw_mae,
        reconciled_mae
    ],

    "RMSE": [
        raw_rmse,
        reconciled_rmse
    ],

    "MAPE (%)": [
        raw_mape,
        reconciled_mape
    ]
})

results = results.round(2)


# --------------------------------------------------
# 12. Calculate improvement
# --------------------------------------------------

mae_improvement = (
    (raw_mae - reconciled_mae)
    / raw_mae
) * 100

rmse_improvement = (
    (raw_rmse - reconciled_rmse)
    / raw_rmse
) * 100

mape_improvement = (
    (raw_mape - reconciled_mape)
    / raw_mape
) * 100


# --------------------------------------------------
# 13. Display final results
# --------------------------------------------------

print("\n========================================")
print("RAW VS RECONCILED FORECAST COMPARISON")
print("========================================")

print(results.to_string(index=False))

print("\nImprovement after reconciliation")
print("---------------------------------")

print(
    "MAE improvement :",
    round(mae_improvement, 2),
    "%"
)

print(
    "RMSE improvement:",
    round(rmse_improvement, 2),
    "%"
)

print(
    "MAPE improvement:",
    round(mape_improvement, 2),
    "%"
)


# --------------------------------------------------
# 14. Save results for the paper
# --------------------------------------------------

results.to_csv(
    "forecast_comparison_results.csv",
    index=False
)

print("\nResults saved to:")
print("forecast_comparison_results.csv")