# Statistical Analysis of Economic Growth and Its Determinants in India

**Data Source:** World Bank World Development Indicators (WDI)  
**Country:** India (Code: IND)  
**Analysis Period:** 1991–2025 (35 annual observations)  

---

## Executive Summary & Key Findings

• **Dataset & Scope:** Analysis covers 35 annual observations for India (1991–2025) sourced from the World Bank WDI, examining GDP Growth alongside five explanatory macroeconomic determinants (Inflation, FDI Net Inflows, Exports, Gross Capital Formation, and Unemployment).
• **Descriptive Characteristics:** Summarizes central tendency and dispersion across all indicators over the study period (e.g., mean GDP Growth = 6.14%, median = 7.10%, std dev = 2.80%, range = -5.78% to 9.69%).
• **Distribution & Normality:** Shapiro-Wilk and Anderson-Darling tests evaluate distribution properties; 2 of 6 variables show no evidence against normality at α = 0.05, while GDP Growth, Inflation (CPI), Exports, Unemployment exhibit empirical non-normality.
• **Correlation Structure:** Pairwise analysis evaluates linear (Pearson) and monotonic (Spearman) relationships with GDP Growth; the strongest positive linear association is with Gross Capital Formation (r = 0.3180, p = 0.0626), and strongest negative is with Unemployment (r = -0.2095, p = 0.2270).
• **Multiple Linear Regression (OLS):** Fits GDP Growth on all five predictors, accounting for 28.37% of the sample variance (R² = 0.2837, Adjusted R² = 0.1602, overall F-statistic = 2.2969, p = 0.0710).
• **Robust HC3 Inference:** Employs heteroskedasticity-consistent HC3 standard errors for inference, identifying 0 statistically significant predictor(s) at α = 0.05 (none).
• **Econometric Diagnostics:** Tests confirm no strong evidence of first-order autocorrelation (Durbin-Watson = 1.744), no statistically significant heteroskedasticity at α = 0.05 (Breusch-Pagan p = 0.1222), residual non-normality (Shapiro-Wilk p = 0.0040), 2 observation(s) exceeding 4/n ≈ 0.114 Cook's Distance screening threshold (1991, 2020), and maximum VIF = 5.71 (Exports).
• **Methodological Caution:** All observed relationships represent conditional empirical associations in observational time-series data and do not imply causal mechanisms.

---

## 1. Descriptive Statistics

Summary statistics for annual macroeconomic variables in India (1991–2025, n = 35):

| Variable | Count | Mean | Median | Std Dev | Min | Max | Range | Q1 | Q3 | IQR | Skewness | Excess Kurtosis |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GDP Growth** | 35 | 6.14 | 7.10 | 2.80 | -5.78 | 9.69 | 15.47 | 5.03 | 7.86 | 2.83 | -2.49 | 8.85 |
| **Inflation (CPI)** | 35 | 6.89 | 6.33 | 3.11 | 2.40 | 13.87 | 11.47 | 4.27 | 9.23 | 4.96 | 0.69 | -0.60 |
| **FDI Net Inflows** | 35 | 1.26 | 1.06 | 0.80 | 0.03 | 3.62 | 3.59 | 0.67 | 1.74 | 1.07 | 0.75 | 0.74 |
| **Exports** | 35 | 17.64 | 19.16 | 5.41 | 8.49 | 25.43 | 16.94 | 12.01 | 22.16 | 10.16 | -0.36 | -1.35 |
| **Gross Capital Formation** | 35 | 32.10 | 32.12 | 5.17 | 22.72 | 41.95 | 19.23 | 29.04 | 34.85 | 5.81 | 0.00 | -0.80 |
| **Unemployment** | 35 | 7.18 | 7.61 | 1.07 | 4.17 | 7.86 | 3.69 | 7.56 | 7.64 | 0.08 | -2.30 | 3.91 |


## 2. Probability & Distribution Analysis

Parametric distribution characteristics and formal tests for normality:

