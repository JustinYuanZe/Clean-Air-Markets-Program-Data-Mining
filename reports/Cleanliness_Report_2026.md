# Data Cleanliness & Profiling Report (2026 - Before vs After)

This report provides a detailed comparison of the data quality (cleanliness) of the raw daily emissions dataset versus the cleaned dataset for the year 2026.

## 1. Cleanliness Audit Summary Table

| Idx | Raw Feature Label | Raw Dtype | Raw Nulls (Count) | Raw Nulls (%) | Cleaned Feature Label | Cleaned Dtype | Cleaned Nulls (Count) | Cleaned Nulls (%) |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- | :---: | :---: |
| 0 | `State` | str | 0 | 0.00% | `state` | str | 0 | 0.00% |
| 1 | `Facility Name` | str | 0 | 0.00% | `facility_name` | str | 0 | 0.00% |
| 2 | `Facility ID` | int64 | 0 | 0.00% | `facility_id` | int64 | 0 | 0.00% |
| 3 | `Unit ID` | str | 0 | 0.00% | `unit_id` | str | 0 | 0.00% |
| 4 | `Associated Stacks` | str | 303,570 | 89.68% | `associated_stacks (Dropped)` | N/A | N/A | N/A |
| 5 | `Date` | str | 0 | 0.00% | `date` | str | 0 | 0.00% |
| 6 | `Operating Time Count` | int64 | 0 | 0.00% | `operating_time_count` | int64 | 0 | 0.00% |
| 7 | `Sum of the Operating Time` | float64 | 82 | 0.02% | `sum_of_the_operating_time` | float64 | 0 | 0.00% |
| 8 | `Gross Load (MWh)` | float64 | 202,049 | 59.69% | `gross_load_mwh` | float64 | 0 | 0.00% |
| 9 | `Steam Load (1000 lb)` | float64 | 329,523 | 97.35% | `steam_load_1000_lb (Dropped)` | N/A | N/A | N/A |
| 10 | `SO2 Mass (short tons)` | float64 | 200,218 | 59.15% | `so2_mass_short_tons` | float64 | 0 | 0.00% |
| 11 | `SO2 Rate (lbs/mmBtu)` | float64 | 200,288 | 59.17% | `so2_rate_lbs_mmbtu` | float64 | 0 | 0.00% |
| 12 | `CO2 Mass (short tons)` | float64 | 200,957 | 59.37% | `co2_mass_short_tons` | float64 | 0 | 0.00% |
| 13 | `CO2 Rate (short tons/mmBtu)` | float64 | 201,006 | 59.38% | `co2_rate_short_tons_mmbtu` | float64 | 0 | 0.00% |
| 14 | `NOx Mass (short tons)` | float64 | 192,825 | 56.97% | `nox_mass_short_tons` | float64 | 0 | 0.00% |
| 15 | `NOx Rate (lbs/mmBtu)` | float64 | 193,412 | 57.14% | `nox_rate_lbs_mmbtu` | float64 | 0 | 0.00% |
| 16 | `Heat Input (mmBtu)` | float64 | 193,323 | 57.11% | `heat_input_mmbtu` | float64 | 0 | 0.00% |
| 17 | `Primary Fuel Type` | str | 0 | 0.00% | `primary_fuel_type` | str | 0 | 0.00% |
| 18 | `Secondary Fuel Type` | str | 213,030 | 62.94% | `secondary_fuel_type` | str | 0 | 0.00% |
| 19 | `Unit Type` | str | 0 | 0.00% | `unit_type` | str | 0 | 0.00% |
| 20 | `SO2 Controls` | str | 306,360 | 90.51% | `so2_controls (Dropped)` | N/A | N/A | N/A |
| 21 | `NOx Controls` | str | 38,700 | 11.43% | `nox_controls` | str | 0 | 0.00% |
| 22 | `PM Controls` | str | 295,830 | 87.40% | `pm_controls (Dropped)` | N/A | N/A | N/A |
| 23 | `Hg Controls` | str | 323,280 | 95.51% | `hg_controls (Dropped)` | N/A | N/A | N/A |
| 24 | `Program Code` | str | 0 | 0.00% | `program_code` | str | 0 | 0.00% |

## 2. Detailed Profiling: The Raw Dataset (Before Cleaning)

### Data Quality Issues Detected:

1. **High Rate of Missing Values**:
   - **SO2 Controls, PM Controls, Hg Controls**: Over **87% to 95%** of the rows were empty (null).
   - **Emissions & Performance metrics**: Approximately **56% to 59%** of rows were missing. This corresponds to days when power units were not operational, leaving blank fields instead of numerical zeroes.
2. **Non-Standard Column Names**:
   - Columns contained uppercase characters, spaces, and brackets/units (e.g. `Gross Load (MWh)`).

## 3. Detailed Profiling: The Cleaned Dataset (After Cleaning)

### Data Quality Enhancements Applied:

1. **Zero Null Values**: All missing values have been programmatically resolved to `'None'` for categoricals and `0.0` for numericals.
2. **Standardized Column Schemas**: Columns converted to lowercase snake_case (e.g., `gross_load_mwh`).
3. **Datatype Consistency**: Enforced explicit numeric/string formats.

## 4. Visual Comparison of Missing Values

![Missing Values Comparison](plots/missing_values_comparison_2026.png)
