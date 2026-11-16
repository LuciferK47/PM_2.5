
=================== FILE: 00_START_HERE.md ===================
# START HERE: briefing for GPT
You cannot open the original project, so everything is in these text files. The project (Delhi PM2.5 time-series study, MATH F428) is **finished**; your job is a **final independent audit**.
## Context in 5 lines
- Daily PM2.5 for Delhi 2015-2020 (CPCB) + ERA5 weather. Q1: does weather predict PM2.5? Q2: how well can PM2.5 be forecast 1 and 52 weeks ahead?
- Weather has a short-memory predictive association (days); at 52 weeks climatology is hard to beat; a Fourier+ARMA model matches/slightly beats it; SARIMA/LSTM do not help.
- Data end July 2020, so it is a historical forecasting study (2017-19 backtests + 2020 outlook).
- A draft had several bugs and over-claims; three reviewers (Claude, Gemini, GPT) found them; each claim was re-tested (file 06).
- Everything (code, tables, numbers) is included. Be critical and specific; do not just agree.
## Files
| File | Content |
|---|---|
| 01_project_overview.md | README: status, data, results, layout |
| 02_data_and_code.md | data samples and full source of src/ |
| 03_phase2_eda_results.md | EDA, stationarity, drift, station check |
| 04_phase3_var_granger_results.md | VAR, Granger (many robustness rows), IRF/GIRF, FEVD |
| 05_phase4_forecasting_results.md | backtest, diagnostics, calibration, 1-week test, 2020 outlook, lockdown |
| 06_review_log.md | every earlier claim with verdict and evidence |
| 07_audit_questions.md | what we want you to audit |
| 08_presentation_and_QA.md | the talk script and Q&A (the public claims) |


=================== FILE: 01_project_overview.md ===================
# 01 Project overview (README)

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


=================== FILE: 02_data_and_code.md ===================
# 02 Data schema and source code

## daily table
```
      Date   pm25   no2  so2   aqi aqi_bucket  rh  wind  temp  precip  imputed  log_pm25           season
2015-01-01 313.22 36.39 9.25 472.0     Severe  68   6.6  16.3     0.0    False      5.75 Winter (Nov–Jan)
2015-01-02 186.18 32.87 6.65 454.0     Severe  83   7.0  15.2     4.2    False      5.23 Winter (Nov–Jan)
2015-01-03  87.18 30.31 2.65 143.0   Moderate  84   5.1  15.6     0.1    False      4.47 Winter (Nov–Jan)
2015-01-04 151.84 36.91 4.63 319.0  Very Poor  78  10.2  14.4     0.0    False      5.02 Winter (Nov–Jan)
2015-01-05 146.60 34.92 3.33 325.0  Very Poor  74  18.7  14.3     0.0    False      4.99 Winter (Nov–Jan)
```

## weekly table
```
      Date   pm25   no2  so2    aqi    rh  wind  temp  precip  n_days  log_pm25
2015-01-04 184.60 34.12 5.80 347.00 78.25  7.22 15.38     4.3       4      5.22
2015-01-11 196.01 41.19 4.44 358.43 79.43  9.91 13.17     0.0       7      5.28
2015-01-18 187.65 49.24 5.45 360.00 82.29  7.53 12.60     4.1       7      5.23
2015-01-25 156.36 24.63 6.52 326.14 80.00  8.09 13.34    20.8       7      5.05
2015-02-01 162.78 37.28 6.47 324.14 70.00 10.09 12.44     0.0       7      5.09
```

### src/data.py
```python
"""Loading, merging and cleaning Delhi air-quality (CPCB) and weather (Open-Meteo ERA5) data."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"

DELHI = {"latitude": 28.61, "longitude": 77.21}

CPCB_COLS = {"PM2.5": "pm25", "NO2": "no2", "SO2": "so2", "AQI": "aqi", "AQI_Bucket": "aqi_bucket"}
WEATHER_COLS = {
    "relative_humidity_2m_mean": "rh",   # %
    "wind_speed_10m_mean": "wind",       # km/h
    "temperature_2m_mean": "temp",       # °C
    "precipitation_sum": "precip",       # mm
}

SEASONS = {"Winter (Nov–Jan)": [11, 12, 1], "Monsoon (Jul–Sep)": [7, 8, 9]}
OTHER_SEASON = "Other months"


def load_cpcb_city(path, city="Delhi"):
    """Daily CPCB records for one city from Kaggle `city_day.csv`, on a complete daily index."""
    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.loc[df["City"] == city, ["Date", *CPCB_COLS]].rename(columns=CPCB_COLS)
    return df.set_index("Date").sort_index().asfreq("D")


def fetch_openmeteo(path, start, end, latitude, longitude):
    """Download daily ERA5 weather from the Open-Meteo archive API (cached at `path`)."""
    path = Path(path)
    if path.exists():
        return path
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start,
        "end_date": end,
        "daily": ",".join(WEATHER_COLS),
        "timezone": "Asia/Kolkata",
    }
    r = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=60)
    r.raise_for_status()
    path.write_text(r.text)
    return path


def load_openmeteo(path):
    daily = json.loads(Path(path).read_text())["daily"]
    df = pd.DataFrame(daily).rename(columns={"time": "Date", **WEATHER_COLS})
    df["Date"] = pd.to_datetime(df["Date"])
    return df.set_index("Date").asfreq("D")


def gap_lengths(s):
    """Length of the run of consecutive NaNs each element belongs to (0 where not NaN)."""
    na = s.isna()
    run_id = (na != na.shift()).cumsum()
    return na.groupby(run_id).transform("sum").where(na, 0).astype(int)


def missing_report(df):
    num = df.select_dtypes("number")
    return pd.DataFrame({
        "n_missing": num.isna().sum(),
        "pct_missing": (num.isna().mean() * 100).round(2),
        "longest_gap_days": num.apply(lambda s: gap_lengths(s).max()),
    })


def clean_daily(df, max_gap=3):
    """Time-interpolate only gaps of <= max_gap days; longer gaps stay NaN.

    Adds `imputed` (True if any core variable was filled that day), `log_pm25` and `season`.
    """
    out = df.copy()
    core = ["pm25", "no2", "so2", "rh", "wind", "temp", "precip"]
    imputed = pd.Series(False, index=out.index)
    for c in core:
        short = out[c].isna() & (gap_lengths(out[c]) <= max_gap)
        filled = out[c].interpolate(method="time", limit_area="inside")
        out[c] = out[c].where(~short, filled)
        imputed |= short & out[c].notna()
    for c in ["pm25", "no2", "so2", "wind", "precip"]:
        out[c] = out[c].clip(lower=0)
    out["imputed"] = imputed
    out["log_pm25"] = np.log(out["pm25"])
    out["season"] = season_of(out.index)
    return out


def season_of(index):
    month = pd.DatetimeIndex(index).month
    season = pd.Series(OTHER_SEASON, index=index)
    for name, months in SEASONS.items():
        season[month.isin(months)] = name
    return season


def to_weekly(daily, min_days=4):
    """Weekly (week ending Sunday) means; drops weeks with fewer than `min_days` PM2.5 days."""
    num = daily[["pm25", "no2", "so2", "aqi", "rh", "wind", "temp"]]
    weekly = num.resample("W-SUN").mean()
    weekly["precip"] = daily["precip"].resample("W-SUN").sum(min_count=1)
    weekly["n_days"] = daily["pm25"].resample("W-SUN").count()
    weekly = weekly[weekly["n_days"] >= min_days].copy()
    weekly["log_pm25"] = np.log(weekly["pm25"])
    return weekly
```

