# Statistical Analysis of Economic Growth and Its Determinants in India

**Data Source:** World Bank World Development Indicators (WDI)  
**Country:** India (Code: IND)  
**Analysis Period:** 1991–2025 (35 annual observations)  
**Report Generated:** 2026-10-07T08:03:33.839526+00:00  

---

## Executive Summary & Key Findings

- Over the period 1991–2025 (35 observations), India's average annual GDP Growth was 6.14% (range: -5.78% to 9.69%).
- Multiple OLS regression accounts for 28.37% of the variance in GDP Growth (R2 = 0.2837, F = 2.2969, p = 0.0710).
- Statistically significant predictors at 5% level: FDI_Net_Inflows (coef = -1.8629, p = 0.0492), Gross_Capital_Formation (coef = 0.3362, p = 0.0403).
- Diagnostic Checks: Durbin-Watson statistic (1.74) indicates no severe autocorrelation, while Breusch-Pagan test (p = 0.1222) confirms homoscedasticity.

---

## 1. Descriptive Statistics

Analysis of annual macroeconomic indicators for India over the period 1991–2025 (35 observations):

| Variable | Count | Mean | Median | Std Dev | Min | Max | Range | Q1 | Q3 | IQR | Skewness | Kurtosis |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GDP_Growth** | 35 | 6.14 | 7.10 | 2.80 | -5.78 | 9.69 | 15.47 | 5.03 | 7.86 | 2.83 | -2.49 | 8.85 |
| **Inflation** | 35 | 6.89 | 6.33 | 3.11 | 2.40 | 13.87 | 11.47 | 4.27 | 9.23 | 4.96 | 0.69 | -0.60 |
| **FDI_Net_Inflows** | 35 | 1.26 | 1.06 | 0.80 | 0.03 | 3.62 | 3.59 | 0.67 | 1.74 | 1.07 | 0.75 | 0.74 |
| **Exports** | 35 | 17.64 | 19.16 | 5.41 | 8.49 | 25.43 | 16.94 | 12.01 | 22.16 | 10.16 | -0.36 | -1.35 |
| **Gross_Capital_Formation** | 35 | 32.10 | 32.12 | 5.17 | 22.72 | 41.95 | 19.23 | 29.04 | 34.85 | 5.81 | 0.00 | -0.80 |
| **Unemployment** | 35 | 7.18 | 7.61 | 1.07 | 4.17 | 7.86 | 3.69 | 7.56 | 7.64 | 0.08 | -2.30 | 3.91 |


## 2. Probability & Distribution Analysis

Evaluation of distribution shape and formal tests for normality:

| Variable | Shapiro-Wilk Stat | Shapiro-Wilk p | Anderson-Darling Stat | Skewness Type | Kurtosis Type | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GDP_Growth** | 0.7735 | 0.0000 | 1.9705 | Negatively Skewed (Left-tailed) | Leptokurtic (Heavy-tailed/Peaked) | Non-normal distribution (use rank/robust methods) |
| **Inflation** | 0.9196 | 0.0139 | 1.0397 | Positively Skewed (Right-tailed) | Platykurtic (Light-tailed/Flat) | Non-normal distribution (use rank/robust methods) |
| **FDI_Net_Inflows** | 0.9545 | 0.1554 | 0.4367 | Positively Skewed (Right-tailed) | Leptokurtic (Heavy-tailed/Peaked) | Normal distribution |
| **Exports** | 0.9034 | 0.0049 | 1.2682 | Symmetric | Platykurtic (Light-tailed/Flat) | Non-normal distribution (use rank/robust methods) |
| **Gross_Capital_Formation** | 0.9691 | 0.4193 | 0.3246 | Symmetric | Platykurtic (Light-tailed/Flat) | Normal distribution |
| **Unemployment** | 0.5024 | 0.0000 | 8.2095 | Negatively Skewed (Left-tailed) | Leptokurtic (Heavy-tailed/Peaked) | Non-normal distribution (use rank/robust methods) |


## 3. Correlation Analysis

Pairwise correlation analysis across 35 annual observations reveals linear (Pearson) and monotonic (Spearman) relationships among economic growth determinants in India. Associations with GDP Growth: Inflation: r = -0.1412 (p = 0.4184, Negative Very Weak / None); FDI_Net_Inflows: r = -0.1189 (p = 0.4962, Negative Very Weak / None); Exports: r = 0.1930 (p = 0.2665, Positive Very Weak / None); Gross_Capital_Formation: r = 0.3180 (p = 0.0626, Positive Weak); Unemployment: r = -0.2095 (p = 0.2270, Negative Weak).

### Pairwise Relationships Table

