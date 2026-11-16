# 05 Phase 4: forecasting (notebook 04, src/forecast.py)
Design: three expanding-window origins (train to 2016-12-25, 2017-12-31, 2018-12-30; forecast next 52 weeks). Headline procedure (fixed in code before the final runs; 2019 had been examined in earlier iterations): Fourier+ARMA with K, (p,q) by AICc inside each level type and the level type by validation on the last training year.
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
           LSTM (small)  36.3  28.3  54.3          41.3        39.7
             SARIMA D=0  44.9  42.8  44.1          43.5        43.9
```
Full metrics by fold and model:
```
 fold                   model  n_train   MAE  RMSE  logMAE    bias  MAE_winter  MAE_other  coverage  winkler  width
 2017          Seasonal naive      104 38.44  65.6  0.2968  -13.56        65.1      25.49    0.8846    261.5  167.1
 2017             Climatology      104    31 43.41  0.2827  -1.201       43.08      25.13    0.6154    399.8  76.87
 2017     Climatology + AR(1)      104  30.7  43.4  0.2813  -1.906       42.17      25.13    0.6154    401.9  76.75
 2017       Linear regression      104 35.89 51.03  0.3195  -11.37       55.35      26.44      0.75    286.5  127.3
 2017            LSTM (small)      104 36.34 50.93  0.3219   2.761       53.92       27.8    0.4231    575.5  55.53
 2017      Fourier+ARMA const      104 30.59 47.65  0.2773  0.1821        45.6       23.3      0.75    327.5  104.6
 2017     Fourier+ARMA linear      104 35.86 50.72  0.3191  -11.09       55.36      26.38    0.6923    330.8  112.7
 2017 Fourier+ARMA (selected)      104 31.48 44.06   0.286  -5.726        48.8      23.07    0.6923    266.4  100.8
 2017              SARIMA D=1      104 53.83 102.1  0.3414  -31.35       101.2       30.8    0.7692    537.5  160.3
 2017              SARIMA D=0      104 44.87 62.59  0.4495  -12.49       47.85      43.43    0.8462    332.6  270.7
 2018          Seasonal naive      157 28.97 46.45  0.2502  -9.897       41.97      22.65    0.9423    223.9    175
 2018             Climatology      157 21.77 29.61  0.1997   -9.09       33.22      16.21    0.9231    142.8  104.6
 2018     Climatology + AR(1)      157 21.67 29.61  0.1993  -9.404        32.9      16.21    0.9231    142.8  104.6
 2018       Linear regression      157 19.99 28.85  0.1762 -0.5138       36.01      12.21    0.9615    147.8  127.9
 2018            LSTM (small)      157 28.32 37.99  0.2582  -7.072       43.68      20.86    0.6923    337.2  77.58
 2018      Fourier+ARMA const      157 22.05 30.44  0.1992  -7.822       36.29      15.13    0.9615    146.6  126.9
 2018     Fourier+ARMA linear      157 19.73 28.35   0.173  -1.816       35.82      11.92    0.9615    146.3  121.2
 2018 Fourier+ARMA (selected)      157 23.43 34.43  0.2009  -8.416       42.26      14.28    0.9423    142.2  116.2
 2018              SARIMA D=1      157 21.08 31.49  0.1842  -8.664       32.77      15.41    0.9423    169.1  151.1
 2018              SARIMA D=0      157 42.84 53.79  0.4193  -9.466       53.49      37.66    0.9615    262.7  260.7
 2019          Seasonal naive      209 30.31 46.29  0.2795   -6.37       56.27       17.7    0.9231    179.5  159.6
 2019             Climatology      209 27.82 42.14  0.2609  -12.56       46.59       18.7    0.8077    224.7  102.8
 2019     Climatology + AR(1)      209 27.33 41.79  0.2587  -13.08       45.08       18.7    0.8077    225.2  102.9
 2019       Linear regression      209 24.94 42.61  0.2177   1.068       50.84      12.36    0.9231    227.1  113.2
 2019            LSTM (small)      209 54.35 84.46  0.4306  -40.16        96.9      33.68    0.4423    920.6  107.5
 2019      Fourier+ARMA const      209 29.26 44.63  0.2643  -11.84       51.32      18.54    0.8846      242  122.9
 2019     Fourier+ARMA linear      209 23.97 41.77  0.2121 -0.3929       48.42       12.1    0.9231    235.4  109.2
 2019 Fourier+ARMA (selected)      209 25.69 39.87   0.233  -8.492       46.32      15.67    0.9038    174.9  125.1
 2019              SARIMA D=1      209 27.45 42.57  0.2632   -14.7       44.42      19.21    0.8462    205.9    133
 2019              SARIMA D=0      209  44.1 60.35  0.4525  -16.09       57.28       37.7    0.9038    262.6  240.5
