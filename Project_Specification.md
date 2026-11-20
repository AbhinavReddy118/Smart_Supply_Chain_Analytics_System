# Smart Supply Chain Analytics System

## 1. Project Overview

The project is a data-quality-aware supply chain analytics and decision-support system.

The system combines:

1. Data Acquisition and Validation
2. Master Data Reconciliation
3. Raw vs Reconciled Dual-Branch Analysis
4. Demand Forecasting
5. Inventory Optimization
6. Supply Planning

The final system will provide an interactive dashboard for comparing the results obtained from raw and reconciled supply-chain data.

The project is not only a demand forecasting system. The main research focus is to investigate whether improving master-data quality through reconciliation can improve downstream forecasting, inventory decisions, and supply-planning results.

---

## 2. Main Research Question

Does improving supply-chain master-data quality through reconciliation produce measurable improvements in demand forecasting, inventory optimization, and supply planning?

---

## 3. Core Research Idea

The system must preserve both versions of the data:

- Raw Data
- Reconciled Data

The same downstream analytical procedures must be applied to both branches so that their results can be compared fairly.

The comparison must not use different models or different processing rules for the two branches unless explicitly required.

The final system should be able to show:

Raw Data
→ Forecasting
→ Inventory Optimization
→ Supply Planning

versus

Reconciled Data
→ Forecasting
→ Inventory Optimization
→ Supply Planning

---

## 4. Dataset Strategy

A project-level supply-chain dataset will be created by combining the useful characteristics and fields available in the existing project datasets.

The final dataset must be internally consistent and suitable for all six project modules.

The dataset should contain information related to:

### Product

- Product_ID
- Product_Name
- Category

### Supplier

- Supplier_ID
- Supplier_Name
- Supplier_Lead_Time_Days

### Warehouse

- Warehouse_ID
- Warehouse_Name
- Region
- Warehouse_Capacity

### Demand / Sales

- Date
- Product_ID
- Warehouse_ID
- Units_Sold

### Inventory

- Inventory_Level
- Reorder_Point
- Order_Quantity

### Cost

- Unit_Cost
- Unit_Price

### Operations

- Promotion_Flag
- Stockout_Flag

Additional fields may be included when they are required by inventory optimization or supply planning.

Fields must not be added merely to make the dataset larger.

---

## 5. Dataset Construction

The dataset must be constructed in two conceptual forms.

### 5.1 Clean Reference Dataset

The clean dataset represents the correct underlying supply-chain information.

It will be used as the reference or ground truth for validating the reconciliation process.

The clean dataset should contain consistent:

- Product IDs
- Product names
- Supplier IDs
- Supplier names
- Warehouse IDs
- Warehouse names

and realistic operational data for demand, inventory, procurement, and supply planning.

### 5.2 Raw Dataset

The raw dataset will simulate real-world master-data quality problems.

Controlled inconsistencies may be introduced into master-data fields such as:

- Product_Name
- Supplier_Name
- Warehouse_Name

Examples:

"Coca Cola"
"Coca-Cola"
"coca cola"
"COCA COLA"
"Coca Cola "

These variations should represent the same underlying entity.

The system must NOT randomly modify business measurements such as Units_Sold, Inventory_Level, Unit_Cost, or Unit_Price merely to create differences between raw and reconciled data.

The main injected inconsistencies should represent master-data quality problems.

---

## 6. Ground-Truth Mapping

When controlled inconsistencies are generated, the system must retain the correct relationship between each inconsistent raw value and its canonical entity.

Example:

Raw Value | Canonical ID
Coca-Cola | P001
coca cola | P001
COCA COLA | P001

This mapping must be available for evaluating reconciliation accuracy but should not be directly used by the reconciliation algorithm during normal processing.

---

## 7. Module 1: Data Acquisition and Validation

The system must accept the raw supply-chain dataset and perform validation.

Validation should include:

- Missing-value detection
- Duplicate-row detection
- Data-type validation
- Date validation
- Invalid identifier detection
- Basic consistency checks

The original raw data must be preserved.

Outputs:

- Validation report
- Cleaned working copy where appropriate
- Data-quality summary

---

## 8. Module 2: Master Data Reconciliation

The reconciliation module must identify inconsistent or duplicate master-data entities.

The initial implementation may use:

- text normalization
- case standardization
- whitespace handling
- punctuation normalization
- similarity matching
- configurable similarity thresholds

The system must map similar raw records to canonical entities when the matching confidence is sufficient.

Outputs:

- Reconciled product master
- Reconciled supplier master
- Reconciled warehouse master where required
- Reconciliation mapping
- Reconciliation summary

The system should retain the relationship between original and reconciled records.

---

## 9. Module 3: Dual-Branch Analysis

