# Clean Air Markets Program - Daily Emissions Data Mining Project

---

## Project & Group Information
* **Course**: 'Data Mining'
* **Project Name**: 'Clean Air Markets Program Daily Emissions Analysis'
* **Team Members**:
  1. Justin
  2. Ha
  3. Darlie
  4. Musa 
  
---

## 1. Repository Overview
This repository contains the data mining process and **Clean Air Markets Program daily emissions dataset** for the first quarter in 2025(~340,000 records) and 2026. 

Our objective is to process a clean dataset, avoiding the inactive operating periods to prevent skewness(NaN, Not Applicable, Not Available,...). And applying some techniques data mining and machine learning to evaluate and analyze the this dataset.

---

## 2. Directory Structure

---

## 3. How to Run the Pipeline
To reproduce the cleaning, filtering, and EDA reports, run the scripts in their numerical order:

```bash
# Step 1: Parse, clean, and resolve nulls in raw CSV
python src/01_clean_data.py

# Step 2: Extract active operation periods to resolve zero-skewness
python src/02_filter_active_data.py

# Step 3: Run comparative data cleanliness profiling
python src/03_run_cleanliness_eda.py

# Step 4: Perform detailed EDA, statistics, and correlation plots
python src/04_run_eda.py
```

---
