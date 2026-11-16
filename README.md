# Delhi PM2.5: Seasonality, Weather Predictability and a Rolling-Origin Forecasting Study

MATH F428 Time Series Analysis project. We ask (Q1) whether weather predicts Delhi's PM2.5 and over what horizon, and (Q2) how well PM2.5 can be forecast one week and 52 weeks ahead.
Because the data end in July 2020 this is a **historical forecasting study**: backtests for 2017-2019 and a month-by-month outlook for 2020 made from data to December 2019.

## Status

| Phase | Work | Status |
|---|---|---|
| 1 | Data acquisition, merging, cleaning | Done |
| 2 | EDA: STL seasonality, log transform, volatility, stationarity, level drift, station-network check | Done |
| 3 | VAR, Granger causality (HAC, controls, season tests), shocks, impulse responses (Cholesky + generalised) | Done |
| 4 | Rolling-origin 52-week backtest, diagnostics, calibrated intervals, 1-week weather test, 2020 outlook, lockdown case study | Done |
| 5 | Deck, report, review log | Done |

## Data

| Source | Content | Period |
|---|---|---|
| CPCB via Kaggle [`rohanrao/air-quality-data-in-india`](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india): `city_day.csv`, `station_day.csv`, `stations.csv` | Delhi daily PM2.5, NO2, SO2; station-level PM2.5 | 2015-01-01 to 2020-07-01 (2,009 days) |
| [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) (ERA5, 28.61N 77.21E) | wind, humidity, temperature, rain | same |

2 PM2.5 values were missing (interpolated). 287 weekly means (week ending Sunday) are used for forecasting.

## Main results (all numbers are re-derived by `slides/beamer/verify_numbers.py`, 65 checks)

- **Seasonality:** winter 213 vs monsoon 48 ug/m3 (4.4x); STL seasonal strength 0.90 (2015-18 weeks). Log transform: skew 1.70 to -0.08, monthly spread 7.9x to 1.3x.
- **Level drift:** after removing the cycle, PM2.5 falls about 25% from 2016 to 2019. Station check: 10, 8, 17, 37, 37 stations reporting; a fixed 6-station panel still falls about 20%, so the decline is mostly real.
- **Weather (Q1):** wind and humidity anomalies predict PM2.5 for about a week (joint HAC tests p<1e-9 at every lag order 1-7; robust to rain/temperature controls, trend, training-only climatology). Reverse direction absent/weak. A 1-SD shock changes PM2.5 by about -6 to -12% (wind) and -4 to -7% (humidity) the next day. Predictive, not proof of physical cause.
- **Weekly scale:** last week's weather adds nothing (delta R2 = 0.005, p = 0.51).
- **52-week forecasts (Q2):** climatology is hard to beat. Pre-declared Fourier+ARMA: MAE 31.5 / 23.4 / 25.7 for 2017 / 2018 / 2019 vs climatology 31.0 / 21.8 / 27.8. SARIMA D=1 is unstable (54 in 2017), SARIMA D=0 and a small LSTM are clearly worse. Most differences are not significant with three origins.
- **Intervals:** model-based 95% intervals covered 90% of 2019 weeks (all misses low: level bias); seasonal rescaling from earlier folds gives 96%.
- **One week ahead:** lagged weather -2.4%, last-3-days +0.7%, same-week weather (hindsight) +6.9% MAE change: weather is explanatory, not a forecasting input.
- **2020:** outlook month by month; validated pipeline on 2019 (all 12 monthly means inside the 95% interval, but Poor-or-worse share over-predicted 55% vs 45%). Lockdown weeks were about 43% below the no-lockdown forecast (38% after weather adjustment).
- **Bugs found and fixed from the earlier draft:** Ljung-Box artifact (52 diffuse residuals), seasonal MA at -0.988 (unidentified), missing constant in D=0 SARIMA, test-year leakage in headline statistics, leap-year day-of-year, over-claims ("weather drives", "p<1e-10 everywhere", PM2.5 band called AQI). See `docs/REVIEW_RESPONSES.md`.

## Layout

```
data/raw/          city_day.csv, station_day.csv, stations.csv, delhi_weather_openmeteo.json
data/processed/    delhi_daily.csv, delhi_weekly.csv
src/               data.py, aqi.py, tsa.py (ADF/KPSS, climatology, week index), forecast.py (models, backtest, metrics, simulation), plots.py
notebooks/         01_data_prep, 02_eda, 03_var_granger, 04_forecasting   (all executed, outputs saved)
results/           CSV/JSON tables (fc_* = forecasting)      figures/  PNG figures from the notebooks
slides/            Delhi_PM25_presentation.pdf; slides/beamer = main.tex, make_figures.py, verify_numbers.py
report/            report.tex (project report)
docs/              REVIEW_RESPONSES.md (every claim of three reviews, verdict, evidence); docs/reviews = the raw reviews
archive/           original SARIMA draft (superseded)         tools/ build helpers
PRESENTATION_SCRIPT.md   talking points and Q&A     gemini_context/, gpt_context/   self-contained briefs for other LLM reviewers
```

## Reproduce

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
for f in city_day station_day stations; do kaggle datasets download rohanrao/air-quality-data-in-india -f $f.csv -p data/raw; done   # unzip the .zip files
cd notebooks && for n in 01_data_prep 02_eda 03_var_granger 04_forecasting; do ../.venv/bin/jupyter nbconvert --to notebook --execute --inplace $n.ipynb; done; cd ..
python tools/build_nb04.py   # only if you want to regenerate notebook 04 from its builder
cd slides/beamer && python make_figures.py && python verify_numbers.py && tectonic main.tex && cd ../../report && tectonic report.tex
```
Notebook 04 takes about 3 minutes (set `OMP_NUM_THREADS=1`; the notebook does this itself).

## Authors

Kushagra Singh, Yatin JM, Aryan Choudhary (BITS Pilani, Goa)