| Variable | Shapiro-Wilk Stat | Shapiro-Wilk p | Anderson-Darling Stat | Skewness Shape | Kurtosis Shape | Normality Decision (α = 0.05) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GDP Growth** | 0.7735 | < 0.0001 | 1.9705 | Negatively Skewed (Left-tailed) | Leptokurtic (Heavy-tailed/Peaked) | Evidence of non-normality at α = 0.05 |
| **Inflation (CPI)** | 0.9196 | 0.0139 | 1.0397 | Positively Skewed (Right-tailed) | Platykurtic (Light-tailed/Flat) | Evidence of non-normality at α = 0.05 |
| **FDI Net Inflows** | 0.9545 | 0.1554 | 0.4367 | Positively Skewed (Right-tailed) | Leptokurtic (Heavy-tailed/Peaked) | No evidence against normality at α = 0.05 |
| **Exports** | 0.9034 | 0.0049 | 1.2682 | Symmetric | Platykurtic (Light-tailed/Flat) | Evidence of non-normality at α = 0.05 |
| **Gross Capital Formation** | 0.9691 | 0.4193 | 0.3246 | Symmetric | Platykurtic (Light-tailed/Flat) | No evidence against normality at α = 0.05 |
| **Unemployment** | 0.5024 | < 0.0001 | 8.2095 | Negatively Skewed (Left-tailed) | Leptokurtic (Heavy-tailed/Peaked) | Evidence of non-normality at α = 0.05 |


## 3. Correlation Analysis

Pairwise correlation evaluates linear (Pearson r) and monotonic (Spearman rho) relationships across the macroeconomic indicators. Associations with GDP Growth:

- Inflation (CPI) shows no statistically significant association with GDP Growth under either Pearson (r = -0.1412, p = 0.4184) or Spearman (rho = -0.1331, p = 0.4461) measures at α = 0.05.
- FDI Net Inflows shows no statistically significant association with GDP Growth under either Pearson (r = -0.1189, p = 0.4962) or Spearman (rho = 0.1090, p = 0.5332) measures at α = 0.05.
- Exports shows no statistically significant association with GDP Growth under either Pearson (r = 0.1930, p = 0.2665) or Spearman (rho = 0.2308, p = 0.1822) measures at α = 0.05.
- Gross Capital Formation exhibits a statistically significant rank correlation (Spearman rho = 0.4305, p = 0.0098 < 0.05), while its linear association is not statistically significant (Pearson r = 0.3180, p = 0.0626 ≥ 0.05), indicating a monotonic rather than strictly linear association.
- Unemployment exhibits a statistically significant rank correlation (Spearman rho = -0.3751, p = 0.0264 < 0.05), while its linear association is not statistically significant (Pearson r = -0.2095, p = 0.2270 ≥ 0.05), indicating a monotonic rather than strictly linear association.

### Pairwise Relationships Table

