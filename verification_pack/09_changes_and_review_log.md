# 09 Changes and review log

## git log (main..HEAD)
```
e7256a8 Round 3 fixes: unrounded MAE macros and checker for every MAE macro (86 checks), band days to one decimal, D=0 fit details, LSTM interval labelled heuristic, softened station/SARIMA/short-memory wording, generated ledger
d5d5e26 Verification pack v3 (full-precision data, daily table, station summary, claims ledger) and refreshed LLM briefs
1a93049 Deck, report, script, README, review log: round-2 corrections and softened claims; file both audits
5f1fb42 verify_numbers: fix month off-by-one and persistence week, offline-safe link checks, 13 new checks (78 total)
03a2dce Notebook 04: matched SARIMA D=0 table, calibration width/Winkler and post-hoc shift sensitivity, one-step forecasts saved, lockdown sensitivities and placebo; re-executed
5cef57e src: fix LSTM window alignment, horizon-specific sd for linreg/LSTM/benchmarks, reject non-converged fits, per-fold circular block bootstrap, coherent daily paths
76e359e Add verification pack (recompute data, code, results, claims ledger) for external audit
3397b23 Deck, report, review-response log, README, presentation script, LLM briefs, verification (65 checks)
9b351f9 Notebook 04: rolling-origin backtest, diagnostics, calibration, 1-week weather test, 2020 outlook, lockdown case study; archive SARIMA draft
2a3d6bc Notebooks 02-03: training-only headline stats, level-drift and station check, extra Granger robustness (temp, trend, seasonal, by-lag), GIRF, nested weekly test; re-executed
d671a29 src: leap-safe climatology, week index, forecasting toolkit, PM2.5-band labelling; pin requirements
982b5ab Baseline: hygiene (.gitignore, untrack pycache) and existing phase 2-3 rework, beamer deck, SARIMA draft, review inputs
```

## Review responses (every claim from five reviews, with verdict, evidence, fix; Round 2 at the end)
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
| R11 | Monthly means and band-day counts come from different draws (GPT) | **Accepted** | `daily_paths` draws a whole Mon-Sun offset vector per simulated week (mean(exp(offset)) = 1), so every week averages exactly to its simulated weekly mean; both outputs derive from the same daily paths. 2019 validation: 12/12 months inside; Poor+ 55.0% predicted vs 45.2% actual (unchanged story). |
| R12 | Block bootstrap joins forecast years (Gemini, GPT) | **Accepted; found a second bug** | Blocks are now drawn within each fold. My first version (non-circular) under-sampled the first and last weeks and gave biased intervals (it declared the linear variant and the selected model "better"); the final version is circular. Result: **no model beats climatology significantly**; the linear variant (-2.9, CI -6.1 to +0.7) is indistinguishable. Seasonal naive, SARIMA D=0 and the LSTM are clearly worse; SARIMA D=1 is worse over all three folds. |
| R13 | Constant predictive sd for linear regression and LSTM (Gemini) | **Accepted** | Linear regression: OLS prediction sd with parameter uncertainty. LSTM: sd from in-sample recursive h-step errors (non-decreasing, capped). Climatology and seasonal naive now carry an sd, so RMSE uses the mean forecast for every model. |
| R14 | Calibration threshold ignores consistent negative bias (Gemini) | **Partly** | The step rule was fixed before 2019 was seen; replacing it afterwards would tune on the test year. Added as a labelled post-hoc sensitivity: a shrunk shift gives 2019 bias +4.3, MAE 23.6, Winkler 161, but is not adopted. |
| R15 | Lockdown gap confounded by model level bias; window starts 23 Mar (both) | **Accepted** | The model was already 11% high in the 12 weeks before the lockdown. New sensitivity table: adjusted gap -36%; constant level -51%; random-walk -43%; 9-week window -42%; post-hoc shift -37%; 2019 placebo -15% (interval spans 0). Wording now "observed PM2.5 was about 43% below the model's no-lockdown median", range 37-51%, not causal. |
| R16 | Over-claims: "matches or slightly beats", "weather adds nothing", "decline is real", "cut PM2.5 by 43%", "65 checks verify every number", "pre-declared / untouched 2019", "LSTM clearly worse" (both) | **Accepted** | Reworded across deck, report, script and README; 2019 described as examined in earlier iterations. |
| R17 | Bootstrap and tests rest on only three origins (both) | **Accepted** | Stated in limitations; no stronger claim made. |
| R18 | Report omits lag-10 Ljung-Box p = 0.088 (Gemini) | **Accepted** | Added. |
| R19 | 52-week fold naming and week-53 cap (GPT) | **Accepted** | Notebook text: the 2017 fold ends 24 Dec 2017; week 53 is folded into 52; seasonal naive is 52 weeks back. |
| R20 | `verify_numbers.py` is not comprehensive (both) | **Accepted** | Described as selected checks. New checks: LSTM alignment, daily-path coherence, saved-forecast recomputation of all MAEs, bootstrap table, one-step MAEs, lockdown sensitivity arithmetic, calibration direction, D=0 table, Granger bound. |
| R21 | Fixed 6-station panel does not prove the decline is real (GPT) | **Accepted** | Wording: "consistent with a genuine decline; network effect not fully excluded". |
| R22 | Gemini: Granger "drive/explain" wording | **Accepted** | "Predictive association" throughout; deck question changed to "Does weather predict PM2.5?". |
| R23 | Gemini: LSTM strawman | **Partly** | It is a small untuned baseline, stated as such; no claim about neural networks. |

