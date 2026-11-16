# 06 What three earlier reviews claimed and what we found

# Review responses: every claim checked against the data

Three independent reviews of the project (Claude: `gemini_context/06_critical_review.md` before the final rewrite; Gemini: `docs/reviews/Geminiplan.md`; GPT: `docs/reviews/gpt.md`) raised the points below.
Each was **re-checked on the data** before acting. "Where" gives the notebook/file that now holds the evidence. Verdicts: **Accepted** (bug or valid point, fixed), **Partly** (right idea, wrong detail), **Rejected** (checked, not true), **Noted** (limit we state rather than fix).

## A. Bugs and statistical errors

| # | Claim (source) | Verdict | Evidence and fix | Where |
|---|---|---|---|---|
| A1 | Ljung-Box p≈0 in the SARIMA draft is an artifact of the 52 diffuse initial residuals (all three) | **Accepted** | `loglikelihood_burn = 52`; with them p = 0 at lag 10, without them p = 0.49 (lag 10), 0.10 (lag 26). **Lag 52 is p = 0.016** (GPT asked for it; the first reviews missed it). `resid_diagnostics()` drops the burn-in | nb04 §3, `src/forecast.py` |
| A2 | Seasonal MA −0.988 means over-differencing (all) | **Accepted, strengthened** | Coefficient −0.988 with SE ≫ 1 (not identified). The D=1 SARIMA also collapses in the 2-year-training fold (MAE 54) | nb04 §3 |
| A3 | D=0 candidates were fit with no constant (`trend='n'`) (Gemini) | **Accepted, effect overstated** | With a constant the D=0 validation MAE falls 39.7 → 30.6 but D=1 still wins on that fold; SARIMA D=0 with constant is still the worst non-LSTM model in the final backtest (44). Fixed: D=0 benchmark uses `trend='c'` | `src/forecast.py` |
| A4 | All 8 misses of the 2019 interval are below the lower bound, so it is level bias, not width (Gemini, GPT) | **Accepted** | 8 below, 0 above; mean log error −0.18. Calibration rule re-centres only if the bias has the same sign and |z|>0.5 in both calibration folds (it did not: −0.66 and −0.45 → below threshold 0.5 in 2018), and rescales spread by season | nb04 §4 |
| A5 | Re-anchoring the level gives 94.2% coverage (Gemini) | **Rejected (number)** | Tested: it gives 90.4% (MAE 25.5). Seasonal scaling from earlier folds gives 96% on 2019 | nb04 §4 |
| A6 | ISO-week folding shifts all of 2016 (Gemini) | **Partly** | Only the week ending 2016-01-03 is ISO week 53 and was merged into week 52. Replaced by one consistent index `week_index()` (Thursday's day-of-year, leap-aware) used everywhere | `src/tsa.py` |
| A7 | Leap years: day-of-year capped at 365 mis-aligns Feb 29 onwards (GPT) | **Accepted (minor)** | `doy365()` maps Feb 29 to day 59 and shifts later days; all anomalies recomputed | `src/tsa.py`, nb02/03 |
| A8 | Shock bins are same-day values and suffer a Jensen bias (Gemini) | **Rejected** | The code takes `exp(mean of the log change from day t−1 to t+1) − 1`: not same-day, no Jensen bias. Wording on the slide is now explicit ("day t+1 vs day t−1") | `make_figures.py`, deck |
| A9 | Weekly R² 0.139 vs 0.140 compares non-nested models (Gemini) | **Accepted** | Replaced by a nested comparison: lagged PM2.5 alone R² 0.134 vs + lagged weather 0.139 (ΔR² = 0.005), joint HAC Wald p = 0.51 | nb03 §9, `weekly_lag_nested.csv` |
| A10 | "p < 1e-10 in every specification" is false (GPT) | **Accepted** | With the rain control humidity p = 2.8e-8 (3e-11 → 7e-8 with rain and temperature). Text now quotes the right p-values | nb03, deck |
| A11 | "Significant at every lag 1–7" is a joint test at each lag order, not per-lag significance (GPT) | **Accepted** | Wording changed to "joint tests at every lag order 1–7"; per-lag-order Wald table saved | `granger_hac_by_lag.csv` |
| A12 | The slides quote reverse-direction p-values (0.04, 0.016) that exist nowhere in `results/` (my review) | **Accepted** | Now saved: PM2.5 → wind is significant at lag orders 1–2 (p = 0.038, 0.015) and not from 3 on | `granger_hac_by_lag.csv` |
| A13 | A PM2.5 band is not the official AQI, which is the max sub-index (GPT) | **Accepted** | Everything relabelled "PM2.5 sub-index band"; `aqi.py` docstring and slides updated | deck, `src/aqi.py` |
| A14 | The lognormal mean correction should be horizon-specific (GPT) | **Accepted** | RMSE uses `exp(mu_h + sd_h²/2)`; MAE uses the median | `src/forecast.py` |
| A15 | A plain Diebold-Mariano on one 52-step path is invalid (GPT) | **Accepted** | 52-week comparisons use a moving-block bootstrap of paired errors over three origins and say "indistinguishable" when the CI contains 0. HLN-DM is used only for the genuine one-step comparison | nb04 §2, §5 |
| A16 | Headline STL strength / Box-Cox / drift use test-period data (my review, Gemini, GPT) | **Accepted** | Headline F_S = 0.90 on 2015–2018 weeks (full sample 0.89); Box-Cox λ train ≈ 0.10 (full 0.045), still ≈ log. Full-sample values kept alongside | nb02 |
| A17 | The 2019 test-year was used to pick the order via 2018 validation overlap (all) | **Accepted** | Selection (K, p, q, level treatment) happens inside each training window with an inner validation year; nothing after the origin is used. Asserted in code (`idx[0] > train end`) | `src/forecast.py` |
| A18 | `__pycache__` tracked, no .gitignore, notebook 04 never executed (my review, GPT) | **Accepted** | `.gitignore`, untracked caches, all four notebooks executed with saved outputs | repo |

## B. Interpretation and over-claims

| # | Claim | Verdict | Evidence and fix |
|---|---|---|---|
| B1 | "Weather drives PM2.5" overstates Granger causality (all) | **Accepted** | Reworded to "robust predictive association" everywhere; still not proof of a physical cause |
| B2 | Omitted variables: temperature is available but unused (Gemini, GPT) | **Accepted** | Temperature control added: wind p 2.5e-18, humidity p 1.4e-9 (still significant); boundary-layer height not available in the data (stated as a limit) |
| B3 | KPSS rejection for the anomaly shows drift, not a unit root; test a trend / training-only climatology (Gemini, GPT) | **Accepted** | KPSS statistic on the anomaly: 0.90 (2015–18) and 2.0 (2015–19) vs 0.46 critical: a real level drift. Granger results are unchanged with a linear trend (p 5.5e-20) and with a training-only climatology (p 6.9e-20) |
| B4 | Humidity effect is monsoon-specific (Gemini, my review) | **Rejected as a predictive claim** | Season-interaction test: monsoon × humidity p = 0.20 (not significant); winter × wind p = 0.03. Wind and humidity are significant in *both* seasons (p ≤ 5e-4). Only the *correlation* pattern differs by season |
| B5 | Reverse PM2.5 → wind reflects synoptic stagnation (Gemini) | **Noted** | Plausible but untested (no boundary-layer data); stated as a possibility only |
| B6 | Cholesky orderings: use generalised IRFs and bands (GPT) | **Accepted** | GIRF day-1: wind −12.0%, humidity −5.2%, inside/near the Cholesky range (−6% to −12%, −4% to −7%); bands saved for both orderings |
| B7 | Weather-first ordering is "the physically preferred" one (Gemini) | **Rejected as a claim** | Daily means share the same 24 h; we report the range and call it identification-dependent |
| B8 | The 2016–19 decline may be a monitor-network artifact (GPT, Gemini, my review) | **Tested** | Stations reporting: 10, 8, 17, 37, 37. But a fixed 6-station panel falls ≈ 20%, all stations ≈ 25%, the weather-adjusted city series ≈ 18% (2016 → 2019): mostly real, with caveats (thin 2017 panel) | nb02 §8 |
| B9 | The "same-week weather" 1-week SARIMAX is an upper bound (all) | **Accepted** | Three variants: lagged weather, last 3 days, same-week (oracle). Result: lagged −2.4%, last-3-days +0.7%, oracle +6.9% (HLN-DM p = 0.07) |
| B10 | Forecast date: data stop in 2020, so "next 12 months" is not current (GPT Q16) | **Accepted (Option A)** | Historical forecasting study: backtests for 2017–19 and a 2020 outlook made from data to Dec 2019, validated by the Jan–Jun 2020 actuals. We do not claim a current advisory |
| B11 | Weekly means cannot give daily AQI categories (all) | **Accepted** | Weekly paths + within-week daily offsets give expected days per PM2.5 band; validated on 2019 (all 12 months inside the interval, but Poor+ share over-predicted: 55% vs 45%) |
| B12 | Conformal prediction is not justified with this little data (GPT) | **Accepted** | Not used; simple season scaling from earlier folds, checked on a later year |
| B13 | GARCH is not needed on weekly residuals (all) | **Accepted** | ARCH-LM(4) on weekly residuals p = 0.87 |
| B14 | TBATS / Prophet suggested (my review) vs "too heavy" (Gemini) | **Partly** | Neither run. Fourier + ARMA is the parsimonious equivalent; adding them would not change the conclusion that the calendar dominates |

## C. New findings from the rework (not raised by any review)

1. The pre-declared headline model is **not** significantly better than climatology (2018–19 MAE 24.6 vs 24.8); the variant with a linear trend is better on 2018–19 (CI excludes 0) but not over all three origins and was not chosen in advance. We report both and claim neither.
2. In the 2-year-training fold (2017) SARIMA D=1 collapses (MAE 54 vs 31 for climatology): another reason to avoid unnecessary seasonal differencing.
3. The calibrated 2020 forecast intervals are *narrower* than those for 2019 (scale factors 1.09/0.95 vs 1.33/1.42): the calibration is fold-dependent, which we report instead of hiding.
4. The 2020 forecast correctly flags the lockdown: March–May means fall below the 95% interval; PM2.5 was ≈ 43% below the no-lockdown forecast (≈ 38% after weather adjustment).
5. The pipeline over-predicts the share of Poor-or-worse days in 2019 (55% vs 45%): the level bias noted above carries into the band table.
