
=================== FILE: 00_START_HERE.md ===================
# START HERE: briefing for GPT

You are being given the full context of a university time-series project so you can act as a **critical reviewer / advisor**.
You cannot open the original zip, so everything you need is in these 9 text files (the original project is not needed).

## Your role
1. Read all files in order. Do not start giving opinions until you have read file 06 (critical review) and 07 (open questions).
2. Give an independent opinion: where do you agree or disagree with the review in 06? What did the authors (and the previous reviewer) miss?
3. Answer the questions in 07, with concrete recommendations (model choices, tests, fixes), and flag anything statistically wrong.
4. Be specific and numerical where possible. If you disagree with a number or method, say why.

## Project in 5 lines
- MATH F428 Time Series Analysis course project, BITS Pilani Goa. Authors: Kushagra Singh, Yatin JM, Aryan Choudhary.
- City: Delhi. Variable: daily PM2.5 (CPCB monitors, via Kaggle) 2015-01-01 to 2020-07-01, plus ERA5 weather (wind, humidity, temp, rain).
- Phases 1-3 are DONE and presented: data cleaning, EDA (seasonality, log transform, stationarity), VAR + Granger causality + impulse responses.
- Phase 4 (NEXT, only a draft exists): SARIMA(X) forecasting of weekly log PM2.5, baselines (seasonal naive, climatology, Linear Regression, LSTM), final 12-month forecast with 95% intervals and a monthly AQI advisory table.
- Design decision from phases 1-3: weather only matters for days, so the 12-month model uses NO weather inputs.

## File index (read in this order)
| File | Content |
|---|---|
| 00_START_HERE.md | this file |
| 01_project_overview.md | goal, data, split, design decisions, status, repo layout, timeline |
| 02_data_and_code.md | data schema + samples, and the full source code of `src/` (cleaning, stationarity tests, plotting helpers) |
| 03_phase2_eda_results.md | EDA and stationarity: method, every number, interpretation |
| 04_phase3_var_granger_results.md | VAR / Granger / HAC / IRF / FVED: method, every number, interpretation |
| 05_phase4_sarima_draft.md | the draft SARIMA code (verbatim), its outputs, baselines table, 2019 forecast table |
| 06_critical_review.md | independent critical analysis: what is solid, what is wrong or weak, with evidence |
| 07_open_questions_for_gpt.md | the specific questions we want your opinion on |
| 08_presentation_and_QA.md | the talk script and Q&A the team prepared (shows the claims being made publicly) |

## Conventions
- "anomaly" = value minus smoothed day-of-year climatology. "HAC" = Newey-West robust errors. "IRF/FEVD" = impulse response / forecast-error variance decomposition.
- Train = 2015-2018, test = 2019 (weekly). The 2020 lockdown is excluded from the test and the VAR.
- All numbers quoted come from files in the repo's `results/` directory; they are reproduced in files 03-05.

=================== FILE: 01_project_overview.md ===================
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

=================== FILE: 02_data_and_code.md ===================
# 02 Data and source code

## Processed daily table (data/processed/delhi_daily.csv): columns and sample

Columns: Date, pm25, no2, so2, aqi, aqi_bucket, rh, wind, temp, precip, imputed, log_pm25, season  (2009 rows)

```
      Date   pm25   no2  so2   aqi aqi_bucket  rh  wind  temp  precip  imputed  log_pm25           season
2015-01-01 313.22 36.39 9.25 472.0     Severe  68   6.6  16.3     0.0    False      5.75 Winter (Nov–Jan)
2015-01-02 186.18 32.87 6.65 454.0     Severe  83   7.0  15.2     4.2    False      5.23 Winter (Nov–Jan)
2015-01-03  87.18 30.31 2.65 143.0   Moderate  84   5.1  15.6     0.1    False      4.47 Winter (Nov–Jan)
2015-01-04 151.84 36.91 4.63 319.0  Very Poor  78  10.2  14.4     0.0    False      5.02 Winter (Nov–Jan)
2015-01-05 146.60 34.92 3.33 325.0  Very Poor  74  18.7  14.3     0.0    False      4.99 Winter (Nov–Jan)
2015-01-06 149.58 37.84 3.66 318.0  Very Poor  75  12.7  15.1     0.0    False      5.01 Winter (Nov–Jan)
```

Summary statistics (daily):
```
          pm25      no2      so2       rh     wind     temp   precip
count  2009.00  2009.00  1900.00  2009.00  2009.00  2009.00  2009.00
mean    117.10    50.80    15.91    62.13     9.38    24.50     1.86
std      82.92    22.69     7.97    17.46     3.17     6.94     5.52
min      10.24    10.63     2.34    17.00     3.20     6.70     0.00
25%      57.08    33.90    10.34    51.00     7.00    18.40     0.00
50%      94.49    47.15    14.46    65.00     8.90    26.60     0.00
75%     152.99    63.57    19.72    75.00    11.20    29.70     0.70
max     685.36   162.50    71.56    95.00    24.30    37.90    75.40
```

## Weekly table (data/processed/delhi_weekly.csv): columns and sample

Columns: Date, pm25, no2, so2, aqi, rh, wind, temp, precip, n_days, log_pm25  (287 rows)

```
      Date   pm25   no2  so2    aqi    rh  wind  temp  precip  n_days  log_pm25
2015-01-04 184.60 34.12 5.80 347.00 78.25  7.22 15.38     4.3       4      5.22
2015-01-11 196.01 41.19 4.44 358.43 79.43  9.91 13.17     0.0       7      5.28
2015-01-18 187.65 49.24 5.45 360.00 82.29  7.53 12.60     4.1       7      5.23
2015-01-25 156.36 24.63 6.52 326.14 80.00  8.09 13.34    20.8       7      5.05
2015-02-01 162.78 37.28 6.47 324.14 70.00 10.09 12.44     0.0       7      5.09
2015-02-08 149.72 44.23 6.51 316.14 75.57  9.50 14.91    16.5       7      5.01
```

Missing-value report (raw merged data):
```
,n_missing,pct_missing,longest_gap_days
pm25,2,0.1,2
no2,2,0.1,2
so2,110,5.48,81
aqi,10,0.5,4
rh,0,0.0,0
wind,0,0.0,0
temp,0,0.0,0
precip,0,0.0,0
```

## Source code (verbatim)
These modules are imported by the notebooks.

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

### src/aqi.py
```python
"""CPCB (India) National AQI categories for 24-hour average PM2.5 (µg/m³)."""
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


def doy_climatology(s, window=31):
    """Smoothed day-of-year mean (circular rolling window), indexed 1..365."""
    doy = np.minimum(s.index.dayofyear, 365)
    clim = s.groupby(doy).mean().reindex(range(1, 366)).interpolate()
    half = window // 2
    padded = pd.concat([clim.iloc[-half:], clim, clim.iloc[:half]])
    return padded.rolling(window, center=True).mean().iloc[half:-half]


def doy_anomaly(s, window=31):
    """Deseasonalised series: value minus its smoothed day-of-year climatology."""
    clim = doy_climatology(s, window)
    doy = np.minimum(s.index.dayofyear, 365)
    return s - clim.reindex(doy).to_numpy()


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

### src/plots.py
Only styling helpers (colour palette, matplotlib rcParams, `savefig`, `shade_aqi_bands`); no analysis logic, omitted for length.

## Notes on the pipeline
- `doy_climatology`: mean per day-of-year (day 366 folded into 365), smoothed with a circular 31-day rolling mean; `doy_anomaly` subtracts it. Climatology is estimated on whatever sample is passed in (for notebook 03 that is 2015-2019, i.e. it includes the test year; harmless for Granger inference, but it would be leakage for forecasting).
- `adf_kpss`: ADF with AIC lag choice (constant only), KPSS level ('c', nlags auto); combined verdict. statsmodels caps the KPSS p-value to [0.01, 0.10].
- `pairwise_granger`: statsmodels SSR F-test with bivariate VARs (no controls).

=================== FILE: 03_phase2_eda_results.md ===================
# 03 Phase 2: EDA and stationarity (notebook 02), method and all numbers

## Steps
1. **Time plot vs CPCB bands.** 52.2% of days are Poor or worse (PM2.5 > 90). Max daily value above 450 not shown.
2. **Seasonality.** Winter (Nov-Jan) mean 213.3 vs monsoon (Jul-Sep) 48.1 => 4.43x. November median / August median = 4.9x.
```
       Unnamed: 0  pm25 pm25.1 wind wind.1   rh   rh.1
              NaN  mean median mean median mean median
           season   NaN    NaN  NaN    NaN  NaN    NaN
Monsoon (Jul–Sep)  48.1   46.0  9.0    8.4 78.0   80.0
     Other months 102.5   93.9  9.9    9.3 52.2   53.0
 Winter (Nov–Jan) 213.3  201.4  8.6    8.1 68.6   69.0
