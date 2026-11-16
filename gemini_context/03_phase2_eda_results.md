# 03 Phase 2: EDA and stationarity (notebook 02), method and all numbers

## Steps
1. **Time plot vs CPCB bands.** 52.2% of days are Poor or worse (PM2.5 > 90). Max daily value above 450 not shown.
2. **Seasonality.** Winter (Nov-Jan) mean 213.3 vs monsoon (Jul-Sep) 48.1 => 4.43x. November median / August median = 4.9x.
```
       Unnamed: 0  pm25 pm25.1 wind wind.1   rh   rh.1
              NaN  mean median mean median mean median
           season   NaN    NaN  NaN    NaN  NaN    NaN
Monsoon (Jul–Sep)  48.1   46.0  9.0    8.4 78.0   80.0
     Other months 102.5   93.9  9.9    9.3 52.2   53.0
 Winter (Nov–Jan) 213.3  201.4  8.6    8.1 68.6   69.0
```

3. **STL** on weekly log PM2.5, period 52, robust=True. Seasonal strength F_S = 1 - Var(R)/Var(S+R) = **0.89**; trend strength 0.34. NOTE: STL is run on the FULL weekly sample incl. 2019 and the 2020 lockdown half-year.
4. **Correlations** (Spearman, daily, pooled): PM2.5 vs wind -0.24, vs humidity -0.20. Within season:
```
           season  ρ(PM2.5, wind)  ρ(PM2.5, RH)  days
Monsoon (Jul–Sep)           -0.39         -0.37   461
     Other months            -0.3         -0.02  1057
 Winter (Nov–Jan)           -0.47         -0.02   491
```

   Interpretation by the team: wind negative in every season; humidity negative only in monsoon (rain washout), about 0 in winter and other months.
5. **ACF/PACF (daily log PM2.5):** slow decay, negative at ~6 months, positive bump near lag 365; PACF cuts after a few lags (AR(1-2)-like).
6. **Stationarity tests, full sample** (ADF H0 unit root; KPSS H0 level-stationary; KPSS p capped at [0.01,0.1]):
```
                           series    n  adf_stat    adf_p  adf_lags  adf_crit_1%  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p                                   verdict
                Daily PM2.5 (raw) 2009     -3.98  0.00152        17       -3.434       -2.863        -2.568      0.224     0.1                                Stationary
                  Daily log PM2.5 2009    -3.089   0.0274        18       -3.434       -2.863        -2.568      0.366  0.0917                                Stationary
                Daily Δ log PM2.5 2008    -15.23 5.35e-28        17       -3.434       -2.863        -2.568      0.031     0.1                                Stationary
                 Daily wind speed 2009    -13.14 1.42e-24         6       -3.434       -2.863        -2.568       0.54  0.0326 Mixed (ADF says stationary, KPSS rejects)
               Daily Δ wind speed 2008    -15.19 6.11e-28        26       -3.434       -2.863        -2.568      0.141     0.1                                Stationary
              Daily rel. humidity 2009    -4.521  0.00018         9       -3.434       -2.863        -2.568      0.052     0.1                                Stationary
            Daily Δ rel. humidity 2008    -20.68        0         8       -3.434       -2.863        -2.568      0.015     0.1                                Stationary
                 Weekly log PM2.5  287    -5.389 3.57e-06         9       -3.454       -2.872        -2.572      0.158     0.1                                Stationary
         Weekly Δ log PM2.5 (d=1)  286    -9.743 8.42e-17         2       -3.454       -2.872        -2.572      0.027     0.1                                Stationary
       Weekly Δ₅₂ log PM2.5 (D=1)  235    -5.852 3.57e-07         2       -3.459       -2.874        -2.573      0.669  0.0163 Mixed (ADF says stationary, KPSS rejects)
Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1)  234    -9.235 1.64e-15         6       -3.459       -2.874        -2.574      0.049     0.1                                Stationary
```

7. **Stationarity, training weeks only (2015-2018)** with lag-1 ACF (over-differencing guard):
```
                           series   n  adf_stat    adf_p  adf_lags  adf_crit_1%  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p    verdict  lag1_acf
         Weekly log PM2.5 (train) 209     -4.28  0.00048         9       -3.464       -2.876        -2.575      0.058     0.1 Stationary      0.87
         Weekly Δ log PM2.5 (d=1) 208    -5.364 4.02e-06         5       -3.463       -2.876        -2.574      0.082     0.1 Stationary     -0.28
       Weekly Δ₅₂ log PM2.5 (D=1) 157    -4.534 0.000171         2       -3.474        -2.88        -2.577      0.341     0.1 Stationary      0.29
Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1) 156    -7.298 1.36e-10         5       -3.475       -2.881        -2.577      0.075     0.1 Stationary     -0.46
```

   Decision: d = 0. The extra first difference gives lag-1 ACF -0.46 (near -0.5 over-differencing warning). D in {0,1} deferred to a validation year.
8. **Why log?** Variance/volatility checks, raw vs log:
```
                                    Unnamed: 0  raw PM2.5  log PM2.5
0                                     Skewness      1.704   -0.07717
1               corr(monthly mean, monthly SD)     0.9512   -0.06664
2                         Max / min monthly SD      7.903      1.341
3      Levene F (equal variance across months)      49.63      2.399
4                               Levene p-value  9.551e-97   0.005908
5  ARCH-LM statistic (7 lags, on daily change)      235.2      36.43
6                              ARCH-LM p-value  3.925e-47  6.002e-06
```

   Monthly mean and SD:
```
 Date  mean  sd_raw  sd_log
    1 197.5   69.88  0.3733
    2   142   53.07  0.3524
    3 87.57   31.71  0.3963
    4 90.93   36.49  0.4483
    5 92.21    40.2  0.4382
    6 69.81   32.45  0.4091
    7 46.42   18.67  0.4063
    8 42.86   14.59  0.3833
    9 55.34   22.75  0.4517
   10 140.9   69.17  0.4584
   11 238.2   115.3  0.4724
   12 208.1   69.61  0.3579
```

   Box-Cox lambda: 0.045 (daily), 0.028 (weekly) => close to 0 = log. ARCH-LM on the daily change: 235 -> 36 (still significant, p=6e-6); Levene p 1e-97 -> 0.006 (still rejects). Team's plan: re-check residuals of the final model.

## Key numbers JSON (results/key_numbers_eda.json)
```
{
  "pct_days_poor_or_worse": 52.2,
  "winter_mean_pm25": 213.3,
  "monsoon_mean_pm25": 48.1,
  "winter_to_monsoon_ratio": 4.43,
  "nov_to_aug_median_ratio": 4.9,
  "seasonal_strength": 0.89,
  "trend_strength": 0.34,
  "spearman_pm25_wind": -0.24,
  "spearman_pm25_rh": -0.2,
  "boxcox_lambda_daily": 0.045,
  "boxcox_lambda_weekly": 0.028
}
```

## Team's physical interpretation (not tested here)
Winds are only modestly calmer in Oct-Dec (~8 vs ~10 km/h in Mar-Jun) in ERA5; the rest of the winter peak is attributed to unmeasured mixing-layer depth / inversions, stubble burning, heating, fireworks. Monsoon is humid and cleanest (wet deposition).
