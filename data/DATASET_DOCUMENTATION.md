# Dataset Architecture & Documentation
## Smart Supply Chain Analytics System

### 1. Overview & Research Objective
The central research objective of this project is to investigate:
> **"Does improving supply-chain master-data quality through reconciliation produce measurable improvements in downstream demand forecasting, inventory optimization, and supply planning?"**

To evaluate this empirically, a dual-branch analytical experimental design is implemented. Both branches share the identical, verified operational transactions (91,250 daily records) while differing strictly in their master-data quality.

---

### 2. Original Dataset Structure
The operational backbone is preserved completely intact from `supply_chain_dataset1.xlsx`:
- **Total Records:** 91,250 rows
- **Columns (15):** `Date`, `SKU_ID`, `Warehouse_ID`, `Supplier_ID`, `Region`, `Units_Sold`, `Inventory_Level`, `Supplier_Lead_Time_Days`, `Reorder_Point`, `Order_Quantity`, `Unit_Cost`, `Unit_Price`, `Promotion_Flag`, `Stockout_Flag`, `Demand_Forecast`
- **Granularity:** 365 daily observations (2024-01-01 to 2024-12-30) across 250 distinct SKU-Warehouse combinations ($50 \text{ SKUs} \times 5 \text{ Warehouses}$).
- **Data Quality:** 0 missing values, 0 exact duplicate rows, balanced time-series panel.
- **Preservation:** The original dataset is preserved untouched at `data/original/supply_chain_dataset1.xlsx` and at the workspace root.

---

### 3. Master Data Tables (Canonical Reference)
To support master-data reconciliation and realistic descriptive entity management, canonical master tables were generated deterministically from existing entity keys:

1. **Product Master (`data/master/product_master.csv` - 50 records):**
   - `SKU_ID`: `SKU_1` to `SKU_50`
   - `Product_Name`: `Product 1` to `Product 50`
   - `Category`: Categorized into 5 balanced categories (10 SKUs each): *Food & Beverage*, *Personal Care*, *Household*, *Produce*, *Packaged Goods*.
2. **Supplier Master (`data/master/supplier_master.csv` - 10 records):**
   - `Supplier_ID`: `SUP_1` to `SUP_10`
   - `Supplier_Name`: `Supplier 1` to `Supplier 10`
3. **Warehouse Master (`data/master/warehouse_master.csv` - 5 records):**
   - `Warehouse_ID`: `WH_1` to `WH_5`
   - `Warehouse_Name`: `Warehouse 1` to `Warehouse 5`
   - `Region`: `North`, `South`, `East`, `West`, `Central`
   - `Capacity`: 50,000 units (based on historical peak daily inventory of ~37,000 units).

---

### 4. Types of Controlled Inconsistencies Introduced
To emulate real-world ERP and master-data corruption without corrupting business measurements, controlled linguistic and typographical variations were injected into descriptive attributes:

| Variation Category | Specific Pattern | Raw Example | Canonical Target |
| :--- | :--- | :--- | :--- |
| **Case Standardization** | All lowercase | `product 1`, `supplier 2`, `warehouse 3` | `Product 1`, `Supplier 2`, `Warehouse 3` |
| **Case Standardization** | All uppercase | `PRODUCT 1`, `SUPPLIER 2`, `WAREHOUSE 3` | `Product 1`, `Supplier 2`, `Warehouse 3` |
| **Whitespace Noise** | Trailing space | `Product 1 `, `Supplier 2 ` | `Product 1`, `Supplier 2` |
| **Whitespace Noise** | Leading space | ` Product 1` | `Product 1` |
| **Whitespace Noise** | Double internal space | `Product  1` | `Product 1` |
| **Delimiters & Punctuation** | Hyphen delimiter | `Product-1`, `Supplier-2`, `Warehouse-3` | `Product 1`, `Supplier 2`, `Warehouse 3` |
| **Delimiters & Punctuation** | Underscore delimiter | `Product_1`, `Supplier_2` | `Product 1`, `Supplier 2` |
| **Abbreviation Handling** | Standard abbreviation | `Prod 1`, `Supp 2`, `WH 3` | `Product 1`, `Supplier 2`, `Warehouse 3` |
| **Abbreviation Handling** | Abbrev. with dot/punct. | `Prod. 1`, `Supp. 2`, `WH-3`, `WH_3` | `Product 1`, `Supplier 2`, `Warehouse 3` |