```

3. **STL** on weekly log PM2.5, period 52, robust=True. Seasonal strength F_S = 1 - Var(R)/Var(S+R) = **0.89**; trend strength 0.34. NOTE: STL is run on the FULL weekly sample incl. 2019 and the 2020 lockdown half-year.
4. **Correlations** (Spearman, daily, pooled): PM2.5 vs wind -0.24, vs humidity -0.20. Within season:
```
           season  ρ(PM2.5, wind)  ρ(PM2.5, RH)  days
Monsoon (Jul–Sep)           -0.39         -0.37   461
     Other months            -0.3         -0.02  1057
 Winter (Nov–Jan)           -0.47         -0.02   491
```

   Interpretation by the team: wind negative in every season; humidity negative only in monsoon (rain washout), about 0 in winter and other months.
5. **ACF/PACF (daily log PM2.5):** slow decay, negative at ~6 months, positive bump near lag 365; PACF cuts after a few lags (AR(1-2)-like).
6. **Stationarity tests, full sample** (ADF H0 unit root; KPSS H0 level-stationary; KPSS p capped at [0.01,0.1]):
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

7. **Stationarity, training weeks only (2015-2018)** with lag-1 ACF (over-differencing guard):
```
                           series   n  adf_stat    adf_p  adf_lags  adf_crit_1%  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p    verdict  lag1_acf
         Weekly log PM2.5 (train) 209     -4.28  0.00048         9       -3.464       -2.876        -2.575      0.058     0.1 Stationary      0.87
         Weekly Δ log PM2.5 (d=1) 208    -5.364 4.02e-06         5       -3.463       -2.876        -2.574      0.082     0.1 Stationary     -0.28
       Weekly Δ₅₂ log PM2.5 (D=1) 157    -4.534 0.000171         2       -3.474        -2.88        -2.577      0.341     0.1 Stationary      0.29
Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1) 156    -7.298 1.36e-10         5       -3.475       -2.881        -2.577      0.075     0.1 Stationary     -0.46
```

   Decision: d = 0. The extra first difference gives lag-1 ACF -0.46 (near -0.5 over-differencing warning). D in {0,1} deferred to a validation year.
8. **Why log?** Variance/volatility checks, raw vs log:
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

   Monthly mean and SD:
```
 Date  mean  sd_raw  sd_log
    1 197.5   69.88  0.3733
    2   142   53.07  0.3524
    3 87.57   31.71  0.3963
    4 90.93   36.49  0.4483
    5 92.21    40.2  0.4382
    6 69.81   32.45  0.4091
    7 46.42   18.67  0.4063
    8 42.86   14.59  0.3833
    9 55.34   22.75  0.4517
   10 140.9   69.17  0.4584
   11 238.2   115.3  0.4724
   12 208.1   69.61  0.3579
```

   Box-Cox lambda: 0.045 (daily), 0.028 (weekly) => close to 0 = log. ARCH-LM on the daily change: 235 -> 36 (still significant, p=6e-6); Levene p 1e-97 -> 0.006 (still rejects). Team's plan: re-check residuals of the final model.

## Key numbers JSON (results/key_numbers_eda.json)
```
{
  "pct_days_poor_or_worse": 52.2,
  "winter_mean_pm25": 213.3,
  "monsoon_mean_pm25": 48.1,
  "winter_to_monsoon_ratio": 4.43,
  "nov_to_aug_median_ratio": 4.9,
  "seasonal_strength": 0.89,
  "trend_strength": 0.34,
  "spearman_pm25_wind": -0.24,
  "spearman_pm25_rh": -0.2,
  "boxcox_lambda_daily": 0.045,
  "boxcox_lambda_weekly": 0.028
}
```

## Team's physical interpretation (not tested here)
Winds are only modestly calmer in Oct-Dec (~8 vs ~10 km/h in Mar-Jun) in ERA5; the rest of the winter peak is attributed to unmeasured mixing-layer depth / inversions, stubble burning, heating, fireworks. Monsoon is humid and cleanest (wet deposition).

=================== FILE: 04_phase3_var_granger_results.md ===================
# 04 Phase 3: VAR, Granger causality, IRF, FEVD (notebook 03), method and all numbers

## Setup
- Daily data 2015-01-01 to 2019-12-31 (1,826 days). 2020 excluded (lockdown).
- Variables: wind, rh, log PM2.5, each **deseasonalised** by subtracting its smoothed day-of-year climatology (31-day circular window, climatology estimated on the same 2015-2019 sample). Rationale: otherwise Granger detects "it is winter".
- Anomaly stationarity (note KPSS rejects for wind and PM2.5 anomaly, because of slow drift, e.g. the 2019 PM2.5 decline; ADF rejects unit root for all three):
```
          series    n  adf_stat    adf_p  adf_lags  adf_crit_1%  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p                                   verdict
    Wind anomaly 1826    -19.57        0         3       -3.434       -2.863        -2.568       1.05    0.01 Mixed (ADF says stationary, KPSS rejects)
Humidity anomaly 1826    -12.61  1.7e-23         3       -3.434       -2.863        -2.568      0.225     0.1                                Stationary
   PM2.5 anomaly 1826    -6.601 6.73e-09        18       -3.434       -2.863        -2.568      2.033    0.01 Mixed (ADF says stationary, KPSS rejects)
```

- Lag order: AIC picks 4, BIC 2, HQIC 3. VAR(4) used (stable, max eigenvalue modulus 0.811; Portmanteau whiteness p = 0.173 using nlags = p+10).
```
 lag   aic   bic  hqic   fpe
   0 4.477 4.486 4.481    88
   1 2.564 2.601 2.578 12.99
   2 2.442 2.506 2.466  11.5
   3 2.432 2.523 2.465 11.38
   4 2.426 2.544  2.47 11.31
   5 2.432 2.578 2.486 11.38
   6  2.43 2.603 2.494 11.36
   7 2.436 2.636  2.51 11.43
   8 2.434 2.662 2.518  11.4
   9  2.44 2.695 2.534 11.48
  10 2.441 2.724 2.546 11.49
  11 2.449 2.758 2.563 11.57
  12 2.456 2.793 2.581 11.66
  13 2.461 2.825 2.595 11.71
  14 2.466 2.858 2.611 11.78
```


## Granger causality (F-test from the VAR(4), anomalies)
```
             spec               direction     F        df   p_value   verdict (5%)
Anomalies, VAR(4)            Wind → PM2.5  35.7 (4, 5427) 1.734e-29 Granger-causes
Anomalies, VAR(4)        Humidity → PM2.5 14.38 (4, 5427) 1.107e-11 Granger-causes
Anomalies, VAR(4) Wind + Humidity → PM2.5 21.89 (8, 5427) 3.983e-33 Granger-causes
Anomalies, VAR(4)            PM2.5 → Wind   1.8 (4, 5427)    0.1268    No evidence
Anomalies, VAR(4)        PM2.5 → Humidity  0.67 (4, 5427)    0.6145    No evidence
```

Robustness (BIC lag 2, first differences with VAR(14) by AIC):
```
                            spec               direction     F         df   p_value   verdict (5%)
         Anomalies, VAR(4) [AIC]            Wind → PM2.5  35.7  (4, 5427) 1.734e-29 Granger-causes
         Anomalies, VAR(4) [AIC]        Humidity → PM2.5 14.38  (4, 5427) 1.107e-11 Granger-causes
         Anomalies, VAR(4) [AIC] Wind + Humidity → PM2.5 21.89  (8, 5427) 3.983e-33 Granger-causes
         Anomalies, VAR(4) [AIC]            PM2.5 → Wind   1.8  (4, 5427)    0.1268    No evidence
         Anomalies, VAR(4) [AIC]        PM2.5 → Humidity  0.67  (4, 5427)    0.6145    No evidence
         Anomalies, VAR(2) [BIC]            Wind → PM2.5 72.87  (2, 5451) 5.848e-32 Granger-causes
         Anomalies, VAR(2) [BIC]        Humidity → PM2.5 28.56  (2, 5451) 4.578e-13 Granger-causes
         Anomalies, VAR(2) [BIC] Wind + Humidity → PM2.5 44.65  (4, 5451) 6.086e-37 Granger-causes
         Anomalies, VAR(2) [BIC]            PM2.5 → Wind   4.1  (2, 5451)   0.01657 Granger-causes
         Anomalies, VAR(2) [BIC]        PM2.5 → Humidity  0.52  (2, 5451)    0.5929    No evidence
First differences, VAR(14) [AIC]            Wind → PM2.5 10.84 (14, 5304) 7.847e-25 Granger-causes
First differences, VAR(14) [AIC]        Humidity → PM2.5  5.47 (14, 5304)  1.47e-10 Granger-causes
First differences, VAR(14) [AIC] Wind + Humidity → PM2.5  7.23 (28, 5304) 1.014e-27 Granger-causes
First differences, VAR(14) [AIC]            PM2.5 → Wind  0.89 (14, 5304)    0.5686    No evidence
First differences, VAR(14) [AIC]        PM2.5 → Humidity  1.19 (14, 5304)     0.276    No evidence
```

Pairwise bivariate SSR F-tests by lag 1-7 (no controls):
```
      Unnamed: 0         1         2         3         4         5         6         7
    Wind → PM2.5 3.348e-08  1.57e-25 9.439e-24  4.87e-23  3.06e-22 1.215e-21 7.652e-21