### src/tsa.py
```python
"""Time-series test helpers: stationarity, deseasonalising and Granger tables."""
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, grangercausalitytests, kpss


def adf_kpss(series, name, alpha=0.05):
    """ADF (H0: unit root) and KPSS (H0: level-stationary) on one series, with a combined verdict."""
    s = pd.Series(series).dropna()
    adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # KPSS warns when p is outside its lookup table
        kpss_stat, kpss_p, *_ = kpss(s, regression="c", nlags="auto")
    adf_ok, kpss_ok = adf_p < alpha, kpss_p > alpha
    if adf_ok and kpss_ok:
        verdict = "Stationary"
    elif not adf_ok and not kpss_ok:
        verdict = "Non-stationary"
    elif adf_ok:
        verdict = "Mixed (ADF says stationary, KPSS rejects)"
    else:
        verdict = "Mixed (KPSS says stationary, ADF can't reject unit root)"
    return {
        "series": name, "n": len(s),
        "adf_stat": round(adf_stat, 3), "adf_p": float(f"{adf_p:.3g}"), "adf_lags": adf_lags,
        **{f"adf_crit_{k}": round(v, 3) for k, v in adf_crit.items()},
        "kpss_stat": round(kpss_stat, 3), "kpss_p": float(f"{kpss_p:.3g}"),
        "verdict": verdict,
    }


def stationarity_table(series_dict):
    return pd.DataFrame([adf_kpss(s, name) for name, s in series_dict.items()]).set_index("series")


def doy365(index):
    """Calendar day-of-year on a fixed 1..365 scale: Feb 29 maps to day 59, later leap-year days shift by -1."""
    idx = pd.DatetimeIndex(index)
    doy = np.asarray(idx.dayofyear)
    leap_after_feb = idx.is_leap_year & (doy > 59)
    return np.where(leap_after_feb, doy - 1, doy).clip(1, 365)


def doy_climatology(s, window=31):
    """Smoothed day-of-year mean (circular rolling window), indexed 1..365. Fit on whatever sample is passed."""
    clim = s.groupby(doy365(s.index)).mean().reindex(range(1, 366)).interpolate()
    half = window // 2
    padded = pd.concat([clim.iloc[-half:], clim, clim.iloc[:half]])
    return padded.rolling(window, center=True).mean().iloc[half:-half]


def apply_climatology(s, clim):
    """Subtract a previously fitted climatology (from `doy_climatology`) from any series."""
    return s - clim.reindex(doy365(s.index)).to_numpy()


def doy_anomaly(s, window=31, ref=None):
    """Deseasonalised series: value minus its smoothed day-of-year climatology.

    The climatology is fitted on `ref` (default: `s` itself). Pass a training slice as `ref` to avoid leakage.
    """
    return apply_climatology(s, doy_climatology(s if ref is None else ref, window))


def week_index(index):
    """1..52 calendar-week index for weekly (W-SUN) dates: day-of-year of the week's Thursday, in 7-day blocks."""
    thu = pd.DatetimeIndex(index) - pd.Timedelta(days=3)
    return np.minimum((doy365(thu) - 1) // 7 + 1, 52)


def pairwise_granger(df, pairs, maxlag=7):
    """p-values (SSR F-test) for 'cause -> effect' at each lag 1..maxlag."""
    rows = {}
    for cause, effect in pairs:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = grangercausalitytests(df[[effect, cause]].dropna(), maxlag=maxlag)
        rows[f"{cause} → {effect}"] = {lag: res[lag][0]["ssr_ftest"][1] for lag in range(1, maxlag + 1)}
    out = pd.DataFrame(rows).T
    out.columns.name = "lag (days)"
    return out
```

### src/aqi.py
```python
"""CPCB (India) National AQI PM2.5 sub-index bands for 24-hour average PM2.5 (µg/m³).

The official AQI is the MAXIMUM sub-index over all pollutants, so a band here is a "PM2.5 sub-index band", not the AQI.
"""
import numpy as np
import pandas as pd

# (category, upper PM2.5 bound in µg/m³, AQI range, CPCB colour)
CPCB_PM25_BANDS = [
    ("Good",         30,     "0–50",    "#00B050"),
    ("Satisfactory", 60,     "51–100",  "#92D050"),
    ("Moderate",     90,     "101–200", "#E6C200"),
    ("Poor",         120,    "201–300", "#FF9900"),
    ("Very Poor",    250,    "301–400", "#FF0000"),
    ("Severe",       np.inf, "401–500", "#C00000"),
]
CATEGORIES = [b[0] for b in CPCB_PM25_BANDS]


def pm25_category(pm25):
    """Map PM2.5 concentration(s) to the CPCB AQI category name."""
    edges = [-np.inf] + [b[1] for b in CPCB_PM25_BANDS]
    return pd.cut(pd.Series(pm25), bins=edges, labels=CATEGORIES, right=True)


def band_edges():
    """(category, lower, upper, colour) tuples for shading plots."""
    lower = 0
    out = []
    for name, upper, _, colour in CPCB_PM25_BANDS:
        out.append((name, lower, upper, colour))
        lower = upper
    return out


def band_probabilities(mu, sd):
    """P(PM2.5 in each band) for a lognormal log-PM2.5 ~ N(mu, sd^2). Returns array (len(CATEGORIES),)."""
    from scipy.stats import norm
    edges = [b[1] for b in CPCB_PM25_BANDS[:-1]]
    cdf = np.r_[0.0, norm.cdf((np.log(edges) - mu) / sd), 1.0]
    return np.diff(cdf)
```

