import pandas as pd
import numpy as np

from rapidfuzz import process, fuzz


# ==========================================================
# 1. SETTINGS
# ==========================================================

FILE_PATH = "Grocery_Inventory new v1.xlsx"

np.random.seed(42)


# ==========================================================
# 2. LOAD DATASET
# ==========================================================

df = pd.read_excel(FILE_PATH)

print("\nORIGINAL DATASET")
print("----------------")
print("Records :", len(df))
print("Columns :", len(df.columns))


# ==========================================================
# 3. CREATE RAW DATA
# ==========================================================

raw_data = df.copy()

print("\nRAW DATA")
print("--------")
print("Records :", len(raw_data))


# ==========================================================
# 4. CREATE CONTROLLED INCONSISTENCIES
# ==========================================================

experiment_data = df.copy()


# ----------------------------------------------------------
# Product name variations
# ----------------------------------------------------------

product_indices = experiment_data.sample(
    n=min(50, len(experiment_data)),
    random_state=42
).index


for index in product_indices:

    product = str(
        experiment_data.loc[index, "Product_Name"]
    )

    variation_type = np.random.choice([
        "lower",
        "upper",
        "space",
        "double_space"
    ])

    if variation_type == "lower":
        variation = product.lower()

    elif variation_type == "upper":
        variation = product.upper()

    elif variation_type == "space":
        variation = product + " "

    else:
        variation = product.replace(" ", "  ")

    experiment_data.loc[
        index,
        "Product_Name"
    ] = variation


# ----------------------------------------------------------
# Supplier name variations
# ----------------------------------------------------------

supplier_indices = experiment_data.sample(
    n=min(50, len(experiment_data)),
    random_state=24
).index


for index in supplier_indices:

    supplier = str(
        experiment_data.loc[index, "Supplier_Name"]
    )

    variation_type = np.random.choice([
        "lower",
        "upper",
        "space"
    ])

    if variation_type == "lower":
        variation = supplier.lower()

    elif variation_type == "upper":
        variation = supplier.upper()

    else:
        variation = supplier + " "

    experiment_data.loc[
        index,
        "Supplier_Name"
    ] = variation


print("\nCONTROLLED INCONSISTENCIES")
print("--------------------------")
print(
    "Modified Product records  :",
    len(product_indices)
)

print(
    "Modified Supplier records :",
    len(supplier_indices)
)


# ==========================================================
# 5. MASTER DATA RECONCILIATION
# ==========================================================

def normalize_text(value):

    value = str(value)

    value = " ".join(
        value.split()
    )

    return value.strip().lower()