Humidity → PM2.5 6.339e-06 2.795e-07 1.468e-06 5.451e-06 1.544e-05  3.85e-06 6.804e-06
    PM2.5 → Wind 0.0009714 0.0004747  0.004117   0.01432   0.03751   0.05918   0.08459
PM2.5 → Humidity    0.2354    0.5658    0.5739    0.6506    0.5535    0.5193    0.6188
```

**HAC (Newey-West, maxlags=10) Wald tests**, manual OLS equation-by-equation with 4 lags of each variable (target equation), plus rain control:
```
                 spec        direction  wald_chi2   p_value
PM2.5, wind, humidity     Wind → PM2.5       95.6 8.378e-20
PM2.5, wind, humidity Humidity → PM2.5       55.2 2.936e-11
       + rain control     Wind → PM2.5       92.4 4.165e-19
       + rain control Humidity → PM2.5       40.9 2.792e-08
       + rain control     Rain → PM2.5        1.3    0.8559
PM2.5, wind, humidity     PM2.5 → Wind        7.8    0.1012
PM2.5, wind, humidity PM2.5 → Humidity        3.1    0.5468
```

Reading: weather -> PM2.5 overwhelming (p < 1e-10) in every specification; PM2.5 -> humidity never; PM2.5 -> wind borderline only at BIC lag 2 (p=0.017) and pairwise lags 1-4. Humidity survives a rain control; rain itself adds nothing (p=0.86).

## Impulse responses (orthogonalised, Cholesky; response of log PM2.5 converted to % via exp(x)-1)
Shock size = 1 SD of the VAR residual: wind 2.54 km/h, humidity 5.43 %RH.
```
                      ordering    shock  day0_pct  day1_pct  day2_pct  day3_pct  day5_pct
weather first (wind, rh, pm25)     Wind      -9.2     -11.9      -4.6      -1.9      -0.3
weather first (wind, rh, pm25) Humidity      -4.5      -6.8      -5.7        -4      -1.4
  PM2.5 first (pm25, wind, rh)     Wind         0      -5.9      -1.1       0.9         1
  PM2.5 first (pm25, wind, rh) Humidity         0        -4      -4.1      -2.8      -0.8
```

Weather-first ordering allows same-day (contemporaneous) weather -> PM2.5; PM2.5-first allows only lagged effects. The team reports the range: wind day-1 effect -6% to -12%, humidity -4% to -7%, fading within ~5-7 days.

## FEVD of PM2.5 (share of forecast-error variance, %)
Default ordering (wind, rh, pm25), by horizon:
```
 horizon (days)  Wind  Humidity  PM2.5
              1  13.2         3   83.7
              2  22.5       6.2   71.4
              3  22.1       8.3   69.6
              4  21.2       9.2   69.6
              5  20.9       9.2   69.9
              6  20.7       9.3     70
              7  20.6       9.4   70.1
              8  20.5       9.5   70.1
              9  20.5       9.5   70.1
             10  20.4       9.5   70.1
             11  20.4       9.5   70.1
             12  20.4       9.5   70.1
             13  20.4       9.5   70.1
             14  20.4       9.5   70.1
```

Both orderings:
```
                      ordering variable  share_h1_pct  share_h14_pct
weather first (wind, rh, pm25)     Wind          13.2           20.4
weather first (wind, rh, pm25) Humidity             3            9.5
weather first (wind, rh, pm25)    PM2.5          83.7           70.1
  PM2.5 first (pm25, wind, rh)    PM2.5           100           93.6
  PM2.5 first (pm25, wind, rh)     Wind             0              3
  PM2.5 first (pm25, wind, rh) Humidity             0            3.3
```

Weather share at h=14: 29.9% (weather first) vs 6.3% (PM2.5 first: 3.0 + 3.3).

## "Shock" illustration (results/shock_binned.json)
VAR residual for wind on 2019-01-21: actual 14.8 km/h, VAR-predicted 7.42, shock +7.37. Days grouped by standardised shock size (z) and the mean PM2.5 deviation in %:
```
{
 "curves": {
  "wind": {
   "z": [
    -1.78,
    -1.05,
    -0.51,
    -0.01,
    0.5,
    1.08,
    2.26
   ],
   "pct": [
    32.0,
    14.4,
    5.9,
    -1.9,
    -6.0,
    -10.9,
    -23.7
   ],
   "n": [
    82,
    318,
    398,
    388,
    264,
    242,
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
    1.03,
    2.22
   ],
   "pct": [
    -1.4,
    1.4,
    5.6,
    4.6,
    2.5,
    -7.8,
    -21.3
   ],
   "n": [
    96,
    276,
    358,
    422,
    325,
    221,
    123
   ]
  }
 },
 "jan21_shock_kmh": 7.375528187562479,
 "jan21_wind": 14.8,
 "jan21_pred": 7.424471812437521
}
```

Reading by the team: unexpectedly windier day -> PM2.5 ~24% lower (z=+2.26), calmer day (z=-1.78) -> ~32% higher. Note the humidity curve is NON-monotonic (+5.6% at z=-0.5, -21% at z=+2.2).

## Weekly-scale check (does weather help beyond a week?)
Weekly anomalies (week-of-year mean from 2015-2018), regression of this week's PM2.5 anomaly on last week's values, HAC errors:
```
               model                 term    coef  p_value  r2_model
   same-week weather                 wind -0.0402   0.0013    0.1403
   same-week weather             humidity -0.0105        0    0.1403
last-week predictors    PM2.5 (last week)  0.3621        0    0.1391
last-week predictors     wind (last week)  0.0066   0.4576    0.1391
last-week predictors humidity (last week) -0.0013   0.4799    0.1391
```

Last week's wind (p=0.46) and humidity (p=0.48) add nothing (R2 0.139 vs same-week model 0.140). This is the basis for dropping weather from the 12-month model.

## Key numbers JSON (results/key_numbers_var.json)
```
{
  "var_sample": "2015-01-01 to 2019-12-31 (1826 days)",
  "var_lag_aic": 4,
  "var_lag_bic": 2,
  "var_stable": true,
  "portmanteau_p": 0.173,
  "max_eigen_modulus": 0.811,
  "irf": {
    "wind": {
      "peak_pct": -11.9,
      "peak_day": 1,
      "shock_sd": 2.54,
      "unit": "km/h"
    },
    "rh": {
      "peak_pct": -6.8,
      "peak_day": 1,
      "shock_sd": 5.43,
      "unit": "% RH"
    }
  },
  "fevd_weather_share_h14": 29.9,
  "fevd_wind_h14": 20.4,
  "fevd_rh_h14": 9.5,
  "granger": {
    "Wind → PM2.5": 1.73e-29,
    "Humidity → PM2.5": 1.11e-11,
    "Wind + Humidity → PM2.5": 3.98e-33,
    "PM2.5 → Wind": 0.127,
    "PM2.5 → Humidity": 0.615
  },
  "granger_hac": {
    "Wind → PM2.5 | PM2.5, wind, humidity": 8.38e-20,
    "Humidity → PM2.5 | PM2.5, wind, humidity": 2.94e-11,
    "Wind → PM2.5 | + rain control": 4.17e-19,
    "Humidity → PM2.5 | + rain control": 2.79e-08,
    "Rain → PM2.5 | + rain control": 0.856,
    "PM2.5 → Wind | PM2.5, wind, humidity": 0.101,
    "PM2.5 → Humidity | PM2.5, wind, humidity": 0.547
  }
}
```


=================== FILE: 05_phase4_sarima_draft.md ===================
# 05 Phase 4: SARIMA draft (next_phase/), code, outputs and status

STATUS: draft only. The notebook `04_sarima.ipynb` was saved WITHOUT executed outputs; the three weekly 12-month result tables below were produced by an earlier run. The one-week-ahead comparison (SARIMA vs SARIMAX with weather vs persistence) has NOT been produced (results/metrics_1week.csv, sarimax_weather_coef.csv, key_numbers_sarima.json do not exist). LSTM and Linear Regression baselines are not written yet.

## What the draft does
Weekly log PM2.5, s=52, train 2015-2018 (209 weeks), test 2019 (52 weeks). Baselines: seasonal naive (same week last year), climatology (train mean of that week-of-year on log scale, then exp), persistence (1-week only). Grid of 72 SARIMA(p,0,q)(P,D,Q)52 models (p,q in 0..2; (P,Q) in 4 combos; D in 0,1), ranked by AIC/BIC within each D (for D=1 the grid uses simple_differencing). D is picked on validation year 2018 (fit 2015-2017). Final model fit on 2015-2018, 52-step forecast with exp() of the log-scale 95% interval. Diagnostics: Ljung-Box, ARCH-LM, Shapiro. 

## Outputs
Grid: 71 of 72 converged. Best D=1 models by AIC (nobs=157 after simple differencing, so AIC is not comparable with D=0, where nobs=209 and the best AIC is far higher):
```
 D  p  q  P  Q  aic  bic  nobs  converged
 1  1  1  0  1 39.4 51.7   157       True
 1  1  2  0  1 40.3 55.6   157       True
 1  2  1  0  1 40.5 55.8   157       True
 1  2  2  0  1 40.6 58.9   157       True
 1  1  1  1  1 41.2 56.5   157       True