## Round 3: final verification audits (Gemini and GPT)
Gemini found nothing to correct (78/78, all claims reproduced; optional: Makefile fallback, archive legacy PDF). GPT reproduced the core numbers and found the following, all re-tested:

| # | Claim (source) | Verdict | Fix |
|---|---|---|---|
| S1 | Macros `fcMaeSarimaNineteen` 27.4 and `fcMaeLstmNineteen` 54.4 are double-rounded (true 27.5, 54.3) (GPT) | **Accepted, confirmed** | `make_figures.py` now reads unrounded MAEs from `fc_backtest_metrics.csv`; `verify_numbers.py` checks every MAE macro against the unrounded value (86 checks). |
| S2 | README ledger: June lower bound 48.7 (true 47.9); lockdown median 85.1 vs 85.0 (GPT) | **Accepted** | The ledger is now generated from `results/` at build time. |
| S3 | 2019 predicted band days rounded to integers sum to 366 (GPT) | **Accepted** | Stored with one decimal (sum 365.0); a checker test enforces it. |
| S4 | SARIMA D=0 without constant is numerically fragile (AR root 0.999; refit gave 64.8 and 81.5-92.1) (GPT) | **Accepted** | Fit details and software versions saved in `fc_sarima_d0_fit_details.csv`; text says "60-90, much worse than climatology"; with-constant result reproduces. |
| S5 | LSTM interval uses in-sample recursive errors, so it is optimistic (GPT) | **Accepted** | Labelled a heuristic in the notebook, report and limits. Point MAEs unaffected. |
| S6 | Seasonal MA near -1 does not prove differencing is unnecessary; SE unstable (GPT) | **Accepted** | Report and deck say "possible over-differencing, identification problem"; SE flagged as unstable. |
| S7 | "Most of the decline is real" too strong (GPT) | **Accepted** | "Persists in a restricted panel and after weather adjustment; consistent with a genuine component; network effect not ruled out." |
| S8 | "No model significantly better" should be tied to the design; "short-memory predictor" stronger than a non-significant test proves; first sentence says "air is Poor or worse" (GPT) | **Accepted** | Reworded (limited rolling-origin evaluation; "within the tested specification"; "PM2.5 sub-index band"). |
| S9 | 12/12 monthly means inside is not proof of calibration (GPT) | **Already stated**; the 55% vs 45% over-prediction is reported next to it. |
| S10 | Path-level simulation draws not preserved; lockdown quantiles not reconstructable (GPT) | **Noted** | Simulated quantities vary by about 0.3 percentage points between re-runs (Monte-Carlo noise: lockdown gap -42.8 to -43.1%); stated, not hidden. |
| S11 | Gemini: Makefile fallback; legacy `Slides.pdf` at the repo root | **Optional; not done** |

## Round 2 audit documents
### GPT
# Independent verification audit — Delhi PM2.5 (`phase4-final`)

Scope: `00_VERIFY_README.md` and supplied files 01–09. Recomputed from the **rounded** weekly data (287 records) and raw backtest predictions (1,560 records) in `06_raw_data_for_recompute.md`. Source-line pointers refer to the supplied Markdown files. No original daily CPCB/ERA5 files, station-level CSVs, actual `numbers.tex`, or simulation-path records were supplied. Consequently, statements dependent on these assets are **internally checked, not independently reproduced**. This audit does not claim to have run `verify_numbers.py` end-to-end.