def reconcile_column(data, column):

    data = data.copy()

    # Original clean values
    master_values = (
        df[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    replacements = {}

    for value in data[column].dropna().astype(str).unique():

        normalized_value = normalize_text(value)

        best_match = None
        best_score = 0

        for master_value in master_values:

            normalized_master = normalize_text(
                master_value
            )

            score = fuzz.ratio(
                normalized_value,
                normalized_master
            )

            if score > best_score:

                best_score = score
                best_match = master_value

        if (
            best_match is not None
            and best_score >= 90
            and value != best_match
        ):

            replacements[value] = best_match

    data[column] = (
        data[column]
        .astype(str)
        .replace(replacements)
    )

    return data, replacements


# ----------------------------------------------------------
# Reconcile Product Names
# ----------------------------------------------------------

reconciled_data, product_replacements = (
    reconcile_column(
        experiment_data,
        "Product_Name"
    )
)


# ----------------------------------------------------------
# Reconcile Supplier Names
# ----------------------------------------------------------

reconciled_data, supplier_replacements = (
    reconcile_column(
        reconciled_data,
        "Supplier_Name"
    )
)


print("\nRECONCILIATION")
print("--------------")

print(
    "Product variations reconciled :",
    len(product_replacements)
)

print(
    "Supplier variations reconciled:",
    len(supplier_replacements)
)


# ==========================================================
# 6. PRODUCT-LEVEL ANALYSIS
# ==========================================================

def product_analysis(data):

    result = (
        data.groupby("Product_Name")
        .agg(
            Total_Sales=(
                "Sales_Volume",
                "sum"
            ),

            Total_Stock=(
                "Stock_Quantity",
                "sum"
            ),

            Average_Reorder_Level=(
                "Reorder_Level",
                "mean"
            ),

            Average_Unit_Price=(
                "Unit_Price",
                "mean"
            )
        )
        .reset_index()
    )

    result["Low_Stock"] = (
        result["Total_Stock"]
        < result["Average_Reorder_Level"]
    )

    return result


raw_product_analysis = product_analysis(
    raw_data
)

reconciled_product_analysis = product_analysis(
    reconciled_data
)


# ==========================================================
# 7. SUPPLIER-LEVEL ANALYSIS
# ==========================================================

def supplier_analysis(data):

    result = (
        data.groupby("Supplier_Name")
        .agg(
            Total_Sales=(
                "Sales_Volume",
                "sum"
            ),

            Total_Stock=(
                "Stock_Quantity",
                "sum"
            ),

            Product_Count=(
                "Product_Name",
                "nunique"
            )
        )
        .reset_index()
    )

    return result


raw_supplier_analysis = supplier_analysis(
    raw_data
)

reconciled_supplier_analysis = supplier_analysis(
    reconciled_data
)


# ==========================================================
# 8. CALCULATE COMPARISON METRICS
# ==========================================================

raw_unique_products = (
    raw_data["Product_Name"]
    .nunique()
)

reconciled_unique_products = (
    reconciled_data["Product_Name"]
    .nunique()
)


raw_unique_suppliers = (
    raw_data["Supplier_Name"]
    .nunique()
)

reconciled_unique_suppliers = (
    reconciled_data["Supplier_Name"]
    .nunique()
)


raw_product_groups = len(
    raw_product_analysis
)

reconciled_product_groups = len(
    reconciled_product_analysis
)


raw_supplier_groups = len(
    raw_supplier_analysis
)

reconciled_supplier_groups = len(
    reconciled_supplier_analysis
)


raw_low_stock = (
    raw_product_analysis["Low_Stock"]
    .sum()
)

reconciled_low_stock = (
    reconciled_product_analysis["Low_Stock"]
    .sum()
)


# ==========================================================
# 9. CREATE FINAL COMPARISON TABLE
# ==========================================================

comparison = pd.DataFrame({

    "Metric": [

        "Unique Product Names",
        "Unique Supplier Names",
        "Product Groups for Analysis",
        "Supplier Groups for Analysis",
        "Low Stock Product Groups"

    ],

    "Raw Data": [

        raw_unique_products,
        raw_unique_suppliers,
        raw_product_groups,
        raw_supplier_groups,
        raw_low_stock

    ],

    "Reconciled Data": [

        reconciled_unique_products,
        reconciled_unique_suppliers,
        reconciled_product_groups,
        reconciled_supplier_groups,
        reconciled_low_stock

    ]

})


comparison["Change"] = (
    comparison["Reconciled Data"]
    - comparison["Raw Data"]
)


# ==========================================================
# 10. DISPLAY RESULTS
# ==========================================================

print("\n")
print("================================================")
print("RAW VS RECONCILED MASTER DATA COMPARISON")
print("================================================")

print(
    comparison.to_string(
        index=False
    )
)


# ==========================================================
# 11. SHOW ACTUAL RECONCILIATION EXAMPLES
# ==========================================================

print("\n")
print("================================================")
print("RECONCILIATION EXAMPLES")
print("================================================")


print("\nProduct Name Replacements:")

for old_value, new_value in list(
    product_replacements.items()
)[:15]:

    print(
        f"{old_value}  ->  {new_value}"
    )


print("\nSupplier Name Replacements:")

for old_value, new_value in list(
    supplier_replacements.items()
)[:15]:

    print(
        f"{old_value}  ->  {new_value}"
    )


# ==========================================================
# 12. SAVE RESULTS
# ==========================================================

comparison.to_csv(
    "grocery_raw_reconciled_results.csv",
    index=False
)


reconciled_data.to_excel(
    "grocery_reconciled_data.xlsx",
    index=False
)


raw_product_analysis.to_csv(
    "raw_product_analysis.csv",
    index=False
)


reconciled_product_analysis.to_csv(
    "reconciled_product_analysis.csv",
    index=False
)


print("\nResults saved to:")
print("grocery_raw_reconciled_results.csv")

print("\nReconciled dataset saved to:")
print("grocery_reconciled_data.xlsx")

print("\nProduct analysis files saved:")
print("raw_product_analysis.csv")
print("reconciled_product_analysis.csv")