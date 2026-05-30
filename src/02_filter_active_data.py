import pandas as pd
import os

def analyze_and_filter():
    input_file = "data/processed/cleaned_daily_emissions.csv"
    print(f"Loading cleaned dataset: {input_file}...")
    df = pd.read_csv(input_file, low_memory=False)
    
    # Filter active operations
    df_filtered = df[(df['sum_of_the_operating_time'] > 0) & (df['heat_input_mmbtu'] > 0)]
    
    print(f"Rows before filter: {df.shape[0]}")
    print(f"Rows after filter: {df_filtered.shape[0]}")
    
    # Save standard filtered dataset
    os.makedirs("data/processed", exist_ok=True)
    output_file = "data/processed/filtered_active_emissions.csv"
    df_filtered.to_csv(output_file, index=False)
    print(f"Successfully filtered and saved standard active-only CSV: {output_file}")

if __name__ == "__main__":
    analyze_and_filter()
