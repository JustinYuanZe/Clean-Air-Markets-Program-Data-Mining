import pandas as pd
import os
import re

def clean_column_name(col):
    c = col.strip().lower()
    c = re.sub(r'[^\w\s]', '_', c)
    c = re.sub(r'[\s_]+', '_', c)
    return c.strip('_')

def clean_data():
    raw_dir = "data/raw"
    files = os.listdir(raw_dir)
    pattern = re.compile(r"q1_(\d{4})\.csv")
    
    datasets = {}
    for filename in files:
        match = pattern.match(filename)
        if match:
            year = match.group(1)
            datasets[year] = os.path.join(raw_dir, filename)
            
    if not datasets:
        print("No raw datasets found matching q1_XXXX.csv inside data/raw/")
        return
        
    years = sorted(list(datasets.keys()))
    print(f"Found raw datasets: {years}")
    
    os.makedirs("data/processed", exist_ok=True)
    
    for year in years:
        filepath = datasets[year]
        print(f"\n--- Cleaning {year} Dataset: {filepath} ---")
        df = pd.read_csv(filepath, low_memory=False)
        
        # 1. Drop columns with >80% missingness
        null_pct = (df.isnull().sum() / len(df)) * 100
        cols_to_drop = null_pct[null_pct > 80.0].index.tolist()
        if cols_to_drop:
            print(f"  Dropping columns with >80% missingness: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)
            
        # 2. Drop rows where Operating Time Count is missing or 0
        op_col = 'Operating Time Count'
        if op_col in df.columns:
            initial_rows = len(df)
            df = df[df[op_col].notnull() & (df[op_col] > 0)]
            print(f"  Dropping non-operating rows: {initial_rows} -> {len(df)} (Dropped {initial_rows - len(df)} rows)")
            
        # 3. Clean Column Names
        original_cols = list(df.columns)
        cleaned_cols = [clean_column_name(col) for col in original_cols]
        df.columns = cleaned_cols
        
        # 4. Separate and Impute
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        
        if 'date' in cat_cols:
            cat_cols.remove('date')
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
        for col in cat_cols:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                df[col] = df[col].fillna('None')
                print(f"  Categorical '{col}': Imputed {null_count} NaNs with 'None'")
                
        for col in num_cols:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                df[col] = df[col].fillna(0.0)
                print(f"  Numerical '{col}': Imputed {null_count} NaNs with 0.0")
                
        # 5. Export
        output_file = f"data/processed/cleaned_daily_emissions_{year}.csv"
        df.to_csv(output_file, index=False)
        print(f"Successfully saved cleaned dataset for {year}: {output_file}")

if __name__ == "__main__":
    clean_data()
