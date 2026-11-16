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
