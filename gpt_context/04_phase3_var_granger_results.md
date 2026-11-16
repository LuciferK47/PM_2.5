# 04 Phase 3: VAR, Granger causality, IRF, FEVD (notebook 03), method and all numbers

## Setup
- Daily data 2015-01-01 to 2019-12-31 (1,826 days). 2020 excluded (lockdown).
- Variables: wind, rh, log PM2.5, each **deseasonalised** by subtracting its smoothed day-of-year climatology (31-day circular window, climatology estimated on the same 2015-2019 sample). Rationale: otherwise Granger detects "it is winter".
- Anomaly stationarity (note KPSS rejects for wind and PM2.5 anomaly, because of slow drift, e.g. the 2019 PM2.5 decline; ADF rejects unit root for all three):
```
          series    n  adf_stat    adf_p  adf_lags  adf_crit_1%  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p                                   verdict
    Wind anomaly 1826    -19.57        0         3       -3.434       -2.863        -2.568       1.05    0.01 Mixed (ADF says stationary, KPSS rejects)
Humidity anomaly 1826    -12.61  1.7e-23         3       -3.434       -2.863        -2.568      0.225     0.1                                Stationary
   PM2.5 anomaly 1826    -6.601 6.73e-09        18       -3.434       -2.863        -2.568      2.033    0.01 Mixed (ADF says stationary, KPSS rejects)
```

- Lag order: AIC picks 4, BIC 2, HQIC 3. VAR(4) used (stable, max eigenvalue modulus 0.811; Portmanteau whiteness p = 0.173 using nlags = p+10).
```
 lag   aic   bic  hqic   fpe
   0 4.477 4.486 4.481    88
   1 2.564 2.601 2.578 12.99
   2 2.442 2.506 2.466  11.5
   3 2.432 2.523 2.465 11.38
   4 2.426 2.544  2.47 11.31
   5 2.432 2.578 2.486 11.38
   6  2.43 2.603 2.494 11.36
   7 2.436 2.636  2.51 11.43
   8 2.434 2.662 2.518  11.4
   9  2.44 2.695 2.534 11.48
  10 2.441 2.724 2.546 11.49
  11 2.449 2.758 2.563 11.57
  12 2.456 2.793 2.581 11.66
  13 2.461 2.825 2.595 11.71
  14 2.466 2.858 2.611 11.78
```


## Granger causality (F-test from the VAR(4), anomalies)
```
             spec               direction     F        df   p_value   verdict (5%)
Anomalies, VAR(4)            Wind → PM2.5  35.7 (4, 5427) 1.734e-29 Granger-causes
Anomalies, VAR(4)        Humidity → PM2.5 14.38 (4, 5427) 1.107e-11 Granger-causes
Anomalies, VAR(4) Wind + Humidity → PM2.5 21.89 (8, 5427) 3.983e-33 Granger-causes
Anomalies, VAR(4)            PM2.5 → Wind   1.8 (4, 5427)    0.1268    No evidence
Anomalies, VAR(4)        PM2.5 → Humidity  0.67 (4, 5427)    0.6145    No evidence
```

Robustness (BIC lag 2, first differences with VAR(14) by AIC):
```
                            spec               direction     F         df   p_value   verdict (5%)
         Anomalies, VAR(4) [AIC]            Wind → PM2.5  35.7  (4, 5427) 1.734e-29 Granger-causes
         Anomalies, VAR(4) [AIC]        Humidity → PM2.5 14.38  (4, 5427) 1.107e-11 Granger-causes
         Anomalies, VAR(4) [AIC] Wind + Humidity → PM2.5 21.89  (8, 5427) 3.983e-33 Granger-causes
         Anomalies, VAR(4) [AIC]            PM2.5 → Wind   1.8  (4, 5427)    0.1268    No evidence
         Anomalies, VAR(4) [AIC]        PM2.5 → Humidity  0.67  (4, 5427)    0.6145    No evidence
         Anomalies, VAR(2) [BIC]            Wind → PM2.5 72.87  (2, 5451) 5.848e-32 Granger-causes
         Anomalies, VAR(2) [BIC]        Humidity → PM2.5 28.56  (2, 5451) 4.578e-13 Granger-causes
         Anomalies, VAR(2) [BIC] Wind + Humidity → PM2.5 44.65  (4, 5451) 6.086e-37 Granger-causes
         Anomalies, VAR(2) [BIC]            PM2.5 → Wind   4.1  (2, 5451)   0.01657 Granger-causes
         Anomalies, VAR(2) [BIC]        PM2.5 → Humidity  0.52  (2, 5451)    0.5929    No evidence
First differences, VAR(14) [AIC]            Wind → PM2.5 10.84 (14, 5304) 7.847e-25 Granger-causes
First differences, VAR(14) [AIC]        Humidity → PM2.5  5.47 (14, 5304)  1.47e-10 Granger-causes
First differences, VAR(14) [AIC] Wind + Humidity → PM2.5  7.23 (28, 5304) 1.014e-27 Granger-causes
First differences, VAR(14) [AIC]            PM2.5 → Wind  0.89 (14, 5304)    0.5686    No evidence
First differences, VAR(14) [AIC]        PM2.5 → Humidity  1.19 (14, 5304)     0.276    No evidence
```