| Variable 1 | Variable 2 | Pearson r | Pearson p | Spearman rho | Spearman p | N Obs | Relationship | Significant (5%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GDP_Growth** | **Inflation** | -0.1412 | 0.4184 | -0.1331 | 0.4461 | 35 | Negative Very Weak / None | No |
| **GDP_Growth** | **FDI_Net_Inflows** | -0.1189 | 0.4962 | 0.1090 | 0.5332 | 35 | Negative Very Weak / None | No |
| **GDP_Growth** | **Exports** | 0.1930 | 0.2665 | 0.2308 | 0.1822 | 35 | Positive Very Weak / None | No |
| **GDP_Growth** | **Gross_Capital_Formation** | 0.3180 | 0.0626 | 0.4305 | 0.0098 | 35 | Positive Weak | No |
| **GDP_Growth** | **Unemployment** | -0.2095 | 0.2270 | -0.3751 | 0.0264 | 35 | Negative Weak | No |
| **Inflation** | **FDI_Net_Inflows** | -0.0940 | 0.5911 | -0.0950 | 0.5874 | 35 | Negative Very Weak / None | No |
| **Inflation** | **Exports** | -0.2212 | 0.2016 | -0.0401 | 0.8193 | 35 | Negative Weak | No |
| **Inflation** | **Gross_Capital_Formation** | -0.0957 | 0.5844 | -0.0717 | 0.6823 | 35 | Negative Very Weak / None | No |
| **Inflation** | **Unemployment** | 0.2869 | 0.0947 | 0.2320 | 0.1800 | 35 | Positive Weak | No |
| **FDI_Net_Inflows** | **Exports** | 0.6956 | 0.0000 | 0.6787 | 0.0000 | 35 | Positive Strong | Yes |
| **FDI_Net_Inflows** | **Gross_Capital_Formation** | 0.6248 | 0.0001 | 0.6118 | 0.0001 | 35 | Positive Strong | Yes |
| **FDI_Net_Inflows** | **Unemployment** | 0.1113 | 0.5246 | 0.1182 | 0.4988 | 35 | Positive Very Weak / None | No |
| **Exports** | **Gross_Capital_Formation** | 0.8249 | 0.0000 | 0.8255 | 0.0000 | 35 | Positive Very Strong | Yes |
| **Exports** | **Unemployment** | -0.3506 | 0.0389 | -0.0826 | 0.6369 | 35 | Negative Weak | Yes |
| **Gross_Capital_Formation** | **Unemployment** | -0.1558 | 0.3713 | -0.1399 | 0.4227 | 35 | Negative Very Weak / None | No |


## 4. Multiple Linear Regression Model (OLS)

**Dependent Variable:** `GDP_Growth`  
**Independent Variables:** `Inflation, FDI_Net_Inflows, Exports, Gross_Capital_Formation, Unemployment`  

- **R-squared:** 0.2837
- **Adjusted R-squared:** 0.1602
- **F-statistic:** 2.2969 (p-value = 0.0710)
- **Residual Standard Error:** 2.5695
- **Sample Size (N):** 35 complete observations

### Regression Coefficients Table

| Variable | Coefficient | Std Error | t-statistic | p-value | 95% CI Lower | 95% CI Upper | Significant (5%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **const** | -1.468261 | 5.195162 | -0.2826 | 0.7795 | -12.0936 | 9.1570 | No |
| **Inflation** | -0.111795 | 0.150015 | -0.7452 | 0.4621 | -0.4186 | 0.1950 | No |
| **FDI_Net_Inflows** | -1.862890 | 0.907512 | -2.0527 | 0.0492 | -3.7190 | -0.0068 | Yes |
| **Exports** | 0.009283 | 0.194612 | 0.0477 | 0.9623 | -0.3887 | 0.4073 | No |
| **Gross_Capital_Formation** | 0.336227 | 0.156632 | 2.1466 | 0.0403 | 0.0159 | 0.6566 | Yes |
| **Unemployment** | -0.031613 | 0.538356 | -0.0587 | 0.9536 | -1.1327 | 1.0694 | No |


## 5. Regression Diagnostics

Econometric verification of OLS assumptions:

### Diagnostic Tests Summary

| Test | Statistic | p-value | Passed (5%) | Conclusion |
| :--- | :--- | :--- | :--- | :--- |
| **Durbin-Watson Autocorrelation** | 1.7440 | N/A | Yes | No significant autocorrelation (near 2.0) |
| **Breusch-Pagan Heteroscedasticity** | 8.6870 | 0.1222 | Yes | Homoscedasticity satisfied (Constant Error Variance) |
| **Shapiro-Wilk Residual Normality** | 0.9001 | 0.0040 | No | Residuals depart from normal distribution |


### Variance Inflation Factors (VIF)

| Predictor Variable | VIF | Multicollinear Warning | Status |
| :--- | :--- | :--- | :--- |
| **Inflation** | 1.1243 | No | Low Multicollinearity (VIF <= 5) |
| **FDI_Net_Inflows** | 2.6905 | No | Low Multicollinearity (VIF <= 5) |
| **Exports** | 5.7055 | Yes | Moderate Multicollinearity (VIF > 5) |
| **Gross_Capital_Formation** | 3.3786 | No | Low Multicollinearity (VIF <= 5) |
| **Unemployment** | 1.7242 | No | Low Multicollinearity (VIF <= 5) |


## 6. Discussion & Methodological Cautions

> **Caution:** Association vs. Causation: Neither Pearson/Spearman correlation coefficients nor Ordinary Least Squares (OLS) regression parameters demonstrate causal mechanisms. Observed relationships indicate statistical association only.

> **Caution:** Sample Size & Observational Data: Analysis is based on 35 annual time-series observations (1991–2025) for India. Time-series data can be subject to structural breaks, macro shocks (e.g., global recessions), and non-stationarity.

> **Caution:** Model Specification & Omitted Variables: OLS regression results reflect the 5 specified indicators (Inflation, FDI Net Inflows, Exports, Gross Capital Formation, Unemployment). Omitted macroeconomic variables (e.g., fiscal policy, monetary stance, institutional changes) may influence the estimated coefficients.
