# Data Profile and Quality Assessment Report
**Dataset:** `supply_chain_dataset1.xlsx`  
**Records:** 91,250 rows $\times$ 15 columns  
**Memory Footprint:** 29.19 MB  

---

## 1. Executive Summary & Health Status
- **Structural Integrity:** PASSED (0 Confirmed Errors)
- **Confirmed Errors:** 0
- **Suspicious Values / Domain Nuances:** 4
- **Temporal Coverage:** 2024-01-01 to 2024-12-30 (365 days, 0 missing calendar days)

---

## 2. Column Schema & Data Types
| Column Name | Inferred Dtype | Null Count | Null (%) | Unique Values |
| :--- | :--- | :---: | :---: | :---: |
| `Date` | `datetime64[ns]` | 0 | 0.0% | 365 |
| `SKU_ID` | `object` | 0 | 0.0% | 50 |
| `Warehouse_ID` | `object` | 0 | 0.0% | 5 |
| `Supplier_ID` | `object` | 0 | 0.0% | 10 |
| `Region` | `object` | 0 | 0.0% | 4 |
| `Units_Sold` | `int64` | 0 | 0.0% | 58 |
| `Inventory_Level` | `int64` | 0 | 0.0% | 781 |
| `Supplier_Lead_Time_Days` | `int64` | 0 | 0.0% | 13 |
| `Reorder_Point` | `int64` | 0 | 0.0% | 142 |
| `Order_Quantity` | `int64` | 0 | 0.0% | 301 |
| `Unit_Cost` | `float64` | 0 | 0.0% | 230 |
| `Unit_Price` | `float64` | 0 | 0.0% | 227 |
| `Promotion_Flag` | `int64` | 0 | 0.0% | 2 |
| `Stockout_Flag` | `int64` | 0 | 0.0% | 1 |
| `Demand_Forecast` | `float64` | 0 | 0.0% | 4736 |

---

## 3. Numerical Statistics Summary
| Column | Min | 25% | Median (50%) | Mean | 75% | Max | Std Dev |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Units_Sold` | 0.0 | 13.0 | 20.0 | 20.0546 | 27.0 | 59.0 | 9.0686 |
| `Inventory_Level` | 168.0 | 370.0 | 461.0 | 471.5223 | 564.0 | 990.0 | 133.488 |
| `Supplier_Lead_Time_Days` | 2.0 | 4.0 | 8.0 | 7.984 | 11.0 | 14.0 | 3.9079 |
| `Reorder_Point` | 201.0 | 252.0 | 300.0 | 300.068 | 346.0 | 398.0 | 54.8799 |
| `Order_Quantity` | 0.0 | 0.0 | 0.0 | 19.2725 | 0.0 | 499.0 | 82.3408 |
| `Unit_Cost` | 5.02 | 8.18 | 11.99 | 12.2033 | 16.32 | 19.76 | 4.575 |
| `Unit_Price` | 6.95 | 12.0 | 18.18 | 18.2618 | 23.39 | 35.1 | 7.1211 |
| `Promotion_Flag` | 0.0 | 0.0 | 0.0 | 0.1016 | 0.0 | 1.0 | 0.3021 |
| `Stockout_Flag` | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| `Demand_Forecast` | 0.0 | 12.95 | 19.95 | 20.082 | 26.93 | 61.42 | 9.504 |

---

## 4. Categorical Entity Distributions
### `SKU_ID` (50 unique entities)
Top observed entities and counts:
- **SKU_1**: 1,825 records
- **SKU_43**: 1,825 records
- **SKU_34**: 1,825 records
- **SKU_35**: 1,825 records
- **SKU_36**: 1,825 records
- **SKU_37**: 1,825 records
- **SKU_38**: 1,825 records
- **SKU_39**: 1,825 records
- **SKU_4**: 1,825 records
- **SKU_40**: 1,825 records

### `Warehouse_ID` (5 unique entities)
Top observed entities and counts:
- **WH_1**: 18,250 records
- **WH_2**: 18,250 records
- **WH_3**: 18,250 records
- **WH_4**: 18,250 records
- **WH_5**: 18,250 records

### `Supplier_ID` (10 unique entities)
Top observed entities and counts:
- **SUP_7**: 12,410 records
- **SUP_8**: 10,220 records
- **SUP_1**: 10,220 records
- **SUP_10**: 9,855 records
- **SUP_2**: 9,490 records
- **SUP_4**: 9,125 records
- **SUP_5**: 8,395 records
- **SUP_3**: 8,395 records
- **SUP_6**: 7,300 records
- **SUP_9**: 5,840 records

### `Region` (4 unique entities)
Top observed entities and counts:
- **North**: 22,974 records
- **East**: 22,934 records
- **South**: 22,720 records
- **West**: 22,622 records

---

## 5. Data-Quality Audit: Confirmed Errors vs. Suspicious Values

### A. Confirmed Errors (Must be 0 for valid pipeline entry)
- ✅ **None.** All 91,250 rows satisfy relational completeness, positive price margins, and non-negativity.

### B. Suspicious Values & Domain Observations (Requires Human Review)
- ⚠️ **NOTE:** Stockout_Flag is 0 in 100% of records (0 stockout events). Minimum Inventory_Level is 168, indicating unconstrained stock in the baseline.
- ⚠️ **NOTE:** Warehouse facilities are associated with multiple regions (e.g., WH_1 in North, South, East, West). In operational logistics, this indicates 'Region' represents customer shipping destination rather than facility address.
- ⚠️ **NOTE:** When Inventory_Level <= Reorder_Point (5041 rows), Order_Quantity is 0 in all cases. Order_Quantity occurs when Inventory_Level is higher, indicating batch receipt logging or lead-time fulfillment delay.
- ⚠️ **NOTE:** Zero-demand observations present: 620 records (0.68% of dataset). Standard for intermittent daily retail sales, but requires non-zero MAPE calculation.

### C. Validated Operational Properties
- ✔️ No missing values (100% complete across all rows and columns).
- ✔️ No exact duplicate records found.
- ✔️ Column 'Units_Sold' strictly non-negative.
- ✔️ Column 'Inventory_Level' strictly non-negative.
- ✔️ Column 'Supplier_Lead_Time_Days' strictly non-negative.
- ✔️ Column 'Reorder_Point' strictly non-negative.
- ✔️ Column 'Order_Quantity' strictly non-negative.
- ✔️ Column 'Unit_Cost' strictly non-negative.
- ✔️ Column 'Unit_Price' strictly non-negative.
- ✔️ Column 'Demand_Forecast' strictly non-negative.
- ✔️ Flag 'Promotion_Flag' contains valid binary values (0 or 1).
- ✔️ Flag 'Stockout_Flag' contains valid binary values (0 or 1).
- ✔️ Unit_Price strictly exceeds Unit_Cost in all records (min margin: $1.19).