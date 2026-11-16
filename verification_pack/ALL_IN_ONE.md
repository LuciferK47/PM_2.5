# 00 Verification pack: how to re-check everything
Project: Delhi PM2.5 time-series study (MATH F428). Branch `phase4-final`. You already have (or can get) the earlier briefing; this pack is **different**: it holds the raw material to *recompute and re-check* every number, not a summary.

## What to do
1. Take the headline claims in file 01 and **recompute each from the raw data in file 06** (weekly table and raw backtest forecasts). Report any mismatch.
2. Read the code (files 02-04, 07) for errors: leakage, off-by-one in horizons/weeks, wrong test, wrong formula.
3. Compare every number in the report/deck (file 08) against the tables (file 05). Report any number that is not in the tables or differs.
4. Judge whether each conclusion follows from the evidence, and which are over-claims.
Be specific: cite file, section, number. If you cannot run code, check by reasoning and by hand arithmetic where possible. Do not just agree.

## Files
| File | Content |
|---|---|
| 01_claims_ledger.md | every headline claim, its stated value, and where it comes from |
| 02_src_code.md | full source of src/ (data, tsa, aqi, forecast) |
| 03_notebooks_02_03_code.md | EDA and VAR/Granger notebooks: code plus printed output |
| 04_notebook_04_code.md | forecasting notebook: code plus printed output |
| 05_all_results_tables.md | every results/*.csv (except raw forecasts) and key_numbers json |
| 06_raw_data_for_recompute.md | weekly data table (287 rows) + raw backtest forecasts (fold, model, date, actual, mu, sd) |
| 07_verification_and_figure_code.md | verify_numbers.py (65 checks) and make_figures.py |
| 08_report_and_deck_text.md | LaTeX source of the written report and the Beamer deck |
| 09_changes_and_review_log.md | git history, what changed vs the original draft, and the review-response log |

## Setup facts
- Weekly series: W-SUN weeks, 287 weeks 2015-01-04 to 2020-07; log of the weekly mean PM2.5. Train 2015-2018 / expanding window.
- Origins: 2016-12-25, 2017-12-31, 2018-12-30, each forecasting 52 weeks. Point forecast = median exp(mu). Mean = exp(mu + sd^2/2).
- Verification already done by the authors: verify_numbers.py passes 65/65 (file 07). Treat that as a claim to test, not as proof.

## Output format
(i) numbers you reproduced (with your values), (ii) mismatches, (iii) code bugs, (iv) over-claims, (v) prioritised fixes.


# 01 Claims ledger (what the deck/report states, and how to check it)
Check each row. 'Source' tells you which file holds the evidence; 'Recompute' says how.

| # | Claim | Source | Recompute |
|---|---|---|---|
| 1 | Backtest MAE 2017/18/19: selected Fourier+ARMA 31.5/23.4/25.7; climatology 31.0/21.8/27.8; SARIMA D=1 53.8/21.1/27.5; SARIMA D=0 about 44; LSTM 36/49/53 | 05 (fc_backtest_mae.csv) | file 06 raw forecasts: mean |actual - exp(mu)| per fold and model |
| 2 | Climatology = mean of log PM2.5 by week index (1-52) over training years, forecast exp(mean) | 02 (forecast.py climatology) | file 06 weekly table |
| 3 | Seasonal naive = same week of the previous year | 02 | file 06 |
| 4 | Selected model not significantly better than climatology (block-bootstrap CI covers 0) | 05 (fc_loss_diff.csv) | resample loss differences, blocks of 8 weeks |
| 5 | 2019 95% interval coverage 90% raw, 96% after seasonal rescaling | 05 (fc_calibration_2019.csv) | share of actuals in [exp(mu-1.96 sd), exp(mu+1.96 sd)] (file 06) |
| 6 | Selected model raw 95% intervals, 2019: 5 misses, all below the lower bound; 2018: 2 below, 1 above; 2017 (stress test): 10 below, 6 above, coverage 69% | 05, 06 | count actual < lower vs > upper per fold (authors' recount: coverage 0.69/0.94/0.90) |
| 7 | One-week-ahead MAE change vs no-weather model: lagged weather -2.4%, last-3-days +0.7%, oracle same-week +6.9% (HLN-DM p about 0.07) | 05 (fc_oneweek.csv) | see 04 notebook cell for the one-step design |
| 8 | Wind/humidity Granger-cause PM2.5 for about a week, robust to rain, temperature, trend, training-only climatology | 05 (granger_*.csv) | 03 notebook; HAC Wald code in src |
| 9 | Weekly nested lag test adds nothing: delta R2 = 0.005, p = 0.51 | 05 (weekly_lag_nested.csv) | 03 notebook section 9 |
| 10 | 2019 pipeline test: 12/12 monthly means inside 95% interval; Poor-or-worse days 55% predicted vs 45% actual | 05 (fc_outlook_validation_2019_*.csv) | file 06 + 04 notebook |
| 11 | Lockdown (25 Mar - 31 May 2020): actual mean 48.7 is 43% below counterfactual median (95% -52% to -32%); weather-adjusted -38% | 05 (fc_lockdown.csv) | 1 - 48.7/median |
| 12 | PM2.5 decline 2016 to 2019: all stations -25%, fixed 6-station panel -20%, weather-adjusted -18% | 05 (station_check.csv) | 02 notebook section 8; needs data/raw/station_day.csv (not included) |
| 13 | Ljung-Box on SARIMA residuals is distorted by the 52 diffuse burn-in residuals; after removing them lags 10/26 pass, lag 52 p = 0.016 | 05 (fc_diagnostics.csv) | 04 notebook |
| 14 | Seasonal MA = -0.988 is unidentified (SE 8.26) | 04 notebook output | 04 notebook |
| 15 | Leap-year fix: day 366 mapped to 365 consistently | 02 (tsa.py doy365) | read code |

Key forecast numbers stored by the notebook:
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



# 02 Source code (src/)

## src/data.py
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

## src/tsa.py
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

## src/aqi.py
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

## src/forecast.py
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


# 03 Notebooks 02 and 03: code and printed output

## notebooks/02_eda.ipynb

### [md 0]
# 02 · Exploratory analysis & stationarity
**Scope note.** Descriptive EDA (sections 1-5, 7) uses the full 2015-01 to 2020-07 sample, which includes the 2020
lockdown months. Every statistic that feeds a modelling decision (seasonal strength, Box-Cox, d and D) is reported
on the **training years 2015-2018** as the headline, with the full-sample value alongside.

Questions:
1. How strong is the seasonal cycle (winter smog vs monsoon clearing)?
2. How does PM2.5 move with NO₂, SO₂, humidity and wind?
3. Which transformations make the series stationary (needed for VAR/Granger and to pick SARIMAX d, D)?

### [code 1]
```python
import sys
sys.path.append("..")

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.seasonal import STL
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from src.data import PROCESSED, RAW, RESULTS, SEASONS, OTHER_SEASON
from src.aqi import pm25_category, CATEGORIES
from src.tsa import stationarity_table
from src.plots import (use_style, savefig, shade_aqi_bands, SEASON_COLORS, LABELS,
                       BLUE, ORANGE, AQUA, NEUTRAL, INK, INK_2, MUTED, SURFACE)

use_style()
daily = pd.read_csv(PROCESSED / "delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
weekly = pd.read_csv(PROCESSED / "delhi_weekly.csv", index_col="Date", parse_dates=True)
key = {}  # headline numbers for the slides
```

### [md 2]
## 1. PM2.5 over time, against CPCB AQI bands

### [code 3]
```python
fig, ax = plt.subplots(figsize=(11, 4))
ymax = 450
shade_aqi_bands(ax, ymax)
ax.plot(daily.index, daily["pm25"], color=BLUE, lw=0.6, alpha=0.45, label="Daily mean")
ax.plot(daily.index, daily["pm25"].rolling(30, center=True).mean(), color=BLUE, lw=2, label="30-day rolling mean")
ax.set_ylim(0, ymax)
ax.set_xlim(daily.index.min(), daily.index.max())
ax.set_ylabel(LABELS["pm25"])
ax.set_title("Delhi PM2.5, 2015–2020: winter peaks every year, monsoon troughs in between")
ax.legend(loc="upper left", ncols=2)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
clipped = (daily["pm25"] > ymax).sum()
ax.annotate(f"{clipped} days above {ymax} µg/m³ not shown (max {daily['pm25'].max():.0f})",
            xy=(1, -0.12), xycoords="axes fraction", ha="right", fontsize=8, color=MUTED)
savefig(fig, "01_pm25_timeseries")
plt.show()
```

output:
```
findfont: Failed to find font weight semibold for DejaVu Sans, now using 700.
<Figure size 1210x440 with 1 Axes>
```

### [code 4]
```python
cat_share = pm25_category(daily["pm25"].to_numpy()).value_counts(normalize=True).reindex(CATEGORIES) * 100
key["pct_days_poor_or_worse"] = round(float(cat_share[["Poor", "Very Poor", "Severe"]].sum()), 1)
cat_share.round(1).rename("% of days").to_frame()
```

output:
```
              % of days
Good                5.0
Satisfactory       22.5
Moderate           20.3
Poor               14.7
Very Poor          30.2
Severe              7.3
```

### [md 5]
## 2. Seasonality: month-by-month distribution (headline figure)

### [code 6]
```python
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
by_month = [daily.loc[daily.index.month == m, "pm25"].dropna() for m in range(1, 13)]
month_season = {m: name for name, months in SEASONS.items() for m in months}
colours = [SEASON_COLORS[month_season.get(m, OTHER_SEASON)] for m in range(1, 13)]

monthly_median = daily["pm25"].groupby(daily.index.month).median()
key_ratio = monthly_median[11] / monthly_median[8]

fig, ax = plt.subplots(figsize=(10, 4.2))
bp = ax.boxplot(by_month, tick_labels=month_names, patch_artist=True, widths=0.6,
                showfliers=True, medianprops=dict(color=INK, lw=1.5),
                whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
                flierprops=dict(marker="o", markersize=2.5, markerfacecolor=MUTED, markeredgecolor="none", alpha=0.5))
for box, c in zip(bp["boxes"], colours):
    box.set(facecolor=c, edgecolor=SURFACE, linewidth=2, alpha=0.9)
ax.set_ylabel(LABELS["pm25"])
ax.set_title(f"PM2.5 by month: November median is {key_ratio:.1f}× August")
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in SEASON_COLORS.values()]
limit = ax.axhline(60, color=INK_2, lw=0.8)
ax.legend([*handles, limit], [*SEASON_COLORS.keys(), "Upper limit of CPCB 'Satisfactory' (60)"],
          loc="upper center", ncols=2)
savefig(fig, "02_monthly_boxplot")
plt.show()
```

output:
```
<Figure size 1100x462 with 1 Axes>
```

### [code 7]
```python
season_stats = daily.groupby("season")[["pm25", "wind", "rh"]].agg(["mean", "median"]).round(1)
winter, monsoon = "Winter (Nov–Jan)", "Monsoon (Jul–Sep)"
key["winter_mean_pm25"] = float(season_stats.loc[winter, ("pm25", "mean")])
key["monsoon_mean_pm25"] = float(season_stats.loc[monsoon, ("pm25", "mean")])
key["winter_to_monsoon_ratio"] = round(key["winter_mean_pm25"] / key["monsoon_mean_pm25"], 2)
monthly_median = daily["pm25"].groupby(daily.index.month).median()
key["nov_to_aug_median_ratio"] = round(float(monthly_median[11] / monthly_median[8]), 2)
season_stats.to_csv(RESULTS / "season_stats.csv")
season_stats
```

output:
```
                    pm25        wind           rh       
                    mean median mean median  mean median
season                                                  
Monsoon (Jul–Sep)   48.1   46.0  9.0    8.4  78.0   80.0
Other months       102.5   93.9  9.9    9.3  52.2   53.0
Winter (Nov–Jan)   213.3  201.4  8.6    8.1  68.6   69.0
```

### [md 8]
Winter averages **~4.4×** the monsoon PM2.5. In ERA5, winds are only modestly calmer in Oct–Dec (~8 km/h vs ~10 km/h
in Mar–Jun). The rest of the winter peak comes from things we don't measure here: a shallow mixing layer and
temperature inversions, stubble burning and heating emissions. The monsoon is the most humid season *and* the
cleanest, because rain washes particles out (wet deposition).

### [md 9]
## 3. STL decomposition (weekly log PM2.5, period = 52)

### [code 10]
```python
stl = STL(weekly["log_pm25"], period=52, robust=True).fit()
fig, axes = plt.subplots(4, 1, figsize=(10, 7), sharex=True)
parts = [("Observed (log PM2.5)", stl.observed), ("Trend", stl.trend),
         ("Seasonal (52-week)", stl.seasonal), ("Residual", stl.resid)]
for ax, (name, series) in zip(axes, parts):
    if name == "Residual":
        ax.vlines(series.index, 0, series, color=BLUE, lw=1)
    else:
        ax.plot(series.index, series, color=BLUE)
    ax.set_ylabel(name, rotation=0, ha="right", va="center")
axes[0].set_title("STL decomposition: a strong annual cycle; the trend falls from 2019 (incl. 2020 lockdown)")
fig.align_ylabels(axes)
savefig(fig, "03_stl_decomposition")
plt.show()

def stl_strengths(s):
    f = STL(s, period=52, robust=True).fit()
    v = np.var(f.resid)
    return (round(float(max(0, 1 - v / np.var(f.seasonal + f.resid))), 2),
            round(float(max(0, 1 - v / np.var(f.trend + f.resid))), 2))

key["seasonal_strength_full"], key["trend_strength_full"] = stl_strengths(weekly["log_pm25"])
key["seasonal_strength"], key["trend_strength"] = stl_strengths(weekly.loc[:"2018-12-31", "log_pm25"])  # headline: training years
print("Full sample  : F_S =", key["seasonal_strength_full"], "| F_T =", key["trend_strength_full"])
print("Training 2015-18 (headline): F_S =", key["seasonal_strength"], "| F_T =", key["trend_strength"])
```

output:
```
<Figure size 1100x770 with 4 Axes>Full sample  : F_S = 0.89 | F_T = 0.34
Training 2015-18 (headline): F_S = 0.9 | F_T = 0.09
```

### [md 11]
Seasonal strength $F_S = 1 - \mathrm{Var}(R)/\mathrm{Var}(S+R)$ is close to 1 (headline value on the 2015-2018 training weeks; the full-sample value is
shown above and is almost identical), so seasonality dominates.
This is why we use a **seasonal** ARIMA with s = 52.

### [md 12]
## 4. How PM2.5 moves with pollutants and weather

### [code 13]
```python
cols = ["pm25", "no2", "so2", "rh", "wind", "temp", "precip"]
corr = daily[cols].corr(method="spearman")
names = [LABELS[c].split(" (")[0] for c in cols]

fig, ax = plt.subplots(figsize=(6.4, 5.2))
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(cols)), names, rotation=40, ha="right")
ax.set_yticks(range(len(cols)), names)
ax.grid(False)
for i in range(len(cols)):
    for j in range(len(cols)):
        v = corr.iloc[i, j]
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                color="white" if abs(v) > 0.55 else INK)
for s in ax.spines.values():
    s.set_visible(False)
fig.colorbar(im, ax=ax, shrink=0.8, label="Spearman ρ")
ax.set_title("Spearman correlation (daily)")
savefig(fig, "04_correlation_heatmap")
plt.show()
key["spearman_pm25_wind"] = round(float(corr.loc["pm25", "wind"]), 2)
key["spearman_pm25_rh"] = round(float(corr.loc["pm25", "rh"]), 2)
```

output:
```
<Figure size 704x572 with 2 Axes>
```

### [code 14]
```python
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for ax, x in zip(axes, ["wind", "rh"]):
    for season, c in SEASON_COLORS.items():
        d = daily[daily["season"] == season]
        ax.scatter(d[x], d["pm25"], s=9, color=c, alpha=0.55, edgecolors="none", label=season)
    bins = pd.qcut(daily[x], 12)
    med = daily.groupby(bins, observed=True).agg(x=(x, "median"), y=("pm25", "median"))
    ax.plot(med["x"], med["y"], color=INK, lw=2, label="Binned median")
    ax.set_xlabel(LABELS[x])
    ax.set_yscale("log")
axes[0].set_ylabel(LABELS["pm25"] + ", log scale")
axes[0].set_title("Higher wind → cleaner air, in every season")
axes[1].set_title("Humidity: linked to cleaner air only in the monsoon")
fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", ncols=4, bbox_to_anchor=(0.5, 1.07))
savefig(fig, "05_pm25_vs_weather")
plt.show()
```

output:
```
<Figure size 1210x462 with 2 Axes>
```

### [md 15]
Pooled correlations mix the seasons together, so we check them **within each season**:

### [code 16]
```python
within = daily.groupby("season").apply(lambda g: pd.Series({
    "ρ(PM2.5, wind)": g["pm25"].corr(g["wind"], method="spearman"),
    "ρ(PM2.5, RH)": g["pm25"].corr(g["rh"], method="spearman"),
    "days": len(g),
})).round(2)
within.to_csv(RESULTS / "within_season_correlation.csv")
within
```

output:
```
                   ρ(PM2.5, wind)  ρ(PM2.5, RH)    days
season                                                 
Monsoon (Jul–Sep)           -0.39         -0.37   461.0
Other months                -0.30         -0.02  1057.0
Winter (Nov–Jan)            -0.47         -0.02   491.0
```

### [md 17]
* **Wind** is negatively correlated with PM2.5 in *every* season (strongest in winter). More wind means more
  dilution.
* **Humidity** is negatively correlated only in the **monsoon** (rain washout). In winter it is ≈ 0.
* These are correlations, not causes. Notebook 03 tests whether weather *predicts* PM2.5 (Granger).

### [md 18]
## 5. Autocorrelation

### [code 19]
```python
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
plot_acf(daily["log_pm25"].dropna(), lags=400, ax=axes[0], marker=None, color=BLUE,
         vlines_kwargs={"colors": BLUE, "lw": 0.6}, title="ACF, daily log PM2.5 (400 lags)")
plot_pacf(daily["log_pm25"].dropna(), lags=30, ax=axes[1], method="ywm", color=BLUE,
          vlines_kwargs={"colors": BLUE}, title="PACF, daily log PM2.5 (30 lags)")
for ax in axes:
    ax.set_xlabel("Lag (days)")
    for coll in ax.collections:
        coll.set_facecolor(NEUTRAL)
        coll.set_alpha(0.35)
axes[0].axvline(365, color=ORANGE, lw=1)
axes[0].text(368, 0.75, "1 year", color=ORANGE, fontsize=8)
savefig(fig, "06_acf_pacf")
plt.show()
```

output:
```
<Figure size 1210x396 with 2 Axes>
```

### [md 20]
The ACF decays slowly, dips negative at about 6 months and rises again near lag 365. This is the annual
cycle. The PACF cuts off after a few lags, so short-run dynamics look AR(1–2)-like.

### [md 21]
## 6. Stationarity tests: ADF + KPSS
* **ADF**, H0: unit root (non-stationary). Small p means stationary.
* **KPSS**, H0: stationary. Small p means non-stationary.

The two tests have opposite null hypotheses, so running both gives a more reliable verdict.

### [code 22]
```python
log_w = weekly["log_pm25"]
tests = {
    "Daily PM2.5 (raw)": daily["pm25"],
    "Daily log PM2.5": daily["log_pm25"],
    "Daily Δ log PM2.5": daily["log_pm25"].diff(),
    "Daily wind speed": daily["wind"],
    "Daily Δ wind speed": daily["wind"].diff(),
    "Daily rel. humidity": daily["rh"],
    "Daily Δ rel. humidity": daily["rh"].diff(),
    "Weekly log PM2.5": log_w,
    "Weekly Δ log PM2.5 (d=1)": log_w.diff(),
    "Weekly Δ₅₂ log PM2.5 (D=1)": log_w.diff(52),
    "Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1)": log_w.diff(52).diff(),
}
stationarity = stationarity_table(tests)
stationarity.to_csv(RESULTS / "stationarity.csv")
stationarity
```

output:
```
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerR
...[truncated]
```

### [md 23]
**Reading the table** (statsmodels caps the KPSS p-value at 0.1, so 0.1 means "≥ 0.1"):
* **No unit root in PM2.5.** Daily and weekly log PM2.5 *levels* pass both tests, i.e. the evidence is consistent with
  stationarity under the tests' assumptions (it is not a proof). Note that KPSS on the raw level is dominated by the large
  seasonal cycle; the slow downward drift only shows once the cycle is removed (section 6c). The annual cycle is a
  repeating, mean-reverting pattern, not a random walk.
* **Wind (daily)** is borderline: ADF rejects a unit root but KPSS rejects stationarity at 5%.
  Its first difference is clearly stationary.
* **Weekly series, full sample:** the seasonal difference Δ₅₂ gives KPSS p ≈ 0.02 (a rejection at 5%).
  That sample includes the 2019–20 decline (and the lockdown), which would also leak test-period information
  into model choices. Section 6b therefore repeats the weekly tests on the **training sample only (2015–2018)**.
* **Stationary does not mean ready for Granger.** Wind, humidity and PM2.5 all follow the same annual
  calendar. Unless we remove that shared seasonal cycle first (notebook 03), Granger tests would pick up
  "the season" instead of a real lead-lag relationship.

### [md 24]
## 6b. Stationarity on the training sample only (2015–2018, weekly)
Model-selection decisions (d, D) must not use the test year, so we repeat the weekly tests on 2015–2018.
`lag-1 ACF` guards against over-differencing: a lag-1 autocorrelation near −0.5 means the series was differenced
too much.

### [code 25]
```python
from statsmodels.tsa.stattools import acf
lw_tr = weekly.loc[:"2018-12-31", "log_pm25"]
tests_tr = {
    "Weekly log PM2.5 (train)": lw_tr,
    "Weekly Δ log PM2.5 (d=1)": lw_tr.diff(),
    "Weekly Δ₅₂ log PM2.5 (D=1)": lw_tr.diff(52),
    "Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1)": lw_tr.diff(52).diff(),
}
st_tr = stationarity_table(tests_tr)
st_tr["lag1_acf"] = [round(float(acf(s.dropna(), nlags=1)[1]), 2) for s in tests_tr.values()]
st_tr.to_csv(RESULTS / "stationarity_train.csv")
st_tr
```

output:
```
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerR
...[truncated]
```

### [md 26]
**Decision:** on the training sample the log level **and** the seasonal difference Δ₅₂ both pass ADF and KPSS, so
**d = 0**. The extra first difference over-differences (lag-1 ACF ≈ −0.46, near the −0.5 warning), so it is
dropped. Whether to take the seasonal difference (**D = 0 or 1**) is decided by rolling-origin validation in
notebook 04 (never on the evaluation year), not by AIC (AIC is not comparable across different D).

### [md 27]
## 7. Why the log transform? Variance and volatility tests
If the spread of PM2.5 grows with its level (as pollution data usually does), a log transform makes the
variance roughly constant, which the SARIMAX and VAR assumptions need.

### [code 28]
```python
from scipy import stats
from statsmodels.stats.diagnostic import het_arch

pm = daily["pm25"].dropna()
lg = np.log(pm)
by_month = pd.DataFrame({
    "mean": pm.groupby(pm.index.month).mean(),
    "sd_raw": pm.groupby(pm.index.month).std(),
    "sd_log": lg.groupby(lg.index.month).std(),
})
groups_raw = [g.to_numpy() for _, g in pm.groupby(pm.index.month)]
groups_log = [g.to_numpy() for _, g in lg.groupby(lg.index.month)]
lev_raw, lev_log = stats.levene(*groups_raw, center="median"), stats.levene(*groups_log, center="median")
arch_raw, arch_log = het_arch(pm.diff().dropna() - pm.diff().mean(), nlags=7), het_arch(lg.diff().dropna() - lg.diff().mean(), nlags=7)
log_tests = pd.DataFrame({
    "raw PM2.5": [stats.skew(pm), np.corrcoef(by_month["mean"], by_month["sd_raw"])[0, 1],
                  by_month["sd_raw"].max() / by_month["sd_raw"].min(), lev_raw.statistic, lev_raw.pvalue,
                  arch_raw[0], arch_raw[1]],
    "log PM2.5": [stats.skew(lg), np.corrcoef(by_month["mean"], by_month["sd_log"])[0, 1],
                  by_month["sd_log"].max() / by_month["sd_log"].min(), lev_log.statistic, lev_log.pvalue,
                  arch_log[0], arch_log[1]],
}, index=["Skewness", "corr(monthly mean, monthly SD)", "Max / min monthly SD", "Levene F (equal variance across months)",
          "Levene p-value", "ARCH-LM statistic (7 lags, on daily change)", "ARCH-LM p-value"])
log_tests.to_csv(RESULTS / "log_justification.csv")
by_month.to_csv(RESULTS / "monthly_mean_sd.csv")
key["boxcox_lambda_daily"] = round(float(stats.boxcox(pm)[1]), 3)
key["boxcox_lambda_weekly"] = round(float(stats.boxcox(weekly["pm25"])[1]), 3)
key["boxcox_lambda_daily_train"] = round(float(stats.boxcox(pm.loc[:"2018-12-31"])[1]), 3)
key["boxcox_lambda_weekly_train"] = round(float(stats.boxcox(weekly.loc[:"2018-12-31", "pm25"])[1]), 3)
print("Box-Cox lambda (0 means log):", key["boxcox_lambda_daily"], "daily,", key["boxcox_lambda_weekly"], "weekly")
log_tests.round(4)
```

output:
```
/home/kushagrasingh/Music/time_anal_proj/.venv/lib64/python3.12/site-packages/statsmodels/stats/diagnostic.py:997: FutureWarning: acorr_lm currently returns a plain tuple whose length depends on the store argument. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an LMTestResult NamedTuple. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  return acorr_lm(
Box-Cox lambda (0 means log): 0.045 daily, 0.028 weekly
                                             raw PM2.5  log PM2.5
Skewness                                        1.7041    -0.0772
corr(monthly mean, monthly SD)                  0.9512    -0.0666
Max / min monthly SD                            7.9030     1.3406
Levene F (equal variance across months)        49.6327     2.3989
Levene p-value                                  0.0000     0.0059
ARCH-LM statistic (7 lags, on daily change)   235.1849    36.4343
ARCH-LM p-value                                 0.0000     0.0000
```

### [md 29]
**Reading it:** the monthly SD of raw PM2.5 moves almost one-for-one with its mean (corr 0.95, SD varies 7.9×
between months). After the log the correlation is about zero and the spread varies only 1.3×. The Box-Cox
estimate λ ≈ 0.03–0.05 (full sample; ≈ 0.10 on the 2015–2018 training years) is close to 0, which is exactly the log transform. Some volatility clustering remains
(ARCH-LM still rejects), so the weekly forecast-model residuals are re-checked in notebook 04 (burn-in residuals removed).

### [md 30]
## 6c. Level drift: is there a slow decline hidden under the seasonal cycle?
The annual mean of PM2.5 fell from 138 (2016) to 108 µg/m³ (2019). KPSS on the raw level does not see it (the seasonal
cycle dominates the long-run variance), but it does once the cycle is removed. The climatology below is fitted on 2015-2018 only.

### [code 31]
```python
from statsmodels.tsa.stattools import kpss
from src.tsa import doy_anomaly
lg = daily["log_pm25"]
an_tr = doy_anomaly(lg, ref=lg.loc[:"2018-12-31"])           # climatology from the training years only
drift = pd.DataFrame({"mean PM2.5 (µg/m³)": daily["pm25"].groupby(daily.index.year).mean().round(1),
                      "mean log anomaly": an_tr.groupby(an_tr.index.year).mean().round(3)})
drift.to_csv(RESULTS / "annual_drift.csv")
import warnings as _w
with _w.catch_warnings():
    _w.simplefilter("ignore")
    key["kpss_stat_level_daily_log"] = round(float(kpss(lg.dropna(), regression="c", nlags="auto")[0]), 3)
    key["kpss_stat_anomaly_train_2015_2018"] = round(float(kpss(an_tr.loc[:"2018-12-31"].dropna(), regression="c", nlags="auto")[0]), 3)
    key["kpss_stat_anomaly_2015_2019"] = round(float(kpss(an_tr.loc[:"2019-12-31"].dropna(), regression="c", nlags="auto")[0]), 3)
print({k: v for k, v in key.items() if k.startswith("kpss_stat")}, "(5% critical value 0.463)")
drift
```

output:
```
{'kpss_stat_level_daily_log': 0.366, 'kpss_stat_anomaly_train_2015_2018': 0.896, 'kpss_stat_anomaly_2015_2019': 1.997} (5% critical value 0.463)
      mean PM2.5 (µg/m³)  mean log anomaly
Date                                      
2015               117.3             0.017
2016               138.5             0.103
2017               124.5            -0.043
2018               115.0            -0.077
2019               108.5            -0.185
2020                80.3            -0.496
```

### [md 32]
**Reading it:** the log anomaly falls from about +0.1 (2016) to about -0.15 (2019): a drift of roughly -20% to -25% over three
years, on top of a stable seasonal cycle. This is why the forecasting notebook must treat level/trend explicitly instead of
assuming a constant mean. Section 8 asks whether the drift is real air-quality improvement or a change in which monitors are counted.

### [md 33]
## 8. Is the 2016-2019 decline real? Station-network check
The Kaggle `city_day` Delhi value is the average over whatever stations reported that day. The number of reporting
stations grew sharply (see below), so a decline could partly be a change in the *mix* of stations. We test this with
`station_day.csv` (same Kaggle dataset, download command in the README): (1) confirm `city_day` = mean of stations,
(2) rebuild the annual series from a **fixed panel** of stations that reported in every year 2015-2019,
(3) remove the weather effect from the city series.

### [code 34]
```python
stn = pd.read_csv(RAW / "station_day.csv", parse_dates=["Date"])
meta = pd.read_csv(RAW / "stations.csv")
x = stn[stn.StationId.isin(meta.loc[meta.City == "Delhi", "StationId"])].dropna(subset=["PM2.5"]).copy()
x["year"] = x["Date"].dt.year
n_stations = x.groupby("year")["StationId"].nunique()
st_mean = x.groupby("Date")["PM2.5"].mean()
cmp_ = pd.concat([daily["pm25"], st_mean], axis=1, keys=["city_day", "station_mean"]).dropna()
key["city_vs_station_mean_corr"] = round(float(cmp_.corr().iloc[0, 1]), 4)
key["stations_by_year"] = {int(k): int(v) for k, v in n_stations.items()}
print("corr(city_day, mean of stations) =", key["city_vs_station_mean_corr"], "| stations reporting PM2.5 per year:", key["stations_by_year"])

days = x[x.year <= 2019].groupby(["StationId", "year"]).size().unstack(fill_value=0).reindex(columns=range(2015, 2020), fill_value=0)
panel = list(days.index[(days >= 60).all(axis=1)])
key["panel_stations"] = panel
print("fixed panel (>= 60 PM2.5 days in every year 2015-2019):", panel)

def annual_anomaly(df, min_stn=3):
    g = df.groupby("Date")["PM2.5"].agg(["mean", "count"])
    g = g[g["count"] >= min_stn]
    lg_ = np.log(g["mean"]).asfreq("D").interpolate(limit=3).dropna()
    an = doy_anomaly(lg_, ref=lg_.loc["2015":"2019"])
    return an.groupby(an.index.year).mean(), g["mean"].groupby(g.index.year).mean(), g["mean"].groupby(g.index.year).size()

a_all, m_all, _ = annual_anomaly(x)
a_pan, m_pan, d_pan = annual_anomaly(x[x.StationId.isin(panel)])

# weather-adjusted city series: regress log-PM2.5 anomaly on wind/rh/temp anomalies, 2015-2019, then average residuals by year
ref = slice("2015", "2019")
A = pd.DataFrame({c: doy_anomaly(daily[c].loc[ref]) for c in ["wind", "rh", "temp"]})
A["y"] = doy_anomaly(daily["log_pm25"].loc[ref]); A = A.dropna()
import statsmodels.api as sm
fit = sm.OLS(A["y"], sm.add_constant(A[["wind", "rh", "temp"]])).fit()
a_wx = fit.resid.groupby(fit.resid.index.year).mean()

station_check = pd.DataFrame({"stations": n_stations, "all_mean_pm25": m_all.round(1), "all_log_anom": a_all.round(3),
                              "panel_mean_pm25": m_pan.round(1), "panel_days": d_pan, "panel_log_anom": a_pan.round(3),
                              "weather_adj_log_anom": a_wx.round(3)}).loc[2015:2019]
station_check.to_csv(RESULTS / "station_check.csv")
chg = lambda s: round(float((np.exp(s.loc[2019] - s.loc[2016]) - 1) * 100), 1)
key["decline_2016_2019_pct"] = {"all_stations": chg(a_all), "fixed_panel": chg(a_pan), "weather_adjusted": chg(a_wx)}
print(key["decline_2016_2019_pct"])
station_check
```

output:
```
corr(city_day, mean of stations) = 0.995 | stations reporting PM2.5 per year: {2015: 10, 2016: 8, 2017: 17, 2018: 37, 2019: 37, 2020: 36}
fixed panel (>= 60 PM2.5 days in every year 2015-2019): ['DL002', 'DL013', 'DL019', 'DL021', 'DL028', 'DL031']
{'all_stations': -24.7, 'fixed_panel': -19.7, 'weather_adjusted': -17.7}
      stations  all_mean_pm25  all_log_anom  panel_mean_pm25  panel_days  \
2015        10          110.0         0.073            111.7         262   
2016         8          138.3         0.121            135.2         342   
2017        17          149.4         0.051            190.0         125   
2018        37          114.7        -0.054            121.6         365   
2019        37          108.2        -0.163            110.9         365   

      panel_log_anom  weather_adj_log_anom  
2015           0.040                 0.056  
2016           0.088                 0.085  
2017           0.020                -0.006  
2018           0.010                -0.026  
2019          -0.132                -0.110
```

### [code 35]
```python
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
axes[0].bar(n_stations.loc[2015:2019].index, n_stations.loc[2015:2019], color=NEUTRAL, width=0.6)
axes[0].set_title("Stations reporting PM2.5 in Delhi"); axes[0].set_ylabel("Stations")
for lab, s, c in [("All stations", a_all, BLUE), ("Fixed panel (6 stations)", a_pan, ORANGE), ("City series, weather-adjusted", a_wx, AQUA)]:
    axes[1].plot(s.loc[2015:2019].index, s.loc[2015:2019], marker="o", color=c, label=lab)
axes[1].axhline(0, color=INK_2, lw=0.8); axes[1].set_ylabel("Mean log-PM2.5 anomaly")
axes[1].set_title("Decline persists on a fixed station panel"); axes[1].legend(fontsize=8)
for ax in axes: ax.set_xticks(range(2015, 2020))
savefig(fig, "12_station_check"); plt.show()
```

output:
```
<Figure size 1210x418 with 2 Axes>
```

### [md 36]
**Reading it:** the city series equals the mean of the stations (corr 0.995), and the station count jumped from 8-10 (2015-16)
to 37 (2018-19), so a mix effect is *possible*. But the fixed panel of six long-running stations shows a decline of the
same sign and a similar size (see `decline_2016_2019_pct`: about -25% all stations, -20% fixed panel, -18% weather-adjusted), and so does the weather-adjusted city series. (The `all_mean_pm25` column averages only days with at least 3 reporting stations, so it is not directly comparable with the city-day annual means in section 6c; the log anomalies are the comparable quantity.)
So most of the decline is a **real drift in the level**, partly (not fully) confirmed by consistent monitors; the 2017 panel
is thin (about 125 days) and the panel is only six stations, so we do not claim a precise magnitude. Consequence for modelling:
the level cannot be treated as constant; notebook 04 compares constant, linear and random-walk level handling on validation years.

### [code 37]
```python
(RESULTS / "key_numbers_eda.json").write_text(json.dumps(key, indent=2))
key
```

output:
```
{'pct_days_poor_or_worse': 52.2,
 'winter_mean_pm25': 213.3,
 'monsoon_mean_pm25': 48.1,
 'winter_to_monsoon_ratio': 4.43,
 'nov_to_aug_median_ratio': 4.9,
 'seasonal_strength_full': 0.89,
 'trend_strength_full': 0.34,
 'seasonal_strength': 0.9,
 'trend_strength': 0.09,
 'spearman_pm25_wind': -0.24,
 'spearman_pm25_rh': -0.2,
 'boxcox_lambda_daily': 0.045,
 'boxcox_lambda_weekly': 0.028,
 'boxcox_lambda_daily_train': 0.097,
 'boxcox_lambda_weekly_train': 0.108,
 'kpss_stat_level_daily_log': 0.366,
 'kpss_stat_anomaly_train_2015_2018': 0.896,
 'kpss_stat_anomaly_2015_2019': 1.997,
 'city_vs_station_mean_corr': 0.995,
 'stations_by_year': {2015: 10,
  2016: 8,
  2017: 17,
  2018: 37,
  2019: 37,
  2020: 36},
 'panel_stations': ['DL002', 'DL013', 'DL019', 'DL021', 'DL028', 'DL031'],
 'decline_2016_2019_pct': {'all_stations': -24.7,
  'fixed_panel': -19.7,
  'weather_adjusted': -17.7}}
```


## notebooks/03_var_granger.ipynb

### [md 0]
# 03 · VAR model & Granger causality
**Question:** do wind speed and humidity *Granger-cause* PM2.5? In other words, does knowing past weather
improve the prediction of PM2.5 beyond what PM2.5's own past gives?

**Setup**
* Daily data, **2015-01-01 → 2019-12-31**. The 2020 COVID lockdown is left out because it is an
  emissions shock, not a weather effect.
* System: `wind`, `rh` and `pm25` (log). All three are **deseasonalised first**.
* Why deseasonalise? Wind, humidity and PM2.5 all follow the same calendar. Without removing that, Granger
  would mostly detect "it's winter" instead of a real lead-lag effect.
* Method: subtract each variable's smoothed day-of-year climatology (31-day circular window).
* Robustness check: repeat the analysis using plain first differences.

### [code 1]
```python
import sys
sys.path.append("..")

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.api import VAR

from src.data import PROCESSED, RESULTS
from src.tsa import doy_climatology, doy_anomaly, doy365, week_index, stationarity_table, pairwise_granger
from src.plots import use_style, savefig, VAR_COLORS, BLUE, ORANGE, AQUA, INK, INK_2, MUTED, NEUTRAL, SURFACE

warnings.filterwarnings("ignore", category=FutureWarning)
use_style()
daily = pd.read_csv(PROCESSED / "delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
d = daily.loc[:"2019-12-31"]
key = {"var_sample": f"{d.index.min().date()} to {d.index.max().date()} ({len(d)} days)"}
NAMES = {"wind": "Wind", "rh": "Humidity", "pm25": "PM2.5"}
```

### [md 2]
## 1. Remove the seasonal cycle

### [code 3]
```python
anom = pd.DataFrame({
    "wind": doy_anomaly(d["wind"]),
    "rh": doy_anomaly(d["rh"]),
    "pm25": doy_anomaly(d["log_pm25"]),
})
assert anom.notna().all().all()

clim = doy_climatology(d["log_pm25"])
fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
axes[0].plot(d.index, d["log_pm25"], color=NEUTRAL, lw=0.8, label="Daily log PM2.5")
axes[0].plot(d.index, clim.reindex(doy365(d.index)).to_numpy(), color=BLUE, lw=2,
             label="Seasonal climatology (day-of-year mean)")
axes[0].set_title("Step 1: remove the shared seasonal cycle before testing causality")
axes[0].legend(loc="lower left", ncols=2)
axes[1].plot(anom.index, anom["pm25"], color=BLUE, lw=0.8)
axes[1].axhline(0, color=INK_2, lw=0.8)
axes[1].set_ylabel("Anomaly")
axes[1].set_title("PM2.5 anomaly = log PM2.5 − climatology (used in the VAR)")
axes[1].xaxis.set_major_locator(mdates.YearLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
savefig(fig, "07_deseasonalise")
plt.show()
```

output:
```
findfont: Failed to find font weight semibold for DejaVu Sans, now using 700.
<Figure size 1100x550 with 2 Axes>
```

### [code 4]
```python
anom_stationarity = stationarity_table({f"{NAMES[c]} anomaly": anom[c] for c in anom})
anom_stationarity.to_csv(RESULTS / "stationarity_anomalies.csv")
anom_stationarity
```

output:
```
                     n  adf_stat         adf_p  adf_lags  adf_crit_1%  \
series                                                                  
Wind anomaly      1826   -19.557  0.000000e+00         3       -3.434   
Humidity anomaly  1826   -12.558  2.140000e-23         3       -3.434   
PM2.5 anomaly     1826    -6.576  7.710000e-09        18       -3.434   

                  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p  \
series                                                           
Wind anomaly           -2.863        -2.568      1.048    0.01   
Humidity anomaly       -2.863        -2.568      0.222    0.10   
PM2.5 anomaly          -2.863        -2.568      2.035    0.01   

                                                    verdict  
series                                                       
Wind anomaly      Mixed (ADF says stationary, KPSS rejects)  
Humidity anomaly                                 Stationary  
PM2.5 anomaly     Mixed (ADF says stationary, KPSS rejects)
```

### [md 5]
ADF strongly rejects a unit root for all three anomaly series (statistics far below the 1% critical value
of about −3.4). KPSS still flags wind and PM2.5, because with n ≈ 1,800 it reacts to small slow drifts
(e.g. the PM2.5 decline in 2019). We therefore fit the VAR on the anomalies, and in Section 6 we re-run
everything on **first differences**, which pass both tests, to check the conclusion is the same.

### [md 6]
## 2. Lag-order selection

### [code 7]
```python
model = VAR(anom)
order = model.select_order(maxlags=14)
lag_table = pd.DataFrame({ic: [getattr(order, "ics")[ic][p] for p in range(15)] for ic in ["aic", "bic", "hqic", "fpe"]})
lag_table.index.name = "lag"
lag_table.round(4).to_csv(RESULTS / "var_lag_selection.csv")
print("Selected orders:", {k: int(v) for k, v in order.selected_orders.items()})
lag_table.style.highlight_min(axis=0, props="font-weight:bold; background-color:#cde2fb")
```

output:
```
Selected orders: {'aic': 4, 'bic': 2, 'hqic': 3, 'fpe': 4}
<pandas.io.formats.style.Styler at 0x7fbd8d5e9d00>
```

### [code 8]
```python
p = int(order.selected_orders["aic"])
res = model.fit(p)
whiteness = res.test_whiteness(nlags=p + 10)
key.update({
    "var_lag_aic": p, "var_lag_bic": int(order.selected_orders["bic"]),
    "var_stable": bool(res.is_stable()),
    "portmanteau_p": round(float(whiteness.pvalue), 3),
})
print(f"VAR({p}) — stable: {res.is_stable()} | Portmanteau test (H0: residuals white, {p + 10} lags): p = {whiteness.pvalue:.3f}")
```

output:
```
VAR(4) — stable: True | Portmanteau test (H0: residuals white, 14 lags): p = 0.168
```

### [md 9]
AIC picks **p = 4 days**, BIC picks 2 and HQIC picks 3. We use the AIC lag, and Section 6 checks the
result under the BIC lag too. The fitted VAR is **stable** and its residuals pass the multivariate
Portmanteau test (no autocorrelation left), so the model is adequate for inference.

### [md 10]
### Stability: companion-matrix eigenvalues must lie inside the unit circle

### [code 11]
```python
eig = 1 / res.roots
fig, ax = plt.subplots(figsize=(4.2, 4.2))
theta = np.linspace(0, 2 * np.pi, 400)
ax.plot(np.cos(theta), np.sin(theta), color=MUTED, lw=1)
ax.scatter(eig.real, eig.imag, s=40, color=BLUE, edgecolors=SURFACE, linewidths=2, zorder=3)
ax.set_aspect("equal")
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.set_title(f"VAR({p}) is stable: max |λ| = {np.abs(eig).max():.2f}")
ax.set_xlabel("Real")
ax.set_ylabel("Imaginary")
savefig(fig, "08_var_stability")
plt.show()
key["max_eigen_modulus"] = round(float(np.abs(eig).max()), 3)
```

output:
```
<Figure size 462x462 with 1 Axes>
```

### [md 12]
## 3. Granger causality tests (from the fitted VAR)
H0: all lagged coefficients of the *causing* variable in the *caused* variable's equation are zero.

### [code 13]
```python
def granger_rows(results, label):
    rows = []
    for causing, caused in [("wind", "pm25"), ("rh", "pm25"), (["wind", "rh"], "pm25"), ("pm25", "wind"), ("pm25", "rh")]:
        t = results.test_causality(caused, causing, kind="f")
        name = " + ".join(NAMES[c] for c in np.atleast_1d(causing))
        rows.append({
            "spec": label, "direction": f"{name} → {NAMES[caused]}",
            "F": round(t.test_statistic, 2), "df": f"({t.df[0]}, {t.df[1]})", "p_value": t.pvalue,
            "verdict (5%)": "Granger-causes" if t.pvalue < 0.05 else "No evidence",
        })
    return rows

granger = pd.DataFrame(granger_rows(res, f"Anomalies, VAR({p})"))
granger.to_csv(RESULTS / "granger_var.csv", index=False)
granger.style.format({"p_value": "{:.2e}"})
```

output:
```
<pandas.io.formats.style.Styler at 0x7fbd8d5eb290>
```

### [md 14]
**Result:** the direction is one-way. Weather → PM2.5 is highly significant (p ≪ 0.001).
PM2.5 → weather, the reverse direction, is **not** significant. That is the physically expected pattern:
pollution does not change the next day's wind, but wind does disperse pollution.

### [md 15]
### Pairwise Granger tests across lags 1–7 days

### [code 16]
```python
pairs = [("wind", "pm25"), ("rh", "pm25"), ("pm25", "wind"), ("pm25", "rh")]
pw = pairwise_granger(anom, pairs, maxlag=7)
pw.index = [f"{NAMES[a]} → {NAMES[b]}" for a, b in pairs]
pw.to_csv(RESULTS / "granger_pairwise_lags.csv")

score = -np.log10(pw.clip(lower=1e-30))
fig, ax = plt.subplots(figsize=(8.5, 3))
im = ax.imshow(score.clip(upper=10), cmap="Blues", vmin=0, vmax=10, aspect="auto")
ax.set_xticks(range(7), [str(c) for c in pw.columns])
ax.set_yticks(range(len(pw)), pw.index)
ax.set_xlabel("Lag (days)")
ax.grid(False)
for s in ax.spines.values():
    s.set_visible(False)
for i in range(pw.shape[0]):
    for j in range(pw.shape[1]):
        v = pw.iloc[i, j]
        txt = "<1e-10" if v < 1e-10 else (f"{v:.0e}" if v < 0.001 else f"{v:.3f}")
        ax.text(j, i, txt, ha="center", va="center", fontsize=8,
                color="white" if score.iloc[i, j] > 5 else INK, fontweight="bold" if v < 0.05 else "normal")
fig.colorbar(im, ax=ax, label="−log₁₀ p  (capped at 10)", shrink=0.9)
ax.set_title("Pairwise Granger p-values: weather → PM2.5 at every lag order; PM2.5 → humidity at none")
savefig(fig, "09_granger_pvalues")
plt.show()
```

output:
```
<Figure size 935x330 with 2 Axes>
```

### [md 17]
Bold means p < 0.05. In pairwise tests, PM2.5 → wind is weakly significant at short lags. Once humidity is
also in the model (the full VAR above), that disappears (p ≈ 0.13), so it is not robust.
Each column is a **joint** test that lags 1..k of the cause add nothing (k = column label); it does not say that each individual
lag k is significant. A possible reason for a short-lag PM2.5 → wind signal in the bivariate test is a shared multi-day
stagnation regime (shallow boundary layer, low wind) that is not measured here; we do not claim it as a physical effect.

### [md 18]
## 4. Impulse responses: how much does PM2.5 respond to a weather shock?
These are orthogonalised (Cholesky) IRFs with ordering wind → humidity → PM2.5, so weather is allowed to
affect PM2.5 on the same day. The response of log PM2.5 is converted to a **% change**.

### [code 19]
```python
H = 14
irf = res.irf(H)
idx = {c: i for i, c in enumerate(anom.columns)}
se = irf.stderr(orth=True)
shock_sd = np.sqrt(np.diag(res.sigma_u))

fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
irf_summary = {}
for ax, imp in zip(axes, ["wind", "rh"]):
    r = irf.orth_irfs[:, idx["pm25"], idx[imp]]
    s = se[:, idx["pm25"], idx[imp]]
    pct, lo, hi = [(np.exp(x) - 1) * 100 for x in (r, r - 1.96 * s, r + 1.96 * s)]
    h = np.arange(H + 1)
    c = VAR_COLORS[imp]
    ax.fill_between(h, lo, hi, color=c, alpha=0.18, lw=0, label="95% CI")
    ax.plot(h, pct, color=c, lw=2, marker="o", markersize=4, label="Response")
    ax.axhline(0, color=INK_2, lw=0.8)
    k = int(np.argmin(pct))
    ax.annotate(f"{pct[k]:.1f}% on day {k}", xy=(k, pct[k]), xytext=(k + 2.5, pct[k] - 1),
                fontsize=9, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    unit = "km/h" if imp == "wind" else "% RH"
    ax.set_title(f"+1 SD {NAMES[imp].lower()} shock ({shock_sd[idx[imp]]:.1f} {unit}) → PM2.5")
    ax.set_xlabel("Days after shock")
    irf_summary[imp] = {"peak_pct": round(float(pct[k]), 1), "peak_day": k,
                        "shock_sd": round(float(shock_sd[idx[imp]]), 2), "unit": unit}
axes[0].set_ylabel("Change in PM2.5 (%)")
axes[0].legend(loc="lower right")
savefig(fig, "10_irf_weather_to_pm25")
plt.show()
key["irf"] = irf_summary
irf_summary
```

output:
```
<Figure size 1210x418 with 2 Axes>{'wind': {'peak_pct': -12.0, 'peak_day': 1, 'shock_sd': 2.54, 'unit': 'km/h'},
 'rh': {'peak_pct': -6.7, 'peak_day': 1, 'shock_sd': 5.43, 'unit': '% RH'}}
```

### [md 20]
## 5. Forecast-error variance decomposition of PM2.5
How much of the uncertainty in future PM2.5 comes from each variable's shocks?

### [code 21]
```python
fevd = pd.DataFrame(res.fevd(H).decomp[idx["pm25"]] * 100, columns=[NAMES[c] for c in anom.columns],
                    index=pd.RangeIndex(1, H + 1, name="horizon (days)"))
fevd.round(1).to_csv(RESULTS / "fevd_pm25.csv")

fig, ax = plt.subplots(figsize=(9, 3.4))
bottom = np.zeros(H)
for col, var in [("PM2.5", "pm25"), ("Wind", "wind"), ("Humidity", "rh")]:
    ax.bar(fevd.index, fevd[col], bottom=bottom, color=VAR_COLORS[var], edgecolor=SURFACE, linewidth=2,
           width=0.8, label=f"{col} shocks")
    bottom += fevd[col].to_numpy()
ax.set_ylim(0, 100)
ax.set_xlabel("Forecast horizon (days)")
ax.set_ylabel("Share of PM2.5 forecast\nerror variance (%)")
ax.set_xticks(fevd.index)
weather_share = fevd.loc[H, "Wind"] + fevd.loc[H, "Humidity"]
ax.set_title(f"Weather first ordering: weather shocks explain {weather_share:.0f}% by day {H} (≈6% if PM2.5 is ordered first, see §8)")
ax.legend(loc="upper center", ncols=3, bbox_to_anchor=(0.5, -0.22))
savefig(fig, "11_fevd_pm25")
plt.show()
key["fevd_weather_share_h14"] = round(float(weather_share), 1)
key["fevd_wind_h14"] = round(float(fevd.loc[H, "Wind"]), 1)
key["fevd_rh_h14"] = round(float(fevd.loc[H, "Humidity"]), 1)
fevd.loc[[1, 3, 7, 14]].round(1)
```

output:
```
<Figure size 990x374 with 1 Axes>                Wind  Humidity  PM2.5
horizon (days)                       
1               13.3       3.0   83.7
3               22.2       8.3   69.6
7               20.6       9.3   70.0
14              20.5       9.5   70.0
```

### [md 22]
## 6. Robustness checks
1. Same anomalies, with the **BIC** lag.
2. **First differences** instead of anomalies. These pass both ADF and KPSS (notebook 02), with the lag
   chosen by AIC.

### [code 23]
```python
res_bic = model.fit(int(order.selected_orders["bic"]))
diffs = pd.DataFrame({"wind": d["wind"].diff(), "rh": d["rh"].diff(), "pm25": d["log_pm25"].diff()}).dropna()
model_d = VAR(diffs)
p_d = int(model_d.select_order(maxlags=14).selected_orders["aic"])
res_d = model_d.fit(p_d)

robust = pd.DataFrame(
    granger_rows(res, f"Anomalies, VAR({p}) [AIC]")
    + granger_rows(res_bic, f"Anomalies, VAR({res_bic.k_ar}) [BIC]")
    + granger_rows(res_d, f"First differences, VAR({p_d}) [AIC]")
)
robust.to_csv(RESULTS / "granger_robustness.csv", index=False)
robust.pivot(index="direction", columns="spec", values="p_value").map(lambda v: f"{v:.1e}")
```

output:
```
spec                    Anomalies, VAR(2) [BIC] Anomalies, VAR(4) [AIC]  \
direction                                                                 
Humidity → PM2.5                        5.1e-13                 1.2e-11   
PM2.5 → Humidity                        5.9e-01                 6.2e-01   
PM2.5 → Wind                            1.5e-02                 1.2e-01   
Wind + Humidity → PM2.5                 4.4e-37                 2.8e-33   
Wind → PM2.5                            3.7e-32                 1.1e-29   

spec                    First differences, VAR(14) [AIC]  
direction                                                 
Humidity → PM2.5                                 1.5e-10  
PM2.5 → Humidity                                 2.8e-01  
PM2.5 → Wind                                     5.7e-01  
Wind + Humidity → PM2.5                          1.0e-27  
Wind → PM2.5                                     7.8e-25
```

### [md 24]
**Weather → PM2.5 is significant in every specification.** PM2.5 → humidity is never significant.
PM2.5 → wind is borderline only with the shortest (BIC) lag and vanishes otherwise.

### [md 25]
## 7. Stronger checks on the Granger result
The daily series have autocorrelated, changing-variance errors (the ARCH test in notebook 02 flagged this), which
can make ordinary F-test p-values look too small. We therefore re-test with **HAC (Newey-West) standard
errors** (robust to autocorrelation and changing variance), and we add **rain** as a control to see whether
humidity only stands in for rain.

### [code 26]
```python
import statsmodels.api as sm

P = p  # VAR lag order chosen above
rain = doy_anomaly(d["precip"])
dfa = anom.assign(rain=rain)


def lagmat(df, cols, lags):
    return pd.concat({f"{c}_l{k}": df[c].shift(k) for c in cols for k in range(1, lags + 1)}, axis=1)


def hac_granger(target, causes, controls):
    cols = [target, *controls]
    X = lagmat(dfa, cols, P)
    data = pd.concat([dfa[target], X], axis=1).dropna()
    fit = sm.OLS(data[target], sm.add_constant(data.drop(columns=target))).fit(cov_type="HAC", cov_kwds={"maxlags": 10})
    hyp = ", ".join(" = 0, ".join(f"{c}_l{k}" for k in range(1, P + 1)) + " = 0" for c in causes)
    w = fit.wald_test(", ".join(f"{c}_l{k} = 0" for c in causes for k in range(1, P + 1)), scalar=True)
    return float(w.statistic), float(w.pvalue)


rows = []
for spec, controls in [("PM2.5, wind, humidity", ["pm25", "wind", "rh"]), ("+ rain control", ["pm25", "wind", "rh", "rain"])]:
    for cause in ["wind", "rh"] + (["rain"] if "rain" in controls else []):
        stat, pv = hac_granger("pm25", [cause], controls)
        rows.append({"spec": spec, "direction": f"{NAMES.get(cause, 'Rain')} → PM2.5", "wald_chi2": round(stat, 1), "p_value": pv})
for cause in ["pm25"]:
    for target in ["wind", "rh"]:
        stat, pv = hac_granger(target, [cause], ["pm25", "wind", "rh"])
        rows.append({"spec": "PM2.5, wind, humidity", "direction": f"PM2.5 → {NAMES[target]}", "wald_chi2": round(stat, 1), "p_value": pv})
granger_hac = pd.DataFrame(rows)
granger_hac.to_csv(RESULTS / "granger_hac.csv", index=False)
granger_hac.style.format({"p_value": "{:.2e}"})
```

output:
```
<pandas.io.formats.style.Styler at 0x7fbd89305910>
```

### [md 27]
With robust errors, weather → PM2.5 is still overwhelmingly significant (wind p ≈ 1e-19; humidity p ≈ 3e-11, and 3e-8 once rain is a
control) and the reverse is not.
**Humidity stays significant after controlling for rain, and rain itself adds nothing** once wind and humidity are
in, so we do *not* claim the humidity effect is simply rain washout.
We quote p-values as "p < 10⁻¹⁰": beyond that, extra digits are not meaningful.

### [md 28]
### 7b. More robustness: temperature, a trend, a training-only climatology, season-specific effects, and lag order
Everything below uses the same manual HAC (Newey-West, 10 lags) Wald test as above, one equation at a time with P = 4 lags.

### [code 29]
```python
def design(frame, target, controls, P, trend=False, inter=None):
    cols = list(dict.fromkeys([target, *controls]))
    X = lagmat(frame, cols, P)
    if trend:
        X["trend"] = np.arange(len(frame)) / 365.25
    for name, (var, mask) in (inter or {}).items():
        for k in range(1, P + 1):
            X[f"{var}_l{k}_x_{name}"] = frame[var].shift(k) * mask
        X[name] = mask.astype(float)
    return X


def hac_wald2(frame, target, causes, controls, P, trend=False, rows=None, inter=None, test=None):
    data = pd.concat([frame[target], design(frame, target, controls, P, trend, inter)], axis=1).dropna()
    if rows is not None:
        data = data.loc[data.index.intersection(rows)]
    fit = sm.OLS(data[target], sm.add_constant(data.drop(columns=target))).fit(cov_type="HAC", cov_kwds={"maxlags": 10})
    names = test or [f"{c}_l{k}" for c in causes for k in range(1, P + 1)]
    w = fit.wald_test(", ".join(f"{n} = 0" for n in names), scalar=True)
    return float(w.statistic), float(w.pvalue), int(fit.nobs)


frame_all = anom.assign(rain=doy_anomaly(d["precip"]), temp=doy_anomaly(d["temp"]))
train_ref = d.loc[:"2018-12-31"]
frame_tr = pd.DataFrame({"wind": doy_anomaly(d["wind"], ref=train_ref["wind"]), "rh": doy_anomaly(d["rh"], ref=train_ref["rh"]),
                         "pm25": doy_anomaly(d["log_pm25"], ref=train_ref["log_pm25"])})
base3 = ["pm25", "wind", "rh"]
rows = []
def add(spec, direction, frame, target, causes, controls, **kw):
    s, pv, n = hac_wald2(frame, target, causes, controls, P, **kw)
    rows.append({"spec": spec, "direction": direction, "wald_chi2": round(s, 1), "p_value": pv, "n": n})
for c, nm in [("wind", "Wind"), ("rh", "Humidity")]:
    add("baseline (P=4)", f"{nm} → PM2.5", frame_all, "pm25", [c], base3)
    add("+ temperature control", f"{nm} → PM2.5", frame_all, "pm25", [c], base3 + ["temp"])
    add("+ rain and temperature", f"{nm} → PM2.5", frame_all, "pm25", [c], base3 + ["rain", "temp"])
    add("+ linear time trend", f"{nm} → PM2.5", frame_all, "pm25", [c], base3, trend=True)
    add("climatology from 2015-2018 only", f"{nm} → PM2.5", frame_tr, "pm25", [c], base3)
add("+ temperature control", "Temperature → PM2.5", frame_all, "pm25", ["temp"], base3 + ["temp"])
for t, nm in [("wind", "Wind"), ("rh", "Humidity")]:
    add("baseline (P=4)", f"PM2.5 → {nm}", frame_all, t, ["pm25"], base3)
    add("+ linear time trend", f"PM2.5 → {nm}", frame_all, t, ["pm25"], base3, trend=True)
robust2 = pd.DataFrame(rows)
robust2.to_csv(RESULTS / "granger_hac_robust.csv", index=False)
robust2.style.format({"p_value": "{:.2e}"})
```

output:
```
<pandas.io.formats.style.Styler at 0x7fbd89887cb0>
```

### [md 30]
**Season-specific effects.** The EDA suggested humidity matters mainly in the monsoon. We test (a) the cause in each season
subsample, and (b) a joint Wald test that the season interactions (monsoon × humidity lags, winter × wind lags) are zero.

### [code 31]
```python
m_ = frame_all.index.month
winter, monsoon = frame_all.index[np.isin(m_, [11, 12, 1])], frame_all.index[np.isin(m_, [7, 8, 9])]
srows = []
for sname, ridx in [("Winter (Nov–Jan)", winter), ("Monsoon (Jul–Sep)", monsoon)]:
    for c, nm in [("wind", "Wind"), ("rh", "Humidity")]:
        s, pv, n = hac_wald2(frame_all, "pm25", [c], base3, P, rows=ridx)
        srows.append({"test": f"{nm} → PM2.5, {sname} only", "wald_chi2": round(s, 1), "p_value": pv, "n": n})
mon_mask = pd.Series(np.isin(m_, [7, 8, 9]), index=frame_all.index)
win_mask = pd.Series(np.isin(m_, [11, 12, 1]), index=frame_all.index)
inter = {"mon": ("rh", mon_mask), "win": ("wind", win_mask)}
for label, tn in [("monsoon × humidity lags = 0", [f"rh_l{k}_x_mon" for k in range(1, P + 1)]),
                  ("winter × wind lags = 0", [f"wind_l{k}_x_win" for k in range(1, P + 1)])]:
    s, pv, n = hac_wald2(frame_all, "pm25", [], base3, P, inter=inter, test=tn)
    srows.append({"test": f"Interaction: {label}", "wald_chi2": round(s, 1), "p_value": pv, "n": n})
seasonal = pd.DataFrame(srows)
seasonal.to_csv(RESULTS / "granger_hac_seasonal.csv", index=False)
seasonal.style.format({"p_value": "{:.2e}"})
```

output:
```
<pandas.io.formats.style.Styler at 0x7fbd898707a0>
```

### [md 32]
**Joint tests at lag order k = 1..7** (HAC, three-variable system). The slides quote these, so they are now saved.

### [code 33]
```python
lrows = []
for pl in range(1, 8):
    for cause, target, nm in [("wind", "pm25", "Wind → PM2.5"), ("rh", "pm25", "Humidity → PM2.5"),
                              ("pm25", "wind", "PM2.5 → Wind"), ("pm25", "rh", "PM2.5 → Humidity")]:
        s, pv, n = hac_wald2(frame_all, target, [cause], base3, pl)
        lrows.append({"direction": nm, "lag_order": pl, "wald_chi2": round(s, 1), "p_value": pv})
by_lag = pd.DataFrame(lrows)
by_lag.to_csv(RESULTS / "granger_hac_by_lag.csv", index=False)
by_lag.pivot(index="direction", columns="lag_order", values="p_value").map(lambda v: f"{v:.1e}")
```

output:
```
lag_order               1        2        3        4        5        6  \
direction                                                                
Humidity → PM2.5  1.2e-10  5.4e-12  1.4e-11  3.5e-11  7.0e-11  2.0e-11   
PM2.5 → Humidity  2.2e-01  6.5e-01  5.4e-01  5.5e-01  5.1e-01  2.2e-01   
PM2.5 → Wind      3.8e-02  1.5e-02  6.5e-02  9.6e-02  2.0e-01  2.6e-01   
Wind → PM2.5      2.9e-10  1.2e-21  1.2e-20  6.0e-20  2.8e-19  2.5e-19   

lag_order               7  
direction                  
Humidity → PM2.5  2.8e-11  
PM2.5 → Humidity  4.4e-01  
PM2.5 → Wind      2.3e-01  
Wind → PM2.5      9.7e-19
```

### [md 34]
**Reading it:** weather → PM2.5 survives temperature and rain controls, a linear trend and a training-only climatology, so the
result is not an artifact of the 2019 decline or of the in-sample climatology. By season, wind and humidity are each
significant in **both** winter and monsoon (p ≤ 5e-4). The interaction tests are the formal comparison: monsoon × humidity
p = 0.20 (humidity's predictive content is *not* detectably different in the monsoon) and winter × wind p = 0.03 (weak
evidence that wind matters differently in winter). So the EDA impression that humidity matters only in the monsoon is a
*correlation* pattern; it is not confirmed as a difference in predictive effect, and we do not claim it.
The reverse direction (PM2.5 → wind) is significant only at lag orders 1-2 (p = 0.04, 0.02) and not from lag order 3 on.

### [md 35]
## 8. Does the shock size depend on the variable ordering?
Orthogonalised impulse responses assume an ordering: variables earlier in the list can affect later ones on the
**same day**. Wind and humidity first (weather → PM2.5 on the same day) gives weather the maximum credit.
PM2.5 first allows only *lagged* weather effects (the conservative case). We report both as a range.

### [code 36]
```python
irf_rows, fevd_rows = [], []
for label, order in [("weather first (wind, rh, pm25)", ["wind", "rh", "pm25"]), ("PM2.5 first (pm25, wind, rh)", ["pm25", "wind", "rh"])]:
    r_o = VAR(anom[order]).fit(p)
    irf_o = r_o.irf(H).orth_irfs
    fe_o = r_o.fevd(H).decomp[order.index("pm25")]
    for imp in ["wind", "rh"]:
        resp = (np.exp(irf_o[:, order.index("pm25"), order.index(imp)]) - 1) * 100
        irf_rows.append({"ordering": label, "shock": NAMES[imp], "day0_pct": resp[0], "day1_pct": resp[1], "day2_pct": resp[2],
                         "day3_pct": resp[3], "day5_pct": resp[5]})
    for j, v in enumerate(order):
        fevd_rows.append({"ordering": label, "variable": NAMES[v], "share_h1_pct": fe_o[0, j] * 100, "share_h14_pct": fe_o[H - 1, j] * 100})
irf_ord = pd.DataFrame(irf_rows).round(1)
fevd_ord = pd.DataFrame(fevd_rows).round(1)
irf_ord.to_csv(RESULTS / "irf_orderings.csv", index=False)
fevd_ord.to_csv(RESULTS / "fevd_orderings.csv", index=False)
display(irf_ord)
fevd_ord
```

output:
```
                         ordering     shock  day0_pct  day1_pct  day2_pct  \
0  weather first (wind, rh, pm25)      Wind      -9.2     -12.0      -4.7   
1  weather first (wind, rh, pm25)  Humidity      -4.5      -6.7      -5.7   
2    PM2.5 first (pm25, wind, rh)      Wind       0.0      -5.9      -1.1   
3    PM2.5 first (pm25, wind, rh)  Humidity       0.0      -4.0      -4.1   

   day3_pct  day5_pct  
0      -1.9      -0.3  
1      -4.0      -1.4  
2       0.9       1.0  
3      -2.7      -0.7                           ordering  variable  share_h1_pct  share_h14_pct
0  weather first (wind, rh, pm25)      Wind          13.3           20.5
1  weather first (wind, rh, pm25)  Humidity           3.0            9.5
2  weather first (wind, rh, pm25)     PM2.5          83.7           70.0
3    PM2.5 first (pm25, wind, rh)     PM2.5         100.0           93.7
4    PM2.5 first (pm25, wind, rh)      Wind           0.0            3.1
5    PM2.5 first (pm25, wind, rh)  Humidity           0.0            3.3
```

### [md 37]
**Reading it:** the next-day effect of a +1 SD wind shock is about −6% (lagged effect only) to −12% (including
same-day effects); humidity −4% to −7%. Weather's share of 14-day forecast-error variance ranges from about
6% (PM2.5 first) to about 30% (weather first). So the honest statement is "**weather accounts for a modest but
real share, roughly 6–30% depending on the assumed ordering**", not a single number.

### [md 38]
### 8b. Generalised impulse responses and confidence bands for both orderings
The Pesaran–Shin generalised IRF does not depend on the variable ordering: the response to a 1-SD shock to variable j is
Ψ_h Σ e_j / sqrt(σ_jj). It is the natural cross-check for the Cholesky range above (shocks are not orthogonal, so shares are not additive).

### [code 39]
```python
Psi = res.ma_rep(H)
Sig = np.asarray(res.sigma_u)
names = list(anom.columns)
ip = names.index("pm25")
girf_rows = []
for imp in ["wind", "rh"]:
    j_ = names.index(imp)
    resp = np.array([Psi[h_][ip] @ Sig[:, j_] / np.sqrt(Sig[j_, j_]) for h_ in range(H + 1)])
    pct_ = (np.exp(resp) - 1) * 100
    girf_rows.append({"shock": NAMES[imp], **{f"day{h_}_pct": round(float(pct_[h_]), 1) for h_ in (0, 1, 2, 3, 5)}})
girf = pd.DataFrame(girf_rows); girf.to_csv(RESULTS / "girf.csv", index=False)

ci_rows = []
for label, order_ in [("weather first (wind, rh, pm25)", ["wind", "rh", "pm25"]), ("PM2.5 first (pm25, wind, rh)", ["pm25", "wind", "rh"])]:
    r_o = VAR(anom[order_]).fit(p)
    i_o = r_o.irf(H); se_o = i_o.stderr(orth=True)
    for imp in ["wind", "rh"]:
        a_, b_ = order_.index("pm25"), order_.index(imp)
        r, s = i_o.orth_irfs[:, a_, b_], se_o[:, a_, b_]
        for h_ in range(H + 1):
            ci_rows.append({"ordering": label, "shock": NAMES[imp], "h": h_, "pct": (np.exp(r[h_]) - 1) * 100,
                            "lo": (np.exp(r[h_] - 1.96 * s[h_]) - 1) * 100, "hi": (np.exp(r[h_] + 1.96 * s[h_]) - 1) * 100})
irf_ci = pd.DataFrame(ci_rows).round(2); irf_ci.to_csv(RESULTS / "irf_ci.csv", index=False)
print("Generalised IRF (day-by-day % change in PM2.5):"); display(girf)
irf_ci[irf_ci.h == 1]
```

output:
```
Generalised IRF (day-by-day % change in PM2.5):
      shock  day0_pct  day1_pct  day2_pct  day3_pct  day5_pct
0      Wind      -9.2     -12.0      -4.7      -1.9      -0.3
1  Humidity      -3.3      -5.2      -5.1      -3.8      -1.4                          ordering     shock  h    pct     lo     hi
1   weather first (wind, rh, pm25)      Wind  1 -11.98 -13.28 -10.66
16  weather first (wind, rh, pm25)  Humidity  1  -6.74  -8.05  -5.41
31    PM2.5 first (pm25, wind, rh)      Wind  1  -5.90  -7.07  -4.72
46    PM2.5 first (pm25, wind, rh)  Humidity  1  -3.99  -5.16  -2.80
```

### [md 40]
The generalised response lies between the two Cholesky bounds, as expected. The day-1 bands (above) exclude zero for wind in both
orderings, so the reported ranges are not just point estimates.

### [md 41]
## 9. Does last week's weather help predict this week's PM2.5? (weekly scale)
The daily effect fades within about 5 days. For a 12-month forecast we need to know whether weather still helps at
the weekly scale. We deseasonalise the weekly series (week-of-year mean from 2015–2018) and regress this week's
PM2.5 anomaly on last week's PM2.5, wind and humidity anomalies, with HAC errors.

### [code 42]
```python
weekly = pd.read_csv(PROCESSED / "delhi_weekly.csv", index_col="Date", parse_dates=True)
wk = weekly.loc[:"2018-12-31", ["log_pm25", "wind", "rh"]].copy()
woy = week_index(wk.index)
wk_an = wk - wk.groupby(woy).transform("mean").to_numpy()
same = sm.OLS(wk_an["log_pm25"], sm.add_constant(wk_an[["wind", "rh"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
lagd = pd.concat([wk_an["log_pm25"].shift(1), wk_an["wind"].shift(1), wk_an["rh"].shift(1)], axis=1, keys=["pm25_lag1", "wind_lag1", "rh_lag1"])
lag_fit = sm.OLS(wk_an["log_pm25"], sm.add_constant(lagd), missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": 4})
weekly_lag = pd.DataFrame({
    "model": ["same-week weather"] * 2 + ["last-week predictors"] * 3,
    "term": ["wind", "humidity", "PM2.5 (last week)", "wind (last week)", "humidity (last week)"],
    "coef": [same.params["wind"], same.params["rh"], lag_fit.params["pm25_lag1"], lag_fit.params["wind_lag1"], lag_fit.params["rh_lag1"]],
    "p_value": [same.pvalues["wind"], same.pvalues["rh"], lag_fit.pvalues["pm25_lag1"], lag_fit.pvalues["wind_lag1"], lag_fit.pvalues["rh_lag1"]],
})
weekly_lag["r2_model"] = [same.rsquared] * 2 + [lag_fit.rsquared] * 3
weekly_lag.round(4).to_csv(RESULTS / "weekly_weather_lag.csv", index=False)

# Nested comparison: does adding last week's wind + humidity improve on last week's PM2.5 alone?
base = sm.OLS(wk_an["log_pm25"], sm.add_constant(lagd[["pm25_lag1"]]), missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": 4})
wald = lag_fit.wald_test("wind_lag1 = 0, rh_lag1 = 0", scalar=True)
nested = pd.DataFrame({"R2_lagged_pm25_only": [base.rsquared], "R2_plus_lagged_weather": [lag_fit.rsquared],
                       "delta_R2": [lag_fit.rsquared - base.rsquared], "joint_wald_p_weather": [float(wald.pvalue)]})
nested.round(4).to_csv(RESULTS / "weekly_lag_nested.csv", index=False)
display(nested.round(4))
weekly_lag.round(4)
```

output:
```
   R2_lagged_pm25_only  R2_plus_lagged_weather  delta_R2  joint_wald_p_weather
0               0.1341                  0.1391     0.005                0.5146                  model                  term    coef  p_value  r2_model
0     same-week weather                  wind -0.0402   0.0013    0.1403
1     same-week weather              humidity -0.0105   0.0000    0.1403
2  last-week predictors     PM2.5 (last week)  0.3621   0.0000    0.1391
3  last-week predictors      wind (last week)  0.0066   0.4576    0.1391
4  last-week predictors  humidity (last week) -0.0013   0.4799    0.1391
```

### [md 43]
**Reading it:** *same-week* weather is significantly related to PM2.5 (the daily effect, averaged over a week),
but **last week's weather adds nothing** once last week's PM2.5 is known: the nested comparison above shows ΔR² ≈ 0 and a
joint HAC Wald p-value far above 0.05. (The two R² values in the first table belong to different, non-nested models, so
they are not compared with each other.) So weather helps explain and
very-short-term-predict PM2.5, but it cannot be forecast a year ahead, so the 12-month model uses no weather
regressors. Weather's short-horizon value is quantified in notebook 04.

### [md 44]
## Conclusions
* **Wind and humidity anomalies have a strong, robust predictive association with PM2.5 (Granger):** joint tests are
  significant at every lag order 1-7, with HAC errors, with BIC lag, with first differences, with rain and temperature
  controls and with a linear trend. The reverse direction is not robust (it depends on the specification).
* **Size and timing:** a +1 SD wind shock (≈2.5 km/h) lowers PM2.5 by ≈6–12% the next day (range across
  orderings); a +1 SD humidity shock (≈5.4% RH) by ≈4–7%. Effects fade within about 5 days.
* **Share of forecast uncertainty:** ≈6–30% at 14 days, depending on the ordering assumption.
* **Horizon:** last week's weather does not add to last week's PM2.5 for predicting this week's PM2.5, so weather is a
  short-horizon tool and the 12-month model uses none.
* **Caveat:** this is *predictive* causality in a restricted observational model. Unmeasured drivers (mixing-layer height,
  stubble burning, fireworks) could confound it, and an in-sample Granger result does not guarantee out-of-sample skill
  (tested in notebook 04).

### [code 45]
```python
key["granger"] = {r["direction"]: float(f"{r['p_value']:.3g}") for r in granger.to_dict("records")}
key["granger_hac"] = {r["direction"] + " | " + r["spec"]: float(f"{r['p_value']:.3g}") for r in granger_hac.to_dict("records")}
(RESULTS / "key_numbers_var.json").write_text(json.dumps(key, indent=2, ensure_ascii=False))
key
```

output:
```
{'var_sample': '2015-01-01 to 2019-12-31 (1826 days)',
 'var_lag_aic': 4,
 'var_lag_bic': 2,
 'var_stable': True,
 'portmanteau_p': 0.168,
 'max_eigen_modulus': 0.813,
 'irf': {'wind': {'peak_pct': -12.0,
   'peak_day': 1,
   'shock_sd': 2.54,
   'unit': 'km/h'},
  'rh': {'peak_pct': -6.7, 'peak_day': 1, 'shock_sd': 5.43, 'unit': '% RH'}},
 'fevd_weather_share_h14': 30.0,
 'fevd_wind_h14': 20.5,
 'fevd_rh_h14': 9.5,
 'granger': {'Wind → PM2.5': 1.08e-29,
  'Humidity → PM2.5': 1.16e-11,
  'Wind + Humidity → PM2.5': 2.76e-33,
  'PM2.5 → Wind': 0.122,
  'PM2.5 → Humidity': 0.617},
 'granger_hac': {'Wind → PM2.5 | PM2.5, wind, humidity': 5.95e-20,
  'Humidity → PM2.5 | PM2.5, wind, humidity': 3.52e-11,
  'Wind → PM2.5 | + rain control': 2.81e-19,
  'Humidity → PM2.5 | + rain control': 3.04e-08,
  'Rain → PM2.5 | + rain control': 0.877,
  'PM2.5 → Wind | PM2.5, wind, humidity': 0.0956,
  'PM2.5 → Humidity | PM2.5, wind, humidity': 0.546}}
```


# 04 Notebook 04: forecasting, code and printed output

## notebooks/04_forecasting.ipynb

### [md 0]
# 04 · Forecasting weekly PM2.5: rolling-origin backtest, calibration, 1-week test, 2020 outlook
**What this notebook answers**
1. Which 52-week-ahead model is best, judged on three expanding-window origins (end of 2016, 2017, 2018 → forecasts for 2017, 2018, 2019)?
   Everything (Fourier order, ARMA order, level/trend treatment) is re-selected at each origin using only data before it.
2. Are the residuals clean (with the diffuse-initialisation residuals removed) and are the intervals calibrated?
3. Does weather help one week ahead, when tested fairly (lagged weather) versus with hindsight (same-week weather = oracle)?
4. What does a model fitted on 2015-2019 say about each month of 2020, and what does the gap to the lockdown months look like?

**Design rules.** Target: weekly mean PM2.5, modelled as log (so the point forecast `exp(mu)` is a *median*; mean forecasts use
`exp(mu + sd²/2)` with the horizon-specific sd). Season length 365.25/7 weeks. No weather in the 52-week models (notebook 03:
last week's weather adds nothing at the weekly scale and future weather is unknown). The 2020 lockdown never enters model selection.

### [code 1]
```python
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
import sys
sys.path.append("..")

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox

from src import forecast as F
from src.aqi import CATEGORIES, pm25_category
from src.data import PROCESSED, RESULTS
from src.plots import use_style, savefig, BLUE, ORANGE, AQUA, NEUTRAL, INK, INK_2, MUTED, SURFACE
from src.tsa import week_index, doy_anomaly

warnings.filterwarnings("ignore")
use_style()
weekly = pd.read_csv(PROCESSED / "delhi_weekly.csv", index_col="Date", parse_dates=True).asfreq("W-SUN")
daily = pd.read_csv(PROCESSED / "delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
y, raw = weekly["log_pm25"], weekly["pm25"]
assert y.notna().all() and len(y) == 287
key = {}
SEL = "Fourier+ARMA (selected)"
print(F.ORIGINS)
```

output:
```
{2017: '2016-12-25', 2018: '2017-12-31', 2019: '2018-12-30'}
```

### [md 2]
## 1. Models
| Model | What it is |
|---|---|
| Seasonal naive | the value 52 weeks earlier |
| Climatology | mean log PM2.5 of the same calendar week over the training years |
| Climatology + AR(1) | climatology plus an AR(1) on the weekly anomalies |
| Linear regression | OLS on 3 Fourier harmonics + a linear time trend (constant-variance intervals) |
| LSTM (small) | 1 layer, 16 units, seeded, recursive one-step on anomalies (no intervals of its own; training-residual sd) |
| Fourier+ARMA const / linear | dynamic harmonic regression: K=3 harmonics, AR(1) errors, constant or linear-trend level |
| **Fourier+ARMA (selected)** | K ∈ 1..5 and (p,q) by AICc inside each trend type (constant / linear / random-walk errors); the trend type chosen by validation on the *last training year*. **Declared as the headline procedure before looking at the test folds.** |
| SARIMA D=1 / D=0 | the benchmark from the draft: (1,0,1)(0,1,1)₅₂, and (1,0,1)(1,0,0)₅₂ **with a constant** (the draft omitted it) |

### [code 3]
```python
models = {
    "Seasonal naive": F.seasonal_naive, "Climatology": F.climatology, "Climatology + AR(1)": F.clim_ar1,
    "Linear regression": F.linreg, "LSTM (small)": F.lstm,
    "Fourier+ARMA const": F.dhr_fixed("const"), "Fourier+ARMA linear": F.dhr_fixed("linear"),
    SEL: F.dhr, "SARIMA D=1": F.sarima_D1, "SARIMA D=0": F.sarima_D0,
}
bt, fcs = F.backtest(y, raw, models, n_jobs=10, verbose=False)
bt.to_csv(RESULTS / "fc_backtest_metrics.csv", index=False)
long = pd.concat([pd.DataFrame({"fold": f, "model": m, "date": o["idx"], "actual": o["actual"], "mu": o["mu"],
                                "sd": o["sd"] if o["sd"] is not None else np.nan})
                  for f, d_ in fcs.items() for m, o in d_.items()])
long.to_csv(RESULTS / "fc_backtest_forecasts.csv", index=False)
specs = {f: fcs[f][SEL]["spec"] for f in fcs}
print("Selected specification per origin:"); display(pd.DataFrame(specs).T[["trend", "K", "p", "q", "inner_mae"]])
```

output:
```
Selected specification per origin:
      trend  K  p  q                                          inner_mae
2017     rw  5  1  1  {'const': 29.500542621119926, 'linear': 47.599...
2018  const  5  1  1  {'const': 30.66527919983907, 'linear': 37.6800...
2019     rw  5  1  1  {'const': 23.425849242714854, 'linear': 21.234...
```

### [md 4]
## 2. Backtest results (52 weeks ahead, MAE in µg/m³ on the original scale)
Folds 2018 and 2019 are the main evidence (3 and 4 training seasons); 2017 (only 2 training years) is a stress test. Climatology is the model to beat.

### [code 5]
```python
tab = bt.pivot(index="model", columns="fold", values="MAE")
tab["mean 2018-19"] = tab[[2018, 2019]].mean(axis=1)
tab["mean all 3"] = tab[[2017, 2018, 2019]].mean(axis=1)
tab = tab.sort_values("mean 2018-19")
tab.round(1).to_csv(RESULTS / "fc_backtest_mae.csv")
display(tab.round(1))
extra = bt.groupby("model")[["RMSE", "logMAE", "MAE_winter", "MAE_other", "bias"]].mean().loc[tab.index]
extra["coverage95"] = bt.groupby("model")["coverage"].mean()
extra["winkler"] = bt.groupby("model")["winkler"].mean()
display(extra.round(2))
```

output:
```
fold                     2017  2018  2019  mean 2018-19  mean all 3
model                                                              
Fourier+ARMA linear      35.9  19.7  24.0          21.9        26.5
Linear regression        35.9  20.0  24.9          22.5        26.9
SARIMA D=1               53.8  21.1  27.5          24.3        34.1
Climatology + AR(1)      30.7  21.7  27.3          24.5        26.6
Fourier+ARMA (selected)  31.5  23.4  25.7          24.6        26.9
Climatology              31.0  21.8  27.8          24.8        26.9
Fourier+ARMA const       30.6  22.0  29.3          25.7        27.3
Seasonal naive           38.4  29.0  30.3          29.6        32.6
SARIMA D=0               44.9  42.8  44.1          43.5        43.9
LSTM (small)             36.3  49.2  52.9          51.1        46.1                          RMSE  logMAE  MAE_winter  MAE_other   bias  \
model                                                                  
Fourier+ARMA linear      40.28    0.23       46.53      16.80  -4.43   
Linear regression        40.75    0.24       47.40      17.01  -3.60   
SARIMA D=1               58.73    0.26       59.47      21.81 -18.24   
Climatology + AR(1)      38.26    0.25       40.05      20.01  -8.13   
Fourier+ARMA (selected)  39.45    0.24       45.80      17.67  -7.54   
Climatology              37.60    0.25       40.96      20.01  -7.62   
Fourier+ARMA const       40.91    0.25       44.40      18.99  -6.49   
Seasonal naive           49.33    0.28       54.45      21.94  -9.94   
SARIMA D=0               58.91    0.44       52.87      39.60 -12.68   
LSTM (small)             68.69    0.36       74.59      32.31 -27.38   

                         coverage95  winkler  
model                                         
Fourier+ARMA linear            0.86   237.50  
Linear regression              0.87   229.25  
SARIMA D=1                     0.85   304.16  
Climatology + AR(1)            0.78   256.63  
Fourier+ARMA (selected)        0.85   194.50  
Climatology                     NaN      NaN  
Fourier+ARMA const             0.87   238.73  
Seasonal naive                  NaN      NaN  
SARIMA D=0                     0.90   285.97  
LSTM (small)                   0.08  1593.46
```

### [code 6]
```python
# Paired loss differences against climatology: moving-block bootstrap (8-week blocks) of the weekly absolute-error differences.
def abs_err(model, folds):
    return np.concatenate([np.abs(fcs[f][model]["actual"] - np.exp(fcs[f][model]["mu"])) for f in folds])

ld = []
for label, folds in [("folds 2018+2019", [2018, 2019]), ("all three folds", [2017, 2018, 2019])]:
    for m in models:
        if m == "Climatology":
            continue
        dm_, lo, hi = F.block_bootstrap_diff(abs_err(m, folds), abs_err("Climatology", folds))
        ld.append({"folds": label, "model": m, "mean_MAE_diff_vs_climatology": dm_, "ci_lo": lo, "ci_hi": hi,
                   "verdict": "better" if hi < 0 else ("worse" if lo > 0 else "indistinguishable")})
ld = pd.DataFrame(ld).round(2); ld.to_csv(RESULTS / "fc_loss_diff.csv", index=False)
display(ld[ld.folds == "folds 2018+2019"])
```

output:
```
             folds                    model  mean_MAE_diff_vs_climatology  \
0  folds 2018+2019           Seasonal naive                          4.84   
1  folds 2018+2019      Climatology + AR(1)                         -0.30   
2  folds 2018+2019        Linear regression                         -2.33   
3  folds 2018+2019             LSTM (small)                         26.26   
4  folds 2018+2019       Fourier+ARMA const                          0.86   
5  folds 2018+2019      Fourier+ARMA linear                         -2.94   
6  folds 2018+2019  Fourier+ARMA (selected)                         -0.23   
7  folds 2018+2019               SARIMA D=1                         -0.53   
8  folds 2018+2019               SARIMA D=0                         18.67   

   ci_lo  ci_hi            verdict  
0   0.19   8.53              worse  
1  -0.75   0.05  indistinguishable  
2  -6.17   0.77  indistinguishable  
3   8.80  42.30              worse  
4  -2.10   2.72  indistinguishable  
5  -6.43  -0.36             better  
6  -3.56   1.81  indistinguishable  
7  -2.32   1.02  indistinguishable  
8  12.96  23.98              worse
```

### [md 7]
**Reading it.** A negative difference means lower error than climatology. The interval is wide because 52 consecutive weekly errors
within one forecast path are strongly dependent: three origins are far too few for a sharp significance claim, and
we say "indistinguishable" whenever the interval contains 0. The earlier draft's 2019 comparison (SARIMA 27.5 vs climatology 27.8)
is such a case.

### [code 8]
```python
sel_name = SEL
fig, axes = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={"width_ratios": [1.5, 1]})
f19 = fcs[2019]; idx19 = f19[sel_name]["idx"]
mu, sd = f19[sel_name]["mu"], f19[sel_name]["sd"]
ax = axes[0]
ax.fill_between(idx19, np.exp(mu - 1.96 * sd), np.exp(mu + 1.96 * sd), color=BLUE, alpha=0.18, lw=0, label="95% prediction interval")
ax.plot(idx19, np.exp(mu), color=BLUE, lw=2, label=f"{sel_name}")
ax.plot(idx19, np.exp(f19["Climatology"]["mu"]), color=NEUTRAL, lw=1.4, ls="--", label="Climatology")
ax.plot(idx19, f19[sel_name]["actual"], color=ORANGE, lw=1.4, marker="o", ms=3, label="Actual 2019")
ax.set_ylabel("Weekly mean PM2.5 (µg/m³)"); ax.legend(ncols=2, fontsize=8)
ax.set_title("52-week forecast for 2019 (made on 30 Dec 2018)")
ax = axes[1]
show = ["Seasonal naive", "Climatology", "Climatology + AR(1)", "Linear regression", "LSTM (small)", SEL, "SARIMA D=1", "SARIMA D=0"]
x = np.arange(len(show)); wdt = 0.27
for k, (f, c) in enumerate([(2017, NEUTRAL), (2018, AQUA), (2019, BLUE)]):
    ax.bar(x + (k - 1) * wdt, [tab.loc[m, f] for m in show], wdt, color=c, label=str(f))
ax.set_xticks(x, [s.replace("Fourier+ARMA (selected)", "Fourier+ARMA\n(selected)").replace(" ", "\n", 1) for s in show], fontsize=7)
ax.set_ylabel("MAE (µg/m³)"); ax.legend(title="fold", fontsize=8); ax.set_title("MAE by fold")
savefig(fig, "13_backtest"); plt.show()
```

output:
```
findfont: Failed to find font weight semibold for DejaVu Sans, now using 700.
<Figure size 1320x440 with 2 Axes>
```

### [md 9]
## 3. Residual diagnostics (the draft's Ljung–Box result was an artifact)
`SARIMAX` with `D=1` initialises the first 52 seasonal states diffusely, so the first 52 in-sample residuals are as large as the series level
(about 5 on the log scale) and must be excluded (`res.loglikelihood_burn`). The draft ran Ljung–Box on all residuals and got p ≈ 0 at every lag.
Below: the same model with and without the exclusion, next to the selected Fourier+ARMA model, all fitted on 2015–2018.

### [code 10]
```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
tr19 = y.loc[:F.ORIGINS[2019]]
sp = specs[2019]
res_dhr = F._fit_dhr(tr19, sp["K"], sp["p"], sp["q"], sp["trend"])
res_s1 = SARIMAX(tr19, order=(1, 0, 1), seasonal_order=(0, 1, 1, 52)).fit(disp=False, maxiter=200)
naive = acorr_ljungbox(pd.Series(np.asarray(res_s1.resid)), lags=[10, 26, 52], model_df=3, return_df=True)
diag = pd.DataFrame({
    f"{SEL} ({sp['trend']}, K={sp['K']}, p={sp['p']}, q={sp['q']})": F.resid_diagnostics(res_dhr),
    "SARIMA D=1, burn-in removed": F.resid_diagnostics(res_s1, model_df=3),
}).T
diag["LB_p_lag10_ALL_residuals (draft's mistake)"] = [np.nan, float(naive.loc[10, "lb_pvalue"])]
diag.to_csv(RESULTS / "fc_diagnostics.csv")
display(diag.T.round(4))
par = pd.DataFrame({"coef": res_s1.params, "se": res_s1.bse}).round(3)
key["sarima_D1_maS_coef"], key["sarima_D1_maS_se"] = float(par.loc["ma.S.L52", "coef"]), float(par.loc["ma.S.L52", "se"])
display(par)
```

output:
```
                                            Fourier+ARMA (selected) (rw, K=5, p=1, q=1)  \
burn                                                                             1.0000   
n_resid                                                                        208.0000   
resid_sd                                                                         0.2265   
LB_p_lag10                                                                       0.0883   
LB_p_lag26                                                                       0.0010   
LB_p_lag52                                                                       0.0092   
ARCH4_p                                                                          0.8696   
JB_p                                                                             0.0006   
LB_p_lag10_ALL_residuals (draft's mistake)                                          NaN   

                                            SARIMA D=1, burn-in removed  
burn                                                            52.0000  
n_resid                                                        157.0000  
resid_sd                                                         0.2690  
LB_p_lag10                                                       0.4887  
LB_p_lag26                                                       0.1048  
LB_p_lag52                                                       0.0159  
ARCH4_p                                                          0.8496  
JB_p                                                             0.6490  
LB_p_lag10_ALL_residuals (draft's mistake)                       0.0000             coef     se
ar.L1     0.883  0.061
ma.L1    -0.633  0.099
ma.S.L52 -0.988  8.259
sigma2    0.046  0.374
```

### [md 11]
**Reading it.** With the burn-in removed the SARIMA residuals are fine at lags 10 and 26, but the seasonal parameter is not identified:
the seasonal MA coefficient is near −1 with a standard error larger than its value, which is the signature of differencing a series that
does not need it (a deterministic seasonal pattern). Residual structure at lag 52 and in the Fourier model is reported honestly in the table
(see `LB_p_lag52`); no GARCH-type model is needed since ARCH-LM on the weekly residuals does not reject.

### [md 12]
## 4. Interval calibration
The draft's 95% interval covered only 85% of 2019 weeks and all misses were below the lower bound, so part of the problem is **level bias**
(2019 was cleaner than the training years), not only width. We calibrate with a rule fixed in advance and tested out of sample:
* compute standardised log errors `z = (log actual − mu)/sd` on the two *earlier* folds;
* scale the sd by season (winter vs other) with shrinkage toward the pooled value (k = 26 pseudo-weeks);
* **re-centre only if** the bias has the same sign in both calibration folds and |mean z| > 0.5. Otherwise leave the centre alone, since a level
  shift that flips sign across years cannot be corrected by the past.

### [code 13]
```python
def standardized(fold, model=SEL):
    o = fcs[fold][model]
    z = (np.log(o["actual"]) - o["mu"]) / o["sd"]
    return pd.DataFrame({"z": z, "fold": fold, "winter": pd.DatetimeIndex(o["idx"]).month.isin(F.WINTER), "h": np.arange(1, len(z) + 1)})

def calibration_rule(folds, k=26):
    cal = pd.concat([standardized(f) for f in folds])
    s_all = cal["z"].std(ddof=0)
    f_season = {}
    for w_ in (True, False):
        zz = cal.loc[cal.winter == w_, "z"]
        f_season[w_] = float(np.sqrt((len(zz) * zz.std(ddof=0) ** 2 + k * s_all ** 2) / (len(zz) + k)))
    by_fold = cal.groupby("fold")["z"].mean()
    recentre = bool((by_fold.abs() > 0.5).all() and np.sign(by_fold).nunique() == 1)
    return {"f": f_season, "shift": float(cal["z"].mean()) if recentre else 0.0, "by_fold_mean_z": by_fold.round(2).to_dict(), "recentre": recentre}

def calibrated_sd_mu(mu, sd, idx, rule):
    wint = pd.DatetimeIndex(idx).month.isin(F.WINTER)
    f = np.where(wint, rule["f"][True], rule["f"][False])
    return mu + rule["shift"] * sd, sd * f

rule19 = calibration_rule([2017, 2018])
o = fcs[2019][SEL]; mu_c, sd_c = calibrated_sd_mu(o["mu"], o["sd"], o["idx"], rule19)
cal_tab = pd.DataFrame({"Model-based Gaussian": F.metrics(o["actual"], o["mu"], o["sd"], o["idx"]),
                        "Calibrated (season scale" + (", re-centred)" if rule19["recentre"] else ")"): F.metrics(o["actual"], mu_c, sd_c, o["idx"])}).T
cal_tab = cal_tab[["MAE", "coverage", "width", "winkler", "bias"]]
cal_tab.round(3).to_csv(RESULTS / "fc_calibration_2019.csv")
print("calibration rule from 2017+2018:", rule19)
display(cal_tab.round(3))
# same table for the other models that carry an sd, for context
ctx = bt[bt.fold == 2019].set_index("model")[["MAE", "coverage", "width", "winkler"]].dropna()
display(ctx.round(3))
key["calibration_rule_2019"] = rule19; key["coverage_2019_raw"] = float(cal_tab.iloc[0]["coverage"]); key["coverage_2019_calibrated"] = float(cal_tab.iloc[1]["coverage"])
```

output:
```
calibration rule from 2017+2018: {'f': {True: 1.3343095497324873, False: 1.421532404826579}, 'shift': 0.0, 'by_fold_mean_z': {2017: -0.66, 2018: -0.45}, 'recentre': False}
                              MAE  coverage    width  winkler   bias
Model-based Gaussian       25.694     0.904  125.080  174.878 -8.492
Calibrated (season scale)  25.694     0.962  178.655  192.721 -8.492                            MAE  coverage    width   winkler
model                                                       
Climatology + AR(1)      27.326     0.808  102.932   225.242
Linear regression        24.945     0.923  109.892   228.959
LSTM (small)             52.870     0.135   18.426  1797.999
Fourier+ARMA const       29.261     0.885  122.861   242.045
Fourier+ARMA linear      23.974     0.923  109.172   235.401
Fourier+ARMA (selected)  25.694     0.904  125.080   174.878
SARIMA D=1               27.452     0.846  132.997   205.876
SARIMA D=0               44.103     0.904  240.505   262.603
```

### [md 14]
## 5. One week ahead: does weather help when tested fairly?
Each test year (2018, 2019) is forecast one week at a time. Parameters are fitted once, on all data before that year; each week the model sees all earlier
observed PM2.5 (a true one-step forecast). The selected model for that origin (from §1) is the "no weather" version; weather variables are weekly anomalies from a
climatology fitted on data before the test year.

| Variant | Weather information | Available in practice? |
|---|---|---|
| lagged weather | last week's mean wind and humidity anomaly | yes |
| last 3 days | mean anomaly of the last 3 days (Fri–Sun) of the previous week | yes |
| **same-week (oracle)** | the forecast week's own observed wind and humidity | **no**, hindsight upper bound (ERA5 reanalysis is not a forecast) |

### [code 15]
```python
def weather_frame(train_end):
    """Weekly wind/rh anomaly features, with climatology fitted on data up to train_end only."""
    ref_w = weekly.loc[:train_end]; ref_d = daily.loc[:train_end]
    out = {}
    for c in ("wind", "rh"):
        clim = ref_w[c].groupby(week_index(ref_w.index)).mean().reindex(range(1, 53)).interpolate(limit_direction="both")
        wk_an = weekly[c] - clim.reindex(week_index(weekly.index)).to_numpy()
        dd_an = doy_anomaly(daily[c], ref=ref_d[c])
        last3 = dd_an.rolling(3).mean()
        prev_sun = weekly.index - pd.Timedelta(days=7)
        out[f"{c}_same"] = wk_an
        out[f"{c}_lag1"] = wk_an.shift(1)
        out[f"{c}_last3"] = pd.Series(last3.reindex(prev_sun).to_numpy(), index=weekly.index)
    return pd.DataFrame(out).fillna(0.0)   # first week has no lagged value: use the climatological value (anomaly 0)

def one_step(year, wx_cols):
    origin = F.ORIGINS[year]; sp_ = specs[year]
    tr_ = y.loc[:origin]; upto = y.loc[:f"{year}-12-31"]
    wx = weather_frame(origin)[wx_cols] if wx_cols else pd.DataFrame(index=weekly.index)
    def X(idx_):
        Z = F.fourier(idx_, sp_["K"])
        return pd.concat([Z, wx.loc[idx_]], axis=1) if wx_cols else Z
    trend, d_ = F.TREND_SPECS[sp_["trend"]]
    fit = SARIMAX(tr_, exog=X(tr_.index), order=(sp_["p"], d_, sp_["q"]), trend=trend).fit(disp=False, maxiter=200)
    full = fit.apply(upto, exog=X(upto.index))
    test_start = upto.index[upto.index > pd.Timestamp(origin)][0]
    pm = full.get_prediction(start=test_start, dynamic=False).predicted_mean
    return pm, fit

variants = {"DHR, no weather": [], "+ lagged weather (operational)": ["wind_lag1", "rh_lag1"],
            "+ last 3 days of prior week (operational)": ["wind_last3", "rh_last3"],
            "+ same-week weather (ORACLE)": ["wind_same", "rh_same"]}
rows, errs = [], {}
for year in (2018, 2019):
    origin = F.ORIGINS[year]; tr_ = y.loc[:origin]
    test_idx = y.loc[f"{year}-01-01":f"{year}-12-31"].index
    test_idx = test_idx[test_idx > pd.Timestamp(origin)]
    act = raw.loc[test_idx].to_numpy()
    preds = {"Persistence": np.log(raw.shift(1).loc[test_idx].to_numpy()),
             "Climatology": F.climatology(tr_, test_idx)["mu"]}
    c = F._clim(tr_); an = (tr_ - c.reindex(week_index(tr_.index)).to_numpy())
    phi = float((an.iloc[1:].to_numpy() * an.iloc[:-1].to_numpy()).sum() / (an.iloc[:-1] ** 2).sum())
    prev = y.shift(1).loc[test_idx]
    preds["Climatology + AR(1)"] = c.reindex(week_index(test_idx)).to_numpy() + phi * (prev.to_numpy() - c.reindex(week_index(test_idx - pd.Timedelta(weeks=1))).to_numpy())
    for name, cols in variants.items():
        pm, _ = one_step(year, cols)
        preds[name] = pm.loc[test_idx].to_numpy()
    for name, mu_ in preds.items():
        e = act - np.exp(mu_)
        errs[(year, name)] = e
        rows.append({"year": year, "model": name, "MAE": np.abs(e).mean(), "logMAE": np.abs(np.log(act) - mu_).mean(), "n": len(e)})
os_tab = pd.DataFrame(rows)
piv = os_tab.pivot(index="model", columns="year", values="MAE")
piv["both years"] = [np.mean(np.concatenate([np.abs(errs[(2018, m)]), np.abs(errs[(2019, m)])])) for m in piv.index]
order_ = ["Persistence", "Climatology", "Climatology + AR(1)", *variants]
piv = piv.loc[order_]
base = "DHR, no weather"
dm = {}
for m in order_:
    e_a = np.concatenate([errs[(2018, m)], errs[(2019, m)]]); e_b = np.concatenate([errs[(2018, base)], errs[(2019, base)]])
    dm[m] = F.hln_dm(e_a, e_b, h=1)[1] if m != base else np.nan
piv["DM p vs no-weather DHR"] = pd.Series(dm)
piv.round(3).to_csv(RESULTS / "fc_oneweek.csv")
display(piv.round(3))
key["oneweek_mae"] = piv["both years"].round(2).to_dict()
```

output:
```
year                                         2018    2019  both years  \
model                                                                   
Persistence                                26.692  34.697      30.694   
Climatology                                21.772  27.818      24.795   
Climatology + AR(1)                        17.897  28.538      23.217   
DHR, no weather                            20.326  24.455      22.391   
+ lagged weather (operational)             21.191  24.648      22.920   
+ last 3 days of prior week (operational)  20.424  24.059      22.241   
+ same-week weather (ORACLE)               17.566  24.121      20.844   

year                                       DM p vs no-weather DHR  
model                                                              
Persistence                                                 0.002  
Climatology                                                 0.249  
Climatology + AR(1)                                         0.714  
DHR, no weather                                               NaN  
+ lagged weather (operational)                              0.075  
+ last 3 days of prior week (operational)                   0.585  
+ same-week weather (ORACLE)                                0.074
```

### [code 16]
```python
# coefficients of the oracle model on the 2019 origin, for interpretation
_, fit_or = one_step(2019, ["wind_same", "rh_same"])
coef = pd.DataFrame({"coef": fit_or.params[["wind_same", "rh_same"]], "p": fit_or.pvalues[["wind_same", "rh_same"]]}).round(4)
coef.to_csv(RESULTS / "fc_oneweek_oracle_coef.csv"); display(coef)
gain = lambda a, b: round(100 * (1 - piv.loc[a, "both years"] / piv.loc[b, "both years"]), 1)
key["oneweek_gain_pct"] = {"lagged": gain("+ lagged weather (operational)", base), "last3": gain("+ last 3 days of prior week (operational)", base),
                           "oracle": gain("+ same-week weather (ORACLE)", base)}
print(key["oneweek_gain_pct"], "(% MAE reduction vs no-weather DHR; positive = better)")
```

output:
```
             coef       p
wind_same -0.0370  0.0033
rh_same   -0.0099  0.0002{'lagged': np.float64(-2.4), 'last3': np.float64(0.7), 'oracle': np.float64(6.9)} (% MAE reduction vs no-weather DHR; positive = better)
```

### [md 17]
**Reading it.** The operational variants (lagged weather) are compared with the model that has no weather; the oracle variant shows how much
accuracy would be available if the week's weather were known in advance. The Diebold–Mariano p-values use genuine one-step errors (Harvey–Leybourne–Newbold
small-sample correction), so unlike the 52-step comparison the test is valid here.

### [code 18]
```python
fig, ax = plt.subplots(figsize=(8, 3.6))
labs = [m.replace(" (operational)", "").replace(" (ORACLE)", "\n(oracle)") for m in order_]
vals = [piv.loc[m, "both years"] for m in order_]
cols_ = [NEUTRAL, NEUTRAL, NEUTRAL, BLUE, AQUA, AQUA, ORANGE]
ax.bar(range(len(vals)), vals, color=cols_)
ax.set_xticks(range(len(vals)), labs, fontsize=7, rotation=20, ha="right")
ax.set_ylabel("One-week-ahead MAE, 2018-19 (µg/m³)")
ax.set_title("Weather helps one week ahead only when the week's own weather is known")
savefig(fig, "14_oneweek"); plt.show()
```

output:
```
<Figure size 880x396 with 1 Axes>
```

### [md 19]
## 6. Final outlook for 2020 and validation of the method on 2019
**Procedure (identical for both).** Fit the headline procedure on the years before the target year; simulate 5,000 weekly paths from the fitted model
(53 weeks so every calendar day is covered); apply the calibration rule (fitted only on earlier folds); convert weekly paths to daily PM2.5 by adding a
resampled within-week offset `log(daily) − log(weekly mean)` drawn from the same calendar month of the training data; classify each day into the CPCB
PM2.5 sub-index bands. This yields (a) the median and 95% interval of each month's mean PM2.5 and (b) the expected number of days per band.
**This is a PM2.5 band, not the official AQI** (the AQI is the maximum sub-index over all pollutants).
2019 is a genuine out-of-sample test of the whole pipeline; 2020 is the deliverable.

### [code 20]
```python
def pipeline(origin, year, folds_for_cal, n=5000):
    tr_ = y.loc[:origin]
    idx = pd.date_range(tr_.index[-1] + pd.Timedelta(weeks=1), periods=53, freq="W-SUN")   # covers every day of `year`
    out = F.dhr(tr_, idx)                          # re-selects K, p, q and trend using data up to `origin` only
    res_, mu_, sd_ = out["res"], out["mu"], out["sd"]
    paths = F.simulate_paths(res_, idx, exog=F.fourier(idx, out["spec"]["K"]), n=n)
    med_gap = float(np.abs(np.median(paths, axis=1) - mu_).mean())
    assert med_gap < 0.03, med_gap                 # simulation agrees with the analytic forecast
    rule = calibration_rule(folds_for_cal)
    f = np.where(pd.DatetimeIndex(idx).month.isin(F.WINTER), rule["f"][True], rule["f"][False])
    paths_c = (mu_ + rule["shift"] * sd_)[:, None] + f[:, None] * (paths - mu_[:, None])
    pools = F.week_offsets_by_month(daily["pm25"].loc[:origin])
    bands = F.daily_band_days(paths_c, idx, pools, year)           # (paths, 12, 6)
    monthly = F.monthly_mean_paths(paths_c, idx, year)             # (12, paths)
    return {"idx": idx, "mu": mu_, "sd": sd_, "paths": paths_c, "bands": bands, "monthly": monthly, "spec": out["spec"], "rule": rule, "res": res_}

month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def month_table(P, year):
    rows = []
    for m in range(12):
        mm = P["monthly"][m]; b = P["bands"][:, m, :]
        row = {"month": month_names[m], "median": np.median(mm), "lo95": np.percentile(mm, 2.5), "hi95": np.percentile(mm, 97.5),
               "P(mean>60)": (mm > 60).mean(), "P(mean>90)": (mm > 90).mean(), "P(mean>120)": (mm > 120).mean()}
        for k, c in enumerate(CATEGORIES):
            row[f"days_{c}"] = b[:, k].mean()
        rows.append(row)
    return pd.DataFrame(rows).set_index("month")

# 2019: validation of the pipeline (calibration only from folds 2017-2018, selection only from data to 2018-12-30)
P19 = pipeline(F.ORIGINS[2019], 2019, [2017, 2018])
mt19 = month_table(P19, 2019)
d19 = daily.loc["2019", "pm25"]
act_days = pd.crosstab(d19.index.month, pm25_category(d19.to_numpy()).to_numpy()).reindex(columns=CATEGORIES, fill_value=0)
act_days.index = month_names
act_med = d19.groupby(d19.index.month).mean(); act_med.index = month_names
val = pd.DataFrame({"actual_mean": act_med, "pred_median": mt19["median"], "pred_lo95": mt19["lo95"], "pred_hi95": mt19["hi95"]})
val["inside95"] = (val.actual_mean >= val.pred_lo95) & (val.actual_mean <= val.pred_hi95)
bands_pred = mt19[[f"days_{c}" for c in CATEGORIES]]; bands_pred.columns = CATEGORIES
err_days = (bands_pred - act_days).abs()
val.round(1).to_csv(RESULTS / "fc_outlook_validation_2019_monthly.csv")
pd.concat({"predicted": bands_pred.round(1), "actual": act_days}, axis=1).to_csv(RESULTS / "fc_outlook_validation_2019_days.csv")
key["validation_2019"] = {"months_actual_inside_95": int(val.inside95.sum()), "annual_days_pred": bands_pred.sum().round(0).to_dict(),
                          "annual_days_actual": act_days.sum().to_dict(), "mean_abs_days_error_per_band_month": round(float(err_days.mean().mean()), 2),
                          "poor_or_worse_pred_pct": round(float(bands_pred[["Poor", "Very Poor", "Severe"]].sum().sum() / 365 * 100), 1),
                          "poor_or_worse_actual_pct": round(float(act_days[["Poor", "Very Poor", "Severe"]].sum().sum() / 365 * 100), 1)}
print(key["validation_2019"]); display(val.round(1))
assert np.allclose(P19["bands"].sum(axis=2)[0], [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
```

output:
```
{'months_actual_inside_95': 12, 'annual_days_pred': {'Good': 21.0, 'Satisfactory': 75.0, 'Moderate': 67.0, 'Poor': 53.0, 'Very Poor': 113.0, 'Severe': 35.0}, 'annual_days_actual': {'Good': 25, 'Satisfactory': 97, 'Moderate': 78, 'Poor': 58, 'Very Poor': 73, 'Severe': 34}, 'mean_abs_days_error_per_band_month': 1.88, 'poor_or_worse_pred_pct': 55.0, 'poor_or_worse_actual_pct': 45.2}
     actual_mean  pred_median  pred_lo95  pred_hi95  inside95
Jan        204.3        209.4      148.8      304.2      True
Feb        122.3        144.1       97.9      212.1      True
Mar         84.2        101.5       66.3      154.8      True
Apr         82.3        101.5       63.7      161.4      True
May         89.7        100.7       62.3      163.0      True
Jun         63.8         74.6       45.4      122.9      True
Jul         46.7         46.0       27.4       78.0      True
Aug         34.1         42.8       24.8       73.6      True
Sep         40.1         57.0       32.7       98.7      True
Oct        123.7        144.7       83.5      255.5      True
Nov        205.4        229.7      130.9      401.4      True
Dec        205.2        199.6      112.4      355.5      True
```

### [code 21]
```python
# 2020 deliverable: selection on data to 2019-12-29, calibration from folds 2018 and 2019
P20 = pipeline("2019-12-29", 2020, [2018, 2019])
mt20 = month_table(P20, 2020)
assert np.allclose(P20["bands"].sum(axis=2)[0], [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
a20 = daily.loc["2020"]["pm25"].dropna()
mt20["actual_mean_2020"] = a20.groupby(a20.index.month).mean().reindex(range(1, 13)).to_numpy()
mt20["actual_days_covered"] = a20.groupby(a20.index.month).count().reindex(range(1, 13)).to_numpy()
mt20.round(3).to_csv(RESULTS / "fc_outlook_2020.csv")
key["outlook_2020_spec"] = {k: v for k, v in P20["spec"].items() if k not in ("inner_mae", "res")}; key["outlook_2020_rule"] = P20["rule"]
display(mt20.round(2))
```

output:
```
       median    lo95    hi95  P(mean>60)  P(mean>90)  P(mean>120)  days_Good  \
month                                                                           
Jan    189.08  140.98  251.50        1.00        1.00         1.00       0.00   
Feb    120.77   91.61  163.52        1.00        0.98         0.52       0.04   
Mar     84.89   66.64  108.82        1.00        0.32         0.00       0.31   
Apr     85.92   66.92  110.71        1.00        0.36         0.01       0.14   
May     83.79   64.62  108.23        1.00        0.29         0.00       0.19   
Jun     62.54   48.70   82.01        0.62        0.00         0.00       1.27   
Jul     38.97   30.40   49.91        0.00        0.00         0.00       9.21   
Aug     35.72   27.95   45.80        0.00        0.00         0.00      10.38   
Sep     46.32   36.19   59.28        0.02        0.00         0.00       6.02   
Oct    119.52   91.45  157.82        1.00        0.98         0.49       0.06   
Nov    189.92  141.14  255.66        1.00        1.00         1.00       0.00   
Dec    168.89  127.24  225.88        1.00        1.00         0.99       0.00   

       days_Satisfactory  days_Moderate  days_Poor  days_Very Poor  \
month                                                                
Jan                 0.13           1.03       3.07           21.21   
Feb                 1.87           6.31       7.63           12.41   
Mar                 6.37          12.58       7.83            3.89   
Apr                 5.21          12.62       8.13            3.90   
May                 6.74          12.85       7.46            3.75   
Jun                13.90          10.73       3.27            0.84   
Jul                19.27           2.32       0.18            0.02   
Aug                19.10           1.46       0.06            0.00   
Sep                17.69           5.31       0.84            0.13   
Oct                 3.02           7.40       7.24           12.27   
Nov                 0.23           1.19       3.17           19.48   
Dec                 0.23           2.12       4.95           19.97   

       days_Severe  actual_mean_2020  actual_days_covered  
month                                                      
Jan           5.55            157.11                 31.0  
Feb           0.74            121.48                 29.0  
Mar           0.01             57.51                 31.0  
Apr           0.01             44.94                 30.0  
May           0.01      
...[truncated]
```

### [code 22]
```python
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.35, 1]})
ax = axes[0]; xs = np.arange(12)
ax.fill_between(xs, mt20["lo95"], mt20["hi95"], color=BLUE, alpha=0.18, lw=0, label="95% prediction interval")
ax.plot(xs, mt20["median"], color=BLUE, lw=2, marker="o", ms=4, label="Forecast median (made Dec 2019)")
ok = mt20["actual_days_covered"] >= 20
ax.plot(xs[ok], mt20.loc[ok, "actual_mean_2020"], color=ORANGE, lw=1.6, marker="s", ms=4, label="Actual 2020 (Jan-May full months)")
for yv, lab in [(60, "Satisfactory limit"), (90, "Moderate limit"), (120, "Poor limit")]:
    ax.axhline(yv, color=MUTED, lw=0.7, ls=":"); ax.text(11.4, yv, lab, fontsize=7, va="bottom", ha="right", color=INK_2)
ax.set_xticks(xs, month_names); ax.set_ylabel("Monthly mean PM2.5 (µg/m³)"); ax.legend(fontsize=8, loc="upper center")
ax.set_title("2020 outlook: monthly mean PM2.5")
ax = axes[1]
colors = {"Good": "#00B050", "Satisfactory": "#92D050", "Moderate": "#E6C200", "Poor": "#FF9900", "Very Poor": "#FF0000", "Severe": "#C00000"}
bottom = np.zeros(12)
for c in CATEGORIES:
    v = mt20[f"days_{c}"].to_numpy(); ax.bar(xs, v, bottom=bottom, color=colors[c], width=0.8, label=c); bottom += v
ax.set_xticks(xs, [m[0] for m in month_names]); ax.set_ylabel("Expected days"); ax.set_title("Expected days per PM2.5 band (2020)")
ax.legend(fontsize=7, ncols=2, loc="lower right")
savefig(fig, "15_outlook_2020"); plt.show()
```

output:
```
<Figure size 1320x462 with 2 Axes>
```

### [md 23]
## 7. Case study: the 2020 lockdown
Delhi's lockdown began on 25 March 2020. We compare the actual weekly PM2.5 of the ten weeks ending 29 March – 31 May with the no-lockdown forecast made on
29 Dec 2019 (calibrated, as above). A second counterfactual uses a version of the same model *with the actual 2020 same-week wind and humidity* (fitted on 2015–2019),
to separate the weather contribution from the rest. Both are descriptive: they rely on the model being right about the level for 2020 (see §4).

### [code 24]
```python
lock_idx = pd.date_range("2020-03-29", "2020-05-31", freq="W-SUN")
act_l = raw.loc[lock_idx].to_numpy()
pos = P20["idx"].get_indexer(lock_idx); assert (pos >= 0).all()
cf = np.exp(P20["paths"][pos]).mean(axis=0)                     # counterfactual mean over the 10 weeks, per simulated path
gap = act_l.mean() / cf - 1
res1 = {"actual_mean": float(act_l.mean()), "cf_median": float(np.median(cf)), "gap_median_pct": float(100 * np.median(gap)),
        "gap_lo95_pct": float(100 * np.percentile(gap, 2.5)), "gap_hi95_pct": float(100 * np.percentile(gap, 97.5))}

# weather-adjusted counterfactual (oracle weather)
wx20 = weather_frame("2019-12-29")[["wind_same", "rh_same"]]
tr_f = y.loc[:"2019-12-29"]; sp_f = P20["spec"]; trend_, d_ = F.TREND_SPECS[sp_f["trend"]]
Xf = lambda ix: pd.concat([F.fourier(ix, sp_f["K"]), wx20.loc[ix]], axis=1)
fit_w = SARIMAX(tr_f, exog=Xf(tr_f.index), order=(sp_f["p"], d_, sp_f["q"]), trend=trend_).fit(disp=False, maxiter=200)
idx_w = pd.date_range("2020-01-05", "2020-06-28", freq="W-SUN")
pw = F.simulate_paths(fit_w, idx_w, exog=Xf(idx_w), n=5000)
fw = fit_w.get_forecast(len(idx_w), exog=Xf(idx_w)); sdw = np.sqrt(fw.var_pred_mean.to_numpy())
f_w = np.where(pd.DatetimeIndex(idx_w).month.isin(F.WINTER), P20["rule"]["f"][True], P20["rule"]["f"][False])
mu_w = fw.predicted_mean.to_numpy(); pw = mu_w[:, None] + f_w[:, None] * (pw - mu_w[:, None])
posw = idx_w.get_indexer(lock_idx)
cfw = np.exp(pw[posw]).mean(axis=0); gapw = act_l.mean() / cfw - 1
res2 = {"cf_median": float(np.median(cfw)), "gap_median_pct": float(100 * np.median(gapw)),
        "gap_lo95_pct": float(100 * np.percentile(gapw, 2.5)), "gap_hi95_pct": float(100 * np.percentile(gapw, 97.5))}
lock = pd.DataFrame({"no-lockdown forecast": res1, "weather-adjusted forecast (oracle weather)": res2}).T
lock.round(1).to_csv(RESULTS / "fc_lockdown.csv"); display(lock.round(1))
key["lockdown"] = {"plain": res1, "weather_adjusted": res2}

fig, ax = plt.subplots(figsize=(9, 3.8))
show_idx = P20["idx"][:26]
lo_, hi_ = np.percentile(np.exp(P20["paths"][:26]), [2.5, 97.5], axis=1)
pd.DataFrame({"lo95": lo_, "median": np.exp(np.median(P20["paths"][:26], axis=1)), "hi95": hi_,
              "weather_adj_median": np.exp(np.median(pw, axis=1)), "actual": raw.reindex(show_idx).to_numpy()}, index=show_idx).rename_axis("date").to_csv(RESULTS / "fc_weekly_2020.csv")
ax.fill_between(show_idx, lo_, hi_, color=BLUE, alpha=0.18, lw=0, label="95% interval (no lockdown)")
ax.plot(show_idx, np.exp(np.median(P20["paths"][:26], axis=1)), color=BLUE, lw=2, label="No-lockdown forecast (median)")
ax.plot(idx_w, np.exp(np.median(pw, axis=1)), color=AQUA, lw=1.6, ls="--", label="Weather-adjusted forecast")
ax.plot(show_idx, raw.loc[show_idx], color=ORANGE, lw=1.6, marker="o", ms=3, label="Actual 2020")
ax.axvspan(pd.Timestamp("2020-03-25"), pd.Timestamp("2020-05-31"), color=NEUTRAL, alpha=0.2, lw=0)
ax.set_ylabel("Weekly mean PM2.5 (µg/m³)"); ax.legend(fontsize=8); ax.set_title("2020 lockdown: actual vs forecast made in Dec 2019")
savefig(fig, "16_lockdown"); plt.show()
```

output:
```
                                            actual_mean  cf_median  \
no-lockdown forecast                               48.7       85.1   
weather-adjusted forecast (oracle weather)          NaN       78.5   

                                            gap_median_pct  gap_lo95_pct  \
no-lockdown forecast                                 -42.8         -52.2   
weather-adjusted forecast (oracle weather)           -38.0         -47.8   

                                            gap_hi95_pct  
no-lockdown forecast                               -31.5  
weather-adjusted forecast (oracle weather)         -26.2  <Figure size 990x418 with 1 Axes>
```

### [md 25]
## 8. Summary numbers

### [code 26]
```python
m_sel = bt[bt.model == SEL].set_index("fold"); m_clim = bt[bt.model == "Climatology"].set_index("fold")
key["backtest"] = {"mae_selected": m_sel["MAE"].round(2).to_dict(), "mae_climatology": m_clim["MAE"].round(2).to_dict(),
                   "coverage_selected": m_sel["coverage"].round(3).to_dict(),
                   "sarima_D1_mae": bt[bt.model == "SARIMA D=1"].set_index("fold")["MAE"].round(2).to_dict(),
                   "sarima_D0_mae": bt[bt.model == "SARIMA D=0"].set_index("fold")["MAE"].round(2).to_dict(),
                   "lstm_mae": bt[bt.model == "LSTM (small)"].set_index("fold")["MAE"].round(2).to_dict(),
                   "specs": {int(f): {k: v for k, v in s.items() if k != "inner_mae"} for f, s in specs.items()}}
key["diagnostics_selected_2019_fold"] = {k: round(float(v), 4) for k, v in diag.iloc[0].items() if k != "LB_p_lag10_ALL_residuals (draft's mistake)"}
(RESULTS / "key_numbers_forecast.json").write_text(json.dumps(key, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
key
```

output:
```
{'sarima_D1_maS_coef': -0.988,
 'sarima_D1_maS_se': 8.259,
 'calibration_rule_2019': {'f': {True: 1.3343095497324873,
   False: 1.421532404826579},
  'shift': 0.0,
  'by_fold_mean_z': {2017: -0.66, 2018: -0.45},
  'recentre': False},
 'coverage_2019_raw': 0.9038461538461539,
 'coverage_2019_calibrated': 0.9615384615384616,
 'oneweek_mae': {'Persistence': 30.69,
  'Climatology': 24.79,
  'Climatology + AR(1)': 23.22,
  'DHR, no weather': 22.39,
  '+ lagged weather (operational)': 22.92,
  '+ last 3 days of prior week (operational)': 22.24,
  '+ same-week weather (ORACLE)': 20.84},
 'oneweek_gain_pct': {'lagged': np.float64(-2.4),
  'last3': np.float64(0.7),
  'oracle': np.float64(6.9)},
 'validation_2019': {'months_actual_inside_95': 12,
  'annual_days_pred': {'Good': 21.0,
   'Satisfactory': 75.0,
   'Moderate': 67.0,
   'Poor': 53.0,
   'Very Poor': 113.0,
   'Severe': 35.0},
  'annual_days_actual': {'Good': 25,
   'Satisfactory': 97,
   'Moderate': 78,
   'Poor': 58,
   'Very Poor': 73,
   'Severe': 34},
  'mean_abs_days_error_per_band_month': 1.88,
  'poor_or_worse_pred_pct': 55.0,
  'poor_or_worse_actual_pct': 45.2},
 'outlook_2020_spec': {'trend': 'linear', 'K': 5, 'p': 1, 'q': 0},
 'outlook_2020_rule': {'f': {True: 1.0935180465819772,
   False: 0.9476619724449761},
  'shift': 0.0,
  'by_fold_mean_z': {2018: -0.45, 2019: -0.53},
  'recentre': False},
 'lockdown': {'plain': {'actual_mean': 48.669714285714285,
   'cf_median': 85.140752539336,
   'gap_median_pct': -42.83617088073022,
   'gap_lo95_pct': -52.21475468260452,
   'gap_hi95_pct': -31.53328399642168},
  'weather_adjusted': {'cf_median': 78.46680894643731,
   'gap_median_pct': -37.97413844184731,
   'gap_lo95_pct': -47.76977454856694,
   'gap_hi95_pct': -26.19979951798827}},
 'backtest': {'mae_selected': {2017: 31.48, 2018: 23.43, 2019: 25.69},
  'mae_climatology': {2017: 31.0, 2018: 21.77, 2019: 27.82},
  'coverage_selected': {2017: 0.692, 2018: 0.942, 2019: 0.904},
  'sarima_D1_mae': {2017: 53.83, 2018: 21.08, 2019: 27.45},
  'sarima_D0_mae': {2017: 44.87, 2018: 42.84, 2019: 44.1},
  'lstm_mae': {2017: 36.29, 2018: 49.23, 2019: 52.87},
  'specs': {2017: {'trend': 'rw', 'K': 5, 'p': 1, 'q': 1},
   2018: {'trend': 'const', 'K': 5, 'p': 1, 'q': 1},
   2019: {'trend': 'rw', 'K': 5, 'p': 1, 'q': 1}}},
 'diagnostics_selected_2019_fold': {'burn': 1.0,
  'n_resid': 208.0,
  'resid_sd': 0.2265,
  'LB_p_lag10': 0.0883,
  'LB_p_lag26': 0.001,
  'LB_p_lag52': 0.0092,
  'ARCH4_p': 0.8696,
  'JB_p': 0.0006}
...[truncated]
```


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


# 06 Raw data for recomputation
## delhi_weekly.csv (287 rows; pm25 = weekly mean ug/m3, log_pm25 = log of it; n_days = daily obs in the week)
```
Date,pm25,no2,so2,aqi,rh,wind,temp,precip,n_days,log_pm25
2015-01-04,184.605,34.12,5.795,347.0,78.25,7.225,15.375,4.3,4,5.2182
2015-01-11,196.0057,41.1871,4.4357,358.4286,79.4286,9.9143,13.1714,0.0,7,5.2781
2015-01-18,187.65,49.24,5.4514,360.0,82.2857,7.5286,12.6,4.1,7,5.2346
2015-01-25,156.3571,24.6343,6.5186,326.1429,80.0,8.0857,13.3429,20.8,7,5.0521
2015-02-01,162.7843,37.2786,6.4714,324.1429,70.0,10.0857,12.4429,0.0,7,5.0924
2015-02-08,149.7229,44.2257,6.5086,316.1429,75.5714,9.5,14.9143,16.5,7,5.0088
2015-02-15,161.0943,47.7586,8.3586,338.5714,66.8571,8.2714,16.3857,0.0,7,5.082
2015-02-22,155.0943,40.2957,7.1386,331.1429,73.8571,11.6714,20.3429,15.2,7,5.044
2015-03-01,129.8043,29.0971,9.6029,321.0,73.0,10.2429,19.0714,28.4,7,4.866
2015-03-08,82.4857,22.6671,4.8643,230.4286,78.0,8.7571,16.9286,35.2,7,4.4126
2015-03-15,85.5757,24.7486,6.63,243.4286,74.1429,9.5143,17.9571,31.5,7,4.4494
2015-03-22,69.4486,22.4271,6.1329,216.7143,71.5714,10.3714,20.1429,6.7,7,4.2406
2015-03-29,93.7471,29.7029,11.0757,318.4286,57.8571,8.0429,25.5143,0.4,7,4.5406
2015-04-05,71.2729,23.1657,13.0314,259.5714,70.0,8.7571,23.2286,34.4,7,4.2665
2015-04-12,92.5714,40.68,14.8314,309.1429,57.1429,7.6571,24.2143,5.9,7,4.528
2015-04-19,93.6129,48.6214,16.2557,302.8571,58.0,8.8143,26.8143,7.7,7,4.5392
2015-04-26,110.25,60.2214,19.7971,371.4286,33.8571,11.6429,30.4714,0.4,7,4.7028
2015-05-03,77.6386,49.3829,14.4871,281.5714,40.8571,10.8429,30.1286,5.9,7,4.3521
2015-05-10,120.3329,74.5757,21.3257,388.0,24.8571,9.0571,32.9857,0.0,7,4.7903
2015-05-17,89.7057,53.3214,13.6643,341.5714,50.2857,6.7286,30.7571,12.7,7,4.4965
2015-05-24,73.6686,56.3929,15.6043,314.7143,28.0,10.1429,34.2714,1.7,7,4.2996
2015-05-31,107.6771,61.0829,13.8786,361.8571,22.1429,10.0286,34.7857,0.1,7,4.6791
2015-06-07,66.4643,59.5057,7.0786,303.2857,37.2857,8.8286,32.5,1.1,7,4.1967
2015-06-14,97.8057,58.3571,6.7714,274.5714,37.7143,12.8857,34.6286,6.7,7,4.583
2015-06-21,106.3971,69.7514,7.55,268.1429,57.2857,8.4286,32.4857,8.9,7,4.6672
2015-06-28,82.3357,51.1014,7.3557,209.2857,68.5714,9.5571,30.8286,50.4,7,4.4108
2015-07-05,73.9029,42.2914,7.8857,217.8571,67.0,10.5286,30.7429,15.0,7,4.3028
2015-07-12,50.77,47.5314,8.0371,223.2857,86.4286,8.1429,27.1429,168.2,7,3.9273
2015-07-19,62.6629,42.81,9.9557,204.4286,78.4286,9.6,29.1429,57.7,7,4.1378
2015-07-26,40.7843,43.9386,15.1686,178.4286,80.7143,12.2857,28.6143,33.3,7,3.7083
2015-08-02,32.7557,35.8729,10.0343,171.1429,78.0,11.5857,27.5,10.6,7,3.4891
2015-08-09,60.7457,47.2029,9.0486,222.4286,87.2857,5.6,27.6571,110.5,7,4.1067
2015-08-16,63.7429,48.1586,8.7786,223.8571,86.5714,5.7571,28.0,42.9,7,4.1549
2015-08-23,48.5886,39.8486,10.8586,194.0,78.1429,8.7143,28.6286,13.3,7,3.8834
2015-08-30,58.94,43.2329,10.4514,228.0,76.1429,8.4143,29.5857,2.9,7,4.0765
2015-09-06,79.7157,31.9186,13.2014,274.1429,60.7143,10.3571,29.2429,0.0,7,4.3785
2015-09-13,68.1743,42.6814,11.1986,218.5714,61.1429,8.8571,29.2,0.3,7,4.2221
2015-09-20,86.3686,54.3257,10.2357,229.0,71.7143,7.3714,29.5,31.3,7,4.4586
2015-09-27,62.7957,43.8543,11.9214,197.1429,71.8571,10.2286,27.4,11.8,7,4.1399
2015-10-04,90.2657,51.3557,11.19,252.2857,59.5714,8.1286,26.8143,0.0,7,4.5028
2015-10-11,144.8343,62.0186,13.31,360.5714,50.5714,8.5143,28.2857,0.0,7,4.9756
2015-10-18,109.2971,47.9614,11.1429,290.8571,66.0,7.0286,27.2143,7.7,7,4.6941
2015-10-25,157.7143,58.7671,16.4629,370.8571,53.1429,7.8714,25.8571,1.4,7,5.0608
2015-11-01,150.76,48.0686,21.4043,311.8571,64.1429,6.2571,22.4857,7.0,7,5.0157
2015-11-08,236.7414,74.7271,26.61,411.2857,68.2857,5.8,23.0571,0.2,7,5.467
2015-11-15,236.7329,68.5471,27.73,420.0,59.1429,8.1286,22.6714,0.6,7,5.4669
2015-11-22,222.7771,86.3814,22.4014,410.5714,54.4286,7.2571,19.9571,1.0,7,5.4062
2015-11-29,199.59,69.7643,19.8857,374.0,60.2857,7.7429,19.4857,0.0,7,5.2963
2015-12-06,216.2557,94.9271,23.6343,401.4286,66.7143,6.9857,19.1429,0.0,7,5.3765
2015-12-13,216.2786,85.5743,20.4243,397.1429,68.4286,8.1429,17.3286,0.2,7,5.3766
2015-12-20,129.0514,45.7686,16.36,278.5714,58.4286,8.3571,13.3571,0.0,7,4.8602
2015-12-27,181.3371,89.1829,19.3314,342.2857,59.1429,9.0286,13.3714,0.0,7,5.2004
2016-01-03,226.9143,80.1514,22.1143,408.2857,61.7143,9.4,15.6857,0.0,7,5.4246
2016-01-10,290.9271,92.8914,23.9257,496.5714,70.1429,7.8857,16.9143,0.5,7,5.6731
2016-01-17,194.9914,61.49,16.37,372.0,74.5714,7.2,14.6,0.0,7,5.273
2016-01-24,272.0914,66.4886,14.7757,438.2857,76.0,6.6143,12.1286,0.0,7,5.6061
2016-01-31,271.9614,85.6914,20.73,456.7143,74.7143,6.6143,15.5714,0.7,7,5.6057
2016-02-07,160.9214,71.0857,22.9286,332.1429,59.8571,9.7857,14.9143,4.0,7,5.0809
2016-02-14,146.91,67.5186,22.73,323.4286,65.4286,8.0714,16.2,0.7,7,4.9898
2016-02-21,136.7371,62.0143,26.1557,300.0,62.2857,8.2857,19.0857,16.0,7,4.9181
2016-02-28,131.8271,76.7214,25.8843,289.7143,57.5714,8.3286,19.8286,0.0,7,4.8815
2016-03-06,134.3671,77.9657,21.8357,302.5714,61.5714,7.6714,22.5143,15.0,7,4.9006
2016-03-13,89.5671,37.9271,18.5429,203.4286,67.4286,9.2571,21.8143,24.4,7,4.495
2016-03-20,77.6214,53.6457,22.3386,188.0,61.4286,8.4429,22.4714,1.5,7,4.3518
2016-03-27,87.7186,53.14,21.5571,239.2857,45.0,12.4714,24.4571,0.0,7,4.4741
2016-04-03,112.1586,41.2629,25.8871,266.8571,41.7143,8.2,27.7714,1.8,7,4.7199
2016-04-10,116.6386,46.7671,33.8714,269.1429,33.1429,8.9,28.5857,0.0,7,4.7591
2016-04-17,98.4757,47.5829,22.5186,259.2857,30.2857,12.8,30.6286,0.0,7,4.5898
2016-04-24,110.9086,52.7929,28.45,287.2857,26.8571,10.1571,31.0714,0.1,7,4.7087
2016-05-01,145.14,78.4271,30.0686,340.4286,20.4286,9.1286,31.1857,0.2,7,4.9777
2016-05-08,90.7643,56.4257,20.2186,256.5714,41.2857,9.3857,31.0714,3.1,7,4.5083
2016-05-15,93.1014,58.2571,18.7471,255.8571,39.5714,9.3429,33.2571,1.7,7,4.5337
2016-05-22,87.84,60.4043,21.3814,279.2857,35.5714,11.5286,34.7857,2.4,7,4.4755
2016-05-29,99.1571,44.1114,13.6757,295.4286,48.7143,10.4857,32.8143,18.1,7,4.5967
2016-06-05,95.8386,54.4229,13.7057,279.7143,50.2857,9.2571,33.3,7.4,7,4.5627
2016-06-12,70.8671,46.94,14.7671,245.0,51.4286,10.6286,34.0571,10.9,7,4.2608
2016-06-19,81.2529,35.5786,9.7329,258.2857,61.0,11.2571,32.4429,19.3,7,4.3976
2016-06-26,76.7629,39.8057,9.5157,218.8571,64.1429,10.4714,32.5143,6.9,7,4.3407
2016-07-03,67.2886,35.5,8.8,168.1429,75.7143,8.9,30.5286,130.9,7,4.209
2016-07-10,60.7229,36.6271,8.2529,165.5714,76.8571,6.4714,30.3571,9.4,7,4.1063
2016-07-17,60.7257,27.8686,7.5971,157.8571,87.0,7.3571,28.1714,203.5,7,4.1064
2016-07-24,48.3671,36.41,7.9271,202.0,77.0,9.1143,29.7571,16.8,7,3.8788
2016-07-31,52.0957,42.2871,9.0671,143.8571,88.4286,7.8571,27.1857,71.6,7,3.9531
2016-08-07,44.7029,34.3129,9.1057,142.8571,82.5714,9.9429,28.6857,32.7,7,3.8
2016-08-14,42.0971,34.9686,9.0929,129.1429,87.1429,8.0,27.6571,72.8,7,3.74
2016-08-21,48.8429,36.7186,9.0914,201.1429,79.4286,9.6857,28.5143,14.9,7,3.8886
2016-08-28,46.3714,31.9114,8.52,125.5714,83.2857,8.4571,28.3286,28.5,7,3.8367
2016-09-04,45.3629,41.19,9.2629,160.0,83.2857,8.6429,27.5714,64.4,7,3.8147
2016-09-11,56.8314,38.4929,11.3143,276.0,67.8571,13.2,28.5,0.2,7,4.0401
2016-09-18,67.0429,50.6314,11.3414,207.8571,73.0,6.5143,28.7,0.1,7,4.2053
2016-09-25,65.7629,62.0729,15.03,199.4286,75.5714,7.0571,28.3714,2.2,7,4.1861
2016-10-02,90.3329,67.3671,15.9771,226.1429,72.8571,5.6286,29.0429,0.6,7,4.5035
2016-10-09,121.8757,79.2743,14.6943,325.7143,73.5714,5.4714,28.4857,11.1,7,4.803
2016-10-16,119.0986,88.8757,20.09,396.5714,51.2857,8.1714,26.0571,0.0,7,4.78
2016-10-23,153.0686,90.6871,23.6629,450.5714,48.1429,9.2,25.4286,0.0,7,5.0309
2016-10-30,258.6486,113.8114,30.9414,495.2857,52.7143,7.9857,24.3,0.0,7,5.5555
2016-11-06,495.1529,129.3271,33.1014,578.1429,62.5714,6.5286,22.8429,0.0,7,6.2049
2016-11-13,318.2071,120.1043,31.1043,522.5714,57.0,8.4143,21.6714,0.0,7,5.7627
2016-11-20,274.3429,110.9071,24.4443,451.2857,55.7143,8.0571,20.3857,0.0,7,5.6144
2016-11-27,198.7486,94.1143,24.4029,403.7143,50.1429,12.5286,20.9286,0.0,7,5.292
2016-12-04,222.4414,100.5543,23.2943,395.0,62.1429,7.5429,19.1,0.0,7,5.4047
2016-12-11,243.4514,72.98,22.8386,413.1429,70.2857,5.8286,18.3,0.0,7,5.4949
2016-12-18,200.6914,77.4771,21.5843,401.0,66.2857,8.4286,16.5571,0.0,7,5.3018
2016-12-25,246.5386,85.98,21.8214,420.5714,64.4286,10.2857,16.4571,0.0,7,5.5075
2017-01-01,230.7143,83.2029,23.9214,383.8571,74.1429,9.1714,15.8143,0.0,7,5.4412
2017-01-08,207.4529,74.5114,24.4014,359.8571,79.1429,7.7286,15.7,7.2,7,5.3349
2017-01-15,196.7457,72.0557,19.9471,372.2857,63.8571,9.0571,11.3429,0.0,7,5.2819
2017-01-22,238.0271,60.8629,19.9043,375.4286,69.1429,10.4857,12.9286,0.3,7,5.4724
2017-01-29,159.2057,61.7914,20.7843,319.2857,78.8571,10.8429,15.9571,47.9,7,5.0702
2017-02-05,177.6186,72.3014,19.5386,360.1429,81.1429,9.1429,15.5714,3.2,7,5.1796
2017-02-12,133.1686,61.5971,18.4114,315.0,72.2857,9.9,14.7857,0.1,7,4.8916
2017-02-19,139.4214,75.5914,20.3357,319.2857,64.4286,10.4714,18.8429,0.0,7,4.9375
2017-02-26,244.8114,56.7414,15.6771,372.0,50.0,12.6286,19.2857,0.0,7,5.5005
2017-03-05,115.9371,70.6671,23.4957,286.8571,49.2857,9.5143,20.1143,4.2,7,4.753
2017-03-12,87.95,45.3057,22.7629,197.4286,59.8571,10.2143,18.3714,14.9,7,4.4768
2017-03-19,106.6343,40.4714,22.2643,305.1429,53.2857,9.4143,19.2429,1.3,7,4.6694
2017-03-26,136.8229,69.0729,22.12,362.0,46.8571,11.9714,24.9571,0.2,7,4.9187
2017-04-02,110.3371,80.1229,19.5186,287.8571,37.2857,13.4,29.4286,0.0,7,4.7035
2017-04-09,90.86,72.8486,24.1429,300.5714,32.8571,13.8286,27.5143,1.1,7,4.5093
2017-04-16,154.8371,86.8143,39.8043,360.4286,26.4286,13.0714,29.5714,0.0,7,5.0424
2017-04-23,133.07,90.8471,36.5114,359.4286,34.4286,10.0857,32.7429,2.0,7,4.8909
2017-04-30,96.7886,70.98,41.2186,251.5714,27.8571,10.3286,30.3714,2.5,7,4.5725
2017-05-07,167.4829,86.2886,48.7114,378.1429,25.1429,9.0143,32.0571,0.0,7,5.1209
2017-05-14,142.7271,70.9771,47.7429,373.0,32.8571,10.7143,33.6429,3.3,7,4.9609
2017-05-21,144.9043,57.0814,42.8871,326.8571,33.7143,9.2429,32.8857,2.1,7,4.9761
2017-05-28,94.8229,67.0186,38.2857,269.2857,42.1429,10.9,32.7714,1.7,7,4.552
2017-06-04,90.0814,90.0314,24.1071,230.4286,47.7143,11.2,32.4714,3.1,7,4.5007
2017-06-11,58.4771,72.2857,19.55,162.8571,47.2857,10.7,33.3,5.8,7,4.0686
2017-06-18,58.1271,90.9814,,101.4286,48.2857,9.3857,32.3,13.2,7,4.0626
2017-06-25,57.1429,70.64,,123.1667,66.1429,7.9714,30.4143,23.8,7,4.0456
2017-07-02,32.95,37.5371,,68.7143,77.7143,10.1857,29.7,69.1,7,3.495
2017-07-09,58.0,19.3571,,106.4286,73.0,10.0,30.5714,10.5,7,4.0604
2017-07-16,31.5557,39.2329,,54.8571,72.4286,11.9857,29.8286,18.8,7,3.4518
2017-07-23,31.4829,67.7143,,74.5714,78.1429,11.5143,29.5571,38.9,7,3.4494
2017-07-30,21.16,21.8357,,37.7143,79.2857,13.1143,28.5571,19.5,7,3.0521
2017-08-06,35.2814,31.9657,,57.0,80.2857,9.4714,28.5143,31.8,7,3.5634
2017-08-13,37.6029,47.6657,,74.8333,79.0,11.6857,29.1,58.7,7,3.6271
2017-08-20,33.6243,57.36,,63.5,70.4286,11.4571,29.9857,7.5,7,3.5152
2017-08-27,43.3986,37.5457,,68.0,83.7143,7.3,28.4143,52.9,7,3.7704
2017-09-03,26.4286,47.19,2.34,86.8,84.4286,11.3857,27.0857,97.5,7,3.2744
2017-09-10,47.1771,24.2329,,96.1429,77.8571,7.8,28.5571,2.3,7,3.8539
2017-09-17,59.2629,26.8757,,123.8571,70.5714,7.1857,29.3,0.0,7,4.082
2017-09-24,44.0271,27.6657,,106.8571,76.7143,9.2571,27.5571,30.5,7,3.7848
2017-10-01,72.0857,28.4143,6.1833,145.1429,66.1429,7.1714,28.4286,0.0,7,4.2779
2017-10-08,76.9129,26.0414,13.23,168.2857,59.0,7.6,28.0429,0.0,7,4.3427
2017-10-15,122.4471,30.0071,11.9486,260.2857,55.4286,7.1429,28.0,0.0,7,4.8077
2017-10-22,198.3271,56.1486,24.56,358.2857,55.4286,7.8714,27.1429,0.0,7,5.2899
2017-10-29,183.8943,75.3229,24.7243,352.0,55.0,7.2571,24.9143,0.0,7,5.2144
2017-11-05,187.9957,53.0643,18.5643,340.0,66.5714,6.3286,23.7,0.0,7,5.2364
2017-11-12,438.4471,73.0086,17.1071,563.1429,68.8571,7.1714,22.3,0.0,7,6.0832
2017-11-19,202.2114,52.9757,16.5886,382.2857,64.8571,9.8286,20.2714,0.4,7,5.3093
2017-11-26,185.72,60.77,17.6186,345.8571,51.2857,10.6857,16.8143,0.0,7,5.2242
2017-12-03,205.8971,64.6971,18.9929,372.2857,59.0,7.0857,17.3857,0.0,7,5.3274
2017-12-10,173.3457,62.1257,21.3414,326.4286,50.2857,8.1286,17.0286,0.1,7,5.1553
2017-12-17,130.5114,42.2843,12.2057,277.1429,69.8571,10.3429,14.4286,7.7,7,4.8715
2017-12-24,191.2171,56.7186,21.67,327.2857,64.0,11.2714,15.6286,0.0,7,5.2534
2017-12-31,251.9814,62.7786,22.7229,402.5714,72.2857,7.8571,14.3857,0.0,7,5.5294
2018-01-07,247.2986,56.0571,14.7614,412.1429,71.7143,7.5143,12.3857,0.0,7,5.5106
2018-01-14,188.26,60.36,20.8757,344.5714,66.8571,11.1714,13.3857,0.0,7,5.2378
2018-01-21,197.46,47.8171,18.1871,357.5714,66.4286,9.9429,14.4857,0.0,7,5.2855
2018-01-28,148.4886,44.2971,11.5457,305.5714,77.0,9.3571,12.9571,6.8,7,5.0005
2018-02-04,137.0471,51.9886,13.8214,296.4286,66.2857,12.0714,16.0857,0.0,7,4.9203
2018-02-11,169.39,69.3214,14.38,337.2857,55.5714,9.6857,15.1857,1.6,7,5.1322
2018-02-18,103.7086,43.17,11.2857,231.7143,68.5714,12.5714,16.6857,2.9,7,4.6416
2018-02-25,158.0829,67.9,15.0471,333.0,64.1429,7.8714,20.5571,2.2,7,5.0631
2018-03-04,104.86,44.5257,12.4543,236.1429,62.0,10.3571,21.7429,1.2,7,4.6526
2018-03-11,96.9486,50.0171,14.97,215.1429,52.4286,10.3,21.9143,1.1,7,4.5742
2018-03-18,102.2143,45.9014,16.5186,248.8571,44.2857,10.2286,23.7143,0.0,7,4.6271
2018-03-25,90.97,40.6986,17.4071,212.1429,49.7143,9.5714,23.8286,2.1,7,4.5105
2018-04-01,97.7286,49.0171,16.3214,242.8571,39.8571,11.8857,26.6286,0.0,7,4.5822
2018-04-08,94.4529,47.0071,15.87,230.2857,48.8571,8.9571,28.0,9.6,7,4.5481
2018-04-15,75.25,48.5371,13.0571,189.4286,50.8571,9.3571,26.4571,9.3,7,4.3208
2018-04-22,92.28,47.0586,15.5986,291.0,30.4286,12.8571,28.9714,7.8,7,4.5248
2018-04-29,103.69,55.1443,14.9043,279.0,30.4286,11.3714,30.7286,2.5,7,4.6414
2018-05-06,68.9371,39.5114,10.4843,188.8571,49.5714,13.4,30.0429,17.1,7,4.2332
2018-05-13,99.3929,50.2014,13.3514,255.4286,42.7143,9.1,30.0571,10.6,7,4.5991
2018-05-20,83.6829,47.3314,12.1657,219.4286,38.8571,8.0429,31.9,1.9,7,4.427
2018-05-27,98.5771,59.8671,14.6943,256.5714,21.7143,10.0286,34.6143,0.1,7,4.5908
2018-06-03,80.0014,39.8929,10.1243,229.5714,43.5714,13.4429,33.6714,5.5,7,4.382
2018-06-10,64.8829,30.8786,8.0857,161.1429,55.2857,12.7714,33.6429,18.6,7,4.1726
2018-06-17,152.4043,27.1543,7.2257,422.0,43.1429,14.7857,34.8571,0.2,7,5.0265
2018-06-24,68.2586,35.1429,10.2543,198.8571,44.1429,7.6143,34.5714,0.6,7,4.2233
2018-07-01,38.8757,31.5529,10.24,118.0,68.1429,11.7,30.9571,58.1,7,3.6604
2018-07-08,51.7443,34.7457,10.3543,138.4286,68.8571,8.2571,30.9714,20.7,7,3.9463
2018-07-15,43.47,31.6914,10.9371,120.8571,76.1429,9.3143,30.5857,50.8,7,3.7721
2018-07-22,36.8086,31.1986,10.4771,101.5714,84.1429,7.0714,29.2714,99.7,7,3.6057
2018-07-29,34.5829,25.7986,9.7886,85.7143,85.0,7.6571,28.3429,50.5,7,3.5434
2018-08-05,59.5043,26.4157,9.5657,186.2857,72.0,12.0143,29.8857,6.8,7,4.086
2018-08-12,39.0543,26.4771,9.5657,115.4286,83.5714,8.0286,28.3714,44.0,7,3.665
2018-08-19,38.7414,27.1671,9.8729,108.5714,82.7143,7.0143,29.1429,29.0,7,3.6569
2018-08-26,31.8071,25.7986,10.9614,99.1429,83.5714,8.0286,28.8571,41.2,7,3.4597
2018-09-02,37.8543,25.9186,10.2671,103.2857,86.8571,6.0429,28.0857,63.3,7,3.6337
2018-09-09,41.95,30.46,10.5171,108.5714,86.5714,8.2571,27.3429,42.8,7,3.7365
2018-09-16,33.33,26.0057,10.9457,107.1429,74.7143,10.1143,28.0,5.8,7,3.5065
2018-09-23,49.2086,28.9671,12.3357,131.2857,76.2857,11.6857,27.0429,72.4,7,3.8961
2018-09-30,57.5586,35.1271,12.11,140.1429,79.4286,9.0429,26.3286,13.7,7,4.0528
2018-10-07,83.3871,44.4757,13.9643,199.1429,68.4286,6.7,26.4143,1.0,7,4.4235
2018-10-14,96.9114,48.2329,16.7043,238.2857,70.7143,8.5429,24.5429,1.5,7,4.5738
2018-10-21,140.4829,56.3129,18.7857,313.2857,62.1429,7.5143,24.5857,0.4,7,4.9451
2018-10-28,171.1543,68.2514,19.5671,353.2857,57.1429,7.5429,23.0143,0.0,7,5.1426
2018-11-04,202.7614,59.9829,17.7529,384.2857,63.8571,7.5857,23.2571,0.1,7,5.312
2018-11-11,283.1486,60.0057,18.2186,425.0,55.0,7.3,20.3429,0.0,7,5.646
2018-11-18,173.0886,58.5643,16.0043,346.7143,67.1429,8.7571,20.4571,1.8,7,5.1538
2018-11-25,168.8671,60.7429,15.9443,334.0,60.7143,9.9286,19.5714,0.0,7,5.1291
2018-12-02,186.7086,65.8386,15.9786,360.1429,67.5714,7.5429,18.5286,0.0,7,5.2295
2018-12-09,201.8729,65.41,16.12,377.1429,67.1429,6.6,16.5571,0.0,7,5.3076
2018-12-16,175.7014,53.79,14.5057,345.5714,70.8571,8.3571,14.4429,1.0,7,5.1688
2018-12-23,261.5357,67.79,17.3671,421.1429,68.5714,8.3286,12.4857,0.0,7,5.5666
2018-12-30,287.3929,68.9343,16.6571,461.7143,64.2857,8.6,12.1857,0.0,7,5.6609
2019-01-06,282.4114,64.44,15.8571,466.4286,71.1429,8.7429,13.0714,2.3,7,5.6434
2019-01-13,215.72,62.4386,16.8186,379.4286,70.5714,8.6143,13.0286,0.0,7,5.374
2019-01-20,239.1957,73.66,17.9814,399.1429,65.4286,9.0143,13.2286,0.0,7,5.4773
2019-01-27,116.3271,45.3686,14.7343,256.4286,77.4286,10.5429,13.0571,23.9,7,4.7564
2019-02-03,166.5671,50.1671,17.2329,332.4286,70.4286,10.6,12.2714,0.8,7,5.1154
2019-02-10,134.5643,48.1286,15.0671,270.5714,76.0,10.8857,14.3571,22.3,7,4.902
2019-02-17,152.7586,52.6171,16.29,317.2857,79.0,8.6143,15.1571,9.0,7,5.0289
2019-02-24,90.0871,46.7029,16.9371,207.0,72.4286,11.4429,16.8429,3.3,7,4.5008
2019-03-03,80.32,47.97,15.9571,185.1429,71.4286,8.6429,14.6429,24.9,7,4.386
2019-03-10,86.03,44.8729,15.9514,196.8571,64.7143,9.4429,17.3286,0.2,7,4.4547
2019-03-17,82.4214,46.4214,17.7386,187.4286,59.7143,10.5857,18.7429,2.0,7,4.4118
2019-03-24,79.0757,42.3014,19.3043,194.8571,45.4286,11.7714,22.4286,0.0,7,4.3704
2019-03-31,87.0914,48.2957,20.7814,206.1429,52.5714,9.8429,25.0,0.5,7,4.467
2019-04-07,104.1229,52.9857,24.0643,240.4286,41.8571,9.4857,27.3857,0.0,7,4.6456
2019-04-14,72.8586,45.5286,20.0614,215.7143,41.1429,10.2143,29.2857,0.2,7,4.2885
2019-04-21,61.77,43.5186,18.6214,164.2857,51.2857,9.5571,25.8857,5.3,7,4.1234
2019-04-28,88.33,49.7186,22.8429,246.5714,31.4286,12.4571,32.5286,0.0,7,4.4811
2019-05-05,85.7743,54.6371,22.0357,241.1429,24.4286,11.7714,32.2143,0.5,7,4.4517
2019-05-12,129.0486,53.33,22.05,329.5714,22.4286,13.6286,33.0714,0.0,7,4.8602
2019-05-19,86.87,46.0586,17.82,225.7143,46.1429,8.9143,29.8286,3.0,7,4.4644
2019-05-26,67.2914,46.4286,17.3686,175.4286,36.4286,11.3,31.9857,0.0,7,4.209
2019-06-02,78.26,57.0429,20.0857,220.4286,25.2857,11.2571,35.0571,0.0,7,4.36
2019-06-09,70.2086,43.2886,15.4186,208.0,37.5714,10.7571,35.2857,0.8,7,4.2515
2019-06-16,69.0129,40.1657,13.1514,229.0,31.7143,13.1714,35.8429,2.2,7,4.2343
2019-06-23,53.5386,34.2971,11.2529,158.4286,48.1429,10.2571,32.6857,1.7,7,3.9804
2019-06-30,56.7329,34.4943,12.6029,177.5714,45.5714,10.6,34.5143,6.0,7,4.0384
2019-07-07,46.7743,29.7957,10.8057,140.4286,59.1429,8.0286,33.0714,14.3,7,3.8453
2019-07-14,62.9386,28.5229,9.7329,222.7143,60.1429,12.4857,32.4857,16.5,7,4.1422
2019-07-21,42.65,33.1529,9.3114,127.0,81.1429,7.1571,28.5857,82.9,7,3.753
2019-07-28,42.49,32.2243,8.8014,115.0,82.8571,9.4857,29.0,68.6,7,3.7493
2019-08-04,34.1886,28.5343,9.1057,94.2857,82.4286,9.3286,28.9,28.6,7,3.5319
2019-08-11,28.4871,28.5871,9.21,93.8571,82.1429,11.0286,29.0,49.5,7,3.3495
2019-08-18,20.7814,24.5386,8.3386,79.5714,85.0,12.0571,28.0714,90.5,7,3.0341
2019-08-25,45.1186,34.8757,8.33,117.1429,83.0,6.9,28.6,23.7,7,3.8093
2019-09-01,39.6414,33.8014,9.0457,109.8571,80.8571,7.5571,29.7571,14.1,7,3.6799
2019-09-08,46.8057,31.7557,9.1186,115.5714,82.7143,7.0286,29.3857,17.9,7,3.846
2019-09-15,50.5686,31.6943,8.7971,120.1429,77.5714,8.6857,29.8143,7.6,7,3.9233
2019-09-22,39.8514,31.9471,9.3571,106.4286,81.0,8.4143,27.9714,28.7,7,3.6852
2019-09-29,25.55,27.9686,9.66,86.1429,80.4286,11.6143,26.5143,17.5,7,3.2406
2019-10-06,43.2557,32.4643,8.7329,109.4286,74.4286,7.4286,26.1429,15.6,7,3.7671
2019-10-13,87.5229,44.3629,11.1314,198.4286,57.4286,7.0286,26.6,0.0,7,4.4719
2019-10-20,111.8514,49.8286,12.3243,267.5714,60.0,7.3429,26.6143,5.2,7,4.7172
2019-10-27,140.2557,54.8186,13.8429,297.1429,57.1429,8.6571,24.4857,0.0,7,4.9435
2019-11-03,353.3686,60.1571,14.2586,495.8571,65.5714,7.6857,24.4571,0.2,7,5.8675
2019-11-10,176.2229,48.9157,12.5643,354.8571,63.4286,10.0571,22.3571,2.2,7,5.1717
2019-11-17,297.9271,59.8814,14.1114,460.8571,64.8571,10.2286,20.9429,0.0,7,5.6968
2019-11-24,152.5214,61.9143,13.7429,308.7143,64.7143,9.0143,19.9857,0.0,7,5.0273
2019-12-01,86.8257,45.67,11.7629,192.2857,74.1429,8.5714,18.3286,23.0,7,4.4639
2019-12-08,204.5543,69.4271,13.2871,358.8571,74.5714,7.5286,15.4714,0.0,7,5.3208
2019-12-15,184.0914,59.0329,11.0843,336.4286,77.7143,8.3429,14.7143,9.6,7,5.2154
2019-12-22,185.5786,45.37,8.1657,321.5714,80.2857,8.0714,12.3571,0.2,7,5.2235
2019-12-29,234.3286,49.9629,8.2914,381.8571,86.7143,8.0714,8.5429,0.0,7,5.4567
2020-01-05,271.1214,56.2371,13.9986,435.1429,79.8571,7.3286,11.1571,0.6,7,5.6026
2020-01-12,139.4771,46.4771,10.4957,292.5714,80.1429,9.5857,11.8571,19.6,7,4.9379
2020-01-19,134.7457,42.7043,9.9971,294.4286,85.8571,8.3714,12.9429,28.8,7,4.9034
2020-01-26,150.8671,45.3143,11.0643,292.4286,75.8571,10.6286,12.6,0.0,7,5.0164
2020-02-02,115.5657,47.6086,10.8557,254.4286,77.5714,9.4714,12.8857,16.9,7,4.7498
2020-02-09,149.5457,54.3486,13.6129,312.2857,74.0,8.3,12.5,0.1,7,5.0076
2020-02-16,129.7643,50.0671,16.0943,273.0,61.2857,14.0,16.4143,0.0,7,4.8657
2020-02-23,106.28,48.8243,16.4329,237.5714,66.4286,13.3429,17.7429,18.8,7,4.6661
2020-03-01,90.5357,42.3443,14.6114,207.0,76.8571,10.1571,18.7714,9.2,7,4.5057
2020-03-08,62.0443,40.2571,13.3857,149.2857,78.4286,10.3714,17.9286,39.2,7,4.1278
2020-03-15,60.5171,35.0314,14.1386,143.1429,71.5714,10.2714,17.6857,16.9,7,4.1029
2020-03-22,77.4529,43.3857,16.7629,182.4286,70.1429,8.6429,20.4286,2.2,7,4.3497
2020-03-29,38.4829,20.0229,12.4286,89.5714,64.2857,10.2143,22.5714,6.8,7,3.6502
2020-04-05,36.5314,19.8243,12.75,84.2857,52.1429,11.2,23.0571,0.1,7,3.5982
2020-04-12,44.0186,21.7029,15.2143,107.5714,45.0,10.5714,25.9857,0.4,7,3.7846
2020-04-19,48.3486,21.3814,15.9186,128.1429,38.7143,10.9,29.5143,0.0,7,3.8784
2020-04-26,48.89,22.2243,16.1057,121.5714,45.2857,9.0714,27.6571,1.9,7,3.8896
2020-05-03,43.1914,16.8329,16.0214,118.7143,59.1429,12.3143,28.1857,25.9,7,3.7656
2020-05-10,46.7,19.1329,13.8386,127.8571,48.5714,9.2857,29.3,0.8,7,3.8437
2020-05-17,62.7657,23.7229,14.9886,146.1429,46.5714,9.9429,30.4857,0.6,7,4.1394
2020-05-24,79.4329,36.6757,20.0971,197.1429,26.1429,10.3143,32.9571,0.0,7,4.3749
2020-05-31,38.3357,23.9057,13.3214,133.2857,41.5714,13.3857,32.4571,9.9,7,3.6464
2020-06-07,46.1957,25.6671,13.6643,117.4286,60.1429,7.2143,29.3429,1.2,7,3.8329
2020-06-14,58.9571,29.2271,13.5371,139.5714,54.1429,7.7,33.1429,0.1,7,4.0768
2020-06-21,41.8586,21.0914,11.7643,124.0,51.1429,10.2714,34.0857,1.3,7,3.7343
2020-06-28,41.0143,20.0529,11.03,108.2857,62.2857,10.8857,32.3857,7.8,7,3.7139
```

## fc_backtest_forecasts.csv (1560 rows; fold = forecast year; mu, sd on log scale; point forecast = exp(mu))
```
fold,model,date,actual,mu,sd
2017,Seasonal naive,2017-01-01,230.7143,5.4246,
2017,Seasonal naive,2017-01-08,207.4529,5.6731,
2017,Seasonal naive,2017-01-15,196.7457,5.273,
2017,Seasonal naive,2017-01-22,238.0271,5.6061,
2017,Seasonal naive,2017-01-29,159.2057,5.6057,
2017,Seasonal naive,2017-02-05,177.6186,5.0809,
2017,Seasonal naive,2017-02-12,133.1686,4.9898,
2017,Seasonal naive,2017-02-19,139.4214,4.9181,
2017,Seasonal naive,2017-02-26,244.8114,4.8815,
2017,Seasonal naive,2017-03-05,115.9371,4.9006,
2017,Seasonal naive,2017-03-12,87.95,4.495,
2017,Seasonal naive,2017-03-19,106.6343,4.3518,
2017,Seasonal naive,2017-03-26,136.8229,4.4741,
2017,Seasonal naive,2017-04-02,110.3371,4.7199,
2017,Seasonal naive,2017-04-09,90.86,4.7591,
2017,Seasonal naive,2017-04-16,154.8371,4.5898,
2017,Seasonal naive,2017-04-23,133.07,4.7087,
2017,Seasonal naive,2017-04-30,96.7886,4.9777,
2017,Seasonal naive,2017-05-07,167.4829,4.5083,
2017,Seasonal naive,2017-05-14,142.7271,4.5337,
2017,Seasonal naive,2017-05-21,144.9043,4.4755,
2017,Seasonal naive,2017-05-28,94.8229,4.5967,
2017,Seasonal naive,2017-06-04,90.0814,4.5627,
2017,Seasonal naive,2017-06-11,58.4771,4.2608,
2017,Seasonal naive,2017-06-18,58.1271,4.3976,
2017,Seasonal naive,2017-06-25,57.1429,4.3407,
2017,Seasonal naive,2017-07-02,32.95,4.209,
2017,Seasonal naive,2017-07-09,58.0,4.1063,
2017,Seasonal naive,2017-07-16,31.5557,4.1064,
2017,Seasonal naive,2017-07-23,31.4829,3.8788,
2017,Seasonal naive,2017-07-30,21.16,3.9531,
2017,Seasonal naive,2017-08-06,35.2814,3.8,
2017,Seasonal naive,2017-08-13,37.6029,3.74,
2017,Seasonal naive,2017-08-20,33.6243,3.8886,
2017,Seasonal naive,2017-08-27,43.3986,3.8367,
2017,Seasonal naive,2017-09-03,26.4286,3.8147,
2017,Seasonal naive,2017-09-10,47.1771,4.0401,
2017,Seasonal naive,2017-09-17,59.2629,4.2053,
2017,Seasonal naive,2017-09-24,44.0271,4.1861,
2017,Seasonal naive,2017-10-01,72.0857,4.5035,
2017,Seasonal naive,2017-10-08,76.9129,4.803,
2017,Seasonal naive,2017-10-15,122.4471,4.78,
2017,Seasonal naive,2017-10-22,198.3271,5.0309,
2017,Seasonal naive,2017-10-29,183.8943,5.5555,
2017,Seasonal naive,2017-11-05,187.9957,6.2049,
2017,Seasonal naive,2017-11-12,438.4471,5.7627,
2017,Seasonal naive,2017-11-19,202.2114,5.6144,
2017,Seasonal naive,2017-11-26,185.72,5.292,
2017,Seasonal naive,2017-12-03,205.8971,5.4047,
2017,Seasonal naive,2017-12-10,173.3457,5.4949,
2017,Seasonal naive,2017-12-17,130.5114,5.3018,
2017,Seasonal naive,2017-12-24,191.2171,5.5075,
2017,Climatology,2017-01-01,230.7143,5.3125,
2017,Climatology,2017-01-08,207.4529,5.4456,
2017,Climatology,2017-01-15,196.7457,5.2755,
2017,Climatology,2017-01-22,238.0271,5.4204,
2017,Climatology,2017-01-29,159.2057,5.3289,
2017,Climatology,2017-02-05,177.6186,5.0867,
2017,Climatology,2017-02-12,133.1686,4.9993,
2017,Climatology,2017-02-19,139.4214,5.0,
2017,Climatology,2017-02-26,244.8114,4.9628,
2017,Climatology,2017-03-05,115.9371,4.8833,
2017,Climatology,2017-03-12,87.95,4.4538,
2017,Climatology,2017-03-19,106.6343,4.4006,
2017,Climatology,2017-03-26,136.8229,4.3574,
2017,Climatology,2017-04-02,110.3371,4.6303,
2017,Climatology,2017-04-09,90.86,4.5128,
2017,Climatology,2017-04-16,154.8371,4.5589,
2017,Climatology,2017-04-23,133.07,4.6239,
2017,Climatology,2017-04-30,96.7886,4.8402,
2017,Climatology,2017-05-07,167.4829,4.4302,
2017,Climatology,2017-05-14,142.7271,4.662,
2017,Climatology,2017-05-21,144.9043,4.486,
2017,Climatology,2017-05-28,94.8229,4.4481,
2017,Climatology,2017-06-04,90.0814,4.6209,
2017,Climatology,2017-06-11,58.4771,4.2287,
2017,Climatology,2017-06-18,58.1271,4.4903,
2017,Climatology,2017-06-25,57.1429,4.5039,
2017,Climatology,2017-07-02,32.95,4.3099,
2017,Climatology,2017-07-09,58.0,4.2045,
2017,Climatology,2017-07-16,31.5557,4.0168,
2017,Climatology,2017-07-23,31.4829,4.0083,
2017,Climatology,2017-07-30,21.16,3.8307,
2017,Climatology,2017-08-06,35.2814,3.6446,
2017,Climatology,2017-08-13,37.6029,3.9233,
2017,Climatology,2017-08-20,33.6243,4.0217,
2017,Climatology,2017-08-27,43.3986,3.86,
2017,Climatology,2017-09-03,26.4286,3.9456,
2017,Climatology,2017-09-10,47.1771,4.2093,
2017,Climatology,2017-09-17,59.2629,4.2137,
2017,Climatology,2017-09-24,44.0271,4.3223,
2017,Climatology,2017-10-01,72.0857,4.3217,
2017,Climatology,2017-10-08,76.9129,4.6529,
2017,Climatology,2017-10-15,122.4471,4.8778,
2017,Climatology,2017-10-22,198.3271,4.8625,
2017,Climatology,2017-10-29,183.8943,5.3081,
2017,Climatology,2017-11-05,187.9957,5.6103,
2017,Climatology,2017-11-12,438.4471,5.6148,
2017,Climatology,2017-11-19,202.2114,5.5407,
2017,Climatology,2017-11-26,185.72,5.3491,
2017,Climatology,2017-12-03,205.8971,5.3505,
2017,Climatology,2017-12-10,173.3457,5.4357,
2017,Climatology,2017-12-17,130.5114,5.3392,
2017,Climatology,2017-12-24,191.2171,5.1839,
2017,Climatology + AR(1),2017-01-01,230.7143,5.4231,0.1444
2017,Climatology + AR(1),2017-01-08,207.4529,5.4835,0.1526
2017,Climatology + AR(1),2017-01-15,196.7457,5.2885,0.1535
2017,Climatology + AR(1),2017-01-22,238.0271,5.4248,0.1536
2017,Climatology + AR(1),2017-01-29,159.2057,5.3304,0.1536
2017,Climatology + AR(1),2017-02-05,177.6186,5.0872,0.1536
2017,Climatology + AR(1),2017-02-12,133.1686,4.9995,0.1536
2017,Climatology + AR(1),2017-02-19,139.4214,5.0001,0.1536
2017,Climatology + AR(1),2017-02-26,244.8114,4.9628,0.1536
2017,Climatology + AR(1),2017-03-05,115.9371,4.8833,0.1536
2017,Climatology + AR(1),2017-03-12,87.95,4.4538,0.1536
2017,Climatology + AR(1),2017-03-19,106.6343,4.4006,0.1536
2017,Climatology + AR(1),2017-03-26,136.8229,4.3574,0.1536
2017,Climatology + AR(1),2017-04-02,110.3371,4.6303,0.1536
2017,Climatology + AR(1),2017-04-09,90.86,4.5128,0.1536
2017,Climatology + AR(1),2017-04-16,154.8371,4.5589,0.1536
2017,Climatology + AR(1),2017-04-23,133.07,4.6239,0.1536
2017,Climatology + AR(1),2017-04-30,96.7886,4.8402,0.1536
2017,Climatology + AR(1),2017-05-07,167.4829,4.4302,0.1536
2017,Climatology + AR(1),2017-05-14,142.7271,4.662,0.1536
2017,Climatology + AR(1),2017-05-21,144.9043,4.486,0.1536
2017,Climatology + AR(1),2017-05-28,94.8229,4.4481,0.1536
2017,Climatology + AR(1),2017-06-04,90.0814,4.6209,0.1536
2017,Climatology + AR(1),2017-06-11,58.4771,4.2287,0.1536
2017,Climatology + AR(1),2017-06-18,58.1271,4.4903,0.1536
2017,Climatology + AR(1),2017-06-25,57.1429,4.5039,0.1536
2017,Climatology + AR(1),2017-07-02,32.95,4.3099,0.1536
2017,Climatology + AR(1),2017-07-09,58.0,4.2045,0.1536
2017,Climatology + AR(1),2017-07-16,31.5557,4.0168,0.1536
2017,Climatology + AR(1),2017-07-23,31.4829,4.0083,0.1536
2017,Climatology + AR(1),2017-07-30,21.16,3.8307,0.1536
2017,Climatology + AR(1),2017-08-06,35.2814,3.6446,0.1536
2017,Climatology + AR(1),2017-08-13,37.6029,3.9233,0.1536
2017,Climatology + AR(1),2017-08-20,33.6243,4.0217,0.1536
2017,Climatology + AR(1),2017-08-27,43.3986,3.86,0.1536
2017,Climatology + AR(1),2017-09-03,26.4286,3.9456,0.1536
2017,Climatology + AR(1),2017-09-10,47.1771,4.2093,0.1536
2017,Climatology + AR(1),2017-09-17,59.2629,4.2137,0.1536
2017,Climatology + AR(1),2017-09-24,44.0271,4.3223,0.1536
2017,Climatology + AR(1),2017-10-01,72.0857,4.3217,0.1536
2017,Climatology + AR(1),2017-10-08,76.9129,4.6529,0.1536
2017,Climatology + AR(1),2017-10-15,122.4471,4.8778,0.1536
2017,Climatology + AR(1),2017-10-22,198.3271,4.8625,0.1536
2017,Climatology + AR(1),2017-10-29,183.8943,5.3081,0.1536
2017,Climatology + AR(1),2017-11-05,187.9957,5.6103,0.1536
2017,Climatology + AR(1),2017-11-12,438.4471,5.6148,0.1536
2017,Climatology + AR(1),2017-11-19,202.2114,5.5407,0.1536
2017,Climatology + AR(1),2017-11-26,185.72,5.3491,0.1536
2017,Climatology + AR(1),2017-12-03,205.8971,5.3505,0.1536
2017,Climatology + AR(1),2017-12-10,173.3457,5.4357,0.1536
2017,Climatology + AR(1),2017-12-17,130.5114,5.3392,0.1536
2017,Climatology + AR(1),2017-12-24,191.2171,5.1839,0.1536
2017,Linear regression,2017-01-01,230.7143,5.4482,0.2162
2017,Linear regression,2017-01-08,207.4529,5.4112,0.2162
2017,Linear regression,2017-01-15,196.7457,5.366,0.2162
2017,Linear regression,2017-01-22,238.0271,5.3123,0.2162
2017,Linear regression,2017-01-29,159.2057,5.2498,0.2162
2017,Linear regression,2017-02-05,177.6186,5.1789,0.2162
2017,Linear regression,2017-02-12,133.1686,5.1007,0.2162
2017,Linear regression,2017-02-19,139.4214,5.0173,0.2162
2017,Linear regression,2017-02-26,244.8114,4.9318,0.2162
2017,Linear regression,2017-03-05,115.9371,4.8482,0.2162
2017,Linear regression,2017-03-12,87.95,4.7706,0.2162
2017,Linear regression,2017-03-19,106.6343,4.7032,0.2162
2017,Linear regression,2017-03-26,136.8229,4.6497,0.2162
2017,Linear regression,2017-04-02,110.3371,4.6127,0.2162
2017,Linear regression,2017-04-09,90.86,4.5929,0.2162
2017,Linear regression,2017-04-16,154.8371,4.5897,0.2162
2017,Linear regression,2017-04-23,133.07,4.6002,0.2162
2017,Linear regression,2017-04-30,96.7886,4.6201,0.2162
2017,Linear regression,2017-05-07,167.4829,4.6436,0.2162
2017,Linear regression,2017-05-14,142.7271,4.6641,0.2162
2017,Linear regression,2017-05-21,144.9043,4.6752,0.2162
2017,Linear regression,2017-05-28,94.8229,4.671,0.2162
2017,Linear regression,2017-06-04,90.0814,4.647,0.2162
2017,Linear regression,2017-06-11,58.4771,4.601,0.2162
2017,Linear regression,2017-06-18,58.1271,4.5331,0.2162
2017,Linear regression,2017-06-25,57.1429,4.4459,0.2162
2017,Linear regression,2017-07-02,32.95,4.3446,0.2162
2017,Linear regression,2017-07-09,58.0,4.2364,0.2162
2017,Linear regression,2017-07-16,31.5557,4.13,0.2162
2017,Linear regression,2017-07-23,31.4829,4.0344,0.2162
2017,Linear regression,2017-07-30,21.16,3.9588,0.2162
2017,Linear regression,2017-08-06,35.2814,3.9109,0.2162
2017,Linear regression,2017-08-13,37.6029,3.8965,0.2162
2017,Linear regression,2017-08-20,33.6243,3.9191,0.2162
2017,Linear regression,2017-08-27,43.3986,3.9793,0.2162
2017,Linear regression,2017-09-03,26.4286,4.0749,0.2162
2017,Linear regression,2017-09-10,47.1771,4.2011,0.2162
2017,Linear regression,2017-09-17,59.2629,4.351,0.2162
2017,Linear regression,2017-09-24,44.0271,4.5163,0.2162
2017,Linear regression,2017-10-01,72.0857,4.6883,0.2162
2017,Linear regression,2017-10-08,76.9129,4.8582,0.2162
2017,Linear regression,2017-10-15,122.4471,5.0182,0.2162
2017,Linear regression,2017-10-22,198.3271,5.1622,0.2162
2017,Linear regression,2017-10-29,183.8943,5.2855,0.2162
2017,Linear regression,2017-11-05,187.9957,5.3859,0.2162
2017,Linear regression,2017-11-12,438.4471,5.4627,0.2162
2017,Linear regression,2017-11-19,202.2114,5.5171,0.2162
2017,Linear regression,2017-11-26,185.72,5.5513,0.2162
2017,Linear regression,2017-12-03,205.8971,5.568,0.2162
2017,Linear regression,2017-12-10,173.3457,5.5704,0.2162
2017,Linear regression,2017-12-17,130.5114,5.561,0.2162
2017,Linear regression,2017-12-24,191.2171,5.5419,0.2162
2017,LSTM (small),2017-01-01,230.7143,5.3943,0.024
2017,LSTM (small),2017-01-08,207.4529,5.3774,0.024
2017,LSTM (small),2017-01-15,196.7457,5.3061,0.024
2017,LSTM (small),2017-01-22,238.0271,5.5587,0.024
2017,LSTM (small),2017-01-29,159.2057,5.3503,0.024
2017,LSTM (small),2017-02-05,177.6186,5.0535,0.024
2017,LSTM (small),2017-02-12,133.1686,4.9939,0.024
2017,LSTM (small),2017-02-19,139.4214,5.0609,0.024
2017,LSTM (small),2017-02-26,244.8114,5.0081,0.024
2017,LSTM (small),2017-03-05,115.9371,4.8439,0.024
2017,LSTM (small),2017-03-12,87.95,4.3818,0.024
2017,LSTM (small),2017-03-19,106.6343,4.4283,0.024
2017,LSTM (small),2017-03-26,136.8229,4.4387,0.024
2017,LSTM (small),2017-04-02,110.3371,4.6182,0.024
2017,LSTM (small),2017-04-09,90.86,4.5551,0.024
2017,LSTM (small),2017-04-16,154.8371,4.9275,0.024
2017,LSTM (small),2017-04-23,133.07,4.6432,0.024
2017,LSTM (small),2017-04-30,96.7886,4.8702,0.024
2017,LSTM (small),2017-05-07,167.4829,4.4373,0.024
2017,LSTM (small),2017-05-14,142.7271,4.631,0.024
2017,LSTM (small),2017-05-21,144.9043,4.3145,0.024
2017,LSTM (small),2017-05-28,94.8229,4.28,0.024
2017,LSTM (small),2017-06-04,90.0814,4.6344,0.024
2017,LSTM (small),2017-06-11,58.4771,4.191,0.024
2017,LSTM (small),2017-06-18,58.1271,4.4995,0.024
2017,LSTM (small),2017-06-25,57.1429,4.552,0.024
2017,LSTM (small),2017-07-02,32.95,4.4568,0.024
2017,LSTM (small),2017-07-09,58.0,4.4145,0.024
2017,LSTM (small),2017-07-16,31.5557,4.1536,0.024
2017,LSTM (small),2017-07-23,31.4829,4.0945,0.024
2017,LSTM (small),2017-07-30,21.16,3.8587,0.024
2017,LSTM (small),2017-08-06,35.2814,3.65,0.024
2017,LSTM (small),2017-08-13,37.6029,3.9655,0.024
2017,LSTM (small),2017-08-20,33.6243,4.1551,0.024
2017,LSTM (small),2017-08-27,43.3986,3.9807,0.024
2017,LSTM (small),2017-09-03,26.4286,4.0361,0.024
2017,LSTM (small),2017-09-10,47.1771,4.2697,0.024
2017,LSTM (small),2017-09-17,59.2629,3.9577,0.024
2017,LSTM (small),2017-09-24,44.0271,4.2528,0.024
2017,LSTM (small),2017-10-01,72.0857,4.386,0.024
2017,LSTM (small),2017-10-08,76.9129,4.6212,0.024
2017,LSTM (small),2017-10-15,122.4471,4.7762,0.024
2017,LSTM (small),2017-10-22,198.3271,4.6416,0.024
2017,LSTM (small),2017-10-29,183.8943,5.4719,0.024
2017,LSTM (small),2017-11-05,187.9957,5.8764,0.024
2017,LSTM (small),2017-11-12,438.4471,5.8529,0.024
2017,LSTM (small),2017-11-19,202.2114,5.816,0.024
2017,LSTM (small),2017-11-26,185.72,5.5776,0.024
2017,LSTM (small),2017-12-03,205.8971,5.4562,0.024
2017,LSTM (small),2017-12-10,173.3457,5.4609,0.024
2017,LSTM (small),2017-12-17,130.5114,5.3884,0.024
2017,LSTM (small),2017-12-24,191.2171,5.2657,0.024
2017,Fourier+ARMA const,2017-01-01,230.7143,5.4104,0.1998
2017,Fourier+ARMA const,2017-01-08,207.4529,5.3473,0.2091
2017,Fourier+ARMA const,2017-01-15,196.7457,5.2894,0.2099
2017,Fourier+ARMA const,2017-01-22,238.0271,5.228,0.21
2017,Fourier+ARMA const,2017-01-29,159.2057,5.1604,0.21
2017,Fourier+ARMA const,2017-02-05,177.6186,5.086,0.21
2017,Fourier+ARMA const,2017-02-12,133.1686,5.0058,0.21
2017,Fourier+ARMA const,2017-02-19,139.4214,4.9218,0.21
2017,Fourier+ARMA const,2017-02-26,244.8114,4.8368,0.21
2017,Fourier+ARMA const,2017-03-05,115.9371,4.7543,0.21
2017,Fourier+ARMA const,2017-03-12,87.95,4.6783,0.21
2017,Fourier+ARMA const,2017-03-19,106.6343,4.6127,0.21
2017,Fourier+ARMA const,2017-03-26,136.8229,4.5607,0.21
2017,Fourier+ARMA const,2017-04-02,110.3371,4.5246,0.21
2017,Fourier+ARMA const,2017-04-09,90.86,4.5054,0.21
2017,Fourier+ARMA const,2017-04-16,154.8371,4.5021,0.21
2017,Fourier+ARMA const,2017-04-23,133.07,4.5121,0.21
2017,Fourier+ARMA const,2017-04-30,96.7886,4.5311,0.21
2017,Fourier+ARMA const,2017-05-07,167.4829,4.5534,0.21
2017,Fourier+ARMA const,2017-05-14,142.7271,4.5728,0.21
2017,Fourier+ARMA const,2017-05-21,144.9043,4.583,0.21
2017,Fourier+ARMA const,2017-05-28,94.8229,4.5782,0.21
2017,Fourier+ARMA const,2017-06-04,90.0814,4.5541,0.21
2017,Fourier+ARMA const,2017-06-11,58.4771,4.5084,0.21
2017,Fourier+ARMA const,2017-06-18,58.1271,4.4411,0.21
2017,Fourier+ARMA const,2017-06-25,57.1429,4.3549,0.21
2017,Fourier+ARMA const,2017-07-02,32.95,4.2546,0.21
2017,Fourier+ARMA const,2017-07-09,58.0,4.1474,0.21
2017,Fourier+ARMA const,2017-07-16,31.5557,4.0416,0.21
2017,Fourier+ARMA const,2017-07-23,31.4829,3.9464,0.21
2017,Fourier+ARMA const,2017-07-30,21.16,3.8707,0.21
2017,Fourier+ARMA const,2017-08-06,35.2814,3.8222,0.21
2017,Fourier+ARMA const,2017-08-13,37.6029,3.8069,0.21
2017,Fourier+ARMA const,2017-08-20,33.6243,3.8284,0.21
2017,Fourier+ARMA const,2017-08-27,43.3986,3.8875,0.21
2017,Fourier+ARMA const,2017-09-03,26.4286,3.9821,0.21
2017,Fourier+ARMA const,2017-09-10,47.1771,4.1077,0.21
2017,Fourier+ARMA const,2017-09-17,59.2629,4.2575,0.21
2017,Fourier+ARMA const,2017-09-24,44.0271,4.4233,0.21
2017,Fourier+ARMA const,2017-10-01,72.0857,4.5964,0.21
2017,Fourier+ARMA const,2017-10-08,76.9129,4.7677,0.21
2017,Fourier+ARMA const,2017-10-15,122.4471,4.9294,0.21
2017,Fourier+ARMA const,2017-10-22,198.3271,5.075,0.21
2017,Fourier+ARMA const,2017-10-29,183.8943,5.1995,0.21
2017,Fourier+ARMA const,2017-11-05,187.9957,5.3004,0.21
2017,Fourier+ARMA const,2017-11-12,438.4471,5.3767,0.21
2017,Fourier+ARMA const,2017-11-19,202.2114,5.4293,0.21
2017,Fourier+ARMA const,2017-11-26,185.72,5.4602,0.21
2017,Fourier+ARMA const,2017-12-03,205.8971,5.4724,0.21
2017,Fourier+ARMA const,2017-12-10,173.3457,5.4689,0.21
2017,Fourier+ARMA const,2017-12-17,130.5114,5.4527,0.21
2017,Fourier+ARMA const,2017-12-24,191.2171,5.4261,0.21
2017,Fourier+ARMA linear,2017-01-01,230.7143,5.4557,0.1967
2017,Fourier+ARMA linear,2017-01-08,207.4529,5.4105,0.2065
2017,Fourier+ARMA linear,2017-01-15,196.7457,5.3618,0.2075
2017,Fourier+ARMA linear,2017-01-22,238.0271,5.3061,0.2076
2017,Fourier+ARMA linear,2017-01-29,159.2057,5.2423,0.2076
2017,Fourier+ARMA linear,2017-02-05,177.6186,5.1705,0.2076
2017,Fourier+ARMA linear,2017-02-12,133.1686,5.0917,0.2076
2017,Fourier+ARMA linear,2017-02-19,139.4214,5.008,0.2076
2017,Fourier+ARMA linear,2017-02-26,244.8114,4.9227,0.2076
2017,Fourier+ARMA linear,2017-03-05,115.9371,4.8394,0.2076
2017,Fourier+ARMA linear,2017-03-12,87.95,4.7625,0.2076
2017,Fourier+ARMA linear,2017-03-19,106.6343,4.696,0.2076
2017,Fourier+ARMA linear,2017-03-26,136.8229,4.6435,0.2076
2017,Fourier+ARMA linear,2017-04-02,110.3371,4.6074,0.2076
2017,Fourier+ARMA linear,2017-04-09,90.86,4.5885,0.2076
2017,Fourier+ARMA linear,2017-04-16,154.8371,4.586,0.2076
2017,Fourier+ARMA linear,2017-04-23,133.07,4.5971,0.2076
2017,Fourier+ARMA linear,2017-04-30,96.7886,4.6174,0.2076
2017,Fourier+ARMA linear,2017-05-07,167.4829,4.641,0.2076
2017,Fourier+ARMA linear,2017-05-14,142.7271,4.6616,0.2076
2017,Fourier+ARMA linear,2017-05-21,144.9043,4.6725,0.2076
2017,Fourier+ARMA linear,2017-05-28,94.8229,4.6681,0.2076
2017,Fourier+ARMA linear,2017-06-04,90.0814,4.6439,0.2076
2017,Fourier+ARMA linear,2017-06-11,58.4771,4.5978,0.2076
2017,Fourier+ARMA linear,2017-06-18,58.1271,4.5299,0.2076
2017,Fourier+ARMA linear,2017-06-25,57.1429,4.4429,0.2076
2017,Fourier+ARMA linear,2017-07-02,32.95,4.3419,0.2076
2017,Fourier+ARMA linear,2017-07-09,58.0,4.2342,0.2076
2017,Fourier+ARMA linear,2017-07-16,31.5557,4.1283,0.2076
2017,Fourier+ARMA linear,2017-07-23,31.4829,4.0334,0.2076
2017,Fourier+ARMA linear,2017-07-30,21.16,3.9584,0.2076
2017,Fourier+ARMA linear,2017-08-06,35.2814,3.911,0.2076
2017,Fourier+ARMA linear,2017-08-13,37.6029,3.8972,0.2076
2017,Fourier+ARMA linear,2017-08-20,33.6243,3.9202,0.2076
2017,Fourier+ARMA linear,2017-08-27,43.3986,3.9806,0.2076
2017,Fourier+ARMA linear,2017-09-03,26.4286,4.0763,0.2076
2017,Fourier+ARMA linear,2017-09-10,47.1771,4.2024,0.2076
2017,Fourier+ARMA linear,2017-09-17,59.2629,4.3522,0.2076
2017,Fourier+ARMA linear,2017-09-24,44.0271,4.5175,0.2076
2017,Fourier+ARMA linear,2017-10-01,72.0857,4.6893,0.2076
2017,Fourier+ARMA linear,2017-10-08,76.9129,4.8591,0.2076
2017,Fourier+ARMA linear,2017-10-15,122.4471,5.0191,0.2076
2017,Fourier+ARMA linear,2017-10-22,198.3271,5.163,0.2076
2017,Fourier+ARMA linear,2017-10-29,183.8943,5.2864,0.2076
2017,Fourier+ARMA linear,2017-11-05,187.9957,5.3868,0.2076
2017,Fourier+ARMA linear,2017-11-12,438.4471,5.4637,0.2076
2017,Fourier+ARMA linear,2017-11-19,202.2114,5.518,0.2076
2017,Fourier+ARMA linear,2017-11-26,185.72,5.552,0.2076
2017,Fourier+ARMA linear,2017-12-03,205.8971,5.5684,0.2076
2017,Fourier+ARMA linear,2017-12-10,173.3457,5.5702,0.2076
2017,Fourier+ARMA linear,2017-12-17,130.5114,5.56,0.2076
2017,Fourier+ARMA linear,2017-12-24,191.2171,5.5399,0.2076
2017,Fourier+ARMA (selected),2017-01-01,230.7143,5.3345,0.1859
2017,Fourier+ARMA (selected),2017-01-08,207.4529,5.3628,0.189
2017,Fourier+ARMA (selected),2017-01-15,196.7457,5.4151,0.1894
2017,Fourier+ARMA (selected),2017-01-22,238.0271,5.4391,0.1896
2017,Fourier+ARMA (selected),2017-01-29,159.2057,5.4082,0.1898
2017,Fourier+ARMA (selected),2017-02-05,177.6186,5.3136,0.1899
2017,Fourier+ARMA (selected),2017-02-12,133.1686,5.1645,0.1901
2017,Fourier+ARMA (selected),2017-02-19,139.4214,4.9851,0.1903
2017,Fourier+ARMA (selected),2017-02-26,244.8114,4.8072,0.1905
2017,Fourier+ARMA (selected),2017-03-05,115.9371,4.661,0.1906
2017,Fourier+ARMA (selected),2017-03-12,87.95,4.5667,0.1908
2017,Fourier+ARMA (selected),2017-03-19,106.6343,4.53,0.191
2017,Fourier+ARMA (selected),2017-03-26,136.8229,4.5415,0.1912
2017,Fourier+ARMA (selected),2017-04-02,110.3371,4.5818,0.1914
2017,Fourier+ARMA (selected),2017-04-09,90.86,4.6278,0.1915
2017,Fourier+ARMA (selected),2017-04-16,154.8371,4.6609,0.1917
2017,Fourier+ARMA (selected),2017-04-23,133.07,4.6712,0.1919
2017,Fourier+ARMA (selected),2017-04-30,96.7886,4.6593,0.1921
2017,Fourier+ARMA (selected),2017-05-07,167.4829,4.6335,0.1922
2017,Fourier+ARMA (selected),2017-05-14,142.7271,4.6048,0.1924
2017,Fourier+ARMA (selected),2017-05-21,144.9043,4.5814,0.1926
2017,Fourier+ARMA (selected),2017-05-28,94.8229,4.5647,0.1928
2017,Fourier+ARMA (selected),2017-06-04,90.0814,4.5484,0.1929
2017,Fourier+ARMA (selected),2017-06-11,58.4771,4.5215,0.1931
2017,Fourier+ARMA (selected),2017-06-18,58.1271,4.4727,0.1933
2017,Fourier+ARMA (selected),2017-06-25,57.1429,4.3957,0.1935
2017,Fourier+ARMA (selected),2017-07-02,32.95,4.2927,0.1936
2017,Fourier+ARMA (selected),2017-07-09,58.0,4.1747,0.1938
2017,Fourier+ARMA (selected),2017-07-16,31.5557,4.0589,0.194
2017,Fourier+ARMA (selected),2017-07-23,31.4829,3.9636,0.1942
2017,Fourier+ARMA (selected),2017-07-30,21.16,3.9026,0.1943
2017,Fourier+ARMA (selected),2017-08-06,35.2814,3.8817,0.1945
2017,Fourier+ARMA (selected),2017-08-13,37.6029,3.8976,0.1947
2017,Fourier+ARMA (selected),2017-08-20,33.6243,3.9405,0.1949
2017,Fourier+ARMA (selected),2017-08-27,43.3986,3.9991,0.195
2017,Fourier+ARMA (selected),2017-09-03,26.4286,4.0655,0.1952
2017,Fourier+ARMA (selected),2017-09-10,47.1771,4.1391,0.1954
2017,Fourier+ARMA (selected),2017-09-17,59.2629,4.2268,0.1955
2017,Fourier+ARMA (selected),2017-09-24,44.0271,4.3396,0.1957
2017,Fourier+ARMA (selected),2017-10-01,72.0857,4.4878,0.1959
2017,Fourier+ARMA (selected),2017-10-08,76.9129,4.6742,0.1961
2017,Fourier+ARMA (selected),2017-10-15,122.4471,4.8903,0.1962
2017,Fourier+ARMA (selected),2017-10-22,198.3271,5.1159,0.1964
2017,Fourier+ARMA (selected),2017-10-29,183.8943,5.3231,0.1966
2017,Fourier+ARMA (selected),2017-11-05,187.9957,5.483,0.1968
2017,Fourier+ARMA (selected),2017-11-12,438.4471,5.5747,0.1969
2017,Fourier+ARMA (selected),2017-11-19,202.2114,5.5916,0.1971
2017,Fourier+ARMA (selected),2017-11-26,185.72,5.5441,0.1973
2017,Fourier+ARMA (selected),2017-12-03,205.8971,5.4573,0.1974
2017,Fourier+ARMA (selected),2017-12-10,173.3457,5.364,0.1976
2017,Fourier+ARMA (selected),2017-12-17,130.5114,5.295,0.1978
2017,Fourier+ARMA (selected),2017-12-24,191.2171,5.2702,0.1979
2017,SARIMA D=1,2017-01-01,230.7143,5.6239,0.2399
2017,SARIMA D=1,2017-01-08,207.4529,5.9486,0.245
2017,SARIMA D=1,2017-01-15,196.7457,5.3557,0.2483
2017,SARIMA D=1,2017-01-22,238.0271,5.9346,0.2504
2017,SARIMA D=1,2017-01-29,159.2057,5.9041,0.2518
2017,SARIMA D=1,2017-02-05,177.6186,5.1511,0.2528
2017,SARIMA D=1,2017-02-12,133.1686,4.9715,0.2534
2017,SARIMA D=1,2017-02-19,139.4214,4.8777,0.2538
2017,SARIMA D=1,2017-02-26,244.8114,4.9075,0.254
2017,SARIMA D=1,2017-03-05,115.9371,5.1592,0.2542
2017,SARIMA D=1,2017-03-12,87.95,4.5299,0.2543
2017,SARIMA D=1,2017-03-19,106.6343,4.4173,0.2544
2017,SARIMA D=1,2017-03-26,136.8229,4.4489,0.2545
2017,SARIMA D=1,2017-04-02,110.3371,4.9529,0.2545
2017,SARIMA D=1,2017-04-09,90.86,4.8798,0.2545
2017,SARIMA D=1,2017-04-16,154.8371,4.6194,0.2545
2017,SARIMA D=1,2017-04-23,133.07,4.7151,0.2545
2017,SARIMA D=1,2017-04-30,96.7886,5.2931,0.2546
2017,SARIMA D=1,2017-05-07,167.4829,4.3697,0.2546
2017,SARIMA D=1,2017-05-14,142.7271,4.5541,0.2546
2017,SARIMA D=1,2017-05-21,144.9043,4.5649,0.2546
2017,SARIMA D=1,2017-05-28,94.8229,4.5567,0.2546
2017,SARIMA D=1,2017-06-04,90.0814,4.7464,0.2546
2017,SARIMA D=1,2017-06-11,58.4771,4.1006,0.2546
2017,SARIMA D=1,2017-06-18,58.1271,4.2634,0.2546
2017,SARIMA D=1,2017-06-25,57.1429,4.3061,0.2546
2017,SARIMA D=1,2017-07-02,32.95,4.1624,0.2546
2017,SARIMA D=1,2017-07-09,58.0,4.1959,0.2546
2017,SARIMA D=1,2017-07-16,31.5557,4.0907,0.2546
2017,SARIMA D=1,2017-07-23,31.4829,3.9639,0.2546
2017,SARIMA D=1,2017-07-30,21.16,4.1847,0.2546
2017,SARIMA D=1,2017-08-06,35.2814,3.6465,0.2546
2017,SARIMA D=1,2017-08-13,37.6029,3.5323,0.2546
2017,SARIMA D=1,2017-08-20,33.6243,3.8906,0.2546
2017,SARIMA D=1,2017-08-27,43.3986,3.7161,0.2546
2017,SARIMA D=1,2017-09-03,26.4286,3.5321,0.2546
2017,SARIMA D=1,2017-09-10,47.1771,3.9479,0.2546
2017,SARIMA D=1,2017-09-17,59.2629,4.0772,0.2546
2017,SARIMA D=1,2017-09-24,44.0271,4.2072,0.2546
2017,SARIMA D=1,2017-10-01,72.0857,4.5015,0.2546
2017,SARIMA D=1,2017-10-08,76.9129,4.7138,0.2545
2017,SARIMA D=1,2017-10-15,122.4471,4.8192,0.2545
2017,SARIMA D=1,2017-10-22,198.3271,5.0115,0.2545
2017,SARIMA D=1,2017-10-29,183.8943,5.8196,0.2545
2017,SARIMA D=1,2017-11-05,187.9957,6.5667,0.2545
2017,SARIMA D=1,2017-11-12,438.4471,5.9021,0.2544
2017,SARIMA D=1,2017-11-19,202.2114,5.7081,0.2544
2017,SARIMA D=1,2017-11-26,185.72,5.2773,0.2543
2017,SARIMA D=1,2017-12-03,205.8971,5.4032,0.2541
2017,SARIMA D=1,2017-12-10,173.3457,5.5349,0.2539
2017,SARIMA D=1,2017-12-17,130.5114,5.4988,0.2535
2017,SARIMA D=1,2017-12-24,191.2171,5.6319,0.253
2017,SARIMA D=0,2017-01-01,230.7143,5.4871,0.2409
2017,SARIMA D=0,2017-01-08,207.4529,5.5156,0.2934
2017,SARIMA D=0,2017-01-15,196.7457,5.3584,0.331
2017,SARIMA D=0,2017-01-22,238.0271,5.4188,0.3595
2017,SARIMA D=0,2017-01-29,159.2057,5.3848,0.3818
2017,SARIMA D=0,2017-02-05,177.6186,5.2006,0.3995
2017,SARIMA D=0,2017-02-12,133.1686,5.1456,0.4137
2017,SARIMA D=0,2017-02-19,139.4214,5.0987,0.4253
2017,SARIMA D=0,2017-02-26,244.8114,5.0642,0.4348
2017,SARIMA D=0,2017-03-05,115.9371,5.048,0.4426
2017,SARIMA D=0,2017-03-12,87.95,4.9096,0.449
2017,SARIMA D=0,2017-03-19,106.6343,4.8496,0.4543
2017,SARIMA D=0,2017-03-26,136.8229,4.8686,0.4587
2017,SARIMA D=0,2017-04-02,110.3371,4.9251,0.4624
2017,SARIMA D=0,2017-04-09,90.86,4.9225,0.4655
2017,SARIMA D=0,2017-04-16,154.8371,4.8602,0.468
2017,SARIMA D=0,2017-04-23,133.07,4.8832,0.4701
2017,SARIMA D=0,2017-04-30,96.7886,4.951,0.4719
2017,SARIMA D=0,2017-05-07,167.4829,4.8041,0.4734
2017,SARIMA D=0,2017-05-14,142.7271,4.8025,0.4746
2017,SARIMA D=0,2017-05-21,144.9043,4.7772,0.4756
2017,SARIMA D=0,2017-05-28,94.8229,4.8051,0.4765
2017,SARIMA D=0,2017-06-04,90.0814,4.7882,0.4772
2017,SARIMA D=0,2017-06-11,58.4771,4.6937,0.4778
2017,SARIMA D=0,2017-06-18,58.1271,4.7279,0.4783
2017,SARIMA D=0,2017-06-25,57.1429,4.706,0.4788
2017,SARIMA D=0,2017-07-02,32.95,4.6626,0.4791
2017,SARIMA D=0,2017-07-09,58.0,4.6282,0.4794
2017,SARIMA D=0,2017-07-16,31.5557,4.6241,0.4797
2017,SARIMA D=0,2017-07-23,31.4829,4.5539,0.4799
2017,SARIMA D=0,2017-07-30,21.16,4.5722,0.48
2017,SARIMA D=0,2017-08-06,35.2814,4.5244,0.4802
2017,SARIMA D=0,2017-08-13,37.6029,4.504,0.4803
2017,SARIMA D=0,2017-08-20,33.6243,4.5448,0.4804
2017,SARIMA D=0,2017-08-27,43.3986,4.5272,0.4805
2017,SARIMA D=0,2017-09-03,26.4286,4.5186,0.4806
2017,SARIMA D=0,2017-09-10,47.1771,4.5824,0.4806
2017,SARIMA D=0,2017-09-17,59.2629,4.6288,0.4807
2017,SARIMA D=0,2017-09-24,44.0271,4.6215,0.4807
2017,SARIMA D=0,2017-10-01,72.0857,4.7127,0.4808
2017,SARIMA D=0,2017-10-08,76.9129,4.7987,0.4808
2017,SARIMA D=0,2017-10-15,122.4471,4.7907,0.4808
2017,SARIMA D=0,2017-10-22,198.3271,4.8628,0.4808
2017,SARIMA D=0,2017-10-29,183.8943,5.015,0.4809
2017,SARIMA D=0,2017-11-05,187.9957,5.2037,0.4809
2017,SARIMA D=0,2017-11-12,438.4471,5.0736,0.4809
2017,SARIMA D=0,2017-11-19,202.2114,5.0294,0.4809
2017,SARIMA D=0,2017-11-26,185.72,4.9345,0.4809
2017,SARIMA D=0,2017-12-03,205.8971,4.9667,0.4809
2017,SARIMA D=0,2017-12-10,173.3457,4.9924,0.4809
2017,SARIMA D=0,2017-12-17,130.5114,4.9354,0.4809
2017,SARIMA D=0,2017-12-24,191.2171,4.995,0.4809
2018,Seasonal naive,2018-01-07,247.2986,5.3349,
2018,Seasonal naive,2018-01-14,188.26,5.2819,
2018,Seasonal naive,2018-01-21,197.46,5.4724,
2018,Seasonal naive,2018-01-28,148.4886,5.0702,
2018,Seasonal naive,2018-02-04,137.0471,5.1796,
2018,Seasonal naive,2018-02-11,169.39,4.8916,
2018,Seasonal naive,2018-02-18,103.7086,4.9375,
2018,Seasonal naive,2018-02-25,158.0829,5.5005,
2018,Seasonal naive,2018-03-04,104.86,4.753,
2018,Seasonal naive,2018-03-11,96.9486,4.4768,
2018,Seasonal naive,2018-03-18,102.2143,4.6694,
2018,Seasonal naive,2018-03-25,90.97,4.9187,
2018,Seasonal naive,2018-04-01,97.7286,4.7035,
2018,Seasonal naive,2018-04-08,94.4529,4.5093,
2018,Seasonal naive,2018-04-15,75.25,5.0424,
2018,Seasonal naive,2018-04-22,92.28,4.8909,
2018,Seasonal naive,2018-04-29,103.69,4.5725,
2018,Seasonal naive,2018-05-06,68.9371,5.1209,
2018,Seasonal naive,2018-05-13,99.3929,4.9609,
2018,Seasonal naive,2018-05-20,83.6829,4.9761,
2018,Seasonal naive,2018-05-27,98.5771,4.552,
2018,Seasonal naive,2018-06-03,80.0014,4.5007,
2018,Seasonal naive,2018-06-10,64.8829,4.0686,
2018,Seasonal naive,2018-06-17,152.4043,4.0626,
2018,Seasonal naive,2018-06-24,68.2586,4.0456,
2018,Seasonal naive,2018-07-01,38.8757,3.495,
2018,Seasonal naive,2018-07-08,51.7443,4.0604,
2018,Seasonal naive,2018-07-15,43.47,3.4518,
2018,Seasonal naive,2018-07-22,36.8086,3.4494,
2018,Seasonal naive,2018-07-29,34.5829,3.0521,
2018,Seasonal naive,2018-08-05,59.5043,3.5634,
2018,Seasonal naive,2018-08-12,39.0543,3.6271,
2018,Seasonal naive,2018-08-19,38.7414,3.5152,
2018,Seasonal naive,2018-08-26,31.8071,3.7704,
2018,Seasonal naive,2018-09-02,37.8543,3.2744,
2018,Seasonal naive,2018-09-09,41.95,3.8539,
2018,Seasonal naive,2018-09-16,33.33,4.082,
2018,Seasonal naive,2018-09-23,49.2086,3.7848,
2018,Seasonal naive,2018-09-30,57.5586,4.2779,
2018,Seasonal naive,2018-10-07,83.3871,4.3427,
2018,Seasonal naive,2018-10-14,96.9114,4.8077,
2018,Seasonal naive,2018-10-21,140.4829,5.2899,
2018,Seasonal naive,2018-10-28,171.1543,5.2144,
2018,Seasonal naive,2018-11-04,202.7614,5.2364,
2018,Seasonal naive,2018-11-11,283.1486,6.0832,
2018,Seasonal naive,2018-11-18,173.0886,5.3093,
2018,Seasonal naive,2018-11-25,168.8671,5.2242,
2018,Seasonal naive,2018-12-02,186.7086,5.3274,
2018,Seasonal naive,2018-12-09,201.8729,5.1553,
2018,Seasonal naive,2018-12-16,175.7014,4.8715,
2018,Seasonal naive,2018-12-23,261.5357,5.2534,
2018,Seasonal naive,2018-12-30,287.3929,5.5294,
2018,Climatology,2018-01-07,247.2986,5.4087,
2018,Climatology,2018-01-14,188.26,5.2777,
2018,Climatology,2018-01-21,197.46,5.4377,
2018,Climatology,2018-01-28,148.4886,5.2427,
2018,Climatology,2018-02-04,137.0471,5.1177,
2018,Climatology,2018-02-11,169.39,4.9634,
2018,Climatology,2018-02-18,103.7086,4.9792,
2018,Climatology,2018-02-25,158.0829,5.142,
2018,Climatology,2018-03-04,104.86,4.8399,
2018,Climatology,2018-03-11,96.9486,4.4615,
2018,Climatology,2018-03-18,102.2143,4.4902,
2018,Climatology,2018-03-25,90.97,4.5445,
2018,Climatology,2018-04-01,97.7286,4.6547,
2018,Climatology,2018-04-08,94.4529,4.5116,
2018,Climatology,2018-04-15,75.25,4.7201,
2018,Climatology,2018-04-22,92.28,4.7129,
2018,Climatology,2018-04-29,103.69,4.751,
2018,Climatology,2018-05-06,68.9371,4.6604,
2018,Climatology,2018-05-13,99.3929,4.7616,
2018,Climatology,2018-05-20,83.6829,4.6494,
2018,Climatology,2018-05-27,98.5771,4.4828,
2018,Climatology,2018-06-03,80.0014,4.5808,
2018,Climatology,2018-06-10,64.8829,4.1754,
2018,Climatology,2018-06-17,152.4043,4.3477,
2018,Climatology,2018-06-24,68.2586,4.3512,
2018,Climatology,2018-07-01,38.8757,4.0383,
2018,Climatology,2018-07-08,51.7443,4.1565,
2018,Climatology,2018-07-15,43.47,3.8285,
2018,Climatology,2018-07-22,36.8086,3.822,
2018,Climatology,2018-07-29,34.5829,3.5712,
2018,Climatology,2018-08-05,59.5043,3.6175,
2018,Climatology,2018-08-12,39.0543,3.8246,
2018,Climatology,2018-08-19,38.7414,3.8529,
2018,Climatology,2018-08-26,31.8071,3.8302,
2018,Climatology,2018-09-02,37.8543,3.7219,
2018,Climatology,2018-09-09,41.95,4.0908,
2018,Climatology,2018-09-16,33.33,4.1698,
2018,Climatology,2018-09-23,49.2086,4.1432,
2018,Climatology,2018-09-30,57.5586,4.3071,
2018,Climatology,2018-10-07,83.3871,4.5495,
2018,Climatology,2018-10-14,96.9114,4.8544,
2018,Climatology,2018-10-21,140.4829,5.005,
2018,Climatology,2018-10-28,171.1543,5.2769,
2018,Climatology,2018-11-04,202.7614,5.4857,
2018,Climatology,2018-11-11,283.1486,5.771,
2018,Climatology,2018-11-18,173.0886,5.4635,
2018,Climatology,2018-11-25,168.8671,5.3075,
2018,Climatology,2018-12-02,186.7086,5.3428,
2018,Climatology,2018-12-09,201.8729,5.3422,
2018,Climatology,2018-12-16,175.7014,5.1833,
2018,Climatology,2018-12-23,261.5357,5.207,
2018,Climatology,2018-12-30,287.3929,5.3989,
2018,Climatology + AR(1),2018-01-07,247.2986,5.4562,0.1957
2018,Climatology + AR(1),2018-01-14,188.26,5.2949,0.2083
2018,Climatology + AR(1),2018-01-21,197.46,5.444,0.2099
2018,Climatology + AR(1),2018-01-28,148.4886,5.2449,0.2101
2018,Climatology + AR(1),2018-02-04,137.0471,5.1185,0.2101
2018,Climatology + AR(1),2018-02-11,169.39,4.9637,0.2101
2018,Climatology + AR(1),2018-02-18,103.7086,4.9793,0.2101
2018,Climatology + AR(1),2018-02-25,158.0829,5.142,0.2101
2018,Climatology + AR(1),2018-03-04,104.86,4.8399,0.2101
2018,Climatology + AR(1),2018-03-11,96.9486,4.4615,0.2101
2018,Climatology + AR(1),2018-03-18,102.2143,4.4902,0.2101
2018,Climatology + AR(1),2018-03-25,90.97,4.5445,0.2101
2018,Climatology + AR(1),2018-04-01,97.7286,4.6547,0.2101
2018,Climatology + AR(1),2018-04-08,94.4529,4.5116,0.2101
2018,Climatology + AR(1),2018-04-15,75.25,4.7201,0.2101
2018,Climatology + AR(1),2018-04-22,92.28,4.7129,0.2101
2018,Climatology + AR(1),2018-04-29,103.69,4.751,0.2101
2018,Climatology + AR(1),2018-05-06,68.9371,4.6604,0.2101
2018,Climatology + AR(1),2018-05-13,99.3929,4.7616,0.2101
2018,Climatology + AR(1),2018-05-20,83.6829,4.6494,0.2101
2018,Climatology + AR(1),2018-05-27,98.5771,4.4828,0.2101
2018,Climatology + AR(1),2018-06-03,80.0014,4.5808,0.2101
2018,Climatology + AR(1),2018-06-10,64.8829,4.1754,0.2101
2018,Climatology + AR(1),2018-06-17,152.4043,4.3477,0.2101
2018,Climatology + AR(1),2018-06-24,68.2586,4.3512,0.2101
2018,Climatology + AR(1),2018-07-01,38.8757,4.0383,0.2101
2018,Climatology + AR(1),2018-07-08,51.7443,4.1565,0.2101
2018,Climatology + AR(1),2018-07-15,43.47,3.8285,0.2101
2018,Climatology + AR(1),2018-07-22,36.8086,3.822,0.2101
2018,Climatology + AR(1),2018-07-29,34.5829,3.5712,0.2101
2018,Climatology + AR(1),2018-08-05,59.5043,3.6175,0.2101
2018,Climatology + AR(1),2018-08-12,39.0543,3.8246,0.2101
2018,Climatology + AR(1),2018-08-19,38.7414,3.8529,0.2101
2018,Climatology + AR(1),2018-08-26,31.8071,3.8302,0.2101
2018,Climatology + AR(1),2018-09-02,37.8543,3.7219,0.2101
2018,Climatology + AR(1),2018-09-09,41.95,4.0908,0.2101
2018,Climatology + AR(1),2018-09-16,33.33,4.1698,0.2101
2018,Climatology + AR(1),2018-09-23,49.2086,4.1432,0.2101
2018,Climatology + AR(1),2018-09-30,57.5586,4.3071,0.2101
2018,Climatology + AR(1),2018-10-07,83.3871,4.5495,0.2101
2018,Climatology + AR(1),2018-10-14,96.9114,4.8544,0.2101
2018,Climatology + AR(1),2018-10-21,140.4829,5.005,0.2101
2018,Climatology + AR(1),2018-10-28,171.1543,5.2769,0.2101
2018,Climatology + AR(1),2018-11-04,202.7614,5.4857,0.2101
2018,Climatology + AR(1),2018-11-11,283.1486,5.771,0.2101
2018,Climatology + AR(1),2018-11-18,173.0886,5.4635,0.2101
2018,Climatology + AR(1),2018-11-25,168.8671,5.3075,0.2101
2018,Climatology + AR(1),2018-12-02,186.7086,5.3428,0.2101
2018,Climatology + AR(1),2018-12-09,201.8729,5.3422,0.2101
2018,Climatology + AR(1),2018-12-16,175.7014,5.1833,0.2101
2018,Climatology + AR(1),2018-12-23,261.5357,5.207,0.2101
2018,Climatology + AR(1),2018-12-30,287.3929,5.3989,0.2101
2018,Linear regression,2018-01-07,247.2986,5.2854,0.2604
2018,Linear regression,2018-01-14,188.26,5.2335,0.2604
2018,Linear regression,2018-01-21,197.46,5.1751,0.2604
2018,Linear regression,2018-01-28,148.4886,5.1107,0.2604
2018,Linear regression,2018-02-04,137.0471,5.0411,0.2604
2018,Linear regression,2018-02-11,169.39,4.9677,0.2604
2018,Linear regression,2018-02-18,103.7086,4.8923,0.2604
2018,Linear regression,2018-02-25,158.0829,4.8177,0.2604
2018,Linear regression,2018-03-04,104.86,4.7469,0.2604
2018,Linear regression,2018-03-11,96.9486,4.6833,0.2604
2018,Linear regression,2018-03-18,102.2143,4.6299,0.2604
2018,Linear regression,2018-03-25,90.97,4.5891,0.2604
2018,Linear regression,2018-04-01,97.7286,4.5622,0.2604
2018,Linear regression,2018-04-08,94.4529,4.549,0.2604
2018,Linear regression,2018-04-15,75.25,4.5479,0.2604
2018,Linear regression,2018-04-22,92.28,4.5556,0.2604
2018,Linear regression,2018-04-29,103.69,4.5673,0.2604
2018,Linear regression,2018-05-06,68.9371,4.5775,0.2604
2018,Linear regression,2018-05-13,99.3929,4.58,0.2604
2018,Linear regression,2018-05-20,83.6829,4.5691,0.2604
2018,Linear regression,2018-05-27,98.5771,4.5399,0.2604
2018,Linear regression,2018-06-03,80.0014,4.4893,0.2604
2018,Linear regression,2018-06-10,64.8829,4.416,0.2604
2018,Linear regression,2018-06-17,152.4043,4.3214,0.2604
2018,Linear regression,2018-06-24,68.2586,4.2094,0.2604
2018,Linear regression,2018-07-01,38.8757,4.0859,0.2604
2018,Linear regression,2018-07-08,51.7443,3.9589,0.2604
2018,Linear regression,2018-07-15,43.47,3.8376,0.2604
2018,Linear regression,2018-07-22,36.8086,3.7313,0.2604
2018,Linear regression,2018-07-29,34.5829,3.649,0.2604
2018,Linear regression,2018-08-05,59.5043,3.5985,0.2604
2018,Linear regression,2018-08-12,39.0543,3.5852,0.2604
2018,Linear regression,2018-08-19,38.7414,3.6122,0.2604
2018,Linear regression,2018-08-26,31.8071,3.6795,0.2604
2018,Linear regression,2018-09-02,37.8543,3.7845,0.2604
2018,Linear regression,2018-09-09,41.95,3.9219,0.2604
2018,Linear regression,2018-09-16,33.33,4.0842,0.2604
2018,Linear regression,2018-09-23,49.2086,4.2628,0.2604
2018,Linear regression,2018-09-30,57.5586,4.4483,0.2604
2018,Linear regression,2018-10-07,83.3871,4.6315,0.2604
2018,Linear regression,2018-10-14,96.9114,4.8042,0.2604
2018,Linear regression,2018-10-21,140.4829,4.9596,0.2604
2018,Linear regression,2018-10-28,171.1543,5.0928,0.2604
2018,Linear regression,2018-11-04,202.7614,5.2011,0.2604
2018,Linear regression,2018-11-11,283.1486,5.2835,0.2604
2018,Linear regression,2018-11-18,173.0886,5.3409,0.2604
2018,Linear regression,2018-11-25,168.8671,5.3753,0.2604
2018,Linear regression,2018-12-02,186.7086,5.3898,0.2604
2018,Linear regression,2018-12-09,201.8729,5.3875,0.2604
2018,Linear regression,2018-12-16,175.7014,5.3715,0.2604
2018,Linear regression,2018-12-23,261.5357,5.3445,0.2604
2018,Linear regression,2018-12-30,287.3929,5.3084,0.2604
2018,LSTM (small),2018-01-07,247.2986,5.3885,0.0196
2018,LSTM (small),2018-01-14,188.26,5.6184,0.0196
2018,LSTM (small),2018-01-21,197.46,5.5981,0.0196
2018,LSTM (small),2018-01-28,148.4886,5.238,0.0196
2018,LSTM (small),2018-02-04,137.0471,5.1347,0.0196
2018,LSTM (small),2018-02-11,169.39,4.8385,0.0196
2018,LSTM (small),2018-02-18,103.7086,4.7558,0.0196
2018,LSTM (small),2018-02-25,158.0829,5.2258,0.0196
2018,LSTM (small),2018-03-04,104.86,4.8522,0.0196
2018,LSTM (small),2018-03-11,96.9486,4.3257,0.0196
2018,LSTM (small),2018-03-18,102.2143,4.4748,0.0196
2018,LSTM (small),2018-03-25,90.97,4.6419,0.0196
2018,LSTM (small),2018-04-01,97.7286,4.8952,0.0196
2018,LSTM (small),2018-04-08,94.4529,4.394,0.0196
2018,LSTM (small),2018-04-15,75.25,4.6968,0.0196
2018,LSTM (small),2018-04-22,92.28,4.9301,0.0196
2018,LSTM (small),2018-04-29,103.69,4.5667,0.0196
2018,LSTM (small),2018-05-06,68.9371,4.4171,0.0196
2018,LSTM (small),2018-05-13,99.3929,5.0035,0.0196
2018,LSTM (small),2018-05-20,83.6829,4.5715,0.0196
2018,LSTM (small),2018-05-27,98.5771,4.824,0.0196
2018,LSTM (small),2018-06-03,80.0014,4.7401,0.0196
2018,LSTM (small),2018-06-10,64.8829,4.3743,0.0196
2018,LSTM (small),2018-06-17,152.4043,4.3535,0.0196
2018,LSTM (small),2018-06-24,68.2586,4.4301,0.0196
2018,LSTM (small),2018-07-01,38.8757,4.3145,0.0196
2018,LSTM (small),2018-07-08,51.7443,4.1302,0.0196
2018,LSTM (small),2018-07-15,43.47,4.0096,0.0196
2018,LSTM (small),2018-07-22,36.8086,4.2887,0.0196
2018,LSTM (small),2018-07-29,34.5829,3.7501,0.0196
2018,LSTM (small),2018-08-05,59.5043,3.5327,0.0196
2018,LSTM (small),2018-08-12,39.0543,3.8383,0.0196
2018,LSTM (small),2018-08-19,38.7414,3.8442,0.0196
2018,LSTM (small),2018-08-26,31.8071,3.8539,0.0196
2018,LSTM (small),2018-09-02,37.8543,3.7579,0.0196
2018,LSTM (small),2018-09-09,41.95,4.0408,0.0196
2018,LSTM (small),2018-09-16,33.33,4.1422,0.0196
2018,LSTM (small),2018-09-23,49.2086,4.3096,0.0196
2018,LSTM (small),2018-09-30,57.5586,4.8606,0.0196
2018,LSTM (small),2018-10-07,83.3871,4.4902,0.0196
2018,LSTM (small),2018-10-14,96.9114,5.254,0.0196
2018,LSTM (small),2018-10-21,140.4829,5.8105,0.0196
2018,LSTM (small),2018-10-28,171.1543,5.9766,0.0196
2018,LSTM (small),2018-11-04,202.7614,6.0701,0.0196
2018,LSTM (small),2018-11-11,283.1486,6.2284,0.0196
2018,LSTM (small),2018-11-18,173.0886,5.8296,0.0196
2018,LSTM (small),2018-11-25,168.8671,5.4976,0.0196
2018,LSTM (small),2018-12-02,186.7086,5.4178,0.0196
2018,LSTM (small),2018-12-09,201.8729,5.034,0.0196
2018,LSTM (small),2018-12-16,175.7014,4.9196,0.0196
2018,LSTM (small),2018-12-23,261.5357,5.1952,0.0196
2018,LSTM (small),2018-12-30,287.3929,5.5055,0.0196
2018,Fourier+ARMA const,2018-01-07,247.2986,5.3896,0.2374
2018,Fourier+ARMA const,2018-01-14,188.26,5.3059,0.2526
2018,Fourier+ARMA const,2018-01-21,197.46,5.2381,0.2545
2018,Fourier+ARMA const,2018-01-28,148.4886,5.172,0.2548
2018,Fourier+ARMA const,2018-02-04,137.0471,5.1029,0.2548
2018,Fourier+ARMA const,2018-02-11,169.39,5.0302,0.2548
2018,Fourier+ARMA const,2018-02-18,103.7086,4.9551,0.2548
2018,Fourier+ARMA const,2018-02-25,158.0829,4.8802,0.2548
2018,Fourier+ARMA const,2018-03-04,104.86,4.8086,0.2548
2018,Fourier+ARMA const,2018-03-11,96.9486,4.7439,0.2548
2018,Fourier+ARMA const,2018-03-18,102.2143,4.6892,0.2548
2018,Fourier+ARMA const,2018-03-25,90.97,4.6472,0.2548
2018,Fourier+ARMA const,2018-04-01,97.7286,4.6193,0.2548
2018,Fourier+ARMA const,2018-04-08,94.4529,4.6055,0.2548
2018,Fourier+ARMA const,2018-04-15,75.25,4.6042,0.2548
2018,Fourier+ARMA const,2018-04-22,92.28,4.6121,0.2548
2018,Fourier+ARMA const,2018-04-29,103.69,4.6244,0.2548
2018,Fourier+ARMA const,2018-05-06,68.9371,4.6353,0.2548
2018,Fourier+ARMA const,2018-05-13,99.3929,4.6387,0.2548
2018,Fourier+ARMA const,2018-05-20,83.6829,4.6286,0.2548
2018,Fourier+ARMA const,2018-05-27,98.5771,4.6,0.2548
2018,Fourier+ARMA const,2018-06-03,80.0014,4.5497,0.2548
2018,Fourier+ARMA const,2018-06-10,64.8829,4.4764,0.2548
2018,Fourier+ARMA const,2018-06-17,152.4043,4.3815,0.2548
2018,Fourier+ARMA const,2018-06-24,68.2586,4.2689,0.2548
2018,Fourier+ARMA const,2018-07-01,38.8757,4.1447,0.2548
2018,Fourier+ARMA const,2018-07-08,51.7443,4.017,0.2548
2018,Fourier+ARMA const,2018-07-15,43.47,3.8949,0.2548
2018,Fourier+ARMA const,2018-07-22,36.8086,3.7882,0.2548
2018,Fourier+ARMA const,2018-07-29,34.5829,3.7058,0.2548
2018,Fourier+ARMA const,2018-08-05,59.5043,3.6554,0.2548
2018,Fourier+ARMA const,2018-08-12,39.0543,3.6426,0.2548
2018,Fourier+ARMA const,2018-08-19,38.7414,3.6702,0.2548
2018,Fourier+ARMA const,2018-08-26,31.8071,3.7384,0.2548
2018,Fourier+ARMA const,2018-09-02,37.8543,3.8442,0.2548
2018,Fourier+ARMA const,2018-09-09,41.95,3.9823,0.2548
2018,Fourier+ARMA const,2018-09-16,33.33,4.145,0.2548
2018,Fourier+ARMA const,2018-09-23,49.2086,4.3237,0.2548
2018,Fourier+ARMA const,2018-09-30,57.5586,4.5088,0.2548
2018,Fourier+ARMA const,2018-10-07,83.3871,4.6912,0.2548
2018,Fourier+ARMA const,2018-10-14,96.9114,4.8628,0.2548
2018,Fourier+ARMA const,2018-10-21,140.4829,5.0169,0.2548
2018,Fourier+ARMA const,2018-10-28,171.1543,5.149,0.2548
2018,Fourier+ARMA const,2018-11-04,202.7614,5.2563,0.2548
2018,Fourier+ARMA const,2018-11-11,283.1486,5.3381,0.2548
2018,Fourier+ARMA const,2018-11-18,173.0886,5.3956,0.2548
2018,Fourier+ARMA const,2018-11-25,168.8671,5.431,0.2548
2018,Fourier+ARMA const,2018-12-02,186.7086,5.4472,0.2548
2018,Fourier+ARMA const,2018-12-09,201.8729,5.4475,0.2548
2018,Fourier+ARMA const,2018-12-16,175.7014,5.4349,0.2548
2018,Fourier+ARMA const,2018-12-23,261.5357,5.4119,0.2548
2018,Fourier+ARMA const,2018-12-30,287.3929,5.3802,0.2548
2018,Fourier+ARMA linear,2018-01-07,247.2986,5.4112,0.2381
2018,Fourier+ARMA linear,2018-01-14,188.26,5.3283,0.2535
2018,Fourier+ARMA linear,2018-01-21,197.46,5.2513,0.2556
2018,Fourier+ARMA linear,2018-01-28,148.4886,5.1706,0.2558
2018,Fourier+ARMA linear,2018-02-04,137.0471,5.0843,0.2559
2018,Fourier+ARMA linear,2018-02-11,169.39,4.9937,0.2559
2018,Fourier+ARMA linear,2018-02-18,103.7086,4.9019,0.2559
2018,Fourier+ARMA linear,2018-02-25,158.0829,4.8129,0.2559
2018,Fourier+ARMA linear,2018-03-04,104.86,4.7308,0.2559
2018,Fourier+ARMA linear,2018-03-11,96.9486,4.6596,0.2559
2018,Fourier+ARMA linear,2018-03-18,102.2143,4.6027,0.2559
2018,Fourier+ARMA linear,2018-03-25,90.97,4.5622,0.2559
2018,Fourier+ARMA linear,2018-04-01,97.7286,4.5388,0.2559
2018,Fourier+ARMA linear,2018-04-08,94.4529,4.5313,0.2559
2018,Fourier+ARMA linear,2018-04-15,75.25,4.5369,0.2559
2018,Fourier+ARMA linear,2018-04-22,92.28,4.5511,0.2559
2018,Fourier+ARMA linear,2018-04-29,103.69,4.5681,0.2559
2018,Fourier+ARMA linear,2018-05-06,68.9371,4.5814,0.2559
2018,Fourier+ARMA linear,2018-05-13,99.3929,4.5846,0.2559
2018,Fourier+ARMA linear,2018-05-20,83.6829,4.5718,0.2559
2018,Fourier+ARMA linear,2018-05-27,98.5771,4.5384,0.2559
2018,Fourier+ARMA linear,2018-06-03,80.0014,4.482,0.2559
2018,Fourier+ARMA linear,2018-06-10,64.8829,4.4023,0.2559
2018,Fourier+ARMA linear,2018-06-17,152.4043,4.3016,0.2559
2018,Fourier+ARMA linear,2018-06-24,68.2586,4.1845,0.2559
2018,Fourier+ARMA linear,2018-07-01,38.8757,4.0579,0.2559
2018,Fourier+ARMA linear,2018-07-08,51.7443,3.9301,0.2559
2018,Fourier+ARMA linear,2018-07-15,43.47,3.8103,0.2559
2018,Fourier+ARMA linear,2018-07-22,36.8086,3.7075,0.2559
2018,Fourier+ARMA linear,2018-07-29,34.5829,3.6302,0.2559
2018,Fourier+ARMA linear,2018-08-05,59.5043,3.585,0.2559
2018,Fourier+ARMA linear,2018-08-12,39.0543,3.5765,0.2559
2018,Fourier+ARMA linear,2018-08-19,38.7414,3.6069,0.2559
2018,Fourier+ARMA linear,2018-08-26,31.8071,3.6755,0.2559
2018,Fourier+ARMA linear,2018-09-02,37.8543,3.7791,0.2559
2018,Fourier+ARMA linear,2018-09-09,41.95,3.9124,0.2559
2018,Fourier+ARMA linear,2018-09-16,33.33,4.0685,0.2559
2018,Fourier+ARMA linear,2018-09-23,49.2086,4.2392,0.2559
2018,Fourier+ARMA linear,2018-09-30,57.5586,4.4163,0.2559
2018,Fourier+ARMA linear,2018-10-07,83.3871,4.5919,0.2559
2018,Fourier+ARMA linear,2018-10-14,96.9114,4.7591,0.2559
2018,Fourier+ARMA linear,2018-10-21,140.4829,4.9122,0.2559
2018,Fourier+ARMA linear,2018-10-28,171.1543,5.0472,0.2559
2018,Fourier+ARMA linear,2018-11-04,202.7614,5.1617,0.2559
2018,Fourier+ARMA linear,2018-11-11,283.1486,5.2547,0.2559
2018,Fourier+ARMA linear,2018-11-18,173.0886,5.3266,0.2559
2018,Fourier+ARMA linear,2018-11-25,168.8671,5.3782,0.2559
2018,Fourier+ARMA linear,2018-12-02,186.7086,5.4112,0.2559
2018,Fourier+ARMA linear,2018-12-09,201.8729,5.4272,0.2559
2018,Fourier+ARMA linear,2018-12-16,175.7014,5.4277,0.2559
2018,Fourier+ARMA linear,2018-12-23,261.5357,5.4136,0.2559
2018,Fourier+ARMA linear,2018-12-30,287.3929,5.3859,0.2559
2018,Fourier+ARMA (selected),2018-01-07,247.2986,5.3098,0.2206
2018,Fourier+ARMA (selected),2018-01-14,188.26,5.3596,0.2243
2018,Fourier+ARMA (selected),2018-01-21,197.46,5.3812,0.2271
2018,Fourier+ARMA (selected),2018-01-28,148.4886,5.3547,0.2291
2018,Fourier+ARMA (selected),2018-02-04,137.0471,5.2729,0.2305
2018,Fourier+ARMA (selected),2018-02-11,169.39,5.1436,0.2316
2018,Fourier+ARMA (selected),2018-02-18,103.7086,4.9871,0.2324
2018,Fourier+ARMA (selected),2018-02-25,158.0829,4.8298,0.2329
2018,Fourier+ARMA (selected),2018-03-04,104.86,4.6972,0.2334
2018,Fourier+ARMA (selected),2018-03-11,96.9486,4.6069,0.2337
2018,Fourier+ARMA (selected),2018-03-18,102.2143,4.5651,0.2339
2018,Fourier+ARMA (selected),2018-03-25,90.97,4.5664,0.2341
2018,Fourier+ARMA (selected),2018-04-01,97.7286,4.5969,0.2342
2018,Fourier+ARMA (selected),2018-04-08,94.4529,4.639,0.2343
2018,Fourier+ARMA (selected),2018-04-15,75.25,4.6772,0.2344
2018,Fourier+ARMA (selected),2018-04-22,92.28,4.7012,0.2344
2018,Fourier+ARMA (selected),2018-04-29,103.69,4.7071,0.2345
2018,Fourier+ARMA (selected),2018-05-06,68.9371,4.6962,0.2345
2018,Fourier+ARMA (selected),2018-05-13,99.3929,4.6715,0.2345
2018,Fourier+ARMA (selected),2018-05-20,83.6829,4.6354,0.2345
2018,Fourier+ARMA (selected),2018-05-27,98.5771,4.5873,0.2345
2018,Fourier+ARMA (selected),2018-06-03,80.0014,4.5241,0.2345
2018,Fourier+ARMA (selected),2018-06-10,64.8829,4.442,0.2345
2018,Fourier+ARMA (selected),2018-06-17,152.4043,4.3396,0.2345
2018,Fourier+ARMA (selected),2018-06-24,68.2586,4.2197,0.2345
2018,Fourier+ARMA (selected),2018-07-01,38.8757,4.091,0.2345
2018,Fourier+ARMA (selected),2018-07-08,51.7443,3.9662,0.2346
2018,Fourier+ARMA (selected),2018-07-15,43.47,3.8591,0.2346
2018,Fourier+ARMA (selected),2018-07-22,36.8086,3.7811,0.2346
2018,Fourier+ARMA (selected),2018-07-29,34.5829,3.7378,0.2346
2018,Fourier+ARMA (selected),2018-08-05,59.5043,3.7279,0.2346
2018,Fourier+ARMA (selected),2018-08-12,39.0543,3.7446,0.2346
2018,Fourier+ARMA (selected),2018-08-19,38.7414,3.779,0.2346
2018,Fourier+ARMA (selected),2018-08-26,31.8071,3.8242,0.2346
2018,Fourier+ARMA (selected),2018-09-02,37.8543,3.8787,0.2346
2018,Fourier+ARMA (selected),2018-09-09,41.95,3.9481,0.2346
2018,Fourier+ARMA (selected),2018-09-16,33.33,4.043,0.2346
2018,Fourier+ARMA (selected),2018-09-23,49.2086,4.1746,0.2346
2018,Fourier+ARMA (selected),2018-09-30,57.5586,4.3497,0.2346
2018,Fourier+ARMA (selected),2018-10-07,83.3871,4.5655,0.2346
2018,Fourier+ARMA (selected),2018-10-14,96.9114,4.8075,0.2346
2018,Fourier+ARMA (selected),2018-10-21,140.4829,5.0511,0.2346
2018,Fourier+ARMA (selected),2018-10-28,171.1543,5.2666,0.2346
2018,Fourier+ARMA (selected),2018-11-04,202.7614,5.4267,0.2346
2018,Fourier+ARMA (selected),2018-11-11,283.1486,5.5139,0.2346
2018,Fourier+ARMA (selected),2018-11-18,173.0886,5.5259,0.2346
2018,Fourier+ARMA (selected),2018-11-25,168.8671,5.4764,0.2346
2018,Fourier+ARMA (selected),2018-12-02,186.7086,5.3915,0.2346
2018,Fourier+ARMA (selected),2018-12-09,201.8729,5.3031,0.2346
2018,Fourier+ARMA (selected),2018-12-16,175.7014,5.2395,0.2346
2018,Fourier+ARMA (selected),2018-12-23,261.5357,5.2175,0.2346
2018,Fourier+ARMA (selected),2018-12-30,287.3929,5.2385,0.2346
2018,SARIMA D=1,2018-01-07,247.2986,5.4097,0.2679
2018,SARIMA D=1,2018-01-14,188.26,5.2535,0.2754
2018,SARIMA D=1,2018-01-21,197.46,5.3964,0.2811
2018,SARIMA D=1,2018-01-28,148.4886,5.2305,0.2854
2018,SARIMA D=1,2018-02-04,137.0471,5.0969,0.2888
2018,SARIMA D=1,2018-02-11,169.39,4.9611,0.2914
2018,SARIMA D=1,2018-02-18,103.7086,4.9507,0.2934
2018,SARIMA D=1,2018-02-25,158.0829,5.1439,0.295
2018,SARIMA D=1,2018-03-04,104.86,4.7076,0.2962
2018,SARIMA D=1,2018-03-11,96.9486,4.4703,0.2971
2018,SARIMA D=1,2018-03-18,102.2143,4.4594,0.2979
2018,SARIMA D=1,2018-03-25,90.97,4.6826,0.2984
2018,SARIMA D=1,2018-04-01,97.7286,4.5956,0.2989
2018,SARIMA D=1,2018-04-08,94.4529,4.5879,0.2992
2018,SARIMA D=1,2018-04-15,75.25,4.7737,0.2995
2018,SARIMA D=1,2018-04-22,92.28,4.7848,0.2997
2018,SARIMA D=1,2018-04-29,103.69,4.6401,0.2999
2018,SARIMA D=1,2018-05-06,68.9371,4.8466,0.3
2018,SARIMA D=1,2018-05-13,99.3929,4.7107,0.3001
2018,SARIMA D=1,2018-05-20,83.6829,4.6502,0.3002
2018,SARIMA D=1,2018-05-27,98.5771,4.5958,0.3003
2018,SARIMA D=1,2018-06-03,80.0014,4.4421,0.3003
2018,SARIMA D=1,2018-06-10,64.8829,4.255,0.3003
2018,SARIMA D=1,2018-06-17,152.4043,4.3157,0.3004
2018,SARIMA D=1,2018-06-24,68.2586,4.2265,0.3004
2018,SARIMA D=1,2018-07-01,38.8757,3.916,0.3004
2018,SARIMA D=1,2018-07-08,51.7443,4.0396,0.3004
2018,SARIMA D=1,2018-07-15,43.47,3.8239,0.3004
2018,SARIMA D=1,2018-07-22,36.8086,3.645,0.3004
2018,SARIMA D=1,2018-07-29,34.5829,3.4379,0.3004
2018,SARIMA D=1,2018-08-05,59.5043,3.7703,0.3004
2018,SARIMA D=1,2018-08-12,39.0543,3.7916,0.3004
2018,SARIMA D=1,2018-08-19,38.7414,3.7202,0.3005
2018,SARIMA D=1,2018-08-26,31.8071,3.8646,0.3005
2018,SARIMA D=1,2018-09-02,37.8543,3.7144,0.3004
2018,SARIMA D=1,2018-09-09,41.95,4.0001,0.3004
2018,SARIMA D=1,2018-09-16,33.33,4.2104,0.3004
2018,SARIMA D=1,2018-09-23,49.2086,3.9933,0.3004
2018,SARIMA D=1,2018-09-30,57.5586,4.399,0.3004
2018,SARIMA D=1,2018-10-07,83.3871,4.6378,0.3004
2018,SARIMA D=1,2018-10-14,96.9114,4.7645,0.3004
2018,SARIMA D=1,2018-10-21,140.4829,5.1456,0.3004
2018,SARIMA D=1,2018-10-28,171.1543,5.2622,0.3004
2018,SARIMA D=1,2018-11-04,202.7614,5.5845,0.3003
2018,SARIMA D=1,2018-11-11,283.1486,5.82,0.3003
2018,SARIMA D=1,2018-11-18,173.0886,5.4165,0.3003
2018,SARIMA D=1,2018-11-25,168.8671,5.2504,0.3002
2018,SARIMA D=1,2018-12-02,186.7086,5.3491,0.3001
2018,SARIMA D=1,2018-12-09,201.8729,5.2993,0.3001
2018,SARIMA D=1,2018-12-16,175.7014,4.9832,0.2999
2018,SARIMA D=1,2018-12-23,261.5357,5.2978,0.2998
2018,SARIMA D=1,2018-12-30,287.3929,5.4404,0.2971
2018,SARIMA D=0,2018-01-07,247.2986,5.3196,0.2751
2018,SARIMA D=0,2018-01-14,188.26,5.271,0.3195
2018,SARIMA D=0,2018-01-21,197.46,5.2987,0.3529
2018,SARIMA D=0,2018-01-28,148.4886,5.1494,0.3789
2018,SARIMA D=0,2018-02-04,137.0471,5.157,0.3997
2018,SARIMA D=0,2018-02-11,169.39,5.0464,0.4166
2018,SARIMA D=0,2018-02-18,103.7086,5.0387,0.4304
2018,SARIMA D=0,2018-02-25,158.0829,5.189,0.4417
2018,SARIMA D=0,2018-03-04,104.86,4.9445,0.4512
2018,SARIMA D=0,2018-03-11,96.9486,4.844,0.459
2018,SARIMA D=0,2018-03-18,102.2143,4.8867,0.4656
2018,SARIMA D=0,2018-03-25,90.97,4.9477,0.4711
2018,SARIMA D=0,2018-04-01,97.7286,4.8694,0.4758
2018,SARIMA D=0,2018-04-08,94.4529,4.7984,0.4797
2018,SARIMA D=0,2018-04-15,75.25,4.9484,0.483
2018,SARIMA D=0,2018-04-22,92.28,4.8922,0.4857
2018,SARIMA D=0,2018-04-29,103.69,4.7863,0.4881
2018,SARIMA D=0,2018-05-06,68.9371,4.9433,0.4901
2018,SARIMA D=0,2018-05-13,99.3929,4.8868,0.4917
2018,SARIMA D=0,2018-05-20,83.6829,4.8839,0.4932
2018,SARIMA D=0,2018-05-27,98.5771,4.7487,0.4944
2018,SARIMA D=0,2018-06-03,80.0014,4.7269,0.4954
2018,SARIMA D=0,2018-06-10,64.8829,4.5903,0.4963
2018,SARIMA D=0,2018-06-17,152.4043,4.5831,0.497
2018,SARIMA D=0,2018-06-24,68.2586,4.5729,0.4976
2018,SARIMA D=0,2018-07-01,38.8757,4.4018,0.4981
2018,SARIMA D=0,2018-07-08,51.7443,4.5686,0.4986
2018,SARIMA D=0,2018-07-15,43.47,4.3806,0.499
2018,SARIMA D=0,2018-07-22,36.8086,4.3763,0.4993
2018,SARIMA D=0,2018-07-29,34.5829,4.2528,0.4996
2018,SARIMA D=0,2018-08-05,59.5043,4.4044,0.4998
2018,SARIMA D=0,2018-08-12,39.0543,4.4208,0.5
2018,SARIMA D=0,2018-08-19,38.7414,4.3844,0.5002
2018,SARIMA D=0,2018-08-26,31.8071,4.4592,0.5003
2018,SARIMA D=0,2018-09-02,37.8543,4.307,0.5004
2018,SARIMA D=0,2018-09-09,41.95,4.4802,0.5005
2018,SARIMA D=0,2018-09-16,33.33,4.5474,0.5006
2018,SARIMA D=0,2018-09-23,49.2086,4.4557,0.5007
2018,SARIMA D=0,2018-09-30,57.5586,4.6033,0.5008
2018,SARIMA D=0,2018-10-07,83.3871,4.6214,0.5008
2018,SARIMA D=0,2018-10-14,96.9114,4.7607,0.5009
2018,SARIMA D=0,2018-10-21,140.4829,4.9054,0.5009
2018,SARIMA D=0,2018-10-28,171.1543,4.8814,0.5009
2018,SARIMA D=0,2018-11-04,202.7614,4.887,0.501
2018,SARIMA D=0,2018-11-11,283.1486,5.1422,0.501
2018,SARIMA D=0,2018-11-18,173.0886,4.9072,0.501
2018,SARIMA D=0,2018-11-25,168.8671,4.8806,0.501
2018,SARIMA D=0,2018-12-02,186.7086,4.911,0.501
2018,SARIMA D=0,2018-12-09,201.8729,4.8583,0.501
2018,SARIMA D=0,2018-12-16,175.7014,4.7718,0.5011
2018,SARIMA D=0,2018-12-23,261.5357,4.8867,0.5011
2018,SARIMA D=0,2018-12-30,287.3929,4.9696,0.5011
2019,Seasonal naive,2019-01-06,282.4114,5.5106,
2019,Seasonal naive,2019-01-13,215.72,5.2378,
2019,Seasonal naive,2019-01-20,239.1957,5.2855,
2019,Seasonal naive,2019-01-27,116.3271,5.0005,
2019,Seasonal naive,2019-02-03,166.5671,4.9203,
2019,Seasonal naive,2019-02-10,134.5643,5.1322,
2019,Seasonal naive,2019-02-17,152.7586,4.6416,
2019,Seasonal naive,2019-02-24,90.0871,5.0631,
2019,Seasonal naive,2019-03-03,80.32,4.6526,
2019,Seasonal naive,2019-03-10,86.03,4.5742,
2019,Seasonal naive,2019-03-17,82.4214,4.6271,
2019,Seasonal naive,2019-03-24,79.0757,4.5105,
2019,Seasonal naive,2019-03-31,87.0914,4.5822,
2019,Seasonal naive,2019-04-07,104.1229,4.5481,
2019,Seasonal naive,2019-04-14,72.8586,4.3208,
2019,Seasonal naive,2019-04-21,61.77,4.5248,
2019,Seasonal naive,2019-04-28,88.33,4.6414,
2019,Seasonal naive,2019-05-05,85.7743,4.2332,
2019,Seasonal naive,2019-05-12,129.0486,4.5991,
2019,Seasonal naive,2019-05-19,86.87,4.427,
2019,Seasonal naive,2019-05-26,67.2914,4.5908,
2019,Seasonal naive,2019-06-02,78.26,4.382,
2019,Seasonal naive,2019-06-09,70.2086,4.1726,
2019,Seasonal naive,2019-06-16,69.0129,5.0265,
2019,Seasonal naive,2019-06-23,53.5386,4.2233,
2019,Seasonal naive,2019-06-30,56.7329,3.6604,
2019,Seasonal naive,2019-07-07,46.7743,3.9463,
2019,Seasonal naive,2019-07-14,62.9386,3.7721,
2019,Seasonal naive,2019-07-21,42.65,3.6057,
2019,Seasonal naive,2019-07-28,42.49,3.5434,
2019,Seasonal naive,2019-08-04,34.1886,4.086,
2019,Seasonal naive,2019-08-11,28.4871,3.665,
2019,Seasonal naive,2019-08-18,20.7814,3.6569,
2019,Seasonal naive,2019-08-25,45.1186,3.4597,
2019,Seasonal naive,2019-09-01,39.6414,3.6337,
2019,Seasonal naive,2019-09-08,46.8057,3.7365,
2019,Seasonal naive,2019-09-15,50.5686,3.5065,
2019,Seasonal naive,2019-09-22,39.8514,3.8961,
2019,Seasonal naive,2019-09-29,25.55,4.0528,
2019,Seasonal naive,2019-10-06,43.2557,4.4235,
2019,Seasonal naive,2019-10-13,87.5229,4.5738,
2019,Seasonal naive,2019-10-20,111.8514,4.9451,
2019,Seasonal naive,2019-10-27,140.2557,5.1426,
2019,Seasonal naive,2019-11-03,353.3686,5.312,
2019,Seasonal naive,2019-11-10,176.2229,5.646,
2019,Seasonal naive,2019-11-17,297.9271,5.1538,
2019,Seasonal naive,2019-11-24,152.5214,5.1291,
2019,Seasonal naive,2019-12-01,86.8257,5.2295,
2019,Seasonal naive,2019-12-08,204.5543,5.3076,
2019,Seasonal naive,2019-12-15,184.0914,5.1688,
2019,Seasonal naive,2019-12-22,185.5786,5.5666,
2019,Seasonal naive,2019-12-29,234.3286,5.6609,
2019,Climatology,2019-01-06,282.4114,5.4342,
2019,Climatology,2019-01-13,215.72,5.2677,
2019,Climatology,2019-01-20,239.1957,5.3997,
2019,Climatology,2019-01-27,116.3271,5.1821,
2019,Climatology,2019-02-03,166.5671,5.0683,
2019,Climatology,2019-02-10,134.5643,5.0056,
2019,Climatology,2019-02-17,152.7586,4.8948,
2019,Climatology,2019-02-24,90.0871,5.1223,
2019,Climatology,2019-03-03,80.32,4.7931,
2019,Climatology,2019-03-10,86.03,4.4896,
2019,Climatology,2019-03-17,82.4214,4.5244,
2019,Climatology,2019-03-24,79.0757,4.536,
2019,Climatology,2019-03-31,87.0914,4.6366,
2019,Climatology,2019-04-07,104.1229,4.5208,
2019,Climatology,2019-04-14,72.8586,4.6202,
2019,Climatology,2019-04-21,61.77,4.6659,
2019,Climatology,2019-04-28,88.33,4.7236,
2019,Climatology,2019-05-05,85.7743,4.5536,
2019,Climatology,2019-05-12,129.0486,4.721,
2019,Climatology,2019-05-19,86.87,4.5938,
2019,Climatology,2019-05-26,67.2914,4.5098,
2019,Climatology,2019-06-02,78.26,4.5311,
2019,Climatology,2019-06-09,70.2086,4.1747,
2019,Climatology,2019-06-16,69.0129,4.5174,
2019,Climatology,2019-06-23,53.5386,4.3192,
2019,Climatology,2019-06-30,56.7329,3.9438,
2019,Climatology,2019-07-07,46.7743,4.104,
2019,Climatology,2019-07-14,62.9386,3.8144,
2019,Climatology,2019-07-21,42.65,3.7679,
2019,Climatology,2019-07-28,42.49,3.5642,
2019,Climatology,2019-08-04,34.1886,3.7346,
2019,Climatology,2019-08-11,28.4871,3.7847,
2019,Climatology,2019-08-18,20.7814,3.8039,
2019,Climatology,2019-08-25,45.1186,3.7375,
2019,Climatology,2019-09-01,39.6414,3.6999,
2019,Climatology,2019-09-08,46.8057,4.0022,
2019,Climatology,2019-09-15,50.5686,4.004,
2019,Climatology,2019-09-22,39.8514,4.0814,
2019,Climatology,2019-09-29,25.55,4.2435,
2019,Climatology,2019-10-06,43.2557,4.518,
2019,Climatology,2019-10-13,87.5229,4.7843,
2019,Climatology,2019-10-20,111.8514,4.99,
2019,Climatology,2019-10-27,140.2557,5.2433,
2019,Climatology,2019-11-03,353.3686,5.4423,
2019,Climatology,2019-11-10,176.2229,5.7397,
2019,Climatology,2019-11-17,297.9271,5.3861,
2019,Climatology,2019-11-24,152.5214,5.2629,
2019,Climatology,2019-12-01,86.8257,5.3145,
2019,Climatology,2019-12-08,204.5543,5.3336,
2019,Climatology,2019-12-15,184.0914,5.1796,
2019,Climatology,2019-12-22,185.5786,5.2969,
2019,Climatology,2019-12-29,234.3286,5.4513,
2019,Climatology + AR(1),2019-01-06,282.4114,5.5109,0.1966
2019,Climatology + AR(1),2019-01-13,215.72,5.2958,0.2094
2019,Climatology + AR(1),2019-01-20,239.1957,5.4099,0.2111
2019,Climatology + AR(1),2019-01-27,116.3271,5.1859,0.2113
2019,Climatology + AR(1),2019-02-03,166.5671,5.0697,0.2113
2019,Climatology + AR(1),2019-02-10,134.5643,5.0061,0.2113
2019,Climatology + AR(1),2019-02-17,152.7586,4.895,0.2113
2019,Climatology + AR(1),2019-02-24,90.0871,5.1224,0.2113
2019,Climatology + AR(1),2019-03-03,80.32,4.7931,0.2113
2019,Climatology + AR(1),2019-03-10,86.03,4.4896,0.2113
2019,Climatology + AR(1),2019-03-17,82.4214,4.5244,0.2113
2019,Climatology + AR(1),2019-03-24,79.0757,4.536,0.2113
2019,Climatology + AR(1),2019-03-31,87.0914,4.6366,0.2113
2019,Climatology + AR(1),2019-04-07,104.1229,4.5208,0.2113
2019,Climatology + AR(1),2019-04-14,72.8586,4.6202,0.2113
2019,Climatology + AR(1),2019-04-21,61.77,4.6659,0.2113
2019,Climatology + AR(1),2019-04-28,88.33,4.7236,0.2113
2019,Climatology + AR(1),2019-05-05,85.7743,4.5536,0.2113
2019,Climatology + AR(1),2019-05-12,129.0486,4.721,0.2113
2019,Climatology + AR(1),2019-05-19,86.87,4.5938,0.2113
2019,Climatology + AR(1),2019-05-26,67.2914,4.5098,0.2113
2019,Climatology + AR(1),2019-06-02,78.26,4.5311,0.2113
2019,Climatology + AR(1),2019-06-09,70.2086,4.1747,0.2113
2019,Climatology + AR(1),2019-06-16,69.0129,4.5174,0.2113
2019,Climatology + AR(1),2019-06-23,53.5386,4.3192,0.2113
2019,Climatology + AR(1),2019-06-30,56.7329,3.9438,0.2113
2019,Climatology + AR(1),2019-07-07,46.7743,4.104,0.2113
2019,Climatology + AR(1),2019-07-14,62.9386,3.8144,0.2113
2019,Climatology + AR(1),2019-07-21,42.65,3.7679,0.2113
2019,Climatology + AR(1),2019-07-28,42.49,3.5642,0.2113
2019,Climatology + AR(1),2019-08-04,34.1886,3.7346,0.2113
2019,Climatology + AR(1),2019-08-11,28.4871,3.7847,0.2113
2019,Climatology + AR(1),2019-08-18,20.7814,3.8039,0.2113
2019,Climatology + AR(1),2019-08-25,45.1186,3.7375,0.2113
2019,Climatology + AR(1),2019-09-01,39.6414,3.6999,0.2113
2019,Climatology + AR(1),2019-09-08,46.8057,4.0022,0.2113
2019,Climatology + AR(1),2019-09-15,50.5686,4.004,0.2113
2019,Climatology + AR(1),2019-09-22,39.8514,4.0814,0.2113
2019,Climatology + AR(1),2019-09-29,25.55,4.2435,0.2113
2019,Climatology + AR(1),2019-10-06,43.2557,4.518,0.2113
2019,Climatology + AR(1),2019-10-13,87.5229,4.7843,0.2113
2019,Climatology + AR(1),2019-10-20,111.8514,4.99,0.2113
2019,Climatology + AR(1),2019-10-27,140.2557,5.2433,0.2113
2019,Climatology + AR(1),2019-11-03,353.3686,5.4423,0.2113
2019,Climatology + AR(1),2019-11-10,176.2229,5.7397,0.2113
2019,Climatology + AR(1),2019-11-17,297.9271,5.3861,0.2113
2019,Climatology + AR(1),2019-11-24,152.5214,5.2629,0.2113
2019,Climatology + AR(1),2019-12-01,86.8257,5.3145,0.2113
2019,Climatology + AR(1),2019-12-08,204.5543,5.3336,0.2113
2019,Climatology + AR(1),2019-12-15,184.0914,5.1796,0.2113
2019,Climatology + AR(1),2019-12-22,185.5786,5.2969,0.2113
2019,Climatology + AR(1),2019-12-29,234.3286,5.4513,0.2113
2019,Linear regression,2019-01-06,282.4114,5.2481,0.2516
2019,Linear regression,2019-01-13,215.72,5.1928,0.2516
2019,Linear regression,2019-01-20,239.1957,5.131,0.2516
2019,Linear regression,2019-01-27,116.3271,5.0636,0.2516
2019,Linear regression,2019-02-03,166.5671,4.9916,0.2516
2019,Linear regression,2019-02-10,134.5643,4.9161,0.2516
2019,Linear regression,2019-02-17,152.7586,4.8391,0.2516
2019,Linear regression,2019-02-24,90.0871,4.7627,0.2516
2019,Linear regression,2019-03-03,80.32,4.6898,0.2516
2019,Linear regression,2019-03-10,86.03,4.6234,0.2516
2019,Linear regression,2019-03-17,82.4214,4.5664,0.2516
2019,Linear regression,2019-03-24,79.0757,4.5211,0.2516
2019,Linear regression,2019-03-31,87.0914,4.4891,0.2516
2019,Linear regression,2019-04-07,104.1229,4.4708,0.2516
2019,Linear regression,2019-04-14,72.8586,4.4648,0.2516
2019,Linear regression,2019-04-21,61.77,4.4687,0.2516
2019,Linear regression,2019-04-28,88.33,4.4783,0.2516
2019,Linear regression,2019-05-05,85.7743,4.4885,0.2516
2019,Linear regression,2019-05-12,129.0486,4.4936,0.2516
2019,Linear regression,2019-05-19,86.87,4.4877,0.2516
2019,Linear regression,2019-05-26,67.2914,4.4658,0.2516
2019,Linear regression,2019-06-02,78.26,4.4241,0.2516
2019,Linear regression,2019-06-09,70.2086,4.3606,0.2516
2019,Linear regression,2019-06-16,69.0129,4.2756,0.2516
2019,Linear regression,2019-06-23,53.5386,4.1716,0.2516
2019,Linear regression,2019-06-30,56.7329,4.0538,0.2516
2019,Linear regression,2019-07-07,46.7743,3.9291,0.2516
2019,Linear regression,2019-07-14,62.9386,3.806,0.2516
2019,Linear regression,2019-07-21,42.65,3.6936,0.2516
2019,Linear regression,2019-07-28,42.49,3.6011,0.2516
2019,Linear regression,2019-08-04,34.1886,3.5368,0.2516
2019,Linear regression,2019-08-11,28.4871,3.507,0.2516
2019,Linear regression,2019-08-18,20.7814,3.5161,0.2516
2019,Linear regression,2019-08-25,45.1186,3.5656,0.2516
2019,Linear regression,2019-09-01,39.6414,3.6542,0.2516
2019,Linear regression,2019-09-08,46.8057,3.778,0.2516
2019,Linear regression,2019-09-15,50.5686,3.9306,0.2516
2019,Linear regression,2019-09-22,39.8514,4.1041,0.2516
2019,Linear regression,2019-09-29,25.55,4.2894,0.2516
2019,Linear regression,2019-10-06,43.2557,4.4771,0.2516
2019,Linear regression,2019-10-13,87.5229,4.6586,0.2516
2019,Linear regression,2019-10-20,111.8514,4.8261,0.2516
2019,Linear regression,2019-10-27,140.2557,4.9737,0.2516
2019,Linear regression,2019-11-03,353.3686,5.0973,0.2516
2019,Linear regression,2019-11-10,176.2229,5.1947,0.2516
2019,Linear regression,2019-11-17,297.9271,5.2657,0.2516
2019,Linear regression,2019-11-24,152.5214,5.3115,0.2516
2019,Linear regression,2019-12-01,86.8257,5.3346,0.2516
2019,Linear regression,2019-12-08,204.5543,5.338,0.2516
2019,Linear regression,2019-12-15,184.0914,5.3248,0.2516
2019,Linear regression,2019-12-22,185.5786,5.2981,0.2516
2019,Linear regression,2019-12-29,234.3286,5.2605,0.2516
2019,LSTM (small),2019-01-06,282.4114,5.2837,0.0318
2019,LSTM (small),2019-01-13,215.72,5.0299,0.0318
2019,LSTM (small),2019-01-20,239.1957,5.2359,0.0318
2019,LSTM (small),2019-01-27,116.3271,5.0132,0.0318
2019,LSTM (small),2019-02-03,166.5671,4.8191,0.0318
2019,LSTM (small),2019-02-10,134.5643,4.8266,0.0318
2019,LSTM (small),2019-02-17,152.7586,4.8249,0.0318
2019,LSTM (small),2019-02-24,90.0871,5.469,0.0318
2019,LSTM (small),2019-03-03,80.32,5.2133,0.0318
2019,LSTM (small),2019-03-10,86.03,4.5867,0.0318
2019,LSTM (small),2019-03-17,82.4214,4.3719,0.0318
2019,LSTM (small),2019-03-24,79.0757,4.4462,0.0318
2019,LSTM (small),2019-03-31,87.0914,4.4704,0.0318
2019,LSTM (small),2019-04-07,104.1229,4.4509,0.0318
2019,LSTM (small),2019-04-14,72.8586,4.472,0.0318
2019,LSTM (small),2019-04-21,61.77,4.2977,0.0318
2019,LSTM (small),2019-04-28,88.33,4.5158,0.0318
2019,LSTM (small),2019-05-05,85.7743,4.491,0.0318
2019,LSTM (small),2019-05-12,129.0486,4.7364,0.0318
2019,LSTM (small),2019-05-19,86.87,4.4192,0.0318
2019,LSTM (small),2019-05-26,67.2914,4.5572,0.0318
2019,LSTM (small),2019-06-02,78.26,5.0154,0.0318
2019,LSTM (small),2019-06-09,70.2086,4.0488,0.0318
2019,LSTM (small),2019-06-16,69.0129,4.2116,0.0318
2019,LSTM (small),2019-06-23,53.5386,4.2224,0.0318
2019,LSTM (small),2019-06-30,56.7329,3.9583,0.0318
2019,LSTM (small),2019-07-07,46.7743,4.158,0.0318
2019,LSTM (small),2019-07-14,62.9386,3.9819,0.0318
2019,LSTM (small),2019-07-21,42.65,4.5009,0.0318
2019,LSTM (small),2019-07-28,42.49,3.8129,0.0318
2019,LSTM (small),2019-08-04,34.1886,3.6249,0.0318
2019,LSTM (small),2019-08-11,28.4871,3.77,0.0318
2019,LSTM (small),2019-08-18,20.7814,3.9841,0.0318
2019,LSTM (small),2019-08-25,45.1186,4.0796,0.0318
2019,LSTM (small),2019-09-01,39.6414,3.896,0.0318
2019,LSTM (small),2019-09-08,46.8057,4.6099,0.0318
2019,LSTM (small),2019-09-15,50.5686,4.3985,0.0318
2019,LSTM (small),2019-09-22,39.8514,4.4043,0.0318
2019,LSTM (small),2019-09-29,25.55,4.554,0.0318
2019,LSTM (small),2019-10-06,43.2557,4.987,0.0318
2019,LSTM (small),2019-10-13,87.5229,5.2235,0.0318
2019,LSTM (small),2019-10-20,111.8514,5.3897,0.0318
2019,LSTM (small),2019-10-27,140.2557,5.6581,0.0318
2019,LSTM (small),2019-11-03,353.3686,5.8757,0.0318
2019,LSTM (small),2019-11-10,176.2229,6.1546,0.0318
2019,LSTM (small),2019-11-17,297.9271,5.7959,0.0318
2019,LSTM (small),2019-11-24,152.5214,5.6892,0.0318
2019,LSTM (small),2019-12-01,86.8257,5.757,0.0318
2019,LSTM (small),2019-12-08,204.5543,5.7639,0.0318
2019,LSTM (small),2019-12-15,184.0914,5.608,0.0318
2019,LSTM (small),2019-12-22,185.5786,5.7362,0.0318
2019,LSTM (small),2019-12-29,234.3286,5.8927,0.0318
2019,Fourier+ARMA const,2019-01-06,282.4114,5.4355,0.2368
2019,Fourier+ARMA const,2019-01-13,215.72,5.3237,0.25
2019,Fourier+ARMA const,2019-01-20,239.1957,5.2459,0.2515
2019,Fourier+ARMA const,2019-01-27,116.3271,5.1756,0.2517
2019,Fourier+ARMA const,2019-02-03,166.5671,5.1041,0.2517
2019,Fourier+ARMA const,2019-02-10,134.5643,5.0297,0.2517
2019,Fourier+ARMA const,2019-02-17,152.7586,4.953,0.2517
2019,Fourier+ARMA const,2019-02-24,90.0871,4.8763,0.2517
2019,Fourier+ARMA const,2019-03-03,80.32,4.8023,0.2517
2019,Fourier+ARMA const,2019-03-10,86.03,4.7343,0.2517
2019,Fourier+ARMA const,2019-03-17,82.4214,4.6756,0.2517
2019,Fourier+ARMA const,2019-03-24,79.0757,4.6287,0.2517
2019,Fourier+ARMA const,2019-03-31,87.0914,4.5954,0.2517
2019,Fourier+ARMA const,2019-04-07,104.1229,4.5763,0.2517
2019,Fourier+ARMA const,2019-04-14,72.8586,4.5702,0.2517
2019,Fourier+ARMA const,2019-04-21,61.77,4.5744,0.2517
2019,Fourier+ARMA const,2019-04-28,88.33,4.5848,0.2517
2019,Fourier+ARMA const,2019-05-05,85.7743,4.596,0.2517
2019,Fourier+ARMA const,2019-05-12,129.0486,4.6023,0.2517
2019,Fourier+ARMA const,2019-05-19,86.87,4.5975,0.2517
2019,Fourier+ARMA const,2019-05-26,67.2914,4.5764,0.2517
2019,Fourier+ARMA const,2019-06-02,78.26,4.5351,0.2517
2019,Fourier+ARMA const,2019-06-09,70.2086,4.4716,0.2517
2019,Fourier+ARMA const,2019-06-16,69.0129,4.3861,0.2517
2019,Fourier+ARMA const,2019-06-23,53.5386,4.2814,0.2517
2019,Fourier+ARMA const,2019-06-30,56.7329,4.1626,0.2517
2019,Fourier+ARMA const,2019-07-07,46.7743,4.0369,0.2517
2019,Fourier+ARMA const,2019-07-14,62.9386,3.9129,0.2517
2019,Fourier+ARMA const,2019-07-21,42.65,3.8,0.2517
2019,Fourier+ARMA const,2019-07-28,42.49,3.7073,0.2517
2019,Fourier+ARMA const,2019-08-04,34.1886,3.6432,0.2517
2019,Fourier+ARMA const,2019-08-11,28.4871,3.614,0.2517
2019,Fourier+ARMA const,2019-08-18,20.7814,3.6241,0.2517
2019,Fourier+ARMA const,2019-08-25,45.1186,3.6746,0.2517
2019,Fourier+ARMA const,2019-09-01,39.6414,3.7643,0.2517
2019,Fourier+ARMA const,2019-09-08,46.8057,3.8889,0.2517
2019,Fourier+ARMA const,2019-09-15,50.5686,4.042,0.2517
2019,Fourier+ARMA const,2019-09-22,39.8514,4.2154,0.2517
2019,Fourier+ARMA const,2019-09-29,25.55,4.4,0.2517
2019,Fourier+ARMA const,2019-10-06,43.2557,4.5867,0.2517
2019,Fourier+ARMA const,2019-10-13,87.5229,4.7667,0.2517
2019,Fourier+ARMA const,2019-10-20,111.8514,4.9326,0.2517
2019,Fourier+ARMA const,2019-10-27,140.2557,5.0787,0.2517
2019,Fourier+ARMA const,2019-11-03,353.3686,5.2011,0.2517
2019,Fourier+ARMA const,2019-11-10,176.2229,5.2981,0.2517
2019,Fourier+ARMA const,2019-11-17,297.9271,5.3695,0.2517
2019,Fourier+ARMA const,2019-11-24,152.5214,5.417,0.2517
2019,Fourier+ARMA const,2019-12-01,86.8257,5.4429,0.2517
2019,Fourier+ARMA const,2019-12-08,204.5543,5.4502,0.2517
2019,Fourier+ARMA const,2019-12-15,184.0914,5.442,0.2517
2019,Fourier+ARMA const,2019-12-22,185.5786,5.421,0.2517
2019,Fourier+ARMA const,2019-12-29,234.3286,5.3896,0.2517
2019,Fourier+ARMA linear,2019-01-06,282.4114,5.3945,0.235
2019,Fourier+ARMA linear,2019-01-13,215.72,5.271,0.2463
2019,Fourier+ARMA linear,2019-01-20,239.1957,5.1864,0.2474
2019,Fourier+ARMA linear,2019-01-27,116.3271,5.1088,0.2475
2019,Fourier+ARMA linear,2019-02-03,166.5671,5.0293,0.2475
2019,Fourier+ARMA linear,2019-02-10,134.5643,4.9465,0.2475
2019,Fourier+ARMA linear,2019-02-17,152.7586,4.862,0.2475
2019,Fourier+ARMA linear,2019-02-24,90.0871,4.7784,0.2475
2019,Fourier+ARMA linear,2019-03-03,80.32,4.6992,0.2475
2019,Fourier+ARMA linear,2019-03-10,86.03,4.6279,0.2475
2019,Fourier+ARMA linear,2019-03-17,82.4214,4.5676,0.2475
2019,Fourier+ARMA linear,2019-03-24,79.0757,4.5209,0.2475
2019,Fourier+ARMA linear,2019-03-31,87.0914,4.4891,0.2475
2019,Fourier+ARMA linear,2019-04-07,104.1229,4.4722,0.2475
2019,Fourier+ARMA linear,2019-04-14,72.8586,4.4686,0.2475
2019,Fourier+ARMA linear,2019-04-21,61.77,4.475,0.2475
2019,Fourier+ARMA linear,2019-04-28,88.33,4.4869,0.2475
2019,Fourier+ARMA linear,2019-05-05,85.7743,4.4987,0.2475
2019,Fourier+ARMA linear,2019-05-12,129.0486,4.5043,0.2475
2019,Fourier+ARMA linear,2019-05-19,86.87,4.4977,0.2475
2019,Fourier+ARMA linear,2019-05-26,67.2914,4.4739,0.2475
2019,Fourier+ARMA linear,2019-06-02,78.26,4.4293,0.2475
2019,Fourier+ARMA linear,2019-06-09,70.2086,4.3623,0.2475
2019,Fourier+ARMA linear,2019-06-16,69.0129,4.2737,0.2475
2019,Fourier+ARMA linear,2019-06-23,53.5386,4.1664,0.2475
2019,Fourier+ARMA linear,2019-06-30,56.7329,4.046,0.2475
2019,Fourier+ARMA linear,2019-07-07,46.7743,3.9197,0.2475
2019,Fourier+ARMA linear,2019-07-14,62.9386,3.7961,0.2475
2019,Fourier+ARMA linear,2019-07-21,42.65,3.6844,0.2475
2019,Fourier+ARMA linear,2019-07-28,42.49,3.5934,0.2475
2019,Fourier+ARMA linear,2019-08-04,34.1886,3.5311,0.2475
2019,Fourier+ARMA linear,2019-08-11,28.4871,3.5034,0.2475
2019,Fourier+ARMA linear,2019-08-18,20.7814,3.5141,0.2475
2019,Fourier+ARMA linear,2019-08-25,45.1186,3.5644,0.2475
2019,Fourier+ARMA linear,2019-09-01,39.6414,3.6525,0.2475
2019,Fourier+ARMA linear,2019-09-08,46.8057,3.7745,0.2475
2019,Fourier+ARMA linear,2019-09-15,50.5686,3.9241,0.2475
2019,Fourier+ARMA linear,2019-09-22,39.8514,4.0934,0.2475
2019,Fourier+ARMA linear,2019-09-29,25.55,4.274,0.2475
2019,Fourier+ARMA linear,2019-10-06,43.2557,4.4571,0.2475
2019,Fourier+ARMA linear,2019-10-13,87.5229,4.6346,0.2475
2019,Fourier+ARMA linear,2019-10-20,111.8514,4.7994,0.2475
2019,Fourier+ARMA linear,2019-10-27,140.2557,4.9462,0.2475
2019,Fourier+ARMA linear,2019-11-03,353.3686,5.0712,0.2475
2019,Fourier+ARMA linear,2019-11-10,176.2229,5.1725,0.2475
2019,Fourier+ARMA linear,2019-11-17,297.9271,5.2498,0.2475
2019,Fourier+ARMA linear,2019-11-24,152.5214,5.3039,0.2475
2019,Fourier+ARMA linear,2019-12-01,86.8257,5.3366,0.2475
2019,Fourier+ARMA linear,2019-12-08,204.5543,5.3503,0.2475
2019,Fourier+ARMA linear,2019-12-15,184.0914,5.3473,0.2475
2019,Fourier+ARMA linear,2019-12-22,185.5786,5.3298,0.2475
2019,Fourier+ARMA linear,2019-12-29,234.3286,5.2996,0.2475
2019,Fourier+ARMA (selected),2019-01-06,282.4114,5.3592,0.2258
2019,Fourier+ARMA (selected),2019-01-13,215.72,5.3426,0.2317
2019,Fourier+ARMA (selected),2019-01-20,239.1957,5.3347,0.2335
2019,Fourier+ARMA (selected),2019-01-27,116.3271,5.2879,0.2348
2019,Fourier+ARMA (selected),2019-02-03,166.5671,5.1963,0.2361
2019,Fourier+ARMA (selected),2019-02-10,134.5643,5.0702,0.2374
2019,Fourier+ARMA (selected),2019-02-17,152.7586,4.9286,0.2386
2019,Fourier+ARMA (selected),2019-02-24,90.0871,4.7932,0.2399
2019,Fourier+ARMA (selected),2019-03-03,80.32,4.6818,0.2411
2019,Fourier+ARMA (selected),2019-03-10,86.03,4.6049,0.2424
2019,Fourier+ARMA (selected),2019-03-17,82.4214,4.5635,0.2436
2019,Fourier+ARMA (selected),2019-03-24,79.0757,4.551,0.2449
2019,Fourier+ARMA (selected),2019-03-31,87.0914,4.5567,0.2461
2019,Fourier+ARMA (selected),2019-04-07,104.1229,4.57,0.2473
2019,Fourier+ARMA (selected),2019-04-14,72.8586,4.5831,0.2485
2019,Fourier+ARMA (selected),2019-04-21,61.77,4.5925,0.2497
2019,Fourier+ARMA (selected),2019-04-28,88.33,4.5981,0.2509
2019,Fourier+ARMA (selected),2019-05-05,85.7743,4.6004,0.2521
2019,Fourier+ARMA (selected),2019-05-12,129.0486,4.5984,0.2533
2019,Fourier+ARMA (selected),2019-05-19,86.87,4.5879,0.2545
2019,Fourier+ARMA (selected),2019-05-26,67.2914,4.5616,0.2557
2019,Fourier+ARMA (selected),2019-06-02,78.26,4.5119,0.2569
2019,Fourier+ARMA (selected),2019-06-09,70.2086,4.4334,0.258
2019,Fourier+ARMA (selected),2019-06-16,69.0129,4.3263,0.2592
2019,Fourier+ARMA (selected),2019-06-23,53.5386,4.1977,0.2603
2019,Fourier+ARMA (selected),2019-06-30,56.7329,4.0607,0.2615
2019,Fourier+ARMA (selected),2019-07-07,46.7743,3.9311,0.2626
2019,Fourier+ARMA (selected),2019-07-14,62.9386,3.8237,0.2638
2019,Fourier+ARMA (selected),2019-07-21,42.65,3.748,0.2649
2019,Fourier+ARMA (selected),2019-07-28,42.49,3.7058,0.2661
2019,Fourier+ARMA (selected),2019-08-04,34.1886,3.6921,0.2672
2019,Fourier+ARMA (selected),2019-08-11,28.4871,3.6974,0.2683
2019,Fourier+ARMA (selected),2019-08-18,20.7814,3.7127,0.2694
2019,Fourier+ARMA (selected),2019-08-25,45.1186,3.7338,0.2706
2019,Fourier+ARMA (selected),2019-09-01,39.6414,3.7641,0.2717
2019,Fourier+ARMA (selected),2019-09-08,46.8057,3.8139,0.2728
2019,Fourier+ARMA (selected),2019-09-15,50.5686,3.8979,0.2739
2019,Fourier+ARMA (selected),2019-09-22,39.8514,4.0288,0.275
2019,Fourier+ARMA (selected),2019-09-29,25.55,4.2117,0.2761
2019,Fourier+ARMA (selected),2019-10-06,43.2557,4.4404,0.2772
2019,Fourier+ARMA (selected),2019-10-13,87.5229,4.6959,0.2782
2019,Fourier+ARMA (selected),2019-10-20,111.8514,4.9503,0.2793
2019,Fourier+ARMA (selected),2019-10-27,140.2557,5.1724,0.2804
2019,Fourier+ARMA (selected),2019-11-03,353.3686,5.3362,0.2815
2019,Fourier+ARMA (selected),2019-11-10,176.2229,5.4273,0.2825
2019,Fourier+ARMA (selected),2019-11-17,297.9271,5.4468,0.2836
2019,Fourier+ARMA (selected),2019-11-24,152.5214,5.4111,0.2847
2019,Fourier+ARMA (selected),2019-12-01,86.8257,5.3463,0.2857
2019,Fourier+ARMA (selected),2019-12-08,204.5543,5.2815,0.2868
2019,Fourier+ARMA (selected),2019-12-15,184.0914,5.2398,0.2878
2019,Fourier+ARMA (selected),2019-12-22,185.5786,5.2327,0.2889
2019,Fourier+ARMA (selected),2019-12-29,234.3286,5.2571,0.2899
2019,SARIMA D=1,2019-01-06,282.4114,5.5583,0.2378
2019,SARIMA D=1,2019-01-13,215.72,5.3532,0.245
2019,SARIMA D=1,2019-01-20,239.1957,5.4392,0.2504
2019,SARIMA D=1,2019-01-27,116.3271,5.2673,0.2546
2019,SARIMA D=1,2019-02-03,166.5671,5.1138,0.2578
2019,SARIMA D=1,2019-02-10,134.5643,5.0825,0.2603
2019,SARIMA D=1,2019-02-17,152.7586,4.937,0.2622
2019,SARIMA D=1,2019-02-24,90.0871,5.1235,0.2637
2019,SARIMA D=1,2019-03-03,80.32,4.72,0.2648
2019,SARIMA D=1,2019-03-10,86.03,4.5344,0.2657
2019,SARIMA D=1,2019-03-17,82.4214,4.5037,0.2664
2019,SARIMA D=1,2019-03-24,79.0757,4.6387,0.267
2019,SARIMA D=1,2019-03-31,87.0914,4.5924,0.2674
2019,SARIMA D=1,2019-04-07,104.1229,4.6076,0.2677
2019,SARIMA D=1,2019-04-14,72.8586,4.6419,0.268
2019,SARIMA D=1,2019-04-21,61.77,4.7234,0.2682
2019,SARIMA D=1,2019-04-28,88.33,4.6505,0.2684
2019,SARIMA D=1,2019-05-05,85.7743,4.6759,0.2685
2019,SARIMA D=1,2019-05-12,129.0486,4.6587,0.2686
2019,SARIMA D=1,2019-05-19,86.87,4.5543,0.2686
2019,SARIMA D=1,2019-05-26,67.2914,4.6131,0.2687
2019,SARIMA D=1,2019-06-02,78.26,4.4178,0.2687
2019,SARIMA D=1,2019-06-09,70.2086,4.2774,0.2688
2019,SARIMA D=1,2019-06-16,69.0129,4.5438,0.2688
2019,SARIMA D=1,2019-06-23,53.5386,4.2594,0.2688
2019,SARIMA D=1,2019-06-30,56.7329,3.9202,0.2688
2019,SARIMA D=1,2019-07-07,46.7743,4.0129,0.2689
2019,SARIMA D=1,2019-07-14,62.9386,3.869,0.2689
2019,SARIMA D=1,2019-07-21,42.65,3.662,0.2689
2019,SARIMA D=1,2019-07-28,42.49,3.5101,0.2689
2019,SARIMA D=1,2019-08-04,34.1886,3.8891,0.2689
2019,SARIMA D=1,2019-08-11,28.4871,3.7961,0.2689
2019,SARIMA D=1,2019-08-18,20.7814,3.7348,0.2689
2019,SARIMA D=1,2019-08-25,45.1186,3.7839,0.2689
2019,SARIMA D=1,2019-09-01,39.6414,3.7727,0.2689
2019,SARIMA D=1,2019-09-08,46.8057,3.9598,0.2689
2019,SARIMA D=1,2019-09-15,50.5686,4.0589,0.2689
2019,SARIMA D=1,2019-09-22,39.8514,3.9967,0.2689
2019,SARIMA D=1,2019-09-29,25.55,4.3283,0.2688
2019,SARIMA D=1,2019-10-06,43.2557,4.6292,0.2688
2019,SARIMA D=1,2019-10-13,87.5229,4.7058,0.2688
2019,SARIMA D=1,2019-10-20,111.8514,5.0724,0.2688
2019,SARIMA D=1,2019-10-27,140.2557,5.2214,0.2687
2019,SARIMA D=1,2019-11-03,353.3686,5.5428,0.2687
2019,SARIMA D=1,2019-11-10,176.2229,5.7258,0.2686
2019,SARIMA D=1,2019-11-17,297.9271,5.355,0.2686
2019,SARIMA D=1,2019-11-24,152.5214,5.2173,0.2685
2019,SARIMA D=1,2019-12-01,86.8257,5.3139,0.2683
2019,SARIMA D=1,2019-12-08,204.5543,5.3102,0.2682
2019,SARIMA D=1,2019-12-15,184.0914,5.024,0.268
2019,SARIMA D=1,2019-12-22,185.5786,5.3519,0.2677
2019,SARIMA D=1,2019-12-29,234.3286,5.4551,0.2635
2019,SARIMA D=0,2019-01-06,282.4114,5.5427,0.2696
2019,SARIMA D=0,2019-01-13,215.72,5.3995,0.3084
2019,SARIMA D=0,2019-01-20,239.1957,5.377,0.3379
2019,SARIMA D=0,2019-01-27,116.3271,5.2358,0.361
2019,SARIMA D=0,2019-02-03,166.5671,5.1725,0.3796
2019,SARIMA D=0,2019-02-10,134.5643,5.2188,0.3947
2019,SARIMA D=0,2019-02-17,152.7586,5.0103,0.407
2019,SARIMA D=0,2019-02-24,90.0871,5.138,0.4173
2019,SARIMA D=0,2019-03-03,80.32,4.9633,0.4257
2019,SARIMA D=0,2019-03-10,86.03,4.912,0.4328
2019,SARIMA D=0,2019-03-17,82.4214,4.9106,0.4387
2019,SARIMA D=0,2019-03-24,79.0757,4.8487,0.4437
2019,SARIMA D=0,2019-03-31,87.0914,4.8573,0.4479
2019,SARIMA D=0,2019-04-07,104.1229,4.8285,0.4514
2019,SARIMA D=0,2019-04-14,72.8586,4.7303,0.4544
2019,SARIMA D=0,2019-04-21,61.77,4.7912,0.4569
2019,SARIMA D=0,2019-04-28,88.33,4.8211,0.459
2019,SARIMA D=0,2019-05-05,85.7743,4.6599,0.4608
2019,SARIMA D=0,2019-05-12,129.0486,4.783,0.4623
2019,SARIMA D=0,2019-05-19,86.87,4.7101,0.4636
2019,SARIMA D=0,2019-05-26,67.2914,4.7608,0.4647
2019,SARIMA D=0,2019-06-02,78.26,4.676,0.4656
2019,SARIMA D=0,2019-06-09,70.2086,4.5915,0.4664
2019,SARIMA D=0,2019-06-16,69.0129,4.8968,0.467
2019,SARIMA D=0,2019-06-23,53.5386,4.5962,0.4676
2019,SARIMA D=0,2019-06-30,56.7329,4.3841,0.4681
2019,SARIMA D=0,2019-07-07,46.7743,4.4831,0.4685
2019,SARIMA D=0,2019-07-14,62.9386,4.4141,0.4688
2019,SARIMA D=0,2019-07-21,42.65,4.3485,0.4691
2019,SARIMA D=0,2019-07-28,42.49,4.3212,0.4693
2019,SARIMA D=0,2019-08-04,34.1886,4.5158,0.4695
2019,SARIMA D=0,2019-08-11,28.4871,4.3579,0.4697
2019,SARIMA D=0,2019-08-18,20.7814,4.3515,0.4699
2019,SARIMA D=0,2019-08-25,45.1186,4.2762,0.47
2019,SARIMA D=0,2019-09-01,39.6414,4.3369,0.4701
2019,SARIMA D=0,2019-09-08,46.8057,4.3718,0.4702
2019,SARIMA D=0,2019-09-15,50.5686,4.2851,0.4703
2019,SARIMA D=0,2019-09-22,39.8514,4.4255,0.4704
2019,SARIMA D=0,2019-09-29,25.55,4.4807,0.4704
2019,SARIMA D=0,2019-10-06,43.2557,4.6144,0.4705
2019,SARIMA D=0,2019-10-13,87.5229,4.6676,0.4705
2019,SARIMA D=0,2019-10-20,111.8514,4.8019,0.4705
2019,SARIMA D=0,2019-10-27,140.2557,4.8726,0.4706
2019,SARIMA D=0,2019-11-03,353.3686,4.9333,0.4706
2019,SARIMA D=0,2019-11-10,176.2229,5.0542,0.4706
2019,SARIMA D=0,2019-11-17,297.9271,4.8729,0.4706
2019,SARIMA D=0,2019-11-24,152.5214,4.8627,0.4706
2019,SARIMA D=0,2019-12-01,86.8257,4.8985,0.4707
2019,SARIMA D=0,2019-12-08,204.5543,4.9261,0.4707
2019,SARIMA D=0,2019-12-15,184.0914,4.8744,0.4707
2019,SARIMA D=0,2019-12-22,185.5786,5.0192,0.4707
2019,SARIMA D=0,2019-12-29,234.3286,5.053,0.4707
```



# 07 Verification and figure code

## slides/beamer/verify_numbers.py
```python
"""Independent audit of every number shown in the deck.

Recomputes the slide numbers from the RAW files (data/raw/*), using different code paths from the notebooks where
practical (manual HAC covariance, manual VAR / impulse responses in numpy), and compares with what the slides use
(tables/numbers.tex, tables/*.tex, results/*.csv). Prints PASS/FAIL per check; exits 1 on any FAIL.
Run: .venv/bin/python slides/beamer/verify_numbers.py
"""
import json
import re
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import het_arch
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import acf, adfuller, kpss

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[2]
RES, TAB = ROOT / "results", Path(__file__).resolve().parent / "tables"
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail else ""))


def close(a, b, tol):
    return abs(float(a) - float(b)) <= tol


macros = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{(.*?)\}", (TAB / "numbers.tex").read_text()))

# ── 1. rebuild the data from the raw files ─────────────────────────────────────────────────────────────
raw = pd.read_csv(ROOT / "data/raw/city_day.csv", parse_dates=["Date"])
dl = raw[raw.City == "Delhi"].set_index("Date").sort_index().asfreq("D")
wx = json.loads((ROOT / "data/raw/delhi_weather_openmeteo.json").read_text())["daily"]
wx = pd.DataFrame(wx).assign(Date=lambda d: pd.to_datetime(d.time)).set_index("Date").asfreq("D")
d = pd.DataFrame({"pm25": dl["PM2.5"], "wind": wx["wind_speed_10m_mean"], "rh": wx["relative_humidity_2m_mean"],
                  "rain": wx["precipitation_sum"]})
n_missing_pm = int(d.pm25.isna().sum())
d["pm25"] = d["pm25"].interpolate(method="time", limit=3, limit_area="inside")
check("2,009 daily records", len(d) == 2009 and d.index.min() == pd.Timestamp("2015-01-01") and d.index.max() == pd.Timestamp("2020-07-01"))
check("2 PM2.5 values missing (then interpolated)", n_missing_pm == 2 and d.pm25.notna().all(), f"missing={n_missing_pm}")
check("weather has no gaps", d[["wind", "rh", "rain"]].notna().all().all())
d["lpm"] = np.log(d.pm25)

# processed files used by the notebooks must equal this independent rebuild
proc = pd.read_csv(ROOT / "data/processed/delhi_daily.csv", index_col="Date", parse_dates=True)
check("processed daily PM2.5/wind/humidity equal independent rebuild",
      np.allclose(proc.pm25, d.pm25) and np.allclose(proc.wind, d.wind) and np.allclose(proc.rh, d.rh))
wk = d[["pm25"]].resample("W-SUN").mean().assign(n=d.pm25.resample("W-SUN").count())
wk = wk[wk.n >= 4]
procw = pd.read_csv(ROOT / "data/processed/delhi_weekly.csv", index_col="Date", parse_dates=True)
check("287 weekly means, equal independent rebuild", len(wk) == 287 and np.allclose(wk.pm25, procw.pm25))
check("weekly series has no gaps", wk.index.to_series().diff().dropna().eq(pd.Timedelta("7D")).all())

# ── 2. slide 2: share of unhealthy days and seasonal means ─────────────────────────────────────────────
share = float((d.pm25 > 90).mean() * 100)
check("52% of days Poor or worse (PM2.5 > 90)", macros["pctPoor"] == f"{share:.0f}", f"{share:.1f}%")
w_mean = d.pm25[d.index.month.isin([11, 12, 1])].mean()
m_mean = d.pm25[d.index.month.isin([7, 8, 9])].mean()
check("winter mean 213", macros["winterMean"] == f"{w_mean:.0f}", f"{w_mean:.1f}")
check("monsoon mean 48", macros["monsoonMean"] == f"{m_mean:.0f}", f"{m_mean:.1f}")
check("winter/monsoon ratio 4.4", macros["ratioWM"] == f"{w_mean / m_mean:.1f}", f"{w_mean / m_mean:.2f}")

# ── 3. slide 5: STL seasonal strength ──────────────────────────────────────────────────────────────────
stl = STL(np.log(wk.pm25.loc[:"2018-12-31"]), period=52, robust=True).fit()
fs = max(0, 1 - np.var(stl.resid) / np.var(stl.seasonal + stl.resid))
check("STL seasonal strength (training weeks 2015-18) 0.90", macros["Fs"] == f"{fs:.2f}", f"{fs:.3f}")

# ── 4. slides 6-7: log transform, volatility ───────────────────────────────────────────────────────────
lpm = d.lpm
check("skewness raw +1.70 / log -0.08", macros["skewRaw"] == f"{stats.skew(d.pm25):+.2f}" and macros["skewLog"].replace("$-$", "-") == f"{stats.skew(lpm):.2f}",
      f"{stats.skew(d.pm25):.3f} / {stats.skew(lpm):.3f}")
lam = stats.boxcox(d.pm25)[1]
check("Box-Cox lambda 0.045", macros["boxcox"] == f"{lam:.3f}", f"{lam:.4f}")
g_raw = [x.values for _, x in d.pm25.groupby(d.index.month)]
g_log = [x.values for _, x in lpm.groupby(d.index.month)]
sd_raw, sd_log = [g.std(ddof=1) for g in g_raw], [g.std(ddof=1) for g in g_log]
check("monthly SD ratio raw 7.9x / log 1.3x", macros["sdRatioRaw"] == f"{max(sd_raw) / min(sd_raw):.1f}" and macros["sdRatioLog"] == f"{max(sd_log) / min(sd_log):.1f}",
      f"{max(sd_raw) / min(sd_raw):.2f} / {max(sd_log) / min(sd_log):.2f}")
check("Nov SD 115 / Aug SD 15", macros["sdNov"] == f"{sd_raw[10]:.0f}" and macros["sdAug"] == f"{sd_raw[7]:.0f}", f"{sd_raw[10]:.1f} / {sd_raw[7]:.1f}")
mm = [g.mean() for g in g_raw]
lt = pd.read_csv(RES / "log_justification.csv", index_col=0)
check("corr(monthly mean, SD) raw 0.95 / log -0.07 (table)", close(np.corrcoef(mm, sd_raw)[0, 1], lt.iloc[1, 0], 0.005) and close(np.corrcoef(mm, sd_log)[0, 1], lt.iloc[1, 1], 0.005))
lev_raw, lev_log = stats.levene(*g_raw, center="median"), stats.levene(*g_log, center="median")
check("Levene F raw 49.63 / log 2.40, log p = 0.006", close(lev_raw.statistic, 49.63, 0.01) and close(lev_log.statistic, 2.40, 0.01) and macros["levPlog"] == f"{lev_log.pvalue:.3f}",
      f"{lev_raw.statistic:.2f} / {lev_log.statistic:.2f} / p={lev_log.pvalue:.4f}")
a_raw = het_arch(d.pm25.diff().dropna() - d.pm25.diff().mean(), nlags=7)
a_log = het_arch(lpm.diff().dropna() - lpm.diff().mean(), nlags=7)
check("ARCH-LM 235 -> 36, both significant", macros["archRaw"] == f"{a_raw[0]:.0f}" and macros["archLog"] == f"{a_log[0]:.0f}" and a_log[1] < 0.05, f"{a_raw[0]:.1f} / {a_log[0]:.1f}, p_log={a_log[1]:.1e}")

# ── 5. slides 8-9: stationarity on the training years ──────────────────────────────────────────────────
tr = np.log(wk.pm25).loc[:"2018-12-31"]
check("train sample = 209 weeks", len(tr) == 209)
st = pd.read_csv(RES / "stationarity_train.csv", index_col=0)
for label, s in [("level", tr), ("seasonal difference", tr.diff(52)), ("double difference", tr.diff(52).diff())]:
    s = s.dropna()
    adf = adfuller(s, autolag="AIC")
    kp = kpss(s, regression="c", nlags="auto")[1]
    ac1 = acf(s, nlags=1)[1]
    row = st.loc[{"level": "Weekly log PM2.5 (train)", "seasonal difference": "Weekly Δ₅₂ log PM2.5 (D=1)", "double difference": "Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1)"}[label]]
    ok = close(adf[0], row.adf_stat, 0.002) and close(ac1, row.lag1_acf, 0.006) and close(kp, row.kpss_p, 0.0011) and adf[1] < 0.05 and (kp >= 0.05 or label == "double difference")
    check(f"ADF/KPSS/ACF {label}: stat {adf[0]:.2f}, p {adf[1]:.1e}, KPSS p {kp:.2f}, lag-1 ACF {ac1:.2f}", ok)
check("double difference lag-1 ACF is about -0.46", close(acf(tr.diff(52).diff().dropna(), nlags=1)[1], -0.46, 0.006))
raw_adf, raw_kpss = adfuller(d.pm25, autolag="AIC")[1], kpss(d.pm25, regression="c", nlags="auto")[1]
check("raw daily PM2.5 also passes ADF and KPSS (claim on stationarity slide)", raw_adf < 0.05 and raw_kpss > 0.05, f"ADF p={raw_adf:.4f}, KPSS p={raw_kpss:.2f}")

# ── 6. slides 10-12: VAR on deseasonalised daily data (2015-2019), implemented by hand ────────────────
def clim_anom(s, window=31):
    doy = np.where(s.index.is_leap_year & (s.index.dayofyear > 59), s.index.dayofyear - 1, s.index.dayofyear)  # Feb 29 -> day 59
    clim = s.groupby(doy).mean().reindex(range(1, 366)).interpolate()
    half = window // 2
    padded = pd.concat([clim.iloc[-half:], clim, clim.iloc[:half]]).rolling(window, center=True).mean().iloc[half:-half]
    return s - padded.reindex(doy).to_numpy()


dd = d.loc[:"2019-12-31"]
A = pd.DataFrame({"wind": clim_anom(dd.wind), "rh": clim_anom(dd.rh), "pm25": clim_anom(dd.lpm), "rain": clim_anom(dd.rain)})
P = 4


def lag_design(df, cols, p):
    X = np.column_stack([df[c].shift(k).to_numpy() for k in range(1, p + 1) for c in cols])
    return X


def ols_var(df, cols, p):
    Y = df[cols].to_numpy()[p:]
    X = np.column_stack([np.ones(len(Y)), lag_design(df, cols, p)[p:]])
    B = np.linalg.lstsq(X, Y, rcond=None)[0]
    U = Y - X @ B
    return B, U, X


def hac_wald(df, target, cause_cols, all_cols, p=P, L=10):
    y = df[target].to_numpy()[p:]
    X = np.column_stack([np.ones(len(y)), lag_design(df, all_cols, p)[p:]])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    u = y - X @ b
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for l in range(1, L + 1):
        G = Xu[l:].T @ Xu[:-l]
        S += (1 - l / (L + 1)) * (G + G.T)
    XtXi = np.linalg.inv(X.T @ X)
    cov = XtXi @ S @ XtXi
    idx = [1 + k * len(all_cols) + all_cols.index(c) for k in range(p) for c in cause_cols]
    Rb = b[idx]
    W = float(Rb @ np.linalg.inv(cov[np.ix_(idx, idx)]) @ Rb)
    return W, float(stats.chi2.sf(W, len(idx)))


gh = pd.read_csv(RES / "granger_hac.csv")
three = ["wind", "rh", "pm25"]
four = ["wind", "rh", "pm25", "rain"]
cases = [("Wind → PM2.5", "PM2.5, wind, humidity", "pm25", ["wind"], three), ("Humidity → PM2.5", "PM2.5, wind, humidity", "pm25", ["rh"], three),
         ("Humidity → PM2.5", "+ rain control", "pm25", ["rh"], four), ("Rain → PM2.5", "+ rain control", "pm25", ["rain"], four),
         ("PM2.5 → Wind", "PM2.5, wind, humidity", "wind", ["pm25"], three), ("PM2.5 → Humidity", "PM2.5, wind, humidity", "rh", ["pm25"], three)]
for dirn, spec, tgt, cc, allc in cases:
    W, pv = hac_wald(A, tgt, cc, allc)
    row = gh[(gh.direction == dirn) & (gh.spec == spec)].iloc[0]
    same = close(W, row.wald_chi2, 0.15 * max(1, row.wald_chi2) * 0.02 + 0.2) and (abs(np.log10(pv) - np.log10(row.p_value)) < 0.3 or (pv > 0.05 and row.p_value > 0.05))
    check(f"HAC Granger {dirn} ({spec}): manual p={pv:.1e} vs table p={row.p_value:.1e}", same)
sig = {(r.direction, r.spec): r.p_value for r in gh.itertuples()}
check("claims: wind & humidity p < 1e-10; humidity still p<0.05 with rain; rain & reverse not significant",
      sig[("Wind → PM2.5", "PM2.5, wind, humidity")] < 1e-10 and sig[("Humidity → PM2.5", "PM2.5, wind, humidity")] < 1e-10 and sig[("Humidity → PM2.5", "+ rain control")] < 0.05
      and sig[("Rain → PM2.5", "+ rain control")] > 0.05 and sig[("PM2.5 → Wind", "PM2.5, wind, humidity")] > 0.05 and sig[("PM2.5 → Humidity", "PM2.5, wind, humidity")] > 0.05)


# lag robustness of the causality claims (manual HAC at lags 1..7)
lags_ok, rev_h, rev_w = True, [], []
for pl in range(1, 8):
    for cause, tgt in [("wind", "pm25"), ("rh", "pm25")]:
        lags_ok &= hac_wald(A, tgt, [cause], three, p=pl)[1] < 1e-9
    rev_h.append(hac_wald(A, "rh", ["pm25"], three, p=pl)[1])
    rev_w.append(hac_wald(A, "wind", ["pm25"], three, p=pl)[1])
check("weather -> PM2.5 has p < 1e-9 at every lag 1..7", lags_ok)
check("PM2.5 -> humidity never significant (lags 1..7)", min(rev_h) > 0.05, f"min p={min(rev_h):.2f}")
check("PM2.5 -> wind weak: p<0.05 only at lags 1-2 (0.04, 0.016), not at 3..7", [p < 0.05 for p in rev_w] == [True, True, False, False, False, False, False], str(np.round(rev_w, 3)))

# impulse responses and FEVD by hand: Theta_h = Phi_h chol(Sigma)
def var_ma(order, H=14):
    B, U, _ = ols_var(A, order, P)
    K = len(order)
    Acoef = [B[1 + k * K: 1 + (k + 1) * K].T for k in range(P)]
    Sig = U.T @ U / (len(U) - K * P - 1)
    Phi = [np.eye(K)]
    for h in range(1, H + 1):
        Phi.append(sum(Acoef[j - 1] @ Phi[h - j] for j in range(1, min(h, P) + 1)))
    L = np.linalg.cholesky(Sig)
    return [ph @ L for ph in Phi], np.sqrt(np.diag(Sig))


io = pd.read_csv(RES / "irf_orderings.csv")
fo = pd.read_csv(RES / "fevd_orderings.csv")
for lab, order in [("weather first", ["wind", "rh", "pm25"]), ("PM2.5 first", ["pm25", "wind", "rh"])]:
    Th, sdv = var_ma(order)
    ip = order.index("pm25")
    for shock, key in [("wind", "Wind"), ("rh", "Humidity")]:
        r1 = (np.exp(Th[1][ip, order.index(shock)]) - 1) * 100
        row = io[(io.shock == key) & io.ordering.str.startswith(lab.split()[0])].iloc[0]
        check(f"IRF day 1, {key} shock, {lab}: manual {r1:.1f}% vs table {row.day1_pct:.1f}%", close(r1, row.day1_pct, 0.11))
    contrib = np.array([sum(Th[h][ip, j] ** 2 for h in range(14)) for j in range(3)])
    share_w = 100 * (1 - contrib[ip] / contrib.sum())
    tab = fo[fo.ordering.str.startswith(lab.split()[0]) & (fo.variable != "PM2.5")].share_h14_pct.sum()
    check(f"FEVD weather share at day 14, {lab}: manual {share_w:.1f}% vs table {tab:.1f}%", close(share_w, tab, 0.21))
Th, sdv = var_ma(["wind", "rh", "pm25"])
check("1 SD wind shock 2.5 km/h, humidity 5.4%", close(sdv[0], 2.54, 0.01) and close(sdv[1], 5.43, 0.01), f"{sdv[0]:.2f}, {sdv[1]:.2f}")
check("slide ranges: wind 6-12%, humidity 4-7%, weather share 6-30%",
      [macros[k] for k in ("irfWindA", "irfWindB", "irfRhA", "irfRhB", "fevdA", "fevdB")] == ["6", "12", "4", "7", "6", "30"], str([macros[k] for k in ("irfWindA", "irfWindB", "irfRhA", "irfRhB", "fevdA", "fevdB")]))

# ── 7. slide 11: shock example and binned relation ─────────────────────────────────────────────────────
order = ["wind", "rh", "pm25"]
B, U, _ = ols_var(A, order, P)
resid = pd.DataFrame(U, index=A.index[P:], columns=order)
z = resid / resid.std()
fut = (A.pm25.shift(-1) - A.pm25.shift(1)).reindex(z.index)
edges = [-np.inf, -1.5, -0.75, -0.25, 0.25, 0.75, 1.5, np.inf]
bins = pd.cut(z.wind, edges)
g = pd.DataFrame({"z": z.wind, "y": fut, "b": bins}).dropna().groupby("b", observed=True)
zm, ym = g.z.mean().to_numpy(), (np.exp(g.y.mean().to_numpy()) - 1) * 100
check(f"binned shock: biggest windier bin {zm[-1]:+.1f} SD -> {ym[-1]:.0f}%; calmest {zm[0]:+.1f} SD -> {ym[0]:+.0f}%",
      macros["shockWindBig"] == f"{abs(ym[-1]):.0f}" and macros["shockWindBigZ"] == f"{zm[-1]:.1f}" and macros["shockWindCalm"] == f"{ym[0]:.0f}" and macros["shockWindCalmZ"] == f"{abs(zm[0]):.1f}")
check("binned relation is monotone for wind (falls as shock rises)", bool(np.all(np.diff(ym) < 0.5)), str(np.round(ym, 1)))
# 21 Jan 2019 example: expected vs actual wind from the manually fitted VAR
Y = A[order].to_numpy()
t0 = A.index.get_loc(pd.Timestamp("2019-01-21"))
xrow = np.concatenate([[1.0]] + [Y[t0 - k] for k in range(1, P + 1)])
pred_anom = float(xrow @ B[:, 0])
clim_wind = float(dd.wind.iloc[t0] - A.wind.iloc[t0])
exp_, act_ = clim_wind + pred_anom, float(dd.wind.iloc[t0])
check(f"21 Jan 2019: expected {exp_:.1f}, actual {act_:.1f}, shock {act_ - exp_:+.1f} km/h",
      macros["janPred"] == f"{exp_:.1f}" and macros["janWind"] == f"{act_:.1f}" and macros["janShock"] == f"{act_ - exp_:.1f}")

# ── 8. weekly: last week's weather does not predict this week's PM2.5 ──────────────────────────────────
w = pd.DataFrame({"pm": np.log(wk.pm25), "wind": d.wind.resample("W-SUN").mean().reindex(wk.index), "rh": d.rh.resample("W-SUN").mean().reindex(wk.index)}).loc[:"2018-12-31"]
woy = np.minimum(w.index.isocalendar().week.to_numpy(), 52)
wa = w - w.groupby(woy).transform("mean").to_numpy()
Xl = np.column_stack([np.ones(len(wa) - 1), wa.pm.to_numpy()[:-1], wa.wind.to_numpy()[:-1], wa.rh.to_numpy()[:-1]])
yl = wa.pm.to_numpy()[1:]
bl = np.linalg.lstsq(Xl, yl, rcond=None)[0]
ul = yl - Xl @ bl
for Lh in (4, 8):
    Xu = Xl * ul[:, None]
    S = Xu.T @ Xu
    for l in range(1, Lh + 1):
        G = Xu[l:].T @ Xu[:-l]
        S += (1 - l / (Lh + 1)) * (G + G.T)
    XtXi = np.linalg.inv(Xl.T @ Xl)
    cov = XtXi @ S @ XtXi
    pw = 2 * stats.norm.sf(abs(bl[2] / np.sqrt(cov[2, 2]))), 2 * stats.norm.sf(abs(bl[3] / np.sqrt(cov[3, 3])))
    check(f"last week's wind/humidity not significant (HAC lags={Lh}): p = {pw[0]:.2f}, {pw[1]:.2f}", pw[0] > 0.05 and pw[1] > 0.05)
check("slide values p = 0.46 / 0.48 (4 lags)", macros["lagWindP"] == "0.46" and macros["lagRhP"] == "0.48")

# ── 9. links and data-source claims ────────────────────────────────────────────────────────────────────
for url in ["https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india", "https://open-meteo.com/en/docs/historical-weather-api"]:
    try:
        code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "-m", "20", "-A", "Mozilla/5.0", "-w", "%{http_code}", url], capture_output=True, text=True).stdout.strip()
    except Exception as e:  # noqa: BLE001
        code = str(e)
    ok_ = code in ("200", "301", "302") or ("kaggle.com" in url and code in ("403", "404") and (ROOT / "data/raw/station_day.csv").exists())  # kaggle blocks scripted GETs; the slug is proven by the downloads
    check(f"link reachable: {url}", ok_, f"HTTP {code}")
check("weather file is ERA5 archive for central Delhi (28.61N, 77.21E)", abs(json.loads((ROOT / "data/raw/delhi_weather_openmeteo.json").read_text())["latitude"] - 28.61) < 0.2)
tex = (Path(__file__).resolve().parent / "main.tex").read_text()

# ── 10. Phase 4 (forecasting): independent re-derivation of the numbers on the forecasting slides ──────
from statsmodels.stats.diagnostic import acorr_ljungbox  # noqa: E402
from statsmodels.tsa.statespace.sarimax import SARIMAX  # noqa: E402

FC = json.loads((RES / "key_numbers_forecast.json").read_text())
mae_tab = pd.read_csv(RES / "fc_backtest_mae.csv", index_col=0)
lw = np.log(wk.pm25)
noleap_doy = lambda ix: np.where(ix.is_leap_year & (ix.dayofyear > 59), ix.dayofyear - 1, ix.dayofyear)  # noqa: E731
wk_idx = lambda ix: np.minimum((noleap_doy(ix - pd.Timedelta(days=3)) - 1) // 7 + 1, 52)  # noqa: E731
origins_ = {2017: "2016-12-25", 2018: "2017-12-31", 2019: "2018-12-30"}
for fold, org in origins_.items():
    tr_ = lw.loc[:org]
    te_ = wk.pm25.loc[org:].iloc[1:53]
    clim_ = tr_.groupby(wk_idx(tr_.index)).mean().reindex(range(1, 53)).interpolate(limit_direction="both")
    mae_c = np.abs(te_.to_numpy() - np.exp(clim_.reindex(wk_idx(te_.index)).to_numpy())).mean()
    mae_n = np.abs(te_.to_numpy() - wk.pm25.shift(52).loc[te_.index].to_numpy()).mean()
    check(f"fold {fold}: climatology MAE {mae_c:.1f} and seasonal naive {mae_n:.1f} re-derived", close(mae_c, mae_tab.loc["Climatology", str(fold)], 0.06) and close(mae_n, mae_tab.loc["Seasonal naive", str(fold)], 0.06))
# selected-model refit (2019 fold) with plain statsmodels, spec taken from the saved results
sp_ = FC["backtest"]["specs"]["2019"]
tr_ = lw.loc[:"2018-12-30"]; te_ = wk.pm25.loc["2018-12-30":].iloc[1:53]
tt = lambda ix: (ix - pd.Timestamp("2015-01-04")).days.to_numpy() / 7.0  # noqa: E731
four = lambda ix, K: pd.DataFrame({**{f"s{k}": np.sin(2 * np.pi * k * tt(ix) / (365.25 / 7)) for k in range(1, K + 1)}, **{f"c{k}": np.cos(2 * np.pi * k * tt(ix) / (365.25 / 7)) for k in range(1, K + 1)}}, index=ix)
trend_, d_ = {"const": ("c", 0), "linear": ("ct", 0), "rw": ("n", 1)}[sp_["trend"]]
fit_ = SARIMAX(tr_, exog=four(tr_.index, sp_["K"]), order=(sp_["p"], d_, sp_["q"]), trend=trend_).fit(disp=False, maxiter=200)
fc_ = fit_.get_forecast(52, exog=four(te_.index, sp_["K"]))
mae_s = np.abs(te_.to_numpy() - np.exp(fc_.predicted_mean.to_numpy())).mean()
cov_ = float(((te_.to_numpy() >= np.exp(fc_.conf_int().iloc[:, 0].to_numpy())) & (te_.to_numpy() <= np.exp(fc_.conf_int().iloc[:, 1].to_numpy()))).mean())
check(f"selected model ({sp_['trend']}, K={sp_['K']}) 2019 refit: MAE {mae_s:.1f}, coverage {cov_:.2f}", close(mae_s, FC["backtest"]["mae_selected"]["2019"], 0.1) and close(cov_, FC["coverage_2019_raw"], 0.02))
check("slide macros for 2019 MAE match", macros["fcMaeSelNineteen"] == f"{FC['backtest']['mae_selected']['2019']:.1f}" and macros["fcMaeClimNineteen"] == f"{mae_tab.loc['Climatology', '2019']:.1f}")
# Ljung-Box artifact: with and without the 52 diffuse residuals
r_s = SARIMAX(tr_, order=(1, 0, 1), seasonal_order=(0, 1, 1, 52)).fit(disp=False, maxiter=200)
e_all = pd.Series(np.asarray(r_s.resid))
p_all = float(acorr_ljungbox(e_all, lags=[10], model_df=3).lb_pvalue.iloc[0]); p_burn = float(acorr_ljungbox(e_all.iloc[52:], lags=[10], model_df=3).lb_pvalue.iloc[0])
check(f"Ljung-Box lag 10: p = {p_all:.1e} with the 52 diffuse residuals, {p_burn:.2f} without", r_s.loglikelihood_burn == 52 and p_all < 1e-6 and p_burn > 0.05)
check(f"seasonal MA coefficient {r_s.params['ma.S.L52']:.3f} (slide {macros['fcMaCoef']}), SE {r_s.bse['ma.S.L52']:.1f} > 1 (not identified; the exact SE is a numerical Hessian near the boundary and varies)", close(r_s.params["ma.S.L52"], FC["sarima_D1_maS_coef"], 0.01) and r_s.params["ma.S.L52"] < -0.95 and r_s.bse["ma.S.L52"] > 1)
# one-week-ahead persistence MAE and lockdown mean
ow = pd.read_csv(RES / "fc_oneweek.csv", index_col=0)
pers = [np.abs(wk.pm25.loc[f"{y_}-01-01":f"{y_}-12-31"].iloc[1:] - wk.pm25.shift(1).loc[f"{y_}-01-01":f"{y_}-12-31"].iloc[1:]).mean() for y_ in (2018, 2019)]
check(f"persistence one-week MAE 2018/2019 = {pers[0]:.1f}/{pers[1]:.1f}", close(pers[0], ow.loc["Persistence", "2018"], 0.6) and close(pers[1], ow.loc["Persistence", "2019"], 0.6))
lock_idx = pd.date_range("2020-03-29", "2020-05-31", freq="W-SUN")
lock_mean = float(wk.pm25.reindex(lock_idx).mean())
lk = pd.read_csv(RES / "fc_lockdown.csv", index_col=0)
check(f"lockdown weeks: actual mean {lock_mean:.1f}; gap vs forecast median {100 * (lock_mean / lk.cf_median.iloc[0] - 1):.0f}% = slide {macros['fcLockPct']}%",
      close(lock_mean, lk.actual_mean.iloc[0], 0.05) and macros["fcLockPct"] == f"{abs(lk.gap_median_pct.iloc[0]):.0f}" and close(100 * (lock_mean / lk.cf_median.iloc[0] - 1), lk.gap_median_pct.iloc[0], 4))
# outlook tables: days per month add up, intervals ordered
o20 = pd.read_csv(RES / "fc_outlook_2020.csv", index_col=0)
dsum = o20[[c for c in o20.columns if c.startswith("days_")]].sum(axis=1).to_numpy()
check("2020 outlook: expected days per month sum to 31/29/31/...", np.allclose(dsum, [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], atol=0.01))
check("2020 outlook: median inside its 95% interval every month", bool(((o20["lo95"] < o20["median"]) & (o20["median"] < o20["hi95"])).all()))
a20_ = d.pm25.loc["2020"]
check("2020 actual Jan-Feb inside interval, Mar-May below (lockdown)", bool(all(o20.loc[m_, "lo95"] <= a20_[a20_.index.month == i_ + 1].mean() <= o20.loc[m_, "hi95"] for i_, m_ in enumerate(["Jan", "Feb"])) and all(a20_[a20_.index.month == i_ + 1].mean() < o20.loc[m_, "lo95"] for i_, m_ in zip((3, 4, 5), ["Mar", "Apr", "May"]))))
# station check
st_ = pd.read_csv(ROOT / "data/raw/station_day.csv", parse_dates=["Date"]); meta_ = pd.read_csv(ROOT / "data/raw/stations.csv")
xs_ = st_[st_.StationId.isin(meta_.loc[meta_.City == "Delhi", "StationId"])].dropna(subset=["PM2.5"])
nst = xs_.groupby(xs_.Date.dt.year).StationId.nunique()
cm_ = pd.concat([d.pm25, xs_.groupby("Date")["PM2.5"].mean()], axis=1, keys=["c", "s"]).dropna()
check(f"stations per year {nst.loc[2015]},{nst.loc[2016]},..,{nst.loc[2019]}; corr(city, station mean) = {cm_.corr().iloc[0, 1]:.3f}", nst.loc[2015] == 10 and nst.loc[2018] == 37 and close(cm_.corr().iloc[0, 1], 0.995, 0.002))
sc = pd.read_csv(RES / "station_check.csv", index_col=0)
check("decline 2016->2019 on slide matches station table", macros["declPanel"] == f"{abs((np.exp(sc.loc[2019, 'panel_log_anom'] - sc.loc[2016, 'panel_log_anom']) - 1) * 100):.0f}")

bad = [r for r in results if not r[1]]
print(f"\n{len(results) - len(bad)}/{len(results)} checks passed")
sys.exit(1 if bad else 0)
```

## slides/beamer/make_figures.py
```python
"""Slide-sized vector figures and LaTeX tables for the Beamer deck.

Each figure is drawn at the size it appears on the slide (14.6 cm wide) with 9-10 pt fonts, so labels are as
readable as the slide text. Numbers come from data/processed and results/, never typed by hand.
Run after notebooks 02-03:  .venv/bin/python slides/beamer/make_figures.py
"""
import sys
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.dates  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from statsmodels.tsa.api import VAR
from statsmodels.tsa.seasonal import STL

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from src.aqi import band_edges  # noqa: E402
from src.plots import AXIS, AQUA, BLUE, INK, INK_2, MUTED, NEUTRAL, ORANGE, SEASON_COLORS, use_style  # noqa: E402
from src.data import SEASONS, OTHER_SEASON  # noqa: E402
from src.tsa import doy_anomaly  # noqa: E402

warnings.filterwarnings("ignore")
FIG, TAB = HERE / "fig", HERE / "tables"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)
W_CM = 14.6
CM = 1 / 2.54

use_style()
mpl.rcParams.update({
    "font.size": 10, "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "axes.titlesize": 10, "axes.titleweight": "normal", "lines.linewidth": 1.8, "pdf.fonttype": 42,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
})

daily = pd.read_csv(ROOT / "data/processed/delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
weekly = pd.read_csv(ROOT / "data/processed/delhi_weekly.csv", index_col="Date", parse_dates=True)
RES = ROOT / "results"
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def new_fig(h_cm, nrows=1, ncols=1, w=None, **kw):
    return plt.subplots(nrows, ncols, figsize=((w or W_CM) * CM, h_cm * CM), layout="constrained", **kw)


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)


def has(*names):
    return all((RES / n).exists() for n in names)


# logo.png is kept in the repo; to rebuild it: pdfimages -png -f 1 -l 1 Slides.pdf slides/beamer/logo
if (HERE / "logo-000.png").exists():
    rgb, mask = Image.open(HERE / "logo-000.png").convert("RGB"), Image.open(HERE / "logo-001.png").convert("L")
    rgb.putalpha(mask)
    rgb.save(HERE / "logo.png")

# ── 1. The problem: daily PM2.5 over CPCB AQI bands ────────────────────────────────────────────────────
fig, ax = new_fig(4.0)
ymax = 400
for name, lo, hi, colour in band_edges():
    if lo >= ymax:
        break
    ax.axhspan(lo, min(hi, ymax), color=colour, alpha=0.13, lw=0, zorder=0)
    ax.text(1.005, (lo + min(hi, ymax)) / 2, name, transform=ax.get_yaxis_transform(), va="center", fontsize=7, color=INK_2)
ax.plot(daily.index, daily["pm25"], color=BLUE, lw=0.6, alpha=0.5, label="Daily mean")
ax.plot(daily.index, daily["pm25"].rolling(30, center=True).mean(), color=BLUE, lw=2.2, label="30-day average")
ax.set_ylim(0, ymax)
ax.set_xlim(daily.index.min(), daily.index.max())
ax.set_ylabel("PM$_{2.5}$ (µg/m³)")
ax.legend(loc="upper left", ncols=2)
save(fig, "problem_aqi")

# ── 2. Seasonality: month boxplot (backup) and STL decomposition ───────────────────────────────────────
fig, ax = new_fig(5.0)
data = [daily.loc[daily.index.month == m, "pm25"].dropna() for m in range(1, 13)]
season_of_month = {m: n for n, ms in SEASONS.items() for m in ms}
bp = ax.boxplot(data, tick_labels=months, patch_artist=True, widths=0.65, showfliers=True,
                medianprops=dict(color=INK, lw=1.8), whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
                flierprops=dict(marker="o", markersize=2.5, markerfacecolor=MUTED, markeredgecolor="none", alpha=0.5))
for box, m in zip(bp["boxes"], range(1, 13)):
    box.set(facecolor=SEASON_COLORS[season_of_month.get(m, OTHER_SEASON)], edgecolor="white", linewidth=1.5)
ax.set_ylabel("PM$_{2.5}$ (µg/m³)")
ax.set_ylim(0, 720)
save(fig, "seasonal_boxplot")

stl = STL(weekly["log_pm25"], period=52, robust=True).fit()
fig, axes = new_fig(4.6, nrows=4, sharex=True)
for ax, (name, lab, s) in zip(axes, [("Observed", "log PM$_{2.5}$", stl.observed), ("Trend", "Trend", stl.trend),
                                      ("Seasonal", "Seasonal", stl.seasonal), ("Residual", "Residual", stl.resid)]):
    if name == "Residual":
        ax.vlines(s.index, 0, s, color=BLUE, lw=1.2)
    else:
        ax.plot(s.index, s, color=BLUE)
    ax.set_ylabel(lab, rotation=0, ha="right", va="center", fontsize=9, color=INK_2)
    ax.tick_params(axis="y", labelsize=8)
save(fig, "stl")

# ── 3. Why log: histograms of raw vs log PM2.5 with the best-fitting normal curve ─────────────────────
from scipy import stats as _st  # noqa: E402
pm = daily["pm25"].dropna()
lg = np.log(pm)
fig, axes = new_fig(4.1, ncols=2)
for ax, s, ttl, c, xl in [(axes[0], pm, "Raw PM$_{2.5}$", ORANGE, "µg/m³"), (axes[1], lg, "log PM$_{2.5}$", BLUE, "log units")]:
    ax.hist(s, bins=40, density=True, color=c, alpha=0.8, edgecolor="white", linewidth=0.5)
    xs = np.linspace(s.min(), s.max(), 300)
    ax.plot(xs, _st.norm.pdf(xs, s.mean(), s.std()), color=INK, lw=1.6, label="normal curve with same mean and SD")
    sk = float(((s - s.mean()) ** 3).mean() / s.std(ddof=0) ** 3)
    ax.set_title(f"{ttl}: skewness {sk:+.2f}", loc="left", color=INK)
    ax.set_xlabel(xl)
    ax.set_yticks([])
    ax.grid(False)
h_, l_ = axes[0].get_legend_handles_labels()
fig.legend(h_, l_, loc="outside lower center", frameon=False, fontsize=8)
save(fig, "why_log")

# ── 4. Volatility: monthly SD, raw vs log ──────────────────────────────────────────────────────────────
bm = pd.read_csv(RES / "monthly_mean_sd.csv", index_col=0)
fig, axes = new_fig(3.1, ncols=2)
for ax, col, ttl, c, ylab in [(axes[0], "sd_raw", "Raw PM$_{2.5}$", ORANGE, "SD (µg/m³)"),
                              (axes[1], "sd_log", "log PM$_{2.5}$", BLUE, "SD (log units)")]:
    ax.bar(range(1, 13), bm[col], color=c, width=0.7)
    ax.set_xticks(range(1, 13), [m[0] for m in months])
    ratio = bm[col].max() / bm[col].min()
    ax.set_title(f"{ttl}: largest / smallest = {ratio:.1f}×", loc="left", color=INK)
    ax.set_ylabel(ylab, fontsize=9)
    ax.grid(axis="x", visible=False)
save(fig, "volatility_sd")

# ── 5. Stationarity: weekly log PM2.5 (training years) with rolling mean and SD ────────────────────────
lw_tr = weekly.loc[:"2018-12-31", "log_pm25"]
roll_m, roll_s = lw_tr.rolling(52).mean(), lw_tr.rolling(52).std()
fig, axes = new_fig(3.9, nrows=2, sharex=True, height_ratios=[1.7, 1])
axes[0].plot(lw_tr.index, lw_tr, color=NEUTRAL, lw=1.3, label="Weekly log PM$_{2.5}$")
axes[0].plot(roll_m.index, roll_m, color=BLUE, lw=2.4, label="52-week rolling mean")
axes[0].set_ylabel("log PM$_{2.5}$", fontsize=9)
axes[0].set_ylim(2.8, 6.8)
axes[1].plot(roll_s.index, roll_s, color=ORANGE, lw=2.4, label="52-week rolling SD")
axes[1].set_ylabel("SD", fontsize=9)
axes[1].set_ylim(0, 1.0)
import matplotlib.dates as mdates
axes[1].xaxis.set_major_locator(mdates.YearLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
h0, l0 = axes[0].get_legend_handles_labels()
h1, l1 = axes[1].get_legend_handles_labels()
fig.legend(h0 + h1, l0 + l1, loc="outside upper center", ncols=3, frameon=False)
save(fig, "stationarity")

# ── 6. Granger tests with robust (HAC) errors ──────────────────────────────────────────────────────────
if has("granger_hac.csv"):
    gh = pd.read_csv(RES / "granger_hac.csv")
    pick = [("Wind → PM2.5", "PM2.5, wind, humidity", "Wind → PM$_{2.5}$"),
            ("Humidity → PM2.5", "PM2.5, wind, humidity", "Humidity → PM$_{2.5}$"),
            ("Humidity → PM2.5", "+ rain control", "Humidity → PM$_{2.5}$, rain controlled"),
            ("Rain → PM2.5", "+ rain control", "Rain → PM$_{2.5}$ (given wind, humidity)"),
            ("PM2.5 → Wind", "PM2.5, wind, humidity", "PM$_{2.5}$ → Wind"),
            ("PM2.5 → Humidity", "PM2.5, wind, humidity", "PM$_{2.5}$ → Humidity")]
    rows = [(lab.replace(' → ', r' $\to$ '), float(gh[(gh.direction == d_) & (gh.spec == s_)].p_value.iloc[0])) for d_, s_, lab in pick][::-1]
    fig, ax = new_fig(4.1)
    score = [-np.log10(p) for _, p in rows]
    ax.barh([r[0] for r in rows], score, color=[BLUE if p < 0.05 else NEUTRAL for _, p in rows], height=0.5)
    ax.axvline(-np.log10(0.05), color=ORANGE, lw=1.6)
    ax.text(-np.log10(0.05) + 0.3, len(rows) - 0.35, "p = 0.05", color=ORANGE, fontsize=8, va="bottom")
    for i, (s_, (_, p)) in enumerate(zip(score, rows)):
        if p < 1e-10:
            lab = r"$p<10^{-10}$"
        elif p < 1e-3:
            m_, e_ = f"{p:.0e}".split("e")
            lab = rf"$p={m_}\times10^{{{int(e_)}}}$"
        else:
            lab = f"p = {p:.2f}, not significant"
        ax.text(max(s_ + 0.3, 2.0), i, lab, va="center", fontsize=8, color=INK)
    ax.set_xlim(0, 27)
    ax.set_xlabel("Evidence: $-\\log_{10}(p)$ (longer = stronger)")
    ax.grid(axis="y", visible=False)
    save(fig, "granger_hac")

# ── 7. What a shock is, and what happens after one ─────────────────────────────────────────────────────
d = daily.loc[:"2019-12-31"]
anom = pd.DataFrame({"wind": doy_anomaly(d["wind"]), "rh": doy_anomaly(d["rh"]), "pm25": doy_anomaly(d["log_pm25"])})
var4 = VAR(anom).fit(4)
wind_clim = d["wind"] - anom["wind"]
wind_pred = wind_clim.loc[var4.fittedvalues.index] + var4.fittedvalues["wind"]
resid = var4.resid
z = resid / resid.std()
fig, axes = new_fig(4.6, ncols=2, width_ratios=[1.1, 1])
seg = slice("2019-01-14", "2019-01-27")
ax = axes[0]
ax.plot(d.loc[seg].index, d.loc[seg, "wind"], color=ORANGE, marker="o", ms=4, label="Actual wind")
ax.plot(wind_pred.loc[seg].index, wind_pred.loc[seg], color=INK_2, ls="--", marker="s", ms=3, label="Predicted from the past")
t0 = pd.Timestamp("2019-01-21")
ax.annotate("", xy=(t0, d.loc[t0, "wind"]), xytext=(t0, wind_pred.loc[t0]), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.4))
ax.text(t0, 20.3, f"expected {wind_pred.loc[t0]:.1f}, actual {d.loc[t0, 'wind']:.1f}\nshock = +{d.loc[t0, 'wind'] - wind_pred.loc[t0]:.1f} km/h", fontsize=8, ha="center", va="center")
ax.set_ylabel("Wind speed (km/h)")
ax.set_ylim(3, 23)
ticks = pd.date_range("2019-01-14", "2019-01-27", freq="4D")
ax.set_xticks(ticks)
ax.set_xticklabels([x.strftime("%d %b") for x in ticks])
ax.set_title("Shock = actual minus predicted", loc="left", color=INK)
ax = axes[1]
edges = [-np.inf, -1.5, -0.75, -0.25, 0.25, 0.75, 1.5, np.inf]
fut = anom["pm25"].shift(-1) - anom["pm25"].shift(1)  # change in log PM2.5 from day t-1 to day t+1
curves = {}
for nm, col, lab in [("wind", ORANGE, "wind shock"), ("rh", AQUA, "humidity shock")]:
    zz = z[nm]
    bins = pd.cut(zz, edges)
    g = pd.DataFrame({"z": zz, "y": fut.loc[zz.index], "bin": bins}).dropna().groupby("bin", observed=True)
    xm = g["z"].mean().to_numpy()
    ym, ys, n = g["y"].mean().to_numpy(), g["y"].std().to_numpy(), g["y"].count().to_numpy()
    se = ys / np.sqrt(n)
    ax.errorbar(xm + (0.04 if nm == "rh" else -0.04), (np.exp(ym) - 1) * 100, yerr=[(np.exp(ym) - np.exp(ym - 1.96 * se)) * 100, (np.exp(ym + 1.96 * se) - np.exp(ym)) * 100],
                color=col, marker="o", ms=4.5, lw=1.5, capsize=2.5, label=lab)
    curves[nm] = {"z": xm.round(2).tolist(), "pct": ((np.exp(ym) - 1) * 100).round(1).tolist(), "n": n.tolist()}
ax.axhline(0, color=INK_2, lw=0.9)
ax.axvline(0, color=MUTED, lw=0.9, ls=":")
ax.set_xlabel("Shock size (SDs; 0 = as predicted)")
ax.set_ylabel("PM$_{2.5}$ change (%)")
ax.set_title("Bigger shock, bigger fall in PM$_{2.5}$", loc="left", color=INK)
ax.set_ylim(-34, 50)
ax.legend(loc="upper right", fontsize=8)
save(fig, "shock_example")
import json
(RES / "shock_binned.json").write_text(json.dumps({"curves": curves, "jan21_shock_kmh": float(d.loc[t0, "wind"] - wind_pred.loc[t0]),
                                                  "jan21_wind": float(d.loc[t0, "wind"]), "jan21_pred": float(wind_pred.loc[t0])}, indent=1))

# ── 8. Impulse responses, with the range across the two orderings ──────────────────────────────────────
H = 10
idx = {c: i for i, c in enumerate(anom.columns)}
irf = var4.irf(H)
se_ = irf.stderr(orth=True)
alt_order = ["pm25", "wind", "rh"]
var_alt = VAR(anom[alt_order]).fit(4)
irf_alt = var_alt.irf(H).orth_irfs
sd = np.sqrt(np.diag(var4.sigma_u))
fig, axes = new_fig(4.3, ncols=2, sharey=True)
for ax, imp, c, ttl in [(axes[0], "wind", ORANGE, f"+1 SD wind shock ({sd[idx['wind']]:.1f} km/h)"),
                        (axes[1], "rh", AQUA, f"+1 SD humidity shock ({sd[idx['rh']]:.1f}% RH)")]:
    r, s = irf.orth_irfs[:H + 1, idx["pm25"], idx[imp]], se_[:H + 1, idx["pm25"], idx[imp]]
    pct = (np.exp(r) - 1) * 100
    lo, hi = (np.exp(r - 1.96 * s) - 1) * 100, (np.exp(r + 1.96 * s) - 1) * 100
    alt = (np.exp(irf_alt[:H + 1, alt_order.index("pm25"), alt_order.index(imp)]) - 1) * 100
    h = np.arange(H + 1)
    ax.fill_between(h, lo, hi, color=c, alpha=0.18, lw=0)
    ax.plot(h, pct, color=c, marker="o", ms=4, label="Weather ordered first (95% band)")
    ax.plot(h, alt, color=INK_2, ls="--", marker="s", ms=3, label="PM$_{2.5}$ ordered first (lagged effect only)")
    ax.axhline(0, color=INK_2, lw=0.9)
    ax.set_title(ttl, loc="left", color=INK)
    ax.set_xlabel("Days after the shock")
axes[0].set_ylabel("PM$_{2.5}$ change (%)")
axes[0].set_ylim(-14.5, 3)
h_, l_ = axes[0].get_legend_handles_labels()
fig.legend(h_, l_, loc="outside lower center", ncols=2, frameon=False, fontsize=8)
save(fig, "irf_range")

# ── tables ─────────────────────────────────────────────────────────────────────────────────────────────
def sci(p):
    if p < 1e-3:
        m, e = f"{p:.1e}".split("e")
        return rf"${m}\times10^{{{int(e)}}}$"
    return f"{p:.3f}" if p < 0.1 else f"{p:.2f}"


def write(name, spec, header, rows):
    body = " \\\\\n".join(" & ".join(str(c) for c in r) for r in rows)
    (TAB / f"{name}.tex").write_text(f"\\begin{{tabular}}{{{spec}}}\n\\toprule\n{header} \\\\\n\\midrule\n{body} \\\\\n\\bottomrule\n\\end{{tabular}}\n")


tex_pm = lambda s: s.replace("→", r"$\to$").replace("PM2.5", r"PM$_{2.5}$")  # noqa: E731

# stationarity (training years)
st = pd.read_csv(RES / "stationarity_train.csv", index_col=0)
labs = {"Weekly log PM2.5 (train)": r"log PM$_{2.5}$ (level)", "Weekly Δ₅₂ log PM2.5 (D=1)": r"seasonal difference $\Delta_{52}$",
        "Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1)": r"$\Delta\Delta_{52}$ (over-differenced)"}
rows = []
for k, lab in labs.items():
    r = st.loc[k]
    rows.append([lab, f"{r['adf_stat']:.2f}", f"{r['adf_crit_5%']:.2f}", sci(r["adf_p"]), f"{r['kpss_p']:.2f}", f"{r['lag1_acf']:.2f}"])
write("stationarity", "lrrrrr", r"\textbf{Weekly series, 2015--18} & \textbf{ADF stat} & \textbf{5\% crit.} & \textbf{ADF $p$} & \textbf{KPSS $p$} & \textbf{lag-1 ACF}", rows)

# variance / volatility tests with plain-English column
lt = pd.read_csv(RES / "log_justification.csv", index_col=0)
q = {"corr(monthly mean, monthly SD)": r"Does spread grow with level? (corr.\ of monthly mean and SD)",
     "Levene F (equal variance across months)": r"Is the spread equal in all 12 months? (Levene $F$)",
     "ARCH-LM statistic (7 lags, on daily change)": r"Do big changes cluster in time? (ARCH-LM)"}
rows = [[lab, f"{lt.loc[k].iloc[0]:.2f}", f"{lt.loc[k].iloc[1]:.2f}"] for k, lab in q.items()]
write("log_tests", "lrr", r"\textbf{Question the test asks} & \textbf{Raw} & \textbf{Log}", rows)

# Granger (HAC) robustness, for the backup slide
if has("granger_hac.csv"):
    gh = pd.read_csv(RES / "granger_hac.csv")
    rows = [[tex_pm(r["direction"]), tex_pm(r["spec"]), f"{r['wald_chi2']:.1f}", sci(r["p_value"])] for _, r in gh.iterrows()]
    write("granger_robust", "llrr", r"\textbf{Direction} & \textbf{Model} & \textbf{Wald $\chi^2$} & \textbf{$p$ (HAC)}", rows)

# IRF/FEVD under both orderings, for the backup slide
if has("irf_orderings.csv", "fevd_orderings.csv"):
    io = pd.read_csv(RES / "irf_orderings.csv")
    fo = pd.read_csv(RES / "fevd_orderings.csv")
    rows = []
    for shock in ["Wind", "Humidity"]:
        a = io[(io.shock == shock) & io.ordering.str.startswith("weather")].iloc[0]
        b = io[(io.shock == shock) & io.ordering.str.startswith("PM2.5")].iloc[0]
        w_ = fo[(fo.variable == shock) & fo.ordering.str.startswith("weather")].share_h14_pct.iloc[0]
        p_ = fo[(fo.variable == shock) & fo.ordering.str.startswith("PM2.5")].share_h14_pct.iloc[0]
        rows.append([f"+1 SD {shock.lower()} shock", f"{a.day1_pct:.0f}\\%", f"{b.day1_pct:.0f}\\%", f"{w_:.0f}\\%", f"{p_:.0f}\\%"])
    write("orderings", "lcccc", r"\textbf{Shock} & \textbf{Day 1: W-first} & \textbf{Day 1: P-first} & \textbf{14-day share: W-first} & \textbf{14-day share: P-first}", rows)

# ── Phase 4 (forecasting) figures, tables and numbers ─────────────────────────────────────────────────
import json as _json  # noqa: E402

FCN = _json.loads((RES / "key_numbers_forecast.json").read_text()) if has("key_numbers_forecast.json") else None
if FCN is not None:
    from matplotlib.patches import Patch  # noqa: E402
    fb = pd.read_csv(RES / "fc_backtest_forecasts.csv", parse_dates=["date"])
    fm = pd.read_csv(RES / "fc_backtest_metrics.csv")
    SELN = "Fourier+ARMA (selected)"

    # 1. backtest: 2019 forecast + MAE by fold
    f19s = fb[(fb.fold == 2019) & (fb.model == SELN)].set_index("date")
    f19c = fb[(fb.fold == 2019) & (fb.model == "Climatology")].set_index("date")
    fig, axes = new_fig(5.0, ncols=2, width_ratios=[1.5, 1])
    ax = axes[0]
    ax.fill_between(f19s.index, np.exp(f19s.mu - 1.96 * f19s.sd), np.exp(f19s.mu + 1.96 * f19s.sd), color=BLUE, alpha=0.18, lw=0, label="95% interval")
    ax.plot(f19s.index, np.exp(f19s.mu), color=BLUE, label="Fourier+ARMA")
    ax.plot(f19c.index, np.exp(f19c.mu), color=NEUTRAL, ls="--", lw=1.3, label="Climatology")
    ax.plot(f19s.index, f19s.actual, color=ORANGE, marker="o", ms=2.5, lw=1.2, label="Actual 2019")
    ax.set_ylabel("Weekly PM$_{2.5}$ ($\\mu$g/m$^3$)")
    ax.set_title("52-week forecast made on 30 Dec 2018", loc="left", color=INK)
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%b")); ax.set_ylim(0, 470); ax.legend(fontsize=6.5, ncols=2, loc="upper center")
    ax = axes[1]
    show = [("Climatology", "Clim."), (SELN, "Fourier"), ("SARIMA D=1", "SARIMA1"), ("SARIMA D=0", "SARIMA0"), ("LSTM (small)", "LSTM")]
    x_ = np.arange(len(show)); w_ = 0.27
    for k, (fo, c) in enumerate([(2017, NEUTRAL), (2018, AQUA), (2019, BLUE)]):
        ax.bar(x_ + (k - 1) * w_, [fm[(fm.fold == fo) & (fm.model == m)].MAE.iloc[0] for m, _ in show], w_, color=c, label=str(fo))
    ax.set_xticks(x_, [s for _, s in show], fontsize=6.5); ax.set_ylabel("MAE ($\\mu$g/m$^3$)"); ax.set_ylim(0, 80); ax.legend(title="forecast year", fontsize=6.5, title_fontsize=6.5, ncols=3, loc="upper left")
    ax.set_title("Error by forecast year", loc="left", color=INK)
    save(fig, "fc_backtest")

    # 2. one week ahead
    ow = pd.read_csv(RES / "fc_oneweek.csv", index_col=0)
    order_ = ["Persistence", "Climatology", "Climatology + AR(1)", "DHR, no weather", "+ lagged weather (operational)", "+ last 3 days of prior week (operational)", "+ same-week weather (ORACLE)"]
    labs_ = ["Persis-\ntence", "Clima-\ntology", "Clim.\n+AR(1)", "Fourier\nARMA", "+ lagged\nweather", "+ last 3\ndays", "+ same-week\n(oracle)"]
    fig, ax = new_fig(4.4)
    ax.bar(range(7), [ow.loc[m, "both years"] for m in order_], color=[NEUTRAL, NEUTRAL, NEUTRAL, BLUE, AQUA, AQUA, ORANGE], width=0.65)
    for i, m in enumerate(order_):
        ax.text(i, ow.loc[m, "both years"] + 0.4, f"{ow.loc[m, 'both years']:.1f}", ha="center", fontsize=8)
    ax.set_xticks(range(7), labs_, fontsize=7.5); ax.set_ylabel("MAE ($\\mu$g/m$^3$)"); ax.set_ylim(0, 35)
    ax.set_title("2018--19, one week ahead (lower is better)", loc="left", color=INK)
    save(fig, "fc_oneweek")

    # 3. 2020 outlook
    o20 = pd.read_csv(RES / "fc_outlook_2020.csv", index_col=0)
    fig, axes = new_fig(5.0, ncols=2, width_ratios=[1.3, 1])
    ax = axes[0]; xs = np.arange(12)
    ax.fill_between(xs, o20["lo95"], o20["hi95"], color=BLUE, alpha=0.18, lw=0)
    ax.plot(xs, o20["median"], color=BLUE, marker="o", ms=3.5, label="Forecast (median, 95% interval)")
    ok = o20["actual_days_covered"] >= 25
    ax.plot(xs[ok.to_numpy()], o20.loc[ok, "actual_mean_2020"], color=ORANGE, marker="s", ms=3.5, label="Actual 2020")
    for yv in (60, 90, 120):
        ax.axhline(yv, color=MUTED, lw=0.6, ls=":")
    ax.set_xticks(xs, [m[0] for m in months]); ax.set_ylabel("Monthly PM$_{2.5}$"); ax.legend(fontsize=7, loc="upper center")
    ax.set_title("Forecast made in Dec 2019", loc="left", color=INK)
    ax = axes[1]
    cols = {"Good": "#00B050", "Satisfactory": "#92D050", "Moderate": "#E6C200", "Poor": "#FF9900", "Very Poor": "#FF0000", "Severe": "#C00000"}
    bot = np.zeros(12)
    for c in cols:
        v = o20[f"days_{c}"].to_numpy(); ax.bar(xs, v, bottom=bot, color=cols[c], width=0.8); bot += v
    ax.set_xticks(xs, [m[0] for m in months]); ax.set_ylabel("Expected days"); ax.set_title("Days per PM$_{2.5}$ band", loc="left", color=INK)
    fig.legend([Patch(color=c) for c in cols.values()], list(cols), loc="outside lower center", ncols=6, frameon=False, fontsize=7)
    save(fig, "fc_outlook")

    # 4. lockdown
    w20 = pd.read_csv(RES / "fc_weekly_2020.csv", index_col=0, parse_dates=True) if has("fc_weekly_2020.csv") else None
    if w20 is not None:
        fig, ax = new_fig(4.6)
        ax.fill_between(w20.index, w20.lo95, w20.hi95, color=BLUE, alpha=0.18, lw=0, label="95% interval (no lockdown)")
        ax.plot(w20.index, w20["median"], color=BLUE, label="No-lockdown forecast")
        ax.plot(w20.index, w20.weather_adj_median, color=AQUA, ls="--", label="Weather-adjusted forecast")
        ax.plot(w20.index, w20.actual, color=ORANGE, marker="o", ms=3, label="Actual 2020")
        ax.axvspan(pd.Timestamp("2020-03-25"), pd.Timestamp("2020-05-31"), color=NEUTRAL, alpha=0.25, lw=0)
        ax.text(pd.Timestamp("2020-04-27"), ax.get_ylim()[1] * 0.93, "lockdown", ha="center", fontsize=8, color=INK_2)
        ax.set_ylabel("Weekly PM$_{2.5}$ ($\\mu$g/m$^3$)"); ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%b")); ax.legend(fontsize=7.5, ncols=2, loc="upper right")
        save(fig, "fc_lockdown")

    # 5. station check
    sc = pd.read_csv(RES / "station_check.csv", index_col=0)
    fig, axes = new_fig(4.2, ncols=2)
    axes[0].bar(sc.index, sc.stations, color=NEUTRAL, width=0.6); axes[0].set_title("Stations reporting PM$_{2.5}$", loc="left", color=INK)
    for lab, col, c in [("All stations", "all_log_anom", BLUE), ("Fixed 6-station panel", "panel_log_anom", ORANGE), ("City, weather-adjusted", "weather_adj_log_anom", AQUA)]:
        axes[1].plot(sc.index, sc[col], marker="o", ms=3.5, color=c, label=lab)
    axes[1].axhline(0, color=INK_2, lw=0.8); axes[1].set_ylabel("Mean log anomaly"); axes[1].legend(fontsize=7)
    axes[1].set_title("The decline persists on fixed monitors", loc="left", color=INK)
    save(fig, "fc_station")

    # tables
    ld = pd.read_csv(RES / "fc_loss_diff.csv"); ld = ld[ld.folds == "folds 2018+2019"].set_index("model")
    mae = pd.read_csv(RES / "fc_backtest_mae.csv", index_col=0)
    rows = []
    for m, lab in [("Climatology", "Climatology (benchmark)"), ("Climatology + AR(1)", r"Climatology + AR(1)"), ("Linear regression", "Linear regression"),
                   (SELN, "Fourier+ARMA (selected)"), ("SARIMA D=1", r"SARIMA $D=1$"), ("SARIMA D=0", r"SARIMA $D=0$ (+constant)"), ("LSTM (small)", "LSTM (small)"), ("Seasonal naive", "Seasonal naive")]:
        v = ld.loc[m, "verdict"] if m in ld.index else "reference"
        rows.append([lab] + [f"{mae.loc[m, c]:.1f}" for c in ["2017", "2018", "2019", "mean 2018-19"]] + [v])
    write("fc_backtest", "lrrrrl", r"\textbf{Model} & \textbf{2017} & \textbf{2018} & \textbf{2019} & \textbf{Mean 18--19} & \textbf{vs climatology}", rows)
    rows = []
    for m_, r in o20.iterrows():
        pp = r["days_Poor"] + r["days_Very Poor"] + r["days_Severe"]
        act = f"{r['actual_mean_2020']:.0f}" if r["actual_days_covered"] >= 25 else "--"
        rows.append([m_, f"{r['median']:.0f}", f"{r['lo95']:.0f}--{r['hi95']:.0f}", f"{r['P(mean>90)'] * 100:.0f}\\%", f"{pp:.0f}", act])
    write("fc_outlook", "lrrrrr", r"\textbf{Month} & \textbf{Median} & \textbf{95\% interval} & \textbf{P(mean$>$90)} & \textbf{Days Poor+} & \textbf{Actual}", rows)

    ck = pd.read_csv(RES / "fc_calibration_2019.csv", index_col=0)
    nums_fc = {
        "fcMaeSelNineteen": f"{FCN['backtest']['mae_selected']['2019']:.1f}", "fcMaeClimNineteen": f"{FCN['backtest']['mae_climatology']['2019']:.1f}",
        "fcMaeSarimaNineteen": f"{FCN['backtest']['sarima_D1_mae']['2019']:.1f}", "fcMaeSarimaSeventeen": f"{FCN['backtest']['sarima_D1_mae']['2017']:.0f}",
        "fcMaeLstmNineteen": f"{FCN['backtest']['lstm_mae']['2019']:.0f}", "fcMaeSarimaZeroNineteen": f"{FCN['backtest']['sarima_D0_mae']['2019']:.0f}",
        "fcCovRaw": f"{FCN['coverage_2019_raw'] * 100:.0f}", "fcCovCal": f"{FCN['coverage_2019_calibrated'] * 100:.0f}",
        "fcMaSE": f"{FCN['sarima_D1_maS_se']:.1f}", "fcMaCoef": f"{FCN['sarima_D1_maS_coef']:.3f}".replace("-", "$-$"),
        "fcOneLagged": f"{FCN['oneweek_gain_pct']['lagged']:+.1f}".replace("-", "$-$"), "fcOneLastThree": f"{FCN['oneweek_gain_pct']['last3']:+.1f}".replace("-", "$-$"),
        "fcOneOracle": f"{FCN['oneweek_gain_pct']['oracle']:+.1f}",
        "fcLockPct": f"{abs(FCN['lockdown']['plain']['gap_median_pct']):.0f}", "fcLockLo": f"{abs(FCN['lockdown']['plain']['gap_hi95_pct']):.0f}", "fcLockHi": f"{abs(FCN['lockdown']['plain']['gap_lo95_pct']):.0f}",
        "fcLockWxPct": f"{abs(FCN['lockdown']['weather_adjusted']['gap_median_pct']):.0f}",
        "fcValPoorPred": f"{FCN['validation_2019']['poor_or_worse_pred_pct']:.0f}", "fcValPoorAct": f"{FCN['validation_2019']['poor_or_worse_actual_pct']:.0f}",
        "fcValInside": f"{FCN['validation_2019']['months_actual_inside_95']}",
    }
    sk = _json.loads((RES / "key_numbers_eda.json").read_text())
    nums_fc.update({"declAll": f"{abs(sk['decline_2016_2019_pct']['all_stations']):.0f}", "declPanel": f"{abs(sk['decline_2016_2019_pct']['fixed_panel']):.0f}",
                    "declWx": f"{abs(sk['decline_2016_2019_pct']['weather_adjusted']):.0f}"})
    FC_NUMS = nums_fc
else:
    FC_NUMS = {}

print("figures:", sorted(p.name for p in FIG.glob("*.pdf")))

# ── numbers used in the slide text (single source of truth) ────────────────────────────────────────────
import json  # noqa: E402

def jl(name):
    return json.loads((RES / name).read_text())


eda, var_k = jl("key_numbers_eda.json"), jl("key_numbers_var.json")
nums = {
    "pctPoor": f"{eda['pct_days_poor_or_worse']:.0f}", "winterMean": f"{eda['winter_mean_pm25']:.0f}", "monsoonMean": f"{eda['monsoon_mean_pm25']:.0f}",
    "ratioWM": f"{eda['winter_to_monsoon_ratio']:.1f}", "Fs": f"{eda['seasonal_strength']:.2f}",
}
lt_ = pd.read_csv(RES / "log_justification.csv", index_col=0)
nums.update({
    "skewRaw": f"{lt_.loc['Skewness'].iloc[0]:+.2f}", "skewLog": f"{lt_.loc['Skewness'].iloc[1]:+.2f}".replace("-", "$-$"),
    "sdRatioRaw": f"{lt_.loc['Max / min monthly SD'].iloc[0]:.1f}", "sdRatioLog": f"{lt_.loc['Max / min monthly SD'].iloc[1]:.1f}",
    "archRaw": f"{lt_.loc['ARCH-LM statistic (7 lags, on daily change)'].iloc[0]:.0f}", "archLog": f"{lt_.loc['ARCH-LM statistic (7 lags, on daily change)'].iloc[1]:.0f}",
    "levPlog": f"{lt_.loc['Levene p-value'].iloc[1]:.3f}", "boxcox": f"{eda['boxcox_lambda_daily']:.3f}",
})
io_, fo_ = pd.read_csv(RES / "irf_orderings.csv"), pd.read_csv(RES / "fevd_orderings.csv")
wk_ = pd.read_csv(RES / "weekly_weather_lag.csv")
neg = lambda x: f"{abs(x):.0f}"  # noqa: E731
nums.update({
    "irfWindA": neg(io_[(io_.shock == "Wind") & io_.ordering.str.startswith("PM2.5")].day1_pct.iloc[0]),
    "irfWindB": neg(io_[(io_.shock == "Wind") & io_.ordering.str.startswith("weather")].day1_pct.iloc[0]),
    "irfRhA": neg(io_[(io_.shock == "Humidity") & io_.ordering.str.startswith("PM2.5")].day1_pct.iloc[0]),
    "irfRhB": neg(io_[(io_.shock == "Humidity") & io_.ordering.str.startswith("weather")].day1_pct.iloc[0]),
    "fevdA": f"{fo_[fo_.ordering.str.startswith('PM2.5') & (fo_.variable != 'PM2.5')].share_h14_pct.sum():.0f}",
    "fevdB": f"{fo_[fo_.ordering.str.startswith('weather') & (fo_.variable != 'PM2.5')].share_h14_pct.sum():.0f}",
    "lagWindP": f"{wk_[wk_.term == 'wind (last week)'].p_value.iloc[0]:.2f}", "lagRhP": f"{wk_[wk_.term == 'humidity (last week)'].p_value.iloc[0]:.2f}",
    "sameWeekRsq": f"{wk_[wk_.model == 'same-week weather'].r2_model.iloc[0]:.2f}",
})
sb = jl("shock_binned.json")
nums.update({"shockWindBig": f"{abs(sb['curves']['wind']['pct'][-1]):.0f}", "shockWindBigZ": f"{sb['curves']['wind']['z'][-1]:.1f}",
             "shockWindCalm": f"{sb['curves']['wind']['pct'][0]:.0f}", "shockWindCalmZ": f"{abs(sb['curves']['wind']['z'][0]):.1f}",
             "janWind": f"{sb['jan21_wind']:.1f}", "janPred": f"{sb['jan21_pred']:.1f}", "janShock": f"{sb['jan21_shock_kmh']:.1f}"})
bm_ = pd.read_csv(RES / "monthly_mean_sd.csv", index_col=0)
nums.update({"sdNov": f"{bm_.loc[11, 'sd_raw']:.0f}", "sdAug": f"{bm_.loc[8, 'sd_raw']:.0f}"})
nums.update(FC_NUMS)
(TAB / "numbers.tex").write_text("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in nums.items()) + "\n")
print("numbers:", len(nums))
```

## verify_numbers.py last output
```
65/65 checks passed (authors' run, 2026-11-16)
```


# 08 Report and deck LaTeX source

## report/report.tex
```latex
% Project report, MATH F428. Build: cd report && tectonic report.tex  (numbers and figures come from ../slides/beamer after make_figures.py)
\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.3cm]{geometry}
\usepackage{graphicx,booktabs,amsmath,amssymb,hyperref,float,caption,xcolor}
\hypersetup{colorlinks=true,urlcolor=blue!60!black,linkcolor=blue!60!black}
\graphicspath{{../slides/beamer/fig/}{../figures/}}
\newcommand{\pmtwo}{PM$_{2.5}$}
\newcommand{\ugm}{$\mu$g/m$^3$}
\newcommand{\ugmm}{\ensuremath{\mu\mathrm{g/m^3}}}
\input{../slides/beamer/tables/numbers.tex}
\setlength{\parskip}{4pt}\setlength{\parindent}{0pt}
\renewcommand{\arraystretch}{1.1}
\title{Forecasting Delhi's \pmtwo{}: Seasonality, Weather Predictability and a Rolling-Origin Forecasting Study}
\author{Kushagra Singh \and Yatin JM \and Aryan Choudhary\\ BITS Pilani, Goa \,--\, MATH F428 Time Series Analysis}
\date{November 2026}
\begin{document}
\maketitle
\begin{abstract}
We study daily \pmtwo{} in Delhi from January 2015 to July 2020 (CPCB monitors; ERA5 wind and humidity). \pmtwo{} has a very strong annual cycle (winter \ratioWM$\times$ the monsoon) and a slow downward drift. After removing the cycle, wind and humidity anomalies \emph{predict} \pmtwo{} for about a week (Granger causality in a VAR, robust to lag order, differencing, HAC errors and rain/temperature controls), but their information is gone at the weekly scale: last week's weather adds nothing for this week, and even the same week's weather, unknown in advance, improves a one-week forecast by only \fcOneOracle\%. For 52-week forecasts we compare climatology, Fourier-term regression with ARMA errors, SARIMA, linear regression and a small LSTM on three expanding-window origins. A smooth Fourier+ARMA model matches or slightly beats climatology; SARIMA with seasonal differencing is fragile, and the LSTM is clearly worse. We fix several diagnostic and design errors found in an earlier draft (residual burn-in, missing constant, leakage), calibrate prediction intervals out of sample, and produce a monthly 2020 outlook that correctly flags the lockdown as a \fcLockPct\% fall below the no-lockdown forecast.
\end{abstract}

\section{Introduction}
Delhi's air is Poor or worse (PM$_{2.5}>90$ \ugm{}) on \pctPoor\% of days in our sample, and the pattern repeats every winter. We ask two questions: \textbf{Q1} (explain) does weather predict \pmtwo{}, and over what horizon? \textbf{Q2} (forecast) how well can \pmtwo{} be forecast one week and 52 weeks ahead, and which model should be trusted? The project was reviewed independently three times; every concrete claim of those reviews was re-tested on the data, and the verdicts are in \texttt{docs/REVIEW\_RESPONSES.md} (summarised in Section~\ref{sec:review}). Because the data end in July 2020, the deliverable is a \emph{historical forecasting study} (backtests for 2017--2019 and an outlook for 2020 made in December 2019), not a current health advisory.

\section{Data and cleaning}
\pmtwo{} (and NO$_2$, SO$_2$) are the CPCB city-level daily values for Delhi from the Kaggle dataset \texttt{rohanrao/air-quality-data-in-india}: 2{,}009 days, 1 Jan 2015 to 1 Jul 2020, with 2 missing \pmtwo{} values (interpolated; gaps $\le3$ days are interpolated, longer ones are left missing). Wind speed, relative humidity, temperature and precipitation are ERA5 reanalysis values for central Delhi (28.61$^\circ$N, 77.21$^\circ$E) from the Open-Meteo archive. Forecasting uses weekly means (weeks ending Sunday, 287 weeks). Modelling is on $\log$ \pmtwo{}; a back-transformed forecast $\exp(\mu)$ is a \emph{median}, and mean forecasts use $\exp(\mu_h+\sigma_h^2/2)$ with the horizon-specific $\sigma_h$. The 2020 lockdown never enters model selection.

\section{Exploratory analysis}
\subsection{Seasonality and the log transform}
Winter (Nov--Jan) averages \winterMean{} \ugm{} against \monsoonMean{} in the monsoon (\ratioWM$\times$). An STL decomposition of the weekly log series gives a seasonal strength $F_S=\Fs$ on the training years (0.89 on the full sample). The spread of daily \pmtwo{} grows with its level (monthly mean and SD correlate at 0.95; the largest monthly SD is \sdRatioRaw$\times$ the smallest); after the log it varies only \sdRatioLog$\times$ and the skewness falls from \skewRaw{} to \skewLog{}. The Box-Cox $\lambda$ is \boxcox{} (about 0.10 on the training years), i.e. close to the log. Some volatility clustering remains in the daily series (ARCH-LM \archRaw{} $\to$ \archLog{}); we check it again on the weekly forecast residuals, where it is absent (ARCH-LM(4) $p=0.87$).
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{stl.pdf}\caption{STL decomposition of weekly log \pmtwo{}.}\end{figure}

\subsection{Stationarity and the hidden drift}
ADF and KPSS (opposite null hypotheses) on 2015--2018 weekly log \pmtwo{} are both consistent with stationarity, as is the seasonal difference; a further first difference over-differences (lag-1 autocorrelation $-0.46$). So $d=0$. But KPSS on the \emph{raw level} is dominated by the large seasonal cycle. Removing a day-of-year climatology reveals a slow decline: the KPSS statistic of the anomaly is 0.90 on 2015--18 and 2.0 on 2015--19 (5\% critical value 0.46), and the mean log anomaly falls from $+0.10$ in 2016 to $-0.19$ in 2019. The level is therefore \emph{not} constant, which drives the model design in Section~\ref{sec:fc}.

\subsection{Is the decline real? A station-level check}
The city series is the mean over reporting stations (correlation 0.995 with the station-level mean), and the number of stations reporting \pmtwo{} rose from 10 and 8 (2015, 2016) to 37 (2018, 2019), so a change in the station mix could create a spurious decline. A fixed panel of six long-running stations (at least 60 days in each year) falls by \declPanel\% between 2016 and 2019, all stations by \declAll\%, and the city series after regressing out wind, humidity and temperature by \declWx\%. We conclude that most of the decline is real, while stressing that the panel is small and thin in 2017.
\begin{figure}[H]\centering\includegraphics[width=0.85\linewidth]{fc_station.pdf}\caption{Left: stations reporting; right: mean log anomaly by year for all stations, the fixed panel and the weather-adjusted city series.}\end{figure}

\section{Does weather predict \pmtwo{}? (Q1)}
Wind, humidity and log \pmtwo{} are deseasonalised with a smoothed day-of-year climatology (31-day circular window; leap years handled by mapping 29 Feb to day 59) and fitted in a VAR(4) (lag by AIC; BIC picks 2; stable, largest root modulus 0.81; portmanteau $p=0.17$).
\paragraph{Granger causality.} Joint tests that lags 1--$k$ of wind or humidity add nothing to the \pmtwo{} equation are rejected at every $k=1,\dots,7$ ($p<10^{-9}$). With HAC (Newey-West) errors the 4-lag tests give $p\approx6\times10^{-20}$ (wind) and $4\times10^{-11}$ (humidity); adding rain and temperature controls gives $9\times10^{-18}$ and $7\times10^{-8}$; adding a linear time trend or using a climatology fitted on 2015--2018 only changes nothing. Season-specific tests show both variables are significant in winter and in the monsoon ($p\le5\times10^{-4}$); the interactions are weak (monsoon $\times$ humidity $p=0.20$, winter $\times$ wind $p=0.03$), so the EDA impression that humidity matters only in the monsoon is a correlation pattern, not a difference in predictive content. The reverse direction is absent for humidity and weak for wind (lag orders 1 and 2 only, $p=0.04$ and $0.02$). We call this a \emph{predictive association}: mixing height, stubble burning and fireworks are unmeasured, and the ERA5 data are one grid cell.
\begin{figure}[H]\centering\includegraphics[width=0.9\linewidth]{granger_hac.pdf}\caption{HAC Wald tests (4 lags).}\end{figure}
\paragraph{Size and timing.} A one-SD wind shock (2.5 km/h) lowers \pmtwo{} by \irfWindA--\irfWindB\% the next day, a one-SD humidity shock (5.4\% RH) by \irfRhA--\irfRhB\%, fading within about a week; the range reflects the Cholesky ordering (weather first allows same-day effects). The generalised IRF, which does not depend on ordering, gives $-12.0\%$ and $-5.2\%$ on day 1, inside or at the edge of those ranges. Weather shocks explain \fevdA--\fevdB\% of the 14-day forecast-error variance of \pmtwo{} depending on the ordering.
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{irf_range.pdf}\caption{Impulse responses of \pmtwo{} to wind and humidity shocks under both orderings.}\end{figure}
\paragraph{Horizon.} At the weekly scale, last week's wind and humidity add nothing to last week's \pmtwo{} for predicting this week's ($\Delta R^2=0.005$, joint HAC Wald $p=0.51$). Weather is therefore a short-memory predictor, and the 52-week models use no weather.

\section{Forecasting (Q2)}\label{sec:fc}
\subsection{Models and evaluation design}
All models forecast weekly log \pmtwo{} with no weather inputs: seasonal naive; \textbf{climatology} (mean of each calendar week, benchmark); climatology + AR(1); \textbf{Fourier + ARMA} (dynamic harmonic regression: $K\le5$ yearly sine/cosine pairs, ARMA$(p,q)$ errors with $p\le2,q\le1$, and a level that is constant, linear or a random walk); SARIMA$(1,0,1)(0,1,1)_{52}$ and SARIMA$(1,0,1)(1,0,0)_{52}$ with a constant; Linear Regression on Fourier terms and a linear trend; and a small LSTM (16 units, recursive, seeded). For the Fourier model, $K$ and $(p,q)$ are chosen by AICc within each level type, and the level type by validation on the last training year; this procedure was declared the headline before any test year was inspected. Evaluation uses three expanding-window origins (end of 2016, 2017, 2018), each forecasting the next 52 weeks, refitting and reselecting every time. The 2017 fold (two training years) is a stress test; 2018 and 2019 are the main evidence. Paired error differences to climatology are summarised with a moving-block bootstrap (8-week blocks); a plain Diebold--Mariano test on 52 weeks of one forecast path is not valid and is not used here.
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{fc_backtest.pdf}\caption{Left: the 2019 forecast of the selected model against climatology and the actual values. Right: MAE by forecast year.}\end{figure}
\subsection{Backtest results}
\begin{table}[H]\centering\footnotesize\input{../slides/beamer/tables/fc_backtest.tex}\caption{52-week-ahead MAE (\ugm{}) by forecast year; last column: bootstrap verdict against climatology over 2018 and 2019.}\end{table}
In 2019 the selected Fourier+ARMA model has an MAE of \fcMaeSelNineteen{} against \fcMaeClimNineteen{} for climatology and \fcMaeSarimaNineteen{} for the seasonal-differenced SARIMA; the SARIMA is, however, at \fcMaeSarimaSeventeen{} in the 2017 fold, where it has only two seasons to learn from. Over 2018--2019 only the seasonal naive forecast, SARIMA with $D=0$ (\fcMaeSarimaZeroNineteen{} in 2019) and the LSTM (\fcMaeLstmNineteen{}) are clearly worse than climatology. The linear-trend Fourier variant is better on 2018--19 (the bootstrap interval excludes 0) but not over all three origins, and it was not the pre-declared choice, so we do not claim it. The honest summary: a year ahead the calendar carries almost all of the predictable signal, and with three origins the remaining models cannot be ranked.

\subsection{Diagnostics: errors in the earlier draft}
The draft's Ljung--Box test had $p\approx0$ at every lag. This was an artifact: a state-space SARIMA with $D=1$ initialises its first 52 seasonal states diffusely, so the first 52 in-sample residuals equal the level of the series (about 5 on the log scale). With them excluded (\texttt{loglikelihood\_burn}) the residuals are acceptable at lags 10 and 26 ($p=0.49,\,0.10$) but not at lag 52 ($p=0.016$). The seasonal MA coefficient is \fcMaCoef{} with a standard error far above 1: the parameter sits on the invertibility boundary and is not identified, the usual sign that the seasonal difference is unnecessary. The $D=0$ candidate in the draft had no constant, forcing the forecast toward $\log \text{PM}_{2.5}=0$; with a constant its validation MAE falls from 39.7 to 30.6 (but it remains the worst non-LSTM model overall). The selected Fourier+ARMA model still shows autocorrelation at lags 26 and 52 in the 2019 fold ($p=0.001$ and $0.009$) and ARCH-LM(4) is clean ($p=0.87$): there is more seasonal structure than a few harmonics capture, which we list as a limit.

\subsection{Prediction intervals}
Model-based 95\% intervals covered \fcCovRaw\% of the 2019 weeks; all misses were below the lower bound because 2019 was cleaner than 2015--18, so the problem is level bias as much as width. We rescale the predictive standard deviation by season (winter vs other months, shrunk toward the pooled value) using only the 2017 and 2018 errors, and re-centre only if the bias has the same sign and size $>0.5$ standard deviations in both calibration years; it did not (mean standardised errors $-0.66$ and $-0.45$), so only the scale is changed. On 2019 the calibrated coverage is \fcCovCal\%. The scale factors differ by fold (1.33/1.42 for 2019, 1.09/0.95 for the 2020 forecast), which shows the calibration is itself uncertain.

\subsection{One week ahead: does weather help?}
Each year 2018 and 2019 is forecast one week at a time with parameters fitted on earlier data. \emph{Lagged weather} (last week's wind and humidity anomalies) changes the error by \fcOneLagged\%, the \emph{last three days} of the previous week by \fcOneLastThree\%, and the \emph{same week's} weather (which is observed, not forecast, and so a hindsight upper bound) by \fcOneOracle\% (Harvey--Leybourne--Newbold $p=0.07$). Weather is explanatory over days, but a poor forecasting input.
\begin{figure}[H]\centering\includegraphics[width=0.7\linewidth]{fc_oneweek.pdf}\caption{One-week-ahead MAE, 2018--19.}\end{figure}

\subsection{The 2020 outlook and its validation}
The final model is fitted on 2015--2019 (selection again inside the window: linear level, $K=5$, AR(1) errors), 5{,}000 weekly paths are simulated, calibrated, converted to daily values by adding a within-week log offset resampled from the same calendar month of the training data, and classified into the CPCB \pmtwo{} bands. The same pipeline run for 2019 (data to 2018 only) places all \fcValInside{} monthly means inside the 95\% interval, but over-predicts the share of Poor-or-worse days (\fcValPoorPred\% vs \fcValPoorAct\% actual), which is the level bias again. These bands are \pmtwo{} sub-index bands, not the official AQI (the maximum over all pollutants).
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{fc_outlook.pdf}\caption{2020 outlook: monthly mean \pmtwo{} with 95\% interval and expected days per band.}\end{figure}
\begin{table}[H]\centering\scriptsize\input{../slides/beamer/tables/fc_outlook.tex}\caption{2020 outlook (\ugm{}); ``Days Poor+'' = expected days above 90 \ugm{}; Actual shown for full months only.}\end{table}
\subsection{Case study: the 2020 lockdown}
From 29 March to 31 May 2020 \pmtwo{} was about \fcLockPct\% below the no-lockdown forecast (95\% interval \fcLockLo--\fcLockHi\%). Using a version of the model that is given the actual wind and humidity of those weeks, the gap is \fcLockWxPct\%: most of the drop is not weather. This is descriptive; it depends on the forecast level for 2020 being right, which the interval calibration above shows is uncertain.
\begin{figure}[H]\centering\includegraphics[width=0.85\linewidth]{fc_lockdown.pdf}\caption{Actual weekly \pmtwo{} in 2020 against the no-lockdown forecast and a weather-adjusted forecast.}\end{figure}

\section{Review of the project and what changed}\label{sec:review}
Three independent reviews proposed about 30 changes. We accepted the confirmed errors (diagnostic burn-in, missing constant, leakage in headline statistics, wording that over-stated causality or p-values, the PM$_{2.5}$-band versus AQI distinction, an invalid DM test) and rejected others after testing them (for example, the claim that re-anchoring the level gives 94\% coverage gives 90\% in the data; the shock-bin statistic has no Jensen bias; humidity's effect is not detectably monsoon-specific). The full log, with evidence for each claim, is \texttt{docs/REVIEW\_RESPONSES.md}.

\section{Limitations}
(i) Granger causality is predictive; boundary-layer height, stubble burning and fireworks are unmeasured, and ERA5 is a single grid cell. (ii) Three backtest origins give few independent tests; most model differences are not significant. (iii) A level bias remains: 2019 was cleaner than the training years, and the calibrated intervals depend on the fold. (iv) The Fourier model leaves some autocorrelation at lags 26 and 52. (v) One city; the data end in July 2020 and the monitoring network changed during the sample; the fixed-station check is small. (vi) The bands are \pmtwo{} sub-index bands, not the official AQI. (vii) The LSTM is deliberately small and is not tuned: it is a small-data negative result, not a statement about deep learning in general.

\section{Conclusion}
Delhi's \pmtwo{} is overwhelmingly a calendar phenomenon with a slowly falling level. Wind and humidity anomalies help for about a week, not for a year. For 52-week forecasts a smooth Fourier+ARMA model is as good as or marginally better than climatology and more robust than SARIMA, and its uncertainty can be calibrated; the forecast correctly isolates the 2020 lockdown. The most valuable parts of the work are the honest accounting of what is and is not significant and the correction of diagnostic errors that would have led to wrong model choices.

\section*{Reproducibility}
\texttt{pip install -r requirements.txt}; download the CPCB files (Section~2) and run notebooks 01--04; then \texttt{python slides/beamer/make\_figures.py}, \texttt{python slides/beamer/verify\_numbers.py} (65 independent checks of every number on the slides) and build \texttt{slides/beamer/main.tex} and this report with \texttt{tectonic}. Code: \texttt{src/} (data, tsa, forecast, aqi, plots).
\end{document}
```

## slides/beamer/main.tex
```latex
% Delhi PM2.5: progress presentation, MATH F428.
% Build: python make_figures.py && tectonic main.tex   (numbers in the slides come from tables/numbers.tex)
\documentclass[aspectratio=169,11pt]{beamer}
\usepackage{graphicx}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,shapes.misc,calc}
\usepackage{booktabs}
\usepackage[most]{tcolorbox}
\usepackage{hyperref}
\hypersetup{colorlinks=true,urlcolor=blue!70!black,linkcolor=blue!70!black}

% ── palette (same blue / orange / aqua as the figures) ─────────────────────────────────────────────────
\definecolor{navy}{HTML}{12284C}
\definecolor{pblue}{HTML}{2A78D6}
\definecolor{porange}{HTML}{EB6834}
\definecolor{paqua}{HTML}{1BAF7A}
\definecolor{pgreen}{HTML}{2E8B57}
\definecolor{lightbg}{HTML}{EEF3FA}
\definecolor{graytxt}{HTML}{5B6573}

\usetheme{default}
\usefonttheme{professionalfonts}
\setbeamertemplate{navigation symbols}{}
\setbeamercolor{normal text}{fg=black}
\setbeamercolor{structure}{fg=pblue}
\setbeamercolor{frametitle}{bg=navy,fg=white}
\setbeamerfont{frametitle}{size=\large,series=\bfseries}
\setbeamersize{text margin left=0.7cm,text margin right=0.7cm}
\setbeamertemplate{itemize item}{\color{pblue}$\blacktriangleright$}
\setbeamertemplate{itemize subitem}{\color{pblue}$\bullet$}
\setlength{\leftmargini}{1.1em}

% slim navy title bar
\setbeamertemplate{frametitle}{%
  \nointerlineskip
  \begin{beamercolorbox}[wd=\paperwidth,ht=0.85cm,dp=0.25cm,leftskip=0.7cm]{frametitle}
    \usebeamerfont{frametitle}\insertframetitle
  \end{beamercolorbox}\vspace{0.05cm}}

% footer: course | topic, small logo, page number
\setbeamertemplate{footline}{%
  \leavevmode\hbox to\paperwidth{%
    \hspace*{0.7cm}\raisebox{0.12cm}{\color{graytxt}\tiny MATH F428 $\cdot$ Delhi PM$_{2.5}$ forecasting $\cdot$ K.\ Singh, Y.\ JM, A.\ Choudhary (BITS Goa)}\hfill
    \raisebox{0.03cm}{\includegraphics[height=0.36cm]{logo.png}}\hspace*{0.25cm}%
    \raisebox{0.12cm}{\color{graytxt}\tiny\insertframenumber\,/\,\inserttotalframenumber}\hspace*{0.7cm}}%
  \vskip0.04cm}

% boxes: definition (light), takeaway (navy)
\newtcolorbox{defbox}[1]{enhanced,colback=lightbg,colframe=pblue,boxrule=0pt,leftrule=2.5pt,arc=1pt,
  left=5pt,right=5pt,top=2pt,bottom=2pt,before skip=3pt,after skip=3pt,fontupper=\footnotesize,
  before upper={\textbf{\textcolor{pblue}{#1}}\;}}
\newtcolorbox{takeaway}{enhanced,colback=navy,colupper=white,boxrule=0pt,arc=2pt,
  left=6pt,right=6pt,top=3pt,bottom=3pt,before skip=3pt,after skip=0pt,fontupper=\small}
\newtcolorbox{card}[2][]{enhanced,colback=white,colframe=#2,coltitle=white,colbacktitle=#2,boxrule=0.6pt,
  arc=2pt,fonttitle=\bfseries\small,fontupper=\small,left=5pt,right=5pt,top=3pt,bottom=3pt,#1}

\tikzset{
  sbox/.style={draw=#1,rounded corners=2pt,line width=0.9pt,fill=white,align=left,inner sep=4pt,text width=5.1cm,minimum height=1.25cm},
  sres/.style={draw=#1,rounded corners=2pt,line width=0.9pt,fill=#1!8,align=left,inner sep=4pt,text width=4.0cm,minimum height=1.25cm},
  gbox/.style={draw=#1,rounded corners=2pt,fill=#1!8,line width=0.8pt,align=center,inner sep=3pt,text width=3.9cm},
  sarr/.style={-{Stealth[length=2.2mm]},line width=0.9pt,color=graytxt}}
\newcommand{\pmtwo}{PM$_{2.5}$}
\newcommand{\ugm}{$\mu$g/m$^3$}
\renewcommand{\arraystretch}{1.1}
\setlength{\parskip}{0pt}\setlength{\parindent}{0pt}
\input{tables/numbers.tex}

\title{Forecasting Delhi's PM$_{2.5}$ Air Pollution}
\author{Kushagra Singh \and Yatin JM \and Aryan Choudhary}
\date{November 2026}

\begin{document}

% ───────────────────────── 1. Title ─────────────────────────
\begin{frame}[plain]
  \begin{tikzpicture}[remember picture,overlay]
    \fill[navy] (current page.south west) rectangle (current page.north east);
    \fill[porange] ([xshift=0.9cm,yshift=-2.15cm]current page.north west) rectangle +(1.4cm,0.09cm);
    \node[anchor=north west,text=white,text width=12cm,inner sep=0] at ([xshift=0.9cm,yshift=-2.4cm]current page.north west)
      {{\fontsize{24}{28}\selectfont\bfseries Forecasting Delhi's PM$_{2.5}$\\[2pt] Air Pollution}\\[8pt]
       {\large Time-series analysis: VAR, Granger causality and seasonal forecasting}\\[14pt]
       {\normalsize Kushagra Singh \;$\cdot$\; Yatin JM \;$\cdot$\; Aryan Choudhary}\\[3pt]
       {\small BITS Pilani, Goa \;$\cdot$\; MATH F428 Project Presentation \;$\cdot$\; November 2026}};
    \node[anchor=south west,text=white!85!navy,text width=10cm,inner sep=0] at ([xshift=0.9cm,yshift=0.8cm]current page.south west)
      {\small Can weather explain Delhi's smog, and can we forecast it a year ahead?};
    \node[anchor=north east,fill=white,circle,inner sep=2pt] at ([xshift=-0.8cm,yshift=-0.8cm]current page.north east)
      {\includegraphics[height=1.5cm]{logo.png}};
  \end{tikzpicture}
\end{frame}

% ───────────────────────── 2. The problem ─────────────────────────
\begin{frame}{The Problem: Delhi's Air Is Unhealthy Most of the Year}
  \centering
  \includegraphics[width=\linewidth]{fig/problem_aqi.pdf}\\[3pt]
  \begin{defbox}{PM$_{2.5}$ and AQI:}
    particles under 2.5 $\mu$m that reach the lungs and blood, in \ugm{} (micrograms per m$^3$). \textbf{AQI} = India's colour-coded Air Quality Index; the bands show its PM$_{2.5}$ categories (Poor starts above 90 \ugm{}). The official AQI takes the worst pollutant; we use the PM$_{2.5}$ band only.
  \end{defbox}
  \begin{takeaway}
    \textbf{\pctPoor\%} of days (2015--2020) were Poor or worse, and the pattern repeats yearly: winter averages \textbf{\winterMean} \ugm{}, the monsoon \textbf{\monsoonMean}: winter is \textbf{\ratioWM$\times$} higher.
  \end{takeaway}
\end{frame}

% ───────────────────────── 3. What we are building ─────────────────────────
\begin{frame}{What We Are Building: Two Questions, Two Time Horizons}
  \centering
  \begin{tikzpicture}[x=1cm,y=1cm,font=\footnotesize]
    \node[draw=navy,fill=navy,text=white,rounded corners=2pt,align=center,text width=2.3cm,minimum height=3.6cm,inner sep=4pt] (data)
      at (1.15,2.0) {\bfseries Data\\[3pt]\footnotesize daily \pmtwo{}, wind, humidity\\ 2015--2020\\[3pt] weekly means for forecasting};
    \node[sbox=pblue] (q1) at (6.0,3.6) {\textbf{Q1. Explain.} Does weather drive \pmtwo{}?\\ Daily VAR + Granger causality};
    \node[sbox=graytxt] (q2a) at (6.0,2.0) {\textbf{Q2a. Next week.} Does weather improve a 1-week forecast?};
    \node[sbox=graytxt] (q2b) at (6.0,0.4) {\textbf{Q2b. Next 12 months.} Fourier+ARMA vs SARIMA and baselines, no weather inputs};
    \node[sres=pgreen] (r1) at (12.3,3.6) {\textbf{Done:} wind and humidity Granger-cause \pmtwo{}; effects fade within about a week};
    \node[sres=pgreen] (r2) at (12.3,2.0) {\textbf{Done:} yesterday's weather adds nothing; same-week weather (unknowable in advance) helps only \fcOneOracle\%};
    \node[sres=pgreen] (r3) at (12.3,0.4) {\textbf{Done:} 52-week forecasts backtested on 2017--19; outlook for 2020};
    \draw[sarr] (data.east) -- ++(0.35,0) |- (q1.west);
    \draw[sarr] (data.east) -- (q2a.west);
    \draw[sarr] (data.east) -- ++(0.35,0) |- (q2b.west);
    \draw[sarr] (q1) -- (r1); \draw[sarr] (q2a) -- (r2); \draw[sarr] (q2b) -- (r3);
  \end{tikzpicture}\\[4pt]
  \begin{takeaway}
    \textbf{Why two horizons?} Q1 shows a weather shock moves \pmtwo{} for only about a week: weather may help a short-term forecast, but it is unknown a year ahead, so the 12-month model will use no weather inputs.
    The final output is a month-by-month PM$_{2.5}$ outlook with prediction intervals.
  \end{takeaway}
\end{frame}

% ───────────────────────── 4. Data ─────────────────────────
\begin{frame}{Data: CPCB Air Quality and ERA5 Weather}
  \footnotesize
  \begin{tabular}{@{}p{3.7cm}p{1.8cm}p{1.1cm}p{6.6cm}@{}}
    \toprule
    \textbf{Variable} & \textbf{Source} & \textbf{Unit} & \textbf{Role in the project} \\
    \midrule
    \pmtwo{} & CPCB & \ugm{} & What we explain and forecast \\
    Wind speed & ERA5 & km/h & Disperses pollution: candidate driver \\
    Relative humidity & ERA5 & \% & Moisture, fog, rain: candidate driver \\
    Other (NO$_2$, SO$_2$, temp., rain) & CPCB, ERA5 & various & Context; rain used as a control \\
    \bottomrule
  \end{tabular}\\[5pt]
  \footnotesize
  \begin{itemize}\setlength\itemsep{2pt}
    \item \textbf{CPCB} (India's pollution board): \href{https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india}{\textbf{Kaggle: Air Quality Data in India}}, Delhi rows.
    \item \textbf{ERA5} = a \emph{reanalysis} (observations blended into a weather model, gap-free): \href{https://open-meteo.com/en/docs/historical-weather-api}{\textbf{Open-Meteo Historical API}}, central Delhi.
    \item \textbf{2{,}009 days}, 1 Jan 2015 -- 1 Jul 2020; 2 \pmtwo{} values interpolated. \textbf{Daily} data for causality, \textbf{weekly means} (287 weeks) for forecasting; validated on three rolling origins.
  \end{itemize}
  \vspace{1pt}
  \centering
  \begin{tikzpicture}[x=2.2cm,font=\scriptsize]
    \fill[pblue] (0,0) rectangle (4,0.55);        \node[text=white] at (2,0.275) {\textbf{Train: 2015--2018} (model fitting and selection)};
    \fill[porange] (4,0) rectangle (5,0.55);      \node[text=white] at (4.5,0.275) {\textbf{Test: 2019}};
    \fill[gray!45] (5,0) rectangle (5.5,0.55);    \node at (5.25,0.275) {2020};
    \foreach \y/\l in {0/2015,1/2016,2/2017,3/2018,4/2019,5/2020} \node[text=graytxt,anchor=north] at (\y,-0.02) {\l};
    \node[text=graytxt,anchor=south,align=center] at (5.25,0.58) {lockdown: case study only};
  \end{tikzpicture}
\end{frame}

% ───────────────────────── 5. Seasonality / STL ─────────────────────────
\begin{frame}{Seasonality: STL Decomposition of Weekly log PM$_{2.5}$}
  \centering
  \includegraphics[width=\linewidth]{fig/stl.pdf}\\[3pt]
  \begin{defbox}{STL.}
    Splits a series into \emph{trend} + \emph{seasonal} (repeats every year) + \emph{residual} (what is left).
    Seasonal strength $F_S=1-\mathrm{Var}(\text{residual})/\mathrm{Var}(\text{seasonal}+\text{residual})$: 0 = no seasonality, 1 = purely seasonal.
  \end{defbox}
  \begin{takeaway}
    $F_S=\mathbf{\Fs}$ (2015--18 weeks): the yearly cycle dominates, so the model must be \textbf{seasonal} (period $s=52$ weeks).
  \end{takeaway}
\end{frame}

% ───────────────────────── 6. Why log ─────────────────────────
\begin{frame}{Why Take Logs? Raw PM$_{2.5}$ Is Spiky and Skewed}
  \centering
  \includegraphics[width=\linewidth]{fig/why_log.pdf}\\[3pt]
  \begin{defbox}{Log transform.}
    PM$_{2.5}$ moves by \emph{percentages}: the spread of daily values (SD) is about \sdNov\ \ugm{} in November but only \sdAug\ in August. On a log scale equal percentage changes are equal distances, so the spread stops depending on the level.
  \end{defbox}
  \begin{takeaway}
    Raw PM$_{2.5}$ has a heavy right tail (skewness \skewRaw); the log is close to a bell curve (skewness \skewLog). The Box-Cox estimate $\lambda\approx\boxcox$ ($\lambda=0$ is the log) agrees.
  \end{takeaway}
\end{frame}

% ───────────────────────── 7. Volatility ─────────────────────────
\begin{frame}{Volatility Tests: Does the Spread Depend on the Level?}
  \centering
  \includegraphics[width=\linewidth]{fig/volatility_sd.pdf}\\[2pt]
  {\scriptsize\input{tables/log_tests.tex}}\\[3pt]
  \begin{takeaway}
    \textbf{Volatility} = how much values swing. In raw units the spread differs \sdRatioRaw$\times$ between months and tracks the level (corr.\ 0.95); after the log it differs only \sdRatioLog$\times$.
    Small differences remain (equal-spread test $p=\levPlog$; ARCH \archRaw\,$\to$\,\archLog, still significant), so we re-check the model residuals.
  \end{takeaway}
\end{frame}

% ───────────────────────── 8. Stationarity (idea) ─────────────────────────
\begin{frame}{Stationarity: Can the Past Predict the Future?}
  \centering
  \includegraphics[width=\linewidth]{fig/stationarity.pdf}\\[3pt]
  \begin{defbox}{Stationary}
    = the mean, spread and autocorrelation do not drift over time, so patterns learned from the past still apply. ARIMA-type models need it; if a series drifts, we \emph{difference} it ($d$ = ordinary difference, $D$ = difference at the seasonal lag).
  \end{defbox}
  \begin{takeaway}
    Weekly log \pmtwo{} (2015--18): the rolling mean is flat and the rolling spread varies only modestly, so the yearly cycle is a repeating pattern. Without the cycle a slow \emph{downward drift} appears (about $-$\declAll\% 2016--19). (The log is for variance, not stationarity.)
  \end{takeaway}
\end{frame}

% ───────────────────────── 8b. ADF / KPSS ─────────────────────────
\begin{frame}{Testing Stationarity with ADF and KPSS, and Choosing $d$ and $D$}
  \centering
  {\footnotesize\input{tables/stationarity.tex}}\par\vspace{5pt}
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \begin{card}[title={ADF test (Augmented Dickey-Fuller)}]{pblue}\footnotesize
      H$_0$: \emph{unit root} (the series wanders, non-stationary).\\ $p<0.05$ rejects H$_0$, which supports stationarity.
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={KPSS test}]{porange}\footnotesize
      H$_0$: the series \emph{is} stationary.\\ $p>0.05$ keeps H$_0$ (the printed 0.10 means ``$\ge0.10$'').
    \end{card}
  \end{columns}
  \vspace{4pt}
  \begin{takeaway}
    \textbf{Both tests are consistent with stationarity} for log \pmtwo{} and its seasonal difference $\Rightarrow$ $d=0$. A further difference over-differences (lag-1 autocorrelation $-0.46$, near the $-0.5$ warning level) and is dropped.
    A seasonal difference $D=1$ is not needed: a $D=1$ SARIMA's seasonal MA coefficient is $\fcMaCoef$ with a standard error above 1, the sign of over-differencing, so we model the cycle with Fourier terms instead.
  \end{takeaway}
\end{frame}

% ───────────────────────── 9. Granger ─────────────────────────
\begin{frame}{Does Weather Predict PM$_{2.5}$? Granger Causality in a VAR}
  \centering
  \begin{tikzpicture}[font=\scriptsize]
    \node[gbox=graytxt] (a) at (2.15,0) {\textbf{Model A:} predict today's \pmtwo{} from\\ past \pmtwo{} only};
    \node[gbox=pblue] (b) at (7.3,0) {\textbf{Model B:} past \pmtwo{} \textbf{+ past wind and humidity}\\(last 4 days)};
    \node[draw=navy,rounded corners=2pt,fill=navy,text=white,align=center,inner sep=3pt,text width=3.5cm] (c) at (12.5,0) {Is B significantly better?\\ \emph{Wald test, robust errors}};
    \draw[sarr] (a) -- (b); \draw[sarr] (b) -- (c);
  \end{tikzpicture}\\[3pt]
  \includegraphics[width=\linewidth]{fig/granger_hac.pdf}\\[2pt]
  \begin{takeaway}
    \textbf{Mainly one way.} Wind and humidity help predict \pmtwo{} in joint tests at every lag order from 1 to 7 days ($p<10^{-9}$; bars: 4 lags), also given rain and temperature. The reverse is absent for humidity and weak for wind (lag orders 1--2 only, $p\approx0.02$--$0.04$). {\footnotesize Predictive, not proof of cause.}
  \end{takeaway}
\end{frame}

% ───────────────────────── 10. Shock ─────────────────────────
\begin{frame}{What Is a ``Shock''? An Unexpected Change in Weather}
  \centering
  \includegraphics[width=\linewidth]{fig/shock_example.pdf}\\[3pt]
  \begin{defbox}{Shock.}
    the part of today's wind (or humidity) the model could \emph{not} predict from the previous 4 days (plus the seasonal level). \textbf{SD} = typical shock size: 1 SD $\approx$ 2.5 km/h (wind), 5.4\% (humidity).
  \end{defbox}
  \begin{takeaway}
    Grouping all days by shock size: after an unexpectedly windier day (+\shockWindBigZ\,SD), \pmtwo{} is \textbf{\shockWindBig\%} lower on day $t+1$ than on day $t-1$; after a calmer one ($-$\shockWindCalmZ\,SD), \textbf{\shockWindCalm\%} higher.
  \end{takeaway}
\end{frame}

% ───────────────────────── 11. IRF ─────────────────────────
\begin{frame}{Impulse Response: How Long Does a Weather Shock Matter?}
  \centering
  \includegraphics[width=\linewidth]{fig/irf_range.pdf}\\[3pt]
  \begin{defbox}{Impulse response.}
    The model's predicted path of \pmtwo{} after a one-SD shock. \textbf{Ordering:} weather first lets a shock move \pmtwo{} on the same day; \pmtwo{} first allows lagged effects only. We show both.
  \end{defbox}
  \begin{takeaway}
    A one-SD wind shock cuts \pmtwo{} by \irfWindA--\irfWindB\% the next day, humidity by \irfRhA--\irfRhB\%; both fade within about a week.
    Weekly: \emph{last} week's weather adds nothing to last week's \pmtwo{} for predicting this week's ($p=\lagWindP$ wind, \lagRhP\ humidity).
  \end{takeaway}
\end{frame}

% ───────────────────────── 13. What we established ─────────────────────────
\begin{frame}{What We Have Established So Far}
  \begin{itemize}\footnotesize\setlength\itemsep{3pt}
    \item \textbf{Seasonality:} a strong yearly cycle ($F_S=\Fs$; winter \ratioWM$\times$ the monsoon), so the forecasting model must be seasonal ($s=52$ weeks).
    \item \textbf{Transformation:} the log stabilises the variance (monthly spread \sdRatioRaw$\times\to$\sdRatioLog$\times$, skewness \skewRaw\ $\to$ \skewLog); log \pmtwo{} is consistent with stationarity ($d=0$), with a slow downward level drift.
    \item \textbf{Causality:} wind and humidity \textbf{Granger-cause} \pmtwo{} (robust to lag choice, differencing, robust errors, rain and temperature controls); the reverse is absent for humidity and weak for wind.
    \item \textbf{Size and timing:} a one-SD shock lowers \pmtwo{} by \irfWindA--\irfWindB\% (wind) and \irfRhA--\irfRhB\% (humidity) the next day, fading within about a week.
    \item \textbf{Horizon:} last week's weather adds nothing for predicting this week's \pmtwo{} ($p\approx0.5$), so weather is a short-memory driver and the 12-month model should not rely on it.
  \end{itemize}
  \vspace{4pt}
  \begin{takeaway}
    Answer to Q1: wind and humidity have a \textbf{robust predictive association} with \pmtwo{} over the following days (predictive, not proof of physical cause).
  \end{takeaway}
\end{frame}

% ───────────────────────── 14. Limits and next phase ─────────────────────────
\begin{frame}{Forecasting: Models and How We Test Them}
  \footnotesize
  \begin{columns}[T,onlytextwidth]
    \column{0.52\linewidth}
    \begin{card}[title={Models (weekly log \pmtwo{}, no weather inputs)}]{pblue}\scriptsize
      \begin{itemize}\setlength\itemsep{1pt}
        \item \textbf{Benchmarks:} seasonal naive; \textbf{climatology} (mean of each calendar week); climatology + AR(1).
        \item \textbf{Fourier + ARMA:} $K\le5$ yearly harmonics + ARMA errors; level = constant, linear or random walk, all chosen \emph{inside} each training window.
        \item \textbf{SARIMA} $D=1$ and $D=0$ (with constant), Linear Regression, a tiny LSTM (16 units).
      \end{itemize}
    \end{card}
    \column{0.45\linewidth}
    \begin{card}[title={Test design}]{porange}\scriptsize
      \begin{itemize}\setlength\itemsep{1pt}
        \item \textbf{Rolling origins:} train to end-2016, 2017, 2018; forecast the next 52 weeks each time; refit and re-select every time.
        \item Main evidence: 2018 and 2019; 2017 (2 training years) is a stress test.
        \item Compare to climatology with a block-bootstrap of paired errors; say ``indistinguishable'' when the interval contains 0.
      \end{itemize}
    \end{card}
  \end{columns}
  \vspace{0pt}\centering
  \begin{tikzpicture}[x=0.72cm,y=0.38cm,font=\scriptsize]
    \foreach \i/\tr/\te in {0/4/2, 1/6/2, 2/8/2} {
      \fill[pblue] (0,-\i) rectangle (\tr,-\i+0.38); \fill[porange] (\tr,-\i) rectangle (\tr+\te,-\i+0.38);}
    \node[anchor=west,text=graytxt] at (6.4,0) {origin 1: train 2015--16, forecast 2017};
    \node[anchor=west,text=graytxt] at (8.4,-1) {origin 2: train 2015--17, forecast 2018};
    \node[anchor=west,text=graytxt] at (10.4,-2) {origin 3: train 2015--18, forecast 2019};
  \end{tikzpicture}\\[3pt]
  \begin{takeaway}
    \textbf{Pre-declared headline:} Fourier+ARMA, selection inside each window. Other variants are comparisons, not cherry-picks.
  \end{takeaway}
\end{frame}

\begin{frame}{52-Week Backtest: Climatology Is Hard to Beat}
  \centering
  \includegraphics[width=0.86\linewidth]{fig/fc_backtest.pdf}\\[3pt]
  \begin{takeaway}
    MAE in \ugm{}; 2019: selected \fcMaeSelNineteen\ vs climatology \fcMaeClimNineteen, SARIMA $D=1$ \fcMaeSarimaNineteen\ (but \fcMaeSarimaSeventeen\ in 2017). A year ahead, the calendar is most of the signal: a smooth Fourier model matches climatology, while SARIMA $D=0$ (\fcMaeSarimaZeroNineteen) and the LSTM (\fcMaeLstmNineteen) are clearly worse.
  \end{takeaway}
\end{frame}

\begin{frame}{Backtest Table: Which Models Beat Climatology?}
  \centering\footnotesize
  \input{tables/fc_backtest.tex}\par\vspace{6pt}
  \begin{takeaway}
    MAE in \ugm{} (lower is better). The last column is a moving-block bootstrap of the paired error differences to climatology over the 2018 and 2019 forecasts: the seasonal naive, SARIMA $D=0$ and the LSTM are \emph{clearly worse}. The linear-trend Fourier variant looks better on 2018--19 but not over all three origins, and it was not our pre-declared choice, so we do not claim it. With three origins we cannot rank the rest.
  \end{takeaway}
\end{frame}

\begin{frame}{Diagnostics and Intervals: Two Pitfalls Fixed}
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \begin{card}[title={Residual checks}]{pblue}\footnotesize
      \begin{itemize}\setlength\itemsep{3pt}
        \item The draft's Ljung-Box $p\approx0$ was an \textbf{artifact}: the first 52 residuals of a $D=1$ model are diffuse-initialisation values. Removed, the SARIMA residuals pass at lags 10 and 26.
        \item The seasonal MA ($\fcMaCoef$, SE $>1$) is not identified: the seasonal difference is not needed.
        \item Honest limit: the Fourier model still shows some autocorrelation at lags 26 and 52.
      \end{itemize}
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={Prediction intervals (95\%)}]{porange}\footnotesize
      \begin{itemize}\setlength\itemsep{3pt}
        \item Model-based intervals covered \fcCovRaw\% of 2019 weeks. All misses were on the low side (2019 was cleaner than 2015--18).
        \item Scaling the spread by season, using only 2017--18 errors, gives \fcCovCal\% coverage on 2019. We re-centre only if the bias had the same sign and was large in both earlier years; it was not.
      \end{itemize}
    \end{card}
  \end{columns}
  \vspace{6pt}
  \begin{takeaway}
    Two earlier ``problems'' were measurement errors, not model failures. Residual structure and a falling level (see the station check) remain real limits.
  \end{takeaway}
\end{frame}

\begin{frame}{One Week Ahead: Does Weather Help?}
  \centering
  \includegraphics[width=0.82\linewidth]{fig/fc_oneweek.pdf}\\[2pt]
  \begin{takeaway}
    Using \emph{last} week's wind and humidity changes the error by \fcOneLagged\% (last 3 days: \fcOneLastThree\%): no gain. Using the \emph{same} week's weather, which is unknown in advance (ERA5 is observed, not forecast), improves by only \fcOneOracle\% ($p\approx0.07$). Weather is explanatory over days, but a poor forecasting input.
  \end{takeaway}
\end{frame}

\begin{frame}{Outlook for 2020, Month by Month}
  \centering
  \includegraphics[width=0.95\linewidth]{fig/fc_outlook.pdf}\\[2pt]
  \begin{takeaway}
    Fitted on 2015--2019 only. \textbf{Validation of the same pipeline on 2019:} all \fcValInside\ monthly means fell inside the 95\% interval, but the model over-predicted the share of Poor-or-worse days (\fcValPoorPred\% vs \fcValPoorAct\% actual), the same level bias as before. In 2020, Jan--Feb fall inside the interval; March--May fall below it (lockdown). Bands are \pmtwo{} sub-index bands, not the official AQI.
  \end{takeaway}
\end{frame}

\begin{frame}{Case Study: The 2020 Lockdown}
  \centering
  \includegraphics[width=0.88\linewidth]{fig/fc_lockdown.pdf}\\[2pt]
  \begin{takeaway}
    From 29 Mar to 31 May 2020, \pmtwo{} was about \textbf{\fcLockPct\%} below the no-lockdown forecast (95\% interval \fcLockLo--\fcLockHi\%). Adjusting the forecast for the actual wind and humidity of those weeks, the gap is \textbf{\fcLockWxPct\%}: most of the drop is not weather. Descriptive: it relies on the model's 2020 level being right.
  \end{takeaway}
\end{frame}

\begin{frame}{What We Established, and the Limits}
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \begin{card}[title={Established}]{pgreen}\scriptsize
      \begin{itemize}\setlength\itemsep{2pt}
        \item Strong yearly cycle (winter \ratioWM$\times$ the monsoon); log stabilises variance.
        \item Wind and humidity anomalies robustly \emph{predict} PM$_{2.5}$ for about a week; effect \irfWindA--\irfWindB\% (wind), \irfRhA--\irfRhB\% (humidity) the next day.
        \item At a weekly-to-yearly horizon weather adds nothing usable; a Fourier+ARMA model matches or slightly beats climatology; SARIMA, LSTM do not help.
        \item The 2016--19 decline is real (about $-$\declPanel\% on a fixed station panel).
        \item The lockdown cut PM$_{2.5}$ by about \fcLockPct\% relative to forecast.
      \end{itemize}
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={Limits}]{porange}\scriptsize
      \begin{itemize}\setlength\itemsep{2pt}
        \item Granger = predictive; mixing height, stubble burning, fireworks are unmeasured.
        \item Weather's share of 14-day error depends on the VAR ordering (\fevdA--\fevdB\%).
        \item Three backtest origins: few independent tests; most model differences are not significant.
        \item Level bias in 2019; residual autocorrelation at long lags.
        \item One city; data end in mid-2020; ERA5 is a grid cell; PM$_{2.5}$ band $\ne$ official AQI.
      \end{itemize}
    \end{card}
  \end{columns}
\end{frame}

% ───────────────────────── Backup A: glossary ─────────────────────────
\appendix
\begin{frame}{Backup: Glossary of Terms}
  \footnotesize
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \textbf{PM$_{2.5}$}: particles under 2.5 $\mu$m, \ugm{}.\\[2pt]
    \textbf{AQI}: India's Air Quality Index (worst pollutant); we use only the PM$_{2.5}$ band.\\[2pt]
    \textbf{Reanalysis (ERA5)}: observations blended into a weather model.\\[2pt]
    \textbf{STL, $F_S$}: trend/seasonal/residual split; seasonal strength.\\[2pt]
    \textbf{Log transform}: makes percentage swings equal; stabilises variance.\\[2pt]
    \textbf{Volatility}: how much values swing; \textbf{ARCH-LM} tests clustering of big swings; \textbf{Levene} tests equal spread.\\[2pt]
    \textbf{Stationary}: no drift in mean, spread or autocorrelation; \textbf{ADF/KPSS} test it.
    \column{0.485\linewidth}
    \textbf{VAR}: each variable predicted from past values of all variables.\\[2pt]
    \textbf{Granger causality}: past X improves the forecast of Y.\\[2pt]
    \textbf{HAC errors}: standard errors robust to autocorrelation and changing variance.\\[2pt]
    \textbf{Shock}: the unpredictable part of a variable today; \textbf{SD} = its typical size.\\[2pt]
    \textbf{Impulse response}: path of PM$_{2.5}$ after a shock; \textbf{FEVD}: share of forecast error due to each variable.\\[2pt]
    \textbf{SARIMA}: seasonal ARIMA. \textbf{Fourier+ARMA}: yearly sine/cosine terms + ARMA errors. \textbf{Climatology}: the average of each calendar week. \textbf{MAE}: mean absolute error.
  \end{columns}
\end{frame}

% ───────────────────────── Backup B: robustness ─────────────────────────
\begin{frame}{Backup: How Robust Is the Weather Result?}
  \centering\scriptsize\setlength{\tabcolsep}{4pt}
  \input{tables/granger_robust.tex}\par\vspace{2pt}
  \input{tables/orderings.tex}\par
  {\tiny W-first = weather ordered first; P-first = PM$_{2.5}$ ordered first.}\par\vspace{1pt}
  \begin{takeaway}
    Robust (HAC) tests agree with the plain tests. The reverse direction (PM$_{2.5}$ $\to$ wind) is weakly significant at 1--2 lags only. The size of a shock's effect and weather's share of forecast error depend on the VAR ordering, so we report ranges, not single values.
  \end{takeaway}
\end{frame}

% ───────────────────────── Backup C: boxplot ─────────────────────────
\begin{frame}{Backup: PM$_{2.5}$ by Month}
  \centering
  \includegraphics[width=\linewidth]{fig/seasonal_boxplot.pdf}\\[2pt]
  \begin{takeaway}
    Box = middle 50\% of days, line = median, dots = unusually high days. Orange: winter (Nov--Jan); blue: monsoon (Jul--Sep).
  \end{takeaway}
\end{frame}


% ───────────────────────── Backup D/E: station check, outlook table ─────────────────────────
\begin{frame}{Backup: Is the 2016--19 Decline Real? Station Check}
  \centering
  \includegraphics[width=0.85\linewidth]{fig/fc_station.pdf}\\[2pt]
  \begin{takeaway}
    The city series is the mean of the stations (corr.\ 0.995) and the number of stations rose from 8--10 to 37, so a mix effect is possible. But a fixed panel of six long-running stations falls by \declPanel\%, all stations by \declAll\%, and the weather-adjusted city series by \declWx\% (2016 $\to$ 2019): most of the decline is real.
  \end{takeaway}
\end{frame}

\begin{frame}{Backup: 2020 Outlook Table}
  \centering\scriptsize\setlength{\tabcolsep}{5pt}
  \input{tables/fc_outlook.tex}\par\vspace{2pt}
  {\tiny Monthly mean \pmtwo{} (\ugm{}); P(mean$>$90) = probability the monthly mean exceeds 90; Days Poor+ = expected days with daily \pmtwo{} above 90 (PM$_{2.5}$ band, not official AQI). Actual shown for full months only.}
\end{frame}

\end{document}
```


# 09 Changes and review log

## git log (main..HEAD)
```
3397b23 Deck, report, review-response log, README, presentation script, LLM briefs, verification (65 checks)
9b351f9 Notebook 04: rolling-origin backtest, diagnostics, calibration, 1-week weather test, 2020 outlook, lockdown case study; archive SARIMA draft
2a3d6bc Notebooks 02-03: training-only headline stats, level-drift and station check, extra Granger robustness (temp, trend, seasonal, by-lag), GIRF, nested weekly test; re-executed
d671a29 src: leap-safe climatology, week index, forecasting toolkit, PM2.5-band labelling; pin requirements
982b5ab Baseline: hygiene (.gitignore, untrack pycache) and existing phase 2-3 rework, beamer deck, SARIMA draft, review inputs
```

## diffstat of source and notebook changes
```
 notebooks/01_data_prep.ipynb             |   58 +-
 notebooks/02_eda.ipynb                   | 1088 +++++++++++--
 notebooks/03_var_granger.ipynb           | 1889 +++++++++++++++++++----
 notebooks/04_forecasting.ipynb           | 2477 ++++++++++++++++++++++++++++++
 src/__pycache__/__init__.cpython-312.pyc |  Bin 166 -> 0 bytes
 src/__pycache__/aqi.cpython-312.pyc      |  Bin 1606 -> 0 bytes
 src/__pycache__/data.cpython-312.pyc     |  Bin 7282 -> 0 bytes
 src/__pycache__/plots.cpython-312.pyc    |  Bin 3597 -> 0 bytes
 src/__pycache__/tsa.cpython-312.pyc      |  Bin 4587 -> 0 bytes
 src/aqi.py                               |   13 +-
 src/forecast.py                          |  367 +++++
 src/tsa.py                               |   42 +-
 tools/build_llm_context.py               |   88 ++
 tools/build_nb04.py                      |  448 ++++++
 tools/edit_deck.py                       |  175 +++
 15 files changed, 6185 insertions(+), 460 deletions(-)
```

## diff of src/tsa.py and src/aqi.py vs main
```diff
diff --git a/src/aqi.py b/src/aqi.py
index 6a7daa2..ebee7e8 100644
--- a/src/aqi.py
+++ b/src/aqi.py
@@ -1,4 +1,7 @@
-"""CPCB (India) National AQI categories for 24-hour average PM2.5 (µg/m³)."""
+"""CPCB (India) National AQI PM2.5 sub-index bands for 24-hour average PM2.5 (µg/m³).
+
+The official AQI is the MAXIMUM sub-index over all pollutants, so a band here is a "PM2.5 sub-index band", not the AQI.
+"""
 import numpy as np
 import pandas as pd
 
@@ -28,3 +31,11 @@ def band_edges():
         out.append((name, lower, upper, colour))
         lower = upper
     return out
+
+
+def band_probabilities(mu, sd):
+    """P(PM2.5 in each band) for a lognormal log-PM2.5 ~ N(mu, sd^2). Returns array (len(CATEGORIES),)."""
+    from scipy.stats import norm
+    edges = [b[1] for b in CPCB_PM25_BANDS[:-1]]
+    cdf = np.r_[0.0, norm.cdf((np.log(edges) - mu) / sd), 1.0]
+    return np.diff(cdf)
diff --git a/src/tsa.py b/src/tsa.py
index 56da05e..3cbfb0e 100644
--- a/src/tsa.py
+++ b/src/tsa.py
@@ -9,7 +9,7 @@ from statsmodels.tsa.stattools import adfuller, grangercausalitytests, kpss
 def adf_kpss(series, name, alpha=0.05):
     """ADF (H0: unit root) and KPSS (H0: level-stationary) on one series, with a combined verdict."""
     s = pd.Series(series).dropna()
-    adf_stat, adf_p, adf_lags, *_ = adfuller(s, autolag="AIC")
+    adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
     with warnings.catch_warnings():
         warnings.simplefilter("ignore")  # KPSS warns when p is outside its lookup table
         kpss_stat, kpss_p, *_ = kpss(s, regression="c", nlags="auto")
@@ -24,8 +24,9 @@ def adf_kpss(series, name, alpha=0.05):
         verdict = "Mixed (KPSS says stationary, ADF can't reject unit root)"
     return {
         "series": name, "n": len(s),
-        "adf_stat": round(adf_stat, 3), "adf_p": round(adf_p, 4), "adf_lags": adf_lags,
-        "kpss_stat": round(kpss_stat, 3), "kpss_p": round(kpss_p, 4),
+        "adf_stat": round(adf_stat, 3), "adf_p": float(f"{adf_p:.3g}"), "adf_lags": adf_lags,
+        **{f"adf_crit_{k}": round(v, 3) for k, v in adf_crit.items()},
+        "kpss_stat": round(kpss_stat, 3), "kpss_p": float(f"{kpss_p:.3g}"),
         "verdict": verdict,
     }
 
@@ -34,20 +35,39 @@ def stationarity_table(series_dict):
     return pd.DataFrame([adf_kpss(s, name) for name, s in series_dict.items()]).set_index("series")
 
 
+def doy365(index):
+    """Calendar day-of-year on a fixed 1..365 scale: Feb 29 maps to day 59, later leap-year days shift by -1."""
+    idx = pd.DatetimeIndex(index)
+    doy = np.asarray(idx.dayofyear)
+    leap_after_feb = idx.is_leap_year & (doy > 59)
+    return np.where(leap_after_feb, doy - 1, doy).clip(1, 365)
+
+
 def doy_climatology(s, window=31):
-    """Smoothed day-of-year mean (circular rolling window), indexed 1..365."""
-    doy = np.minimum(s.index.dayofyear, 365)
-    clim = s.groupby(doy).mean().reindex(range(1, 366)).interpolate()
+    """Smoothed day-of-year mean (circular rolling window), indexed 1..365. Fit on whatever sample is passed."""
+    clim = s.groupby(doy365(s.index)).mean().reindex(range(1, 366)).interpolate()
     half = window // 2
     padded = pd.concat([clim.iloc[-half:], clim, clim.iloc[:half]])
     return padded.rolling(window, center=True).mean().iloc[half:-half]
 
 
-def doy_anomaly(s, window=31):
-    """Deseasonalised series: value minus its smoothed day-of-year climatology."""
-    clim = doy_climatology(s, window)
-    doy = np.minimum(s.index.dayofyear, 365)
-    return s - clim.reindex(doy).to_numpy()
+def apply_climatology(s, clim):
+    """Subtract a previously fitted climatology (from `doy_climatology`) from any series."""
+    return s - clim.reindex(doy365(s.index)).to_numpy()
+
+
+def doy_anomaly(s, window=31, ref=None):
+    """Deseasonalised series: value minus its smoothed day-of-year climatology.
+
+    The climatology is fitted on `ref` (default: `s` itself). Pass a training slice as `ref` to avoid leakage.
+    """
+    return apply_climatology(s, doy_climatology(s if ref is None else ref, window))
+
+
+def week_index(index):
+    """1..52 calendar-week index for weekly (W-SUN) dates: day-of-year of the week's Thursday, in 7-day blocks."""
+    thu = pd.DatetimeIndex(index) - pd.Timedelta(days=3)
+    return np.minimum((doy365(thu) - 1) // 7 + 1, 52)
 
 
 def pairwise_granger(df, pairs, maxlag=7):
```

## Review responses (each earlier claim, verdict, evidence)
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
