# Handoff: Delhi PM2.5 time-series project (MATH F428)

Written for a teammate who has to present and defend this project without having built it. Read sections 1-3 first (30 minutes), then use 4 (theory) and 8 (viva questions) as reference. Every number below comes from a file in `results/` (named in the text) and was re-checked against it; if a number and a results file ever disagree, the file wins.

Authors: Kushagra Singh, Yatin JM, Aryan Choudhary. Course instructor: Prof. Anupama Sharma.

---

## 1. What the project is

**One paragraph.** Delhi's PM2.5 (fine particles) has a huge yearly cycle: winter averages 213 ug/m3, the monsoon 48 ug/m3 (4.4x), and 52% of days are in the "Poor or worse" PM2.5 band. We asked two questions. **Q1 (explain):** do wind and humidity predict PM2.5, and over what horizon? **Q2 (forecast):** how well can PM2.5 be forecast one week and 52 weeks ahead, and what does a model fitted before 2020 say about the 2020 lockdown? Answers: weather predicts PM2.5 over a few days, robustly, but adds nothing detectable at the weekly scale; for 52-week forecasts the plain calendar average (climatology) is hard to beat, and no model was significantly better; the 2020 lockdown shows up as a large gap (about 43%) below the model's no-lockdown projection, but that size is model-relative and not a causal estimate.

**Scope.** The data end on 1 July 2020, so this is a **historical forecasting study**: backtests for 2017, 2018, 2019 and a month-by-month outlook for 2020 made from data to December 2019. It is not a current air-quality advisory.

**What is *not* claimed** (say this proactively in a viva): not that weather causes pollution (Granger is predictive); not that any model beats climatology; not that the lockdown "caused" a 43% drop; not that the decline 2016-2019 is certainly real (station network changed); not anything about neural networks in general (our LSTM is tiny and untuned); not that the PM2.5 bands equal the official AQI.

**Deliverables.** `slides/beamer/main.tex` (final deck), `report/report.tex` (final report, 7 pages), notebooks 01-04, `src/` (library code), `results/` (all tables), `README.md` (overview). PDFs are not tracked; build them (section 3).

---

## 2. Data, and its quirks

| Item | Detail | File |
|---|---|---|
| PM2.5, NO2, SO2 (city daily) | CPCB records via Kaggle `rohanrao/air-quality-data-in-india` (`city_day.csv`), Delhi, 2015-01-01 to 2020-07-01, **2,009 days** | `data/raw/city_day.csv` |
| Station-level PM2.5 | `station_day.csv` + `stations.csv` (same dataset) | `data/raw/` |
| Weather | ERA5 reanalysis via Open-Meteo, one grid cell at 28.61N, 77.21E: wind, relative humidity, temperature, rain | `data/raw/delhi_weather_openmeteo.json` |
| Processed daily / weekly | merged tables used by all notebooks | `data/processed/delhi_daily.csv`, `delhi_weekly.csv` |

**Cleaning and construction**
- 2 missing PM2.5 days were interpolated (`results/missing_report.csv`).
- **Weekly series:** 287 weekly means, weeks end on **Sunday** (pandas `W-SUN`), 2015-01-04 to 2020-06-28. The forecasting target is the **log** of the weekly mean.
- **Training years** for all headline statistics are 2015-2018 (209 weeks). Using the full sample for "headline" numbers was an earlier mistake (test-year leakage); full-sample values appear only as a comparison.

**Quirks you must know**
1. **Week index.** Climatology needs "which week of the year is this". `src/tsa.py: week_index` maps each Sunday-ending week to 1..52 using the week's Thursday on a fixed 365-day calendar; **week 53 is folded into week 52**. Seasonal naive uses "52 weeks earlier", which is not the same calendar week in 53-week years.
2. **Leap years.** `doy365` maps 29 Feb to day 59 and shifts later leap-year days by -1, so day-of-year climatologies line up across years.
3. **Station count changes.** Stations reporting PM2.5: 10 (2015), 8 (2016), 17 (2017), 37 (2018), 37 (2019) (`results/key_numbers_eda.json`). The city series is the mean over stations (correlation 0.995 with the station-mean series), so a mix effect is possible. The fixed six-station panel (DL002, DL013, DL019, DL021, DL028, DL031; at least 60 days in each year) is thin in 2017 (125 days).
4. **The fold boundaries.** A 52-week forecast from origin 2016-12-25 ends 2017-12-24, not 31 Dec. Folds are "52 weeks after the origin", labelled by the year they mostly cover.
5. **The 2020 data include the lockdown** (from 25 March 2020). Lockdown weeks never enter model selection.
6. **PM2.5 bands are not the AQI.** The official CPCB AQI is the maximum sub-index over pollutants. We use only the PM2.5 breakpoints (24-hour, ug/m3): Good 0-30, Satisfactory 31-60, Moderate 61-90, Poor 91-120, Very Poor 121-250, Severe above 250 (`src/aqi.py`). "Poor or worse" means above 90.

