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
