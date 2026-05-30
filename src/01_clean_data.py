import pandas as pd
import os
import re

def clean_column_name(col):
    c = col.strip().lower()
    c = re.sub(r'[^\w\s]', '_', c)
    c = re.sub(r'[\s_]+', '_', c)
    return c.strip('_')

def clean_data():
    input_file = "data/raw/daily-emissions-f436a512-59f3-466a-9dd4-bc31cafbbb3a.csv"
    print(f"Loading dataset: {input_file}...")
    
    df = pd.read_csv(input_file, low_memory=False)
    
    # 1. Clean Column Names
    original_cols = list(df.columns)
    cleaned_cols = [clean_column_name(col) for col in original_cols]
    df.columns = cleaned_cols
    
    # 2. Data Cleaning
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    
    if 'date' in cat_cols:
        cat_cols.remove('date')
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
    for col in cat_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            df[col] = df[col].fillna('None')
            
    for col in num_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            df[col] = df[col].fillna(0.0)
            
    # 3. Export to processed format
    os.makedirs("data/processed", exist_ok=True)
    output_file = "data/processed/cleaned_daily_emissions.csv"
    df.to_csv(output_file, index=False)
    print(f"Successfully cleaned and saved standard CSV: {output_file}")

if __name__ == "__main__":
    clean_data()