## I. Ledger of 15 claims

| Ledger | Independent finding | Status |
|---|---|---|
| 1. Forecast MAE for 2017/18/19 | Independently recomputed all ten models, all three folds. Selected model 31.483/23.426/25.695; climatology 30.998/21.774/27.818; SARIMA D=1 53.827/21.083/27.452; D=0 44.874/42.834/44.103; LSTM 36.291/49.231/52.869. | **PASS** (stored forecast rows) |
| 2. Calendar-week climatology | Rebuilt group means of log weekly PM2.5 using the training years and `week_index`. Stored predictions agree to <0.00008 log units, explained by input rounding. | **PASS** |
| 3. Seasonal naive | Stored median forecasts match the observed PM2.5 52 weeks earlier exactly, across all three folds. | **PASS** |
| 4. Moving-block CI | Re-ran RNG seed=0, block length 8, 4,000 replications. Selected minus climatology (2018–19) mean difference −0.235 µg/m³, CI [−3.558,+1.806]; Fourier linear −2.942, CI [−6.430,−0.357]. | **PASS arithmetic**, inferential caveat (few origins) |
| 5. Raw/calibrated intervals | Raw selected 2019: 47/52 =90.3846%. Applying stored seasonal scale factors 1.33430955 winter, 1.42153240 non-winter: 50/52 =96.1538%. | **PASS**, calibration score worsens |
| 6. Misses by year | 2017: 10 below/6 above, 36/52=69.23%; 2018: 2 below/1 above, 49/52=94.23%; 2019: 5 below/0 above, 47/52=90.38%. | **PASS** |
| 7. One-week weather | From `05` table: no weather 22.39; lagged 22.92 (−2.4% gain), prior-last-3-days 22.24 (+0.7%), same-week oracle 20.84 (+6.9%); DM/HLN approx 0.074. Raw one-step forecasts are **not** supplied in `06`, so cannot independently recompute its errors or p-value. | **Consistent, unverified from raw** |
| 8. Daily Granger | Report values match `05` tables (base HAC p roughly 6e−20 and 4e−11; with rain/temp roughly 9e−18 and 7e−8). Full daily anomaly inputs absent; exact p-values not independently re-estimated. | **Table-consistent, not independently reproduced** |
| 9. Weekly nested weather | Independently implemented the lag-1 nested regression on supplied weekly data. R² base 0.13408324, full 0.13908401, ΔR²=0.00500077, joint HAC Wald p=0.5146397. | **PASS** |
| 10. 2019 monthly pipeline | `05` reports 12/12 monthly means inside 95% and Poor+ 55.0% predicted vs 45.2% actual. Weekly raw file cannot reconstruct daily observed counts, stochastic daily profiles, or Monte Carlo draws. | **Unverifiable from raw pack** |
| 11. Lockdown contrast | Ten weeks 29 Mar–31 May 2020: actual mean 48.66972 (from `06`) vs reported model counterfactual median 85.14075 (`05`), (actual/median−1)=−42.836%; weather-adjusted median 78.46681, −37.974%. Counterfactual simulation distribution and interval **not supplied**. | **Percent arithmetic PASS; causal meaning NOT established** |
| 12. Station-panel decline | Reported log-anomaly changes imply exp(−0.163−0.121)−1=−24.72%; fixed panel exp(−0.132−0.088)−1=−19.75%; weather-adjusted exp(−0.110−0.085)−1=−17.72%. **Required raw station_day.csv absent**: cannot verify 6-station panel or composition claims. | **Arithmetic PASS; underlying evidence unavailable** |
| 13. SARIMA diffuse burn-in | `04` reports drop initial 52 residuals, Ljung–Box p=.49 (lag10), .10 (lag26), .016 (lag52). Without original full-precision series cannot independently refit identical parameters. | **Code/output-consistent** |
| 14. Seasonal MA −.988, SE 8.26 | Reported in notebook and `05`; cannot refit exactly. Very high SE signals weak identification, rather than quantitatively proving over-differencing. | **Code/output-consistent** |
| 15. Leap-year `doy365` | Code maps Feb29 to Feb28 index, subtracts 1 from Mar1–Dec31 during leap years, giving 365-day seasonal alignment. | **PASS**, residual 53-week-compression caveat |