### src/forecast.py
```python
"""Phase 4 forecasting toolkit: models for weekly log PM2.5, expanding-window backtest, metrics, simulation.

Every model is a function `model(y_train, idx_test) -> dict(mu=log forecast, sd=log predictive sd or None, ...)`.
All selection (Fourier order K, ARMA order, trend type) happens inside the function using ONLY `y_train`.
"""
import warnings
from itertools import product

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tsa.statespace.sarimax import SARIMAX

from .aqi import CPCB_PM25_BANDS
from .tsa import week_index

H = 52
PERIOD = 365.25 / 7  # weeks per year
T0 = pd.Timestamp("2015-01-04")
WINTER = [11, 12, 1, 2]
warnings.filterwarnings("ignore")


# ── features ────────────────────────────────────────────────────────────────────────────────────────────
def fourier(idx, K):
    t = (pd.DatetimeIndex(idx) - T0).days.to_numpy() / 7.0
    cols = {}
    for k in range(1, K + 1):
        cols[f"s{k}"] = np.sin(2 * np.pi * k * t / PERIOD)
        cols[f"c{k}"] = np.cos(2 * np.pi * k * t / PERIOD)
    return pd.DataFrame(cols, index=pd.DatetimeIndex(idx))


def future_index(y_train, h=H):
    return pd.date_range(y_train.index[-1] + pd.Timedelta(weeks=1), periods=h, freq="W-SUN")


def aicc(res):
    k, n = len(res.params), res.nobs
    return res.aic + 2 * k * (k + 1) / max(n - k - 1, 1)


# ── baselines ───────────────────────────────────────────────────────────────────────────────────────────
def seasonal_naive(y, idx):
    return {"mu": y.iloc[-H:].to_numpy()[: len(idx)], "sd": None}


def _clim(y):
    wk = week_index(y.index)
    c = y.groupby(wk).mean().reindex(range(1, 53)).interpolate(limit_direction="both")
    return c


def climatology(y, idx):
    return {"mu": _clim(y).reindex(week_index(idx)).to_numpy(), "sd": None}


def clim_ar1(y, idx):
    """Weekly climatology + AR(1) on the anomalies; forecast variance grows to the anomaly variance."""
    c = _clim(y)
    a = y - c.reindex(week_index(y.index)).to_numpy()
    phi = float(np.clip((a.iloc[1:].to_numpy() * a.iloc[:-1].to_numpy()).sum() / (a.iloc[:-1] ** 2).sum(), -0.99, 0.99))
    s2 = float(np.var(a.iloc[1:].to_numpy() - phi * a.iloc[:-1].to_numpy()))
    h = np.arange(1, len(idx) + 1)
    mu = c.reindex(week_index(idx)).to_numpy() + a.iloc[-1] * phi ** h
    sd = np.sqrt(s2 * (1 - phi ** (2 * h)) / (1 - phi ** 2))
    return {"mu": mu, "sd": sd, "phi": phi}


# ── dynamic harmonic regression (Fourier + ARMA errors) ────────────────────────────────────────────────
TREND_SPECS = {  # name -> (trend arg, d)
    "const": ("c", 0),
    "linear": ("ct", 0),
    "rw": ("n", 1),  # ARIMA(p,1,q) errors: a local level that follows the data
}
PQ_GRID = [(0, 0), (1, 0), (2, 0), (1, 1), (2, 1)]


def _fit_dhr(y, K, p, q, trend):
    tr, d = TREND_SPECS[trend]
    mod = SARIMAX(y, exog=fourier(y.index, K), order=(p, d, q), trend=tr)
    return mod.fit(disp=False, maxiter=200)


def _best_by_aicc(y, trend):
    best = None
    for K, (p, q) in product(range(1, 6), PQ_GRID):
        try:
            r = _fit_dhr(y, K, p, q, trend)
            a = aicc(r)
        except Exception:  # noqa: BLE001
            continue
        if np.isfinite(a) and (best is None or a < best[0]):
            best = (a, K, p, q, r)
    return best


def select_dhr(y, inner=H):
    """Choose (K, p, q) by AICc within each trend type, then the trend type by validation on the last `inner` weeks
    of the training sample (so nothing after the training end is ever used)."""
    sub, val = y.iloc[:-inner], y.iloc[-inner:]
    scores = {}
    for trend in TREND_SPECS:
        b = _best_by_aicc(sub, trend)
        if b is None:
            continue
        _, K, p, q, r = b
        fc = r.get_forecast(inner, exog=fourier(val.index, K)).predicted_mean
        scores[trend] = float(np.abs(np.exp(val.to_numpy()) - np.exp(fc.to_numpy())).mean())
    trend = min(scores, key=scores.get)
    _, K, p, q, res = _best_by_aicc(y, trend)
    return {"trend": trend, "K": K, "p": p, "q": q, "inner_mae": scores, "res": res}


def dhr(y, idx, fixed=None):
    """Fourier + ARMA. `fixed` = dict(trend, K, p, q) skips selection."""
    sel = select_dhr(y) if fixed is None else {**fixed, "res": _fit_dhr(y, fixed["K"], fixed["p"], fixed["q"], fixed["trend"])}
    res = sel["res"]
    f = res.get_forecast(len(idx), exog=fourier(idx, sel["K"]))
    return {"mu": f.predicted_mean.to_numpy(), "sd": np.sqrt(f.var_pred_mean.to_numpy()), "res": res, "spec": sel}


def dhr_fixed(trend, K=3, p=1, q=0):
    return lambda y, idx: dhr(y, idx, fixed={"trend": trend, "K": K, "p": p, "q": q})


# ── SARIMA benchmarks ───────────────────────────────────────────────────────────────────────────────────
def sarima(order, sorder, trend="n"):
    def _m(y, idx):
        res = SARIMAX(y, order=order, seasonal_order=sorder, trend=trend).fit(disp=False, maxiter=200)
        f = res.get_forecast(len(idx))
        return {"mu": f.predicted_mean.to_numpy(), "sd": np.sqrt(f.var_pred_mean.to_numpy()), "res": res}
    return _m


sarima_D1 = sarima((1, 0, 1), (0, 1, 1, 52))
sarima_D0 = sarima((1, 0, 1), (1, 0, 0, 52), trend="c")


# ── Linear Regression and small LSTM baselines ─────────────────────────────────────────────────────────
def _design(idx, K, t0):
    X = fourier(idx, K)
    X["t"] = ((pd.DatetimeIndex(idx) - t0).days.to_numpy() / 365.25)
    return X


def linreg(y, idx, K=3):
    from sklearn.linear_model import LinearRegression
    X = _design(y.index, K, y.index[0])
    m = LinearRegression().fit(X, y.to_numpy())
    sd = float(np.std(y.to_numpy() - m.predict(X), ddof=X.shape[1] + 1))
    return {"mu": m.predict(_design(idx, K, y.index[0])), "sd": np.full(len(idx), sd)}


def lstm(y, idx, lag=8, hidden=16, epochs=300, seed=0):
    """Tiny recursive one-step LSTM on weekly log-anomalies (vs training climatology) + calendar features."""
    import torch
    torch.manual_seed(seed)
    np.random.seed(seed)
    c = _clim(y)
    a = (y - c.reindex(week_index(y.index)).to_numpy()).to_numpy()
    sd_a = a.std()
    z = a / sd_a

    def cal(ix):
        w = week_index(ix)
        return np.c_[np.sin(2 * np.pi * w / 52), np.cos(2 * np.pi * w / 52)]

    C = cal(y.index)
    X, Y = [], []
    for i in range(lag, len(z)):
        X.append(np.c_[z[i - lag:i], C[i - lag:i]])
        Y.append(z[i])
    X = torch.tensor(np.array(X), dtype=torch.float32)
    Y = torch.tensor(np.array(Y), dtype=torch.float32)

    class Net(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.rnn = torch.nn.LSTM(3, hidden, batch_first=True)
            self.out = torch.nn.Linear(hidden, 1)

        def forward(self, x):
            o, _ = self.rnn(x)
            return self.out(o[:, -1]).squeeze(-1)

    net = Net()
    opt = torch.optim.Adam(net.parameters(), lr=0.01, weight_decay=1e-3)
    for _ in range(epochs):
        opt.zero_grad()
        loss = torch.mean((net(X) - Y) ** 2)
        loss.backward()
        opt.step()
    with torch.no_grad():
        resid_sd = float(torch.std(net(X) - Y)) * sd_a
        hist = list(z[-lag:])
        Cf = cal(idx)
        Cp = cal(y.index[-lag:])
        preds = []
        for j in range(len(idx)):
            cc = np.vstack([Cp, Cf[:j + 1]])[-lag:] if j else Cp
            xin = torch.tensor(np.c_[hist[-lag:], cc][None], dtype=torch.float32)
            nxt = float(net(xin))
            preds.append(nxt)
            hist.append(nxt)
    mu = c.reindex(week_index(idx)).to_numpy() + np.array(preds) * sd_a
    return {"mu": mu, "sd": np.full(len(idx), resid_sd)}


# ── metrics ─────────────────────────────────────────────────────────────────────────────────────────────
def metrics(actual, mu, sd=None, dates=None, level=0.95):
    """Raw-scale MAE uses the median forecast exp(mu); RMSE uses the mean forecast exp(mu + sd^2/2)."""
    actual, mu = np.asarray(actual, float), np.asarray(mu, float)
    med = np.exp(mu)
    mean = np.exp(mu + (0.5 * np.asarray(sd) ** 2 if sd is not None else 0))
    out = {"MAE": np.abs(actual - med).mean(), "RMSE": np.sqrt(((actual - mean) ** 2).mean()),
           "logMAE": np.abs(np.log(actual) - mu).mean(), "bias": (actual - med).mean()}
    if dates is not None:
        m = pd.DatetimeIndex(dates).month.isin(WINTER)
        out["MAE_winter"] = np.abs(actual - med)[m].mean()
        out["MAE_other"] = np.abs(actual - med)[~m].mean()
    if sd is not None:
        z = stats.norm.ppf(0.5 + level / 2)
        lo, hi = np.exp(mu - z * np.asarray(sd)), np.exp(mu + z * np.asarray(sd))
        out["coverage"] = float(((actual >= lo) & (actual <= hi)).mean())
        a = 1 - level
        out["winkler"] = float(np.mean((hi - lo) + (2 / a) * (lo - actual) * (actual < lo) + (2 / a) * (actual - hi) * (actual > hi)))
        out["width"] = float((hi - lo).mean())
    return {k: float(v) for k, v in out.items()}


# ── backtest ────────────────────────────────────────────────────────────────────────────────────────────
ORIGINS = {2017: "2016-12-25", 2018: "2017-12-31", 2019: "2018-12-30"}


def _run_one(fn, tr, idx):
    import os
    os.environ["OMP_NUM_THREADS"] = "1"
    out = fn(tr, idx)
    spec = out.get("spec")
    if spec is not None:
        out["spec"] = {k: v for k, v in spec.items() if k != "res"}
    out.pop("res", None)
    return out


def backtest(y, raw, models, origins=ORIGINS, h=H, n_jobs=8, verbose=True):
    """Expanding-window backtest (each model refit, and re-selected, at each origin using only data up to it).

    Returns (metrics table, forecasts[fold][model] dict with mu, sd, idx, actual, spec)."""
    from joblib import Parallel, delayed
    tasks = []
    for fold, origin in origins.items():
        tr = y.loc[:origin]
        idx = future_index(tr, h)
        assert idx[0] > tr.index[-1] and idx.isin(y.index).all()
        for name, fn in models.items():
            tasks.append((fold, name, tr, idx, fn))
    outs = Parallel(n_jobs=n_jobs)(delayed(_run_one)(fn, tr, idx) for _, _, tr, idx, fn in tasks)
    rows, fcs = [], {}
    for (fold, name, tr, idx, _), out in zip(tasks, outs):
        act = raw.loc[idx].to_numpy()
        fcs.setdefault(fold, {})[name] = {**out, "idx": idx, "actual": act}
        rows.append({"fold": fold, "model": name, "n_train": len(tr), **metrics(act, out["mu"], out.get("sd"), idx)})
        if verbose:
            print(fold, name, round(rows[-1]["MAE"], 1))
    return pd.DataFrame(rows), fcs


def block_bootstrap_diff(e_a, e_b, block=8, n=4000, seed=0):
    """Mean of (e_a - e_b) with a moving-block bootstrap 95% CI (e = absolute errors, concatenated over folds)."""
    d = np.asarray(e_a) - np.asarray(e_b)
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(len(d) / block))
    starts = np.arange(len(d) - block + 1)
    means = np.array([np.concatenate([d[s:s + block] for s in rng.choice(starts, nb)])[:len(d)].mean() for _ in range(n)])
    return float(d.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def hln_dm(e_a, e_b, h=1, power=1):
    """Harvey-Leybourne-Newbold modified Diebold-Mariano test (two-sided) on loss |e|^power."""
    d = np.abs(e_a) ** power - np.abs(e_b) ** power
    n = len(d)
    dbar = d.mean()
    g0 = np.mean((d - dbar) ** 2)
    var = g0 + 2 * sum((1 - k / h) * np.mean((d[k:] - dbar) * (d[:-k] - dbar)) for k in range(1, h)) if h > 1 else g0
    dm = dbar / np.sqrt(var / n)
    dm *= np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return float(dm), float(2 * stats.t.sf(abs(dm), n - 1))


# ── diagnostics ─────────────────────────────────────────────────────────────────────────────────────────
def resid_diagnostics(res, lags=(10, 26, 52), model_df=None):
    """Residual checks that drop the diffuse-initialisation residuals (`loglikelihood_burn`)."""
    burn = int(res.loglikelihood_burn)
    e = pd.Series(np.asarray(res.resid)).iloc[max(burn, 0):]
    mdf = model_df if model_df is not None else int(sum(1 for n in res.param_names if n.startswith(("ar.", "ma."))))
    lb = acorr_ljungbox(e, lags=list(lags), model_df=mdf, return_df=True)
    arch = het_arch(e, nlags=4)
    jb = stats.jarque_bera(e)
    return {"burn": burn, "n_resid": len(e), "resid_sd": float(e.std()),
            **{f"LB_p_lag{l}": float(lb.loc[l, "lb_pvalue"]) for l in lags},
            "ARCH4_p": float(arch[1]), "JB_p": float(jb.pvalue)}


# ── simulation and PM2.5-band conversion ───────────────────────────────────────────────────────────────
def simulate_paths(res, idx, exog=None, n=5000, seed=1):
    """Simulated future log paths, shape (len(idx), n). Anchored at the end of the fitted sample."""
    np.random.seed(seed)
    sim = res.simulate(nsimulations=len(idx), repetitions=n, anchor="end", exog=exog)
    return np.asarray(sim).reshape(len(idx), n)


def band_edges():
    return [b[1] for b in CPCB_PM25_BANDS[:-1]]  # 30, 60, 90, 120, 250


def week_offsets_by_month(daily_pm25):
    """Pool of log(daily) - log(weekly mean) offsets, by calendar month of the day (training data only)."""
    d = daily_pm25.dropna()
    wk_end = d.index + pd.to_timedelta((6 - d.index.weekday) % 7, unit="D")
    wmean = d.groupby(wk_end).transform("mean")
    n = d.groupby(wk_end).transform("count")
    off = (np.log(d) - np.log(wmean))[n == 7]
    return {m: off[off.index.month == m].to_numpy() for m in range(1, 13)}


def daily_band_days(paths, idx, pools, year, seed=2):
    """Monte-Carlo days per PM2.5 band per month for the calendar `year`.

    paths: weekly log-mean paths (len(idx), n_paths) for weeks `idx` (W-SUN). Each day gets its week's path value plus a
    resampled within-week offset from the matching month pool. Returns array (n_paths, 12, 6) of days per band.
    """
    rng = np.random.default_rng(seed)
    days = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
    wk_end = days + pd.to_timedelta((6 - days.weekday) % 7, unit="D")
    pos = pd.Index(idx).get_indexer(wk_end)
    keep = pos >= 0
    days, pos = days[keep], pos[keep]
    n = paths.shape[1]
    vals = np.empty((len(days), n))
    for i, d in enumerate(days):
        vals[i] = np.exp(paths[pos[i]] + rng.choice(pools[d.month], size=n))
    cat = np.searchsorted(band_edges(), vals, side="left")  # 0..5 (<=edge -> lower band)
    out = np.zeros((n, 12, 6))
    for m in range(12):
        sel = days.month == m + 1
        for b in range(6):
            out[:, m, b] = (cat[sel] == b).sum(axis=0)
    return out


def monthly_mean_paths(paths, idx, year):
    """Monthly mean PM2.5 (raw scale) per simulated path, weighting weekly means by days falling in each month."""
    days = pd.date_range(f"{year}-01-01", f"{year}-12-31", freq="D")
    wk_end = days + pd.to_timedelta((6 - days.weekday) % 7, unit="D")
    pos = pd.Index(idx).get_indexer(wk_end)
    keep = pos >= 0
    days, pos = days[keep], pos[keep]
    raw = np.exp(paths)
    out = np.full((12, paths.shape[1]), np.nan)
    for m in range(12):
        sel = days.month == m + 1
        if sel.any():
            out[m] = raw[pos[sel]].mean(axis=0)
    return out
```