```
Best D=0 models:
```
 D  p  q  P  Q  aic  bic  nobs  converged
 0  1  1  1  1 58.9 75.6   209       True
 0  2  1  1  1 59.5 79.6   209       True
 0  2  2  1  1 61.1 84.5   209       True
 0  1  2  1  1 61.1 81.1   209       True
 0  2  0  1  1 64.7 81.5   209       True
```
D choice on validation (fit 2015-2017, forecast 2018, MAE in ug/m3):
```
 D            order  MAE  RMSE
 0 (1,0,1)(1,0,1)52 39.7  43.6
 1 (1,0,1)(0,1,1)52 21.1  28.6
```

=> D=1, order (1,0,1)(0,1,1)52.

**Test 2019, 52-week-ahead (original ug/m3):**
```
                   Unnamed: 0  MAE  RMSE
SARIMA(1, 0, 1)x(0, 1, 1)[52] 27.5  40.5
               Seasonal naive 30.3  44.2
                  Climatology 27.8  41.1
```

95% interval empirical coverage on 2019 actuals: **84.6%** (nominal 95%). Mean forecast error (actual - forecast): SARIMA -14.7, climatology -12.6, seasonal naive -6.4 (all over-predict: 2019 was cleaner than 2015-2018).
Fitted parameters (re-fit by the reviewer): ar.L1 0.883, ma.L1 -0.633, ma.S.L52 **-0.988**, sigma2 0.046.

Ljung-Box file in next_phase/ (ljungbox.csv): every p-value is ~0 (49 lags, 0% above 0.05). See file 06: this is an artifact, not model failure.

## Forecast table (full, weekly, 2019)
```
      Date  actual  forecast  lo95  hi95  seasonal_naive  climatology
2019-01-06   282.4     259.4 162.7 413.4           247.3        229.1
2019-01-13   215.7     211.3 130.7 341.5           188.3        194.0
2019-01-20   239.2     230.2 140.9 376.1           197.5        221.3
2019-01-27   116.3     193.9 117.7 319.4           148.5        178.1
2019-02-03   166.6     166.3 100.3 275.6           137.0        158.9
2019-02-10   134.6     161.2  96.8 268.5           169.4        149.2
2019-02-17   152.8     139.4  83.4 233.0           103.7        133.6
2019-02-24    90.1     167.9 100.2 281.6           158.1        167.7
2019-03-03    80.3     112.2  66.8 188.5           104.9        120.7
2019-03-10    86.0      93.2  55.3 156.8            96.9         89.1
2019-03-17    82.4      90.3  53.6 152.3           102.2         92.2
2019-03-24    79.1     103.4  61.3 174.5            91.0         93.3
2019-03-31    87.1      98.7  58.5 166.8            97.7        103.2
2019-04-07   104.1     100.2  59.3 169.4            94.5         91.9
2019-04-14    72.9     103.7  61.4 175.4            75.2        101.5
2019-04-21    61.8     112.5  66.5 190.4            92.3        106.3
2019-04-28    88.3     104.6  61.8 177.1           103.7        112.6
2019-05-05    85.8     107.3  63.4 181.6            68.9         95.0
2019-05-12   129.0     105.5  62.3 178.6            99.4        112.3
2019-05-19    86.9      95.0  56.1 160.9            83.7         98.9
2019-05-26    67.3     100.8  59.5 170.7            98.6         90.9
2019-06-02    78.3      82.9  49.0 140.4            80.0         92.9
2019-06-09    70.2      72.1  42.5 122.0            64.9         65.0
2019-06-16    69.0      94.0  55.5 159.3           152.4         91.6
2019-06-23    53.5      70.8  41.8 119.9            68.3         75.1
2019-06-30    56.7      50.4  29.8  85.4            38.9         51.6
2019-07-07    46.8      55.3  32.7  93.7            51.7         60.6
2019-07-14    62.9      47.9  28.3  81.1            43.5         45.3
2019-07-21    42.6      38.9  23.0  66.0            36.8         43.3
2019-07-28    42.5      33.5  19.7  56.7            34.6         35.3
2019-08-04    34.2      48.9  28.9  82.8            59.5         41.9
2019-08-11    28.5      44.5  26.3  75.4            39.1         44.0
2019-08-18    20.8      41.9  24.7  70.9            38.7         44.9
2019-08-25    45.1      44.0  26.0  74.5            31.8         42.0
2019-09-01    39.6      43.5  25.7  73.7            37.9         40.4
2019-09-08    46.8      52.4  31.0  88.8            42.0         54.7
2019-09-15    50.6      57.9  34.2  98.1            33.3         54.8
2019-09-22    39.9      54.4  32.1  92.2            49.2         59.2
2019-09-29    25.6      75.8  44.8 128.4            57.6         69.7
2019-10-06    43.3     102.4  60.5 173.5            83.4         91.7
2019-10-13    87.5     110.6  65.3 187.3            96.9        119.6
2019-10-20   111.9     159.6  94.2 270.2           140.5        146.9
2019-10-27   140.3     185.2 109.4 313.6           171.2        189.3
2019-11-03   353.4     255.4 150.8 432.4           202.8        231.0
2019-11-10   176.2     306.7 181.1 519.2           283.1        311.0
2019-11-17   297.9     211.7 125.0 358.3           173.1        218.4
2019-11-24   152.5     184.4 109.0 312.1           168.9        193.0
2019-12-01    86.8     203.1 120.1 343.7           186.7        203.3
2019-12-08   204.6     202.4 119.6 342.3           201.9        207.2
2019-12-15   184.1     152.0  89.9 257.0           175.7        177.6
2019-12-22   185.6     211.0 124.9 356.6           261.5        199.7
2019-12-29   234.3     233.9 139.6 392.1           287.4        233.1
```

## Draft code (verbatim, next_phase/04_sarima_draft.py)
```python
# %% [markdown]
# # 04 · Preliminary SARIMA / SARIMAX models (weekly log PM2.5)
# **Aim:** (a) a 12-month (52-week) forecast and (b) a measure of how much weather helps at a 1-week horizon.
#
# **Design (from notebooks 02–03)**
# * Weekly series (week ending Sunday), **s = 52**, modelled on **log PM2.5**.
# * Split: train 2015-01 → 2018-12 (209 weeks), test 2019 (52 weeks). The 2020 lockdown is excluded.
# * **d = 0** (the log level passes ADF and KPSS on the training sample). **D ∈ {0, 1}** is chosen on a
#   *validation* year (2018, models fitted on 2015–2017), never on the test year.
# * **12-month forecast: no weather inputs.** Notebook 03 showed last week's weather does not predict this week's
#   PM2.5, and future weather is unknown a year ahead.
# * **1-week-ahead: with and without same-week wind and humidity.** The "with weather" version assumes the week's
#   weather is known (e.g. from a weather forecast), so it is an *upper bound* for what weather can add.
# * Forecasts are made on the log scale and back-transformed with exp(). That gives a **median** forecast (the
#   mean would be slightly higher). Intervals are exp() of the log-scale 95% interval, so they are asymmetric.

# %%
import sys
sys.path.append("..")

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from scipy import stats
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch

from src.data import PROCESSED, RESULTS
from src.plots import use_style, BLUE, ORANGE, INK_2, NEUTRAL

warnings.filterwarnings("ignore")
use_style()
S = 52
weekly = pd.read_csv(PROCESSED / "delhi_weekly.csv", index_col="Date", parse_dates=True).asfreq("W-SUN")
y = weekly["log_pm25"]
raw = weekly["pm25"]
train, test = y.loc[:"2018-12-31"], y.loc["2019-01-01":"2019-12-31"]
assert len(train) == 209 and len(test) == 52 and y.notna().all()
key = {"n_train": len(train), "n_test": len(test)}

# %% [markdown]
# ## 1. Baselines the SARIMA model has to beat
# * **Seasonal naive:** the value from the same week one year earlier.
# * **Climatology:** the average (on the log scale, then exp) of that calendar week over the training years.
# * **Persistence** (for the 1-week-ahead test only): last week's value.

# %%
woy = lambda idx: np.minimum(pd.DatetimeIndex(idx).isocalendar().week.to_numpy(), 52)  # noqa: E731
clim_log = train.groupby(woy(train.index)).mean()
baseline = pd.DataFrame(index=test.index)
baseline["actual"] = raw.loc[test.index]
baseline["seasonal_naive"] = raw.shift(S).loc[test.index]
baseline["climatology"] = np.exp(clim_log.reindex(woy(test.index)).to_numpy())
baseline["persistence"] = raw.shift(1).loc[test.index]


