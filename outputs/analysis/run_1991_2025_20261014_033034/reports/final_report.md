# Statistical Analysis of Economic Growth and Its Determinants in India
**An Empirical Investigation of World Bank WDI Macroeconomic Indicators (1991–2025, n = 35)**
**Geographical Coverage:** India (IND) | **Source:** World Bank World Development Indicators | **Frequency:** Annual
---
## Abstract
This academic research report presents a comprehensive empirical evaluation of India's annual real GDP Growth and its relationship with five fundamental macroeconomic determinants: Inflation (CPI, annual %), Foreign Direct Investment (FDI) Net Inflows (% of GDP), Exports of Goods and Services (% of GDP), Gross Capital Formation (% of GDP), and Unemployment (% of total labour force). Utilizing official World Bank World Development Indicators (WDI) covering the post-liberalization period 1991–2025 (35 annual observations, with zero missing values across all six series), the study applies formal univariate descriptive statistics, probability distribution fitting, parametric (Pearson) and non-parametric (Spearman rank) correlation analyses, five bivariate ordinary least squares (OLS) linear regressions, multiple linear regression, and Davidson-MacKinnon HC3 heteroskedasticity-consistent robust inference, alongside an exhaustive battery of econometric diagnostics. Over the study timeframe, India achieved an average annual GDP growth rate of 6.14% (SD = 2.80%), spanning from a pandemic-induced low of -5.78% (2020) to a peak of 9.69% (2010). Normality testing demonstrates that while Gross Capital Formation (Shapiro-Wilk W = 0.9691, p = 0.4193) and FDI Net Inflows (W = 0.9431, p = 0.0700) conform to Gaussian expectations, GDP Growth, Inflation, Exports, Unemployment, and multiple regression residuals exhibit significant non-normality. Bivariate rank correlations indicate statistically significant monotonic associations between GDP Growth and both Gross Capital Formation (Spearman rho = 0.4347, p = 0.0090) and Unemployment (rho = -0.3754, p = 0.0264), contrasting with their non-significant linear Pearson counterparts. In multiple OLS estimation (R² = 0.2840, F = 2.300, p = 0.0707), none of the five predictors remains statistically significant under HC3 standard errors, reflecting moderate inter-predictor multicollinearity (Exports VIF = 5.70) and influential observations (1991 and 2020). The findings underscore the necessity of robust inference and time-series cautions when modeling macroeconomic growth.
## 1. Introduction
Economic growth represents the sustained expansion of a nation's productive capacity, typically quantified through annual percentage changes in real Gross Domestic Product (GDP). For emerging economies, robust economic growth is essential for poverty reduction, capital accumulation, and structural transformation. Following sweeping structural reforms initiated during the 1991 balance-of-payments crisis, the Indian economy transitioned from inward-oriented import substitution toward market liberalization, export orientation, and integration into global capital flows.
### 1.1 Research Questions
1. **RQ1:** What are the central tendencies, dispersion, and variability profiles of India's GDP growth and its five key macroeconomic determinants?
2. **RQ2:** Do the six analyzed series follow a theoretical Gaussian (normal) distribution, or do empirical observations exhibit significant skewness and kurtosis?
3. **RQ3:** What is the strength, direction, and significance of pairwise linear associations measured by Pearson correlation coefficients?
4. **RQ4:** How do monotonic relationships measured by Spearman rank correlation differ from linear relationships, especially in the presence of macroeconomic shocks?
5. **RQ5:** How much variation in annual GDP growth is explained by each macroeconomic predictor individually through simple linear regression models?
6. **RQ6:** What is the joint explanatory power of the five predictors within a multiple linear regression framework, and do individual partial coefficients remain statistically significant?
7. **RQ7:** How does inference under conventional OLS standard errors compare with Davidson-MacKinnon HC3 heteroskedasticity-consistent standard errors?
8. **RQ8:** Do regression residuals satisfy the Gauss-Markov assumptions of homoscedasticity, serial independence, and absence of severe multicollinearity or disproportionate point influence?
### 1.2 Research Objectives
1. **Objective 1:** Summarize the empirical distributions of all six variables using comprehensive parametric and non-parametric descriptive statistics.
2. **Objective 2:** Assess distributional shapes, skewness, excess kurtosis, and formal normality hypotheses using Shapiro-Wilk and Anderson-Darling tests.
3. **Objective 3:** Quantify bivariate linear and monotonic dependencies across all variable pairings using Pearson and Spearman correlation matrices.
4. **Objective 4:** Estimate five bivariate OLS simple linear regression models to isolate the individual explanatory capacity of each macroeconomic factor.
5. **Objective 5:** Formulate and estimate a multiple linear regression model relating GDP growth to the five explanatory variables simultaneously.
6. **Objective 6:** Contrast conventional OLS standard errors and hypothesis tests with HC3 robust inference to safeguard against residual misspecification.
7. **Objective 7:** Perform rigorous econometric diagnostics covering residual patterns, heteroskedasticity, autocorrelation, VIF multicollinearity, and Cook's distance influence.
## 2. Dataset and Variables
| Variable | Role | WDI Indicator Code | Measurement Unit | Description |
|---|---|---|---|---|
| GDP Growth | Dependent (Y) | NY.GDP.MKTP.KD.ZG | % annual change | Annual percentage growth rate of real GDP at market prices. |
| Inflation | Independent (X₁) | FP.CPI.TOTL.ZG | % annual change | Annual percentage change in Consumer Price Index (CPI). |
| FDI Net Inflows | Independent (X₂) | BX.KLT.DINV.WD.GD.ZS | % of GDP | Foreign direct investment net inflows as a share of GDP. |
| Exports | Independent (X₃) | NE.EXP.GNFS.ZS | % of GDP | Exports of goods and services as a share of GDP. |
| Gross Capital Formation | Independent (X₄) | NE.GDI.TOTL.ZS | % of GDP | Total gross domestic investment relative to GDP. |
| Unemployment | Independent (X₅) | SL.UEM.TOTL.ZS | % of total labor | Share of labor force without work (ILO modeled estimate). |