## II. Independently recalculated MAE (µg/m³)

| Model | 2017 | 2018 | 2019 |
|---|---:|---:|---:|
| Fourier+ARMA selected |31.483|23.426|25.695|
| Climatology |30.998|21.774|27.818|
| SARIMA D1 |53.827|21.083|27.452|
| SARIMA D0 |44.874|42.834|44.103|
| Fourier+ARMA linear |35.856|19.733|23.974|
| Climatology+AR1 |30.701|21.668|27.327|
| Fourier+ARMA const |30.593|22.048|29.262|
| Linear regression |35.893|19.991|24.944|
| LSTM |36.291|49.231|52.869|
| Seasonal naive |38.438|28.965|30.306|

Computed 287 equally spaced weekly observations (2015-01-04–2020-06-28). Weekly ln(PM2.5) differs from supplied rounded log column by no more than 0.00005.

## III. Report/deck vs tables — specific mismatches or unsupported numbers

1. **Seasonal Granger p-value overstatement** — `08_report_and_deck_text.md`, report Granger paragraph, ~line 46: claims both wind and humidity significant in winter and monsoon at *p* ≤ 5×10^-4. `05_all_results_tables.md`, `granger_hac_seasonal.csv`, winter humidity **p=0.00053516**, which is slightly GREATER than 0.0005. Change to `p < 0.001` or quote exact maximum.
2. **Missing-constant D0 MAE 39.7→30.6 unsupported** — `08` report ~line 61 says introducing constant improves validation MAE from 39.7 to 30.6; current `05` table `fc_backtest_mae.csv` lists D0 MAEs **44.9, 42.8, 44.1**, and the value 30.6 belongs to `Fourier+ARMA const`, 2017. These may refer to distinct draft configurations/horizons; without a saved matched-pair output, the exact 30.6 improvement is **not supported by current results**, and attribution solely to constant is unwarranted.
3. **2020 month omission** — Deck ~line 459 says January–February inside, March–May below interval. `05`, `fc_outlook_2020.csv` also shows **June** actual 46.695 below lower 48.702, and June is a full observed month. Include June or explain why excluded. Related plotted title “Jan–May full months” is inaccurate.
4. **Calibration is presented as improvement while interval quality worsens** — `05`, `fc_calibration_2019.csv`: raw 90.4% to calibrated 96.2% coverage, but average interval width **125.08→178.66** (+42.8%) and mean Winkler score **174.88→192.72** (+10.2%; lower is better). Code correct for coverage but the evidence does not show uniformly *better* predictive intervals.
5. **Title/model-class mismatch** — `08` calls the selected model Fourier+ARMA. `02_src_code.md`, `TREND_SPECS['rw']`, specifies **ARIMA(p,1,q) errors** for selected 2017 and 2019 folds. More accurate: Fourier regression with ARIMA errors, or DHR with candidate ARMA/ARIMA error structures.
6. **Unverifiable ‘predetermined’ claim** — `08` ~line 54 and deck ~line403 claim the headline rule was decided before test years were inspected. The prior project material already included 2019 results and iterative model development. Current code can be internally chronological while the **research process** reuses 2019 as a model development reference. Do not describe 2019 as a pristine untouched prospective holdout.
7. **Numerical statements otherwise agree** — headline MAEs, 2017–2019 interval miss counts, calibration coverage, bootstrapped loss differences, weekly ΔR² and p=.51, one-week MAE improvements *as tabulated*, forecast-day shares *as tabulated*, station-change percentages *as tabulated*, IRF and FEVD summaries *as tabulated*, and lockdown gap arithmetic match to published rounding. This is a comparison of the provided LaTeX and `05` tables, **not** a check of actual `numbers.tex` macro contents; the macro file was not included.

## IV. Confirmed code defects and verification blind spots

**P0: Recursive LSTM feature alignment** — `02_src_code.md`, `src/forecast.py`, line ~456: `cc = np.vstack([Cp, Cf[:j + 1]])[-lag:] if j else Cp` but input anomaly history `hist[-lag:]` stops at previous week. For j≥1, `cc` contains next/current week's calendar vector, one step ahead of the corresponding anomaly input. Correct to `Cf[:j]` and rerun LSTM baseline. The existing backtest MAE computed from *saved predictions* is correct, but the training/forecast implementation is wrong; do not draw general conclusions about LSTM performance from uncorrected runs. Independent refit of the code on rounded weekly data was unstable/did not reproduce stored LSTM metrics (especially 2018 and 2019), so include a complete locked environment and raw unrounded inputs for reproducibility.