def metrics(pred, actual):
    e = actual - pred
    return {"MAE": float(np.abs(e).mean()), "RMSE": float(np.sqrt((e ** 2).mean()))}


{k: {m: round(v, 1) for m, v in metrics(baseline[k], baseline["actual"]).items()} for k in ["seasonal_naive", "climatology"]}

# %% [markdown]
# ## 2. Order search: SARIMA(p, 0, q)(P, D, Q)₅₂, ranked by AIC and BIC
# Grid: p, q ∈ {0, 1, 2}; (P, Q) ∈ {(0,0), (1,0), (0,1), (1,1)}; D ∈ {0, 1}. 72 models, fitted on the training
# years. For speed the D = 1 grid uses simple differencing (the series is differenced once at lag 52 before
# fitting). **AIC and BIC are only comparable between models with the same D** (different numbers of observations).

# %%
def fit_one(series, p, q, P, Q, D, exog=None, simple=False, maxiter=100):
    mod = SARIMAX(series, exog=exog, order=(p, 0, q), seasonal_order=(P, D, Q, S), simple_differencing=simple)
    return mod.fit(disp=False, maxiter=maxiter)


def grid_row(p, q, P, Q, D):
    try:
        r = fit_one(train, p, q, P, Q, D, simple=(D == 1))
        return dict(D=D, p=p, q=q, P=P, Q=Q, aic=r.aic, bic=r.bic, nobs=int(r.nobs), converged=bool(r.mle_retvals.get("converged", False)))
    except Exception as e:  # noqa: BLE001
        return dict(D=D, p=p, q=q, P=P, Q=Q, aic=np.nan, bic=np.nan, nobs=0, converged=False)


combos = [(p, q, P, Q, D) for D in (0, 1) for p in (0, 1, 2) for q in (0, 1, 2) for P, Q in ((0, 0), (1, 0), (0, 1), (1, 1))]
grid = pd.DataFrame(Parallel(n_jobs=8)(delayed(grid_row)(*c) for c in combos))
grid.to_csv(RESULTS / "sarima_grid.csv", index=False)
print("models:", len(grid), "| converged:", int(grid["converged"].sum()), "| failed:", int(grid["aic"].isna().sum()))
top = {D: grid[(grid.D == D) & grid.converged].sort_values("aic").head(5) for D in (0, 1)}
pd.concat(top.values()).round(1)

# %% [markdown]
# Only models that converged are ranked. The best model by AIC and by BIC (within each D) is recorded below.

# %%
best = {}
for D in (0, 1):
    g = grid[(grid.D == D) & grid.converged]
    best[D] = {"aic": g.sort_values("aic").iloc[0].to_dict(), "bic": g.sort_values("bic").iloc[0].to_dict()}
    print(f"D={D}: best AIC = SARIMA({int(best[D]['aic']['p'])},0,{int(best[D]['aic']['q'])})({int(best[D]['aic']['P'])},{D},{int(best[D]['aic']['Q'])})52 "
          f"(AIC {best[D]['aic']['aic']:.1f}) | best BIC = ({int(best[D]['bic']['p'])},0,{int(best[D]['bic']['q'])})({int(best[D]['bic']['P'])},{D},{int(best[D]['bic']['Q'])})52 (BIC {best[D]['bic']['bic']:.1f})")

# %% [markdown]
# ## 3. Choosing D on a validation year (2018), not on the test year
# For each D, take its best-AIC order, fit on 2015–2017 and forecast the 52 weeks of 2018. The D with the lower
# validation MAE is used. (The order search above did see 2018 in-sample but never 2019.)

# %%
tr_sub, val = y.loc[:"2017-12-31"], y.loc["2018-01-01":"2018-12-31"]
assert len(val) == 52
val_rows = []
for D in (0, 1):
    b = best[D]["aic"]
    r = fit_one(tr_sub, int(b["p"]), int(b["q"]), int(b["P"]), int(b["Q"]), D)
    fc = np.exp(r.get_forecast(52).predicted_mean.to_numpy())
    val_rows.append({"D": D, "order": f"({int(b['p'])},0,{int(b['q'])})({int(b['P'])},{D},{int(b['Q'])})52", **{k: round(v, 1) for k, v in metrics(fc, raw.loc[val.index].to_numpy()).items()}})
val_sn = metrics(raw.shift(S).loc[val.index].to_numpy(), raw.loc[val.index].to_numpy())
val_tab = pd.DataFrame(val_rows)
val_tab.to_csv(RESULTS / "sarima_D_choice.csv", index=False)
D_star = int(val_tab.sort_values("MAE").iloc[0]["D"])
key["D_chosen"] = D_star
key["validation_seasonal_naive_MAE"] = round(val_sn["MAE"], 1)
print("Validation (2018):"); print(val_tab); print("seasonal naive on 2018:", {k: round(v, 1) for k, v in val_sn.items()}, "| chosen D =", D_star)

# %% [markdown]
# ## 4. Final model: fit on 2015–2018, forecast 2019 (52 weeks)

# %%
b = best[D_star]["aic"]
order = (int(b["p"]), 0, int(b["q"]))
sorder = (int(b["P"]), D_star, int(b["Q"]), S)
spec = f"SARIMA{order}x{sorder[:3]}[{S}]"
res = SARIMAX(train, order=order, seasonal_order=sorder).fit(disp=False, maxiter=200)
fc = res.get_forecast(52)
ci = fc.conf_int(alpha=0.05)
fcdf = pd.DataFrame({"actual": raw.loc[test.index], "forecast": np.exp(fc.predicted_mean.to_numpy()),
                     "lo95": np.exp(ci.iloc[:, 0].to_numpy()), "hi95": np.exp(ci.iloc[:, 1].to_numpy()),
                     "seasonal_naive": baseline["seasonal_naive"], "climatology": baseline["climatology"]}, index=test.index)
fcdf.to_csv(RESULTS / "forecast_2019.csv")
cover = float(((fcdf.actual >= fcdf.lo95) & (fcdf.actual <= fcdf.hi95)).mean())
m12 = pd.DataFrame({name: metrics(fcdf[col], fcdf["actual"]) for name, col in
                    [(spec, "forecast"), ("Seasonal naive", "seasonal_naive"), ("Climatology", "climatology")]}).T.round(1)
m12.to_csv(RESULTS / "metrics_12month.csv")
key.update({"final_model": spec, "coverage_95": round(cover, 3), "ci_width_first_week": round(float(fcdf.hi95.iloc[0] - fcdf.lo95.iloc[0]), 1),
            "ci_width_last_week": round(float(fcdf.hi95.iloc[-1] - fcdf.lo95.iloc[-1]), 1)})
print(spec, "| 95% interval coverage of 2019 actuals:", round(cover, 2))
m12

# %%
fig, ax = plt.subplots(figsize=(10, 4))
ax.fill_between(fcdf.index, fcdf.lo95, fcdf.hi95, color=BLUE, alpha=0.18, lw=0, label="95% interval")
ax.plot(fcdf.index, fcdf.forecast, color=BLUE, lw=2, label=f"Forecast: {spec}")
ax.plot(fcdf.index, fcdf.actual, color=ORANGE, lw=1.6, marker="o", ms=3, label="Actual 2019")
ax.plot(fcdf.index, fcdf.climatology, color=NEUTRAL, lw=1.2, ls="--", label="Climatology")
ax.set_ylabel("Weekly mean PM2.5 (µg/m³)")
ax.legend(ncols=2)
ax.set_title("12-month (52-week) forecast for 2019 vs actual")
plt.show()

# %% [markdown]
# ## 5. Residual diagnostics: are the residuals white noise?
# **Ljung-Box** tests H₀: no autocorrelation up to lag k (large p-values are good). **ARCH-LM** tests whether large
# residuals cluster (changing variance).

# %%
resid = pd.Series(res.resid, index=train.index)
df_model = order[0] + order[2] + sorder[0] + sorder[2]
lb = acorr_ljungbox(resid, lags=list(range(df_model + 1, 53)), model_df=df_model, return_df=True)
lb.to_csv(RESULTS / "ljungbox.csv")
arch_lm, arch_p, _, _ = het_arch(resid, nlags=4)
shapiro = stats.shapiro(resid)
key.update({"ljungbox_share_p_above_0.05": round(float((lb["lb_pvalue"] > 0.05).mean()), 2), "ljungbox_min_p": round(float(lb["lb_pvalue"].min()), 3),
            "ljungbox_p_lag10": round(float(lb.loc[10, "lb_pvalue"]), 3) if 10 in lb.index else None,
            "ljungbox_p_lag26": round(float(lb.loc[26, "lb_pvalue"]), 3) if 26 in lb.index else None,
            "ljungbox_p_lag52": round(float(lb.loc[52, "lb_pvalue"]), 3),
            "arch_lm_p": round(float(arch_p), 3), "shapiro_p": round(float(shapiro.pvalue), 3)})