Pairwise bivariate SSR F-tests by lag 1-7 (no controls):
```
      Unnamed: 0         1         2         3         4         5         6         7
    Wind → PM2.5 3.348e-08  1.57e-25 9.439e-24  4.87e-23  3.06e-22 1.215e-21 7.652e-21
Humidity → PM2.5 6.339e-06 2.795e-07 1.468e-06 5.451e-06 1.544e-05  3.85e-06 6.804e-06
    PM2.5 → Wind 0.0009714 0.0004747  0.004117   0.01432   0.03751   0.05918   0.08459
PM2.5 → Humidity    0.2354    0.5658    0.5739    0.6506    0.5535    0.5193    0.6188
```

**HAC (Newey-West, maxlags=10) Wald tests**, manual OLS equation-by-equation with 4 lags of each variable (target equation), plus rain control:
```
                 spec        direction  wald_chi2   p_value
PM2.5, wind, humidity     Wind → PM2.5       95.6 8.378e-20
PM2.5, wind, humidity Humidity → PM2.5       55.2 2.936e-11
       + rain control     Wind → PM2.5       92.4 4.165e-19
       + rain control Humidity → PM2.5       40.9 2.792e-08
       + rain control     Rain → PM2.5        1.3    0.8559
PM2.5, wind, humidity     PM2.5 → Wind        7.8    0.1012
PM2.5, wind, humidity PM2.5 → Humidity        3.1    0.5468
```

Reading: weather -> PM2.5 overwhelming (p < 1e-10) in every specification; PM2.5 -> humidity never; PM2.5 -> wind borderline only at BIC lag 2 (p=0.017) and pairwise lags 1-4. Humidity survives a rain control; rain itself adds nothing (p=0.86).

## Impulse responses (orthogonalised, Cholesky; response of log PM2.5 converted to % via exp(x)-1)
Shock size = 1 SD of the VAR residual: wind 2.54 km/h, humidity 5.43 %RH.
```
                      ordering    shock  day0_pct  day1_pct  day2_pct  day3_pct  day5_pct
weather first (wind, rh, pm25)     Wind      -9.2     -11.9      -4.6      -1.9      -0.3
weather first (wind, rh, pm25) Humidity      -4.5      -6.8      -5.7        -4      -1.4
  PM2.5 first (pm25, wind, rh)     Wind         0      -5.9      -1.1       0.9         1
  PM2.5 first (pm25, wind, rh) Humidity         0        -4      -4.1      -2.8      -0.8
```

Weather-first ordering allows same-day (contemporaneous) weather -> PM2.5; PM2.5-first allows only lagged effects. The team reports the range: wind day-1 effect -6% to -12%, humidity -4% to -7%, fading within ~5-7 days.

## FEVD of PM2.5 (share of forecast-error variance, %)
Default ordering (wind, rh, pm25), by horizon:
```
 horizon (days)  Wind  Humidity  PM2.5
              1  13.2         3   83.7
              2  22.5       6.2   71.4
              3  22.1       8.3   69.6
              4  21.2       9.2   69.6
              5  20.9       9.2   69.9
              6  20.7       9.3     70
              7  20.6       9.4   70.1
              8  20.5       9.5   70.1
              9  20.5       9.5   70.1
             10  20.4       9.5   70.1
             11  20.4       9.5   70.1
             12  20.4       9.5   70.1
             13  20.4       9.5   70.1
             14  20.4       9.5   70.1
```