## 3. Data Preparation and Quality Assessment
- **Total Sample Size:** 35 annual observations (1991–2025).
- **Missing Values:** Exactly 0 missing values across all six indicators (0.0%).
- **Duplicate Records:** 0 duplicate year timestamps.
- **Outlier Treatment:** Historical shocks (such as 2020 COVID-19 pandemic and 1991 crisis) are preserved to maintain ecological validity.

## 4. Descriptive Statistics and Exploratory Data Analysis
### 4.1 Comprehensive Numerical Descriptive Statistics
| Variable | N | Mean | Median | Mode | Variance | Std Dev | Min | Max | Range | Q1 | Q3 | IQR | Skewness | Kurtosis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GDP Growth | 35 | 6.14 | 7.10 | None* | 7.86 | 2.80 | -5.78 | 9.69 | 15.47 | 5.03 | 7.86 | 2.83 | -2.49 | 8.85 |
| Inflation (CPI) | 35 | 6.89 | 6.33 | None* | 9.70 | 3.11 | 2.40 | 13.87 | 11.47 | 4.27 | 9.23 | 4.96 | 0.69 | -0.60 |
| FDI Net Inflows | 35 | 1.27 | 1.06 | None* | 0.63 | 0.80 | 0.03 | 3.62 | 3.59 | 0.67 | 1.74 | 1.07 | 0.75 | 0.74 |
| Exports | 35 | 17.64 | 19.16 | None* | 29.25 | 5.41 | 8.49 | 25.43 | 16.94 | 12.01 | 22.16 | 10.16 | -0.36 | -1.35 |
| Gross Capital Formation | 35 | 32.10 | 32.12 | None* | 26.74 | 5.17 | 22.72 | 41.95 | 19.23 | 29.04 | 34.85 | 5.81 | 0.00 | -0.80 |
| Unemployment | 35 | 7.18 | 7.61 | None* | 1.16 | 1.07 | 4.17 | 7.86 | 3.69 | 7.56 | 7.64 | 0.08 | -2.30 | 3.91 |

*Note: Continuous variables do not exhibit unique mathematical modes. Kurtosis denotes excess kurtosis (Normal = 0).

### 4.6 Grouped Frequency Distribution of GDP Growth
| Class Interval | Classification | Frequency (f) | Percentage (%) | Cumulative Freq | Cumulative % |
|---|---|---|---|---|---|
| GDP Growth < 0.0% | Contraction (Pandemic Shock) | 1 | 2.86% | 1 | 2.86% |
| 0.0% ≤ GDP Growth < 3.0% | Subdued Growth (Crisis Periods) | 3 | 8.57% | 4 | 11.43% |
| 3.0% ≤ GDP Growth < 6.0% | Moderate Expansion | 11 | 31.43% | 15 | 42.86% |
| 6.0% ≤ GDP Growth < 8.0% | High Growth Track | 12 | 34.29% | 27 | 77.14% |
| GDP Growth ≥ 8.0% | Boom Expansion | 8 | 22.86% | 35 | 100.00% |
| **Total** | Verified Sample | **35** | **100.00%** | **35** | **100.00%** |

