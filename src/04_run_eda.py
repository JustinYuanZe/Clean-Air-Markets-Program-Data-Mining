import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_eda():
    input_file = "data/processed/filtered_active_emissions.csv"
    print(f"Loading filtered active dataset: {input_file}...")
    df = pd.read_csv(input_file, low_memory=False)
    
    os.makedirs("reports/plots", exist_ok=True)
    
    # 1. Metadata and Column overview
    n_rows, n_cols = df.shape
    columns_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null = df[col].count()
        null_count = df[col].isnull().sum()
        unique_vals = df[col].nunique()
        columns_info.append((col, dtype, non_null, null_count, unique_vals))
    
    # 2. Descriptive statistics
    num_cols = [
        'sum_of_the_operating_time', 'gross_load_mwh', 'steam_load_1000_lb',
        'so2_mass_short_tons', 'so2_rate_lbs_mmbtu', 'co2_mass_short_tons',
        'co2_rate_short_tons_mmbtu', 'nox_mass_short_tons', 'nox_rate_lbs_mmbtu',
        'heat_input_mmbtu'
    ]
    
    desc_stats = df[num_cols].describe(percentiles=[.25, .5, .75, .9, .95, .99]).T
    desc_stats['skewness'] = df[num_cols].skew()
    desc_stats['kurtosis'] = df[num_cols].kurt()
    desc_stats['variance'] = df[num_cols].var()
    
    # 3. Categorical value distributions
    cat_cols = ['state', 'primary_fuel_type', 'unit_type']
    cat_stats = {}
    for col in cat_cols:
        counts = df[col].value_counts()
        pcts = df[col].value_counts(normalize=True) * 100
        cat_stats[col] = pd.DataFrame({'count': counts, 'percentage': pcts})
        
    # 4. Correlation Matrix
    corr_matrix = df[num_cols].corr()
    
    # 5. Visualizations
    print("Generating visualizations...")
    
    # Heatmap
    plt.figure(figsize=(10, 8))
    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.matshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    fig.colorbar(cax)
    
    ticks = np.arange(0, len(num_cols), 1)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_xticklabels(num_cols, rotation=45, ha='left', fontsize=8)
    ax.set_yticklabels(num_cols, fontsize=8)
    
    for i in range(len(num_cols)):
        for j in range(len(num_cols)):
            ax.text(j, i, f"{corr_matrix.iloc[i, j]:.2f}", ha='center', va='center', color='black', fontsize=8)
            
    plt.title("Pearson Correlation Matrix", y=1.15, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("reports/plots/correlation_matrix.png", dpi=300)
    plt.close()
    
    # Fuel emissions
    fuel_grouped = df.groupby('primary_fuel_type')[['co2_mass_short_tons', 'so2_mass_short_tons', 'nox_mass_short_tons']].mean()
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    
    metrics = ['co2_mass_short_tons', 'so2_mass_short_tons', 'nox_mass_short_tons']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    titles = ['Average CO2 Emissions (short tons)', 'Average SO2 Emissions (short tons)', 'Average NOx Emissions (short tons)']
    
    for i, (metric, color, title) in enumerate(zip(metrics, colors, titles)):
        fuel_grouped[metric].plot(kind='barh', ax=axes[i], color=color)
        axes[i].set_title(title, fontsize=12, fontweight='bold')
        axes[i].set_xlabel('Mean Mass per Operating Day')
        axes[i].set_ylabel('')
        axes[i].grid(axis='x', linestyle='--', alpha=0.7)
        
    plt.tight_layout()
    plt.savefig("reports/plots/emissions_by_fuel.png", dpi=300)
    plt.close()
    
    # Hexbin scatter
    plt.figure(figsize=(8, 6))
    plt.hexbin(df['heat_input_mmbtu'], df['gross_load_mwh'], gridsize=50, cmap='inferno', mincnt=1)
    plt.colorbar(label='Count of Observations')
    plt.title("Operational Efficiency: Gross Load vs Heat Input", fontsize=12, fontweight='bold')
    plt.xlabel("Heat Input (mmBtu)")
    plt.ylabel("Gross Load (MWh)")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("reports/plots/gross_load_vs_heat_input.png", dpi=300)
    plt.close()
    
    print("Writing EDA report...")
    with open("reports/EDA_Report.md", "w", encoding="utf-8") as f:
        f.write("# Exploratory Data Analysis (EDA) Report\n\n")
        f.write("This report provides a detailed exploratory analysis of the cleaned and filtered daily emissions dataset containing active rows only.\n\n")
        f.write("## 1. Dataset Overview\n\n")
        f.write(f"- **Total Rows**: {n_rows}\n")
        f.write(f"- **Total Columns**: {n_cols}\n\n")
        
        f.write("| Feature Label | Data Type | Non-Null Count | Null Count | Unique Count |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for info in columns_info:
            f.write(f"| `{info[0]}` | {info[1]} | {info[2]} | {info[3]} | {info[4]} |\n")
        f.write("\n")
        
        f.write("## 2. Descriptive Statistics (Numerical Columns)\n\n")
        f.write("| Metric Feature | Mean | Std Dev | Min | 25% | 50% (Median) | 75% | 90% | 95% | 99% | Max | Skewness | Kurtosis | Variance |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for index, row in desc_stats.iterrows():
            f.write(f"| `{index}` | {row['mean']:.2f} | {row['std']:.2f} | {row['min']:.2f} | {row['25%']:.2f} | {row['50%']:.2f} | {row['75%']:.2f} | {row['90%']:.2f} | {row['95%']:.2f} | {row['99%']:.2f} | {row['max']:.2f} | {row['skewness']:.2f} | {row['kurtosis']:.2f} | {row['variance']:.2e} |\n")
        f.write("\n")
        
        f.write("## 3. Categorical Distributions\n\n")
        for key, value in cat_stats.items():
            f.write(f"### Distribution of `{key}`\n\n")
            f.write(f"| `{key}` Category | Count | Percentage (%) |\n")
            f.write("| :--- | :---: | :---: |\n")
            for cat, r in value.iterrows():
                f.write(f"| {cat} | {r['count']} | {r['percentage']:.2f}% |\n")
            f.write("\n")
            
        f.write("## 4. Visualizations & Interpretations\n\n")
        f.write("### A. Pearson Correlation Heatmap\n")
        f.write("![Pearson Correlation Heatmap](plots/correlation_matrix.png)\n\n")
        f.write("### B. Emissions Profile by Fuel Type\n")
        f.write("![Emissions Profile by Fuel Type](plots/emissions_by_fuel.png)\n\n")
        f.write("### C. Gross Load vs Heat Input density\n")
        f.write("![Gross Load vs Heat Input](plots/gross_load_vs_heat_input.png)\n\n")
        
    print("EDA Report and Visualizations successfully generated!")

if __name__ == "__main__":
    run_eda()