---

## 3. Repository map and how to run it

```
data/raw, data/processed     inputs (section 2)
src/data.py, tsa.py, aqi.py, forecast.py, plots.py    library code
notebooks/01_data_prep, 02_eda, 03_var_granger, 04_forecasting    executed, outputs saved
results/                     every CSV/JSON table (fc_* = forecasting)
figures/                     PNG figures from the notebooks
slides/beamer/               main.tex (deck), make_figures.py, verify_numbers.py, tables/*.tex, fig/*.pdf (deck), fig_report/*.pdf (report)
report/report.tex            final report source
tools/build_nb04.py          regenerates notebook 04 from code
```

**Order to run** (see `README.md` for the full commands): create the environment from `requirements.txt` (Python 3.12, statsmodels 0.15.0 etc.), download the three Kaggle files into `data/raw/` (needs a Kaggle token), run the notebooks in order 01 to 04, then `python slides/beamer/make_figures.py` and `PROFILE=report python slides/beamer/make_figures.py` (the second writes the column-sized `fig_report/*.pdf`; the first writes `fig/*.pdf`, `tables/*.tex`, and `tables/numbers.tex` - the macros every slide and report number comes from), `python slides/beamer/verify_numbers.py` (independent re-derivation of the numbers; must end "checks passed"), then `tectonic main.tex` and `tectonic report/report.tex`.

**Things that bite**
- Notebook 04 takes roughly 10-12 minutes. It sets `OMP_NUM_THREADS=1` itself; without that, BLAS threads oversubscribe the parallel jobs and it crawls.
- **Never edit numbers in `main.tex` or `report.tex` by hand.** Every number is a macro from `tables/numbers.tex` or a generated table. If a result changes, re-run `make_figures.py`, then `verify_numbers.py`.
- **Monte-Carlo noise.** Simulated quantities (lockdown gap, band-day counts, interval bounds) vary by about 0.3 percentage points between re-runs because simulation paths are not bit-reproducible across runs. The backtest MAEs, Granger tables and station tables are deterministic.
- `tools/build_nb04.py` is the source of notebook 04. Edit the builder, rebuild, then execute; editing the notebook alone is lost on the next rebuild.
- `verify_numbers.py` skips (does not fail) the two web-link checks when offline.
- `*.pdf` is git-ignored on purpose.

---

## 4. Theory primer: what each method is, why we used it, what to watch for

### 4.1 Time-series basics we rely on
- **Stationarity.** A series is (weakly) stationary if its mean, variance and autocorrelations do not change over time. Many models assume it. **Wold's decomposition:** any stationary process = a deterministic part + an infinite moving average of white noise. This is why a *deterministic* seasonal pattern (Fourier terms) is a legitimate alternative to differencing it away.
- **ADF test** (Dickey-Fuller, 1979): H0 = unit root (non-stationary). **KPSS** (Kwiatkowski et al., 1992): H0 = stationary. They have **opposite nulls**, so we use both; agreement is informative, disagreement is a warning. On weekly log PM2.5, training years: ADF statistic -4.28 (5% critical value -2.88, p 4.8e-4); KPSS p-value 0.10 (does not reject). The seasonal difference is also stationary (ADF -4.53). Differencing a second time gives lag-1 autocorrelation -0.46: **over-differencing**. (`results/stationarity_train.csv`)
- **Trap:** KPSS on the *raw level* "rejects stationarity" mostly because of the seasonal cycle, so it says nothing about a trend. We look at annual means of the *deseasonalised* series for that (`results/annual_drift.csv`): PM2.5 falls about 25% from 2016 to 2019, so the level is **not** constant.
- **Log transform.** Raw PM2.5 is right-skewed (skew 1.70) and its monthly spread grows with its level (max/min monthly SD 7.9x; correlation of monthly mean and SD 0.95). After the log: skew -0.08, ratio 1.3x. A Box-Cox transform (lambda about 0.1 on training weeks) is close to the log, so the log is the simple choice. (`results/log_justification.csv`)
- **STL decomposition** (Cleveland et al., 1990): trend + seasonal + remainder by loess. Seasonal strength F_s = 0.90 on the training weeks (0.89 full sample): the cycle explains most of the variance.
- **ARCH-LM test** (Engle, 1982): tests whether large changes cluster in time (volatility clustering). It falls from 235 (raw) to 36 (log) but is still significant on daily changes; on weekly model residuals ARCH(4) is clean (p 0.87).

