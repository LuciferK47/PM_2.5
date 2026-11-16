# 06 Critical review (by Claude, an earlier reviewer; verify independently, do not just agree)

Evidence marked **[verified]** was re-computed by the reviewer from the repo data. Others are read from code/results.

## A. What is solid
1. **Data hygiene is good.** Only 2 PM2.5 gaps; weather from ERA5 has no gaps; clear cleaning rule; weekly aggregation rule explicit; train/test split fixed before modelling; 2020 lockdown kept out of test and VAR.
2. **Deseasonalising before Granger** is the right call, and the team shows a robustness grid (anomalies/AIC lag, BIC lag, first differences) plus HAC errors and a rain control. The direction weather -> PM2.5 is stable across all of them (p < 1e-10), the reverse is not.
3. **Honest reporting of the ordering sensitivity** (IRF -6% to -12%, FEVD 6% to 30%) rather than one flattering number.
4. **Evidence-based design choice:** the weekly lag regression shows last week's weather adds nothing, which justifies a weather-free 12-month model.
5. **Reproducibility:** `verify_numbers.py` independently re-derives 52 slide numbers.

## B. Real problems found

### B1. Ljung-Box "failure" in the SARIMA draft is an artifact **[verified]**
`ljungbox.csv` shows p ~ 0 at all 49 lags. Cause: with D=1 the first 52 in-sample residuals are the diffuse-initialisation residuals (about 5.2 on the log scale, i.e. the series level itself), and the code runs Ljung-Box on all of `res.resid`. After dropping the first 52 residuals: residual SD 0.269, Ljung-Box p = 0.49 (lag 10) and 0.10 (lag 26), i.e. residuals are fine. Fix: `resid.iloc[S:]` (or use `simple_differencing`) before any residual diagnostic (Ljung-Box, ARCH-LM, Shapiro, ACF).

### B2. The SARIMA model barely beats climatology, and the interval is too narrow **[verified]**
2019 test MAE: SARIMA(1,0,1)(0,1,1)52 = 27.5, climatology = 27.8, seasonal naive = 30.3. A 0.3 ug/m3 gap on 52 points is within noise; no Diebold-Mariano test is done. Empirical 95% interval coverage on 2019 = 84.6%, not 95%. All three forecasts over-predict (mean error -14.7 / -12.6 / -6.4) because 2019 (mean 108) was cleaner than 2015-2018 (114-138): there is a downward drift the models do not have. One test year is a very small basis for ranking models.