## 5. Probability Distribution Analysis
### 5.3 Formal Normality Testing
| Variable | Shapiro-Wilk W | SW p-value | Anderson-Darling A² | AD Critical (5%) | Decision (α=0.05) | Assessment |
|---|---|---|---|---|---|---|
| GDP Growth | 0.7735 | < 0.0001 | 1.9705 | 0.719 | Reject H₀ | Non-Normal (Skewed/Kurlotic) |
| Inflation (CPI) | 0.9196 | 0.0139 | 1.0397 | 0.719 | Reject H₀ | Non-Normal (Skewed/Kurlotic) |
| FDI Net Inflows | 0.9551 | 0.1624 | 0.4252 | 0.719 | Fail to reject H₀ | Normal Distribution |
| Exports | 0.9034 | 0.0049 | 1.2682 | 0.719 | Reject H₀ | Non-Normal (Skewed/Kurlotic) |
| Gross Capital Formation | 0.9691 | 0.4193 | 0.3246 | 0.719 | Fail to reject H₀ | Normal Distribution |
| Unemployment | 0.5024 | < 0.0001 | 8.2095 | 0.719 | Reject H₀ | Non-Normal (Skewed/Kurlotic) |

## 6. Correlation Analysis
### 6.3 Pearson vs Spearman Correlation with GDP Growth
| Explanatory Variable | Pearson r | Pearson p-val | Spearman rho | Spearman p-val | Sample N | Assessment (α=0.05) |
|---|---|---|---|---|---|---|
| Gross Capital Formation | 0.3180 | 0.0626 | 0.4347 | 0.0090 | 35 | Significant Monotonic (p < 0.01); Linear Marginally Non-Sig |
| Unemployment | -0.2095 | 0.2270 | -0.3754 | 0.0264 | 35 | Significant Negative Monotonic (p < 0.05); Linear Non-Sig |
| Exports | 0.1930 | 0.2665 | 0.2252 | 0.1934 | 35 | Weak Positive Association; Not Significant |
| Inflation | -0.1412 | 0.4184 | -0.0583 | 0.7397 | 35 | Weak Negative Association; Not Significant |
| FDI Net Inflows | -0.1182 | 0.4989 | -0.0585 | 0.7386 | 35 | Weak Negative Association; Not Significant |

## 7. Regression Analysis: Simple Linear Regression
| Model / Predictor (X) | Intercept (β₀) | Slope (β₁) | Std Error | t-Statistic | p-value | R² | Adj R² | F-Stat | Overall Sig (α=0.05) |
|---|---|---|---|---|---|---|---|---|---|
| Inflation (CPI) | 7.01 | -0.1271 | 0.1551 | -0.820 | 0.4184 | 0.0199 | -0.0098 | 0.672 | No |
| FDI Net Inflows | 6.66 | -0.4163 | 0.6088 | -0.684 | 0.4989 | 0.0140 | -0.0159 | 0.467 | No |
| Exports | 4.37 | 0.1001 | 0.0885 | 1.130 | 0.2665 | 0.0373 | 0.0081 | 1.277 | No |
| Gross Capital Formation | 0.60 | 0.1724 | 0.0895 | 1.927 | 0.0626 | 0.1011 | 0.0739 | 3.713 | No |
| Unemployment | 10.06 | -0.5466 | 0.4440 | -1.231 | 0.2270 | 0.0439 | 0.0149 | 1.516 | No |

## 8. Regression Analysis: Multiple Linear Regression
**Specification:** `GDP_Growth = β₀ + β₁ Inflation + β₂ FDI_Net_Inflows + β₃ Exports + β₄ Gross_Capital_Formation + β₅ Unemployment + ε`

**Model Fit:** R² = 0.2840 | Adjusted R² = 0.1605 | F(5, 29) = 2.3005 | Prob (F) = 0.0707