### 4.2 VAR and Granger causality
- **VAR(p):** each variable is regressed on p lags of all variables. We use three deseasonalised daily series (wind W, humidity H, log PM2.5 P). "Deseasonalised" means minus the day-of-year climatology. VAR(4) is the AIC minimum (BIC picks 2); the VAR is stable (max eigenvalue modulus 0.81); Portmanteau test on residuals p = 0.168 (`results/var_lag_selection.csv`, `key_numbers_var.json`).
- **Granger causality** (Granger, 1969): W "Granger-causes" P if past W improves the prediction of P beyond the past of P (and H). Test in the P equation: H0 = all coefficients on lagged W are zero (Wald/F test). **It is a statement about prediction, not physical cause.** Unmeasured common drivers (boundary-layer height, stubble burning, fireworks) can create Granger causality.
- **HAC errors** (Newey-West, 1987): the plain F test assumes independent, equal-variance errors; daily residuals are autocorrelated and heteroskedastic, so we also report a Wald test with heteroskedasticity-and-autocorrelation-consistent covariance. We implemented the HAC covariance by hand in `verify_numbers.py` as an independent check.
- **Results** (`results/granger_hac*.csv`): wind to PM2.5 p = 6.0e-20, humidity to PM2.5 p = 3.5e-11 (4 lags). Robust: with rain and temperature 9.1e-18 and 6.8e-8; with a linear trend 5.5e-20 and 1.3e-11; with a climatology fitted on 2015-2018 only 6.9e-20 and 2.6e-11. Rain adds nothing once wind and humidity are in (p 0.88). Season-specific tests are all below 1e-3 (largest: winter humidity 5.4e-4). **Season interactions are weak** (monsoon x humidity p 0.20; winter x wind p 0.03), so "humidity matters only in the monsoon" is a correlation pattern, not a difference in predictive content.
- **Reverse direction** (PM2.5 to weather) is absent for humidity and weak for wind (significant only at lag orders 1-2, p 0.038 and 0.015; not in the full VAR, p 0.12). Possible reason: a shared multi-day stagnation regime. We call it unproven.
- **Impulse responses.** A "shock" is the part of today's value the past does not predict. A one-SD wind shock (2.5 km/h) changes PM2.5 on day 1 by -12% (weather ordered first) or -6% (PM2.5 first); humidity (5.4% RH) by -7% or -4% (`results/irf_orderings.csv`). **Cholesky IRFs depend on variable ordering** (weather first allows same-day effects), so we report the range, 6-12% for wind and 4-7% for humidity. The **generalised IRF** (Pesaran and Shin, 1998) does not depend on ordering and lies inside that range (day 1: -12.0% and -5.2%).
- **FEVD** (forecast-error variance decomposition): weather shocks explain 6-30% of the 14-day forecast-error variance of PM2.5, again depending on the ordering (30% weather-first: 20.5% wind plus 9.5% humidity).
- **Weekly horizon test** (`results/weekly_lag_nested.csv`): regress this week's PM2.5 on last week's PM2.5 (R2 0.134), then add last week's wind and humidity (R2 0.139): delta R2 = 0.005, joint HAC Wald p = 0.51. We compare **nested** models; an earlier version compared non-nested R2s, which is invalid.