fig, ax = plt.subplots(figsize=(9, 3.2))
ax.vlines(lb.index, 0, lb["lb_pvalue"], color=BLUE, lw=1)
ax.scatter(lb.index, lb["lb_pvalue"], color=BLUE, s=14, zorder=3)
ax.axhline(0.05, color=ORANGE, lw=1.5)
ax.set_ylim(0, 1.02); ax.set_xlabel("Lag (weeks)"); ax.set_ylabel("Ljung-Box p-value")
plt.show()
{k: key[k] for k in key if k.startswith(("ljung", "arch", "shapiro"))}

# %% [markdown]
# ## 6. One-week-ahead test: does same-week weather help?
# Parameters are fixed from the training fit. For each 2019 week the model sees all earlier weeks, then predicts
# that week (so no future information is used). The SARIMAX version additionally uses that week's standardised
# wind and humidity, which is only possible if the weather is known (for example from a weather forecast).

# %%
ex_cols = ["wind", "rh"]
ex = (weekly[ex_cols] - weekly.loc[train.index, ex_cols].mean()) / weekly.loc[train.index, ex_cols].std()
y_all = y.loc[:"2019-12-31"]


def one_step(exog):
    kw = {} if exog is None else {"exog": exog.loc[train.index]}
    r_tr = SARIMAX(train, order=order, seasonal_order=sorder, **kw).fit(disp=False, maxiter=200)
    kw_all = {} if exog is None else {"exog": exog.loc[y_all.index]}
    r_all = SARIMAX(y_all, order=order, seasonal_order=sorder, **kw_all).smooth(r_tr.params)
    pr = r_all.get_prediction(start=test.index[0], dynamic=False).predicted_mean
    assert np.abs(pr.to_numpy() - test.to_numpy()).mean() < 1.0, "one-step predictions are not on the log-level scale"
    return r_tr, np.exp(pr.to_numpy())


r_plain, pred_plain = one_step(None)
r_wx, pred_wx = one_step(ex[ex_cols])
os_tab = pd.DataFrame({
    "Persistence (last week)": metrics(baseline["persistence"], baseline["actual"]),
    "Seasonal naive": metrics(baseline["seasonal_naive"], baseline["actual"]),
    f"{spec} (no weather)": metrics(pred_plain, baseline["actual"]),
    f"{spec} + same-week wind & humidity": metrics(pred_wx, baseline["actual"]),
}).T.round(1)
os_tab.to_csv(RESULTS / "metrics_1week.csv")
wx_coef = pd.DataFrame({"coef": r_wx.params[ex_cols], "p_value": r_wx.pvalues[ex_cols]}).round(4)
wx_coef.to_csv(RESULTS / "sarimax_weather_coef.csv")
gain = 100 * (1 - os_tab.iloc[3]["MAE"] / os_tab.iloc[2]["MAE"])
key["one_week_mae_gain_from_weather_pct"] = round(float(gain), 1)
os_tab
wx_coef

# %% [markdown]
# **Reading it:** see the table. "Gain from weather" is the MAE reduction of the weather model over the same model
# without weather. It uses the *actual* same-week weather, so in practice (with imperfect weather forecasts) the
# gain would be smaller.

