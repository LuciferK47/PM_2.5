# 05 All results tables (results/)

## annual_drift.csv
```
 Date  mean PM2.5 (µg/m³)  mean log anomaly
 2015               117.3             0.017
 2016               138.5             0.103
 2017               124.5            -0.043
 2018                 115            -0.077
 2019               108.5            -0.185
 2020                80.3            -0.496
```

## fc_backtest_mae.csv
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

## fc_backtest_metrics.csv
```
 fold                   model  n_train    MAE   RMSE  logMAE     bias  MAE_winter  MAE_other  coverage  winkler  width
 2017          Seasonal naive      104 38.438 61.872  0.2968   -13.56      65.098     25.489       NaN      NaN    NaN
 2017             Climatology      104 30.999 43.309 0.28271  -1.2015      43.078     25.131       NaN      NaN    NaN
 2017     Climatology + AR(1)      104 30.701 43.396 0.28125  -1.9062      42.167     25.131   0.61538    401.9 76.751
 2017       Linear regression      104 35.893 50.825 0.31948  -11.367      55.353     26.441   0.73077   313.76 118.15
 2017            LSTM (small)      104 36.291 50.161 0.32118  -10.286      52.828     28.259   0.11538   1224.5 12.651
 2017      Fourier+ARMA const      104 30.592 47.655  0.2773  0.18211      45.602     23.302      0.75    327.5  104.6
 2017     Fourier+ARMA linear      104 35.856 50.717 0.31914  -11.087      55.358     26.383   0.69231   330.84 112.71
 2017 Fourier+ARMA (selected)      104 31.483 44.063 0.28597  -5.7257      48.805      23.07   0.69231   266.41 100.75
 2017              SARIMA D=1      104 53.827 102.13 0.34136  -31.352      101.23     30.802   0.76923   537.52 160.32
 2017              SARIMA D=0      104 44.874  62.59 0.44952   -12.49       47.85     43.428   0.84615   332.58 270.65
 2018          Seasonal naive      157 28.965 41.961 0.25023  -9.8967      41.972     22.648       NaN      NaN    NaN
 2018             Climatology      157 21.772 28.356 0.19972    -9.09      33.224      16.21       NaN      NaN    NaN
 2018     Climatology + AR(1)      157 21.667 29.605 0.19932  -9.4044      32.903      16.21   0.92308   142.76 104.61
 2018       Linear regression      157  19.99  28.81 0.17624 -0.51377      36.009     12.209   0.96154   145.04 122.51
 2018            LSTM (small)      157 49.231 75.089 0.34473  -32.394      75.802     36.325         0   1757.9 11.262
 2018      Fourier+ARMA const      157 22.049  30.44 0.19919  -7.8222      36.286     15.134   0.96154   146.63 126.92
 2018     Fourier+ARMA linear      157 19.733 28.354 0.17299  -1.8157      35.817      11.92   0.96154   146.26 121.18
 2018 Fourier+ARMA (selected)      157 23.426 34.432 0.20086  -8.4162      42.257      14.28   0.94231   142.22 116.16
 2018              SARIMA D=1      157 21.084  31.49 0.18417  -8.6636      32.766     15.409   0.94231   169.08 151.11
 2018              SARIMA D=0      157 42.835 53.791 0.41929  -9.4661      53.492     37.659   0.96154   262.74  260.7
 2019          Seasonal naive      209 30.306  44.17 0.27952  -6.3698      56.268     17.696       NaN      NaN    NaN
 2019             Climatology      209 27.818 41.121 0.26091  -12.562      46.588     18.701       NaN      NaN    NaN
 2019     Climatology + AR(1)      209 27.326 41.786 0.25875  -13.083      45.084     18.701   0.80769   225.24 102.93
 2019       Linear regression      209 24.945 42.603  0.2177    1.068      50.845     12.365   0.92308   228.96 109.89
 2019            LSTM (small)      209  52.87 80.833 0.40125  -39.458      95.145     32.337   0.13462     1798 18.426
 2019      Fourier+ARMA const      209 29.261 44.632 0.26435  -11.842      51.324     18.545   0.88462   242.05 122.86
 2019     Fourier+ARMA linear      209 23.974 41.773 0.21215 -0.39285      48.416     12.101   0.92308    235.4 109.17
 2019 Fourier+ARMA (selected)      209 25.694 39.869 0.23295  -8.4921      46.324     15.674   0.90385   174.88 125.08
 2019              SARIMA D=1      209 27.452 42.571 0.26318  -14.696      44.417     19.212   0.84615   205.88    133
 2019              SARIMA D=0      209 44.103 60.354 0.45248   -16.09       57.28     37.703   0.90385    262.6  240.5
```