**P0: Independent verifier off by one month** — `07_verification_and_figure_code.md`, `verify_numbers.py`, ~line 327: `for i_,m_ in zip((3,4,5), ['Mar','Apr','May'])` then selects `a20_.index.month==i_+1`. This checks April, May, June observed concentrations against March, April, May intervals. Fix to `index.month==i_`. A PASS from this code cannot validate the intended claim.

**P1: Persistence checker drops first week** — `07`, ~line 314: `.iloc[1:]` is applied to both actual and previous-week reference even though previous-week observations are available. It skips one complete test week. The computed persistence MAE changes, but generous tolerance currently masks the error. Check every available weekly forecast and eliminate the tolerance masking.

**P1: Non-converged model selection** — `02`, `_best_by_aicc` ~line 340 accepts any finite AICc without testing optimizer convergence. Global warning suppression hides warnings. Check `res.mle_retvals['converged']`, covariance warnings and invalid seasonal/invertibility parameters and document excluded candidates.

**P1: Incoherent daily simulations vs weekly forecasts** — `02`, `daily_band_days` ~lines 583–619 constructs daily exceedance counts from separately sampled patterns, while monthly PM2.5 means are generated from a separate weekly trajectory (`monthly_mean_paths`). Their daily profiles are not constrained to exactly reproduce that same simulation's weekly means. A single coherent daily-to-weekly simulation should produce both monthly mean and counts. The 2019 daily band validation needs raw daily data/simulation paths to independently verify.

**P1: 'Independent' verification is not comprehensive** — `07`, `verify_numbers.py` depends on original raw CPCB/ERA5, processed files, station files, and generated macro files not provided in this bundle; therefore its 65/65 claim cannot be independently rerun from this upload alone. Some checks compare saved result tables or selected model specifications rather than recomputing model selection or full uncertainty procedure. It does not fully certify weather one-step, LSTM refits, station panel, outlook simulation or every report/deck number.

**P1: Block bootstrap effective sample size** — `02`, `block_bootstrap_diff` resamples concatenated weekly loss differences across yearly origin boundaries, assuming weak stationarity. The 104 2018+19 weekly errors represent only two highly dependent forecast paths. Its percentiles reproduce as coded, but inferential significance is fragile.

**P2: Horizon/calendar naming** — A 52-step weekly forecast from 2016-12-25 ends 2017-12-24, not on 2017-12-31. This is legitimate for a fixed 52-week horizon but should not be confused with a full calendar-year forecast. `week_index` caps week 53 at 52; the baseline still matched observed stored forecasts here. Annual calendar reporting must address 53-week years explicitly. Full 2019/2020 monthly outlooks use 53 projected weeks to cover all days, which is the appropriate distinct design.

**Leakage conclusion**: Model selection in `select_dhr` and seasonal calibration uses data restricted to each backtest origin according to the supplied code. The apparent “same-week ERA5” model is explicitly marked oracle and is not used for operational forecasts. I found **no certain direct look-ahead in the main 52-week selected-model backtest**; the serious issues are (a) test-year reuse during iterative model development, (b) LSTM time-feature misalignment, and (c) uncertainty/verification design. Do not call every retrospective climatology or contemporaneous weather analysis “leakage”.

## V. Interpretative overclaims

- **“Weather adds nothing”** is stronger than a non-significant p=.515 and modest test-set accuracy changes. Better: no convincing *additional predictive benefit detected* in tested weekly specifications. In-sample Granger predictability does not establish physical causal ‘driving’.
- **“Fourier+ARMA beats climatology”** only weakly: MAE 2018–19 average selected 24.56 vs climatology 24.80; block CI includes zero. The 2017 fold slightly favors climatology. The linear trend variant is apparently stronger on 2018–19, but selecting it after reviewing test results would require new evaluation.
- **“Calibration works”** because 2019 coverage 96% omits the increase in interval width and worsening Winkler score; 2017 coverage is just 69%. No reliability guarantee over future years from three forecast origins.
- **“Lockdown cut PM2.5 by 43%”** is an unjustified causal statement. This is a comparison to a projected counterfactual (median 85.14 vs observed 48.67). Forecast model was already high by ~8.5% relative to observed January–March pre-lockdown weeks, using available weekly 2020 records. The 10 Sunday weeks cover 23 Mar–31 May, including 23–24 Mar before 25 Mar lockdown. Weather adjustment does not resolve all competing confounders. Write “observed mean was approximately 43% below the model’s no-lockdown median projection over the 10 selected weeks.”
- **“Most monitoring decline is real”** is not proven by a six-station fixed panel with differing year coverage; raw station file absent and weather covariates do not establish emissions causality.
- **“LSTM clearly worse”** as a conclusion about a fairly evaluated baseline must wait for its recursive alignment fix and a reproducible rerun. It is not evidence that deep learning generally underperforms.
- **“Monthly risk bands”** refer to PM2.5 sub-indices rather than full CPCB AQI, an appropriate distinction the revised report largely makes. Daily category probabilities derived from weekly means need a single coherent daily simulation and daily data for checking.