```
Paired loss differences vs climatology (block bootstrap):
```
          folds                   model  mean_MAE_diff_vs_climatology  ci_lo  ci_hi           verdict
folds 2018+2019          Seasonal naive                          4.84   0.94   8.96             worse
folds 2018+2019     Climatology + AR(1)                          -0.3   -0.8   0.02 indistinguishable
folds 2018+2019       Linear regression                         -2.33  -5.83   1.91 indistinguishable
folds 2018+2019            LSTM (small)                         16.54   6.62  27.75             worse
folds 2018+2019      Fourier+ARMA const                          0.86  -2.09   4.32 indistinguishable
folds 2018+2019     Fourier+ARMA linear                         -2.94  -6.12   0.68 indistinguishable
folds 2018+2019 Fourier+ARMA (selected)                         -0.23  -2.91   2.77 indistinguishable
folds 2018+2019              SARIMA D=1                         -0.53  -1.91   0.98 indistinguishable
folds 2018+2019              SARIMA D=0                         18.67  13.13  23.88             worse
all three folds          Seasonal naive                          5.71   2.04  10.07             worse
all three folds     Climatology + AR(1)                          -0.3  -0.68      0 indistinguishable
all three folds       Linear regression                          0.08  -3.19    3.6 indistinguishable
all three folds            LSTM (small)                         12.81   6.07  20.63             worse
all three folds      Fourier+ARMA const                          0.44  -1.84   2.94 indistinguishable
all three folds     Fourier+ARMA linear                         -0.34  -3.45   3.04 indistinguishable
all three folds Fourier+ARMA (selected)                             0   -2.2   2.28 indistinguishable
all three folds              SARIMA D=1                          7.26   0.37  14.97             worse
all three folds              SARIMA D=0                         17.07  11.68  22.58             worse
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
Season scale + shrunk shift (post-hoc sensitivity)  23.6     0.962  158.9      161  4.328
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
       Jan        204.3        209.8        147      301.4      True
       Feb        122.3        141.9       95.2        213      True
       Mar         84.2        101.7       65.5      156.9      True
       Apr         82.3        101.5       63.8      160.2      True
       May         89.7        100.2       61.5      163.3      True
       Jun         63.8         75.4       45.7      122.8      True
       Jul         46.7         46.2       27.3       77.3      True
       Aug         34.1         43.2       25.3       73.8      True
       Sep         40.1         57.3       32.7       99.3      True
       Oct        123.7        141.9       80.7      250.8      True
       Nov        205.4        234.6      133.6      403.4      True
       Dec        205.2        199.2      113.8      346.7      True
```
2020 outlook:
```
month  median  lo95  hi95  P(mean>60)  P(mean>90)  P(mean>120)  days_Good  days_Satisfactory  days_Moderate  days_Poor  days_Very Poor  days_Severe  actual_mean_2020  actual_days_covered
  Jan   190.4 141.7 254.9           1           1        0.999          0              0.117          0.985      3.013           21.18        5.703             157.1                   31
  Feb   121.9 90.35 164.8           1       0.976        0.541       0.04              1.832          6.283      7.817            12.3        0.731             121.5                   29
  Mar   84.45 66.28 108.7       0.994       0.304        0.001      0.261              6.036          12.71      8.084           3.909        0.003             57.51                   31
  Apr   85.71 66.92 110.7       0.997       0.348        0.005      0.151              5.439          12.56      7.906           3.936        0.008             44.94                   30
  May   84.11 65.63 108.7       0.995       0.297        0.003      0.159              6.384          12.86      7.787           3.804        0.011             55.45                   31
  Jun   62.75 47.93  81.7        0.64       0.004            0      1.365               13.9          10.64      3.267           0.826        0.001              46.7                   30
  Jul   38.89 30.27 50.51           0           0            0      8.796              19.52          2.475      0.195           0.014            0             54.01                    1
  Aug   35.52 27.55 46.09           0           0            0      11.05              18.51           1.38      0.063           0.001            0               NaN                  NaN
  Sep   45.56 35.29 58.63       0.018           0            0      5.867              18.06          5.369      0.645           0.058            0               NaN                  NaN
  Oct   120.1 91.86 155.9           1       0.983        0.503      0.028              2.755          7.582      7.479           12.22        0.938               NaN                  NaN
  Nov   192.1 143.3 259.6           1           1            1      0.001              0.206          1.127      2.988           19.63        6.048               NaN                  NaN
  Dec   169.3 126.1 225.7           1           1         0.99          0              0.237          2.157      4.964           19.86        3.784               NaN                  NaN
```
Lockdown:
```
                                   Unnamed: 0  actual_mean  cf_median  gap_median_pct  gap_lo95_pct  gap_hi95_pct
