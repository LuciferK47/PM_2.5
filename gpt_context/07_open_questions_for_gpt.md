# 07 Questions for GPT

Please answer each question with a concrete recommendation (and say if you disagree with file 06).

## Forecasting design (most important)
1. With 4 training seasons (209 weekly points) is a SARIMA(…)(…)52 sensible at all? Rank these for a 52-week-ahead forecast of weekly log PM2.5: (a) seasonal climatology, (b) climatology + AR(1) on anomalies, (c) Fourier-term regression (K harmonics) + ARMA errors, (d) SARIMA with D=1, (e) SARIMA with D=0, (f) ETS/TBATS, (g) Prophet-style additive model, (h) LSTM. Which do you expect to win and why?
2. The fitted seasonal MA coefficient is -0.988 under D=1. Is this evidence of over-differencing? What would you do (D=0 with seasonal AR or Fourier terms; fixed seasonal dummies)?
3. How should the model handle the 2019-2020 downward drift (possible level shift)? Is it a real air-quality improvement, monitoring-station composition change, or both, and how would you test it?
4. The 95% interval covers only 84.6% of 2019 weeks. What is the best fix with this little data: residual bootstrap, seasonal variance, quantile regression, conformal prediction (e.g. split/rolling conformal on weekly errors)?
5. Is a single test year adequate? Propose a rolling-origin evaluation design that respects the 52-step horizon with only ~5.5 years of data. Which significance test would you use to compare SARIMA vs climatology?
6. The end deliverable is a "monthly AQI advisory table". Should we forecast weekly means, daily values, or monthly means directly? How should we convert predictions into AQI category probabilities (e.g. P(category) per month)?
7. For the 1-week-ahead horizon, how should we fairly test whether weather helps (lagged weather, or ERA5 forecasts as exogenous inputs, vs the current "same-week actual weather" upper bound)?

## Causality / VAR (phase 3 already presented)
8. Do you agree that the conclusion "weather Granger-causes PM2.5 over 1-7 days" is well supported given deseasonalised anomalies, HAC errors, rain control, and lag robustness? What is the weakest link?
9. Is Cholesky-ordered IRF/FEVD a defensible choice for daily data where all three variables are 24-h means? Would generalised IRF or a local-projection approach be better? Is reporting a range (6%-30%) the right framing?
10. The humidity effect looks non-monotonic and season-dependent. Which minimal extra analysis (season-interacted VAR, threshold VAR, nonlinear Granger) would add most value for a course project, and which should be skipped?
11. Is it a problem that KPSS rejects stationarity for the PM2.5 and wind anomalies, and that the climatology is estimated on the same sample (including the trend)? Would you detrend, or use first differences as the primary spec?
12. Which additional variables (temperature, boundary-layer height, fire counts, NO2) are most worth adding for the Granger/VAR work, and would their addition plausibly change the conclusion?

## Methodology / reporting
13. Is the log transform adequately justified given residual ARCH effects (LM 36, p 6e-6) and monthly log-SD that still ranges 0.35-0.47? Is modelling the variance (GARCH, seasonal variance) worth it here?
14. Are there any statistical errors or over-claims in the presentation script (file 08) that a course instructor might challenge?
15. If the team has about two weeks left, what is the minimum set of analyses/changes that would most increase the grade/quality? Provide a prioritised list of at most 7 items.
16. Anything we missed that you think matters more than everything above?

Format your answer as: (i) agreements with file 06, (ii) disagreements, (iii) new issues found, (iv) numbered answers to Q1-Q16, (v) prioritised plan.