## fc_calibration_2019.csv
```
               Unnamed: 0    MAE  coverage  width  winkler   bias
     Model-based Gaussian 25.694     0.904 125.08   174.88 -8.492
Calibrated (season scale) 25.694     0.962 178.66   192.72 -8.492
```

## fc_diagnostics.csv
```
                                 Unnamed: 0  burn  n_resid  resid_sd  LB_p_lag10  LB_p_lag26  LB_p_lag52  ARCH4_p       JB_p  LB_p_lag10_ALL_residuals (draft's mistake)
Fourier+ARMA (selected) (rw, K=5, p=1, q=1)     1      208   0.22653    0.088338   0.0010369    0.009213  0.86964 0.00063185                                         NaN
                SARIMA D=1, burn-in removed    52      157   0.26901     0.48866     0.10481    0.015892  0.84959    0.64897                                           0
```

## fc_lockdown.csv
```
                                Unnamed: 0  actual_mean  cf_median  gap_median_pct  gap_lo95_pct  gap_hi95_pct
                      no-lockdown forecast         48.7       85.1           -42.8         -52.2         -31.5
weather-adjusted forecast (oracle weather)          NaN       78.5             -38         -47.8         -26.2
```

## fc_loss_diff.csv
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

## fc_oneweek.csv
```
                                    model   2018   2019  both years  DM p vs no-weather DHR
                              Persistence 26.692 34.697      30.694                   0.002
                              Climatology 21.772 27.818      24.795                   0.249
                      Climatology + AR(1) 17.897 28.538      23.217                   0.714
                          DHR, no weather 20.326 24.455      22.391                     NaN
           + lagged weather (operational) 21.191 24.648       22.92                   0.075
+ last 3 days of prior week (operational) 20.424 24.059      22.241                   0.585
             + same-week weather (ORACLE) 17.566 24.121      20.844                   0.074
```

## fc_oneweek_oracle_coef.csv
```
Unnamed: 0    coef      p
 wind_same  -0.037 0.0033
   rh_same -0.0099 0.0002
```

## fc_outlook_2020.csv
```
month  median   lo95   hi95  P(mean>60)  P(mean>90)  P(mean>120)  days_Good  days_Satisfactory  days_Moderate  days_Poor  days_Very Poor  days_Severe  actual_mean_2020  actual_days_covered
  Jan  189.08 140.98  251.5           1           1        0.999          0              0.131          1.033      3.072          21.209        5.555            157.11                   31
  Feb  120.77 91.615 163.52           1        0.98        0.516      0.036              1.867          6.313      7.632          12.413        0.739            121.48                   29
  Mar  84.893 66.636 108.82       0.998       0.321        0.003      0.314              6.371          12.58      7.834           3.894        0.006            57.506                   31
  Apr  85.919 66.921 110.71       0.997       0.357        0.005      0.141              5.208         12.618       8.13           3.896        0.007             44.94                   30
  May  83.789 64.619 108.23       0.996       0.291        0.003      0.189              6.736         12.848      7.459           3.753        0.015            55.449                   31
  Jun   62.54 48.702 82.009       0.622       0.004            0      1.268             13.905         10.726      3.265           0.836            0            46.695                   30
  Jul  38.973 30.403 49.911           0           0            0      9.212             19.269          2.323      0.178           0.018            0             54.01                    1
  Aug  35.721 27.954 45.801           0           0            0     10.383             19.098          1.456      0.061           0.002            0               NaN                  NaN
  Sep   46.32 36.193 59.279        0.02           0            0      6.022             17.694          5.314      0.843           0.129            0               NaN                  NaN
  Oct  119.52 91.451 157.82           1       0.983        0.488      0.058              3.023          7.403      7.244          12.267        1.006               NaN                  NaN
  Nov  189.92 141.14 255.66           1           1        0.999      0.002              0.235          1.191      3.174          19.476        5.923               NaN                  NaN
  Dec  168.89 127.25 225.88           1           1        0.993          0              0.229          2.116       4.95          19.969        3.736               NaN                  NaN
```

