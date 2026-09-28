"""
Week 1 Task: Data Acquisition, Cleaning, and Exploratory Data Analysis (EDA)
Project: Virtual Data Science with Python Apprentice Intern
Domain: Customer Retention & Behavioral Analytics (Telco Customer Churn)
Author: Data Science Apprentice
"""

import os
import urllib.request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Set aesthetic visual style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    'font.sans-serif': 'Arial',
    'font.family': 'sans-serif',
    'figure.titlesize': 14,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.autolayout': True
})

DATA_RAW_URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "telco_customer_churn_raw.csv")
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "telco_customer_churn_cleaned.csv")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
METRICS_PATH = os.path.join(BASE_DIR, "data", "processed", "eda_metrics.json")


def acquire_data():
    """Acquires raw dataset from public repository and stores locally."""
    print("=" * 60)
    print("STEP 1: DATA ACQUISITION")
    print("=" * 60)
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Downloading dataset from: {DATA_RAW_URL}...")
        urllib.request.urlretrieve(DATA_RAW_URL, RAW_DATA_PATH)
        print(f"Raw data successfully saved to: {RAW_DATA_PATH}")
    else:
        print(f"Raw data already exists at: {RAW_DATA_PATH}")

    df_raw = pd.read_csv(RAW_DATA_PATH)
    print(f"Acquired dataset shape: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns")
    return df_raw


def clean_and_preprocess(df_raw):
    """
    Performs data cleaning:
    - Whitespace trimming
    - Correcting data types (TotalCharges object -> float)
    - Handling missing values (11 records with whitespace TotalCharges)
    - Deduplication
    - Outlier identification
    - Feature engineering (Tenure cohorts, Total services count)
    """
    print("\n" + "=" * 60)
    print("STEP 2: DATA CLEANING AND PREPROCESSING")
    print("=" * 60)

    df = df_raw.copy()

    # 1. Inspect duplicate records
    dup_count = df.duplicated().sum()
    dup_id_count = df['customerID'].duplicated().sum()
    print(f"Total duplicate rows: {dup_count}")
    print(f"Total duplicate Customer IDs: {dup_id_count}")

    # 2. String trimming
    str_cols = df.select_dtypes(include=['object', 'string']).columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.strip()

    # 3. Detect anomalies in TotalCharges
    # In raw data, new customers with tenure = 0 have empty spaces " "
    raw_missing_charges = (df['TotalCharges'] == '').sum()
    print(f"Blank space values detected in 'TotalCharges': {raw_missing_charges}")

    # Convert TotalCharges to numeric, coercing invalid/empty strings to NaN
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    nan_charges_count = df['TotalCharges'].isna().sum()
    print(f"NaN values after coercion in 'TotalCharges': {nan_charges_count}")

    # Rationale: All records with NaN in TotalCharges have tenure == 0 (newly onboarded customers).
    # Since tenure is 0 months, they have not completed their initial billing cycle.
    # Therefore, imputing TotalCharges with 0.0 is domain-justified and mathematically rigorous.
    tenure_zero_count = (df['tenure'] == 0).sum()
    print(f"Customers with tenure = 0: {tenure_zero_count}")
    df['TotalCharges'] = df['TotalCharges'].fillna(0.0)

    # Verify no null values remain
    remaining_nulls = df.isna().sum().sum()
    print(f"Remaining null values across entire dataset: {remaining_nulls}")

    # 4. Standardize binary / categorical columns
    service_cols = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 
                    'TechSupport', 'StreamingTV', 'StreamingMovies']
    for col in service_cols:
        # Standardize 'No internet service' to 'No' for service subscription count
        df[col + '_Flag'] = df[col].apply(lambda x: 1 if x == 'Yes' else 0)

    df['NumServices'] = df[[c + '_Flag' for c in service_cols]].sum(axis=1)

    # 5. Feature Engineering: Tenure Cohorts
    bins = [-1, 12, 24, 48, 72]
    labels = ['0-12 M (New)', '13-24 M (Developing)', '25-48 M (Established)', '49-72 M (Loyal)']
    df['TenureCohort'] = pd.cut(df['tenure'], bins=bins, labels=labels)

    # Binary numeric churn indicator for correlation analysis
    df['Churn_Numeric'] = df['Churn'].apply(lambda x: 1 if x == 'Yes' else 0)

    # 6. Outlier Analysis using IQR
    numeric_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
    outlier_summary = {}
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_summary[col] = {
            'Q1': round(float(q1), 2),
            'Q3': round(float(q3), 2),
            'IQR': round(float(iqr), 2),
            'LowerBound': round(float(lower_bound), 2),
            'UpperBound': round(float(upper_bound), 2),
            'OutlierCount': int(len(outliers))
        }
        print(f"Feature '{col}': IQR={iqr:.2f}, Outliers count={len(outliers)}")

    # Save cleaned dataset
    os.makedirs(os.path.dirname(CLEANED_DATA_PATH), exist_ok=True)
    df.to_csv(CLEANED_DATA_PATH, index=False)
    print(f"Cleaned dataset saved successfully to: {CLEANED_DATA_PATH}")

    return df, raw_missing_charges, outlier_summary


