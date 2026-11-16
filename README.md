# Delhi PM2.5 Analysis: Seasonality, Stationarity, VAR and Granger Causality

Time Series Analysis course project (MATH F428). Goal: understand what drives Delhi's PM2.5 and prepare a 12-month
forecast with 95% intervals for AQI advisory planning.

## Status

| Phase | Work | Status |
|---|---|---|
| 1 | Data acquisition, merging, cleaning | Done |
| 2 | EDA: seasonality (STL), log transform, volatility tests, stationarity | Done |
| 3 | VAR and Granger causality, shocks and impulse responses | Done |
| 4 | SARIMA(X) models, baselines (seasonal naive, climatology, LR, LSTM), final forecast | Next phase |

## Data

| Source | Content | Period |
|---|---|---|
| CPCB via Kaggle [`rohanrao/air-quality-data-in-india`](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india) (`city_day.csv`) | Delhi daily PM2.5, NO2, SO2 | 2015-01-01 to 2020-07-01 (2,009 days) |
| [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) (ERA5 reanalysis, 28.61N 77.21E) | Daily wind speed, relative humidity, temperature, rain | same |

Only 2 PM2.5 values were missing (interpolated). Weekly means (287 weeks, period 52) are prepared for forecasting.
Split: train 2015-2018, test 2019; the 2020 lockdown is excluded.

## Main results

- **Seasonality:** winter (Nov-Jan) mean 213 vs monsoon (Jul-Sep) 48 ug/m3 (4.4x); STL seasonal strength 0.89.
- **Log transform:** monthly spread 7.9x to 1.3x, skewness 1.70 to -0.08, Box-Cox lambda 0.045. Some volatility
  clustering remains (ARCH-LM 235 to 36, still significant): to be re-checked on model residuals.
- **Stationarity (training years):** log PM2.5 and its seasonal difference pass ADF and KPSS, so d = 0; a further
  difference over-differences (lag-1 ACF -0.46). The seasonal difference D is chosen in the next phase on a validation year.
- **Granger causality** (daily, deseasonalised, VAR(4), HAC errors): wind and humidity predict PM2.5 at every lag from
  1 to 7 days (p < 1e-9) and humidity still does after controlling for rain; the reverse is absent for humidity and
  weak for wind (lags 1-2 only).
- **Shocks:** a +1 SD wind shock (2.5 km/h) lowers PM2.5 by 6-12% the next day, humidity (5.4% RH) by 4-7%,
  fading within about a week (range over the VAR ordering). Weather's share of 14-day forecast error: 6-30%.
- **Horizon:** last week's weather does not predict this week's PM2.5 (p about 0.5), so the 12-month model should not rely on weather.
- Caveat: Granger causality is predictive, not proof of a physical cause.

## Project layout

```
data/raw/          city_day.csv, delhi_weather_openmeteo.json
data/processed/    delhi_daily.csv, delhi_weekly.csv
src/               data.py, aqi.py, tsa.py (ADF/KPSS, deseasonalising), plots.py
notebooks/         01_data_prep, 02_eda, 03_var_granger
results/           CSV/JSON result tables
figures/           PNG figures from the notebooks
slides/            Delhi_PM25_presentation.pdf; slides/beamer/ = main.tex, make_figures.py, verify_numbers.py
next_phase/        SARIMA draft (notebook, grid, forecast outputs): not part of the current deliverable
PRESENTATION_SCRIPT.md   talking points and Q&A
```

## Reproduce

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
kaggle datasets download rohanrao/air-quality-data-in-india -f city_day.csv -p data/raw && unzip data/raw/city_day.csv.zip -d data/raw
# run notebooks 01, 02, 03 (jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb)
python slides/beamer/make_figures.py && cd slides/beamer && tectonic main.tex    # build the slides
python slides/beamer/verify_numbers.py                                           # independent audit of every slide number
```

## Authors

Kushagra Singh, Yatin JM, Aryan Choudhary (BITS Pilani, Goa)