# %%
(RESULTS / "key_numbers_sarima.json").write_text(json.dumps(key, indent=2, ensure_ascii=False, default=str))
key
```

=================== FILE: 06_critical_review.md ===================
# 06 Critical review (by Claude, an earlier reviewer; verify independently, do not just agree)

Evidence marked **[verified]** was re-computed by the reviewer from the repo data. Others are read from code/results.

## A. What is solid
1. **Data hygiene is good.** Only 2 PM2.5 gaps; weather from ERA5 has no gaps; clear cleaning rule; weekly aggregation rule explicit; train/test split fixed before modelling; 2020 lockdown kept out of test and VAR.
2. **Deseasonalising before Granger** is the right call, and the team shows a robustness grid (anomalies/AIC lag, BIC lag, first differences) plus HAC errors and a rain control. The direction weather -> PM2.5 is stable across all of them (p < 1e-10), the reverse is not.
3. **Honest reporting of the ordering sensitivity** (IRF -6% to -12%, FEVD 6% to 30%) rather than one flattering number.
4. **Evidence-based design choice:** the weekly lag regression shows last week's weather adds nothing, which justifies a weather-free 12-month model.
5. **Reproducibility:** `verify_numbers.py` independently re-derives 52 slide numbers.

## B. Real problems found

### B1. Ljung-Box "failure" in the SARIMA draft is an artifact **[verified]**
`ljungbox.csv` shows p ~ 0 at all 49 lags. Cause: with D=1 the first 52 in-sample residuals are the diffuse-initialisation residuals (about 5.2 on the log scale, i.e. the series level itself), and the code runs Ljung-Box on all of `res.resid`. After dropping the first 52 residuals: residual SD 0.269, Ljung-Box p = 0.49 (lag 10) and 0.10 (lag 26), i.e. residuals are fine. Fix: `resid.iloc[S:]` (or use `simple_differencing`) before any residual diagnostic (Ljung-Box, ARCH-LM, Shapiro, ACF).

### B2. The SARIMA model barely beats climatology, and the interval is too narrow **[verified]**
2019 test MAE: SARIMA(1,0,1)(0,1,1)52 = 27.5, climatology = 27.8, seasonal naive = 30.3. A 0.3 ug/m3 gap on 52 points is within noise; no Diebold-Mariano test is done. Empirical 95% interval coverage on 2019 = 84.6%, not 95%. All three forecasts over-predict (mean error -14.7 / -12.6 / -6.4) because 2019 (mean 108) was cleaner than 2015-2018 (114-138): there is a downward drift the models do not have. One test year is a very small basis for ranking models.

### B3. The seasonal MA parameter is on the invertibility boundary **[verified]**
Fitted ma.S.L52 = -0.988. With D=1 plus a seasonal MA near -1, the seasonal difference and the MA term nearly cancel: it is a sign of over-differencing / a deterministic seasonal pattern (the team's own stationarity tests said the log level is already stationary, d=0, and the seasonal-difference KPSS on the full sample is borderline). The D=1 choice rests on one validation year (MAE 21.1 vs 39.7 for D=0), but the D=0 candidate there was a (1,0,1)(1,0,1) model that was fit on only 3 years with a 52-lag seasonal AR: a weak competitor. Better competitors that were never tried: harmonic regression (Fourier terms) + ARMA errors (dynamic harmonic regression), a seasonal-dummies/climatology + AR(1) anomaly model, and ETS/TBATS. With only 4 training seasons (209 weeks), estimating a 52-lag seasonal structure is statistically thin. The sub-1 % improvement over climatology suggests that most of the predictability is the calendar mean.

### B4. Information leakage / inconsistent samples across phases
- Notebook 03 estimates the day-of-year climatology on 2015-2019, so the 2019 test year influences the anomalies; fine for inference, but it must not be reused for forecasting evaluation.
- STL, Box-Cox and the "full-sample" stationarity tables use the full weekly sample incl. 2019 and the 2020 lockdown half-year (STL title even notes the trend falls from 2019 including lockdown). The team does repeat tests on the training set, but the headline STL strength 0.89 and Box-Cox lambda come from the full sample.
- The SARIMA order grid (AIC on 2015-2018) and the validation year 2018 overlap in-sample: the team admits this.

### B5. Statistical subtleties in the Granger/VAR work
- **Anomaly series are not clearly stationary:** KPSS rejects for PM2.5 and wind anomalies (stat 2.03 and 1.05 vs 0.46 critical). The team attributes it to the 2019 decline and runs a first-difference robustness check, which is reasonable, but the primary spec stays on anomalies.
- **p-values like 1e-29** from a plain F-test with autocorrelated, heteroskedastic residuals are not meaningful; the team already switches to HAC (1e-20 .. 1e-11) and states "p < 1e-10". The HAC is done "equation by equation" (a manual OLS rather than the full VAR), fine.
- **Inconsistency in the reverse direction PM2.5 -> wind:** pairwise bivariate table (granger_pairwise_lags.csv) gives p < 0.05 for lags 1-5 (0.001, 0.0005, 0.004, 0.014, 0.038); the VAR(4) F-test gives p = 0.127 (not significant); BIC VAR(2) gives 0.017; the slides quote "lags 1-2 only, p = 0.04 and 0.016" from a third (trivariate HAC per-lag) specification that is not saved in results/. So "PM2.5 -> wind is weak" depends on specification. Physically plausible reverse channel is negligible; the safe statement is "no robust reverse causality".
- **IRF identification:** Cholesky ordering is arbitrary; the team handles this with a range. Weather-first treats same-day PM2.5 as a pure response, which is questionable because daily means of wind/humidity and PM2.5 are measured over the same 24 h. IRF CIs are shown only for the default ordering.
- **Nonlinearity not examined:** humidity effect is non-monotonic (shock_binned.json: +5.6% at z = -0.5, -21% at z = +2.2) and EDA shows humidity matters only in the monsoon; a linear VAR with one coefficient for all seasons averages these. A season-interacted or regime-switching check is missing. Also no mixing height / boundary-layer height, stubble-burning fire counts, or temperature in the VAR (temp is available and unused; ERA5 offers boundary_layer_height). Omitted-variable bias is acknowledged only verbally. "Weather drives PM2.5" is stronger than "wind and humidity anomalies precede lower PM2.5".
- **ERA5 is a single grid cell** vs. CPCB Delhi being a multi-station city aggregate; measurement mismatch weakens estimated effects (attenuation).
- **Data quality:** the Kaggle CPCB file is an aggregation with known quirks (station mix changes over time; AQI from 2015 onwards). A secular decline from 2018 to 2019 could be partly a change in monitoring stations rather than real air quality.

### B6. Variance modelling is acknowledged but not resolved
Log PM2.5 still shows ARCH effects (LM 36, p = 6e-6) and unequal monthly variance (Levene p = 0.006; monthly log-SD ranges 0.35-0.47). The 12-month interval is built on a constant-variance Gaussian assumption on the log scale; the 84.6% coverage is consistent with that being too optimistic (winter variance of raw PM2.5 is much larger). Interval modelling could use seasonal variance, quantile forecasting, or a bootstrap.

### B7. Forecast target and reporting
- exp() of a log forecast is a **median**; the AQI advisory is about means/exceedance. Converting with exp(mu + sigma^2/2) (sigma^2 about 0.046) raises forecasts by about 2.3%; negligible vs the other errors, but should be stated.
- A "monthly AQI advisory table" from weekly mean PM2.5 hides within-week peaks: weekly means will under-state how often a single day crosses the "Severe" band. If the end user cares about exceedance days, a model of the daily distribution is more relevant than the weekly mean.
- Evaluation metrics are MAE/RMSE on the raw scale, dominated by the winter weeks; also report log-scale error / MAPE and per-season errors. For winter (Jan-Feb, Nov-Dec) the SARIMA MAE is 44.4 vs 46.6 climatology vs 56.3 seasonal naive **[verified]**, so most of the SARIMA gain is in winter.

### B8. Planned baselines are likely to disappoint or mislead
- **LSTM on 209 weekly points** is almost certainly over-parameterised; a 52-step recursive forecast without exogenous info would collapse to a mean seasonal pattern; including it as a "baseline" mostly demonstrates the point that deep learning is not suited here. Linear Regression needs a defined feature set (Fourier terms/lags); without it the baseline is ill-defined. Compare through rolling-origin (expanding window) cross-validation across 2017, 2018, 2019 rather than one test year.
- The 1-week SARIMAX with **same-week actual weather** is an upper bound that uses information not available at forecast time; a fair test would use lagged weather or an actual weather forecast. Also the weekly-aggregated weather is the mean of the same 7 days as PM2.5, so same-week R^2 0.14 partly reflects simultaneity, not predictability.

### B9. Repo hygiene
- README has been rewritten but `git status` shows uncommitted changes: modified notebooks/results/README, deleted slides/*.pptx/pdf, and untracked beamer sources, PRESENTATION_SCRIPT.md, next_phase/, new result tables.
- `__pycache__/*.pyc` are tracked and there is no `.gitignore`; `.venv` is in the working dir.
- `notebooks/04` is not executed (no stored outputs), so it can't be graded as evidence.
- The statement in the slide script "Isn't raw PM2.5 stationary too? Yes" slightly weakens the claim that stationarity needed logs; fine, since the script says logs are for variance.

## C. Severity ranking
1. B1 (diagnostic artifact; trivial fix, but would wrongly lead to rejecting the model).
2. B2/B3 (the headline forecasting result is not distinguishable from climatology; interval is miscalibrated; over-differencing signal).
3. B5 non-linear/seasonal heterogeneity, omitted variables (limits the strength of the causal story).
4. B7/B8 evaluation design (single test year, LSTM plan, upper-bound weather test).
5. B4, B6, B9.

## D. Suggested path forward (reviewer's recommendation)
1. Fix residual diagnostics (drop first s residuals), rerun and execute notebook 04 end-to-end.
2. Evaluate with rolling-origin cross-validation (e.g. fit 2015-2016 -> 2017, 2015-2017 -> 2018, 2015-2018 -> 2019), report MAE/RMSE on both raw and log scales, per-season errors, and Diebold-Mariano vs climatology.
3. Add competitors that fit the data size: Fourier-term regression + ARMA errors, climatology + AR(1) anomaly, ETS. Treat SARIMA(0,1,1)(0,1,1) airline-type models carefully; check ma.S near -1.
4. Calibrate the intervals (seasonally varying variance, or empirical residual quantiles / bootstrap) and report coverage; reconsider the target if the advisory depends on exceedance days.
5. Keep LSTM small/optional (or drop), state it as a negative result if kept.
6. Explicit trend handling: the downward drift into 2019-2020 (add a linear trend / level-shift term, or fit with the most recent years weighted more).
7. For the weather story, state it as "predictive, short-horizon", add temperature and optionally boundary-layer height, and test a season-interacted VAR if time permits.

=================== FILE: 07_open_questions_for_gpt.md ===================
# 07 Questions for GPT

Please answer each question with a concrete recommendation (and say if you disagree with file 06).

## Forecasting design (most important)
1. With 4 training seasons (209 weekly points) is a SARIMA(…)(…)52 sensible at all? Rank these for a 52-week-ahead forecast of weekly log PM2.5: (a) seasonal climatology, (b) climatology + AR(1) on anomalies, (c) Fourier-term regression (K harmonics) + ARMA errors, (d) SARIMA with D=1, (e) SARIMA with D=0, (f) ETS/TBATS, (g) Prophet-style additive model, (h) LSTM. Which do you expect to win and why?
2. The fitted seasonal MA coefficient is -0.988 under D=1. Is this evidence of over-differencing? What would you do (D=0 with seasonal AR or Fourier terms; fixed seasonal dummies)?
3. How should the model handle the 2019-2020 downward drift (possible level shift)? Is it a real air-quality improvement, monitoring-station composition change, or both, and how would you test it?
4. The 95% interval covers only 84.6% of 2019 weeks. What is the best fix with this little data: residual bootstrap, seasonal variance, quantile regression, conformal prediction (e.g. split/rolling conformal on weekly errors)?
5. Is a single test year adequate? Propose a rolling-origin evaluation design that respects the 52-step horizon with only ~5.5 years of data. Which significance test would you use to compare SARIMA vs climatology?
6. The end deliverable is a "monthly AQI advisory table". Should we forecast weekly means, daily values, or monthly means directly? How should we convert predictions into AQI category probabilities (e.g. P(category) per month)?
7. For the 1-week-ahead horizon, how should we fairly test whether weather helps (lagged weather, or ERA5 forecasts as exogenous inputs, vs the current "same-week actual weather" upper bound)?

## Causality / VAR (phase 3 already presented)
8. Do you agree that the conclusion "weather Granger-causes PM2.5 over 1-7 days" is well supported given deseasonalised anomalies, HAC errors, rain control, and lag robustness? What is the weakest link?
9. Is Cholesky-ordered IRF/FEVD a defensible choice for daily data where all three variables are 24-h means? Would generalised IRF or a local-projection approach be better? Is reporting a range (6%-30%) the right framing?
10. The humidity effect looks non-monotonic and season-dependent. Which minimal extra analysis (season-interacted VAR, threshold VAR, nonlinear Granger) would add most value for a course project, and which should be skipped?
11. Is it a problem that KPSS rejects stationarity for the PM2.5 and wind anomalies, and that the climatology is estimated on the same sample (including the trend)? Would you detrend, or use first differences as the primary spec?
12. Which additional variables (temperature, boundary-layer height, fire counts, NO2) are most worth adding for the Granger/VAR work, and would their addition plausibly change the conclusion?

## Methodology / reporting
13. Is the log transform adequately justified given residual ARCH effects (LM 36, p 6e-6) and monthly log-SD that still ranges 0.35-0.47? Is modelling the variance (GARCH, seasonal variance) worth it here?
14. Are there any statistical errors or over-claims in the presentation script (file 08) that a course instructor might challenge?
15. If the team has about two weeks left, what is the minimum set of analyses/changes that would most increase the grade/quality? Provide a prioritised list of at most 7 items.
16. Anything we missed that you think matters more than everything above?

Format your answer as: (i) agreements with file 06, (ii) disagreements, (iii) new issues found, (iv) numbered answers to Q1-Q16, (v) prioritised plan.

=================== FILE: 08_presentation_and_QA.md ===================
# 08 Presentation script and Q&A (as prepared by the team)
This shows the claims the team makes publicly. Judge whether each is justified.


Deck: `slides/Delhi_PM25_presentation.pdf` (14 slides + 3 backup; source `slides/beamer/main.tex`).
Every number in the deck is generated from `results/` and re-checked by `slides/beamer/verify_numbers.py` (52 checks).

## One-line pitch
"Delhi's PM2.5 repeats a huge winter peak every year. We first tested whether weather (wind and humidity) actually drives it. It does, over the next few days. In the next phase we use that to build and compare forecasting models for the coming 12 months."

## What to say on each slide

**1. Title.** "We are forecasting Delhi's PM2.5 air pollution. Today: what we have established. Next phase: the forecasting models."

**2. The problem.** "PM2.5 means particles under 2.5 micrometres that reach the lungs and blood, measured in micrograms per cubic metre. India's AQI colours these bands. 52 percent of days from 2015 to 2020 were Poor or worse, and it repeats every year: winter averages 213, the monsoon 48, so winter is 4.4 times higher."

**3. What we are building (say the intent clearly here).** "Two questions. Q1: does weather drive PM2.5? That is done, using a VAR model and Granger causality. Q2: what will PM2.5 be next? That is the next phase, on two horizons: next week, where weather may help, and the next 12 months, where weather is unknown, so we will not use weather inputs. The final output is a month-by-month AQI outlook for health advisories."

**4. Data.** "PM2.5 from CPCB, India's pollution board, through Kaggle; wind and humidity from ERA5, a reanalysis, meaning observations blended into a weather model to give a gap-free record. Links are on the slide. 2,009 days from January 2015 to July 2020, only 2 PM2.5 values interpolated. We use daily data for causality and weekly means, 287 weeks, for forecasting. Train 2015 to 2018, test 2019; the 2020 lockdown is excluded."

**5. STL.** "STL splits the series into trend, seasonal and residual. Seasonal strength is 0.89 on a scale where 1 is purely seasonal, so the yearly cycle dominates and the forecasting model must be seasonal with period 52 weeks."

**6. Why logs.** "PM2.5 moves by percentages: its spread is about 115 in November but 15 in August. Raw data has a heavy right tail, skewness 1.70. The log is close to a bell curve, skewness minus 0.08. The Box-Cox estimate is 0.045, close to 0, which is exactly the log."

**7. Volatility tests.** "Volatility is how much values swing. Raw spread differs 7.9 times between months and tracks the level; after the log only 1.3 times. Honest note: small differences remain. The equal-spread test still gives p = 0.006 and the ARCH test, which asks whether big swings cluster, drops from 235 to 36 but is still significant. So we re-check the model residuals later."

**8. Stationarity.** "Stationary means mean, spread and autocorrelation do not drift, so past patterns still apply. Weekly log PM2.5 on the training years has a flat rolling mean and a modestly varying spread: a repeating yearly pattern, not a drifting trend."

**9. ADF and KPSS.** "Two tests with opposite null hypotheses. ADF: H0 is a unit root; a small p supports stationarity. KPSS: H0 is stationary; a large p supports it. Both pass for log PM2.5 and its seasonal difference, so d = 0. A further difference over-differences, with lag-1 autocorrelation minus 0.46. Whether to use the seasonal difference D is decided in the next phase on a validation year, not the test year."

**10. Granger causality.** "X Granger-causes Y if past X improves the forecast of Y beyond Y's own past. We compare Model A (past PM2.5 only) with Model B (plus past wind and humidity) using a Wald test with robust errors. We removed the seasonal cycle first. Wind and humidity help predict PM2.5 at every lag from 1 to 7 days, p below 10 to the minus 9, and humidity still matters after controlling for rain. The reverse is absent for humidity and weak for wind, only at 1 to 2 lags. This is predictive causality, not proof of a physical cause."

**11. What is a shock.** "A shock is the part of today's wind or humidity that the model could not predict from the previous 4 days. On 21 January 2019 the model expected 7.4 km/h and the wind was 14.8, a shock of plus 7.4. One SD is a typical shock: 2.5 km/h for wind, 5.4 percent for humidity. Grouping all days by shock size, an unexpectedly windier day is followed by PM2.5 about 24 percent lower, a calmer one by about 32 percent higher."

**12. Impulse response.** "This traces PM2.5 after a one-SD shock. The size depends on the ordering assumption: weather first lets a shock act on the same day; PM2.5 first allows lagged effects only. Wind cuts PM2.5 by 6 to 12 percent the next day, humidity 4 to 7 percent, fading within about a week. At the weekly scale, last week's weather adds nothing to predict this week's PM2.5."

**13. Established so far.** Read the five bullets; end with: "Answer to Q1: yes, weather drives PM2.5 over the following days."

**14. Limits and next phase.** "Limits: Granger is predictive causality and mixing height, stubble burning and fireworks are not measured; weather's share of 14-day error is 6 to 30 percent depending on ordering; one city, data end mid-2020. Next: SARIMA(X) with AIC/BIC search and residual checks; baselines (seasonal naive, climatology, Linear Regression, LSTM) compared by test MAE on 2019; the final 12-month forecast with 95 percent intervals and a monthly AQI table."

## Likely questions and answers

**What is the project about?** Forecasting Delhi's PM2.5, after first testing whether wind and humidity drive it, so we know whether to use weather in the forecasting models.

**Why is there no forecast yet?** We split the work in two phases: first understand the data and the weather link (done); next fit and validate the SARIMA models. Doing the analysis first changed the design: weather only matters for days, so the 12-month model should not use it.

**Why logs?** The spread of PM2.5 grows with its level (corr. 0.95 between monthly mean and monthly SD, spread 7.9 times across months). The log makes the spread nearly constant (1.3 times) and removes the skew (1.70 to minus 0.08). Box-Cox lambda 0.045 is near 0.

**What does the volatility test show, and is the log enough?** It removes most of the level dependence, but the equal-spread test (p = 0.006) and ARCH (36, p about 6e-6) still reject. We will check the model residuals and add a variance model if needed.

**What is stationarity and which tests?** No drift in mean, spread or autocorrelation. ADF (H0 unit root) and KPSS (H0 stationary). Both pass for log PM2.5 and its seasonal difference on 2015 to 2018.

**Isn't raw PM2.5 stationary too?** Yes, it passes ADF and KPSS in our checks (ADF p = 0.0015, KPSS p at least 0.10). The log is for variance, not for stationarity.

**Why did you not use the seasonal difference twice (d = 1 and D = 1)?** The lag-1 autocorrelation is minus 0.46, close to the minus 0.5 warning level for over-differencing, and the series already passes the tests.

**What is a shock?** The unpredictable part of today's value given the past (the VAR residual). One SD is its typical size.

**What is an impulse response, and why a range?** The path of PM2.5 after a one-SD shock. It depends on the Cholesky ordering. We report weather-first and PM2.5-first, so wind is 6 to 12 percent, humidity 4 to 7 percent on day 1.

**Does it prove wind causes lower PM2.5?** No. Granger causality is predictive. Mixing height, stubble burning and fireworks are not in the data.

**Is the reverse direction (PM2.5 to wind) significant?** Weakly at 1 to 2 lags (p = 0.04 and 0.016), not at 3 or more (0.07 to 0.2); PM2.5 to humidity never (p at least 0.2). Weather to PM2.5 is significant at every lag from 1 to 7 (p below 1e-9).

**Why deseasonalise before Granger?** All series follow the calendar. Without removing it the test mostly detects "it is winter". We subtract a smoothed day-of-year mean.

**Why robust (HAC) errors?** The residuals are autocorrelated and their variance changes (ARCH), which can make ordinary p-values too small. HAC errors correct for that. Our manual implementation matches the software.

**Does humidity just stand in for rain?** No: with rain as a control, humidity stays significant (p = 3e-8) and rain adds nothing (p = 0.86).

**What does "6 to 30 percent" mean?** The share of the 14-day forecast-error variance of PM2.5 due to weather shocks in the VAR; 6 percent if PM2.5 is ordered first, 30 percent if weather is first.

**Why is weather not used for the 12-month forecast?** Its effect lasts about a week, last week's weather does not predict this week's PM2.5 (p = 0.46 and 0.48), and future weather is unknown a year ahead.

**Why weekly data for forecasting?** A 12-month horizon is 52 steps with a clear seasonal period of 52, which keeps the model fast and stable.

**What data and reliability?** CPCB through Kaggle; ERA5 reanalysis (a grid-cell estimate for central Delhi, not a station reading). A station dataset would be a good robustness check.

**Why train on 2015 to 2018 and test on 2019?** One full seasonal cycle for testing, and it keeps the 2020 lockdown (an emissions shock) out of the test.

## Numbers to remember
- 2,009 days; 52% of days Poor or worse; winter 213 vs monsoon 48 (4.4x); STL strength 0.89
- Log: skewness 1.70 to minus 0.08; monthly spread 7.9x to 1.3x; Box-Cox 0.045
- Training weeks 209: ADF stat minus 4.28 (level), minus 4.53 (seasonal difference); KPSS p at least 0.10; double-difference ACF minus 0.46
- Granger (4 lags, HAC): wind p = 8e-20, humidity 3e-11 (with rain control 3e-8), rain 0.86; reverse 0.10 (wind), 0.55 (humidity)
- 1 SD: wind 2.5 km/h, humidity 5.4%; day-1 effect wind minus 6 to minus 12%, humidity minus 4 to minus 7%; weather share 6 to 30%
- 21 Jan 2019: expected 7.4, actual 14.8, shock plus 7.4 km/h
