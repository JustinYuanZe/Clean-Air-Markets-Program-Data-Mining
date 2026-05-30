import os
import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import math

def round_up_to_clean(val):
    if val <= 0:
        return 1.0
    magnitude = 10 ** int(math.log10(val))
    ratio = val / magnitude
    if ratio <= 1.2:
        return 1.2 * magnitude
    elif ratio <= 1.5:
        return 1.5 * magnitude
    elif ratio <= 2.0:
        return 2.0 * magnitude
    elif ratio <= 5.0:
        return 5.0 * magnitude
    else:
        return 10.0 * magnitude

def run_eda():
    # 1. Dynamic Discovery of Processed Datasets
    processed_dir = "data/processed"
    files = os.listdir(processed_dir)
    pattern = re.compile(r"filtered_active_emissions_(\d{4})\.csv")
    
    datasets = {}
    for filename in files:
        match = pattern.match(filename)
        if match:
            year = match.group(1)
            datasets[year] = os.path.join(processed_dir, filename)
            
    if not datasets:
        print("No processed datasets found matching filtered_active_emissions_XXXX.csv")
        return
        
    years = sorted(list(datasets.keys()))
    print(f"Found active datasets for years: {years}")
    
    os.makedirs("reports/plots", exist_ok=True)
    
    # Target columns
    metrics = ['co2_mass_short_tons', 'so2_mass_short_tons', 'nox_mass_short_tons']
    num_cols = [
        'sum_of_the_operating_time', 'gross_load_mwh', 'steam_load_1000_lb',
        'so2_mass_short_tons', 'so2_rate_lbs_mmbtu', 'co2_mass_short_tons',
        'co2_rate_short_tons_mmbtu', 'nox_mass_short_tons', 'nox_rate_lbs_mmbtu',
        'heat_input_mmbtu'
    ]
    
    # 2. First-Pass Analysis to determine Global Limits
    print("\n--- First-Pass Analysis (Determining Global Scales) ---")
    global_max_avg_emissions = {m: 0.0 for m in metrics}
    global_max_heat_input = 0.0
    global_max_gross_load = 0.0
    global_max_bin_count = 0
    
    loaded_data = {}
    
    for year in years:
        filepath = datasets[year]
        print(f"Profiling {year} for scale parameters...")
        df = pd.read_csv(filepath, low_memory=False)
        loaded_data[year] = df
        
        # Track max average for Bar Charts
        fuel_grouped = df.groupby('primary_fuel_type')[metrics].mean()
        for metric in metrics:
            max_avg = fuel_grouped[metric].max()
            if max_avg > global_max_avg_emissions[metric]:
                global_max_avg_emissions[metric] = max_avg
                
        # Track max parameters for Hexbin Scatter Axis Limits
        max_heat = df['heat_input_mmbtu'].max()
        max_load = df['gross_load_mwh'].max()
        if max_heat > global_max_heat_input:
            global_max_heat_input = max_heat
        if max_load > global_max_gross_load:
            global_max_gross_load = max_load
            
        # Track max bin count for Hexbin colorbar limit (vmax)
        plt.figure()
        hb = plt.hexbin(df['heat_input_mmbtu'], df['gross_load_mwh'], gridsize=50, mincnt=1)
        max_bin = hb.get_array().max()
        plt.close()
        if max_bin > global_max_bin_count:
            global_max_bin_count = max_bin
            
    # Calculate Rounded clean limits
    global_emissions_limits = {m: round_up_to_clean(global_max_avg_emissions[m]) for m in metrics}
    global_heat_input_limit = round_up_to_clean(global_max_heat_input)
    global_gross_load_limit = round_up_to_clean(global_max_gross_load)
    
    print("\nCalculated Global Plot Scale Limits (applicable across all datasets):")
    print(f"  Hexbin X-axis (heat_input_mmbtu) Max Limit: {global_heat_input_limit:.2f} (Actual max: {global_max_heat_input:.2f})")
    print(f"  Hexbin Y-axis (gross_load_mwh) Max Limit: {global_gross_load_limit:.2f} (Actual max: {global_max_gross_load:.2f})")
    print(f"  Hexbin Colorbar Max Density Count: {global_max_bin_count} (vmax)")
    for metric in metrics:
         print(f"  Bar Chart X-axis ({metric}) Max Limit: {global_emissions_limits[metric]:.2f} (Actual max: {global_max_avg_emissions[metric]:.2f})")
         
    # 3. Second-Pass: Render Report and Visualizations
    for year in years:
        df = loaded_data[year]
        print(f"\n--- Generating EDA Report and Unified Plots for {year} ---")
        
        # A. Metadata and Column overview
        n_rows, n_cols = df.shape
        columns_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null = df[col].count()
            null_count = df[col].isnull().sum()
            unique_vals = df[col].nunique()
            columns_info.append((col, dtype, non_null, null_count, unique_vals))
        
        # B. Descriptive statistics
        desc_stats = df[num_cols].describe(percentiles=[.25, .5, .75, .9, .95, .99]).T
        desc_stats['skewness'] = df[num_cols].skew()
        desc_stats['kurtosis'] = df[num_cols].kurt()
        desc_stats['variance'] = df[num_cols].var()
        
        # C. Categorical distributions
        cat_cols = ['state', 'primary_fuel_type', 'unit_type']
        cat_stats = {}
        for col in cat_cols:
            counts = df[col].value_counts()
            pcts = df[col].value_counts(normalize=True) * 100
            cat_stats[col] = pd.DataFrame({'count': counts, 'percentage': pcts})
            
        # D. Correlation Matrix
        corr_matrix = df[num_cols].corr()
        
        # E. Visualizations
        print(f"[{year}] Saving plots...")
        
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
                
        plt.title(f"{year} Pearson Correlation Matrix", y=1.15, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f"reports/plots/correlation_matrix_{year}.png", dpi=300)
        plt.close()
        
        # Fuel emissions Bar Chart (Applying Unified Scale xlim)
        fuel_grouped = df.groupby('primary_fuel_type')[metrics].mean()
        fig, axes = plt.subplots(3, 1, figsize=(10, 12))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        titles = ['Average CO2 Emissions (short tons)', 'Average SO2 Emissions (short tons)', 'Average NOx Emissions (short tons)']
        
        for i, (metric, color, title) in enumerate(zip(metrics, colors, titles)):
            fuel_grouped[metric].plot(kind='barh', ax=axes[i], color=color)
            axes[i].set_title(title, fontsize=12, fontweight='bold')
            axes[i].set_xlabel('Mean Mass per Operating Day')
            axes[i].set_ylabel('')
            axes[i].set_xlim(0, global_emissions_limits[metric])  # Applying unified scaling limit!
            axes[i].grid(axis='x', linestyle='--', alpha=0.7)
            
        plt.tight_layout()
        plt.savefig(f"reports/plots/emissions_by_fuel_{year}.png", dpi=300)
        plt.close()
        
        # Hexbin Scatter Plot (Applying Unified Scale xlim, ylim, colorbar vmax)
        plt.figure(figsize=(8, 6))
        hb = plt.hexbin(
            df['heat_input_mmbtu'], 
            df['gross_load_mwh'], 
            gridsize=50, 
            cmap='inferno', 
            mincnt=1,
            vmax=global_max_bin_count  # Applying unified colorbar limit!
        )
        plt.colorbar(hb, label='Count of Observations')
        plt.xlim(0, global_heat_input_limit)   # Applying unified X axis limit!
        plt.ylim(0, global_gross_load_limit)   # Applying unified Y axis limit!
        plt.title(f"Operational Efficiency: {year} Gross Load vs Heat Input", fontsize=12, fontweight='bold')
        plt.xlabel("Heat Input (mmBtu)")
        plt.ylabel("Gross Load (MWh)")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(f"reports/plots/gross_load_vs_heat_input_{year}.png", dpi=300)
        plt.close()
        
        # Write Report
        report_file = f"reports/EDA_Report_{year}.md"
        print(f"[{year}] Writing EDA report: {report_file}...")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"# Exploratory Data Analysis (EDA) Report ({year})\n\n")
            f.write(f"This report provides a detailed exploratory analysis of the cleaned and filtered daily emissions dataset containing active rows only for the year {year}. Visual scales are dynamically aligned across all years to support visual comparison.\n\n")
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
                
            f.write("## 4. Visualizations & Interpretations (Unified Scaling Enforced)\n\n")
            f.write("### A. Pearson Correlation Heatmap\n")
            f.write(f"![Pearson Correlation Heatmap](plots/correlation_matrix_{year}.png)\n\n")
            f.write("### B. Emissions Profile by Fuel Type\n")
            f.write(f"This bar chart displays the mean emissions grouped by fuel. To avoid visual comparison distortion, the x-axis scale has been locked to a clean, rounded global maximum limit of: CO2={global_emissions_limits['co2_mass_short_tons']:.0f}, SO2={global_emissions_limits['so2_mass_short_tons']:.1f}, NOx={global_emissions_limits['nox_mass_short_tons']:.1f} short tons.\n\n")
            f.write(f"![Emissions Profile by Fuel Type](plots/emissions_by_fuel_{year}.png)\n\n")
            f.write("### C. Gross Load vs Heat Input density\n")
            f.write(f"This operational density hexbin plot has shared X-axis limits (0 to {global_heat_input_limit:.0f} mmBtu), Y-axis limits (0 to {global_gross_load_limit:.0f} MWh), and colorbar limits (0 to {global_max_bin_count} observation count) to allow clear visualization of operational efficiency and density shifts.\n\n")
            f.write(f"![Gross Load vs Heat Input](plots/gross_load_vs_heat_input_{year}.png)\n\n")
            
        print(f"[{year}] EDA Report and Visualizations successfully generated!")
        
    print("\nAll tasks completed successfully!")

if __name__ == "__main__":
    run_eda()