## fc_outlook_validation_2019_days.csv
```
Unnamed: 0 predicted  predicted.1 predicted.2 predicted.3 predicted.4 predicted.5 actual     actual.1 actual.2 actual.3  actual.4 actual.5
       NaN      Good Satisfactory    Moderate        Poor   Very Poor      Severe   Good Satisfactory Moderate     Poor Very Poor   Severe
       Jan       0.0          0.0         0.6         2.2        19.6         8.5      0            1        1        2        16       11
       Feb       0.0          1.0         3.8         5.9        15.0         2.2      0            3        6        6        12        1
       Mar       0.3          4.9         9.3         7.7         8.4         0.3      0            5       13       13         0        0
       Apr       0.1          4.1         9.0         7.7         8.7         0.4      1            6       12        9         2        0
       May       0.3          5.0         9.2         7.5         8.6         0.4      0            6       12        8         5        0
       Jun       1.2          9.9        10.0         5.2         3.6         0.1      1           12       14        3         0        0
       Jul       7.1         17.0         5.4         1.2         0.4         0.0      4           17       10        0         0        0
       Aug       7.9         17.1         4.8         0.9         0.2         0.0     11           19        1        0         0        0
       Sep       4.4         13.6         7.7         2.8         1.5         0.0      8           18        4        0         0        0
       Oct       0.1          2.2         5.2         5.8        13.9         3.7      0            8        2        8         9        4
       Nov       0.0          0.1         0.9         2.2        15.6        11.3      0            2        1        6        12        9
       Dec       0.0          0.2         1.6         3.5        17.7         8.0      0            0        2        3        17        9
```

## fc_outlook_validation_2019_monthly.csv
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

## fc_weekly_2020.csv
```
      date   lo95  median   hi95  weather_adj_median  actual
2020-01-05 117.43  197.22 326.23              199.29  271.12
2020-01-12 115.59  192.53 322.58               177.2  139.48
2020-01-19 112.08  188.49 320.19              167.73  134.75
2020-01-26 106.09  178.63 301.57              176.13  150.87
2020-02-02 96.131  162.39 271.34              156.84  115.57
2020-02-09 83.778   141.1  238.5              142.96  149.55
2020-02-16 72.098   120.5 202.45              110.41  129.76
2020-02-23 61.826  103.65 174.75              90.204  106.28
2020-03-01 58.667  92.037 146.05              78.434  90.536
2020-03-08 55.011  85.389 134.07              72.546  62.044
2020-03-15 51.937  82.039 129.49              71.268  60.517
2020-03-22 52.485  81.863 127.95              75.622  77.453
2020-03-29 52.078  82.411 129.87              68.353  38.483
2020-04-05 53.864  83.636 130.34              75.303  36.531
2020-04-12 53.228  84.018 131.26              83.312  44.019
2020-04-19 53.039  84.333 133.77              86.219  48.349
2020-04-26 54.213  84.322 134.28              77.837   48.89
2020-05-03 53.898  84.065 130.64              62.269  43.191
2020-05-10 54.315  84.188 131.34              75.335    46.7
2020-05-17 53.674  83.937 131.55              76.421  62.766
2020-05-24  52.06  81.986 130.55              94.091  79.433
2020-05-31 50.673  78.187 123.11              70.176  38.336
2020-06-07 47.475  73.799 115.14              74.586  46.196
2020-06-14   42.5  67.022 106.03              75.895  58.957
2020-06-21 37.817  58.649 93.832              60.644  41.859
2020-06-28 32.637  51.362 80.133               54.48  41.014
```

## fevd_orderings.csv
```
                      ordering variable  share_h1_pct  share_h14_pct
weather first (wind, rh, pm25)     Wind          13.3           20.5
weather first (wind, rh, pm25) Humidity             3            9.5
weather first (wind, rh, pm25)    PM2.5          83.7             70
  PM2.5 first (pm25, wind, rh)    PM2.5           100           93.7
  PM2.5 first (pm25, wind, rh)     Wind             0            3.1
  PM2.5 first (pm25, wind, rh) Humidity             0            3.3
```

## fevd_pm25.csv
```
 horizon (days)  Wind  Humidity  PM2.5
              1  13.3         3   83.7
              2  22.6       6.2   71.3
              3  22.2       8.3   69.6
              4  21.3       9.1   69.5
              5    21       9.2   69.8
              6  20.8       9.3     70
              7  20.6       9.3     70
              8  20.6       9.4     70
              9  20.5       9.4     70
             10  20.5       9.5     70
             11  20.5       9.5     70
             12  20.5       9.5     70
             13  20.5       9.5     70
             14  20.5       9.5     70
```

## girf.csv
```
   shock  day0_pct  day1_pct  day2_pct  day3_pct  day5_pct
    Wind      -9.2       -12      -4.7      -1.9      -0.3
Humidity      -3.3      -5.2      -5.1      -3.8      -1.4
```

## granger_hac.csv
```
                 spec        direction  wald_chi2    p_value
PM2.5, wind, humidity     Wind → PM2.5       96.3 5.9514e-20
PM2.5, wind, humidity Humidity → PM2.5       54.8 3.5177e-11
       + rain control     Wind → PM2.5       93.2 2.8142e-19
       + rain control Humidity → PM2.5       40.7 3.0364e-08
       + rain control     Rain → PM2.5        1.2    0.87711
PM2.5, wind, humidity     PM2.5 → Wind        7.9    0.09564
PM2.5, wind, humidity PM2.5 → Humidity        3.1    0.54566
```