=================== FILE: 03_phase2_eda_results.md ===================
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


=================== FILE: 04_phase3_var_granger_results.md ===================
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


=================== FILE: 05_phase4_forecasting_results.md ===================
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


=================== FILE: 06_review_log.md ===================
# 06 What three earlier reviews claimed and what we found

# Review responses: every claim checked against the data

Three independent reviews of the project (Claude: `gemini_context/06_critical_review.md` before the final rewrite; Gemini: `docs/reviews/Geminiplan.md`; GPT: `docs/reviews/gpt.md`) raised the points below.
Each was **re-checked on the data** before acting. "Where" gives the notebook/file that now holds the evidence. Verdicts: **Accepted** (bug or valid point, fixed), **Partly** (right idea, wrong detail), **Rejected** (checked, not true), **Noted** (limit we state rather than fix).

## A. Bugs and statistical errors

| # | Claim (source) | Verdict | Evidence and fix | Where |
|---|---|---|---|---|
| A1 | Ljung-Box p≈0 in the SARIMA draft is an artifact of the 52 diffuse initial residuals (all three) | **Accepted** | `loglikelihood_burn = 52`; with them p = 0 at lag 10, without them p = 0.49 (lag 10), 0.10 (lag 26). **Lag 52 is p = 0.016** (GPT asked for it; the first reviews missed it). `resid_diagnostics()` drops the burn-in | nb04 §3, `src/forecast.py` |
| A2 | Seasonal MA −0.988 means over-differencing (all) | **Accepted, strengthened** | Coefficient −0.988 with SE ≫ 1 (not identified). The D=1 SARIMA also collapses in the 2-year-training fold (MAE 54) | nb04 §3 |
| A3 | D=0 candidates were fit with no constant (`trend='n'`) (Gemini) | **Accepted, effect overstated** | With a constant the D=0 validation MAE falls 39.7 → 30.6 but D=1 still wins on that fold; SARIMA D=0 with constant is still the worst non-LSTM model in the final backtest (44). Fixed: D=0 benchmark uses `trend='c'` | `src/forecast.py` |
| A4 | All 8 misses of the 2019 interval are below the lower bound, so it is level bias, not width (Gemini, GPT) | **Accepted** | 8 below, 0 above; mean log error −0.18. Calibration rule re-centres only if the bias has the same sign and |z|>0.5 in both calibration folds (it did not: −0.66 and −0.45 → below threshold 0.5 in 2018), and rescales spread by season | nb04 §4 |
| A5 | Re-anchoring the level gives 94.2% coverage (Gemini) | **Rejected (number)** | Tested: it gives 90.4% (MAE 25.5). Seasonal scaling from earlier folds gives 96% on 2019 | nb04 §4 |
| A6 | ISO-week folding shifts all of 2016 (Gemini) | **Partly** | Only the week ending 2016-01-03 is ISO week 53 and was merged into week 52. Replaced by one consistent index `week_index()` (Thursday's day-of-year, leap-aware) used everywhere | `src/tsa.py` |
| A7 | Leap years: day-of-year capped at 365 mis-aligns Feb 29 onwards (GPT) | **Accepted (minor)** | `doy365()` maps Feb 29 to day 59 and shifts later days; all anomalies recomputed | `src/tsa.py`, nb02/03 |
| A8 | Shock bins are same-day values and suffer a Jensen bias (Gemini) | **Rejected** | The code takes `exp(mean of the log change from day t−1 to t+1) − 1`: not same-day, no Jensen bias. Wording on the slide is now explicit ("day t+1 vs day t−1") | `make_figures.py`, deck |
| A9 | Weekly R² 0.139 vs 0.140 compares non-nested models (Gemini) | **Accepted** | Replaced by a nested comparison: lagged PM2.5 alone R² 0.134 vs + lagged weather 0.139 (ΔR² = 0.005), joint HAC Wald p = 0.51 | nb03 §9, `weekly_lag_nested.csv` |
| A10 | "p < 1e-10 in every specification" is false (GPT) | **Accepted** | With the rain control humidity p = 2.8e-8 (3e-11 → 7e-8 with rain and temperature). Text now quotes the right p-values | nb03, deck |
| A11 | "Significant at every lag 1–7" is a joint test at each lag order, not per-lag significance (GPT) | **Accepted** | Wording changed to "joint tests at every lag order 1–7"; per-lag-order Wald table saved | `granger_hac_by_lag.csv` |
| A12 | The slides quote reverse-direction p-values (0.04, 0.016) that exist nowhere in `results/` (my review) | **Accepted** | Now saved: PM2.5 → wind is significant at lag orders 1–2 (p = 0.038, 0.015) and not from 3 on | `granger_hac_by_lag.csv` |
| A13 | A PM2.5 band is not the official AQI, which is the max sub-index (GPT) | **Accepted** | Everything relabelled "PM2.5 sub-index band"; `aqi.py` docstring and slides updated | deck, `src/aqi.py` |
| A14 | The lognormal mean correction should be horizon-specific (GPT) | **Accepted** | RMSE uses `exp(mu_h + sd_h²/2)`; MAE uses the median | `src/forecast.py` |
| A15 | A plain Diebold-Mariano on one 52-step path is invalid (GPT) | **Accepted** | 52-week comparisons use a moving-block bootstrap of paired errors over three origins and say "indistinguishable" when the CI contains 0. HLN-DM is used only for the genuine one-step comparison | nb04 §2, §5 |
| A16 | Headline STL strength / Box-Cox / drift use test-period data (my review, Gemini, GPT) | **Accepted** | Headline F_S = 0.90 on 2015–2018 weeks (full sample 0.89); Box-Cox λ train ≈ 0.10 (full 0.045), still ≈ log. Full-sample values kept alongside | nb02 |
| A17 | The 2019 test-year was used to pick the order via 2018 validation overlap (all) | **Accepted** | Selection (K, p, q, level treatment) happens inside each training window with an inner validation year; nothing after the origin is used. Asserted in code (`idx[0] > train end`) | `src/forecast.py` |
| A18 | `__pycache__` tracked, no .gitignore, notebook 04 never executed (my review, GPT) | **Accepted** | `.gitignore`, untracked caches, all four notebooks executed with saved outputs | repo |

## B. Interpretation and over-claims

| # | Claim | Verdict | Evidence and fix |
|---|---|---|---|
| B1 | "Weather drives PM2.5" overstates Granger causality (all) | **Accepted** | Reworded to "robust predictive association" everywhere; still not proof of a physical cause |
| B2 | Omitted variables: temperature is available but unused (Gemini, GPT) | **Accepted** | Temperature control added: wind p 2.5e-18, humidity p 1.4e-9 (still significant); boundary-layer height not available in the data (stated as a limit) |
| B3 | KPSS rejection for the anomaly shows drift, not a unit root; test a trend / training-only climatology (Gemini, GPT) | **Accepted** | KPSS statistic on the anomaly: 0.90 (2015–18) and 2.0 (2015–19) vs 0.46 critical: a real level drift. Granger results are unchanged with a linear trend (p 5.5e-20) and with a training-only climatology (p 6.9e-20) |
| B4 | Humidity effect is monsoon-specific (Gemini, my review) | **Rejected as a predictive claim** | Season-interaction test: monsoon × humidity p = 0.20 (not significant); winter × wind p = 0.03. Wind and humidity are significant in *both* seasons (p ≤ 5e-4). Only the *correlation* pattern differs by season |
| B5 | Reverse PM2.5 → wind reflects synoptic stagnation (Gemini) | **Noted** | Plausible but untested (no boundary-layer data); stated as a possibility only |
| B6 | Cholesky orderings: use generalised IRFs and bands (GPT) | **Accepted** | GIRF day-1: wind −12.0%, humidity −5.2%, inside/near the Cholesky range (−6% to −12%, −4% to −7%); bands saved for both orderings |
| B7 | Weather-first ordering is "the physically preferred" one (Gemini) | **Rejected as a claim** | Daily means share the same 24 h; we report the range and call it identification-dependent |
| B8 | The 2016–19 decline may be a monitor-network artifact (GPT, Gemini, my review) | **Tested** | Stations reporting: 10, 8, 17, 37, 37. But a fixed 6-station panel falls ≈ 20%, all stations ≈ 25%, the weather-adjusted city series ≈ 18% (2016 → 2019): mostly real, with caveats (thin 2017 panel) | nb02 §8 |
| B9 | The "same-week weather" 1-week SARIMAX is an upper bound (all) | **Accepted** | Three variants: lagged weather, last 3 days, same-week (oracle). Result: lagged −2.4%, last-3-days +0.7%, oracle +6.9% (HLN-DM p = 0.07) |
| B10 | Forecast date: data stop in 2020, so "next 12 months" is not current (GPT Q16) | **Accepted (Option A)** | Historical forecasting study: backtests for 2017–19 and a 2020 outlook made from data to Dec 2019, validated by the Jan–Jun 2020 actuals. We do not claim a current advisory |
| B11 | Weekly means cannot give daily AQI categories (all) | **Accepted** | Weekly paths + within-week daily offsets give expected days per PM2.5 band; validated on 2019 (all 12 months inside the interval, but Poor+ share over-predicted: 55% vs 45%) |
| B12 | Conformal prediction is not justified with this little data (GPT) | **Accepted** | Not used; simple season scaling from earlier folds, checked on a later year |
| B13 | GARCH is not needed on weekly residuals (all) | **Accepted** | ARCH-LM(4) on weekly residuals p = 0.87 |
| B14 | TBATS / Prophet suggested (my review) vs "too heavy" (Gemini) | **Partly** | Neither run. Fourier + ARMA is the parsimonious equivalent; adding them would not change the conclusion that the calendar dominates |

## C. New findings from the rework (not raised by any review)

1. The pre-declared headline model is **not** significantly better than climatology (2018–19 MAE 24.6 vs 24.8); the variant with a linear trend is better on 2018–19 (CI excludes 0) but not over all three origins and was not chosen in advance. We report both and claim neither.
2. In the 2-year-training fold (2017) SARIMA D=1 collapses (MAE 54 vs 31 for climatology): another reason to avoid unnecessary seasonal differencing.
3. The calibrated 2020 forecast intervals are *narrower* than those for 2019 (scale factors 1.09/0.95 vs 1.33/1.42): the calibration is fold-dependent, which we report instead of hiding.
4. The 2020 forecast correctly flags the lockdown: March–May means fall below the 95% interval; PM2.5 was ≈ 43% below the no-lockdown forecast (≈ 38% after weather adjustment).
5. The pipeline over-predicts the share of Poor-or-worse days in 2019 (55% vs 45%): the level bias noted above carries into the band table.


=================== FILE: 07_audit_questions.md ===================
# 07 Audit questions for GPT
Answer each concretely (numbers, named tests, alternative code). Say where you disagree with file 06.
1. Is anything in the *design* of the backtest still leaky (selection of K, p, q, level; calibration folds; the pre-declared headline)? Is declaring the headline model "before looking" credible given the code history?
2. The pre-declared headline is not significantly better than climatology, and a linear-trend variant is better on 2018-19 only. Is our wording ("as good, more robust, calibrated") honest and sufficient? What additional test would settle it with 5.5 years of data?
3. Is the calibration rule (season scale with shrinkage k=26; re-centre only if same sign and |mean z|>0.5 in both calibration folds) defensible? The 2019 vs 2020 scale factors differ (1.33/1.42 vs 1.09/0.95); what does that imply for the 2020 intervals?
4. Is the daily-band conversion (weekly simulated paths + resampled within-week log offsets by calendar month) statistically sound? It over-predicted Poor-or-worse days in 2019 (55% vs 45%): is that just level bias or a flaw in the offset model?
5. Station check: is a fixed 6-station panel (>=60 days in each year) a fair test of whether the decline is real? What would you do instead with the data in hand?
6. VAR/Granger: any remaining error in HAC implementation, the season-interaction test, the generalised IRF (Psi_h Sigma e_j / sqrt(sigma_jj)), or the weekly nested test?
7. Lockdown case study: is a % gap to a simulated no-lockdown path with an oracle-weather variant a valid decomposition? What would a reviewer attack?
8. Which statements in the deck/script (file 08) are still over-claims?
9. List the top 5 remaining weaknesses ranked by how much they could change a conclusion, with the fix for each that could be done in two days.
10. Anything we missed.
Format: (i) agreements, (ii) disagreements with reasons, (iii) new issues, (iv) numbered answers, (v) prioritised fixes.


=================== FILE: 08_presentation_and_QA.md ===================
# Presentation script and Q&A

Deck: `slides/Delhi_PM25_presentation.pdf` (21 slides + 5 backup; source `slides/beamer/main.tex`). Every number on a slide comes from `results/` and is re-derived by `slides/beamer/verify_numbers.py` (65 checks). The full report is `report/report.pdf`; the log of what three reviewers claimed and what we found is `docs/REVIEW_RESPONSES.md`.

## One-line pitch
"Delhi's PM2.5 repeats a huge winter peak. Weather predicts it for about a week, but not for a year. A smooth seasonal model forecasts the year ahead about as well as the calendar average does, and we show honestly where it is and is not better."

## What to say on each slide

**1. Title.** "We forecast Delhi's PM2.5. First: does weather explain it, and over what horizon? Then: how well can we forecast a week and a year ahead?"

**2. Problem.** "PM2.5 is particles under 2.5 micrometres. 52 percent of days from 2015 to 2020 were Poor or worse on India's PM2.5 band; winter averages 213 against 48 in the monsoon, 4.4 times. Note: the official AQI takes the worst pollutant; we use only the PM2.5 band."

**3. What we built.** "Q1 explain, Q2a next week, Q2b next 12 months. All three are answered. Weather has a short memory, so the 12-month model uses no weather."

**4. Data.** "CPCB PM2.5 through Kaggle, ERA5 weather (a reanalysis, observed not forecast) through Open-Meteo. 2,009 days, 2 values interpolated. Daily data for causality, weekly means for forecasting, validated on three rolling origins."

**5. STL.** "Seasonal strength 0.90 on the training years: the cycle dominates."

**6-7. Log and volatility.** "Spread grows with the level, so we model the log: monthly spread 7.9x becomes 1.3x, skewness 1.70 becomes -0.08. Some volatility clustering remains in the daily data; on the weekly forecast residuals ARCH is absent."

**8-9. Stationarity.** "ADF and KPSS have opposite null hypotheses; both are consistent with stationarity for log PM2.5, so d = 0. KPSS on the raw level hides a slow decline under the cycle: once the cycle is removed PM2.5 falls about 25 percent from 2016 to 2019. A D=1 SARIMA's seasonal MA coefficient is -0.988 with a huge standard error: the seasonal difference is not needed, so we model the cycle with Fourier terms."

**10. Granger.** "Model A uses past PM2.5; model B adds past wind and humidity; a Wald test with robust errors asks if B is better. Joint tests at every lag order 1 to 7 reject, also with rain and temperature controls. Reverse: absent for humidity, weak for wind at lag orders 1 and 2. This is predictive, not proof of a physical cause."

**11. Shock.** "A shock is the unpredictable part of today's wind. Binned by size, PM2.5 on day t+1 is 24 percent lower than on day t-1 after an unexpectedly windy day."

**12. Impulse response.** "A 1-SD wind shock cuts PM2.5 by 6 to 12 percent next day, humidity 4 to 7; the range is the variable ordering; the ordering-free generalised response sits inside it. Fades in about a week. Last week's weather adds nothing at the weekly scale."

**13. Established.** Read the bullets; answer to Q1: robust predictive association over days.

**14. Models and design.** "Benchmarks, a Fourier-plus-ARMA family, SARIMA, linear regression and a tiny LSTM. Three expanding-window origins; everything re-selected inside each window. We declared the headline model before looking at the test years."

**15-16. Backtest.** "Climatology is hard to beat. In 2019 the selected model scores 25.7 against 27.8; SARIMA D=1 27.5 but 54 in the 2017 fold. Seasonal naive, SARIMA D=0 and the LSTM are clearly worse. The linear-trend variant looks better in 2018-19 but not over all three origins and it was not our pre-declared choice, so we do not claim it. With three origins we cannot rank the rest."

**17. Diagnostics.** "The earlier draft's Ljung-Box p of zero was a bug: the first 52 residuals of a D=1 model are initialisation values. Without them the residuals pass lags 10 and 26 (lag 52: p = 0.016). Intervals: 90 percent of 2019 weeks covered, all misses on the low side; seasonal rescaling from earlier years gives 96 percent. We re-centre only if the bias is consistent; it was not."

**18. One week ahead.** "Last week's weather: no gain (-2.4 percent). Last three days: +0.7. The same week's weather, which no one knows in advance, +6.9 percent. Weather is explanatory but a weak forecasting input."

**19. Outlook for 2020.** "Fitted on 2015-2019 only, simulated paths, converted to daily PM2.5 bands. Validated on 2019: all 12 monthly means inside the interval, but the Poor-or-worse share is over-predicted, 55 against 45 percent: the level bias. In 2020, January and February fall inside the interval; March to May fall below it."

**20. Lockdown.** "Weeks from 29 March to 31 May were about 43 percent below the no-lockdown forecast, 38 percent after adjusting for the actual wind and humidity: most of the drop is not weather. Descriptive; relies on the level of the forecast."

**21. Established and limits.** Read both cards.

**Backups:** glossary; robustness of Granger and IRF orderings; PM2.5 by month; station check (is the decline real?); outlook table.

## Likely questions and answers

**Does weather cause PM2.5?** We claim a robust *predictive* association: after removing the seasonal cycle, lagged wind and humidity improve prediction of PM2.5 in every specification. Boundary-layer height, stubble burning and fireworks are unmeasured, so this is not a causal proof.

**Is humidity only important in the monsoon?** Not as a predictive effect. Both variables are significant in winter and in the monsoon (p <= 5e-4); the monsoon-by-humidity interaction is not significant (p = 0.20). The correlation pattern in the EDA differs by season; the Granger effect does not detectably differ.

**Why are the p-values so small? Aren't they inflated?** The plain F-tests (1e-29) assume independent errors, which is false; we use HAC errors (1e-20 to 1e-11) and a rain/temperature control (down to 7e-8). We quote them as "significant", not as precise numbers.

**Why does the reverse PM2.5 -> wind appear at lags 1-2?** Possibly a shared stagnation regime (low wind and high PM2.5 on consecutive days). We have no boundary-layer data, so we call it unproven. It vanishes at lag order 3 and above and is absent in the full VAR F-test.

**Why Fourier + ARMA instead of SARIMA?** A SARIMA with a seasonal difference spends 52 of 209 points on differencing, and its seasonal MA hits -0.988 with a very large standard error (unidentified); it collapses in the 2017 fold (MAE 54). Fourier terms use 10 parameters for the yearly cycle.

**Is the Fourier model really better than climatology?** The pre-declared model is not significantly better (2018-19 MAE 24.6 vs 24.8). A linear-trend variant is better on 2018-19 but not over all three origins and we did not choose it in advance. Our message is "as good, more robust, with calibrated uncertainty", not "better".

**Why is the LSTM so bad?** 209 weekly points, recursive 52-step forecast: it can only learn the mean cycle and drifts. It is a small-data negative result, not a statement about deep learning in general.

**Is the decline over 2016-2019 real or a change in monitors?** Both are possible: stations reporting rose from 10 and 8 to 37. A fixed panel of six long-running stations still falls about 20 percent (all stations 25, weather-adjusted 18). Mostly real, with caveats: the panel is small and thin in 2017.

**What does the "monthly outlook" mean? Is it the AQI?** It is a PM2.5 sub-index band outlook: the official AQI is the maximum over pollutants. Weekly paths plus a within-week daily offset give expected days per band; validated on 2019.

**Why didn't you re-centre the forecast for the 2019 bias?** The bias had the same sign in both calibration years (-0.66 and -0.45 SD) but the smaller one is below our pre-set 0.5 SD threshold; we decided the rule before seeing 2019 and report the bias rather than tune it.

**Why is the 2020 interval narrower than 2019's?** The calibration scale factors come from the two preceding folds and differ by year (1.33/1.42 vs 1.09/0.95): calibration itself is uncertain with this little data.

**Why not a Diebold-Mariano test for the 52-week comparison?** The 52 errors are one forecast path (strongly dependent), not 52 replications; we use a block bootstrap over three origins and say "indistinguishable". DM (HLN) is used only for the genuine one-step comparison.

**Did you use the test year to choose anything?** No: the Fourier order, ARMA order and level treatment are chosen inside each training window (inner validation on its last year). The earlier draft chose D on 2018 after an in-sample order search; that overlap is gone. Headline STL / Box-Cox are on the training years.

**What was wrong with the draft?** (1) Ljung-Box on the 52 initial residuals; (2) no constant in the D=0 model; (3) full-sample statistics quoted as headline; (4) wording ("drives", "p<1e-10 everywhere", "AQI"); (5) a weekday index that merged ISO week 53; (6) leap-year day-of-year. All fixed; see `docs/REVIEW_RESPONSES.md`.

**Why is the forecast for 2020 and not for the next 12 months from today?** Our data end in July 2020; a current advisory would need newer, consistently monitored data. This is a historical forecasting study with a real out-of-sample check (Jan-Jun 2020).

## Numbers to remember
- 2,009 days; 52% Poor or worse; winter 213 vs monsoon 48 (4.4x); STL strength 0.90 (training), 0.89 (full)
- Log: skew 1.70 -> -0.08; monthly spread 7.9x -> 1.3x; drift about -25% (2016 -> 2019)
- Granger (HAC, 4 lags): wind p ~ 6e-20, humidity ~ 4e-11 (with rain+temperature: 9e-18, 7e-8); IRF day 1: wind -6 to -12%, humidity -4 to -7%; FEVD 6-30%
- Backtest MAE 2017/2018/2019: Fourier+ARMA 31.5/23.4/25.7; climatology 31.0/21.8/27.8; SARIMA D=1 53.8/21.1/27.5
- Coverage 2019: 90% raw, 96% calibrated; one week ahead: -2.4% / +0.7% / +6.9% (oracle)
- Lockdown: -43% (95% -52 to -32), weather-adjusted -38%
