# 03 Phase 2: EDA and stationarity (notebook 02)
Season statistics:
```
       Unnamed: 0  pm25 pm25.1 wind wind.1   rh   rh.1
              NaN  mean median mean median mean median
           season   NaN    NaN  NaN    NaN  NaN    NaN
Monsoon (Jul–Sep)  48.1   46.0  9.0    8.4 78.0   80.0
     Other months 102.5   93.9  9.9    9.3 52.2   53.0
 Winter (Nov–Jan) 213.3  201.4  8.6    8.1 68.6   69.0
```
Within-season correlation:
```
           season  ρ(PM2.5, wind)  ρ(PM2.5, RH)  days
Monsoon (Jul–Sep)           -0.39         -0.37   461
     Other months            -0.3         -0.02  1057
 Winter (Nov–Jan)           -0.47         -0.02   491
```
Stationarity (full sample):
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
Stationarity (training weeks 2015-18, with lag-1 ACF):
```
                           series   n  adf_stat    adf_p  adf_lags  adf_crit_1%  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p    verdict  lag1_acf
         Weekly log PM2.5 (train) 209     -4.28  0.00048         9       -3.464       -2.876        -2.575      0.058     0.1 Stationary      0.87
         Weekly Δ log PM2.5 (d=1) 208    -5.364 4.02e-06         5       -3.463       -2.876        -2.574      0.082     0.1 Stationary     -0.28
       Weekly Δ₅₂ log PM2.5 (D=1) 157    -4.534 0.000171         2       -3.474        -2.88        -2.577      0.341     0.1 Stationary      0.29
Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1) 156    -7.298 1.36e-10         5       -3.475       -2.881        -2.577      0.075     0.1 Stationary     -0.46
```
Log justification:
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

Annual drift (anomaly vs training climatology):
```
 Date  mean PM2.5 (µg/m³)  mean log anomaly
 2015               117.3             0.017
 2016               138.5             0.103
 2017               124.5            -0.043
 2018                 115            -0.077
 2019               108.5            -0.185
 2020                80.3            -0.496
```
Station-network check (fixed panel, all stations, weather-adjusted):
```
 Unnamed: 0  stations  all_mean_pm25  all_log_anom  panel_mean_pm25  panel_days  panel_log_anom  weather_adj_log_anom
       2015        10            110         0.073            111.7         262            0.04                 0.056
       2016         8          138.3         0.121            135.2         342           0.088                 0.085
       2017        17          149.4         0.051              190         125            0.02                -0.006
       2018        37          114.7        -0.054            121.6         365            0.01                -0.026
       2019        37          108.2        -0.163            110.9         365          -0.132                 -0.11
```

Key numbers:
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