## granger_hac_by_lag.csv
```
       direction  lag_order  wald_chi2    p_value
    Wind → PM2.5          1       39.7 2.9444e-10
Humidity → PM2.5          1       41.5 1.1767e-10
    PM2.5 → Wind          1        4.3   0.037711
PM2.5 → Humidity          1        1.5     0.2172
    Wind → PM2.5          2       96.3 1.1968e-21
Humidity → PM2.5          2       51.9 5.4323e-12
    PM2.5 → Wind          2        8.4   0.015024
PM2.5 → Humidity          2        0.8    0.65378
    Wind → PM2.5          3       95.8 1.2347e-20
Humidity → PM2.5          3       53.5 1.4389e-11
    PM2.5 → Wind          3        7.2   0.064789
PM2.5 → Humidity          3        2.2    0.53639
    Wind → PM2.5          4       96.3 5.9514e-20
Humidity → PM2.5          4       54.8 3.5177e-11
    PM2.5 → Wind          4        7.9    0.09564
PM2.5 → Humidity          4        3.1    0.54566
    Wind → PM2.5          5       96.6 2.8143e-19
Humidity → PM2.5          5       56.3 6.9845e-11
    PM2.5 → Wind          5        7.2    0.20348
PM2.5 → Humidity          5        4.3    0.51336
    Wind → PM2.5          6        100 2.5323e-19
Humidity → PM2.5          6       61.7 2.0249e-11
    PM2.5 → Wind          6        7.7    0.25745
PM2.5 → Humidity          6        8.3    0.21666
    Wind → PM2.5          7      100.2 9.6739e-19
Humidity → PM2.5          7       63.6 2.8224e-11
    PM2.5 → Wind          7        9.4    0.22594
PM2.5 → Humidity          7        6.9    0.43821
```

## granger_hac_robust.csv
```
                           spec           direction  wald_chi2    p_value    n
                 baseline (P=4)        Wind → PM2.5       96.3 5.9514e-20 1822
          + temperature control        Wind → PM2.5       88.7 2.4804e-18 1822
         + rain and temperature        Wind → PM2.5       86.1 9.0608e-18 1822
            + linear time trend        Wind → PM2.5       96.5 5.5157e-20 1822
climatology from 2015-2018 only        Wind → PM2.5         96  6.889e-20 1822
                 baseline (P=4)    Humidity → PM2.5       54.8 3.5177e-11 1822
          + temperature control    Humidity → PM2.5       47.2 1.4163e-09 1822
         + rain and temperature    Humidity → PM2.5       39.1  6.799e-08 1822
            + linear time trend    Humidity → PM2.5       56.9 1.3171e-11 1822
climatology from 2015-2018 only    Humidity → PM2.5       55.4 2.6155e-11 1822
          + temperature control Temperature → PM2.5       43.3 9.0928e-09 1822
                 baseline (P=4)        PM2.5 → Wind        7.9    0.09564 1822
            + linear time trend        PM2.5 → Wind        9.6   0.047186 1822
                 baseline (P=4)    PM2.5 → Humidity        3.1    0.54566 1822
            + linear time trend    PM2.5 → Humidity        3.1    0.54102 1822
```

## granger_hac_seasonal.csv
```
                                    test  wald_chi2    p_value    n
     Wind → PM2.5, Winter (Nov–Jan) only       34.8 5.1822e-07  456
 Humidity → PM2.5, Winter (Nov–Jan) only       19.8 0.00053516  456
    Wind → PM2.5, Monsoon (Jul–Sep) only       47.6 1.1206e-09  460
Humidity → PM2.5, Monsoon (Jul–Sep) only       28.3 1.0976e-05  460
Interaction: monsoon × humidity lags = 0          6    0.19851 1822
     Interaction: winter × wind lags = 0       10.8   0.029343 1822
```

## granger_pairwise_lags.csv
```
      Unnamed: 0          1          2          3          4          5          6          7
    Wind → PM2.5 2.9007e-08 1.0203e-25 6.3508e-24 3.2579e-23 2.0842e-22 8.0101e-22 5.0983e-21
Humidity → PM2.5 7.4034e-06 3.1776e-07 1.6308e-06 6.0115e-06 1.6863e-05 4.0518e-06 7.1361e-06
    PM2.5 → Wind 0.00090552 0.00043834  0.0038446   0.013515   0.035788   0.056725    0.08261
PM2.5 → Humidity    0.25671    0.55311     0.5735    0.65111    0.56406     0.5313    0.63106
```

