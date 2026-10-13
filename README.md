# Delhi PM2.5 / AQI Forecasting: SARIMAX, VAR and Granger Causality

Time Series Analysis course project. We forecast urban PM2.5 for Delhi and test whether weather
(wind speed, humidity) causally drives it. The final goal is a 12-month AQI forecast with 95%
confidence intervals for public-health advisory planning.

## Status

| Phase | Work | Status |
|---|---|---|
| 0 | Environment setup | Done |
| 1 | Data acquisition, merging, cleaning | Done |
| 2 | EDA, seasonality, stationarity tests | Done |
| 3 | VAR and Granger causality | Done |
| 4 | SARIMAX (AIC/BIC grid, Ljung-Box diagnostics) | Not started |
| 5 | Baselines: seasonal naive, Linear Regression, LSTM (test MAE) | Not started |
| 6 | 12-month forecast with 95% CI and AQI advisory table | Not started |

## Data

| Source | Content | Period |
|---|---|---|
| CPCB via Kaggle [`rohanrao/air-quality-data-in-india`](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india) (`city_day.csv`) | Delhi daily PM2.5, NO2, SO2, AQI | 2015-01-01 to 2020-07-01 (2,009 days) |
| Open-Meteo Historical API (ERA5 reanalysis, 28.61N 77.21E) | Daily mean humidity, wind speed, temperature, precipitation | same |

Cleaning: only 2 PM2.5 days were missing, filled by time interpolation (gaps of 3 days or less).
SO2 has long gaps (28 and 81 days), so it is used only descriptively. PM2.5 is log-transformed.
Weekly means (weeks ending Sunday, 287 weeks) are prepared for the forecasting models (period 52).

## What has been done and the main results

**EDA and stationarity** ([notebooks/02_eda.ipynb](notebooks/02_eda.ipynb))
- Strong annual cycle: winter (Nov-Jan) mean PM2.5 is 213 ug/m3 vs 48 in the monsoon (Jul-Sep), about 4.4x.
  The November median is 4.9x the August median. 52% of days are rated Poor or worse (CPCB bands).
- STL seasonal strength is 0.89, which justifies a seasonal model with period 52 weeks.
- ADF and KPSS: log PM2.5 levels are stationary. The weekly seasonal difference alone is borderline
  (KPSS), so SARIMAX will compare D=0 and D=1 using held-out error and residual checks.
- Wind is negatively correlated with PM2.5 in every season. Humidity is negatively correlated only in the monsoon.

**VAR and Granger causality** ([notebooks/03_var_granger.ipynb](notebooks/03_var_granger.ipynb))
- Daily data 2015-2019 (the 2020 lockdown is excluded), with the seasonal cycle removed first
  (otherwise the shared calendar creates spurious causality).
- VAR(4) chosen by AIC. It is stable (max |eigenvalue| = 0.81) and the residuals pass the Portmanteau test (p = 0.17).
- Wind to PM2.5: p ~ 1.7e-29. Humidity to PM2.5: p ~ 1.1e-11. The reverse directions are not significant
  (p = 0.13 and 0.61). Results hold with the BIC lag and with first differences.
- Impulse response: a +1 SD wind shock (2.5 km/h) lowers PM2.5 by about 12% the next day. A +1 SD
  humidity shock (5.4% RH) lowers it by about 7%.
- Weather shocks explain about 30% of 14-day PM2.5 forecast-error variance (depends on the Cholesky ordering).
- Caveat: Granger causality is predictive, not proof of a physical cause. Mixing height and stubble burning are not measured.

## Planned next

- **SARIMAX:** weekly log PM2.5, s = 52, wind and humidity as exogenous inputs, order grid by AIC/BIC, Ljung-Box plots.
- **Comparison:** seasonal naive, Linear Regression and LSTM. Train 2015-2018, test 2019, compare test MAE.
- **Forecast:** refit on all data, 52-week forecast with 95% CI, monthly AQI advisory table. 2020 as a lockdown case study.

## Project layout

```
data/raw/          city_day.csv, delhi_weather_openmeteo.json
data/processed/    delhi_daily.csv, delhi_weekly.csv
src/               data.py (load/clean/merge), aqi.py (CPCB bands), tsa.py (ADF/KPSS, Granger), plots.py (style)
notebooks/         01_data_prep, 02_eda, 03_var_granger
figures/           PNG figures (used in the slides)
results/           CSV/JSON tables (stationarity, Granger p-values, FEVD, key numbers)
slides/            Delhi_PM25_progress.pptx / .pdf (4-slide progress deck)
make_slides.py     builds the slide deck from the figures
```

## Reproduce

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt python-pptx
# get the CPCB file (needs Kaggle credentials)
kaggle datasets download rohanrao/air-quality-data-in-india -f city_day.csv -p data/raw
unzip data/raw/city_day.csv.zip -d data/raw
# run the notebooks in order (the weather file downloads automatically)
cd notebooks && ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace 01_data_prep.ipynb 02_eda.ipynb 03_var_granger.ipynb
```

## Authors

Kushagra Singh (LuciferK47)