After reconciliation, the system must preserve two analysis branches.

### Raw Branch

Original validated raw data is used for downstream analysis.

### Reconciled Branch

Reconciled data is used for downstream analysis.

Both branches must use comparable processing and analytical methods.

The purpose is to measure the downstream effect of master-data reconciliation.

---

## 10. Module 4: Demand Forecasting

Demand forecasting will use historical demand information.

Potential features include:

- Historical Units_Sold
- Lag features
- Rolling statistics
- Time-based features
- Seasonality indicators
- Promotion information where applicable

Forecasting performance must be evaluated using appropriate metrics.

Primary metrics:

- MAE
- RMSE
- MAPE

The first implementation should establish a reliable baseline model before adding more complex models.

Candidate models may include:

- XGBoost
- LightGBM
- LSTM
- GRU
- CNN-LSTM

Model selection must be based on actual evaluation results, not assumed performance.

---

## 11. Module 5: Inventory Optimization

Inventory decisions must use forecast demand together with relevant inventory and lead-time information.

The module may calculate:

- Safety Stock
- Reorder Point
- Inventory Requirement
- Stockout Risk
- Excess Inventory indicators

The exact formulas must be documented in the implementation.

The same inventory logic must be applied to both raw and reconciled branches.

---

## 12. Module 6: Supply Planning

Supply planning must use warehouse-level demand and inventory information.

The system should identify:

- Warehouses with potential shortages
- Warehouses with potential surplus
- Inventory imbalances
- Potential transfer recommendations

Where the available data supports it, transfer recommendations may consider:

- Available inventory
- Warehouse capacity
- Transfer cost
- Transfer lead time
- Expected demand

The same planning logic must be applied to both raw and reconciled branches.

---

## 13. Comparative Analysis

The system must compare raw and reconciled results.

Comparison areas include:

### Data Quality

- Duplicate entities
- Inconsistent entity names
- Reconciliation counts

### Forecasting

- MAE
- RMSE
- MAPE

### Inventory

- Safety stock
- Reorder requirements
- Stockout risk
- Excess inventory

### Supply Planning

- Warehouse shortages
- Warehouse surplus
- Transfer recommendations

The comparison must clearly show whether reconciliation produced an improvement, no significant change, or an unexpected result.

The system must not assume that reconciliation will always improve every metric.

---

## 14. Dashboard

The dashboard should present:

1. Overall data-quality status
2. Reconciliation results
3. Raw vs reconciled forecasting performance
4. Inventory insights
5. Supply-planning insights
6. Comparative metrics
7. Warehouse-level analysis where applicable

The dashboard should make the Raw vs Reconciled experiment clearly visible.

---

## 15. Implementation Order

Development must proceed incrementally.

### Phase 1
Inspect and understand all existing datasets.

### Phase 2
Define the final dataset schema.

### Phase 3
Create the clean reference dataset.

### Phase 4
Generate the controlled raw/inconsistent dataset.

### Phase 5
Implement data validation.

### Phase 6
Implement master-data reconciliation.

### Phase 7
Validate reconciliation against the known ground truth.

### Phase 8
Create raw and reconciled analysis branches.

### Phase 9
Implement baseline demand forecasting.

### Phase 10
Implement inventory optimization.

### Phase 11
Implement supply planning.

### Phase 12
Run the same analytical pipeline on both branches.

### Phase 13
Generate comparative results.

### Phase 14
Build the dashboard.

### Phase 15
Add additional forecasting models and refinements if required.

---

## 16. Important Development Rules

Do not build the entire project in one step.

Each module must be implemented and tested independently before moving to the next module.

Do not hide errors or silently modify data.

Do not randomly alter business values to manufacture differences between raw and reconciled results.

Do not assume reconciliation improves forecasting or inventory performance.

All improvements must be supported by actual experimental results.

Keep raw data unchanged.

Keep intermediate datasets and results so that the workflow can be reproduced.

Keep configuration values such as similarity thresholds outside the main processing logic where practical.

---

## 17. Expected Project Outputs

The final project should produce:

- Clean reference dataset
- Raw/inconsistent dataset
- Reconciled dataset
- Validation report
- Reconciliation report
- Raw forecasting results
- Reconciled forecasting results
- Raw inventory results
- Reconciled inventory results
- Raw supply-planning results
- Reconciled supply-planning results
- Comparative analysis
- Interactive dashboard

---

## 18. Current Development Status

The project is currently at the planning and dataset-design stage.

Do not begin full application development until:

1. Existing datasets have been inspected.
2. Final dataset requirements have been defined.
3. The final schema has been approved.
4. The raw vs reconciled experimental design has been confirmed.
5. The clean reference dataset has been created and validated.

After these are complete, implementation should proceed module by module.