## granger_robustness.csv
```
                            spec               direction     F         df    p_value   verdict (5%)
         Anomalies, VAR(4) [AIC]            Wind → PM2.5 35.95  (4, 5427) 1.0757e-29 Granger-causes
         Anomalies, VAR(4) [AIC]        Humidity → PM2.5 14.35  (4, 5427) 1.1646e-11 Granger-causes
         Anomalies, VAR(4) [AIC] Wind + Humidity → PM2.5 21.99  (8, 5427) 2.7623e-33 Granger-causes
         Anomalies, VAR(4) [AIC]            PM2.5 → Wind  1.82  (4, 5427)    0.12152    No evidence
         Anomalies, VAR(4) [AIC]        PM2.5 → Humidity  0.66  (4, 5427)    0.61663    No evidence
         Anomalies, VAR(2) [BIC]            Wind → PM2.5 73.35  (2, 5451) 3.6612e-32 Granger-causes
         Anomalies, VAR(2) [BIC]        Humidity → PM2.5 28.44  (2, 5451) 5.1392e-13 Granger-causes
         Anomalies, VAR(2) [BIC] Wind + Humidity → PM2.5 44.82  (4, 5451) 4.3604e-37 Granger-causes
         Anomalies, VAR(2) [BIC]            PM2.5 → Wind  4.18  (2, 5451)   0.015317 Granger-causes
         Anomalies, VAR(2) [BIC]        PM2.5 → Humidity  0.53  (2, 5451)     0.5881    No evidence
First differences, VAR(14) [AIC]            Wind → PM2.5 10.84 (14, 5304) 7.8472e-25 Granger-causes
First differences, VAR(14) [AIC]        Humidity → PM2.5  5.47 (14, 5304) 1.4703e-10 Granger-causes
First differences, VAR(14) [AIC] Wind + Humidity → PM2.5  7.23 (28, 5304) 1.0137e-27 Granger-causes
First differences, VAR(14) [AIC]            PM2.5 → Wind  0.89 (14, 5304)    0.56861    No evidence
First differences, VAR(14) [AIC]        PM2.5 → Humidity  1.19 (14, 5304)    0.27596    No evidence
```

## granger_var.csv
```
             spec               direction     F        df    p_value   verdict (5%)
Anomalies, VAR(4)            Wind → PM2.5 35.95 (4, 5427) 1.0757e-29 Granger-causes
Anomalies, VAR(4)        Humidity → PM2.5 14.35 (4, 5427) 1.1646e-11 Granger-causes
Anomalies, VAR(4) Wind + Humidity → PM2.5 21.99 (8, 5427) 2.7623e-33 Granger-causes
Anomalies, VAR(4)            PM2.5 → Wind  1.82 (4, 5427)    0.12152    No evidence
Anomalies, VAR(4)        PM2.5 → Humidity  0.66 (4, 5427)    0.61663    No evidence
```

