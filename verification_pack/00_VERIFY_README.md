# 00 Verification pack (round 3, final check): how to re-check everything
Project: Delhi PM2.5 time-series study (MATH F428), branch `phase4-final`. Two earlier audits (Gemini, GPT) recomputed the numbers and found real bugs; those were fixed and everything was re-run. **Your job now: check that the fixes are correct, that nothing new broke, and that every statement is supported.**

## What to do
1. Recompute the claims below from the raw data in files 05 and 06. Report every mismatch.
2. Read the code (file 01, notebooks 02-03; 03 for notebook 04, 07 for the checker) for leakage, alignment errors, wrong formulas. Pay special attention to the fixes: `lstm_window` and `_lstm_recursive`, `daily_paths`, `block_bootstrap_diff` (circular, per fold), `linreg` sd, `_best_by_aicc`, `week_offsets_by_month`.
3. Compare every number in the report/deck text (file 08) with the tables (file 04).
4. Decide which conclusions are still over-claims. Do not just agree; give file and number.

## Files (10)
| File | Content |
|---|---|
| 00_VERIFY_README.md | this file, instructions, claims ledger |
| 01_src_code.md | full source of src/ |
| 02_notebooks_02_03_code.md | EDA and VAR/Granger notebooks: code plus printed output |
| 03_notebook_04_code.md | forecasting notebook: code plus printed output |
| 04_all_results_tables.md | every results/*.csv except raw forecasts, and the key_numbers json |
| 05_raw_forecasts_and_weekly.md | weekly table (full precision, 287 rows), raw 52-week backtest forecasts, one-step forecasts, 2020 weekly forecasts |
| 06_daily_data_and_stations.md | the full daily table (PM2.5 and weather) and per-station-per-year PM2.5 summary |
| 07_checker_and_figure_code.md | verify_numbers.py (78 checks), make_figures.py, slide number macros |
| 08_report_and_deck_text.md | LaTeX source of the report and the deck |
| 09_changes_and_review_log.md | git history, source diffs, review log with Round 2 |

## Setup facts
Weekly W-SUN series, 287 weeks 2015-01-04 to 2020-06-28 (log of weekly mean PM2.5). Origins 2016-12-25, 2017-12-31, 2018-12-30, each forecasting 52 weeks (the 2017 fold ends 24 Dec 2017). Point forecast = exp(mu) (median); mean = exp(mu + sd^2/2). Authors' checker: 78/78 passed (a claim to test, not proof). Raw CPCB/ERA5 files are not included; the daily table in file 06 is the processed series.

## Output format
(i) numbers you reproduced with your values, (ii) mismatches, (iii) code bugs, (iv) over-claims, (v) prioritised fixes.

## Claims ledger (round 2: statements as they now stand)
| # | Claim | Evidence file | Recompute from |
|---|---|---|---|
| 1 | MAE 2017/18/19: selected Fourier+ARMA 31.5/23.4/25.7; climatology 31.0/21.8/27.8; SARIMA D=1 53.8/21.1/27.5; SARIMA D=0 44.9/42.8/44.1; LSTM 36.3/28.3/54.3 (rerun after the alignment fix); linear regression 35.9/20.0/24.9 | 04 fc_backtest_mae.csv | 05 backtest forecasts: mean abs(actual - exp(mu)) |
| 2 | Climatology = mean log PM2.5 by week index 1-52 over training years; seasonal naive = value 52 weeks earlier | 01 forecast.py | 05 weekly table |
| 3 | No model is significantly better than climatology (circular moving-block bootstrap, 8-week blocks, drawn within each fold): 2018-19 selected -0.2 [-2.9,+2.8], linear -2.9 [-6.1,+0.7]; seasonal naive, SARIMA D=0, LSTM worse; SARIMA D=1 worse over all three folds | 04 fc_loss_diff.csv | resample per-fold absolute-error differences |
| 4 | 2019 raw 95% coverage 90.4% (5 misses, all below), 2018 94.2% (2 below, 1 above), 2017 69.2% (10 below, 6 above) | 04 fc_backtest_metrics.csv | 05: share of actual in [exp(mu-1.96 sd), exp(mu+1.96 sd)] |
| 5 | Season rescaling (2017-18 errors): 2019 coverage 96.2% but width 125 -> 179 and Winkler 175 -> 193 (worse) | 04 fc_calibration_2019.csv | 05 + scale factors 1.334 (winter) / 1.422 |
| 6 | One-week MAE vs no-weather DHR: lagged -2.4%, last-3-days +0.7%, same-week oracle +6.9% (p 0.075/0.585/0.074) | 04 fc_oneweek.csv | 05 one-step forecasts (fc_oneweek_forecasts) |
| 7 | HAC Granger wind->PM2.5 p~6e-20, humidity ~4e-11 (4 lags, with rain+temp 9e-18, 7e-8); seasonal tests all p<1e-3; interactions p=0.20 (monsoon x humidity), 0.03 (winter x wind) | 04 granger_*.csv | 06 daily data (anomalies from doy climatology) |
| 8 | Weekly nested test: R2 0.1341 -> 0.1391, p = 0.515 | 04 weekly_lag_nested.csv | 05 weekly table |
| 9 | 2019 pipeline validation: 12/12 monthly means inside 95%; Poor-or-worse 55.0% predicted vs 45.2% actual | 04 fc_outlook_validation_2019_*.csv | 06 daily data (actual band counts) |
| 10 | Lockdown: 10 Sunday-ending weeks 29 Mar-31 May (cover 23 Mar-31 May); actual mean 48.7 vs model median 85.5 = -43% (95% -52 to -32); weather-adjusted -38%; pre-lockdown (5 Jan-22 Mar) model gap -11%; adjusted = (1+gap)/(1+pre-gap)-1 = -36%; other level specs -51% to -37%; 2019 placebo -15% | 04 fc_lockdown*.csv | 05 lockdown weekly table (fc_weekly_2020) |
| 11 | June 2020 monthly mean 46.7 is below its lower bound 48.2; Jan-Feb inside; Mar-Jun below | 04 fc_outlook_2020.csv | 06 daily data |
| 12 | Station panel: city series 2016->2019 -25%, fixed 6-station panel -20%, weather-adjusted -18%; stations reporting 10, 8, 17, 37, 37 | 04 station_check.csv | 06 station summary (per station-year mean and days) |
| 13 | Ljung-Box on SARIMA D=1 residuals: p~0 with the 52 diffuse residuals; without them 0.49/0.10/0.016 (lags 10/26/52); seasonal MA -0.988, SE 8.26 | 03 nb04 output | needs full-precision refit |
| 14 | SARIMA D=0 with/without constant (same orders/folds): 44.9/42.8/44.1 vs 76.9/61.0/92.1 | 04 fc_sarima_d0_constant.csv | refit |
| 15 | doy365 maps 29 Feb to day 59 and shifts later leap-year days by -1 | 01 tsa.py | read code |

Note: all numbers in this ledger are generated from results/ at build time.

## What the first-round audits already found and what was fixed (verify the fixes!)
LSTM calendar/anomaly misalignment (now one helper `lstm_window`, deterministic torch); verifier checked April-June against March-May intervals and skipped a persistence week; non-converged fits accepted in AICc search; daily band days and monthly means from different draws (now one set of daily paths whose weekly means equal the weekly paths exactly); bootstrap joined forecast years (and a first fix without wrap-around biased the interval: now circular within each fold); constant predictive sd for linear regression/LSTM (now horizon-specific); report claims (winter humidity bound, D=0 '39.7 to 30.6', June omission, over-claims). See file 09 (Round 2 table R1-R23).
