# 01 Claims ledger (what the deck/report states, and how to check it)
Check each row. 'Source' tells you which file holds the evidence; 'Recompute' says how.

| # | Claim | Source | Recompute |
|---|---|---|---|
| 1 | Backtest MAE 2017/18/19: selected Fourier+ARMA 31.5/23.4/25.7; climatology 31.0/21.8/27.8; SARIMA D=1 53.8/21.1/27.5; SARIMA D=0 about 44; LSTM 36/49/53 | 05 (fc_backtest_mae.csv) | file 06 raw forecasts: mean |actual - exp(mu)| per fold and model |
| 2 | Climatology = mean of log PM2.5 by week index (1-52) over training years, forecast exp(mean) | 02 (forecast.py climatology) | file 06 weekly table |
| 3 | Seasonal naive = same week of the previous year | 02 | file 06 |
| 4 | Selected model not significantly better than climatology (block-bootstrap CI covers 0) | 05 (fc_loss_diff.csv) | resample loss differences, blocks of 8 weeks |
| 5 | 2019 95% interval coverage 90% raw, 96% after seasonal rescaling | 05 (fc_calibration_2019.csv) | share of actuals in [exp(mu-1.96 sd), exp(mu+1.96 sd)] (file 06) |
| 6 | Selected model raw 95% intervals, 2019: 5 misses, all below the lower bound; 2018: 2 below, 1 above; 2017 (stress test): 10 below, 6 above, coverage 69% | 05, 06 | count actual < lower vs > upper per fold (authors' recount: coverage 0.69/0.94/0.90) |
| 7 | One-week-ahead MAE change vs no-weather model: lagged weather -2.4%, last-3-days +0.7%, oracle same-week +6.9% (HLN-DM p about 0.07) | 05 (fc_oneweek.csv) | see 04 notebook cell for the one-step design |
| 8 | Wind/humidity Granger-cause PM2.5 for about a week, robust to rain, temperature, trend, training-only climatology | 05 (granger_*.csv) | 03 notebook; HAC Wald code in src |
| 9 | Weekly nested lag test adds nothing: delta R2 = 0.005, p = 0.51 | 05 (weekly_lag_nested.csv) | 03 notebook section 9 |
| 10 | 2019 pipeline test: 12/12 monthly means inside 95% interval; Poor-or-worse days 55% predicted vs 45% actual | 05 (fc_outlook_validation_2019_*.csv) | file 06 + 04 notebook |
| 11 | Lockdown (25 Mar - 31 May 2020): actual mean 48.7 is 43% below counterfactual median (95% -52% to -32%); weather-adjusted -38% | 05 (fc_lockdown.csv) | 1 - 48.7/median |
| 12 | PM2.5 decline 2016 to 2019: all stations -25%, fixed 6-station panel -20%, weather-adjusted -18% | 05 (station_check.csv) | 02 notebook section 8; needs data/raw/station_day.csv (not included) |
| 13 | Ljung-Box on SARIMA residuals is distorted by the 52 diffuse burn-in residuals; after removing them lags 10/26 pass, lag 52 p = 0.016 | 05 (fc_diagnostics.csv) | 04 notebook |
| 14 | Seasonal MA = -0.988 is unidentified (SE 8.26) | 04 notebook output | 04 notebook |
| 15 | Leap-year fix: day 366 mapped to 365 consistently | 02 (tsa.py doy365) | read code |

Key forecast numbers stored by the notebook:
```
{
 "sarima_D1_maS_coef": -0.988,
 "sarima_D1_maS_se": 8.259,
 "calibration_rule_2019": {
  "f": {
   "true": 1.3343095497324873,
   "false": 1.421532404826579
  },
  "shift": 0.0,
  "by_fold_mean_z": {
   "2017": -0.66,
   "2018": -0.45
  },
  "recentre": false
 },
 "coverage_2019_raw": 0.9038461538461539,
 "coverage_2019_calibrated": 0.9615384615384616,
 "oneweek_mae": {
  "Persistence": 30.69,
  "Climatology": 24.79,
  "Climatology + AR(1)": 23.22,
  "DHR, no weather": 22.39,
  "+ lagged weather (operational)": 22.92,
  "+ last 3 days of prior week (operational)": 22.24,
  "+ same-week weather (ORACLE)": 20.84
 },
 "oneweek_gain_pct": {
  "lagged": -2.4,
  "last3": 0.7,
  "oracle": 6.9
 },
 "validation_2019": {
  "months_actual_inside_95": 12,
  "annual_days_pred": {
   "Good": 21.0,
   "Satisfactory": 75.0,
   "Moderate": 67.0,
   "Poor": 53.0,
   "Very Poor": 113.0,
   "Severe": 35.0
  },
  "annual_days_actual": {
   "Good": 25,
   "Satisfactory": 97,
   "Moderate": 78,
   "Poor": 58,
   "Very Poor": 73,
   "Severe": 34
  },
  "mean_abs_days_error_per_band_month": 1.88,
  "poor_or_worse_pred_pct": 55.0,
  "poor_or_worse_actual_pct": 45.2
 },
 "outlook_2020_spec": {
  "trend": "linear",
  "K": 5,
  "p": 1,
  "q": 0
 },
 "outlook_2020_rule": {
  "f": {
   "true": 1.0935180465819772,
   "false": 0.9476619724449761
  },
  "shift": 0.0,
  "by_fold_mean_z": {
   "2018": -0.45,
   "2019": -0.53
  },
  "recentre": false
 },
 "lockdown": {
  "plain": {
   "actual_mean": 48.669714285714285,
   "cf_median": 85.140752539336,
   "gap_median_pct": -42.83617088073022,
   "gap_lo95_pct": -52.21475468260452,
   "gap_hi95_pct": -31.53328399642168
  },
  "weather_adjusted": {
   "cf_median": 78.46680894643731,
   "gap_median_pct": -37.97413844184731,
   "gap_lo95_pct": -47.76977454856694,
   "gap_hi95_pct": -26.19979951798827
  }
 },
 "backtest": {
  "mae_selected": {
   "2017": 31.48,
   "2018": 23.43,
   "2019": 25.69
  },
  "mae_climatology": {
   "2017": 31.0,
   "2018": 21.77,
   "2019": 27.82
  },
  "coverage_selected": {
   "2017": 0.692,
   "2018": 0.942,
   "2019": 0.904
  },
  "sarima_D1_mae": {
   "2017": 53.83,
   "2018": 21.08,
   "2019": 27.45
  },
  "sarima_D0_mae": {
   "2017": 44.87,
   "2018": 42.84,
   "2019": 44.1
  },
  "lstm_mae": {
   "2017": 36.29,
   "2018": 49.23,
   "2019": 52.87
  },
  "specs": {
   "2017": {
    "trend": "rw",
    "K": 5,
    "p": 1,
    "q": 1
   },
   "2018": {
    "trend": "const",
    "K": 5,
    "p": 1,
    "q": 1
   },
   "2019": {
    "trend": "rw",
    "K": 5,
    "p": 1,
    "q": 1
   }
  }
 },
 "diagnostics_selected_2019_fold": {
  "burn": 1.0,
  "n_resid": 208.0,
  "resid_sd": 0.2265,
  "LB_p_lag10": 0.0883,
  "LB_p_lag26": 0.001,
  "LB_p_lag52": 0.0092,
  "ARCH4_p": 0.8696,
  "JB_p": 0.0006
 }
}
```