### B3. The seasonal MA parameter is on the invertibility boundary **[verified]**
Fitted ma.S.L52 = -0.988. With D=1 plus a seasonal MA near -1, the seasonal difference and the MA term nearly cancel: it is a sign of over-differencing / a deterministic seasonal pattern (the team's own stationarity tests said the log level is already stationary, d=0, and the seasonal-difference KPSS on the full sample is borderline). The D=1 choice rests on one validation year (MAE 21.1 vs 39.7 for D=0), but the D=0 candidate there was a (1,0,1)(1,0,1) model that was fit on only 3 years with a 52-lag seasonal AR: a weak competitor. Better competitors that were never tried: harmonic regression (Fourier terms) + ARMA errors (dynamic harmonic regression), a seasonal-dummies/climatology + AR(1) anomaly model, and ETS/TBATS. With only 4 training seasons (209 weeks), estimating a 52-lag seasonal structure is statistically thin. The sub-1 % improvement over climatology suggests that most of the predictability is the calendar mean.

### B4. Information leakage / inconsistent samples across phases
- Notebook 03 estimates the day-of-year climatology on 2015-2019, so the 2019 test year influences the anomalies; fine for inference, but it must not be reused for forecasting evaluation.
- STL, Box-Cox and the "full-sample" stationarity tables use the full weekly sample incl. 2019 and the 2020 lockdown half-year (STL title even notes the trend falls from 2019 including lockdown). The team does repeat tests on the training set, but the headline STL strength 0.89 and Box-Cox lambda come from the full sample.
- The SARIMA order grid (AIC on 2015-2018) and the validation year 2018 overlap in-sample: the team admits this.

### B5. Statistical subtleties in the Granger/VAR work
- **Anomaly series are not clearly stationary:** KPSS rejects for PM2.5 and wind anomalies (stat 2.03 and 1.05 vs 0.46 critical). The team attributes it to the 2019 decline and runs a first-difference robustness check, which is reasonable, but the primary spec stays on anomalies.
- **p-values like 1e-29** from a plain F-test with autocorrelated, heteroskedastic residuals are not meaningful; the team already switches to HAC (1e-20 .. 1e-11) and states "p < 1e-10". The HAC is done "equation by equation" (a manual OLS rather than the full VAR), fine.
- **Inconsistency in the reverse direction PM2.5 -> wind:** pairwise bivariate table (granger_pairwise_lags.csv) gives p < 0.05 for lags 1-5 (0.001, 0.0005, 0.004, 0.014, 0.038); the VAR(4) F-test gives p = 0.127 (not significant); BIC VAR(2) gives 0.017; the slides quote "lags 1-2 only, p = 0.04 and 0.016" from a third (trivariate HAC per-lag) specification that is not saved in results/. So "PM2.5 -> wind is weak" depends on specification. Physically plausible reverse channel is negligible; the safe statement is "no robust reverse causality".
- **IRF identification:** Cholesky ordering is arbitrary; the team handles this with a range. Weather-first treats same-day PM2.5 as a pure response, which is questionable because daily means of wind/humidity and PM2.5 are measured over the same 24 h. IRF CIs are shown only for the default ordering.
- **Nonlinearity not examined:** humidity effect is non-monotonic (shock_binned.json: +5.6% at z = -0.5, -21% at z = +2.2) and EDA shows humidity matters only in the monsoon; a linear VAR with one coefficient for all seasons averages these. A season-interacted or regime-switching check is missing. Also no mixing height / boundary-layer height, stubble-burning fire counts, or temperature in the VAR (temp is available and unused; ERA5 offers boundary_layer_height). Omitted-variable bias is acknowledged only verbally. "Weather drives PM2.5" is stronger than "wind and humidity anomalies precede lower PM2.5".
- **ERA5 is a single grid cell** vs. CPCB Delhi being a multi-station city aggregate; measurement mismatch weakens estimated effects (attenuation).
- **Data quality:** the Kaggle CPCB file is an aggregation with known quirks (station mix changes over time; AQI from 2015 onwards). A secular decline from 2018 to 2019 could be partly a change in monitoring stations rather than real air quality.

### B6. Variance modelling is acknowledged but not resolved
Log PM2.5 still shows ARCH effects (LM 36, p = 6e-6) and unequal monthly variance (Levene p = 0.006; monthly log-SD ranges 0.35-0.47). The 12-month interval is built on a constant-variance Gaussian assumption on the log scale; the 84.6% coverage is consistent with that being too optimistic (winter variance of raw PM2.5 is much larger). Interval modelling could use seasonal variance, quantile forecasting, or a bootstrap.

### B7. Forecast target and reporting
- exp() of a log forecast is a **median**; the AQI advisory is about means/exceedance. Converting with exp(mu + sigma^2/2) (sigma^2 about 0.046) raises forecasts by about 2.3%; negligible vs the other errors, but should be stated.
- A "monthly AQI advisory table" from weekly mean PM2.5 hides within-week peaks: weekly means will under-state how often a single day crosses the "Severe" band. If the end user cares about exceedance days, a model of the daily distribution is more relevant than the weekly mean.
- Evaluation metrics are MAE/RMSE on the raw scale, dominated by the winter weeks; also report log-scale error / MAPE and per-season errors. For winter (Jan-Feb, Nov-Dec) the SARIMA MAE is 44.4 vs 46.6 climatology vs 56.3 seasonal naive **[verified]**, so most of the SARIMA gain is in winter.

### B8. Planned baselines are likely to disappoint or mislead
- **LSTM on 209 weekly points** is almost certainly over-parameterised; a 52-step recursive forecast without exogenous info would collapse to a mean seasonal pattern; including it as a "baseline" mostly demonstrates the point that deep learning is not suited here. Linear Regression needs a defined feature set (Fourier terms/lags); without it the baseline is ill-defined. Compare through rolling-origin (expanding window) cross-validation across 2017, 2018, 2019 rather than one test year.
- The 1-week SARIMAX with **same-week actual weather** is an upper bound that uses information not available at forecast time; a fair test would use lagged weather or an actual weather forecast. Also the weekly-aggregated weather is the mean of the same 7 days as PM2.5, so same-week R^2 0.14 partly reflects simultaneity, not predictability.

### B9. Repo hygiene
- README has been rewritten but `git status` shows uncommitted changes: modified notebooks/results/README, deleted slides/*.pptx/pdf, and untracked beamer sources, PRESENTATION_SCRIPT.md, next_phase/, new result tables.
- `__pycache__/*.pyc` are tracked and there is no `.gitignore`; `.venv` is in the working dir.
- `notebooks/04` is not executed (no stored outputs), so it can't be graded as evidence.
- The statement in the slide script "Isn't raw PM2.5 stationary too? Yes" slightly weakens the claim that stationarity needed logs; fine, since the script says logs are for variance.

## C. Severity ranking
1. B1 (diagnostic artifact; trivial fix, but would wrongly lead to rejecting the model).
2. B2/B3 (the headline forecasting result is not distinguishable from climatology; interval is miscalibrated; over-differencing signal).
3. B5 non-linear/seasonal heterogeneity, omitted variables (limits the strength of the causal story).
4. B7/B8 evaluation design (single test year, LSTM plan, upper-bound weather test).
5. B4, B6, B9.

## D. Suggested path forward (reviewer's recommendation)
1. Fix residual diagnostics (drop first s residuals), rerun and execute notebook 04 end-to-end.
2. Evaluate with rolling-origin cross-validation (e.g. fit 2015-2016 -> 2017, 2015-2017 -> 2018, 2015-2018 -> 2019), report MAE/RMSE on both raw and log scales, per-season errors, and Diebold-Mariano vs climatology.
3. Add competitors that fit the data size: Fourier-term regression + ARMA errors, climatology + AR(1) anomaly, ETS. Treat SARIMA(0,1,1)(0,1,1) airline-type models carefully; check ma.S near -1.
4. Calibrate the intervals (seasonally varying variance, or empirical residual quantiles / bootstrap) and report coverage; reconsider the target if the advisory depends on exceedance days.
5. Keep LSTM small/optional (or drop), state it as a negative result if kept.
6. Explicit trend handling: the downward drift into 2019-2020 (add a linear trend / level-shift term, or fit with the most recent years weighted more).
7. For the weather story, state it as "predictive, short-horizon", add temperature and optionally boundary-layer height, and test a season-interacted VAR if time permits.