### 4.3 The forecasting models (`src/forecast.py`)
Everything forecasts the weekly **log** PM2.5, with no weather inputs (future weather is unknown at 52 weeks and weekly weather adds nothing).
- **Climatology** (benchmark): mean log PM2.5 of each calendar week 1..52 over the training years.
- **Seasonal naive:** the value 52 weeks earlier.
- **Climatology + AR(1):** climatology plus an AR(1) on the anomalies.
- **Linear regression:** OLS on 3 Fourier pairs and a linear trend; its predictive sd includes parameter uncertainty, sd_h^2 = s^2 (1 + x_h'(X'X)^-1 x_h), so it widens with the horizon.
- **Dynamic harmonic regression (DHR)**, the "Fourier + ARMA" model (Hyndman and Athanasopoulos, FPP3, section 10.5): y_t = c + delta*t + sum_k [alpha_k sin(2 pi k t/m) + beta_k cos(2 pi k t/m)] + eta_t, with m = 365.25/7 weeks and ARMA(p,q) errors eta_t. **Why:** a weekly series has a period of about 52.18, which pure SARIMA handles badly (it needs a 52-lag seasonal operator that burns 52 observations); Fourier terms use about 10 parameters for the whole cycle and allow non-integer periods. The **level** is constant, linear, or a **random walk** (then the errors are ARIMA(p,1,q), so "ARMA" in the label covers both). Selection (inside every training window, never using later data): K in 1..5 and (p,q) from a grid by **AICc** within each level type (AICc = AIC + 2k(k+1)/(n-k-1), Hurvich and Tsai, 1989), then the level type by validation on the last 52 training weeks. Fits that do not converge are rejected and counted.
- **SARIMA:** (1,0,1)(0,1,1)_52 (**D=1**, seasonal difference) and (1,0,1)(1,0,0)_52 with a constant (**D=0**).
- **LSTM** (Hochreiter and Schmidhuber, 1997): one layer, 16 units, 8-week lag, trained to predict the next anomaly (vs training climatology) from the last 8 anomalies and calendar sin/cos features; forecasts are **recursive** (each prediction is fed back). Seeded and deterministic. **Each input row pairs an anomaly with the calendar features of its own week** (a first version paired it with the next week's, an alignment bug found by an outside audit). Its interval is an in-sample heuristic and optimistic.
- **Median vs mean.** If log y ~ N(mu, sigma^2), then exp(mu) is the **median** of y and the mean is exp(mu + sigma^2/2). MAE is computed against the median; RMSE against the mean.

### 4.4 Diagnostics: the diffuse-initialisation artifact
A state-space SARIMA with D=1 initialises its first 52 seasonal states **diffusely**, so its first 52 in-sample residuals equal roughly the series level (about 5 on the log scale) and are huge. The first draft ran Ljung-Box (Ljung and Box, 1978) on all residuals and got p about 0 at every lag. With the burn-in removed (`res.loglikelihood_burn` = 52) the residuals pass at lags 10 and 26 (p 0.49, 0.10) but not at lag 52 (p 0.016) (`results/fc_diagnostics.csv`). The seasonal MA coefficient is -0.988 (near the invertibility boundary of -1) with a standard error of about 8 that is **unstable across refits**: the parameter is not identified, a sign of *possible* over-differencing, not a proof that the seasonal difference is unnecessary.

### 4.5 Evaluation design
- **Expanding-window (rolling-origin) backtest** (Tashman, 2000): origins at the end of 2016, 2017, 2018; each forecasts the next 52 weeks; every model is refit and **reselected** at each origin using only earlier data. 2018 and 2019 are the main evidence; 2017 (two training years) is a stress test.
- **Metrics:** MAE (ug/m3, original scale); coverage of the 95% interval exp(mu +/- 1.96 sd); mean interval width; **Winkler interval score** W = (u - l) + (2/alpha)(l - y)1{y < l} + (2/alpha)(y - u)1{y > u}, alpha = 0.05 (lower is better; it rewards narrow intervals that still cover, Winkler 1972; Gneiting and Raftery 2007).
- **Why a block bootstrap and not Diebold-Mariano (DM) for 52-week comparisons.** The 52 errors of one forecast path are strongly dependent, not 52 replications. We resample **circular moving blocks of 8 weeks within each forecast year** (so no block crosses two origins) and report a 95% interval for the mean paired absolute-error difference to climatology; if the interval contains 0 we write "indistinguishable". Three origins are few, so even this is conditional. **DM with the Harvey-Leybourne-Newbold correction** is used only for genuine one-step-ahead forecasts (the one-week experiment).
- **Bootstrap detail that matters:** the first version resampled non-circular blocks, which under-samples the first and last weeks and gave biased intervals (it wrongly declared the linear variant "better"). The final version is circular within each year.

### 4.6 The 2020 outlook, calibration and the lockdown study
- **Simulation.** Fit the headline procedure on 2015-2019, simulate 5,000 weekly log paths (53 weeks so every calendar day is covered), apply the calibration, convert to daily values by adding a **whole within-week offset vector** (Monday to Sunday, taken from a training week of the same month and constructed so mean(exp(offset)) = 1), so each simulated week averages exactly to its simulated weekly mean. Monthly means and band-day counts are computed from the same daily paths. Bands are PM2.5 sub-index bands.
- **Calibration rule** (fixed before 2019 was scored): standardised log errors z = (log y - mu)/sigma on the earlier folds; scale sigma separately for winter and other months with shrinkage toward the pooled value (26 pseudo-weeks); re-centre only if the bias has the same sign and exceeds 0.5 SD in both folds. In 2019 the mean z was -0.66 and -0.45, so no re-centring. **Honest trade-off:** rescaling lifts 2019 coverage from 90% to 96%, but the mean width grows from 125 to 179 ug/m3 and the Winkler score *worsens* (175 to 193); it buys coverage, not sharper intervals. A smooth shrunk shift defined *after* seeing 2019 removes the level bias (bias -8.5 to +4.3, Winkler 161) but is only a sensitivity.
- **Lockdown.** Compare actual weekly PM2.5 in the ten Sunday-ending weeks 29 Mar - 31 May 2020 (these cover 23 Mar - 31 May, including two pre-lockdown days) with the no-lockdown projection. Headline: actual mean 48.7 vs model median 85.5, about **43% lower** (95% interval 32-52%); 38% if the model is given the actual 2020 weather ("oracle weather", unknowable in advance). **Why not causal:** the model was already about 11% too high in the 12 weeks before the lockdown; adjusting for that gives about 36%; a constant or random-walk level gives 43-51%; a placebo on the same weeks of 2019 gives 15% with an interval spanning zero (`results/fc_lockdown_sensitivity.csv`). The sign is robust; the size is model-relative. The "95% interval" is model predictive uncertainty, not a confidence bound on a causal effect.

---

## 5. Results (numbers and where they live)

| Result | Value | File |
|---|---|---|
| Poor-or-worse days | 52% of 2,009 days | `key_numbers_eda.json` |
| Winter vs monsoon mean | 213 vs 48 ug/m3 (4.4x) | same |
| Seasonal strength (STL) | 0.90 (training) | same |
| 4-lag HAC Granger p, wind / humidity | 6.0e-20 / 3.5e-11 | `granger_hac.csv` |
| Weekly nested test | R2 0.134 to 0.139, delta 0.005, p 0.51 | `weekly_lag_nested.csv` |
| MAE 2017 / 2018 / 2019, selected DHR | 31.5 / 23.4 / 25.7 | `fc_backtest_mae.csv` |
| MAE, climatology | 31.0 / 21.8 / 27.8 | same |
| MAE, SARIMA D=1 | 53.8 / 21.1 / 27.5 | same |
| MAE, SARIMA D=0 (+constant) | 44.9 / 42.8 / 44.1 | same |
| MAE, small LSTM (after the alignment fix) | 36.3 / 28.3 / 54.3 | same |
| MAE, linear regression | 35.9 / 20.0 / 24.9 | same |
| Selected minus climatology, 2018-19 | -0.2 ug/m3, 95% interval [-2.9, +2.8]: indistinguishable | `fc_loss_diff.csv` |
| Linear-trend DHR, mean 2018-19 | 21.9 vs 24.8 climatology, interval [-6.1, +0.7]: also indistinguishable | same |
| Raw 95% coverage 2017 / 2018 / 2019 | 69% / 94% / 90% | `fc_backtest_metrics.csv` |
| One week ahead (MAE change vs 22.4 no-weather) | lagged -2.4%, last 3 days +0.7%, same-week "oracle" +6.9% (p about 0.07) | `fc_oneweek.csv` |
| 2019 pipeline check | 12/12 monthly means inside; Poor-or-worse 55% predicted vs 45% observed | `key_numbers_forecast.json` |
| Lockdown | about 43% below projection; 36% adjusted; 37-51% across specs; placebo 15% | `fc_lockdown*.csv` |
| Station decline 2016-2019 | 25% (all), 20% (fixed panel), 18% (weather-adjusted) | `station_check.csv` |

The "headline" model procedure is DHR with selection inside each window. The 2017 and 2019 folds picked a random-walk level and the 2018 fold a constant level, all with K=5, p=1, q=1; the final 2020 fit (data to 2019) picked a linear level, K=5, AR(1) errors (`key_numbers_forecast.json`: `backtest.specs`, `outlook_2020_spec`).

---

## 6. Limitations and peculiarities (the full honest list)

1. **Three annual origins.** Resampling weekly errors cannot create extra test years. "Indistinguishable" only means the bootstrap interval contains 0.
2. **2019 is not a pristine hold-out.** It was examined in earlier iterations of the project. In the code, selection and calibration use only earlier data, but the *research process* saw 2019. Say "chronologically held out, not pristine".
3. **Level bias.** 2019 was cleaner than the training years, so forecasts were too high; all five 2019 raw-interval misses were below the lower bound.
4. **Interval width trade-off.** Calibrated intervals cover more but are wider and score worse on Winkler. The LSTM's intervals are optimistic.
5. **The lockdown gap** is model-relative and descriptive (section 4.6).
6. **Granger causality is predictive**; ERA5 is a single grid cell; mixing height, stubble burning and fireworks are unmeasured.
7. **Station network.** The six-station check is small and thin in 2017; the decline is "consistent with a genuine component, network effect not ruled out".
8. **SARIMA D=0 without a constant is numerically fragile** (AR root about 0.999). Our no-constant MAEs (76.9 / 61.0 / 92.1) are not reproducible to the decimal across software versions (an audit refit gave 64.8 in 2018 and 81.5-92.1 in 2019). Read it as "60-90, much worse than climatology". With a constant the result is stable. Fit details: `fc_sarima_d0_fit_details.csv`.
9. **Residual seasonality.** The selected DHR still has autocorrelation at lags 26 and 52 (p 0.001 and 0.009 in the 2019 fold; lag 10 marginal at 0.088).
10. **Seasonal MA near -1** with an unstable standard error: unidentified, not proof of over-differencing.
11. **Monte-Carlo noise** of about 0.3 percentage points in simulated quantities.
12. **One city**, data end July 2020, PM2.5 bands are not the AQI.

---

## 7. What went wrong earlier and how it was fixed

The project was reviewed by three people/LLMs and then audited twice more by Gemini and GPT recomputing from a data pack. Every claim was re-tested against the data before acting; some claims were wrong and were rejected. Be ready to explain any of these.

| Problem | Verdict | Fix |
|---|---|---|
| Ljung-Box p about 0 at every lag | Real: artifact of 52 diffuse residuals | drop `loglikelihood_burn` residuals |
| Seasonal MA at -0.988 treated as meaningful | Real: unidentified (SE about 8) | reported as an identification problem |
| SARIMA D=0 had no constant | Real | added a constant; matched comparison saved |
| Headline STL/Box-Cox on full sample (used test years) | Real | recomputed on 2015-2018 |
| Leap-year day-of-year capping | Real (minor) | `doy365` |
| Weekly R2 comparison of non-nested models | Real | nested test with joint Wald |
| "p < 1e-10 in every specification", "drives", PM2.5 band called AQI | Real over-claims | exact p-values, "predicts", "PM2.5 sub-index band" |
| Gemini: "re-anchoring gives 94.2% coverage" | **Rejected**: the data give 90.4% | none |
| Gemini: shock-bin plot has Jensen bias | **Rejected**: it averages the log change | wording only |
| Gemini: humidity matters only in the monsoon | **Rejected**: interaction p 0.20 | none |
| Gemini: ISO-week fold shifts all of 2016 | **Partly**: only 2016-01-03 (ISO week 53) | one consistent `week_index` |
| LSTM calendar features one week ahead of the anomalies | Real (found in audit round 2) | `lstm_window`; rerun: 36.3 / 28.3 / 54.3 |
| Checker compared April-June with March-May intervals; skipped a persistence week | Real (audit) | fixed; the checker now has 100+ checks (see the last line of its output) |
| Block bootstrap joined forecast years | Real | within-fold; then circular (the first fix was biased) |
| Linear regression and LSTM had constant-width intervals | Real | horizon-specific sd |
| Monthly means and band-days from different random draws | Real | one set of coherent daily paths |
| Non-converged fits accepted in AICc search | Real | rejected and counted |
| Double-rounded MAE macros (27.4 for 27.5; 54.4 for 54.3) | Real | macros read unrounded metrics |
| "D=0 MAE 39.7 to 30.6 with a constant" had no saved evidence | Real | replaced by the matched table |
| Over-claims: "matches or slightly beats", "weather adds nothing", "decline is real", "cut PM2.5 by 43%", "pre-declared / pristine 2019" | Real | reworded everywhere |

The `verify_numbers.py` checker re-derives selected numbers (it covers headline tables, macros and several independent refits; it does not re-run every model selection or the station download). "All checks pass" is evidence, not proof.

---

## 8. Likely viva questions (short answers)

1. **Why log?** Raw PM2.5 is skewed and its spread scales with its level; the log stabilises the variance (monthly SD ratio 7.9x to 1.3x) and makes errors multiplicative.
2. **ADF and KPSS disagree?** They did not: both indicate stationarity of the log series. They have opposite nulls, which is why we use both.
3. **Why Fourier terms instead of a seasonal difference?** Weekly period is about 52.18, non-integer; a seasonal difference burns 52 of 209 weeks; the cycle looks deterministic; D=1 SARIMA gave an unidentified seasonal MA and collapsed in 2017 (MAE 53.8).
4. **What is Granger causality here?** Past wind/humidity improve prediction of PM2.5; not a physical-cause claim.
5. **Why HAC?** Residuals are autocorrelated and heteroskedastic; plain F tests are overconfident.
6. **Why does the IRF have a range?** Cholesky depends on ordering; we show both orderings and the ordering-free generalised IRF.
7. **Does weather help forecasting?** Over days, yes in-sample; one week ahead only the same week's weather (unknowable) helps, by 6.9%; lagged weather changes MAE by -2.4%; at weekly lags nothing detectable (p 0.51).
8. **Is your Fourier model better than climatology?** No: statistically indistinguishable (2018-19: -0.2 ug/m3, interval [-2.9, +2.8]). The linear-trend variant has the lowest 2018-19 MAE but its interval also spans zero.
9. **Why not a Diebold-Mariano test?** Errors of one 52-step path are not independent replications; we use a within-year circular block bootstrap, and DM only for one-step errors.
10. **Why is SARIMA D=1 so bad in 2017?** Two training years: after differencing, almost nothing is left to learn the seasonal pattern from.
11. **Why is the LSTM bad?** About 200 weekly points and a recursive 52-step rollout; it learns little beyond the mean cycle. An alignment bug in the first version was fixed and it is still poor. It is a small baseline, not a verdict on deep learning.
12. **Did you use the test year to choose anything?** Selection happens inside each training window. But 2019 was examined during development, so it is not a pristine hold-out. The calibration rule was fixed before 2019 was scored; the smooth shift was defined after, so it is only a sensitivity.
13. **Why do your intervals under-cover in 2017?** Only two training years, large level shifts; coverage 69%. Calibration cannot fix a level bias it cannot see.
14. **Calibration made intervals worse?** It raised coverage (90% to 96%) but widened them 43% and the Winkler score rose 175 to 193; we report both.
15. **Is the 43% lockdown drop causal?** No: it is a gap to a model projection. The model was already 11% high before; adjusted 36%; specs 37-51%; the 2019 placebo gives 15% (interval spans 0).
16. **Is the 2016-19 decline real or a monitor change?** Consistent with a genuine decline (fixed panel -20%, weather-adjusted -18%), but the station count rose from 8-10 to 37 so a network effect is not ruled out.
17. **Is a band the AQI?** No. The AQI is the maximum sub-index over all pollutants; we use only PM2.5 breakpoints.
18. **Why median forecasts?** exp(mu) is the median of a lognormal; the mean needs exp(mu + sigma^2/2). MAE is optimal for the median.
19. **What do the diffuse residuals do?** They make Ljung-Box look terrible (p about 0) when it is fine; drop `loglikelihood_burn` residuals.
20. **How do you know the numbers are right?** Every slide/report number is a macro from `results/`; `verify_numbers.py` re-derives them (independent HAC, VAR, refits, bootstrap); two outside audits recomputed them from raw data.

---

## 9. Glossary

- **AIC / AICc:** model-selection criteria penalising parameters; AICc adds a small-sample correction.
- **ADF / KPSS:** unit-root test / stationarity test with opposite nulls.
- **ARMA(p,q):** autoregressive moving-average errors; **ARIMA(p,d,q)** adds d differences.
- **ARCH-LM:** test for volatility clustering.
- **Box-Cox:** power transform; the log is its limit at lambda 0.
- **Burn-in (diffuse):** the first residuals of a state-space model with diffuse initial states; must be dropped before diagnostics.
- **Climatology:** the average value of each calendar week over the training years.
- **Coverage:** share of actual values inside the prediction interval.
- **DHR:** dynamic harmonic regression (Fourier terms plus ARMA errors).
- **DM / HLN:** Diebold-Mariano forecast-comparison test and its small-sample correction (valid for one-step errors).
- **Expanding window:** training set grows with each origin; the test period moves forward.
- **FEVD:** share of a variable's forecast-error variance due to each shock.
- **Granger causality:** predictive content of one series for another.
- **HAC:** heteroskedasticity-and-autocorrelation-consistent covariance (Newey-West).
- **IRF / GIRF:** impulse response (Cholesky, ordering-dependent) / generalised, ordering-free.
- **Ljung-Box:** residual autocorrelation test.
- **LSTM:** long short-term memory recurrent neural network.
- **MAE:** mean absolute error.
- **Origin:** the last training week; the forecast starts the week after.
- **Oracle weather:** the actual weather of the forecast week, known only with hindsight.
- **PM2.5 band:** CPCB PM2.5 breakpoints (not the full AQI).
- **SARIMA(p,d,q)(P,D,Q)_s:** seasonal ARIMA with seasonal period s.
- **STL:** seasonal-trend decomposition by loess.
- **VAR:** vector autoregression.
- **Winkler score:** interval score combining width and misses (lower is better).
- **W-SUN:** weekly frequency ending on Sunday.

---

## 10. Appendix: references and how each was verified

The report cites 27 references. Each was checked on 17 Nov 2026; treat this table as the audit trail. **Crossref** = the DOI was looked up at `api.crossref.org/works/<doi>` and the authors, title, year, journal, volume, issue and pages compared with the bibliography entry. Crossref gives only the first page for older JSTOR items, so end pages for those were confirmed on a second source (RePEc/EconBiz/Econometric Society pages) as noted.

| # | Reference | How verified | Result |
|---|---|---|---|
| 1 | CPCB, National Air Quality Index, Oct 2014 | web search of the NIUA-hosted copy (CPCB report, MoEF&CC, Oct 2014); PM2.5 breakpoints confirmed on IES Arthapedia (citing CPCB): 0-30, 31-60, 61-90, 91-120, 121-250, 250+ | confirmed; the PDF itself could not be fetched, so cited by title and issuer only |
| 2 | Box, Jenkins, Reinsel, Ljung, *Time Series Analysis: Forecasting and Control*, 5th ed., Wiley, 2015 | confirmed as the 5th ed. in the FPP3 "further reading" entry | confirmed (not checked in Crossref) |
| 3 | Rao, Kaggle "Air Quality Data in India (2015-2020)" | web search; page returns HTTP 200; title and owner confirmed via mirrors | confirmed |
| 4 | Hersbach et al. 2020, ERA5, QJRMS 146(730):1999-2049 | Crossref 10.1002/qj.3803 | match |
| 5 | Zippenfenig 2023, Open-Meteo.com Weather API, Zenodo | DOI 10.5281/zenodo.7970649 is the concept DOI listed on open-meteo.com/en/licence; resolves via doi.org (HTTP 200); not in Crossref (DataCite) | confirmed; we cite the concept DOI (a version-specific DOI also exists) |
| 6 | Cleveland et al. 1990, STL, J. Official Statistics 6(1):3-73 | statsmodels and stlplus documentation both cite exactly this; no DOI | confirmed |
| 7 | Box and Cox 1964, JRSS-B 26(2):211-243 | Crossref 10.1111/j.2517-6161.1964.tb00553.x | match |
| 8 | Engle 1982, Econometrica 50(4) | Crossref 10.2307/1912773; pages 987-1007 confirmed via EconBiz/Econometric Society (some databases print 987-1008) | match |
| 9 | Dickey and Fuller 1979, JASA 74(366a):427-431 | Crossref 10.1080/01621459.1979.10482531 | match (Crossref issue label "366a") |
| 10 | Kwiatkowski et al. 1992, J. Econometrics 54(1-3):159-178 | Crossref 10.1016/0304-4076(92)90104-Y | match |
| 11 | Sims 1980, Econometrica 48(1):1-48 | Crossref 10.2307/1912017; pages via Econometric Society | match |
| 12 | Lutkepohl 2005, New Introduction to Multiple Time Series Analysis, Springer | Crossref 10.1007/978-3-540-27752-1 | match |
| 13 | Granger 1969, Econometrica 37(3):424-438 | Crossref 10.2307/1912791; pages via RePEc/Econometric Society | match |
| 14 | Newey and West 1987, Econometrica 55(3):703-708 | Crossref 10.2307/1913610; pages via EconBiz/Stata manual | match |
| 15 | Pesaran and Shin 1998, Economics Letters 58(1):17-29 | Crossref 10.1016/S0165-1765(97)00214-0 | match |
| 16 | Hyndman and Athanasopoulos, FPP3, section 10.5 "Dynamic harmonic regression" | otexts.com/fpp3/dhr.html fetched: section 10.5 in chapter "Dynamic regression models"; 3rd edition released Feb 2021 | confirmed (authors not printed on that page; authorship is standard) |
| 17 | Hurvich and Tsai 1989, Biometrika 76(2):297-307 | Crossref 10.1093/biomet/76.2.297 | match |
| 18 | Hochreiter and Schmidhuber 1997, Neural Computation 9(8):1735-1780 | Crossref 10.1162/neco.1997.9.8.1735 | match |
| 19 | Tashman 2000, Int. J. Forecasting 16(4):437-450 | Crossref 10.1016/S0169-2070(00)00065-0 | match |
| 20 | Winkler 1972, JASA 67(337):187-191 | Crossref 10.1080/01621459.1972.10481224 | match |
| 21 | Gneiting and Raftery 2007, JASA 102(477):359-378 | Crossref 10.1198/016214506000001437 | match |
| 22 | Kunsch 1989, Annals of Statistics 17(3):1217-1241 | Crossref 10.1214/aos/1176347265 | match |
| 23 | Diebold and Mariano 1995, JBES 13(3):253-263 | Crossref 10.1080/07350015.1995.10524599 | match |
| 24 | Harvey, Leybourne, Newbold 1997, Int. J. Forecasting 13(2):281-291 | Crossref 10.1016/S0169-2070(96)00719-4 | match |
| 25 | Ljung and Box 1978, Biometrika 65(2):297-303 | Crossref 10.1093/biomet/65.2.297 | match |
| 26 | Durbin and Koopman, *Time Series Analysis by State Space Methods*, 2nd ed., OUP, 2012 | Crossref 10.1093/acprof:oso/9780199641178.001.0001 (year 2012, monograph) | match; "2nd ed." from the publisher's standard edition statement, not shown by Crossref |
| 27 | Mahato, Pal, Ghosh 2020, Sci. Total Environ. 730:139086 | Crossref 10.1016/j.scitotenv.2020.139086 | match |

Not cited because not verified: the Politis-Romano stationary bootstrap and Seabold-Perktold (statsmodels) were considered; the latter verified in Crossref (10.25080/Majora-92bf1922-011) but is not cited in the final report, so add it if you cite the software.