## irf_ci.csv
```
                      ordering    shock  h    pct     lo     hi
weather first (wind, rh, pm25)     Wind  0  -9.22 -10.28  -8.15
weather first (wind, rh, pm25)     Wind  1 -11.98 -13.28 -10.66
weather first (wind, rh, pm25)     Wind  2  -4.66  -6.19   -3.1
weather first (wind, rh, pm25)     Wind  3  -1.94  -3.56   -0.3
weather first (wind, rh, pm25)     Wind  4  -1.39  -2.98   0.22
weather first (wind, rh, pm25)     Wind  5  -0.33  -1.87   1.24
weather first (wind, rh, pm25)     Wind  6   0.07  -1.11   1.27
weather first (wind, rh, pm25)     Wind  7      0  -0.84   0.85
weather first (wind, rh, pm25)     Wind  8  -0.05  -0.64   0.55
weather first (wind, rh, pm25)     Wind  9  -0.08  -0.46    0.3
weather first (wind, rh, pm25)     Wind 10   -0.1  -0.35   0.14
weather first (wind, rh, pm25)     Wind 11  -0.09  -0.27   0.08
weather first (wind, rh, pm25)     Wind 12  -0.07   -0.2   0.06
weather first (wind, rh, pm25)     Wind 13  -0.05  -0.15   0.05
weather first (wind, rh, pm25)     Wind 14  -0.03  -0.11   0.05
weather first (wind, rh, pm25) Humidity  0  -4.53  -5.59  -3.45
weather first (wind, rh, pm25) Humidity  1  -6.74  -8.05  -5.41
weather first (wind, rh, pm25) Humidity  2  -5.66  -7.16  -4.14
weather first (wind, rh, pm25) Humidity  3  -4.03   -5.6  -2.44
weather first (wind, rh, pm25) Humidity  4  -2.01  -3.46  -0.54
weather first (wind, rh, pm25) Humidity  5  -1.41  -2.79     -0
weather first (wind, rh, pm25) Humidity  6  -1.34   -2.7   0.04
weather first (wind, rh, pm25) Humidity  7  -1.14  -2.37    0.1
weather first (wind, rh, pm25) Humidity  8  -0.85  -1.92   0.23
weather first (wind, rh, pm25) Humidity  9  -0.59  -1.51   0.34
weather first (wind, rh, pm25) Humidity 10   -0.4   -1.2    0.4
weather first (wind, rh, pm25) Humidity 11  -0.28  -0.97   0.41
weather first (wind, rh, pm25) Humidity 12  -0.21   -0.8   0.38
weather first (wind, rh, pm25) Humidity 13  -0.16  -0.65   0.35
weather first (wind, rh, pm25) Humidity 14  -0.12  -0.53   0.31
  PM2.5 first (pm25, wind, rh)     Wind  0      0      0      0
  PM2.5 first (pm25, wind, rh)     Wind  1   -5.9  -7.07  -4.72
  PM2.5 first (pm25, wind, rh)     Wind  2  -1.13  -2.66   0.42
  PM2.5 first (pm25, wind, rh)     Wind  3   0.88  -0.75   2.53
  PM2.5 first (pm25, wind, rh)     Wind  4   0.72  -0.87   2.33
  PM2.5 first (pm25, wind, rh)     Wind  5   1.03  -0.49   2.58
  PM2.5 first (pm25, wind, rh)     Wind  6   1.03  -0.12   2.19
  PM2.5 first (pm25, wind, rh)     Wind  7   0.72   -0.1   1.55
  PM2.5 first (pm25, wind, rh)     Wind  8   0.47   -0.1   1.04
  PM2.5 first (pm25, wind, rh)     Wind  9   0.29  -0.07   0.65
  PM2.5 first (pm25, wind, rh)     Wind 10   0.16  -0.07    0.4
  PM2.5 first (pm25, wind, rh)     Wind 11    0.1  -0.08   0.27
  PM2.5 first (pm25, wind, rh)     Wind 12   0.07  -0.06    0.2
  PM2.5 first (pm25, wind, rh)     Wind 13   0.05  -0.05   0.15
  PM2.5 first (pm25, wind, rh)     Wind 14   0.04  -0.04   0.12
  PM2.5 first (pm25, wind, rh) Humidity  0      0      0      0
  PM2.5 first (pm25, wind, rh) Humidity  1  -3.99  -5.16   -2.8
  PM2.5 first (pm25, wind, rh) Humidity  2  -4.12  -5.59  -2.63
  PM2.5 first (pm25, wind, rh) Humidity  3  -2.73  -4.29  -1.15
  PM2.5 first (pm25, wind, rh) Humidity  4  -1.01  -2.45   0.45
  PM2.5 first (pm25, wind, rh) Humidity  5  -0.74  -2.12   0.66
  PM2.5 first (pm25, wind, rh) Humidity  6  -0.87  -2.21    0.5
  PM2.5 first (pm25, wind, rh) Humidity  7   -0.8  -2.01   0.43
  PM2.5 first (pm25, wind, rh) Humidity  8   -0.6  -1.66   0.47
  PM2.5 first (pm25, wind, rh) Humidity  9  -0.41  -1.34   0.52
  PM2.5 first (pm25, wind, rh) Humidity 10  -0.27  -1.08   0.54
  PM2.5 first (pm25, wind, rh) Humidity 11  -0.19  -0.89   0.51
  PM2.5 first (pm25, wind, rh) Humidity 12  -0.14  -0.74   0.46
  PM2.5 first (pm25, wind, rh) Humidity 13  -0.11  -0.62    0.4
  PM2.5 first (pm25, wind, rh) Humidity 14  -0.08  -0.51   0.35
```

## irf_orderings.csv
```
                      ordering    shock  day0_pct  day1_pct  day2_pct  day3_pct  day5_pct
weather first (wind, rh, pm25)     Wind      -9.2       -12      -4.7      -1.9      -0.3
weather first (wind, rh, pm25) Humidity      -4.5      -6.7      -5.7        -4      -1.4
  PM2.5 first (pm25, wind, rh)     Wind         0      -5.9      -1.1       0.9         1
  PM2.5 first (pm25, wind, rh) Humidity         0        -4      -4.1      -2.7      -0.7
```

## log_justification.csv
```
                                 Unnamed: 0  raw PM2.5  log PM2.5
                                   Skewness     1.7041  -0.077175
             corr(monthly mean, monthly SD)    0.95121  -0.066645
                       Max / min monthly SD      7.903     1.3406
    Levene F (equal variance across months)     49.633     2.3989
                             Levene p-value 9.5512e-97   0.005908
ARCH-LM statistic (7 lags, on daily change)     235.18     36.434
                            ARCH-LM p-value 3.9253e-47 6.0017e-06
```