def generate_visualizations(df, raw_missing_count):
    """
    Generates 5 comprehensive, publication-grade exploratory visualizations:
    - Fig 1: Data Cleaning & Missingness Comparison + Numeric Boxplots
    - Fig 2: Overall Churn Distribution & Demographic Breakdown
    - Fig 3: Contract Type & Payment Method Churn Risk Analysis
    - Fig 4: Tenure & Monthly Charges Distribution (Kernel Density Estimation)
    - Fig 5: Correlation Heatmap of Numeric & Behavioral Features
    """
    print("\n" + "=" * 60)
    print("STEP 3: EXPLORATORY DATA ANALYSIS & VISUALIZATION GENERATION")
    print("=" * 60)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    fig_paths = {}

    # -------------------------------------------------------------------------
    # FIGURE 1: Data Quality & Missingness Analysis
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    
    # Subplot A: Before vs After Missing Values
    missing_data = pd.DataFrame({
        'Stage': ['Raw Data (Uncleaned)', 'Processed Data (Post-Cleaning)'],
        'Missing Values (TotalCharges)': [int(raw_missing_count), 0]
    })
    bars = sns.barplot(data=missing_data, x='Stage', y='Missing Values (TotalCharges)', 
                       hue='Stage', palette=['#e74c3c', '#2ecc71'], ax=axes[0], width=0.45, legend=False)
    axes[0].set_title('Figure 1A: Missing Values in TotalCharges Before vs. After Cleaning', fontsize=11, fontweight='bold')
    axes[0].set_ylabel('Number of Missing / Non-Numeric Values')
    axes[0].set_ylim(0, max(int(raw_missing_count) + 5, 15))
    for bar in bars.patches:
        h = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2., h + 0.5, f'{int(h)}', ha='center', fontweight='bold')

    # Subplot B: Outlier Distribution (Boxplots)
    norm_num = (df[['tenure', 'MonthlyCharges', 'TotalCharges']] - df[['tenure', 'MonthlyCharges', 'TotalCharges']].min()) / \
               (df[['tenure', 'MonthlyCharges', 'TotalCharges']].max() - df[['tenure', 'MonthlyCharges', 'TotalCharges']].min())
    sns.boxplot(data=norm_num, palette="Blues", ax=axes[1], width=0.5)
    axes[1].set_title('Figure 1B: Normalized Numeric Distributions & Outlier Scan', fontsize=11, fontweight='bold')
    axes[1].set_ylabel('Normalized Scale [0, 1]')
    axes[1].set_xticks([0, 1, 2])
    axes[1].set_xticklabels(['Tenure', 'Monthly Charges', 'Total Charges'])

    plt.tight_layout()
    f1_path = os.path.join(FIGURES_DIR, "fig1_missing_values_and_quality.png")
    plt.savefig(f1_path, dpi=300)
    plt.close()
    fig_paths['fig1'] = f1_path
    print(f"Generated: {f1_path}")

    # -------------------------------------------------------------------------
    # FIGURE 2: Churn Distribution & Demographic Breakdown
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Subplot A: Overall Churn Donut
    churn_counts = df['Churn'].value_counts()
    colors = ['#3498db', '#e74c3c']
    axes[0].pie(churn_counts, labels=[f"Retained ({churn_counts['No']})", f"Churned ({churn_counts['Yes']})"],
                autopct='%1.1f%%', startangle=140, colors=colors, explode=(0, 0.07),
                wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2))
    axes[0].set_title('Figure 2A: Overall Customer Churn Ratio', fontsize=12, fontweight='bold')

    # Subplot B: Demographic Churn Comparison
    demog_df = pd.DataFrame([
        {'Demographic': 'Senior: Yes', 'ChurnRate': df[df['SeniorCitizen'] == 1]['Churn_Numeric'].mean() * 100},
        {'Demographic': 'Senior: No', 'ChurnRate': df[df['SeniorCitizen'] == 0]['Churn_Numeric'].mean() * 100},
        {'Demographic': 'Partner: Yes', 'ChurnRate': df[df['Partner'] == 'Yes']['Churn_Numeric'].mean() * 100},
        {'Demographic': 'Partner: No', 'ChurnRate': df[df['Partner'] == 'No']['Churn_Numeric'].mean() * 100},
        {'Demographic': 'Dependents: Yes', 'ChurnRate': df[df['Dependents'] == 'Yes']['Churn_Numeric'].mean() * 100},
        {'Demographic': 'Dependents: No', 'ChurnRate': df[df['Dependents'] == 'No']['Churn_Numeric'].mean() * 100},
    ])
    demog_bars = sns.barplot(data=demog_df, y='Demographic', x='ChurnRate', hue='Demographic', palette='Reds_r', ax=axes[1], legend=False)
    axes[1].set_title('Figure 2B: Churn Rate Across Demographic Cohorts (%)', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Churn Rate (%)')
    axes[1].set_xlim(0, 50)
    for p in demog_bars.patches:
        w = p.get_width()
        axes[1].text(w + 1, p.get_y() + p.get_height()/2., f'{w:.1f}%', va='center', fontweight='bold')

    plt.tight_layout()
    f2_path = os.path.join(FIGURES_DIR, "fig2_churn_distribution_and_demographics.png")
    plt.savefig(f2_path, dpi=300)
    plt.close()
    fig_paths['fig2'] = f2_path
    print(f"Generated: {f2_path}")

    # -------------------------------------------------------------------------
    # FIGURE 3: Contract Type & Payment Method Analysis
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Subplot A: Churn Rate by Contract Type
    contract_churn = df.groupby('Contract')['Churn_Numeric'].agg(Rate='mean', Count='count').reset_index()
    contract_churn['RatePct'] = contract_churn['Rate'] * 100
    b1 = sns.barplot(data=contract_churn, x='Contract', y='RatePct', hue='Contract', palette='Oranges_r', ax=axes[0], legend=False)
    axes[0].set_title('Figure 3A: Churn Rate by Contract Commitment (%)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Churn Rate (%)')
    axes[0].set_ylim(0, 55)
    for p in b1.patches:
        h = p.get_height()
        axes[0].text(p.get_x() + p.get_width()/2., h + 1.2, f'{h:.1f}%', ha='center', fontweight='bold')

    # Subplot B: Churn Rate by Payment Method
    payment_churn = df.groupby('PaymentMethod')['Churn_Numeric'].agg(Rate='mean').reset_index()
    payment_churn['RatePct'] = payment_churn['Rate'] * 100
    payment_churn = payment_churn.sort_values(by='RatePct', ascending=False)
    b2 = sns.barplot(data=payment_churn, y='PaymentMethod', x='RatePct', hue='PaymentMethod', palette='Purples_r', ax=axes[1], legend=False)
    axes[1].set_title('Figure 3B: Churn Rate by Billing/Payment Channel (%)', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Churn Rate (%)')
    axes[1].set_xlim(0, 55)
    for p in b2.patches:
        w = p.get_width()
        axes[1].text(w + 1, p.get_y() + p.get_height()/2., f'{w:.1f}%', va='center', fontweight='bold')

    plt.tight_layout()
    f3_path = os.path.join(FIGURES_DIR, "fig3_contract_and_payment_impact.png")
    plt.savefig(f3_path, dpi=300)
    plt.close()
    fig_paths['fig3'] = f3_path
    print(f"Generated: {f3_path}")

    # -------------------------------------------------------------------------
    # FIGURE 4: Continuous Distributions (Tenure & Monthly Charges)
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    # Subplot A: Tenure KDE distribution by Churn
    sns.kdeplot(data=df[df['Churn'] == 'No']['tenure'], label='Retained', fill=True, color='#2980b9', ax=axes[0], alpha=0.35)
    sns.kdeplot(data=df[df['Churn'] == 'Yes']['tenure'], label='Churned', fill=True, color='#e74c3c', ax=axes[0], alpha=0.35)
    axes[0].set_title('Figure 4A: Customer Tenure Density Distribution (Months)', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Tenure (Months)')
    axes[0].set_ylabel('Density')
    axes[0].legend(title='Status')

    # Subplot B: Monthly Charges KDE distribution by Churn
    sns.kdeplot(data=df[df['Churn'] == 'No']['MonthlyCharges'], label='Retained', fill=True, color='#2980b9', ax=axes[1], alpha=0.35)
    sns.kdeplot(data=df[df['Churn'] == 'Yes']['MonthlyCharges'], label='Churned', fill=True, color='#e74c3c', ax=axes[1], alpha=0.35)
    axes[1].set_title('Figure 4B: Monthly Charges Density Distribution ($)', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Monthly Charges ($)')
    axes[1].set_ylabel('Density')
    axes[1].legend(title='Status')

    plt.tight_layout()
    f4_path = os.path.join(FIGURES_DIR, "fig4_tenure_and_monthly_charges_distribution.png")
    plt.savefig(f4_path, dpi=300)
    plt.close()
    fig_paths['fig4'] = f4_path
    print(f"Generated: {f4_path}")

    # -------------------------------------------------------------------------
    # FIGURE 5: Correlation Heatmap
    # -------------------------------------------------------------------------
    plt.figure(figsize=(10, 7.5))
    corr_cols = ['tenure', 'MonthlyCharges', 'TotalCharges', 'NumServices', 'SeniorCitizen', 'Churn_Numeric']
    corr_matrix = df[corr_cols].corr()
    corr_labels = ['Tenure', 'Monthly Charges', 'Total Charges', 'Services Subscribed', 'Senior Citizen', 'Churn']
    
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1,
                xticklabels=corr_labels, yticklabels=corr_labels, linewidths=1.2, linecolor='white')
    plt.title('Figure 5: Correlation Heatmap of Numerical & Key Behavioral Features', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    f5_path = os.path.join(FIGURES_DIR, "fig5_correlation_heatmap.png")
    plt.savefig(f5_path, dpi=300)
    plt.close()
    fig_paths['fig5'] = f5_path
    print(f"Generated: {f5_path}")

    return fig_paths


def extract_key_metrics(df, raw_missing_count, outlier_summary):
    """Computes and serializes key statistics for inclusion in report."""
    total_customers = len(df)
    churn_count = int(df['Churn_Numeric'].sum())
    churn_rate = float(df['Churn_Numeric'].mean() * 100)
    retained_count = total_customers - churn_count

    # Tenure Cohort Churn Rates
    cohort_churn = df.groupby('TenureCohort', observed=False)['Churn_Numeric'].agg(['count', 'mean']).reset_index()
    cohort_metrics = []
    for _, row in cohort_churn.iterrows():
        cohort_metrics.append({
            'cohort': str(row['TenureCohort']),
            'count': int(row['count']),
            'churn_rate': round(float(row['mean']) * 100, 2)
        })

    # Contract Churn Rates
    contract_churn = df.groupby('Contract')['Churn_Numeric'].agg(['count', 'mean']).reset_index()
    contract_metrics = []
    for _, row in contract_churn.iterrows():
        contract_metrics.append({
            'contract': str(row['Contract']),
            'count': int(row['count']),
            'churn_rate': round(float(row['mean']) * 100, 2)
        })

    # Summary Statistics
    numeric_stats = {}
    for col in ['tenure', 'MonthlyCharges', 'TotalCharges']:
        numeric_stats[col] = {
            'mean': round(float(df[col].mean()), 2),
            'median': round(float(df[col].median()), 2),
            'std': round(float(df[col].std()), 2),
            'min': round(float(df[col].min()), 2),
            'max': round(float(df[col].max()), 2)
        }

    metrics = {
        'total_customers': total_customers,
        'churn_count': churn_count,
        'retained_count': retained_count,
        'churn_rate': round(churn_rate, 2),
        'raw_missing_count': int(raw_missing_count),
        'outlier_summary': outlier_summary,
        'cohort_metrics': cohort_metrics,
        'contract_metrics': contract_metrics,
        'numeric_stats': numeric_stats
    }

    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=4)

    print(f"Metrics serialized to: {METRICS_PATH}")
    return metrics


def main():
    df_raw = acquire_data()
    df_cleaned, raw_missing_count, outlier_summary = clean_and_preprocess(df_raw)
    fig_paths = generate_visualizations(df_cleaned, raw_missing_count)
    metrics = extract_key_metrics(df_cleaned, raw_missing_count, outlier_summary)
    print("\n" + "=" * 60)
    print("DATA PIPELINE & EDA EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"Total Rows: {metrics['total_customers']}, Churn Rate: {metrics['churn_rate']}%")
    print("=" * 60)


if __name__ == "__main__":
    main()