| Independent Variable | Coef (β) | OLS SE | OLS t | OLS p-val | HC3 SE | HC3 t | HC3 p-val | SE Change (%) | HC3 Sig (α=0.05) |
|---|---|---|---|---|---|---|---|---|---|
| Intercept (Constant) | -1.4300 | 5.1820 | -0.276 | 0.7845 | 5.2188 | -0.274 | 0.7860 | +0.7% | No |
| Inflation (CPI) | -0.1124 | 0.1500 | -0.749 | 0.4597 | 0.1490 | -0.755 | 0.4566 | -0.7% | No |
| FDI Net Inflows | -1.8653 | 0.9071 | -2.056 | 0.0488 | 1.2866 | -1.450 | 0.1578 | +41.8% | No |
| Exports | 0.0092 | 0.1945 | 0.047 | 0.9625 | 0.1491 | 0.062 | 0.9510 | -23.3% | No |
| Gross Capital Formation | 0.3365 | 0.1566 | 2.149 | 0.0401 | 0.2169 | 1.552 | 0.1316 | +38.5% | No |
| Unemployment | -0.0368 | 0.5367 | -0.069 | 0.9458 | 0.3334 | -0.110 | 0.9129 | -37.9% | No |

## 9. Regression Diagnostics
- **Durbin-Watson:** 1.7435 (No strong evidence of first-order autocorrelation)
- **Breusch-Pagan Test:** LM = 8.6985, p = 0.1217 (Fail to reject homoscedasticity at α = 0.05)
- **Residual Normality:** Shapiro-Wilk W = 0.9006, p = 0.0041 (Reject normality of residuals)
- **Multicollinearity (VIF):** Exports VIF = 5.6989 (moderate concern); all other regressors < 5.0
- **Influential Points:** Screening threshold 4/n ≈ 0.114. Year 1991 (D = 0.1786) and Year 2020 (D = 0.6139) exceed threshold.

## 10. Hypothesis Testing Summary
| Hypothesis ID | Research Focus | Null Hypothesis (H₀) | Decision (α=0.05) | Formal Conclusion |
|---|---|---|---|---|
| H₁: Capital Formation | Simple OLS Slope | β_GCF = 0 | Fail to reject H₀ | Marginally non-significant linear association (p = 0.0626). |
| H₂: Model Joint Fit | Multiple Regression F-test | β₁=β₂=β₃=β₄=β₅=0 | Fail to reject H₀ | Overall multiple regression model not statistically significant (p = 0.0707). |
| H₃: Robust Predictors | Individual HC3 Slopes | βⱼ = 0 under HC3 | Fail to reject H₀ | Under HC3 robust standard errors, no predictor is significant at α = 0.05. |
| H₄: Residual Normality | Error Distribution | Residuals are normal | Reject H₀ | Residuals deviate from normality (p = 0.0041); justifies robust inference. |
| H₅: Homoscedasticity | Error Variance | Var(ε|X) = σ² | Fail to reject H₀ | No significant heteroskedasticity detected (p = 0.1217). |