## missing_report.csv
```
Unnamed: 0  n_missing  pct_missing  longest_gap_days
      pm25          2          0.1                 2
       no2          2          0.1                 2
       so2        110         5.48                81
       aqi         10          0.5                 4
        rh          0            0                 0
      wind          0            0                 0
      temp          0            0                 0
    precip          0            0                 0
```

## monthly_mean_sd.csv
```
 Date   mean  sd_raw  sd_log
    1 197.49  69.877 0.37333
    2 141.98  53.074  0.3524
    3 87.574  31.707 0.39633
    4 90.932  36.493 0.44833
    5  92.21  40.202 0.43825
    6  69.81  32.453 0.40911
    7 46.418  18.666 0.40635
    8 42.858  14.588 0.38326
    9 55.345  22.754  0.4517
   10 140.91  69.169 0.45839
   11 238.25  115.29 0.47244
   12  208.1   69.61 0.35791
```

## season_stats.csv
```
       Unnamed: 0  pm25 pm25.1 wind wind.1   rh   rh.1
              NaN  mean median mean median mean median
           season   NaN    NaN  NaN    NaN  NaN    NaN
Monsoon (Jul–Sep)  48.1   46.0  9.0    8.4 78.0   80.0
     Other months 102.5   93.9  9.9    9.3 52.2   53.0
 Winter (Nov–Jan) 213.3  201.4  8.6    8.1 68.6   69.0
```

## station_check.csv
```
 Unnamed: 0  stations  all_mean_pm25  all_log_anom  panel_mean_pm25  panel_days  panel_log_anom  weather_adj_log_anom
       2015        10            110         0.073            111.7         262            0.04                 0.056
       2016         8          138.3         0.121            135.2         342           0.088                 0.085
       2017        17          149.4         0.051              190         125            0.02                -0.006
       2018        37          114.7        -0.054            121.6         365            0.01                -0.026
       2019        37          108.2        -0.163            110.9         365          -0.132                 -0.11
```

## stationarity.csv
```
                           series    n  adf_stat    adf_p  adf_lags  adf_crit_1%  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p                                   verdict
                Daily PM2.5 (raw) 2009     -3.98  0.00152        17       -3.434       -2.863        -2.568      0.224     0.1                                Stationary
                  Daily log PM2.5 2009    -3.089   0.0274        18       -3.434       -2.863        -2.568      0.366  0.0917                                Stationary
                Daily Δ log PM2.5 2008   -15.229 5.35e-28        17       -3.434       -2.863        -2.568      0.031     0.1                                Stationary
                 Daily wind speed 2009   -13.142 1.42e-24         6       -3.434       -2.863        -2.568       0.54  0.0326 Mixed (ADF says stationary, KPSS rejects)
               Daily Δ wind speed 2008   -15.186 6.11e-28        26       -3.434       -2.863        -2.568      0.141     0.1                                Stationary
              Daily rel. humidity 2009    -4.521  0.00018         9       -3.434       -2.863        -2.568      0.052     0.1                                Stationary
            Daily Δ rel. humidity 2008   -20.681        0         8       -3.434       -2.863        -2.568      0.015     0.1                                Stationary
                 Weekly log PM2.5  287    -5.389 3.57e-06         9       -3.454       -2.872        -2.572      0.158     0.1                                Stationary
         Weekly Δ log PM2.5 (d=1)  286    -9.743 8.42e-17         2       -3.454       -2.872        -2.572      0.027     0.1                                Stationary
       Weekly Δ₅₂ log PM2.5 (D=1)  235    -5.852 3.57e-07         2       -3.459       -2.874        -2.573      0.669  0.0163 Mixed (ADF says stationary, KPSS rejects)
Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1)  234    -9.235 1.64e-15         6       -3.459       -2.874        -2.574      0.049     0.1                                Stationary
```

## stationarity_anomalies.csv
```
          series    n  adf_stat    adf_p  adf_lags  adf_crit_1%  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p                                   verdict
    Wind anomaly 1826   -19.557        0         3       -3.434       -2.863        -2.568      1.048    0.01 Mixed (ADF says stationary, KPSS rejects)
Humidity anomaly 1826   -12.558 2.14e-23         3       -3.434       -2.863        -2.568      0.222     0.1                                Stationary
   PM2.5 anomaly 1826    -6.576 7.71e-09        18       -3.434       -2.863        -2.568      2.035    0.01 Mixed (ADF says stationary, KPSS rejects)
```

