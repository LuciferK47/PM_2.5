# 05 Phase 4: forecasting (notebook 04, src/forecast.py)
Design: three expanding-window origins (train to 2016-12-25, 2017-12-31, 2018-12-30; forecast next 52 weeks). Headline procedure (pre-declared): Fourier+ARMA with K, (p,q) by AICc inside each level type and the level type by validation on the last training year.
MAE (ug/m3):
```
                  model  2017  2018  2019  mean 2018-19  mean all 3
    Fourier+ARMA linear  35.9  19.7    24          21.9        26.5
      Linear regression  35.9    20  24.9          22.5        26.9
             SARIMA D=1  53.8  21.1  27.5          24.3        34.1
    Climatology + AR(1)  30.7  21.7  27.3          24.5        26.6
Fourier+ARMA (selected)  31.5  23.4  25.7          24.6        26.9
            Climatology    31  21.8  27.8          24.8        26.9
     Fourier+ARMA const  30.6    22  29.3          25.7        27.3
         Seasonal naive  38.4    29  30.3          29.6        32.6
             SARIMA D=0  44.9  42.8  44.1          43.5        43.9
           LSTM (small)  36.3  49.2  52.9          51.1        46.1
```
Full metrics by fold and model:
```
 fold                   model  n_train   MAE  RMSE  logMAE    bias  MAE_winter  MAE_other  coverage  winkler  width
 2017          Seasonal naive      104 38.44 61.87  0.2968  -13.56        65.1      25.49       NaN      NaN    NaN
 2017             Climatology      104    31 43.31  0.2827  -1.201       43.08      25.13       NaN      NaN    NaN
 2017     Climatology + AR(1)      104  30.7  43.4  0.2813  -1.906       42.17      25.13    0.6154    401.9  76.75
 2017       Linear regression      104 35.89 50.83  0.3195  -11.37       55.35      26.44    0.7308    313.8  118.1
 2017            LSTM (small)      104 36.29 50.16  0.3212  -10.29       52.83      28.26    0.1154     1225  12.65
 2017      Fourier+ARMA const      104 30.59 47.65  0.2773  0.1821        45.6       23.3      0.75    327.5  104.6
 2017     Fourier+ARMA linear      104 35.86 50.72  0.3191  -11.09       55.36      26.38    0.6923    330.8  112.7
 2017 Fourier+ARMA (selected)      104 31.48 44.06   0.286  -5.726        48.8      23.07    0.6923    266.4  100.8
 2017              SARIMA D=1      104 53.83 102.1  0.3414  -31.35       101.2       30.8    0.7692    537.5  160.3
 2017              SARIMA D=0      104 44.87 62.59  0.4495  -12.49       47.85      43.43    0.8462    332.6  270.7
 2018          Seasonal naive      157 28.97 41.96  0.2502  -9.897       41.97      22.65       NaN      NaN    NaN
 2018             Climatology      157 21.77 28.36  0.1997   -9.09       33.22      16.21       NaN      NaN    NaN
 2018     Climatology + AR(1)      157 21.67 29.61  0.1993  -9.404        32.9      16.21    0.9231    142.8  104.6
 2018       Linear regression      157 19.99 28.81  0.1762 -0.5138       36.01      12.21    0.9615      145  122.5
 2018            LSTM (small)      157 49.23 75.09  0.3447  -32.39        75.8      36.33         0     1758  11.26
 2018      Fourier+ARMA const      157 22.05 30.44  0.1992  -7.822       36.29      15.13    0.9615    146.6  126.9
 2018     Fourier+ARMA linear      157 19.73 28.35   0.173  -1.816       35.82      11.92    0.9615    146.3  121.2
 2018 Fourier+ARMA (selected)      157 23.43 34.43  0.2009  -8.416       42.26      14.28    0.9423    142.2  116.2
 2018              SARIMA D=1      157 21.08 31.49  0.1842  -8.664       32.77      15.41    0.9423    169.1  151.1
 2018              SARIMA D=0      157 42.84 53.79  0.4193  -9.466       53.49      37.66    0.9615    262.7  260.7
 2019          Seasonal naive      209 30.31 44.17  0.2795   -6.37       56.27       17.7       NaN      NaN    NaN
 2019             Climatology      209 27.82 41.12  0.2609  -12.56       46.59       18.7       NaN      NaN    NaN
 2019     Climatology + AR(1)      209 27.33 41.79  0.2587  -13.08       45.08       18.7    0.8077    225.2  102.9
 2019       Linear regression      209 24.94  42.6  0.2177   1.068       50.84      12.36    0.9231      229  109.9
 2019            LSTM (small)      209 52.87 80.83  0.4013  -39.46       95.15      32.34    0.1346     1798  18.43
 2019      Fourier+ARMA const      209 29.26 44.63  0.2643  -11.84       51.32      18.54    0.8846      242  122.9
 2019     Fourier+ARMA linear      209 23.97 41.77  0.2121 -0.3929       48.42       12.1    0.9231    235.4  109.2
 2019 Fourier+ARMA (selected)      209 25.69 39.87   0.233  -8.492       46.32      15.67    0.9038    174.9  125.1
 2019              SARIMA D=1      209 27.45 42.57  0.2632   -14.7       44.42      19.21    0.8462    205.9    133
 2019              SARIMA D=0      209  44.1 60.35  0.4525  -16.09       57.28       37.7    0.9038    262.6  240.5
```
Paired loss differences vs climatology (block bootstrap):
```
          folds                   model  mean_MAE_diff_vs_climatology  ci_lo  ci_hi           verdict
folds 2018+2019          Seasonal naive                          4.84   0.19   8.53             worse
folds 2018+2019     Climatology + AR(1)                          -0.3  -0.75   0.05 indistinguishable
folds 2018+2019       Linear regression                         -2.33  -6.17   0.77 indistinguishable
folds 2018+2019            LSTM (small)                         26.26    8.8   42.3             worse
folds 2018+2019      Fourier+ARMA const                          0.86   -2.1   2.72 indistinguishable
folds 2018+2019     Fourier+ARMA linear                         -2.94  -6.43  -0.36            better
folds 2018+2019 Fourier+ARMA (selected)                         -0.23  -3.56   1.81 indistinguishable
folds 2018+2019              SARIMA D=1                         -0.53  -2.32   1.02 indistinguishable
folds 2018+2019              SARIMA D=0                         18.67  12.96  23.98             worse
all three folds          Seasonal naive                          5.71   1.22    9.4             worse
all three folds     Climatology + AR(1)                          -0.3   -0.6   0.02 indistinguishable
all three folds       Linear regression                          0.08  -3.71   3.97 indistinguishable
all three folds            LSTM (small)                         19.27   7.53  30.95             worse
all three folds      Fourier+ARMA const                          0.44  -1.91   2.12 indistinguishable
all three folds     Fourier+ARMA linear                         -0.34  -3.96   3.24 indistinguishable
all three folds Fourier+ARMA (selected)                             0  -2.49   1.97 indistinguishable
all three folds              SARIMA D=1                          7.26  -0.57  14.21 indistinguishable
all three folds              SARIMA D=0                         17.07   11.1  22.85             worse
```
Residual diagnostics (burn-in removed):
```
                                 Unnamed: 0  burn  n_resid  resid_sd  LB_p_lag10  LB_p_lag26  LB_p_lag52  ARCH4_p      JB_p  LB_p_lag10_ALL_residuals (draft's mistake)
Fourier+ARMA (selected) (rw, K=5, p=1, q=1)     1      208    0.2265     0.08834    0.001037    0.009213   0.8696 0.0006318                                         NaN
                SARIMA D=1, burn-in removed    52      157     0.269      0.4887      0.1048     0.01589   0.8496     0.649                                           0
```
Calibration on 2019:
```
               Unnamed: 0   MAE  coverage  width  winkler   bias
     Model-based Gaussian 25.69     0.904  125.1    174.9 -8.492
Calibrated (season scale) 25.69     0.962  178.7    192.7 -8.492
```
One week ahead:
```
                                    model  2018  2019  both years  DM p vs no-weather DHR
                              Persistence 26.69  34.7       30.69                   0.002
                              Climatology 21.77 27.82        24.8                   0.249
                      Climatology + AR(1)  17.9 28.54       23.22                   0.714
                          DHR, no weather 20.33 24.45       22.39                     NaN
           + lagged weather (operational) 21.19 24.65       22.92                   0.075
+ last 3 days of prior week (operational) 20.42 24.06       22.24                   0.585
             + same-week weather (ORACLE) 17.57 24.12       20.84                   0.074
```
2019 pipeline validation (monthly):
```
Unnamed: 0  actual_mean  pred_median  pred_lo95  pred_hi95  inside95
       Jan        204.3        209.4      148.8      304.2      True
       Feb        122.3        144.1       97.9      212.1      True
       Mar         84.2        101.5       66.3      154.8      True
       Apr         82.3        101.5       63.7      161.4      True
       May         89.7        100.7       62.3        163      True
       Jun         63.8         74.6       45.4      122.9      True
       Jul         46.7           46       27.4         78      True
       Aug         34.1         42.8       24.8       73.6      True
       Sep         40.1           57       32.7       98.7      True
       Oct        123.7        144.7       83.5      255.5      True
       Nov        205.4        229.7      130.9      401.4      True
       Dec        205.2        199.6      112.4      355.5      True
```
2020 outlook:
```
month  median  lo95  hi95  P(mean>60)  P(mean>90)  P(mean>120)  days_Good  days_Satisfactory  days_Moderate  days_Poor  days_Very Poor  days_Severe  actual_mean_2020  actual_days_covered
  Jan   189.1   141 251.5           1           1        0.999          0              0.131          1.033      3.072           21.21        5.555             157.1                   31
  Feb   120.8 91.61 163.5           1        0.98        0.516      0.036              1.867          6.313      7.632           12.41        0.739             121.5                   29
  Mar   84.89 66.64 108.8       0.998       0.321        0.003      0.314              6.371          12.58      7.834           3.894        0.006             57.51                   31
  Apr   85.92 66.92 110.7       0.997       0.357        0.005      0.141              5.208          12.62       8.13           3.896        0.007             44.94                   30
  May   83.79 64.62 108.2       0.996       0.291        0.003      0.189              6.736          12.85      7.459           3.753        0.015             55.45                   31
  Jun   62.54  48.7 82.01       0.622       0.004            0      1.268               13.9          10.73      3.265           0.836            0              46.7                   30
  Jul   38.97  30.4 49.91           0           0            0      9.212              19.27          2.323      0.178           0.018            0             54.01                    1
  Aug   35.72 27.95  45.8           0           0            0      10.38               19.1          1.456      0.061           0.002            0               NaN                  NaN
  Sep   46.32 36.19 59.28        0.02           0            0      6.022              17.69          5.314      0.843           0.129            0               NaN                  NaN
  Oct   119.5 91.45 157.8           1       0.983        0.488      0.058              3.023          7.403      7.244           12.27        1.006               NaN                  NaN
  Nov   189.9 141.1 255.7           1           1        0.999      0.002              0.235          1.191      3.174           19.48        5.923               NaN                  NaN
  Dec   168.9 127.2 225.9           1           1        0.993          0              0.229          2.116       4.95           19.97        3.736               NaN                  NaN
```
Lockdown:
```
                                   Unnamed: 0  actual_mean  cf_median  gap_median_pct  gap_lo95_pct  gap_hi95_pct
0                        no-lockdown forecast         48.7       85.1           -42.8         -52.2         -31.5
1  weather-adjusted forecast (oracle weather)          NaN       78.5             -38         -47.8         -26.2
```
Key numbers:
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
