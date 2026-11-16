# 04 Phase 3: VAR, Granger, IRF, FEVD (notebook 03)
VAR(4) on deseasonalised wind, humidity, log PM2.5 (2015-2019). Lag selection:
```
 lag   aic   bic  hqic   fpe
   0 4.484 4.493 4.487 88.59
   1 2.566 2.603  2.58 13.02
   2 2.444 2.508 2.468 11.52
   3 2.434 2.525 2.467  11.4
   4 2.428 2.546 2.471 11.33
   5 2.434 2.579 2.487  11.4
   6 2.432 2.605 2.496 11.38
   7 2.438 2.638 2.512 11.45
   8 2.436 2.663  2.52 11.42
   9 2.442 2.697 2.536  11.5
  10 2.443 2.725 2.547 11.51
  11  2.45  2.76 2.565 11.59
  12 2.458 2.795 2.582 11.68
  13 2.462 2.827 2.597 11.73
  14 2.468 2.859 2.612 11.79
```
Granger (VAR F-tests):
```
             spec               direction     F        df   p_value   verdict (5%)
Anomalies, VAR(4)            Wind → PM2.5 35.95 (4, 5427) 1.076e-29 Granger-causes
Anomalies, VAR(4)        Humidity → PM2.5 14.35 (4, 5427) 1.165e-11 Granger-causes
Anomalies, VAR(4) Wind + Humidity → PM2.5 21.99 (8, 5427) 2.762e-33 Granger-causes
Anomalies, VAR(4)            PM2.5 → Wind  1.82 (4, 5427)    0.1215    No evidence
Anomalies, VAR(4)        PM2.5 → Humidity  0.66 (4, 5427)    0.6166    No evidence
```
Robustness (BIC lag, first differences):
```
                            spec               direction     F         df   p_value   verdict (5%)
         Anomalies, VAR(4) [AIC]            Wind → PM2.5 35.95  (4, 5427) 1.076e-29 Granger-causes
         Anomalies, VAR(4) [AIC]        Humidity → PM2.5 14.35  (4, 5427) 1.165e-11 Granger-causes
         Anomalies, VAR(4) [AIC] Wind + Humidity → PM2.5 21.99  (8, 5427) 2.762e-33 Granger-causes
         Anomalies, VAR(4) [AIC]            PM2.5 → Wind  1.82  (4, 5427)    0.1215    No evidence
         Anomalies, VAR(4) [AIC]        PM2.5 → Humidity  0.66  (4, 5427)    0.6166    No evidence
         Anomalies, VAR(2) [BIC]            Wind → PM2.5 73.35  (2, 5451) 3.661e-32 Granger-causes
         Anomalies, VAR(2) [BIC]        Humidity → PM2.5 28.44  (2, 5451) 5.139e-13 Granger-causes
         Anomalies, VAR(2) [BIC] Wind + Humidity → PM2.5 44.82  (4, 5451)  4.36e-37 Granger-causes
         Anomalies, VAR(2) [BIC]            PM2.5 → Wind  4.18  (2, 5451)   0.01532 Granger-causes
         Anomalies, VAR(2) [BIC]        PM2.5 → Humidity  0.53  (2, 5451)    0.5881    No evidence
First differences, VAR(14) [AIC]            Wind → PM2.5 10.84 (14, 5304) 7.847e-25 Granger-causes
First differences, VAR(14) [AIC]        Humidity → PM2.5  5.47 (14, 5304)  1.47e-10 Granger-causes
First differences, VAR(14) [AIC] Wind + Humidity → PM2.5  7.23 (28, 5304) 1.014e-27 Granger-causes
First differences, VAR(14) [AIC]            PM2.5 → Wind  0.89 (14, 5304)    0.5686    No evidence
First differences, VAR(14) [AIC]        PM2.5 → Humidity  1.19 (14, 5304)     0.276    No evidence
```
HAC Wald:
```
                 spec        direction  wald_chi2   p_value
PM2.5, wind, humidity     Wind → PM2.5       96.3 5.951e-20
PM2.5, wind, humidity Humidity → PM2.5       54.8 3.518e-11
       + rain control     Wind → PM2.5       93.2 2.814e-19
       + rain control Humidity → PM2.5       40.7 3.036e-08
       + rain control     Rain → PM2.5        1.2    0.8771
PM2.5, wind, humidity     PM2.5 → Wind        7.9   0.09564
PM2.5, wind, humidity PM2.5 → Humidity        3.1    0.5457
```
HAC robustness (temperature, trend, training-only climatology):
```
                           spec           direction  wald_chi2   p_value    n
                 baseline (P=4)        Wind → PM2.5       96.3 5.951e-20 1822
          + temperature control        Wind → PM2.5       88.7  2.48e-18 1822
         + rain and temperature        Wind → PM2.5       86.1 9.061e-18 1822
            + linear time trend        Wind → PM2.5       96.5 5.516e-20 1822
climatology from 2015-2018 only        Wind → PM2.5         96 6.889e-20 1822
                 baseline (P=4)    Humidity → PM2.5       54.8 3.518e-11 1822
          + temperature control    Humidity → PM2.5       47.2 1.416e-09 1822
         + rain and temperature    Humidity → PM2.5       39.1 6.799e-08 1822
            + linear time trend    Humidity → PM2.5       56.9 1.317e-11 1822
climatology from 2015-2018 only    Humidity → PM2.5       55.4 2.615e-11 1822
          + temperature control Temperature → PM2.5       43.3 9.093e-09 1822
                 baseline (P=4)        PM2.5 → Wind        7.9   0.09564 1822
            + linear time trend        PM2.5 → Wind        9.6   0.04719 1822
                 baseline (P=4)    PM2.5 → Humidity        3.1    0.5457 1822
            + linear time trend    PM2.5 → Humidity        3.1     0.541 1822
```
Season-specific and interaction tests:
```
                                    test  wald_chi2   p_value    n
     Wind → PM2.5, Winter (Nov–Jan) only       34.8 5.182e-07  456
 Humidity → PM2.5, Winter (Nov–Jan) only       19.8 0.0005352  456
    Wind → PM2.5, Monsoon (Jul–Sep) only       47.6 1.121e-09  460
Humidity → PM2.5, Monsoon (Jul–Sep) only       28.3 1.098e-05  460
Interaction: monsoon × humidity lags = 0          6    0.1985 1822
     Interaction: winter × wind lags = 0       10.8   0.02934 1822
```
Joint tests by lag order:
```
       direction  lag_order  wald_chi2   p_value
    Wind → PM2.5          1       39.7 2.944e-10
Humidity → PM2.5          1       41.5 1.177e-10
    PM2.5 → Wind          1        4.3   0.03771
PM2.5 → Humidity          1        1.5    0.2172
    Wind → PM2.5          2       96.3 1.197e-21
Humidity → PM2.5          2       51.9 5.432e-12
    PM2.5 → Wind          2        8.4   0.01502
PM2.5 → Humidity          2        0.8    0.6538
    Wind → PM2.5          3       95.8 1.235e-20
Humidity → PM2.5          3       53.5 1.439e-11
    PM2.5 → Wind          3        7.2   0.06479
PM2.5 → Humidity          3        2.2    0.5364
    Wind → PM2.5          4       96.3 5.951e-20
Humidity → PM2.5          4       54.8 3.518e-11
    PM2.5 → Wind          4        7.9   0.09564
PM2.5 → Humidity          4        3.1    0.5457
    Wind → PM2.5          5       96.6 2.814e-19
Humidity → PM2.5          5       56.3 6.984e-11
    PM2.5 → Wind          5        7.2    0.2035
PM2.5 → Humidity          5        4.3    0.5134
    Wind → PM2.5          6        100 2.532e-19
Humidity → PM2.5          6       61.7 2.025e-11
    PM2.5 → Wind          6        7.7    0.2575
PM2.5 → Humidity          6        8.3    0.2167
    Wind → PM2.5          7      100.2 9.674e-19
Humidity → PM2.5          7       63.6 2.822e-11
    PM2.5 → Wind          7        9.4    0.2259
PM2.5 → Humidity          7        6.9    0.4382
```
IRF by ordering:
```
                      ordering    shock  day0_pct  day1_pct  day2_pct  day3_pct  day5_pct
weather first (wind, rh, pm25)     Wind      -9.2       -12      -4.7      -1.9      -0.3
weather first (wind, rh, pm25) Humidity      -4.5      -6.7      -5.7        -4      -1.4
  PM2.5 first (pm25, wind, rh)     Wind         0      -5.9      -1.1       0.9         1
  PM2.5 first (pm25, wind, rh) Humidity         0        -4      -4.1      -2.7      -0.7
```
Generalised IRF:
```
   shock  day0_pct  day1_pct  day2_pct  day3_pct  day5_pct
    Wind      -9.2       -12      -4.7      -1.9      -0.3
Humidity      -3.3      -5.2      -5.1      -3.8      -1.4
```
FEVD by ordering:
```
                      ordering variable  share_h1_pct  share_h14_pct
weather first (wind, rh, pm25)     Wind          13.3           20.5
weather first (wind, rh, pm25) Humidity             3            9.5
weather first (wind, rh, pm25)    PM2.5          83.7             70
  PM2.5 first (pm25, wind, rh)    PM2.5           100           93.7
  PM2.5 first (pm25, wind, rh)     Wind             0            3.1
  PM2.5 first (pm25, wind, rh) Humidity             0            3.3
```
Weekly lag regression:
```
               model                 term    coef  p_value  r2_model
   same-week weather                 wind -0.0402   0.0013    0.1403
   same-week weather             humidity -0.0105        0    0.1403
last-week predictors    PM2.5 (last week)  0.3621        0    0.1391
last-week predictors     wind (last week)  0.0066   0.4576    0.1391
last-week predictors humidity (last week) -0.0013   0.4799    0.1391
```
Nested comparison:
```
 R2_lagged_pm25_only  R2_plus_lagged_weather  delta_R2  joint_wald_p_weather
              0.1341                  0.1391     0.005                0.5146
```
Key numbers:
```
{
  "var_sample": "2015-01-01 to 2019-12-31 (1826 days)",
  "var_lag_aic": 4,
  "var_lag_bic": 2,
  "var_stable": true,
  "portmanteau_p": 0.168,
  "max_eigen_modulus": 0.813,
  "irf": {
    "wind": {
      "peak_pct": -12.0,
      "peak_day": 1,
      "shock_sd": 2.54,
      "unit": "km/h"
    },
    "rh": {
      "peak_pct": -6.7,
      "peak_day": 1,
      "shock_sd": 5.43,
      "unit": "% RH"
    }
  },
  "fevd_weather_share_h14": 30.0,
  "fevd_wind_h14": 20.5,
  "fevd_rh_h14": 9.5,
  "granger": {
    "Wind → PM2.5": 1.08e-29,
    "Humidity → PM2.5": 1.16e-11,
    "Wind + Humidity → PM2.5": 2.76e-33,
    "PM2.5 → Wind": 0.122,
    "PM2.5 → Humidity": 0.617
  },
  "granger_hac": {
    "Wind → PM2.5 | PM2.5, wind, humidity": 5.95e-20,
    "Humidity → PM2.5 | PM2.5, wind, humidity": 3.52e-11,
    "Wind → PM2.5 | + rain control": 2.81e-19,
    "Humidity → PM2.5 | + rain control": 3.04e-08,
    "Rain → PM2.5 | + rain control": 0.877,
    "PM2.5 → Wind | PM2.5, wind, humidity": 0.0956,
    "PM2.5 → Humidity | PM2.5, wind, humidity": 0.546
  }
}
```