## VI. Priority fixes

1. Fix LSTM time-feature alignment, rerun all LSTM folds and store full-precision reproducibility inputs, seeds, PyTorch/version and outputs.
2. Fix verifier’s month off-by-one and persistence skipped-week bugs; add true raw-output recomputation checks for all 15 ledger items, including one-week forecasts, station panel and simulated monthly outlook.
3. Remove/correct report's winter-humidity p cutoff and unsubstantiated D0 validation “39.7→30.6” assertion; amend June 2020 omission.
4. Show coverage, interval width **and Winkler score** together; avoid calling wider intervals uniformly “calibrated improvement.”
5. Rebuild coherent daily trajectories whose weekly means match forecast draws; validate monthly risk-band counts from the actual historical daily series.
6. Change causal lockdown language to explicit model-based counterfactual and clearly state 10 selected weeks begin 23 March.
7. Temper significance and model-selection claims given only two main 52-step origins and reuse of the 2019 holdout; accurately label integrated DHR errors.

Source: files 00–09 uploaded for this audit. Calculated supporting CSV: `audit_recomputed_metrics.csv`.

### Gemini
# Gemini verification audit (round 2), condensed transcription

Source: pasted by the user from Gemini's reply to `verification_pack/`. Numeric tables omitted where they only confirm values already in `results/`.

**Claimed run results (not reproducible from the pack: raw CPCB/ERA5/station files were not included, so these cannot have come from the supplied files alone):** verify_numbers.py 63/65 (the two failures were live link checks); make_figures.py exit 0.

**Reproduced from the raw pack (all matched):** backtest MAEs (all models, 3 folds), climatology and seasonal naive, interval coverage and miss counts (2017 69.2% 10 below/6 above; 2018 94.2% 2/1; 2019 90.4% 5/0; calibrated 96.2%), bootstrap loss differences, one-week MAE changes, HAC Granger p-values, weekly nested test (R2 0.1341 to 0.1391, p = 0.5146), 2019 pipeline validation, lockdown arithmetic (48.67 vs 85.14 = -42.8%; weather-adjusted -38.0%), station-decline arithmetic, Ljung-Box with/without burn-in, seasonal MA -0.988 SE 8.26, doy365.

**Mismatches / discrepancies reported:**
1. verify_numbers.py makes live curl calls; fails offline.
2. Some macros rounded to integers (MAE 54, LSTM 53, D0 44; lockdown bounds).
3. Ledger said lockdown "25 Mar - 31 May"; the series uses 10 Sunday-ending weeks 29 Mar - 31 May.
4. Report Section 5.3 omits that lag 10 is only marginal (p = 0.088).

**Code findings:**
- linreg and lstm return a constant predictive sd across horizons (LSTM: one-step residual sd, hence 0% coverage in 2018).
- block_bootstrap_diff concatenates folds, blocks straddle the year boundary.
- Calibration step rule (|mean z| > 0.5 in both folds) did not re-centre in 2019 (z = -0.66, -0.45; actual 2019 -0.53).
- RMSE uses the lognormal mean for models with sd but the median for those without.

**Over-claims:** "matches or slightly beats climatology" (CI spans 0); lockdown 43% confounded with model level bias (model already high in 2019); LSTM comparison is a strawman; "drive/explain" language for Granger results.

**Prioritised fixes:** make verifier sandbox-safe; reword abstract; smooth the calibration rule; horizon-dependent sd for linreg/LSTM; sensitivity bounds for the lockdown gap (constant and random-walk level).