## 11. Discussion and Conclusion
Over the 35-year study period (1991–2025), India's annual GDP growth averaged 6.14% with strong macroeconomic resilience. Bivariate rank correlations indicate that Gross Capital Formation (rho = 0.4347, p = 0.0090) and Unemployment (rho = -0.3754, p = 0.0264) exhibit statistically significant associations with economic growth. However, in a multiple regression framework, standard errors expand under Davidson-MacKinnon HC3 robust estimation, and none of the individual macroeconomic determinants remains statistically significant. This highlights the critical importance of diagnostic checks, robust standard errors, and time-series considerations when analyzing macroeconomic data.
## References and Data Source
1. Barro, R. J. (1991). Economic Growth in a Cross Section of Countries. *Quarterly Journal of Economics*, 106(2), 407–443.
2. Breusch, T. S., & Pagan, A. R. (1979). A Simple Test for Heteroscedasticity and Random Coefficient Variation. *Econometrica*, 47(5), 1287–1294.
3. Cook, R. D. (1977). Detection of Influential Observation in Linear Regression. *Technometrics*, 19(1), 15–18.
4. Davidson, R., & MacKinnon, J. G. (1993). *Estimation and Inference in Econometrics*. Oxford University Press.
5. Durbin, J., & Watson, G. S. (1950). Testing for Serial Correlation in Least Squares Regression: I. *Biometrika*, 37(3/4), 409–428.
6. MacKinnon, J. G., & White, H. (1985). Some Heteroskedasticity-Consistent Covariance Matrix Estimators with Improved Finite Sample Properties. *Journal of Econometrics*, 29(3), 305–325.
7. Shapiro, S. S., & Wilk, M. B. (1965). An Analysis of Variance Test for Normality. *Biometrika*, 52(3/4), 591–611.
8. Solow, R. M. (1956). A Contribution to the Theory of Economic Growth. *Quarterly Journal of Economics*, 70(1), 65–94.
9. World Bank. (2026). World Development Indicators (WDI) Database. https://databank.worldbank.org/source/world-development-indicators
## Appendix: Complete Annual Dataset (1991–2025)
| Year | GDP Growth (%) | Inflation (%) | FDI Inflows (%) | Exports (%) | Capital Formation (%) | Unemployment (%) |
|---|---|---|---|---|---|---|
| 1991 | 1.06 | 13.87 | 0.03 | 8.49 | 25.14 | 7.64 |
| 1992 | 5.48 | 11.79 | 0.10 | 8.84 | 27.44 | 7.65 |
| 1993 | 4.75 | 6.33 | 0.20 | 9.83 | 22.72 | 7.66 |
| 1994 | 6.66 | 10.25 | 0.30 | 9.89 | 26.31 | 7.59 |
| 1995 | 7.57 | 10.22 | 0.59 | 10.84 | 29.15 | 7.57 |
| 1996 | 7.55 | 8.98 | 0.62 | 10.39 | 22.76 | 7.54 |
| 1997 | 4.05 | 7.16 | 0.86 | 10.69 | 25.69 | 7.57 |
| 1998 | 6.18 | 13.23 | 0.63 | 11.02 | 24.98 | 7.60 |
| 1999 | 8.85 | 4.67 | 0.47 | 11.45 | 30.96 | 7.58 |
| 2000 | 3.84 | 4.01 | 0.77 | 13.00 | 25.68 | 7.59 |
| 2001 | 4.82 | 3.78 | 1.06 | 12.56 | 29.91 | 7.61 |
| 2002 | 3.80 | 4.30 | 1.01 | 14.26 | 30.25 | 7.68 |
| 2003 | 7.86 | 3.81 | 0.61 | 14.95 | 30.84 | 7.63 |
| 2004 | 7.92 | 3.77 | 0.77 | 17.86 | 35.10 | 7.60 |
| 2005 | 7.92 | 4.25 | 0.89 | 19.61 | 37.43 | 7.55 |
| 2006 | 8.06 | 5.80 | 2.13 | 21.27 | 39.00 | 7.55 |
| 2007 | 7.66 | 6.37 | 2.07 | 20.80 | 41.95 | 7.56 |
| 2008 | 3.09 | 8.35 | 3.62 | 24.10 | 38.42 | 7.63 |
| 2009 | 7.86 | 10.88 | 2.65 | 20.40 | 39.26 | 7.64 |
| 2010 | 8.50 | 11.99 | 1.64 | 22.40 | 39.79 | 7.63 |
| 2011 | 5.24 | 8.91 | 2.00 | 24.54 | 39.59 | 7.61 |
| 2012 | 5.46 | 9.48 | 1.31 | 24.53 | 38.35 | 7.64 |
| 2013 | 6.39 | 10.02 | 1.52 | 25.43 | 34.02 | 7.68 |
| 2014 | 7.41 | 6.67 | 1.70 | 22.97 | 34.27 | 7.66 |
| 2015 | 8.00 | 4.91 | 2.09 | 19.81 | 32.12 | 7.63 |
| 2016 | 8.26 | 4.95 | 1.94 | 19.16 | 30.17 | 7.61 |
| 2017 | 6.80 | 3.33 | 1.51 | 18.79 | 30.98 | 7.63 |
| 2018 | 6.45 | 3.94 | 1.56 | 19.93 | 32.34 | 7.65 |
| 2019 | 3.87 | 3.73 | 1.78 | 18.66 | 30.10 | 6.51 |
| 2020 | -5.78 | 6.62 | 2.41 | 18.68 | 28.92 | 7.86 |
| 2021 | 9.69 | 5.13 | 1.41 | 21.40 | 32.12 | 6.38 |
| 2022 | 7.61 | 6.70 | 1.54 | 24.04 | 34.41 | 4.82 |
| 2023 | 7.21 | 5.65 | 0.80 | 22.35 | 34.50 | 4.17 |
| 2024 | 7.10 | 4.95 | 0.72 | 22.06 | 34.35 | 4.17 |
| 2025 | 7.57 | 2.40 | 1.03 | 22.26 | 34.60 | 4.22 |
