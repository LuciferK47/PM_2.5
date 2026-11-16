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