| Variable 1 | Variable 2 | Pearson r | Pearson p | Spearman rho | Spearman p | N Obs | Relationship | Significant (5%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GDP Growth** | **Inflation (CPI)** | -0.1412 | 0.4184 | -0.1331 | 0.4461 | 35 | Negative Very Weak / None | No |
| **GDP Growth** | **FDI Net Inflows** | -0.1189 | 0.4962 | 0.1090 | 0.5332 | 35 | Negative Very Weak / None | No |
| **GDP Growth** | **Exports** | 0.1930 | 0.2665 | 0.2308 | 0.1822 | 35 | Positive Very Weak / None | No |
| **GDP Growth** | **Gross Capital Formation** | 0.3180 | 0.0626 | 0.4305 | 0.0098 | 35 | Positive Weak | Yes |
| **GDP Growth** | **Unemployment** | -0.2095 | 0.2270 | -0.3751 | 0.0264 | 35 | Negative Weak | Yes |
| **Inflation (CPI)** | **FDI Net Inflows** | -0.0940 | 0.5911 | -0.0950 | 0.5874 | 35 | Negative Very Weak / None | No |
| **Inflation (CPI)** | **Exports** | -0.2212 | 0.2016 | -0.0401 | 0.8193 | 35 | Negative Weak | No |
| **Inflation (CPI)** | **Gross Capital Formation** | -0.0957 | 0.5844 | -0.0717 | 0.6823 | 35 | Negative Very Weak / None | No |
| **Inflation (CPI)** | **Unemployment** | 0.2869 | 0.0947 | 0.2320 | 0.1800 | 35 | Positive Weak | No |
| **FDI Net Inflows** | **Exports** | 0.6956 | < 0.0001 | 0.6787 | < 0.0001 | 35 | Positive Strong | Yes |
| **FDI Net Inflows** | **Gross Capital Formation** | 0.6248 | < 0.0001 | 0.6118 | < 0.0001 | 35 | Positive Strong | Yes |
| **FDI Net Inflows** | **Unemployment** | 0.1113 | 0.5246 | 0.1182 | 0.4988 | 35 | Positive Very Weak / None | No |
| **Exports** | **Gross Capital Formation** | 0.8249 | < 0.0001 | 0.8255 | < 0.0001 | 35 | Positive Very Strong | Yes |
| **Exports** | **Unemployment** | -0.3506 | 0.0389 | -0.0826 | 0.6369 | 35 | Negative Weak | Yes |
| **Gross Capital Formation** | **Unemployment** | -0.1558 | 0.3713 | -0.1399 | 0.4227 | 35 | Negative Very Weak / None | No |


## 4. Multiple Linear Regression Model (OLS)

**Dependent Variable:** `GDP Growth`  
**Independent Variables:** `Inflation (CPI), FDI Net Inflows, Exports, Gross Capital Formation, Unemployment`  
**Estimated Equation:** `GDP Growth = -1.4683 − 0.1118 × Inflation (CPI) − 1.8629 × FDI Net Inflows + 0.0093 × Exports + 0.3362 × Gross Capital Formation − 0.0316 × Unemployment`  

- **R-squared:** 0.2837
- **Adjusted R-squared:** 0.1602
- **F-statistic:** 2.2969 (p-value = 0.0710)
- **Residual Standard Error:** 2.5695
- **Sample Size (N):** 35 complete annual observations

### Regression Coefficients Table (HC3 Robust SE)

| Variable | Coefficient | HC3 Robust SE | t-statistic | p-value | 95% CI Lower | 95% CI Upper | Significant (5%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Intercept (Constant)** | -1.468261 | 5.243594 | -0.2800 | 0.7815 | -12.1926 | 9.2561 | No |
| **Inflation (CPI)** | -0.111795 | 0.149001 | -0.7503 | 0.4591 | -0.4165 | 0.1929 | No |
| **FDI Net Inflows** | -1.862890 | 1.285579 | -1.4491 | 0.1580 | -4.4922 | 0.7664 | No |
| **Exports** | 0.009283 | 0.149119 | 0.0623 | 0.9508 | -0.2957 | 0.3143 | No |
| **Gross Capital Formation** | 0.336227 | 0.216727 | 1.5514 | 0.1317 | -0.1070 | 0.7795 | No |
| **Unemployment** | -0.031613 | 0.334334 | -0.0946 | 0.9253 | -0.7154 | 0.6522 | No |


### OLS vs HC3 Robust Standard Errors Comparison

| Variable | OLS Coef | OLS SE | OLS p-value | HC3 SE | HC3 p-value | SE Change (%) | HC3 Significant (5%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Intercept (Constant)** | -1.468261 | 5.195162 | 0.7795 | 5.243594 | 0.7815 | +0.93% | No |
| **Inflation (CPI)** | -0.111795 | 0.150015 | 0.4621 | 0.149001 | 0.4591 | -0.68% | No |
| **FDI Net Inflows** | -1.862890 | 0.907512 | 0.0492 | 1.285579 | 0.1580 | +41.66% | No |
| **Exports** | 0.009283 | 0.194612 | 0.9623 | 0.149119 | 0.9508 | -23.38% | No |
| **Gross Capital Formation** | 0.336227 | 0.156632 | 0.0403 | 0.216727 | 0.1317 | +38.37% | No |
| **Unemployment** | -0.031613 | 0.538356 | 0.9536 | 0.334334 | 0.9253 | -37.90% | No |


## 5. Regression Diagnostics

Econometric verification of classical linear regression model assumptions:

### Diagnostic Tests Summary

| Test | Statistic | p-value | Decision / Status | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **Durbin-Watson Autocorrelation** | 1.7440 | N/A | No strong evidence | DW = 1.744; the statistic is reasonably close to 2.0, suggesting no strong evidence of first-order autocorrelation. |
| **Breusch-Pagan Heteroscedasticity** | 8.6870 | 0.1222 | Fail to reject H₀ | No statistically significant evidence of heteroskedasticity at α = 0.05. |
| **Shapiro-Wilk Residual Normality** | 0.9001 | 0.0040 | Reject H₀ | Evidence of non-normality in residuals at α = 0.05. |
| **Cook's Distance (Influential Points)** | 0.6130 | N/A | 2 Exceeding Obs. | 2 observation(s) (1991, 2020) exceed the Cook's D screening threshold (4/n ≈ 0.114). These observations should be examined for influence and contextual validity; exceeding the screening threshold does not by itself imply that the observations are erroneous or should be removed. |


### Variance Inflation Factors (VIF)

| Predictor Variable | VIF | Screening Guideline / Status |
| :--- | :--- | :--- |
| **Inflation (CPI)** | 1.1243 | Low concern (VIF < 5) |
| **FDI Net Inflows** | 2.6905 | Low concern (VIF < 5) |
| **Exports** | 5.7055 | Potential concern (5 ≤ VIF < 10) |
| **Gross Capital Formation** | 3.3786 | Low concern (VIF < 5) |
| **Unemployment** | 1.7242 | Low concern (VIF < 5) |


## 6. Discussion & Methodological Cautions

1. **Descriptive Characteristics & Macroeconomic Volatility:** Over the study period (1991–2025, n = 35), India's annual GDP Growth averaged 6.14% with a standard deviation of 2.80%, with values ranging from -5.78% to 9.69%. The observed variability may reflect changes in domestic economic conditions, the policy environment, and external economic factors over the study period.

2. **Distributional Shapes & Robust Estimation:** Univariate normality testing indicates that 2 of the 6 variables (FDI Net Inflows and Gross Capital Formation) show no evidence against normality at α = 0.05, while GDP Growth, Inflation, Exports, and Unemployment exhibit empirical non-normality. In addition, the OLS regression residuals show evidence of non-normality (Shapiro-Wilk p = 0.0040). Consequently, HC3 Robust Standard Errors are utilized as a robustness measure for coefficient inference, particularly given the small sample size and potential sensitivity to leverage.

3. **Correlation Structure & Regression Estimation:** Pairwise Pearson and Spearman correlations reveal different patterns of association with GDP Growth, particularly for Gross Capital Formation and Unemployment. Both variables show statistically significant Spearman rank correlations (Gross Capital Formation: Spearman rho = 0.4305, p = 0.0098; Unemployment: Spearman rho = -0.3751, p = 0.0264), while their Pearson correlations are not statistically significant at α = 0.05 (Gross Capital Formation: Pearson r = 0.3180, p = 0.0626; Unemployment: Pearson r = -0.2095, p = 0.2270). The multiple linear regression model accounts for 28.37% of sample variance (R² = 0.2837, Adjusted R² = 0.1602, F = 2.2969, p = 0.0710), indicating that the overall model is not statistically significant at α = 0.05. Under HC3 Robust Standard Errors, none of the five individual macroeconomic predictors reaches statistical significance at α = 0.05.

4. **Econometric Diagnostics & Multicollinearity Screening:** Diagnostic tests show Durbin-Watson = 1.744, suggesting no strong evidence of first-order autocorrelation, and the Breusch-Pagan test (p = 0.1222) shows no statistically significant evidence of heteroskedasticity at α = 0.05. Residual Shapiro-Wilk testing (p = 0.0040) indicates evidence of residual non-normality. Cook's Distance flags 2 observation(s) (1991, 2020) exceeding the screening threshold (4/n ≈ 0.114); these observations warrant examination for influence and context, but exceeding the threshold does not by itself imply that the observations are erroneous or should be removed. Variance Inflation Factors indicate no high multicollinearity, although Exports has a VIF of 5.71, indicating a potential multicollinearity concern that warrants attention.

5. **Methodological Cautions & Limitations:**
- *Association vs. Causation:* All reported correlation and regression coefficients quantify conditional empirical associations; they do not establish causal relationships or structural policy mechanisms.
- *Sample Size & Time-Series Constraints:* The 35 annual observations (1991–2025) provide a relatively small sample for multiple regression, limiting statistical power and precision. Time-series data may also be affected by structural changes and non-stationarity; these issues were not formally tested in the present analysis.
- *Model Specification & Omitted Variables:* Estimated parameters reflect the five specified macroeconomic indicators. Omitted macroeconomic factors (e.g., monetary policy, fiscal deficits, exchange rates, global energy prices) may influence growth outcomes.
- *Diagnostic Interpretation:* Econometric screening tests (DW, BP, Shapiro-Wilk, Cook's D, VIF) provide heuristic diagnostic evidence rather than absolute mathematical certainty.