**Controlled Subset in Operational Data:**
- In the downstream operational dataset, a controlled **15% subset of records** randomly receives these descriptive inconsistencies across `Product_Name`, `Supplier_Name`, and `Warehouse_Name`.
- **Operational Non-Corruption Rule:** Zero operational fields (`Units_Sold`, `Inventory_Level`, `Unit_Cost`, `Unit_Price`, `Supplier_Lead_Time_Days`, `Reorder_Point`, `Order_Quantity`, `Promotion_Flag`, `Stockout_Flag`) were altered or dropped.

---

### 5. Ground-Truth Mapping Table
- **File:** `data/master/ground_truth_mapping.csv` (555 mapping records)
- **Schema:** `entity_type`, `entity_id`, `raw_value`, `canonical_value`, `variation_type`
- **Integrity Rule:** This mapping is strictly an evaluation benchmark. It is **never** provided to the reconciliation algorithm during processing.

---

### 6. Master Data Reconciliation Method
The reconciliation algorithm operates directly on noisy descriptive text:
1. **Punctuation & Delimiter Stripping:** Replaces `-`, `_`, and `.` with standard spaces.
2. **Whitespace Normalization:** Strips leading/trailing spaces and collapses repeated spaces.
3. **Case Normalization:** Converts strings to lowercase.
4. **Domain Abbreviation Expansion:** Expands standard abbreviations (`prod` $\to$ `product`, `supp` $\to$ `supplier`, `wh` $\to$ `warehouse`).
5. **Entity-Aware Guardrails:** Isolates integer tokens to prevent false-positive matching between adjacent numbers (e.g., ensuring `Product 1` never matches `Product 10`).
6. **Fuzzy String Similarity:** Evaluates string similarity ratio using `SequenceMatcher` against canonical candidate entities.
7. **Configurable Threshold:** Evaluates against a minimum matching threshold ($\ge 85.0\%$). Records meeting the threshold are assigned `RECONCILED`; records below threshold are marked `UNRESOLVED`.

---

### 7. Reconciliation Performance & Validation Report
Summary of evaluation against the ground-truth benchmark (`data/processed/reconciliation_report.csv`):
- **Total Master Records Audited:** 620 records (65 clean canonical + 555 inconsistent variants)
- **Inconsistent Records Requiring Reconciliation:** 555 records
- **Successfully Reconciled:** 620 records (100.0%)
- **Unresolved Records:** 0
- **False / Incorrect Matches:** 0
- **Overall Reconciliation Accuracy:** **100.00%**
- **Similarity Threshold Applied:** 85.0%

---

### 8. Output Datasets & Downstream Dual Branches

| Directory | File Name | Records | Description |
| :--- | :--- | :--- | :--- |
| `data/original/` | `supply_chain_dataset1.xlsx` | 91,250 | Complete, untouched copy of original source dataset. |
| `data/master/` | `product_master.csv` | 50 | Canonical Product Master (SKU_ID, Product_Name, Category). |
| `data/master/` | `supplier_master.csv` | 10 | Canonical Supplier Master (Supplier_ID, Supplier_Name). |
| `data/master/` | `warehouse_master.csv` | 5 | Canonical Warehouse Master (Warehouse_ID, Warehouse_Name, Region, Capacity). |
| `data/master/` | `ground_truth_mapping.csv` | 555 | Ground-truth mapping linking every raw variant to its canonical entity. |
| `data/raw/` | `raw_master_data.csv` | 620 | Audited raw master-data feed containing canonical and noisy variants. |
| `data/reconciled/` | `reconciled_master_data.csv` | 620 | Output of reconciliation pipeline with normalized text and match scores. |
| `data/processed/` | `reconciliation_report.csv` | 8 | Formal validation audit report of reconciliation performance metrics. |
| `data/raw/` | `raw_branch.csv` | 91,250 | **Raw Branch Dataset:** Operational records joined with noisy raw master data (15% inconsistent). |
| `data/reconciled/` | `reconciled_branch.csv` | 91,250 | **Reconciled Branch Dataset:** Operational records joined with reconciled canonical master data. |

### 9. Downstream Dual-Branch Analytical Impact
In `raw_branch.csv`, un-reconciled descriptive attributes fragment individual products (e.g., `Product 1`, `product 1`, `Prod 1` appear as distinct entities when grouped by name). In `reconciled_branch.csv`, reconciliation consolidates these records back into the unified canonical entity. 

Because both datasets preserve the exact same operational numbers, any divergence in downstream demand forecasting, safety stock, and transfer planning can be directly attributed to **master-data quality**.