0                        no-lockdown forecast         48.7         85           -42.8         -52.1         -31.8
1  weather-adjusted forecast (oracle weather)          NaN       78.6           -38.1         -47.5         -26.7
```
Key numbers:
```
{
  "sarima_d0_const": {
    "2017": {
      "no constant": 76.92,
      "with constant": 44.87,
      "Climatology (reference)": 31.0
    },
    "2018": {
      "no constant": 60.98,
      "with constant": 42.84,
      "Climatology (reference)": 21.77
    },
    "2019": {
      "no constant": 92.11,
      "with constant": 44.1,
      "Climatology (reference)": 27.82
    }
  },
  "nonconverged_rejected_per_origin": {
    "2017": 6,
    "2018": 3,
    "2019": 5
  },
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
  "calibration_2019_all": {
    "Model-based Gaussian": {
      "MAE": 25.694,
      "coverage": 0.904,
      "width": 125.08,
      "winkler": 174.878,
      "bias": -8.492
    },
    "Calibrated (season scale)": {
      "MAE": 25.694,
      "coverage": 0.962,
      "width": 178.655,
      "winkler": 192.721,
      "bias": -8.492
    },
    "Season scale + shrunk shift (post-hoc sensitivity)": {
      "MAE": 23.598,
      "coverage": 0.962,
      "width": 158.878,
      "winkler": 161.033,
      "bias": 4.328
    }
  },
  "shrunk_shift_2019": -0.445110367609404,
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
      "Moderate": 68.0,
      "Poor": 53.0,
      "Very Poor": 114.0,
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
    "mean_abs_days_error_per_band_month": 1.9,
    "poor_or_worse_pred_pct": 55.1,
    "poor_or_worse_actual_pct": 45.2
  },
  "outlook_2020_spec": {
    "trend": "linear",
    "K": 5,
    "p": 1,
    "q": 0,
    "n_rejected_nonconverged": 13
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
      "cf_median": 85.04899262695417,
      "gap_median_pct": -42.77449646078571,
      "gap_lo95_pct": -52.11359900861902,
      "gap_hi95_pct": -31.819259395224652
    },
    "weather_adjusted": {
      "cf_median": 78.5752915693168,
      "gap_median_pct": -38.059772562764856,
      "gap_lo95_pct": -47.516118559968525,
      "gap_hi95_pct": -26.675729977641215
    }
  },
  "lockdown_sensitivity": {
    "selected spec (linear, K=5, AR1), headline": {
      "pre_lockdown_gap_pct": -11.32,
      "lockdown_gap_10wk_pct": -42.77,
      "lo95": -52.11,
      "hi95": -31.82,
      "gap_9wk_from_5Apr_pct": -41.49,
      "lockdown_gap_adjusted_for_pre_gap_pct": -35.47
    },
    "constant level": {
      "pre_lockdown_gap_pct": -22.6,
      "lockdown_gap_10wk_pct": -50.84,
      "lo95": -59.58,
      "hi95": -40.01,
      "gap_9wk_from_5Apr_pct": -49.78,
      "lockdown_gap_adjusted_for_pre_gap_pct": -36.48
    },
    "random-walk level (ARIMA errors)": {
      "pre_lockdown_gap_pct": -9.87,
      "lockdown_gap_10wk_pct": -43.11,
      "lo95": -54.55,
      "hi95": -28.55,
      "gap_9wk_from_5Apr_pct": -41.74,
      "lockdown_gap_adjusted_for_pre_gap_pct": -36.88
    },
    "headline + shrunk mean-bias shift (post-hoc)": {
      "pre_lockdown_gap_pct": -2.43,
      "lockdown_gap_10wk_pct": -37.02,
      "lo95": -47.3,
      "hi95": -24.97,
      "gap_9wk_from_5Apr_pct": -35.61,
      "lockdown_gap_adjusted_for_pre_gap_pct": -35.45
    },
    "PLACEBO: same weeks of 2019 vs 2019 forecast": {
      "pre_lockdown_gap_pct": -8.88,
      "lockdown_gap_10wk_pct": -14.87,
      "lo95": -43.9,
      "hi95": 28.17,
      "gap_9wk_from_5Apr_pct": NaN,
      "lockdown_gap_adjusted_for_pre_gap_pct": NaN
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
      "2017": 36.34,
      "2018": 28.32,
      "2019": 54.35
    },
    "specs": {
      "2017": {
        "trend": "rw",
        "K": 5,
        "p": 1,
        "q": 1,
        "n_rejected_nonconverged": 6
      },
      "2018": {
        "trend": "const",
        "K": 5,
        "p": 1,
        "q": 1,
        "n_rejected_nonconverged": 3
      },
      "2019": {
        "trend": "rw",
        "K": 5,
        "p": 1,
        "q": 1,
        "n_rejected_nonconverged": 5
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
