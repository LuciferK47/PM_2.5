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

1. The headline Fourier+ARMA procedure is **not** significantly better than climatology (2018-19 MAE 24.6 vs 24.8); neither is the linear-trend variant (21.9, interval -6.1 to +0.7), so nothing beats climatology (Round 2, R12).
2. In the 2-year-training fold (2017) SARIMA D=1 collapses (MAE 54 vs 31 for climatology): another reason to avoid unnecessary seasonal differencing.
3. The calibrated 2020 forecast intervals are *narrower* than those for 2019 (scale factors 1.09/0.95 vs 1.33/1.42): the calibration is fold-dependent, which we report instead of hiding; calibration also widens intervals and worsens the Winkler score.
4. The observed March-June 2020 monthly means fall below the 95% interval; lockdown-period PM2.5 was about 43% below the model's no-lockdown median (35-51% across adjustments; a 2019 placebo gives 15%): descriptive, not causal.
5. The pipeline over-predicts the share of Poor-or-worse days in 2019 (55% vs 45%): the level bias noted above carries into the band table.

## Round 2: outside verification audits of the finished project (Gemini and GPT)
Both audits (`docs/reviews/round2/`) received `verification_pack/` and recomputed the headline numbers. Every number they recomputed matched. They also reported code bugs, checker defects and over-claims, each re-tested against the code and data before acting. Gemini's statement that it ran `verify_numbers.py` (63/65) could not have been done from the pack, which did not contain the raw data, so it is not relied on.

| # | Claim (source) | Verdict | Evidence and fix |
|---|---|---|---|
| R1 | LSTM recursive input pairs each anomaly with the calendar row of the *next* week (GPT) | **Accepted, confirmed** | `forecast.py` built the window as `Cp[j+1:] + Cf[:j+1]`. Now one helper (`lstm_window`) builds training and forecast windows, with a unit test. Rerun: MAE 36.3 / 28.3 / 54.3 (was 36.3 / 49.2 / 52.9): 2018 improves, still clearly worse than climatology over 2018-19. |
| R2 | verify_numbers checks April-June against March-May intervals (GPT) | **Accepted, confirmed** | `month == i_ + 1`. Fixed; each month now compared with its own interval and June added. Conclusion unchanged (Mar-Jun all below). |
| R3 | Persistence check skips the first test week (GPT) | **Accepted** | `.iloc[1:]` removed, tolerance 0.6 -> 0.01. |
| R4 | Link checks fail offline (Gemini) | **Accepted** | HTTP 000 is reported as offline and the local raw files are checked instead. |
| R5 | Report: seasonal Granger "p <= 5e-4"; winter humidity is 5.35e-4 (GPT) | **Accepted** | Report now says all p < 1e-3; a verify check enforces it. |
| R6 | Report: D=0 MAE "39.7 -> 30.6" with a constant has no saved evidence (GPT) | **Accepted** | Came from a planning run, not a saved result. Replaced by a matched table (`fc_sarima_d0_constant.csv`): without constant 76.9 / 61.0 / 92.1, with 44.9 / 42.8 / 44.1, climatology 31.0 / 21.8 / 27.8. |
| R7 | June 2020 omitted (GPT) | **Accepted** | June actual 46.7 < lower bound 48.7. Deck and report now say March-June; verify check extended. |
| R8 | Calibration raises coverage but widens intervals and worsens the Winkler score (GPT) | **Accepted** | Width 125 -> 179, Winkler 175 -> 193; now stated everywhere; "calibrated" reworded to "interval widths rescaled". 2017 coverage 69% is also reported. |
| R9 | "ARMA" label although the rw level is ARIMA(p,1,q) (GPT) | **Accepted** | Wording changed in definitions (label kept). |
| R10 | `_best_by_aicc` accepts non-converged fits; warnings suppressed globally (GPT) | **Accepted** | Fits with `converged = False` are rejected and counted (6 / 3 / 5 per origin); warnings now suppressed only inside the fit call. Selected specs unchanged. |
| R11 | Monthly means and band-day counts come from different draws (GPT) | **Accepted** | `daily_paths` draws a whole Mon-Sun offset vector per simulated week (mean(exp(offset)) = 1), so every week averages exactly to its simulated weekly mean; both outputs derive from the same daily paths. 2019 validation: 12/12 months inside; Poor+ 55.1% predicted vs 45.2% actual (unchanged story). |
| R12 | Block bootstrap joins forecast years (Gemini, GPT) | **Accepted; found a second bug** | Blocks are now drawn within each fold. My first version (non-circular) under-sampled the first and last weeks and gave biased intervals (it declared the linear variant and the selected model "better"); the final version is circular. Result: **no model beats climatology significantly**; the linear variant (-2.9, CI -6.1 to +0.7) is indistinguishable. Seasonal naive, SARIMA D=0 and the LSTM are clearly worse; SARIMA D=1 is worse over all three folds. |
| R13 | Constant predictive sd for linear regression and LSTM (Gemini) | **Accepted** | Linear regression: OLS prediction sd with parameter uncertainty. LSTM: sd from in-sample recursive h-step errors (non-decreasing, capped). Climatology and seasonal naive now carry an sd, so RMSE uses the mean forecast for every model. |
| R14 | Calibration threshold ignores consistent negative bias (Gemini) | **Partly** | The step rule was fixed before 2019 was seen; replacing it afterwards would tune on the test year. Added as a labelled post-hoc sensitivity: a shrunk shift gives 2019 bias +4.3, MAE 23.6, Winkler 161, but is not adopted. |
| R15 | Lockdown gap confounded by model level bias; window starts 23 Mar (both) | **Accepted** | The model was already 11% high in the 12 weeks before the lockdown. New sensitivity table: adjusted gap -35%; constant level -51%; random-walk -43%; 9-week window -42%; post-hoc shift -37%; 2019 placebo -15% (interval spans 0). Wording now "observed PM2.5 was about 43% below the model's no-lockdown median", range 37-51%, not causal. |
| R16 | Over-claims: "matches or slightly beats", "weather adds nothing", "decline is real", "cut PM2.5 by 43%", "65 checks verify every number", "pre-declared / untouched 2019", "LSTM clearly worse" (both) | **Accepted** | Reworded across deck, report, script and README; 2019 described as examined in earlier iterations. |
| R17 | Bootstrap and tests rest on only three origins (both) | **Accepted** | Stated in limitations; no stronger claim made. |
| R18 | Report omits lag-10 Ljung-Box p = 0.088 (Gemini) | **Accepted** | Added. |
| R19 | 52-week fold naming and week-53 cap (GPT) | **Accepted** | Notebook text: the 2017 fold ends 24 Dec 2017; week 53 is folded into 52; seasonal naive is 52 weeks back. |
| R20 | `verify_numbers.py` is not comprehensive (both) | **Accepted** | Described as selected checks. New checks: LSTM alignment, daily-path coherence, saved-forecast recomputation of all MAEs, bootstrap table, one-step MAEs, lockdown sensitivity arithmetic, calibration direction, D=0 table, Granger bound. |
| R21 | Fixed 6-station panel does not prove the decline is real (GPT) | **Accepted** | Wording: "consistent with a genuine decline; network effect not fully excluded". |
| R22 | Gemini: Granger "drive/explain" wording | **Accepted** | "Predictive association" throughout; deck question changed to "Does weather predict PM2.5?". |
| R23 | Gemini: LSTM strawman | **Partly** | It is a small untuned baseline, stated as such; no claim about neural networks. |