## stationarity_train.csv
```
                           series   n  adf_stat    adf_p  adf_lags  adf_crit_1%  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p    verdict  lag1_acf
         Weekly log PM2.5 (train) 209     -4.28  0.00048         9       -3.464       -2.876        -2.575      0.058     0.1 Stationary      0.87
         Weekly Δ log PM2.5 (d=1) 208    -5.364 4.02e-06         5       -3.463       -2.876        -2.574      0.082     0.1 Stationary     -0.28
       Weekly Δ₅₂ log PM2.5 (D=1) 157    -4.534 0.000171         2       -3.474        -2.88        -2.577      0.341     0.1 Stationary      0.29
Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1) 156    -7.298 1.36e-10         5       -3.475       -2.881        -2.577      0.075     0.1 Stationary     -0.46
```

## var_lag_selection.csv
```
 lag    aic    bic   hqic    fpe
   0  4.484 4.4931 4.4874 88.588
   1 2.5663 2.6028 2.5798 13.018
   2 2.4443 2.5081 2.4678 11.523
   3 2.4336 2.5247 2.4673   11.4
   4 2.4278 2.5462 2.4715 11.334
   5 2.4337 2.5794 2.4875 11.401
   6 2.4322 2.6053 2.4961 11.384
   7 2.4378 2.6382 2.5117 11.448
   8 2.4356 2.6634 2.5197 11.423
   9 2.4421 2.6972 2.5362 11.497
  10  2.443 2.7254 2.5472 11.507
  11 2.4503   2.76 2.5646 11.592
  12  2.458 2.7951 2.5824 11.682
  13 2.4622 2.8266 2.5967 11.731
  14 2.4676 2.8593 2.6121 11.794
```

## weekly_lag_nested.csv
```
 R2_lagged_pm25_only  R2_plus_lagged_weather  delta_R2  joint_wald_p_weather
              0.1341                  0.1391     0.005                0.5146
```

## weekly_weather_lag.csv
```
               model                 term    coef  p_value  r2_model
   same-week weather                 wind -0.0402   0.0013    0.1403
   same-week weather             humidity -0.0105        0    0.1403
last-week predictors    PM2.5 (last week)  0.3621        0    0.1391
last-week predictors     wind (last week)  0.0066   0.4576    0.1391
last-week predictors humidity (last week) -0.0013   0.4799    0.1391
```

## within_season_correlation.csv
```
           season  ρ(PM2.5, wind)  ρ(PM2.5, RH)  days
Monsoon (Jul–Sep)           -0.39         -0.37   461
     Other months            -0.3         -0.02  1057
 Winter (Nov–Jan)           -0.47         -0.02   491
```

## key_numbers_eda.json
```
{
  "pct_days_poor_or_worse": 52.2,
  "winter_mean_pm25": 213.3,
  "monsoon_mean_pm25": 48.1,
  "winter_to_monsoon_ratio": 4.43,
  "nov_to_aug_median_ratio": 4.9,
  "seasonal_strength_full": 0.89,
  "trend_strength_full": 0.34,
  "seasonal_strength": 0.9,
  "trend_strength": 0.09,
  "spearman_pm25_wind": -0.24,
  "spearman_pm25_rh": -0.2,
  "boxcox_lambda_daily": 0.045,
  "boxcox_lambda_weekly": 0.028,
  "boxcox_lambda_daily_train": 0.097,
  "boxcox_lambda_weekly_train": 0.108,
  "kpss_stat_level_daily_log": 0.366,
  "kpss_stat_anomaly_train_2015_2018": 0.896,
  "kpss_stat_anomaly_2015_2019": 1.997,
  "city_vs_station_mean_corr": 0.995,
  "stations_by_year": {
    "2015": 10,
    "2016": 8,
    "2017": 17,
    "2018": 37,
    "2019": 37,
    "2020": 36
  },
  "panel_stations": [
    "DL002",
    "DL013",
    "DL019",
    "DL021",
    "DL028",
    "DL031"
  ],
  "decline_2016_2019_pct": {
    "all_stations": -24.7,
    "fixed_panel": -19.7,
    "weather_adjusted": -17.7
  }
}
```

## key_numbers_forecast.json
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

## key_numbers_var.json
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

## shock_binned.json
```
{
 "curves": {
  "wind": {
   "z": [
    -1.79,
    -1.05,
    -0.5,
    -0.01,
    0.5,
    1.07,
    2.26
   ],
   "pct": [
    31.4,
    14.5,
    6.0,
    -1.9,
    -6.2,
    -10.7,
    -23.8
   ],
   "n": [
    80,
    322,
    395,
    390,
    260,
    245,
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
    1.04,
    2.23
   ],
   "pct": [
    -1.4,
    1.6,
    5.4,
    4.9,
    2.2,
    -7.9,
    -21.2
   ],
   "n": [
    96,
    278,
    355,
    423,
    324,
    223,
    122
   ]
  }
 },
 "jan21_shock_kmh": 7.376632291245462,
 "jan21_wind": 14.8,
 "jan21_pred": 7.423367708754538
}
```
