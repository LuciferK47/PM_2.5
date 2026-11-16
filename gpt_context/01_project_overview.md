# 01 Project overview

## Goal
Understand what drives Delhi's PM2.5 and prepare a **12-month forecast with 95% intervals** for AQI advisory planning.
Two questions:
- **Q1 (done):** does weather (wind, humidity) drive PM2.5? Answered with VAR + Granger causality + IRF.
- **Q2 (next):** what will PM2.5 be? Two horizons: (a) 12 months ahead (52 weekly steps) without weather; (b) 1 week ahead, where same-week weather may add accuracy (upper bound, assumes weather is known).

## Data
| Source | Content | Period |
|---|---|---|
| CPCB via Kaggle `rohanrao/air-quality-data-in-india`, file `city_day.csv`, City == "Delhi" | daily PM2.5, NO2, SO2, AQI, AQI_Bucket (a city-level aggregate of stations) | 2015-01-01 to 2020-07-01, 2,009 days |
| Open-Meteo Historical API (ERA5 reanalysis, one grid cell at 28.61N, 77.21E) | daily mean relative humidity (rh, %), wind speed 10 m (wind, km/h), temperature (temp, C), precipitation sum (precip, mm) | same |

Cleaning (src/data.py): merge on date; gaps <= 3 days time-interpolated; longer gaps left NaN (only SO2 has long gaps: 28 and 81 days, SO2 only used descriptively); negatives clipped to 0; `log_pm25 = ln(pm25)`; PM2.5 missing = 2 days (0.1%), both interpolated.
Weekly series: weeks ending Sunday, mean of daily values (precip summed); weeks with < 4 valid PM2.5 days dropped. 287 weeks, 2015-01-04 to 2020-06-28, seasonal period s = 52.

Yearly mean PM2.5 (weekly data, ug/m3): 2015 117.0, 2016 137.5, 2017 126.4, 2018 114.5, **2019 108.1**, 2020 (half year, lockdown) 83.2. So there is a downward drift into the test year.

## Split and design decisions
- Train 2015-2018 (209 weeks), test 2019 (52 weeks). 2020 excluded from test and from the VAR (lockdown = emissions shock).
- Model log PM2.5 (variance stabilisation); back-transform with exp() gives a *median* forecast.
- d = 0 (log level passes ADF and KPSS on training data); D in {0,1} to be picked on a validation year (2018, fit on 2015-2017), not on the test year.
- Weather is NOT used in the 12-month model: Granger effect lasts about a week, last week's weather does not predict this week's PM2.5 (p ~ 0.46), and future weather is unknown a year ahead.
- AQI categories (CPCB, PM2.5 24h, ug/m3): Good <=30, Satisfactory <=60, Moderate <=90, Poor <=120, Very Poor <=250, Severe >250. 52.2% of days were Poor or worse.

## Status (README)
| Phase | Work | Status |
|---|---|---|
| 1 | data acquisition, merging, cleaning | Done |
| 2 | EDA: STL seasonality, log transform, volatility tests, stationarity | Done |
| 3 | VAR, Granger causality, shocks, impulse responses | Done |
| 4 | SARIMA(X), baselines (seasonal naive, climatology, Linear Regression, LSTM), final forecast | Draft only (`next_phase/`), notebook NOT executed; 1-week-ahead results do not exist yet |

## Repo layout (original)
```
data/raw/ city_day.csv, delhi_weather_openmeteo.json      data/processed/ delhi_daily.csv, delhi_weekly.csv
src/ data.py aqi.py tsa.py plots.py                       notebooks/ 01_data_prep, 02_eda, 03_var_granger
results/ CSV/JSON tables                                  figures/ 11 PNGs
slides/beamer/ main.tex, make_figures.py, verify_numbers.py (52 automated checks of slide numbers)
next_phase/ 04_sarima.ipynb, 04_sarima_draft.py + outputs  PRESENTATION_SCRIPT.md
```
Stack: Python 3.12, pandas, statsmodels, scipy, matplotlib, scikit-learn, torch (for the planned LSTM).
Git: 3 commits (first commit, README, authors); the phase 2/3 rework, next_phase/, beamer slides are uncommitted. `__pycache__` is tracked and there is no .gitignore.

## Current deliverable
A 14-slide Beamer deck (plus 3 backup) presenting phases 1-3 and the plan for phase 4. SARIMA is explicitly "next phase".