Both orderings:
```
                      ordering variable  share_h1_pct  share_h14_pct
weather first (wind, rh, pm25)     Wind          13.2           20.4
weather first (wind, rh, pm25) Humidity             3            9.5
weather first (wind, rh, pm25)    PM2.5          83.7           70.1
  PM2.5 first (pm25, wind, rh)    PM2.5           100           93.6
  PM2.5 first (pm25, wind, rh)     Wind             0              3
  PM2.5 first (pm25, wind, rh) Humidity             0            3.3
```

Weather share at h=14: 29.9% (weather first) vs 6.3% (PM2.5 first: 3.0 + 3.3).

## "Shock" illustration (results/shock_binned.json)
VAR residual for wind on 2019-01-21: actual 14.8 km/h, VAR-predicted 7.42, shock +7.37. Days grouped by standardised shock size (z) and the mean PM2.5 deviation in %:
```
{
 "curves": {
  "wind": {
   "z": [
    -1.78,
    -1.05,
    -0.51,
    -0.01,
    0.5,
    1.08,
    2.26
   ],
   "pct": [
    32.0,
    14.4,
    5.9,
    -1.9,
    -6.0,
    -10.9,
    -23.7
   ],
   "n": [
    82,
    318,
    398,
    388,
    264,
    242,
    129
   ]
  },
  "rh": {
   "z": [
    -2.0,
    -1.05,
    -0.49,
    -0.01,
    0.49,
    1.03,
    2.22
   ],
   "pct": [
    -1.4,
    1.4,
    5.6,
    4.6,
    2.5,
    -7.8,
    -21.3
   ],
   "n": [
    96,
    276,
    358,
    422,
    325,
    221,
    123
   ]
  }
 },
 "jan21_shock_kmh": 7.375528187562479,
 "jan21_wind": 14.8,
 "jan21_pred": 7.424471812437521
}
```

Reading by the team: unexpectedly windier day -> PM2.5 ~24% lower (z=+2.26), calmer day (z=-1.78) -> ~32% higher. Note the humidity curve is NON-monotonic (+5.6% at z=-0.5, -21% at z=+2.2).

## Weekly-scale check (does weather help beyond a week?)
Weekly anomalies (week-of-year mean from 2015-2018), regression of this week's PM2.5 anomaly on last week's values, HAC errors:
```
               model                 term    coef  p_value  r2_model
   same-week weather                 wind -0.0402   0.0013    0.1403
   same-week weather             humidity -0.0105        0    0.1403
last-week predictors    PM2.5 (last week)  0.3621        0    0.1391
last-week predictors     wind (last week)  0.0066   0.4576    0.1391
last-week predictors humidity (last week) -0.0013   0.4799    0.1391
```

Last week's wind (p=0.46) and humidity (p=0.48) add nothing (R2 0.139 vs same-week model 0.140). This is the basis for dropping weather from the 12-month model.

## Key numbers JSON (results/key_numbers_var.json)
```
{
  "var_sample": "2015-01-01 to 2019-12-31 (1826 days)",
  "var_lag_aic": 4,
  "var_lag_bic": 2,
  "var_stable": true,
  "portmanteau_p": 0.173,
  "max_eigen_modulus": 0.811,
  "irf": {
    "wind": {
      "peak_pct": -11.9,
      "peak_day": 1,
      "shock_sd": 2.54,
      "unit": "km/h"
    },
    "rh": {
      "peak_pct": -6.8,
      "peak_day": 1,
      "shock_sd": 5.43,
      "unit": "% RH"
    }
  },
  "fevd_weather_share_h14": 29.9,
  "fevd_wind_h14": 20.4,
  "fevd_rh_h14": 9.5,
  "granger": {
    "Wind → PM2.5": 1.73e-29,
    "Humidity → PM2.5": 1.11e-11,
    "Wind + Humidity → PM2.5": 3.98e-33,
    "PM2.5 → Wind": 0.127,
    "PM2.5 → Humidity": 0.615
  },
  "granger_hac": {
    "Wind → PM2.5 | PM2.5, wind, humidity": 8.38e-20,
    "Humidity → PM2.5 | PM2.5, wind, humidity": 2.94e-11,
    "Wind → PM2.5 | + rain control": 4.17e-19,
    "Humidity → PM2.5 | + rain control": 2.79e-08,
    "Rain → PM2.5 | + rain control": 0.856,
    "PM2.5 → Wind | PM2.5, wind, humidity": 0.101,
    "PM2.5 → Humidity | PM2.5, wind, humidity": 0.547
  }
}
```

