# Virtual Data Science with Python Apprentice Intern
## Week 1: Data Acquisition, Cleaning, and Exploratory Data Analysis (EDA)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg)
![Seaborn](https://img.shields.io/badge/Seaborn-Visualizations-4c72b0.svg)
![Status](https://img.shields.io/badge/Milestone-Week%201%20Completed-brightgreen.svg)

---

### 📋 Overview
This repository contains the complete deliverables for **Week 1** of the **Virtual Data Science with Python Apprentice Internship**. The objective of this milestone is to simulate the enterprise data preparation and exploratory analysis lifecycle foundational to modern machine learning workflows.

Targeting the **Customer Retention & Churn Analytics** domain, the project programmatically acquires the canonical IBM Watson Telco Customer Churn dataset, performs rigorous data hygiene and domain-grounded preprocessing, and conducts extensive univariate, bivariate, and multivariate Exploratory Data Analysis (EDA).

---

### 📂 Repository Structure
```text
virtual-data-science-internship-week1/
├── analysis_pipeline.py                    # Complete end-to-end Python pipeline (download, clean, EDA)
├── generate_docx_report.py                 # Automated Word document report generator
├── Week1_Data_Acquisition_Cleaning_EDA_Report.docx # Official submission document
├── requirements.txt                        # Python dependencies
├── .gitignore                              # Git exclusion rules
├── README.md                               # Project documentation & findings
├── data/
│   ├── raw/
│   │   └── telco_customer_churn_raw.csv    # Raw dataset (7,043 rows, 21 columns)
│   └── processed/
│       ├── telco_customer_churn_cleaned.csv# Cleaned and engineered dataset
│       └── eda_metrics.json                # Serialized statistical metrics
└── figures/
    ├── fig1_missing_values_and_quality.png # Missing value resolution & boxplots
    ├── fig2_churn_distribution_and_demographics.png # Churn distribution & demographics
    ├── fig3_contract_and_payment_impact.png# Contract types & payment channels
    ├── fig4_tenure_and_monthly_charges_distribution.png # Tenure & monthly charges KDE
    └── fig5_correlation_heatmap.png        # Correlation matrix heatmap
```

---

### 🎯 Key Objectives Met
1. **Public Data Acquisition:** Automated programmatic downloading from IBM Watson's public repository via Python's `urllib.request`.
2. **Data Cleaning & Hygiene:**
   - Identified and stripped trailing/leading whitespace across all string variables.
   - Detected 11 anomalies in `TotalCharges` stored as blank whitespace strings (`" "`).
   - Mathematically and domain-justified imputing `TotalCharges = 0.0` for newly enrolled subscribers with `tenure == 0` (no bills issued yet), avoiding sample loss and survivorship bias.
   - Verified zero duplicate records across 7,043 unique accounts.
   - Outlier diagnosis using Tukey's Interquartile Range (IQR) method (0 spurious outliers).
3. **Feature Engineering:**
   - **Tenure Cohorts:** Binned into `0-12 M (New)`, `13-24 M (Developing)`, `25-48 M (Established)`, and `49-72 M (Loyal)`.
   - **Service Portfolio Breadth (`NumServices`):** Aggregation of 6 optional digital add-on services.
4. **Visual Analytics:** Generated 5 publication-ready, 300-DPI visual charts covering distributions, missingness, contract types, demographic risks, and correlations.
5. **Technical Report:** Compiled a 10-page Word Document (`.docx`) summarizing methodology, code snippets, statistical tables, and strategic recommendations.

---

### 📊 Exploratory Insights Summary

| Metric / Attribute | Observed Value | Strategic Takeaway |
| :--- | :--- | :--- |
| **Total Subscribers** | 7,043 | Sufficient sample size for statistically valid inference |
| **Overall Churn Rate** | 26.54% (1,869 churned) | Moderately imbalanced target variable |
| **New Customer Churn (0-12 M)** | **47.44%** | The "First-Year Cliff": critical onboarding drop-off window |
| **Established Churn (49-72 M)** | **6.60%** | Retention exponentially increases with subscriber tenure |
| **Month-to-Month Churn** | **42.71%** | Highest flight risk contract category |
| **Two-Year Contract Churn** | **2.83%** | Long-term contracts serve as an effective protective moat |
| **Electronic Check Churn** | **45.29%** | Severe payment friction compared to auto-pay (~15-16%) |
| **Senior Citizen Churn** | **41.68%** | 18% higher than non-seniors (requires dedicated support) |

---

### 🚀 Getting Started

#### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/virtual-data-science-internship-week1.git
cd virtual-data-science-internship-week1
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run the End-to-End Pipeline
```bash
python analysis_pipeline.py
```
This automatically fetches raw data, validates schema, applies cleaning, creates engineered features, generates all 5 figures in `figures/`, and outputs `data/processed/telco_customer_churn_cleaned.csv`.

#### 4. Compile the Word Report (.docx)
```bash
python generate_docx_report.py
```
Outputs `Week1_Data_Acquisition_Cleaning_EDA_Report.docx` ready for submission.

---

### 💡 Strategic Business Recommendations
1. **90-Day Onboarding Concierge:** Focus immediate retention interventions on subscribers in months 0-12 to flatten the 47.44% churn cliff.
2. **Auto-Pay Incentivization:** Offer a $5/month billing discount for customers switching from Electronic Check to ACH or Credit Card auto-pay.
3. **Contract Migration Bundles:** Incentivize Month-to-Month customers to transition to 1- or 2-year agreements by bundling free security or streaming services.
4. **Senior Customer Experience Desk:** Create simplified billing and priority technical phone support for Senior Citizens.

---

### 🔮 Future Modeling Roadmap (Week 2 & Beyond)
- One-Hot and Target Encoding for high-cardinality categorical attributes.
- SMOTE & Class-Weight balancing to handle the 73.5% / 26.5% class distribution.
- Supervised classification modeling (Logistic Regression, Random Forest, XGBoost, LightGBM).
- Survival Analysis (Kaplan-Meier curves and Cox Proportional Hazards) for time-to-churn forecasting.

---
**Author:** ksangam990  
**Internship:** Virtual Data Science with Python Apprentice Intern  
**Adherence to Workload:** 32 Hours Logged  
