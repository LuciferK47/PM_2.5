# 00 Verification pack (round 3, final check): how to re-check everything
Project: Delhi PM2.5 time-series study (MATH F428), branch `phase4-final`. Two earlier audits (Gemini, GPT) recomputed the numbers and found real bugs; those were fixed and everything was re-run. **Your job now: check that the fixes are correct, that nothing new broke, and that every statement is supported.**

## What to do
1. Recompute the claims below from the raw data in files 05 and 06. Report every mismatch.
2. Read the code (file 01, notebooks 02-03; 03 for notebook 04, 07 for the checker) for leakage, alignment errors, wrong formulas. Pay special attention to the fixes: `lstm_window` and `_lstm_recursive`, `daily_paths`, `block_bootstrap_diff` (circular, per fold), `linreg` sd, `_best_by_aicc`, `week_offsets_by_month`.
3. Compare every number in the report/deck text (file 08) with the tables (file 04).
4. Decide which conclusions are still over-claims. Do not just agree; give file and number.

## Files (10)
| File | Content |
|---|---|
| 00_VERIFY_README.md | this file, instructions, claims ledger |
| 01_src_code.md | full source of src/ |
| 02_notebooks_02_03_code.md | EDA and VAR/Granger notebooks: code plus printed output |
| 03_notebook_04_code.md | forecasting notebook: code plus printed output |
| 04_all_results_tables.md | every results/*.csv except raw forecasts, and the key_numbers json |
| 05_raw_forecasts_and_weekly.md | weekly table (full precision, 287 rows), raw 52-week backtest forecasts, one-step forecasts, 2020 weekly forecasts |
| 06_daily_data_and_stations.md | the full daily table (PM2.5 and weather) and per-station-per-year PM2.5 summary |
| 07_checker_and_figure_code.md | verify_numbers.py (78 checks), make_figures.py, slide number macros |
| 08_report_and_deck_text.md | LaTeX source of the report and the deck |
| 09_changes_and_review_log.md | git history, source diffs, review log with Round 2 |

## Setup facts
Weekly W-SUN series, 287 weeks 2015-01-04 to 2020-06-28 (log of weekly mean PM2.5). Origins 2016-12-25, 2017-12-31, 2018-12-30, each forecasting 52 weeks (the 2017 fold ends 24 Dec 2017). Point forecast = exp(mu) (median); mean = exp(mu + sd^2/2). Authors' checker: 78/78 passed (a claim to test, not proof). Raw CPCB/ERA5 files are not included; the daily table in file 06 is the processed series.

## Output format
(i) numbers you reproduced with your values, (ii) mismatches, (iii) code bugs, (iv) over-claims, (v) prioritised fixes.

## Claims ledger (round 2: statements as they now stand)
| # | Claim | Evidence file | Recompute from |
|---|---|---|---|
| 1 | MAE 2017/18/19: selected Fourier+ARMA 31.5/23.4/25.7; climatology 31.0/21.8/27.8; SARIMA D=1 53.8/21.1/27.5; SARIMA D=0 44.9/42.8/44.1; LSTM 36.3/28.3/54.3 (rerun after the alignment fix); linear regression 35.9/20.0/24.9 | 04 fc_backtest_mae.csv | 05 backtest forecasts: mean abs(actual - exp(mu)) |
| 2 | Climatology = mean log PM2.5 by week index 1-52 over training years; seasonal naive = value 52 weeks earlier | 01 forecast.py | 05 weekly table |
| 3 | No model is significantly better than climatology (circular moving-block bootstrap, 8-week blocks, drawn within each fold): 2018-19 selected -0.2 [-2.9,+2.8], linear -2.9 [-6.1,+0.7]; seasonal naive, SARIMA D=0, LSTM worse; SARIMA D=1 worse over all three folds | 04 fc_loss_diff.csv | resample per-fold absolute-error differences |
| 4 | 2019 raw 95% coverage 90.4% (5 misses, all below), 2018 94.2% (2 below, 1 above), 2017 69.2% (10 below, 6 above) | 04 fc_backtest_metrics.csv | 05: share of actual in [exp(mu-1.96 sd), exp(mu+1.96 sd)] |
| 5 | Season rescaling (2017-18 errors): 2019 coverage 96.2% but width 125 -> 179 and Winkler 175 -> 193 (worse) | 04 fc_calibration_2019.csv | 05 + scale factors 1.334 (winter) / 1.422 |
| 6 | One-week MAE vs no-weather DHR: lagged -2.4%, last-3-days +0.7%, same-week oracle +6.9% (p 0.075/0.585/0.074) | 04 fc_oneweek.csv | 05 one-step forecasts (fc_oneweek_forecasts) |
| 7 | HAC Granger wind->PM2.5 p~6e-20, humidity ~4e-11 (4 lags, with rain+temp 9e-18, 7e-8); seasonal tests all p<1e-3; interactions p=0.20 (monsoon x humidity), 0.03 (winter x wind) | 04 granger_*.csv | 06 daily data (anomalies from doy climatology) |
| 8 | Weekly nested test: R2 0.1341 -> 0.1391, p = 0.515 | 04 weekly_lag_nested.csv | 05 weekly table |
| 9 | 2019 pipeline validation: 12/12 monthly means inside 95%; Poor-or-worse 55.1% predicted vs 45.2% actual | 04 fc_outlook_validation_2019_*.csv | 06 daily data (actual band counts) |
| 10 | Lockdown: 10 Sunday-ending weeks 29 Mar-31 May (cover 23 Mar-31 May); actual mean 48.7 vs model median 85.1 = -43% (95% -52 to -32); weather-adjusted -38%; pre-lockdown (5 Jan-22 Mar) model gap -11%; adjusted -35%; other level specs -43% to -51%; 2019 placebo -15% (95% -44 to +28) | 04 fc_lockdown*.csv | 05 lockdown weekly table (fc_weekly_2020) |
| 11 | June 2020 monthly mean 46.7 below its lower bound 48.7; Jan-Feb inside; Mar-Jun below | 04 fc_outlook_2020.csv | 06 daily data |
| 12 | Station panel: city series 2016->2019 -25%, fixed 6-station panel -20%, weather-adjusted -18%; stations reporting 10, 8, 17, 37, 37 | 04 station_check.csv | 06 station summary (per station-year mean and days) |
| 13 | Ljung-Box on SARIMA D=1 residuals: p~0 with the 52 diffuse residuals; without them 0.49/0.10/0.016 (lags 10/26/52); seasonal MA -0.988, SE 8.26 | 03 nb04 output | needs full-precision refit |
| 14 | SARIMA D=0 with/without constant (same orders/folds): 44.9/42.8/44.1 vs 76.9/61.0/92.1 | 04 fc_sarima_d0_constant.csv | refit |
| 15 | doy365 maps 29 Feb to day 59 and shifts later leap-year days by -1 | 01 tsa.py | read code |

## What the first-round audits already found and what was fixed (verify the fixes!)
LSTM calendar/anomaly misalignment (now one helper `lstm_window`, deterministic torch); verifier checked April-June against March-May intervals and skipped a persistence week; non-converged fits accepted in AICc search; daily band days and monthly means from different draws (now one set of daily paths whose weekly means equal the weekly paths exactly); bootstrap joined forecast years (and a first fix without wrap-around biased the interval: now circular within each fold); constant predictive sd for linear regression/LSTM (now horizon-specific); report claims (winter humidity bound, D=0 '39.7 to 30.6', June omission, over-claims). See file 09 (Round 2 table R1-R23).


# 01 Source code (src/)

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
    """Same week one year (52 weeks) earlier. sd = spread of 52-week log differences in the training data."""
    d52 = (y - y.shift(H)).dropna()
    return {"mu": y.iloc[-H:].to_numpy()[: len(idx)], "sd": np.full(len(idx), float(np.sqrt(np.mean(d52 ** 2))))}


def _clim(y):
    wk = week_index(y.index)
    c = y.groupby(wk).mean().reindex(range(1, 53)).interpolate(limit_direction="both")
    return c


def climatology(y, idx):
    """Mean log PM2.5 of each calendar week over the training years. sd = training residual sd around it."""
    c = _clim(y)
    resid = y - c.reindex(week_index(y.index)).to_numpy()
    sd = float(np.sqrt(np.mean(resid ** 2)))
    return {"mu": c.reindex(week_index(idx)).to_numpy(), "sd": np.full(len(idx), sd)}


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


def _fit(mod, maxiter=200):
    """Fit a statsmodels state-space model, silencing only its convergence / start-value warnings (they are checked
    explicitly through `converged`)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return mod.fit(disp=False, maxiter=maxiter)


def converged(res):
    return bool(getattr(res, "mle_retvals", {}).get("converged", True))


def _fit_dhr(y, K, p, q, trend):
    tr, d = TREND_SPECS[trend]
    return _fit(SARIMAX(y, exog=fourier(y.index, K), order=(p, d, q), trend=tr))


def _best_by_aicc(y, trend):
    """Lowest AICc over K=1..5 and the (p,q) grid; fits whose optimiser did not converge are rejected and counted."""
    best, rejected = None, 0
    for K, (p, q) in product(range(1, 6), PQ_GRID):
        try:
            r = _fit_dhr(y, K, p, q, trend)
            a = aicc(r)
        except Exception:  # noqa: BLE001
            rejected += 1
            continue
        if not converged(r) or not np.isfinite(a):
            rejected += 1
            continue
        if best is None or a < best[0]:
            best = (a, K, p, q, r)
    return None if best is None else (*best, rejected)


def select_dhr(y, inner=H):
    """Choose (K, p, q) by AICc within each trend type, then the trend type by validation on the last `inner` weeks
    of the training sample (so nothing after the training end is ever used)."""
    sub, val = y.iloc[:-inner], y.iloc[-inner:]
    scores, n_rej = {}, 0
    for trend in TREND_SPECS:
        b = _best_by_aicc(sub, trend)
        if b is None:
            continue
        _, K, p, q, r, rej = b
        n_rej += rej
        fc = r.get_forecast(inner, exog=fourier(val.index, K)).predicted_mean
        scores[trend] = float(np.abs(np.exp(val.to_numpy()) - np.exp(fc.to_numpy())).mean())
    trend = min(scores, key=scores.get)
    _, K, p, q, res, rej = _best_by_aicc(y, trend)
    return {"trend": trend, "K": K, "p": p, "q": q, "inner_mae": scores, "res": res,
            "n_rejected_nonconverged": n_rej + rej}


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
        res = _fit(SARIMAX(y, order=order, seasonal_order=sorder, trend=trend))
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
    """OLS on Fourier terms + linear time. The predictive sd includes parameter uncertainty, so it grows with the horizon:
    sd_h^2 = s^2 (1 + x_h' (X'X)^-1 x_h)."""
    import statsmodels.api as sm
    X = sm.add_constant(_design(y.index, K, y.index[0]), has_constant="add")
    m = sm.OLS(y.to_numpy(), X.to_numpy()).fit()
    Xf = sm.add_constant(_design(idx, K, y.index[0]), has_constant="add")
    pr = m.get_prediction(Xf.to_numpy())
    se_obs = np.sqrt(pr.se_mean ** 2 + m.scale)
    return {"mu": pr.predicted_mean, "sd": se_obs}


def lstm_window(z_hist, C_hist, lag):
    """Input window for predicting the step after the end of `z_hist`: the last `lag` anomalies, each next to the calendar
    features OF ITS OWN WEEK. `z_hist` and `C_hist` must be aligned row by row (same weeks). Used for training and forecasting."""
    assert len(z_hist) == len(C_hist) and len(z_hist) >= lag
    return np.c_[np.asarray(z_hist)[-lag:], np.asarray(C_hist)[-lag:]]


def _lstm_recursive(net, z_hist, C_hist, C_future, torch):
    """Recursive multi-step forecast; the calendar block grows by exactly one week per predicted week (aligned)."""
    zh, Ch, out = list(z_hist), [list(r) for r in C_hist], []
    lag = net.lag
    for j in range(len(C_future)):
        xin = torch.tensor(lstm_window(zh, Ch, lag)[None], dtype=torch.float32)
        nxt = float(net(xin))
        out.append(nxt)
        zh.append(nxt)
        Ch.append(list(C_future[j]))  # the predicted value belongs to week j of the future index
    return np.array(out)


def lstm(y, idx, lag=8, hidden=16, epochs=300, seed=0):
    """Tiny recursive one-step LSTM on weekly log-anomalies (vs training climatology) + calendar features.

    Predictive sd is horizon-specific: the spread of h-step recursive errors from in-sample origins (non-decreasing in h,
    capped at the training anomaly sd, which is the long-horizon limit)."""
    import torch
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
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
        X.append(lstm_window(z[:i], C[:i], lag))
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
    net.lag = lag
    opt = torch.optim.Adam(net.parameters(), lr=0.01, weight_decay=1e-3)
    for _ in range(epochs):
        opt.zero_grad()
        loss = torch.mean((net(X) - Y) ** 2)
        loss.backward()
        opt.step()
    with torch.no_grad():
        one_step_sd = float(torch.std(net(X) - Y))
        preds = _lstm_recursive(net, z, C, cal(idx), torch)
        # horizon-specific sd from in-sample recursive forecasts (every 4 weeks), in z units
        hmax = len(idx)
        errs = [[] for _ in range(hmax)]
        for o in range(lag, len(z) - 1, 4):
            steps = min(hmax, len(z) - o)
            p = _lstm_recursive(net, z[:o], C[:o], C[o:o + steps], torch)
            for h in range(steps):
                errs[h].append(z[o + h] - p[h])
        sd_z = np.empty(hmax)
        for h in range(hmax):
            sd_z[h] = np.sqrt(np.mean(np.square(errs[h]))) if len(errs[h]) >= 8 else np.nan
        sd_z = pd.Series(sd_z).ffill().fillna(one_step_sd).to_numpy()
        sd_z = np.minimum(np.maximum.accumulate(np.maximum(sd_z, one_step_sd)), max(1.0, one_step_sd))
    mu = c.reindex(week_index(idx)).to_numpy() + preds * sd_a
    return {"mu": mu, "sd": sd_z * sd_a}


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
    """Mean of (e_a - e_b) with a circular moving-block bootstrap 95% CI.

    e_a, e_b: lists of per-fold error arrays (absolute errors), or single arrays (one fold). Blocks are drawn WITHIN each fold
    (stratified), so no block joins one forecast year to another. Blocks wrap around inside a fold (circular), so every week
    is equally likely to be drawn; without wrapping, the first and last weeks are under-sampled and the interval is biased."""
    if not isinstance(e_a, (list, tuple)):
        e_a, e_b = [e_a], [e_b]
    ds = [np.asarray(a, float) - np.asarray(b, float) for a, b in zip(e_a, e_b)]
    rng = np.random.default_rng(seed)
    total = sum(len(d) for d in ds)
    means = np.empty(n)
    for r in range(n):
        s_ = 0.0
        for d in ds:
            L = len(d)
            nb = int(np.ceil(L / block))
            starts = rng.integers(0, L, nb)
            take = np.concatenate([d[(st + np.arange(block)) % L] for st in starts])[:L]
            s_ += take.sum()
        means[r] = s_ / total
    d_all = np.concatenate(ds)
    return float(d_all.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


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
    """Pool of complete within-week offset VECTORS (Mon..Sun) of log(daily) - log(weekly mean), keyed by the calendar month of
    the week's Thursday (training data only). Each vector satisfies mean(exp(offset)) = 1 exactly, so adding it to a weekly
    log-mean keeps that week's mean unchanged."""
    d = daily_pm25.dropna()
    wk_end = d.index + pd.to_timedelta((6 - d.index.weekday) % 7, unit="D")
    full = d.groupby(wk_end).transform("count") == 7
    d = d[full]
    wk_end = wk_end[full.to_numpy()]
    off = np.log(d) - np.log(d.groupby(wk_end).transform("mean"))
    vecs = off.groupby(wk_end).apply(lambda s: s.sort_index().to_numpy())
    thu = pd.DatetimeIndex(vecs.index) - pd.Timedelta(days=3)
    return {m: np.vstack(vecs[thu.month == m].to_list()) for m in range(1, 13)}


def daily_paths(paths, idx, pools, year, seed=2):
    """Daily PM2.5 paths for calendar `year`, coherent with the weekly paths.

    paths: weekly log-mean paths (len(idx), n_paths) for W-SUN weeks `idx`. For each week and path one whole offset vector is
    drawn from the pool of that week's month, so the 7 daily values of every simulated week average EXACTLY to the simulated
    weekly mean, and within-week day-to-day dependence is kept. Returns (days, values[n_days, n_paths])."""
    rng = np.random.default_rng(seed)
    n = paths.shape[1]
    idx = pd.DatetimeIndex(idx)
    allv = np.empty((len(idx) * 7, n))
    alld = []
    for w, end in enumerate(idx):
        pool = pools[(end - pd.Timedelta(days=3)).month]
        pick = pool[rng.integers(0, len(pool), n)]                  # (n, 7)
        allv[w * 7:(w + 1) * 7] = np.exp(paths[w][None, :] + pick.T)
        alld.extend(pd.date_range(end - pd.Timedelta(days=6), end, freq="D"))
    alld = pd.DatetimeIndex(alld)
    keep = alld.year == year
    return alld[keep], allv[keep]


def daily_band_days(days, vals):
    """Days per PM2.5 band per month for each path, from `daily_paths` output. Returns (n_paths, 12, 6)."""
    cat = np.searchsorted(band_edges(), vals, side="left")  # 0..5 (<=edge -> lower band)
    out = np.zeros((vals.shape[1], 12, 6))
    for m in range(12):
        sel = days.month == m + 1
        for b in range(6):
            out[:, m, b] = (cat[sel] == b).sum(axis=0)
    return out


def monthly_mean_paths(days, vals):
    """Monthly mean PM2.5 per path from the SAME daily paths used for the band counts. Returns (12, n_paths)."""
    out = np.full((12, vals.shape[1]), np.nan)
    for m in range(12):
        sel = days.month == m + 1
        if sel.any():
            out[m] = vals[sel].mean(axis=0)
    return out
```


# 02 Notebooks 02 and 03: code and printed output

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


# 03 Notebook 04: forecasting, code and printed output

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
| Seasonal naive | the value 52 weeks earlier (52 weeks, not the same calendar week in 53-week years) |
| Climatology | mean log PM2.5 of the same calendar week over the training years |
| Climatology + AR(1) | climatology plus an AR(1) on the weekly anomalies |
| Linear regression | OLS on 3 Fourier harmonics + a linear time trend (prediction interval includes parameter uncertainty, so it widens with the horizon) |
| LSTM (small) | 1 layer, 16 units, seeded and deterministic, recursive one-step on anomalies; each input row pairs the anomaly with the calendar features of **its own week** (an alignment bug in the first version was fixed); interval sd from in-sample recursive h-step errors. Small-data baseline only |
| Fourier+ARMA const / linear | dynamic harmonic regression (DHR): K=3 harmonics, AR(1) errors, constant or linear-trend level |
| **Fourier+ARMA (selected)** | K ∈ 1..5 and (p,q) by AICc inside each trend type (constant / linear / random-walk errors); the trend type chosen by validation on the *last training year*. The random-walk option makes the errors **ARIMA(p,1,q)**, so "ARMA" in the label covers both. Non-converged fits are rejected and counted. The procedure was fixed in the code before the final runs, but 2019 had been looked at in earlier iterations of the project, so it is not a pristine hold-out. |
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
Folds 2018 and 2019 are the main evidence (3 and 4 training seasons); 2017 (only 2 training years) is a stress test. Climatology is the model to beat. Each fold is 52 weeks starting the week after the origin (the 2017 fold ends 24 Dec 2017, not 31 Dec).

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
LSTM (small)             36.3  28.3  54.3          41.3        39.7
SARIMA D=0               44.9  42.8  44.1          43.5        43.9                          RMSE  logMAE  MAE_winter  MAE_other   bias  \
model                                                                  
Fourier+ARMA linear      40.28    0.23       46.53      16.80  -4.43   
Linear regression        40.83    0.24       47.40      17.01  -3.60   
SARIMA D=1               58.73    0.26       59.47      21.81 -18.24   
Climatology + AR(1)      38.26    0.25       40.05      20.01  -8.13   
Fourier+ARMA (selected)  39.45    0.24       45.80      17.67  -7.54   
Climatology              38.39    0.25       40.96      20.01  -7.62   
Fourier+ARMA const       40.91    0.25       44.40      18.99  -6.49   
Seasonal naive           52.78    0.28       54.45      21.94  -9.94   
LSTM (small)             57.79    0.34       64.83      27.45 -14.82   
SARIMA D=0               58.91    0.44       52.87      39.60 -12.68   

                         coverage95  winkler  
model                                         
Fourier+ARMA linear            0.86   237.50  
Linear regression              0.88   220.47  
SARIMA D=1                     0.85   304.16  
Climatology + AR(1)            0.78   256.63  
Fourier+ARMA (selected)        0.85   194.50  
Climatology                    0.78   255.77  
Fourier+ARMA const             0.87   238.73  
Seasonal naive                 0.92   221.65  
LSTM (small)                   0.52   611.08  
SARIMA D=0                     0.90   285.97
```

### [code 6]
```python
# Paired loss differences against climatology: moving-block bootstrap (8-week blocks) of the weekly absolute-error differences.
def abs_err(model, folds):
    return [np.abs(fcs[f][model]["actual"] - np.exp(fcs[f][model]["mu"])) for f in folds]   # one array per fold: blocks never cross folds

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
3  folds 2018+2019             LSTM (small)                         16.54   
4  folds 2018+2019       Fourier+ARMA const                          0.86   
5  folds 2018+2019      Fourier+ARMA linear                         -2.94   
6  folds 2018+2019  Fourier+ARMA (selected)                         -0.23   
7  folds 2018+2019               SARIMA D=1                         -0.53   
8  folds 2018+2019               SARIMA D=0                         18.67   

   ci_lo  ci_hi            verdict  
0   0.94   8.96              worse  
1  -0.80   0.02  indistinguishable  
2  -5.83   1.91  indistinguishable  
3   6.62  27.75              worse  
4  -2.09   4.32  indistinguishable  
5  -6.12   0.68  indistinguishable  
6  -2.91   2.77  indistinguishable  
7  -1.91   0.98  indistinguishable  
8  13.13  23.88              worse
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

### [code 9]
```python
# SARIMA D=0 with vs without a constant, same orders, same three folds (replaces the unsupported "39.7 -> 30.6" remark of the first write-up)
d0 = {"no constant": F.sarima((1, 0, 1), (1, 0, 0, 52), trend="n"), "with constant": F.sarima((1, 0, 1), (1, 0, 0, 52), trend="c")}
bt0, _ = F.backtest(y, raw, d0, n_jobs=6, verbose=False)
d0tab = bt0.pivot(index="model", columns="fold", values="MAE")
for f in (2017, 2018, 2019):
    d0tab.loc["Climatology (reference)", f] = bt[(bt.model == "Climatology") & (bt.fold == f)]["MAE"].iloc[0]
d0tab.round(1).to_csv(RESULTS / "fc_sarima_d0_constant.csv"); display(d0tab.round(1))
key["sarima_d0_const"] = d0tab.round(2).to_dict()
```

output:
```
fold                     2017  2018  2019
model                                    
no constant              76.9  61.0  92.1
with constant            44.9  42.8  44.1
Climatology (reference)  31.0  21.8  27.8
```

### [md 10]
**Reading it.** Adding the constant changes the SARIMA D=0 error by the amounts above (same orders, same folds); D=0 stays clearly worse than climatology either way.

### [md 11]
## 3. Residual diagnostics (the draft's Ljung–Box result was an artifact)
`SARIMAX` with `D=1` initialises the first 52 seasonal states diffusely, so the first 52 in-sample residuals are as large as the series level
(about 5 on the log scale) and must be excluded (`res.loglikelihood_burn`). The draft ran Ljung–Box on all residuals and got p ≈ 0 at every lag.
Below: the same model with and without the exclusion, next to the selected Fourier+ARMA model, all fitted on 2015–2018.

### [code 12]
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
key["nonconverged_rejected_per_origin"] = {int(f): int(specs[f]["n_rejected_nonconverged"]) for f in specs}
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

### [md 13]
**Reading it.** With the burn-in removed the SARIMA residuals are fine at lags 10 and 26, but the seasonal parameter is not identified:
the seasonal MA coefficient is near −1 with a standard error larger than its value, which is the signature of differencing a series that
does not need it (a deterministic seasonal pattern). Residual structure at lag 52 and in the Fourier model is reported honestly in the table
(see `LB_p_lag52`); no GARCH-type model is needed since ARCH-LM on the weekly residuals does not reject.

### [md 14]
## 4. Interval calibration
The draft's 95% interval covered only 85% of 2019 weeks and all misses were below the lower bound, so part of the problem is **level bias**
(2019 was cleaner than the training years), not only width. We calibrate with a rule fixed in advance and tested out of sample:
* compute standardised log errors `z = (log actual − mu)/sd` on the two *earlier* folds;
* scale the sd by season (winter vs other) with shrinkage toward the pooled value (k = 26 pseudo-weeks);
* **re-centre only if** the bias has the same sign in both calibration folds and |mean z| > 0.5. Otherwise leave the centre alone, since a level
  shift that flips sign across years cannot be corrected by the past.

### [code 15]
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

def shrunk_shift(folds, k=26):
    """POST-HOC sensitivity (defined after seeing 2019): continuous shrinkage of the mean z toward 0, in place of the step rule."""
    z = pd.concat([standardized(f) for f in folds])["z"]
    return float(z.sum() / (len(z) + k))

rule19 = calibration_rule([2017, 2018])
o = fcs[2019][SEL]; mu_c, sd_c = calibrated_sd_mu(o["mu"], o["sd"], o["idx"], rule19)
sh19 = shrunk_shift([2017, 2018]); mu_s = o["mu"] + sh19 * o["sd"]
cal_tab = pd.DataFrame({"Model-based Gaussian": F.metrics(o["actual"], o["mu"], o["sd"], o["idx"]),
                        "Calibrated (season scale" + (", re-centred)" if rule19["recentre"] else ")"): F.metrics(o["actual"], mu_c, sd_c, o["idx"]),
                        "Season scale + shrunk shift (post-hoc sensitivity)": F.metrics(o["actual"], mu_s, sd_c, o["idx"])}).T
cal_tab = cal_tab[["MAE", "coverage", "width", "winkler", "bias"]]
cal_tab.round(3).to_csv(RESULTS / "fc_calibration_2019.csv")
print("calibration rule from 2017+2018:", rule19)
display(cal_tab.round(3))
# same table for the other models that carry an sd, for context
ctx = bt[bt.fold == 2019].set_index("model")[["MAE", "coverage", "width", "winkler"]].dropna()
display(ctx.round(3))
key["calibration_rule_2019"] = rule19; key["coverage_2019_raw"] = float(cal_tab.iloc[0]["coverage"]); key["coverage_2019_calibrated"] = float(cal_tab.iloc[1]["coverage"])
key["calibration_2019_all"] = cal_tab.round(3).to_dict("index"); key["shrunk_shift_2019"] = sh19
```

output:
```
calibration rule from 2017+2018: {'f': {True: 1.3343095497324873, False: 1.421532404826579}, 'shift': 0.0, 'by_fold_mean_z': {2017: -0.66, 2018: -0.45}, 'recentre': False}
                                                       MAE  coverage    width  \
Model-based Gaussian                                25.694     0.904  125.080   
Calibrated (season scale)                           25.694     0.962  178.655   
Season scale + shrunk shift (post-hoc sensitivity)  23.598     0.962  158.878   

                                                    winkler   bias  
Model-based Gaussian                                174.878 -8.492  
Calibrated (season scale)                           192.721 -8.492  
Season scale + shrunk shift (post-hoc sensitivity)  161.033  4.328                              MAE  coverage    width  winkler
model                                                      
Seasonal naive           30.306     0.923  159.619  179.509
Climatology              27.818     0.808  102.837  224.736
Climatology + AR(1)      27.326     0.808  102.932  225.242
Linear regression        24.945     0.923  113.246  227.112
LSTM (small)             54.347     0.442  107.484  920.579
Fourier+ARMA const       29.261     0.885  122.861  242.045
Fourier+ARMA linear      23.974     0.923  109.172  235.401
Fourier+ARMA (selected)  25.694     0.904  125.080  174.878
SARIMA D=1               27.452     0.846  132.997  205.876
SARIMA D=0               44.103     0.904  240.505  262.603
```

### [md 16]
**Reading it.** The season scale raises 2019 coverage from about 90% to 96%, but it does so by making the intervals about 43% wider and the Winkler interval score *worse*
(the proper score penalises width). So calibration here buys nominal coverage, not sharper or better intervals. The 2017 fold's coverage is only about 69%, so three origins do not
support a general reliability claim. The step rule did not re-centre in 2019 because the 2018 mean z (-0.45) missed the 0.5 cut-off; the last column (a smooth shrunk shift defined *after* seeing 2019)
is a sensitivity, not the headline.

### [md 17]
## 5. One week ahead: does weather help when tested fairly?
Each test year (2018, 2019) is forecast one week at a time. Parameters are fitted once, on all data before that year; each week the model sees all earlier
observed PM2.5 (a true one-step forecast). The selected model for that origin (from §1) is the "no weather" version; weather variables are weekly anomalies from a
climatology fitted on data before the test year.

| Variant | Weather information | Available in practice? |
|---|---|---|
| lagged weather | last week's mean wind and humidity anomaly | yes |
| last 3 days | mean anomaly of the last 3 days (Fri–Sun) of the previous week | yes |
| **same-week (oracle)** | the forecast week's own observed wind and humidity | **no**, hindsight upper bound (ERA5 reanalysis is not a forecast) |

### [code 18]
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
rows, errs, onestep_store = [], {}, {}
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
        onestep_store[(year, name)] = (test_idx, act, mu_)
        rows.append({"year": year, "model": name, "MAE": np.abs(e).mean(), "logMAE": np.abs(np.log(act) - mu_).mean(), "n": len(e)})
os_tab = pd.DataFrame(rows)
pd.DataFrame([{"year": yr, "model": nm, "date": d_, "actual": a_, "mu": m_}
              for (yr, nm), (dd_, aa_, mm_) in onestep_store.items() for d_, a_, m_ in zip(dd_, aa_, mm_)]).to_csv(RESULTS / "fc_oneweek_forecasts.csv", index=False)
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

### [code 19]
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

### [md 20]
**Reading it.** The operational variants (lagged weather) are compared with the model that has no weather; the oracle variant shows how much
accuracy would be available if the week's weather were known in advance. The Diebold–Mariano p-values use genuine one-step errors (Harvey–Leybourne–Newbold
small-sample correction), so unlike the 52-step comparison the test is valid here.

### [code 21]
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

### [md 22]
## 6. Final outlook for 2020 and validation of the method on 2019
**Procedure (identical for both).** Fit the headline procedure on the years before the target year; simulate 5,000 weekly paths from the fitted model
(53 weeks so every calendar day is covered); apply the calibration rule (fitted only on earlier folds); convert weekly paths to daily PM2.5 by adding a
whole within-week offset vector (Mon–Sun, `log(daily) − log(weekly mean)`, from a training week of the same month), so each simulated week still averages exactly to its simulated weekly mean and day-to-day dependence is kept; classify each day into the CPCB
PM2.5 sub-index bands. Monthly means and band-day counts are computed from the same daily paths. This yields (a) the median and 95% interval of each month's mean PM2.5 and (b) the expected number of days per band.
**This is a PM2.5 band, not the official AQI** (the AQI is the maximum sub-index over all pollutants).
2019 is a genuine out-of-sample test of the whole pipeline; 2020 is the deliverable.

### [code 23]
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
    dd, dv = F.daily_paths(paths_c, idx, pools, year)               # daily values whose weekly means equal the weekly paths
    bands = F.daily_band_days(dd, dv)                                # (paths, 12, 6)  band days and monthly means come from the SAME daily paths
    monthly = F.monthly_mean_paths(dd, dv)                           # (12, paths)
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
{'months_actual_inside_95': 12, 'annual_days_pred': {'Good': 21.0, 'Satisfactory': 75.0, 'Moderate': 68.0, 'Poor': 53.0, 'Very Poor': 114.0, 'Severe': 35.0}, 'annual_days_actual': {'Good': 25, 'Satisfactory': 97, 'Moderate': 78, 'Poor': 58, 'Very Poor': 73, 'Severe': 34}, 'mean_abs_days_error_per_band_month': 1.9, 'poor_or_worse_pred_pct': 55.1, 'poor_or_worse_actual_pct': 45.2}
     actual_mean  pred_median  pred_lo95  pred_hi95  inside95
Jan        204.3        209.8      147.0      301.4      True
Feb        122.3        141.9       95.2      213.0      True
Mar         84.2        101.7       65.5      156.9      True
Apr         82.3        101.5       63.8      160.2      True
May         89.7        100.2       61.5      163.3      True
Jun         63.8         75.4       45.7      122.8      True
Jul         46.7         46.2       27.3       77.3      True
Aug         34.1         43.2       25.3       73.8      True
Sep         40.1         57.3       32.7       99.3      True
Oct        123.7        141.9       80.7      250.8      True
Nov        205.4        234.6      133.6      403.4      True
Dec        205.2        199.2      113.8      346.7      True
```

### [code 24]
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
Jan    190.41  141.68  254.94        1.00        1.00         1.00       0.00   
Feb    121.89   90.35  164.84        1.00        0.98         0.54       0.04   
Mar     84.45   66.28  108.66        0.99        0.30         0.00       0.26   
Apr     85.71   66.92  110.66        1.00        0.35         0.00       0.15   
May     84.11   65.63  108.65        1.00        0.30         0.00       0.16   
Jun     62.75   47.93   81.70        0.64        0.00         0.00       1.36   
Jul     38.89   30.28   50.51        0.00        0.00         0.00       8.80   
Aug     35.52   27.55   46.09        0.00        0.00         0.00      11.05   
Sep     45.56   35.29   58.63        0.02        0.00         0.00       5.87   
Oct    120.12   91.86  155.92        1.00        0.98         0.50       0.03   
Nov    192.13  143.31  259.61        1.00        1.00         1.00       0.00   
Dec    169.29  126.12  225.66        1.00        1.00         0.99       0.00   

       days_Satisfactory  days_Moderate  days_Poor  days_Very Poor  \
month                                                                
Jan                 0.12           0.98       3.01           21.18   
Feb                 1.83           6.28       7.82           12.30   
Mar                 6.04          12.71       8.08            3.91   
Apr                 5.44          12.56       7.91            3.94   
May                 6.38          12.86       7.79            3.80   
Jun                13.90          10.64       3.27            0.83   
Jul                19.52           2.48       0.19            0.01   
Aug                18.51           1.38       0.06            0.00   
Sep                18.06           5.37       0.65            0.06   
Oct                 2.75           7.58       7.48           12.22   
Nov                 0.21           1.13       2.99           19.63   
Dec                 0.24           2.16       4.96           19.86   

       days_Severe  actual_mean_2020  actual_days_covered  
month                                                      
Jan           5.70            157.11                 31.0  
Feb           0.73            121.48                 29.0  
Mar           0.00             57.51                 31.0  
Apr           0.01             44.94                 30.0  
May           0.01      
...[truncated]
```

### [code 25]
```python
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.35, 1]})
ax = axes[0]; xs = np.arange(12)
ax.fill_between(xs, mt20["lo95"], mt20["hi95"], color=BLUE, alpha=0.18, lw=0, label="95% prediction interval")
ax.plot(xs, mt20["median"], color=BLUE, lw=2, marker="o", ms=4, label="Forecast median (made Dec 2019)")
ok = mt20["actual_days_covered"] >= 28
ax.plot(xs[ok], mt20.loc[ok, "actual_mean_2020"], color=ORANGE, lw=1.6, marker="s", ms=4, label="Actual 2020 (full months)")
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

### [md 26]
## 7. Case study: the 2020 lockdown
Delhi's lockdown began on 25 March 2020. We compare the actual weekly PM2.5 of the ten Sunday-ending weeks 29 March – 31 May (these cover 23 March – 31 May, so two pre-lockdown days are included) with the no-lockdown forecast made on
29 Dec 2019 (calibrated, as above). A second counterfactual uses a version of the same model *with the actual 2020 same-week wind and humidity* (fitted on 2015–2019),
to separate the weather contribution from the rest. Both are descriptive, not causal: they rely on the model being right about the level for 2020, and the model was already about 9% too high in the weeks before the lockdown (sensitivities below).

### [code 27]
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
no-lockdown forecast                               48.7       85.0   
weather-adjusted forecast (oracle weather)          NaN       78.6   

                                            gap_median_pct  gap_lo95_pct  \
no-lockdown forecast                                 -42.8         -52.1   
weather-adjusted forecast (oracle weather)           -38.1         -47.5   

                                            gap_hi95_pct  
no-lockdown forecast                               -31.8  
weather-adjusted forecast (oracle weather)         -26.7  <Figure size 990x418 with 1 Axes>
```

### [md 28]
### Sensitivity of the lockdown gap
The gap to a forecast is only as good as the forecast's level. Checks: (a) the same model's gap in the 12 weeks *before* the lockdown (5 Jan – 22 Mar), and the lockdown gap adjusted for it;
(b) a 9-week window starting 5 April (no pre-lockdown days); (c) other level specifications (constant, random-walk); (d) a mean-bias shift shrunk from the 2018–19 errors (post-hoc);
(e) a placebo: the same calendar weeks of 2019 against the 2019 forecast pipeline.

### [code 29]
```python
def gap_stats(paths, idx_, weeks):
    pos_ = pd.DatetimeIndex(idx_).get_indexer(weeks); assert (pos_ >= 0).all()
    cf_ = np.exp(paths[pos_]).mean(axis=0); g = raw.reindex(weeks).mean() / cf_ - 1
    return float(100 * np.median(g)), float(100 * np.percentile(g, 2.5)), float(100 * np.percentile(g, 97.5))

wk_pre = pd.date_range("2020-01-05", "2020-03-22", freq="W-SUN")
wk_9 = pd.date_range("2020-04-05", "2020-05-31", freq="W-SUN")
rule20 = P20["rule"]; f20 = np.where(pd.DatetimeIndex(P20["idx"]).month.isin(F.WINTER), rule20["f"][True], rule20["f"][False])
def spec_paths(trend, K, p_, q_):
    r_ = F._fit_dhr(y.loc[:"2019-12-29"], K, p_, q_, trend)
    pa = F.simulate_paths(r_, P20["idx"], exog=F.fourier(P20["idx"], K), n=5000)
    fc_ = r_.get_forecast(len(P20["idx"]), exog=F.fourier(P20["idx"], K)); mu_ = fc_.predicted_mean.to_numpy()
    return mu_[:, None] + f20[:, None] * (pa - mu_[:, None]), mu_, np.sqrt(fc_.var_pred_mean.to_numpy())

rows = []
def add(name, paths, idx_=P20["idx"]):
    pre = gap_stats(paths, idx_, wk_pre); l10 = gap_stats(paths, idx_, lock_idx); l9 = gap_stats(paths, idx_, wk_9)
    adj = 100 * ((1 + l10[0] / 100) / (1 + pre[0] / 100) - 1)
    rows.append({"counterfactual": name, "pre_lockdown_gap_pct": pre[0], "lockdown_gap_10wk_pct": l10[0], "lo95": l10[1], "hi95": l10[2],
                 "gap_9wk_from_5Apr_pct": l9[0], "lockdown_gap_adjusted_for_pre_gap_pct": adj})
add("selected spec (linear, K=5, AR1), headline", P20["paths"])
for nm, (tr_, K_, p_, q_) in {"constant level": ("const", 5, 1, 0), "random-walk level (ARIMA errors)": ("rw", 5, 1, 1)}.items():
    pa_, _, _ = spec_paths(tr_, K_, p_, q_); add(nm, pa_)
sh20 = shrunk_shift([2018, 2019])
add("headline + shrunk mean-bias shift (post-hoc)", P20["paths"] + sh20 * P20["sd"][:, None])
# placebo: 2019 pipeline, same calendar weeks of 2019
wk_pl = pd.date_range("2019-03-31", "2019-06-02", freq="W-SUN")
pl = gap_stats(P19["paths"], P19["idx"], wk_pl)
rows.append({"counterfactual": "PLACEBO: same weeks of 2019 vs 2019 forecast", "pre_lockdown_gap_pct": gap_stats(P19["paths"], P19["idx"], pd.date_range("2019-01-06", "2019-03-24", freq="W-SUN"))[0],
             "lockdown_gap_10wk_pct": pl[0], "lo95": pl[1], "hi95": pl[2], "gap_9wk_from_5Apr_pct": np.nan, "lockdown_gap_adjusted_for_pre_gap_pct": np.nan})
sens = pd.DataFrame(rows); sens.round(1).to_csv(RESULTS / "fc_lockdown_sensitivity.csv", index=False); display(sens.round(1))
key["lockdown_sensitivity"] = sens.round(2).set_index("counterfactual").to_dict("index")
```

output:
```
                                 counterfactual  pre_lockdown_gap_pct  \
0    selected spec (linear, K=5, AR1), headline                 -11.3   
1                                constant level                 -22.6   
2              random-walk level (ARIMA errors)                  -9.9   
3  headline + shrunk mean-bias shift (post-hoc)                  -2.4   
4  PLACEBO: same weeks of 2019 vs 2019 forecast                  -8.9   

   lockdown_gap_10wk_pct  lo95  hi95  gap_9wk_from_5Apr_pct  \
0                  -42.8 -52.1 -31.8                  -41.5   
1                  -50.8 -59.6 -40.0                  -49.8   
2                  -43.1 -54.5 -28.5                  -41.7   
3                  -37.0 -47.3 -25.0                  -35.6   
4                  -14.9 -43.9  28.2                    NaN   

   lockdown_gap_adjusted_for_pre_gap_pct  
0                                  -35.5  
1                                  -36.5  
2                                  -36.9  
3                                  -35.5  
4                                    NaN
```

### [md 30]
## 8. Summary numbers

### [code 31]
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
{'sarima_d0_const': {2017: {'no constant': 76.92,
   'with constant': 44.87,
   'Climatology (reference)': 31.0},
  2018: {'no constant': 60.98,
   'with constant': 42.84,
   'Climatology (reference)': 21.77},
  2019: {'no constant': 92.11,
   'with constant': 44.1,
   'Climatology (reference)': 27.82}},
 'nonconverged_rejected_per_origin': {2017: 6, 2018: 3, 2019: 5},
 'sarima_D1_maS_coef': -0.988,
 'sarima_D1_maS_se': 8.259,
 'calibration_rule_2019': {'f': {True: 1.3343095497324873,
   False: 1.421532404826579},
  'shift': 0.0,
  'by_fold_mean_z': {2017: -0.66, 2018: -0.45},
  'recentre': False},
 'coverage_2019_raw': 0.9038461538461539,
 'coverage_2019_calibrated': 0.9615384615384616,
 'calibration_2019_all': {'Model-based Gaussian': {'MAE': 25.694,
   'coverage': 0.904,
   'width': 125.08,
   'winkler': 174.878,
   'bias': -8.492},
  'Calibrated (season scale)': {'MAE': 25.694,
   'coverage': 0.962,
   'width': 178.655,
   'winkler': 192.721,
   'bias': -8.492},
  'Season scale + shrunk shift (post-hoc sensitivity)': {'MAE': 23.598,
   'coverage': 0.962,
   'width': 158.878,
   'winkler': 161.033,
   'bias': 4.328}},
 'shrunk_shift_2019': -0.445110367609404,
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
   'Moderate': 68.0,
   'Poor': 53.0,
   'Very Poor': 114.0,
   'Severe': 35.0},
  'annual_days_actual': {'Good': 25,
   'Satisfactory': 97,
   'Moderate': 78,
   'Poor': 58,
   'Very Poor': 73,
   'Severe': 34},
  'mean_abs_days_error_per_band_month': 1.9,
  'poor_or_worse_pred_pct': 55.1,
  'poor_or_worse_actual_pct': 45.2},
 'outlook_2020_spec': {'trend': 'linear',
  'K': 5,
  'p': 1,
  'q': 0,
  'n_rejected_nonconverged': 13},
 'outlook_2020_rule': {'f': {True: 1.0935180465819772,
   False: 0.9476619724449761},
  'shift': 0.0,
  'by_fold_mean_z': {2018: -0.45, 2019: -0.53},
  'recentre': False},
 'lockdown': {'plain': {'actual_mean': 48.669714285714285,
   'cf_median': 85.04899262695417,
   'gap_median_pct': -42.77449646078571,
   'gap_lo95_pct': -52.11359900861902,
   'gap_hi95_pct': -31.819259395224652},
  'weather_ad
...[truncated]
```


# 04 All results tables (results/)

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
           LSTM (small)  36.3  28.3  54.3          41.3        39.7
             SARIMA D=0  44.9  42.8  44.1          43.5        43.9
```

## fc_backtest_metrics.csv
```
 fold                   model  n_train    MAE   RMSE  logMAE     bias  MAE_winter  MAE_other  coverage  winkler  width
 2017          Seasonal naive      104 38.438 65.597  0.2968   -13.56      65.098     25.489   0.88462   261.55 167.09
 2017             Climatology      104 30.999 43.409 0.28271  -1.2015      43.078     25.131   0.61538   399.77 76.866
 2017     Climatology + AR(1)      104 30.701 43.396 0.28125  -1.9062      42.167     25.131   0.61538    401.9 76.751
 2017       Linear regression      104 35.893 51.028 0.31948  -11.367      55.353     26.441      0.75   286.47 127.27
 2017            LSTM (small)      104 36.339 50.931 0.32186   2.7608      53.916     27.802   0.42308   575.48 55.528
 2017      Fourier+ARMA const      104 30.592 47.655  0.2773  0.18211      45.602     23.302      0.75    327.5  104.6
 2017     Fourier+ARMA linear      104 35.856 50.717 0.31914  -11.087      55.358     26.383   0.69231   330.84 112.71
 2017 Fourier+ARMA (selected)      104 31.483 44.063 0.28597  -5.7257      48.805      23.07   0.69231   266.41 100.75
 2017              SARIMA D=1      104 53.827 102.13 0.34136  -31.352      101.23     30.802   0.76923   537.52 160.32
 2017              SARIMA D=0      104 44.874  62.59 0.44952   -12.49       47.85     43.428   0.84615   332.58 270.65
 2018          Seasonal naive      157 28.965 46.452 0.25023  -9.8967      41.972     22.648   0.94231    223.9 175.04
 2018             Climatology      157 21.772 29.614 0.19972    -9.09      33.224      16.21   0.92308    142.8 104.61
 2018     Climatology + AR(1)      157 21.667 29.605 0.19932  -9.4044      32.903      16.21   0.92308   142.76 104.61
 2018       Linear regression      157  19.99 28.849 0.17624 -0.51377      36.009     12.209   0.96154   147.81 127.88
 2018            LSTM (small)      157 28.318  37.99 0.25825  -7.0718      43.681     20.856   0.69231   337.18 77.581
 2018      Fourier+ARMA const      157 22.049  30.44 0.19919  -7.8222      36.286     15.134   0.96154   146.63 126.92
 2018     Fourier+ARMA linear      157 19.733 28.354 0.17299  -1.8157      35.817      11.92   0.96154   146.26 121.18
 2018 Fourier+ARMA (selected)      157 23.426 34.432 0.20086  -8.4162      42.257      14.28   0.94231   142.22 116.16
 2018              SARIMA D=1      157 21.084  31.49 0.18417  -8.6636      32.766     15.409   0.94231   169.08 151.11
 2018              SARIMA D=0      157 42.835 53.791 0.41929  -9.4661      53.492     37.659   0.96154   262.74  260.7
 2019          Seasonal naive      209 30.306  46.29 0.27952  -6.3698      56.268     17.696   0.92308   179.51 159.62
 2019             Climatology      209 27.818 42.136 0.26091  -12.562      46.588     18.701   0.80769   224.74 102.84
 2019     Climatology + AR(1)      209 27.326 41.786 0.25875  -13.083      45.084     18.701   0.80769   225.24 102.93
 2019       Linear regression      209 24.945 42.606  0.2177    1.068      50.845     12.365   0.92308   227.11 113.25
 2019            LSTM (small)      209 54.347 84.461 0.43056  -40.157      96.898      33.68   0.44231   920.58 107.48
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
Season scale + shrunk shift (post-hoc sensitivity) 23.598     0.962 158.88   161.03  4.328
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
                      no-lockdown forecast         48.7         85           -42.8         -52.1         -31.8
weather-adjusted forecast (oracle weather)          NaN       78.6           -38.1         -47.5         -26.7
```

## fc_lockdown_sensitivity.csv
```
                              counterfactual  pre_lockdown_gap_pct  lockdown_gap_10wk_pct  lo95  hi95  gap_9wk_from_5Apr_pct  lockdown_gap_adjusted_for_pre_gap_pct
  selected spec (linear, K=5, AR1), headline                 -11.3                  -42.8 -52.1 -31.8                  -41.5                                  -35.5
                              constant level                 -22.6                  -50.8 -59.6   -40                  -49.8                                  -36.5
            random-walk level (ARIMA errors)                  -9.9                  -43.1 -54.5 -28.5                  -41.7                                  -36.9
headline + shrunk mean-bias shift (post-hoc)                  -2.4                    -37 -47.3   -25                  -35.6                                  -35.5
PLACEBO: same weeks of 2019 vs 2019 forecast                  -8.9                  -14.9 -43.9  28.2                    NaN                                    NaN
```

## fc_loss_diff.csv
```
          folds                   model  mean_MAE_diff_vs_climatology  ci_lo  ci_hi           verdict
folds 2018+2019          Seasonal naive                          4.84   0.94   8.96             worse
folds 2018+2019     Climatology + AR(1)                          -0.3   -0.8   0.02 indistinguishable
folds 2018+2019       Linear regression                         -2.33  -5.83   1.91 indistinguishable
folds 2018+2019            LSTM (small)                         16.54   6.62  27.75             worse
folds 2018+2019      Fourier+ARMA const                          0.86  -2.09   4.32 indistinguishable
folds 2018+2019     Fourier+ARMA linear                         -2.94  -6.12   0.68 indistinguishable
folds 2018+2019 Fourier+ARMA (selected)                         -0.23  -2.91   2.77 indistinguishable
folds 2018+2019              SARIMA D=1                         -0.53  -1.91   0.98 indistinguishable
folds 2018+2019              SARIMA D=0                         18.67  13.13  23.88             worse
all three folds          Seasonal naive                          5.71   2.04  10.07             worse
all three folds     Climatology + AR(1)                          -0.3  -0.68      0 indistinguishable
all three folds       Linear regression                          0.08  -3.19    3.6 indistinguishable
all three folds            LSTM (small)                         12.81   6.07  20.63             worse
all three folds      Fourier+ARMA const                          0.44  -1.84   2.94 indistinguishable
all three folds     Fourier+ARMA linear                         -0.34  -3.45   3.04 indistinguishable
all three folds Fourier+ARMA (selected)                             0   -2.2   2.28 indistinguishable
all three folds              SARIMA D=1                          7.26   0.37  14.97             worse
all three folds              SARIMA D=0                         17.07  11.68  22.58             worse
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
  Jan  190.41 141.68 254.94           1           1        0.999          0              0.117          0.985      3.013          21.182        5.703            157.11                   31
  Feb  121.89 90.349 164.84           1       0.976        0.541       0.04              1.832          6.283      7.817          12.297        0.731            121.48                   29
  Mar  84.449 66.285 108.66       0.994       0.304        0.001      0.261              6.036         12.707      8.084           3.909        0.003            57.506                   31
  Apr  85.706 66.921 110.66       0.997       0.348        0.005      0.151              5.439          12.56      7.906           3.936        0.008             44.94                   30
  May  84.108  65.63 108.65       0.995       0.297        0.003      0.159              6.384         12.856      7.787           3.804        0.011            55.449                   31
  Jun  62.753 47.927 81.704        0.64       0.004            0      1.365             13.898         10.643      3.267           0.826        0.001            46.695                   30
  Jul  38.892 30.275  50.51           0           0            0      8.796              19.52          2.475      0.195           0.014            0             54.01                    1
  Aug  35.517  27.55 46.091           0           0            0     11.047              18.51           1.38      0.063           0.001            0               NaN                  NaN
  Sep  45.561 35.291 58.631       0.018           0            0      5.867             18.061          5.369      0.645           0.058            0               NaN                  NaN
  Oct  120.12 91.856 155.92           1       0.983        0.503      0.028              2.755          7.582      7.479          12.218        0.938               NaN                  NaN
  Nov  192.13 143.31 259.61           1           1            1      0.001              0.206          1.127      2.988           19.63        6.048               NaN                  NaN
  Dec  169.29 126.12 225.66           1           1         0.99          0              0.237          2.157      4.964          19.858        3.784               NaN                  NaN
```

## fc_outlook_validation_2019_days.csv
```
Unnamed: 0 predicted  predicted.1 predicted.2 predicted.3 predicted.4 predicted.5 actual     actual.1 actual.2 actual.3  actual.4 actual.5
       NaN      Good Satisfactory    Moderate        Poor   Very Poor      Severe   Good Satisfactory Moderate     Poor Very Poor   Severe
       Jan       0.0          0.0         0.6         2.2        19.5         8.6      0            1        1        2        16       11
       Feb       0.0          1.1         4.0         6.0        14.9         1.9      0            3        6        6        12        1
       Mar       0.3          4.5         9.0         7.8         9.0         0.4      0            5       13       13         0        0
       Apr       0.1          4.2         9.0         7.6         8.6         0.4      1            6       12        9         2        0
       May       0.2          5.0         9.1         7.6         8.7         0.4      0            6       12        8         5        0
       Jun       1.3         10.0         9.8         5.2         3.7         0.1      1           12       14        3         0        0
       Jul       6.8         16.9         5.6         1.3         0.4         0.0      4           17       10        0         0        0
       Aug       7.9         17.1         4.9         0.9         0.2         0.0     11           19        1        0         0        0
       Sep       4.2         13.6         7.8         2.9         1.5         0.0      8           18        4        0         0        0
       Oct       0.1          2.3         5.4         5.9        13.9         3.4      0            8        2        8         9        4
       Nov       0.0          0.1         0.7         1.9        15.6        11.6      0            2        1        6        12        9
       Dec       0.0          0.2         1.6         3.5        17.6         8.1      0            0        2        3        17        9
```

## fc_outlook_validation_2019_monthly.csv
```
Unnamed: 0  actual_mean  pred_median  pred_lo95  pred_hi95  inside95
       Jan        204.3        209.8        147      301.4      True
       Feb        122.3        141.9       95.2        213      True
       Mar         84.2        101.7       65.5      156.9      True
       Apr         82.3        101.5       63.8      160.2      True
       May         89.7        100.2       61.5      163.3      True
       Jun         63.8         75.4       45.7      122.8      True
       Jul         46.7         46.2       27.3       77.3      True
       Aug         34.1         43.2       25.3       73.8      True
       Sep         40.1         57.3       32.7       99.3      True
       Oct        123.7        141.9       80.7      250.8      True
       Nov        205.4        234.6      133.6      403.4      True
       Dec        205.2        199.2      113.8      346.7      True
```

## fc_sarima_d0_constant.csv
```
                  model  2017  2018  2019
            no constant  76.9    61  92.1
          with constant  44.9  42.8  44.1
Climatology (reference)    31  21.8  27.8
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
  "sarima_d0_const": {
    "2017": {
      "no constant": 76.92,
      "with constant": 44.87,
      "Climatology (reference)": 31.0
    },
    "2018": {
      "no constant": 60.98,
      "with constant": 42.84,
      "Climatology (reference)": 21.77
    },
    "2019": {
      "no constant": 92.11,
      "with constant": 44.1,
      "Climatology (reference)": 27.82
    }
  },
  "nonconverged_rejected_per_origin": {
    "2017": 6,
    "2018": 3,
    "2019": 5
  },
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
  "calibration_2019_all": {
    "Model-based Gaussian": {
      "MAE": 25.694,
      "coverage": 0.904,
      "width": 125.08,
      "winkler": 174.878,
      "bias": -8.492
    },
    "Calibrated (season scale)": {
      "MAE": 25.694,
      "coverage": 0.962,
      "width": 178.655,
      "winkler": 192.721,
      "bias": -8.492
    },
    "Season scale + shrunk shift (post-hoc sensitivity)": {
      "MAE": 23.598,
      "coverage": 0.962,
      "width": 158.878,
      "winkler": 161.033,
      "bias": 4.328
    }
  },
  "shrunk_shift_2019": -0.445110367609404,
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
      "Moderate": 68.0,
      "Poor": 53.0,
      "Very Poor": 114.0,
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
    "mean_abs_days_error_per_band_month": 1.9,
    "poor_or_worse_pred_pct": 55.1,
    "poor_or_worse_actual_pct": 45.2
  },
  "outlook_2020_spec": {
    "trend": "linear",
    "K": 5,
    "p": 1,
    "q": 0,
    "n_rejected_nonconverged": 13
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
      "cf_median": 85.04899262695417,
      "gap_median_pct": -42.77449646078571,
      "gap_lo95_pct": -52.11359900861902,
      "gap_hi95_pct": -31.819259395224652
    },
    "weather_adjusted": {
      "cf_median": 78.5752915693168,
      "gap_median_pct": -38.059772562764856,
      "gap_lo95_pct": -47.516118559968525,
      "gap_hi95_pct": -26.675729977641215
    }
  },
  "lockdown_sensitivity": {
    "selected spec (linear, K=5, AR1), headline": {
      "pre_lockdown_gap_pct": -11.32,
      "lockdown_gap_10wk_pct": -42.77,
      "lo95": -52.11,
      "hi95": -31.82,
      "gap_9wk_from_5Apr_pct": -41.49,
      "lockdown_gap_adjusted_for_pre_gap_pct": -35.47
    },
    "constant level": {
      "pre_lockdown_gap_pct": -22.6,
      "lockdown_gap_10wk_pct": -50.84,
      "lo95": -59.58,
      "hi95": -40.01,
      "gap_9wk_from_5Apr_pct": -49.78,
      "lockdown_gap_adjusted_for_pre_gap_pct": -36.48
    },
    "random-walk level (ARIMA errors)": {
      "pre_lockdown_gap_pct": -9.87,
      "lockdown_gap_10wk_pct": -43.11,
      "lo95": -54.55,
      "hi95": -28.55,
      "gap_9wk_from_5Apr_pct": -41.74,
      "lockdown_gap_adjusted_for_pre_gap_pct": -36.88
    },
    "headline + shrunk mean-bias shift (post-hoc)": {
      "pre_lockdown_gap_pct": -2.43,
      "lockdown_gap_10wk_pct": -37.02,
      "lo95": -47.3,
      "hi95": -24.97,
      "gap_9wk_from_5Apr_pct": -35.61,
      "lockdown_gap_adjusted_for_pre_gap_pct": -35.45
    },
    "PLACEBO: same weeks of 2019 vs 2019 forecast": {
      "pre_lockdown_gap_pct": -8.88,
      "lockdown_gap_10wk_pct": -14.87,
      "lo95": -43.9,
      "hi95": 28.17,
      "gap_9wk_from_5Apr_pct": NaN,
      "lockdown_gap_adjusted_for_pre_gap_pct": NaN
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
      "2017": 36.34,
      "2018": 28.32,
      "2019": 54.35
    },
    "specs": {
      "2017": {
        "trend": "rw",
        "K": 5,
        "p": 1,
        "q": 1,
        "n_rejected_nonconverged": 6
      },
      "2018": {
        "trend": "const",
        "K": 5,
        "p": 1,
        "q": 1,
        "n_rejected_nonconverged": 3
      },
      "2019": {
        "trend": "rw",
        "K": 5,
        "p": 1,
        "q": 1,
        "n_rejected_nonconverged": 5
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


# 05 Raw data for recomputation
## delhi_weekly.csv (287 rows, full precision; pm25 = weekly mean ug/m3, log_pm25 its log, n_days = daily obs in the week)
```
Date,pm25,no2,so2,aqi,rh,wind,temp,precip,n_days,log_pm25
2015-01-04,184.605,34.12,5.795,347.0,78.25,7.225,15.375,4.3,4,5.21821840729241
2015-01-11,196.00571428571428,41.18714285714286,4.435714285714286,358.42857142857144,79.42857142857143,9.914285714285716,13.171428571428573,0.0,7,5.2781438133244825
2015-01-18,187.65,49.24,5.451428571428571,360.0,82.28571428571429,7.528571428571429,12.6,4.1,7,5.23457852558103
2015-01-25,156.35714285714286,24.634285714285717,6.518571428571429,326.1428571428572,80.0,8.085714285714285,13.342857142857143,20.8,7,5.052142767907604
2015-02-01,162.78428571428572,37.27857142857143,6.471428571428571,324.1428571428572,70.0,10.085714285714284,12.44285714285714,0.0,7,5.092425923813068
2015-02-08,149.72285714285712,44.22571428571428,6.508571428571429,316.1428571428572,75.57142857142857,9.5,14.914285714285716,16.5,7,5.008785966095243
2015-02-15,161.0942857142857,47.75857142857143,8.358571428571429,338.57142857142856,66.85714285714286,8.27142857142857,16.385714285714286,0.0,7,5.0819898191273065
2015-02-22,155.09428571428572,40.29571428571428,7.138571428571429,331.1428571428572,73.85714285714286,11.671428571428573,20.342857142857145,15.2,7,5.044033226913754
2015-03-01,129.80428571428573,29.09714285714286,9.602857142857143,321.0,73.0,10.242857142857144,19.071428571428573,28.4,7,4.866027821554542
2015-03-08,82.48571428571428,22.66714285714286,4.864285714285714,230.42857142857144,78.0,8.757142857142856,16.928571428571427,35.2,7,4.412625118173521
2015-03-15,85.57571428571428,24.74857142857143,6.63,243.42857142857144,74.14285714285714,9.514285714285714,17.95714285714286,31.5,7,4.449401531278455
2015-03-22,69.44857142857143,22.427142857142854,6.132857142857143,216.7142857142857,71.57142857142857,10.37142857142857,20.142857142857142,6.7,7,4.240586499205803
2015-03-29,93.74714285714286,29.702857142857145,11.075714285714286,318.42857142857144,57.85714285714285,8.042857142857143,25.514285714285712,0.4,7,4.540601188195636
2015-04-05,71.27285714285713,23.165714285714284,13.031428571428572,259.57142857142856,70.0,8.757142857142856,23.228571428571428,34.400000000000006,7,4.266515569707812
2015-04-12,92.57142857142856,40.68,14.831428571428573,309.1428571428572,57.142857142857146,7.6571428571428575,24.214285714285715,5.9,7,4.527980547296961
2015-04-19,93.61285714285714,48.621428571428574,16.255714285714284,302.85714285714283,58.0,8.814285714285715,26.814285714285717,7.699999999999999,7,4.539167736687526
2015-04-26,110.25,60.221428571428575,19.797142857142852,371.4285714285714,33.857142857142854,11.642857142857142,30.47142857142857,0.3999999999999999,7,4.702750514326955
2015-05-03,77.63857142857144,49.38285714285714,14.487142857142857,281.57142857142856,40.85714285714285,10.842857142857143,30.12857142857143,5.9,7,4.352064358190408
2015-05-10,120.33285714285716,74.57571428571428,21.325714285714287,388.0,24.857142857142858,9.057142857142855,32.98571428571429,0.0,7,4.790261712395366
2015-05-17,89.7057142857143,53.32142857142857,13.664285714285716,341.57142857142856,50.285714285714285,6.728571428571429,30.75714285714286,12.7,7,4.496534471447241
2015-05-24,73.66857142857143,56.392857142857146,15.604285714285714,314.7142857142857,28.0,10.142857142857142,34.27142857142857,1.7,7,4.299576269011815
2015-05-31,107.67714285714284,61.08285714285715,13.87857142857143,361.8571428571428,22.142857142857142,10.028571428571428,34.785714285714285,0.1,7,4.6791373318997325
2015-06-07,66.46428571428571,59.50571428571429,7.078571428571428,303.2857142857143,37.285714285714285,8.828571428571427,32.5,1.1,7,4.196664746467047
2015-06-14,97.80571428571427,58.35714285714285,6.771428571428571,274.57142857142856,37.71428571428572,12.885714285714286,34.628571428571426,6.7,7,4.582983003613194
2015-06-21,106.39714285714288,69.75142857142858,7.55,268.1428571428572,57.285714285714285,8.428571428571429,32.48571428571429,8.9,7,4.667178723700598
2015-06-28,82.33571428571429,51.10142857142857,7.355714285714286,209.28571428571428,68.57142857142857,9.55714285714286,30.82857142857143,50.400000000000006,7,4.410804965991709
2015-07-05,73.90285714285713,42.291428571428575,7.885714285714286,217.8571428571429,67.0,10.528571428571428,30.74285714285714,15.0,7,4.3027514894917305
2015-07-12,50.77,47.53142857142858,8.037142857142857,223.28571428571428,86.42857142857143,8.142857142857142,27.142857142857142,168.20000000000002,7,3.927305628959303
2015-07-19,62.66285714285714,42.81,9.955714285714285,204.42857142857144,78.42857142857143,9.6,29.142857142857142,57.7,7,4.13776888204048
2015-07-26,40.78428571428572,43.93857142857143,15.168571428571427,178.42857142857142,80.71428571428571,12.285714285714286,28.61428571428572,33.3,7,3.708296853157615
2015-08-02,32.75571428571429,35.87285714285714,10.034285714285714,171.14285714285714,78.0,11.585714285714284,27.5,10.6,7,3.489077428867589
2015-08-09,60.74571428571429,47.20285714285715,9.04857142857143,222.42857142857144,87.28571428571429,5.6000000000000005,27.65714285714285,110.5,7,4.106696532994906
2015-08-16,63.74285714285714,48.15857142857143,8.778571428571428,223.8571428571429,86.57142857142857,5.757142857142858,28.0,42.9,7,4.154857132943119
2015-08-23,48.58857142857143,39.84857142857143,10.858571428571429,194.0,78.14285714285714,8.714285714285714,28.62857142857143,13.3,7,3.883388347462279
2015-08-30,58.940000000000005,43.23285714285714,10.45142857142857,228.0,76.14285714285714,8.414285714285715,29.585714285714285,2.9,7,4.076519977309549
2015-09-06,79.71571428571428,31.91857142857143,13.20142857142857,274.1428571428572,60.71428571428572,10.357142857142858,29.24285714285714,0.0,7,4.3784667343123695
2015-09-13,68.17428571428572,42.68142857142857,11.198571428571428,218.57142857142856,61.142857142857146,8.857142857142858,29.2,0.3,7,4.222067451438566
2015-09-20,86.36857142857143,54.32571428571429,10.235714285714286,229.0,71.71428571428571,7.371428571428572,29.5,31.3,7,4.458623853020768
2015-09-27,62.79571428571428,43.85428571428572,11.921428571428573,197.14285714285717,71.85714285714286,10.228571428571428,27.4,11.8,7,4.139886827287382
2015-10-04,90.26571428571428,51.355714285714285,11.19,252.28571428571428,59.57142857142857,8.128571428571428,26.814285714285717,0.0,7,4.502757701565248
2015-10-11,144.83428571428573,62.01857142857143,13.31,360.57142857142856,50.57142857142857,8.514285714285714,28.285714285714285,0.0,7,4.975590231718496
2015-10-18,109.29714285714284,47.96142857142858,11.142857142857142,290.85714285714283,66.0,7.028571428571429,27.214285714285715,7.7,7,4.69407025446702
2015-10-25,157.71428571428572,58.76714285714286,16.462857142857143,370.8571428571428,53.142857142857146,7.871428571428572,25.857142857142858,1.4,7,5.060785077781727
2015-11-01,150.76,48.06857142857143,21.404285714285717,311.85714285714283,64.14285714285714,6.257142857142857,22.485714285714288,7.0,7,5.015689168398935
2015-11-08,236.74142857142857,74.72714285714287,26.610000000000003,411.2857142857143,68.28571428571429,5.8,23.057142857142857,0.2,7,5.466968526855047
2015-11-15,236.7328571428572,68.54714285714286,27.73,420.0,59.142857142857146,8.128571428571428,22.67142857142857,0.6,7,5.466932320333042
2015-11-22,222.77714285714288,86.38142857142857,22.40142857142857,410.57142857142856,54.42857142857143,7.257142857142857,19.957142857142856,1.0,7,5.406171912382576
2015-11-29,199.59,69.76428571428572,19.885714285714283,374.0,60.285714285714285,7.742857142857143,19.485714285714288,0.0,7,5.2962652624219055
2015-12-06,216.25571428571428,94.92714285714284,23.634285714285717,401.4285714285714,66.71428571428571,6.985714285714286,19.142857142857142,0.0,7,5.376461569905478
2015-12-13,216.27857142857144,85.57428571428571,20.424285714285716,397.1428571428572,68.42857142857143,8.142857142857142,17.32857142857143,0.2,7,5.376567259297665
2015-12-20,129.05142857142857,45.76857142857143,16.360000000000003,278.57142857142856,58.42857142857143,8.357142857142858,13.357142857142858,0.0,7,4.860210996009811
2015-12-27,181.33714285714285,89.18285714285715,19.33142857142857,342.2857142857143,59.142857142857146,9.028571428571428,13.37142857142857,0.0,7,5.200357966370521
2016-01-03,226.9142857142857,80.15142857142858,22.11428571428572,408.2857142857143,61.71428571428572,9.4,15.685714285714283,0.0,7,5.424572350201784
2016-01-10,290.9271428571429,92.89142857142858,23.925714285714285,496.57142857142856,70.14285714285714,7.885714285714285,16.914285714285715,0.5,7,5.673072867635633
2016-01-17,194.99142857142857,61.49,16.37,372.0,74.57142857142857,7.2,14.6,0.0,7,5.272955601553695
2016-01-24,272.0914285714286,66.48857142857142,14.775714285714283,438.2857142857143,76.0,6.614285714285714,12.12857142857143,0.0,7,5.6061381442692495
2016-01-31,271.9614285714286,85.69142857142857,20.73,456.7142857142857,74.71428571428571,6.614285714285714,15.571428571428571,0.7,7,5.6056602495177845
2016-02-07,160.92142857142858,71.08571428571429,22.928571428571427,332.1428571428572,59.85714285714285,9.785714285714286,14.914285714285716,4.0,7,5.080916224567838
2016-02-14,146.91,67.51857142857143,22.73,323.42857142857144,65.42857142857143,8.071428571428571,16.2,0.7,7,4.989820154382335
2016-02-21,136.73714285714286,62.01428571428572,26.15571428571429,300.0,62.285714285714285,8.285714285714286,19.085714285714285,16.0,7,4.918060417555802
2016-02-28,131.82714285714286,76.72142857142856,25.884285714285717,289.7142857142857,57.57142857142857,8.328571428571427,19.82857142857143,0.0,7,4.88149154060126
2016-03-06,134.36714285714285,77.96571428571428,21.835714285714285,302.57142857142856,61.57142857142857,7.671428571428572,22.514285714285712,14.999999999999998,7,4.90057592541159
2016-03-13,89.56714285714285,37.92714285714286,18.542857142857144,203.42857142857144,67.42857142857143,9.257142857142856,21.814285714285717,24.4,7,4.494988543542957
2016-03-20,77.62142857142858,53.64571428571429,22.33857142857143,188.0,61.42857142857143,8.442857142857143,22.47142857142857,1.5,7,4.351843530453547
2016-03-27,87.71857142857142,53.14,21.557142857142857,239.28571428571428,45.0,12.471428571428572,24.457142857142856,0.0,7,4.4741336378330745
2016-04-03,112.15857142857143,41.262857142857136,25.88714285714286,266.85714285714283,41.71428571428572,8.2,27.77142857142857,1.8,7,4.719913686298705
2016-04-10,116.63857142857144,46.76714285714286,33.871428571428574,269.1428571428572,33.142857142857146,8.9,28.585714285714285,0.0,7,4.759080020487912
2016-04-17,98.47571428571428,47.58285714285715,22.518571428571427,259.2857142857143,30.285714285714285,12.8,30.62857142857143,0.0,7,4.589809962303264
2016-04-24,110.90857142857143,52.79285714285714,28.45,287.2857142857143,26.857142857142858,10.157142857142857,31.071428571428573,0.1,7,4.708706181077213
2016-05-01,145.14,78.42714285714285,30.068571428571428,340.42857142857144,20.428571428571427,9.12857142857143,31.185714285714287,0.2,7,4.977698793849991
2016-05-08,90.76428571428572,56.425714285714285,20.21857142857143,256.57142857142856,41.285714285714285,9.385714285714286,31.071428571428573,3.1,7,4.50826587909523
2016-05-15,93.10142857142856,58.25714285714286,18.74714285714285,255.8571428571429,39.57142857142857,9.342857142857143,33.25714285714286,1.7,7,4.533689528648954
2016-05-22,87.84,60.40428571428571,21.38142857142857,279.2857142857143,35.57142857142857,11.528571428571428,34.785714285714285,2.4,7,4.47551697776122
2016-05-29,99.15714285714286,44.11142857142857,13.675714285714289,295.42857142857144,48.71428571428572,10.485714285714286,32.81428571428571,18.1,7,4.596705893290225
2016-06-05,95.83857142857144,54.42285714285714,13.705714285714285,279.7142857142857,50.285714285714285,9.257142857142856,33.3,7.4,7,4.5626652284606735
2016-06-12,70.86714285714285,46.94,14.767142857142858,245.0,51.42857142857143,10.628571428571428,34.05714285714286,10.9,7,4.260806896744107
2016-06-19,81.25285714285714,35.57857142857143,9.732857142857142,258.2857142857143,61.0,11.257142857142856,32.44285714285714,19.3,7,4.397565985426743
2016-06-26,76.76285714285714,39.80571428571428,9.515714285714283,218.8571428571429,64.14285714285714,10.471428571428572,32.51428571428571,6.9,7,4.340720892214076
2016-07-03,67.28857142857143,35.5,8.799999999999999,168.14285714285714,75.71428571428571,8.9,30.52857142857143,130.9,7,4.208990406904594
2016-07-10,60.72285714285714,36.62714285714286,8.252857142857144,165.57142857142858,76.85714285714286,6.471428571428571,30.357142857142858,9.4,7,4.106320186375232
2016-07-17,60.72571428571429,27.868571428571425,7.597142857142857,157.85714285714286,87.0,7.357142857142857,28.17142857142857,203.5,7,4.106367237449181
2016-07-24,48.36714285714286,36.41,7.927142857142857,202.0,77.0,9.114285714285714,29.75714285714286,16.8,7,3.878820716600366
2016-07-31,52.09571428571429,42.28714285714285,9.067142857142857,143.85714285714286,88.42857142857143,7.857142857142857,27.185714285714287,71.6,7,3.953082685984552
2016-08-07,44.70285714285715,34.31285714285714,9.105714285714289,142.85714285714286,82.57142857142857,9.94285714285714,28.685714285714287,32.7,7,3.800037417761567
2016-08-14,42.097142857142856,34.96857142857143,9.092857142857143,129.14285714285714,87.14285714285714,8.0,27.65714285714285,72.8,7,3.739979872759299
2016-08-21,48.84285714285714,36.71857142857142,9.09142857142857,201.14285714285717,79.42857142857143,9.685714285714283,28.514285714285712,14.9,7,3.888608147589942
2016-08-28,46.371428571428574,31.91142857142857,8.52,125.57142857142856,83.28571428571429,8.457142857142857,28.328571428571426,28.5,7,3.8366835060251776
2016-09-04,45.362857142857145,41.19,9.262857142857143,160.0,83.28571428571429,8.642857142857142,27.571428571428573,64.4,7,3.814693645594052
2016-09-11,56.83142857142857,38.49285714285714,11.314285714285717,276.0,67.85714285714286,13.2,28.5,0.2,7,4.040089492621601
2016-09-18,67.04285714285714,50.63142857142857,11.34142857142857,207.8571428571429,73.0,6.514285714285714,28.7,0.1,7,4.205332073745058
2016-09-25,65.76285714285714,62.07285714285714,15.03,199.42857142857144,75.57142857142857,7.057142857142857,28.37142857142857,2.2,7,4.1860551978402345
2016-10-02,90.33285714285716,67.36714285714285,15.977142857142857,226.14285714285717,72.85714285714286,5.628571428571428,29.042857142857144,0.6,7,4.503501260716411
2016-10-09,121.87571428571428,79.27428571428571,14.694285714285714,325.7142857142857,73.57142857142857,5.471428571428571,28.485714285714288,11.1,7,4.8030017901066975
2016-10-16,119.09857142857145,88.87571428571428,20.09,396.57142857142856,51.285714285714285,8.171428571428573,26.057142857142857,0.0,7,4.779951481566995
2016-10-23,153.06857142857143,90.68714285714285,23.662857142857145,450.57142857142856,48.142857142857146,9.2,25.428571428571427,0.0,7,5.030886000261812
2016-10-30,258.6485714285714,113.81142857142858,30.94142857142857,495.2857142857143,52.71428571428572,7.985714285714287,24.3,0.0,7,5.555470273250708
2016-11-06,495.1528571428572,129.32714285714286,33.10142857142857,578.1428571428571,62.57142857142857,6.528571428571429,22.842857142857145,0.0,7,6.204866517207873
2016-11-13,318.20714285714286,120.10428571428572,31.10428571428572,522.5714285714286,57.0,8.414285714285715,21.67142857142857,0.0,7,5.762702563348607
2016-11-20,274.3428571428572,110.90714285714286,24.444285714285712,451.2857142857143,55.71428571428572,8.057142857142857,20.385714285714283,0.0,7,5.614378627601472
2016-11-27,198.74857142857144,94.11428571428571,24.40285714285714,403.7142857142857,50.142857142857146,12.528571428571428,20.928571428571427,0.0,7,5.292040565727836
2016-12-04,222.4414285714286,100.55428571428573,23.294285714285717,395.0,62.142857142857146,7.542857142857143,19.1,0.0,7,5.404663824576337
2016-12-11,243.45142857142855,72.98,22.83857142857143,413.1428571428572,70.28571428571429,5.828571428571428,18.3,0.0,7,5.494917450639543
2016-12-18,200.69142857142856,77.47714285714287,21.58428571428572,401.0,66.28571428571429,8.428571428571429,16.557142857142857,0.0,7,5.301768547224268
2016-12-25,246.53857142857143,85.98,21.821428571428573,420.57142857142856,64.42857142857143,10.285714285714286,16.45714285714286,0.0,7,5.507518457625249
2017-01-01,230.7142857142857,83.20285714285714,23.92142857142857,383.8571428571428,74.14285714285714,9.171428571428573,15.814285714285717,0.0,7,5.441180086601444
2017-01-08,207.45285714285717,74.51142857142858,24.40142857142857,359.85714285714283,79.14285714285714,7.728571428571429,15.7,7.2,7,5.33490411936592
2017-01-15,196.74571428571429,72.05571428571429,19.947142857142858,372.2857142857143,63.85714285714285,9.057142857142855,11.342857142857143,0.0,7,5.281912104522604
2017-01-22,238.02714285714288,60.862857142857145,19.90428571428572,375.4285714285714,69.14285714285714,10.485714285714286,12.928571428571429,0.3,7,5.472384712787015
2017-01-29,159.2057142857143,61.791428571428575,20.78428571428572,319.2857142857143,78.85714285714286,10.842857142857143,15.957142857142856,47.89999999999999,7,5.070197166520604
2017-02-05,177.6185714285714,72.30142857142857,19.53857142857143,360.1428571428572,81.14285714285714,9.142857142857142,15.571428571428571,3.2,7,5.179638393945697
2017-02-12,133.16857142857145,61.597142857142856,18.41142857142857,315.0,72.28571428571429,9.9,14.785714285714286,0.1,7,4.891615780029702
2017-02-19,139.42142857142858,75.59142857142857,20.335714285714285,319.2857142857143,64.42857142857143,10.471428571428572,18.842857142857145,0.0,7,4.9375012065373065
2017-02-26,244.8114285714286,56.74142857142857,15.677142857142858,372.0,50.0,12.62857142857143,19.285714285714285,0.0,7,5.500488234889247
2017-03-05,115.93714285714285,70.66714285714285,23.49571428571429,286.85714285714283,49.285714285714285,9.514285714285714,20.11428571428572,4.2,7,4.753048172319535
2017-03-12,87.95,45.30571428571428,22.762857142857143,197.42857142857144,59.85714285714285,10.214285714285714,18.37142857142857,14.9,7,4.476768471183568
2017-03-19,106.63428571428572,40.471428571428575,22.264285714285712,305.1428571428572,53.285714285714285,9.414285714285716,19.24285714285714,1.3,7,4.669405089609958
2017-03-26,136.82285714285717,69.07285714285715,22.12,362.0,46.85714285714285,11.971428571428572,24.957142857142856,0.2,7,4.918687075609021
2017-04-02,110.33714285714288,80.12285714285714,19.518571428571427,287.85714285714283,37.285714285714285,13.4,29.428571428571427,0.0,7,4.703540613519024
2017-04-09,90.86,72.84857142857143,24.142857142857142,300.57142857142856,32.857142857142854,13.828571428571427,27.514285714285712,1.1,7,4.509319860331257
2017-04-16,154.83714285714285,86.81428571428572,39.80428571428571,360.4285714285714,26.428571428571427,13.071428571428571,29.571428571428573,0.0,7,5.042373873312019
2017-04-23,133.07,90.84714285714286,36.51142857142857,359.42857142857144,34.42857142857143,10.085714285714284,32.74285714285714,2.0,7,4.890875305555651
2017-04-30,96.78857142857144,70.98,41.21857142857142,251.57142857142856,27.857142857142858,10.328571428571427,30.37142857142857,2.5,7,4.57252892355803
2017-05-07,167.48285714285717,86.28857142857143,48.71142857142858,378.1428571428572,25.142857142857142,9.014285714285714,32.05714285714286,0.0,7,5.120881000611694
2017-05-14,142.7271428571429,70.97714285714287,47.74285714285714,373.0,32.857142857142854,10.714285714285714,33.642857142857146,3.3,7,4.960934715625462
2017-05-21,144.9042857142857,57.08142857142857,42.887142857142855,326.85714285714283,33.714285714285715,9.242857142857144,32.885714285714286,2.1,7,4.976073425937455
2017-05-28,94.82285714285716,67.01857142857143,38.285714285714285,269.2857142857143,42.142857142857146,10.9,32.77142857142857,1.7000000000000002,7,4.5520104893007165
2017-06-04,90.08142857142856,90.03142857142858,24.107142857142858,230.42857142857144,47.71428571428572,11.2,32.471428571428575,3.1,7,4.500714023184685
2017-06-11,58.47714285714285,72.28571428571429,19.55,162.85714285714286,47.285714285714285,10.7,33.3,5.8,7,4.06863595749599
2017-06-18,58.12714285714286,90.98142857142857,,101.42857142857144,48.285714285714285,9.385714285714286,32.3,13.2,7,4.06263272958742
2017-06-25,57.142857142857146,70.64,,123.16666666666669,66.14285714285714,7.971428571428571,30.414285714285715,23.8,7,4.045554398052669
2017-07-02,32.95,37.53714285714285,,68.71428571428571,77.71428571428571,10.185714285714283,29.7,69.1,7,3.4949912609485163
2017-07-09,58.0,19.357142857142858,,106.42857142857144,73.0,10.0,30.571428571428573,10.5,7,4.060443010546419
2017-07-16,31.555714285714288,39.23285714285714,,54.85714285714285,72.42857142857143,11.985714285714286,29.82857142857143,18.8,7,3.451754690993422
2017-07-23,31.482857142857146,67.71428571428571,,74.57142857142857,78.14285714285714,11.514285714285714,29.557142857142857,38.9,7,3.4494431800043177
2017-07-30,21.16,21.835714285714285,,37.71428571428572,79.28571428571429,13.114285714285714,28.557142857142857,19.5,7,3.052112606990099
2017-08-06,35.28142857142857,31.965714285714284,,57.0,80.28571428571429,9.471428571428572,28.514285714285712,31.8,7,3.563356722706227
2017-08-13,37.60285714285715,47.66571428571428,,74.83333333333333,79.0,11.685714285714283,29.1,58.7,7,3.627080035350864
2017-08-20,33.62428571428571,57.36,,63.5,70.42857142857143,11.457142857142856,29.985714285714288,7.5,7,3.515248594998551
2017-08-27,43.39857142857142,37.54571428571428,,68.0,83.71428571428571,7.3,28.414285714285715,52.9,7,3.77042652417224
2017-09-03,26.428571428571427,47.19,2.34,86.8,84.42857142857143,11.385714285714286,27.085714285714285,97.5,7,3.2744456760230114
2017-09-10,47.17714285714286,24.232857142857146,,96.14285714285714,77.85714285714286,7.8,28.557142857142857,2.3000000000000003,7,3.85390951379783
2017-09-17,59.26285714285715,26.875714285714285,,123.85714285714286,70.57142857142857,7.185714285714285,29.3,0.0,7,4.08198275466622
2017-09-24,44.027142857142856,27.665714285714284,,106.85714285714286,76.71428571428571,9.257142857142856,27.557142857142857,30.5,7,3.7848063268409686
2017-10-01,72.08571428571429,28.41428571428571,6.183333333333334,145.14285714285714,66.14285714285714,7.171428571428572,28.428571428571427,0.0,7,4.277855887151644
2017-10-08,76.91285714285713,26.04142857142857,13.23,168.28571428571428,59.0,7.6,28.042857142857144,0.0,7,4.342673055551451
2017-10-15,122.44714285714284,30.00714285714286,11.948571428571428,260.2857142857143,55.42857142857143,7.142857142857143,28.0,0.0,7,4.807679449987064
2017-10-22,198.3271428571429,56.14857142857143,24.56,358.2857142857143,55.42857142857143,7.871428571428572,27.142857142857142,0.0,7,5.289917903905407
2017-10-29,183.8942857142857,75.32285714285715,24.724285714285717,352.0,55.0,7.257142857142857,24.914285714285715,0.0,7,5.214361058339501
2017-11-05,187.99571428571429,53.06428571428571,18.564285714285717,340.0,66.57142857142857,6.328571428571428,23.7,0.0,7,5.236419166217525
2017-11-12,438.44714285714286,73.00857142857143,17.107142857142858,563.1428571428571,68.85714285714286,7.171428571428572,22.3,0.0,7,6.08323926374192
2017-11-19,202.21142857142857,52.97571428571428,16.58857142857143,382.2857142857143,64.85714285714286,9.828571428571427,20.27142857142857,0.4,7,5.309313826113883
2017-11-26,185.72,60.77,17.61857142857143,345.85714285714283,51.285714285714285,10.685714285714283,16.814285714285713,0.0,7,5.224240163151721
2017-12-03,205.89714285714285,64.69714285714285,18.99285714285714,372.2857142857143,59.0,7.085714285714286,17.385714285714286,0.0,7,5.3273767375758485
2017-12-10,173.3457142857143,62.12571428571429,21.34142857142857,326.42857142857144,50.285714285714285,8.12857142857143,17.02857142857143,0.1,7,5.155287948927893
2017-12-17,130.51142857142858,42.28428571428572,12.205714285714285,277.1428571428572,69.85714285714286,10.342857142857143,14.428571428571429,7.699999999999999,7,4.871460798188248
2017-12-24,191.21714285714285,56.71857142857142,21.67,327.2857142857143,64.0,11.271428571428572,15.628571428571428,0.0,7,5.253409655892827
2017-12-31,251.98142857142852,62.77857142857143,22.722857142857144,402.57142857142856,72.28571428571429,7.857142857142857,14.385714285714286,0.0,7,5.529355388650604
2018-01-07,247.29857142857145,56.05714285714286,14.76142857142857,412.1428571428572,71.71428571428571,7.514285714285714,12.385714285714286,0.0,7,5.510596397836895
2018-01-14,188.26,60.36,20.875714285714285,344.57142857142856,66.85714285714286,11.171428571428573,13.385714285714286,0.0,7,5.237823986119074
2018-01-21,197.46,47.81714285714286,18.187142857142856,357.57142857142856,66.42857142857143,9.94285714285714,14.485714285714286,0.0,7,5.285536032183304
2018-01-28,148.48857142857145,44.29714285714285,11.545714285714284,305.57142857142856,77.0,9.357142857142858,12.957142857142856,6.8,7,5.000507995204216
2018-02-04,137.04714285714286,51.98857142857143,13.821428571428571,296.42857142857144,66.28571428571429,12.071428571428571,16.085714285714285,0.0,7,4.92032497508269
2018-02-11,169.39,69.32142857142857,14.38,337.2857142857143,55.57142857142857,9.685714285714283,15.185714285714283,1.6,7,5.1322037485982905
2018-02-18,103.70857142857145,43.17,11.285714285714286,231.7142857142857,68.57142857142857,12.571428571428571,16.685714285714287,2.9,7,4.641584767832887
2018-02-25,158.08285714285714,67.9,15.047142857142855,333.0,64.14285714285714,7.871428571428572,20.557142857142857,2.2,7,5.063119307867456
2018-03-04,104.86,44.52571428571429,12.454285714285716,236.14285714285717,62.0,10.357142857142858,21.74285714285714,1.2,7,4.652626127144386
2018-03-11,96.94857142857144,50.01714285714286,14.97,215.14285714285717,52.42857142857143,10.3,21.914285714285715,1.1,7,4.574180646444166
2018-03-18,102.21428571428572,45.901428571428575,16.518571428571427,248.8571428571429,44.285714285714285,10.228571428571428,23.714285714285715,0.0,7,4.627071449941192
2018-03-25,90.97,40.69857142857143,17.407142857142855,212.14285714285717,49.71428571428572,9.571428571428571,23.82857142857143,2.1,7,4.510529781833971
2018-04-01,97.72857142857144,49.01714285714286,16.321428571428573,242.8571428571429,39.85714285714285,11.885714285714286,26.62857142857143,0.0,7,4.582193956711639
2018-04-08,94.45285714285714,47.00714285714286,15.87,230.28571428571428,48.85714285714285,8.957142857142857,28.0,9.6,7,4.548100843811397
2018-04-15,75.25,48.53714285714285,13.05714285714286,189.42857142857144,50.85714285714285,9.357142857142858,26.457142857142856,9.3,7,4.3208159036289855
2018-04-22,92.28,47.05857142857143,15.598571428571429,291.0,30.428571428571427,12.857142857142858,28.97142857142857,7.800000000000001,7,4.524827433305553
2018-04-29,103.68999999999998,55.14428571428572,14.904285714285717,279.0,30.428571428571427,11.37142857142857,30.728571428571428,2.5,7,4.6414056785701865
2018-05-06,68.93714285714286,39.51142857142857,10.484285714285717,188.8571428571429,49.57142857142857,13.400000000000002,30.042857142857144,17.1,7,4.233195116324223
2018-05-13,99.39285714285714,50.201428571428565,13.35142857142857,255.42857142857144,42.71428571428572,9.1,30.057142857142857,10.6,7,4.599080251350687
2018-05-20,83.68285714285715,47.33142857142857,12.165714285714284,219.42857142857144,38.85714285714285,8.042857142857143,31.9,1.9,7,4.427034143410322
2018-05-27,98.57714285714285,59.86714285714286,14.694285714285714,256.57142857142856,21.714285714285715,10.028571428571428,34.614285714285714,0.1,7,4.59083941787023
2018-06-03,80.00142857142858,39.892857142857146,10.124285714285715,229.57142857142856,43.57142857142857,13.44285714285714,33.67142857142857,5.5,7,4.382044491657302
2018-06-10,64.88285714285715,30.878571428571423,8.085714285714285,161.14285714285714,55.285714285714285,12.771428571428572,33.642857142857146,18.6,7,4.17258344618121
2018-06-17,152.4042857142857,27.15428571428572,7.225714285714285,422.0,43.142857142857146,14.785714285714286,34.857142857142854,0.2,7,5.026536764341959
2018-06-24,68.25857142857143,35.142857142857146,10.254285714285714,198.8571428571429,44.142857142857146,7.614285714285714,34.57142857142857,0.6,7,4.223303014876486
2018-07-01,38.87571428571429,31.552857142857142,10.24,118.0,68.14285714285714,11.7,30.957142857142856,58.1,7,3.660369744239649
2018-07-08,51.74428571428571,34.745714285714286,10.354285714285714,138.42857142857142,68.85714285714286,8.257142857142856,30.97142857142857,20.7,7,3.946314005068647
2018-07-15,43.470000000000006,31.69142857142857,10.937142857142858,120.85714285714286,76.14285714285714,9.314285714285717,30.585714285714285,50.8,7,3.772071045000701
2018-07-22,36.80857142857143,31.198571428571427,10.477142857142857,101.57142857142856,84.14285714285714,7.071428571428571,29.27142857142857,99.7,7,3.605730737308065
2018-07-29,34.582857142857144,25.798571428571428,9.788571428571428,85.71428571428571,85.0,7.657142857142857,28.342857142857145,50.5,7,3.5433581009847326
2018-08-05,59.50428571428571,26.415714285714284,9.565714285714288,186.28571428571428,72.0,12.014285714285714,29.885714285714283,6.8,7,4.086048338769158
2018-08-12,39.05428571428571,26.47714285714286,9.565714285714288,115.42857142857144,83.57142857142857,8.028571428571428,28.37142857142857,44.0,7,3.6649526196691937
2018-08-19,38.74142857142857,27.167142857142856,9.872857142857145,108.57142857142856,82.71428571428571,7.014285714285714,29.142857142857142,29.0,7,3.6569095331747534
2018-08-26,31.807142857142857,25.798571428571428,10.961428571428572,99.14285714285714,83.57142857142857,8.028571428571428,28.857142857142858,41.2,7,3.459690882712398
2018-09-02,37.85428571428572,25.91857142857143,10.267142857142858,103.28571428571428,86.85714285714286,6.042857142857144,28.085714285714285,63.3,7,3.633744202384664
2018-09-09,41.95,30.46,10.517142857142858,108.57142857142856,86.57142857142857,8.257142857142856,27.342857142857145,42.8,7,3.736478432913215
2018-09-16,33.33,26.005714285714284,10.945714285714288,107.14285714285714,74.71428571428571,10.114285714285714,28.0,5.8,7,3.506457892319648
2018-09-23,49.20857142857143,28.967142857142854,12.335714285714284,131.28571428571428,76.28571428571429,11.685714285714289,27.042857142857144,72.4,7,3.8960678243522873
2018-09-30,57.55857142857143,35.12714285714286,12.11,140.14285714285714,79.42857142857143,9.042857142857144,26.32857142857143,13.7,7,4.05280306288858
2018-10-07,83.38714285714286,44.47571428571428,13.964285714285714,199.14285714285717,68.42857142857143,6.7,26.414285714285715,1.0,7,4.423494135096081
2018-10-14,96.91142857142856,48.23285714285714,16.704285714285714,238.28571428571428,70.71428571428571,8.542857142857143,24.542857142857144,1.5,7,4.573797453855727
2018-10-21,140.48285714285714,56.31285714285714,18.785714285714285,313.2857142857143,62.142857142857146,7.514285714285714,24.585714285714285,0.4,7,4.945085468111484
2018-10-28,171.1542857142857,68.25142857142858,19.56714285714286,353.2857142857143,57.142857142857146,7.542857142857143,23.014285714285712,0.0,7,5.142565405353804
2018-11-04,202.76142857142852,59.98285714285714,17.752857142857142,384.2857142857143,63.85714285714285,7.585714285714286,23.25714285714286,0.1,7,5.312030059206812
2018-11-11,283.1485714285714,60.00571428571429,18.21857142857143,425.0,55.0,7.3,20.342857142857145,0.0,7,5.645971747265686
2018-11-18,173.0885714285714,58.56428571428571,16.004285714285714,346.7142857142857,67.14285714285714,8.757142857142856,20.457142857142856,1.8000000000000005,7,5.15380343705958
2018-11-25,168.86714285714285,60.74285714285714,15.944285714285714,334.0,60.71428571428572,9.928571428571429,19.571428571428573,0.0,7,5.129112268815404
2018-12-02,186.70857142857145,65.83857142857143,15.978571428571428,360.1428571428572,67.57142857142857,7.542857142857143,18.52857142857143,0.0,7,5.22954895966294
2018-12-09,201.8728571428572,65.41,16.12,377.1428571428572,67.14285714285714,6.6,16.557142857142857,0.0,7,5.30763807914836
2018-12-16,175.70142857142858,53.790000000000006,14.505714285714284,345.57142857142856,70.85714285714286,8.357142857142858,14.44285714285714,1.0,7,5.168786125902334
2018-12-23,261.5357142857143,67.78999999999999,17.367142857142856,421.1428571428572,68.57142857142857,8.32857142857143,12.485714285714286,0.0,7,5.566570848885866
2018-12-30,287.3928571428572,68.93428571428572,16.657142857142855,461.7142857142857,64.28571428571429,8.6,12.185714285714283,0.0,7,5.660850119970929
2019-01-06,282.41142857142853,64.44,15.857142857142858,466.4285714285714,71.14285714285714,8.742857142857144,13.071428571428571,2.3,7,5.64336497424579
2019-01-13,215.72,62.43857142857143,16.818571428571428,379.4285714285714,70.57142857142857,8.614285714285714,13.028571428571428,0.0,7,5.373981270469026
2019-01-20,239.19571428571427,73.66,17.981428571428573,399.1428571428572,65.42857142857143,9.014285714285714,13.228571428571428,0.0,7,5.477282105050224
2019-01-27,116.32714285714285,45.36857142857143,14.734285714285717,256.42857142857144,77.42857142857143,10.542857142857144,13.05714285714286,23.9,7,4.756406418856059
2019-02-03,166.56714285714287,50.167142857142856,17.232857142857142,332.42857142857144,70.42857142857143,10.6,12.271428571428572,0.8,7,5.115398488536135
2019-02-10,134.56428571428572,48.12857142857143,15.067142857142857,270.57142857142856,76.0,10.885714285714284,14.357142857142858,22.3,7,4.90204204555607
2019-02-17,152.75857142857143,52.61714285714286,16.29,317.2857142857143,79.0,8.614285714285714,15.157142857142857,9.0,7,5.028858710576035
2019-02-24,90.08714285714288,46.70285714285715,16.937142857142856,207.0,72.42857142857143,11.44285714285714,16.842857142857145,3.3000000000000003,7,4.500777455843011
2019-03-03,80.32000000000001,47.970000000000006,15.957142857142856,185.14285714285717,71.42857142857143,8.642857142857142,14.642857142857142,24.9,7,4.38601865594342
2019-03-10,86.03,44.87285714285714,15.95142857142857,196.8571428571429,64.71428571428571,9.44285714285714,17.32857142857143,0.2,7,4.454696072633257
2019-03-17,82.42142857142858,46.42142857142857,17.73857142857143,187.42857142857144,59.71428571428572,10.585714285714284,18.74285714285714,2.0,7,4.411845458585364
2019-03-24,79.07571428571428,42.30142857142857,19.304285714285715,194.8571428571429,45.42857142857143,11.771428571428572,22.428571428571427,0.0,7,4.370405802166587
2019-03-31,87.09142857142857,48.29571428571428,20.78142857142857,206.14285714285717,52.57142857142857,9.842857142857143,25.0,0.5,7,4.466958469962336
2019-04-07,104.12285714285711,52.98571428571428,24.064285714285717,240.42857142857144,41.85714285714285,9.485714285714286,27.385714285714283,0.0,7,4.645571520614807
2019-04-14,72.85857142857142,45.52857142857143,20.06142857142857,215.7142857142857,41.142857142857146,10.214285714285714,29.285714285714285,0.2,7,4.288520184313964
2019-04-21,61.77,43.51857142857143,18.62142857142857,164.28571428571428,51.285714285714285,9.55714285714286,25.885714285714283,5.3,7,4.123417809707807
2019-04-28,88.33,49.71857142857142,22.842857142857145,246.57142857142856,31.428571428571427,12.457142857142856,32.528571428571425,0.0,7,4.4810798007570405
2019-05-05,85.77428571428571,54.637142857142855,22.035714285714285,241.14285714285717,24.428571428571427,11.771428571428572,32.214285714285715,0.5,7,4.451719261275106
2019-05-12,129.04857142857142,53.33,22.05,329.57142857142856,22.428571428571427,13.62857142857143,33.07142857142857,0.0,7,4.860188856196892
2019-05-19,86.87,46.05857142857143,17.82,225.7142857142857,46.142857142857146,8.914285714285715,29.82857142857143,3.0000000000000004,7,4.464412748271829
2019-05-26,67.29142857142857,46.42857142857143,17.36857142857143,175.42857142857142,36.42857142857143,11.3,31.985714285714288,0.0,7,4.209032867045144
2019-06-02,78.25999999999999,57.04285714285714,20.085714285714285,220.42857142857144,25.285714285714285,11.257142857142856,35.05714285714286,0.0,7,4.360036616782266
2019-06-09,70.20857142857143,43.28857142857142,15.418571428571427,208.0,37.57142857142857,10.757142857142856,35.285714285714285,0.8,7,4.251470403700252
2019-06-16,69.01285714285714,40.16571428571429,13.151428571428571,229.0,31.714285714285715,13.171428571428567,35.84285714285714,2.2,7,4.2342928226427015
2019-06-23,53.53857142857142,34.29714285714286,11.252857142857142,158.42857142857142,48.142857142857146,10.257142857142856,32.68571428571429,1.7,7,3.980402355415933
2019-06-30,56.73285714285714,34.49428571428572,12.602857142857143,177.57142857142858,45.57142857142857,10.6,34.51428571428571,5.999999999999999,7,4.038353533949284
2019-07-07,46.77428571428572,29.795714285714286,10.805714285714286,140.42857142857142,59.142857142857146,8.028571428571428,33.07142857142857,14.3,7,3.8453336013708825
2019-07-14,62.93857142857143,28.52285714285714,9.732857142857142,222.7142857142857,60.142857142857146,12.485714285714286,32.48571428571429,16.5,7,4.142159194025184
2019-07-21,42.65,33.152857142857144,9.311428571428571,127.0,81.14285714285714,7.1571428571428575,28.585714285714285,82.9,7,3.753027273937688
2019-07-28,42.49,32.22428571428571,8.801428571428572,115.0,82.85714285714286,9.485714285714286,29.0,68.6,7,3.74926875412672
2019-08-04,34.18857142857143,28.53428571428572,9.105714285714283,94.28571428571428,82.42857142857143,9.328571428571427,28.9,28.6,7,3.531891419466518
2019-08-11,28.487142857142857,28.58714285714285,9.21,93.85714285714286,82.14285714285714,11.028571428571428,29.0,49.5,7,3.3494528576662868
2019-08-18,20.78142857142857,24.53857142857143,8.338571428571429,79.57142857142857,85.0,12.05714285714286,28.071428571428573,90.5,7,3.0340597307300574
2019-08-25,45.11857142857143,34.87571428571429,8.33,117.14285714285714,83.0,6.9,28.6,23.700000000000003,7,3.8092939450877537
2019-09-01,39.64142857142857,33.801428571428566,9.045714285714286,109.85714285714286,80.85714285714286,7.557142857142857,29.75714285714286,14.1,7,3.6798747474458255
2019-09-08,46.80571428571428,31.755714285714284,9.118571428571428,115.57142857142856,82.71428571428571,7.028571428571428,29.385714285714283,17.9,7,3.846005295592088
2019-09-15,50.56857142857143,31.694285714285712,8.797142857142857,120.14285714285714,77.57142857142857,8.685714285714287,29.814285714285717,7.6,7,3.9233302653072943
2019-09-22,39.85142857142857,31.947142857142858,9.357142857142858,106.42857142857144,81.0,8.414285714285715,27.97142857142857,28.7,7,3.6851582533120815
2019-09-29,25.55,27.96857142857143,9.66,86.14285714285714,80.42857142857143,11.614285714285714,26.514285714285712,17.5,7,3.2406373166497136
2019-10-06,43.25571428571429,32.464285714285715,8.732857142857142,109.42857142857144,74.42857142857143,7.428571428571429,26.142857142857142,15.6,7,3.7671293468635647
2019-10-13,87.52285714285713,44.362857142857145,11.131428571428572,198.42857142857144,57.42857142857143,7.028571428571429,26.6,0.0,7,4.4718999837401885
2019-10-20,111.85142857142856,49.82857142857143,12.324285714285711,267.57142857142856,60.0,7.342857142857143,26.61428571428572,5.2,7,4.717171460062251
2019-10-27,140.25571428571428,54.81857142857143,13.842857142857143,297.1428571428572,57.142857142857146,8.657142857142857,24.485714285714288,0.0,7,4.943467287142965
2019-11-03,353.36857142857144,60.15714285714286,14.258571428571427,495.8571428571428,65.57142857142857,7.685714285714285,24.457142857142856,0.2,7,5.867511623923472
2019-11-10,176.22285714285712,48.91571428571429,12.564285714285717,354.85714285714283,63.42857142857143,10.057142857142855,22.357142857142858,2.2,7,5.171749427806506
2019-11-17,297.9271428571428,59.881428571428565,14.111428571428572,460.8571428571428,64.85714285714286,10.228571428571428,20.942857142857143,0.0,7,5.696848969557004
2019-11-24,152.52142857142854,61.91428571428572,13.742857142857144,308.7142857142857,64.71428571428571,9.014285714285714,19.985714285714288,0.0,7,5.02730510139861
2019-12-01,86.82571428571428,45.67,11.762857142857143,192.28571428571428,74.14285714285714,8.571428571428571,18.32857142857143,23.0,7,4.46390282532494
2019-12-08,204.55428571428573,69.42714285714285,13.287142857142856,358.85714285714283,74.57142857142857,7.528571428571429,15.471428571428572,0.0,7,5.320833396071274
2019-12-15,184.0914285714286,59.03285714285715,11.084285714285716,336.42857142857144,77.71428571428571,8.342857142857143,14.714285714285714,9.6,7,5.215432528607776
2019-12-22,185.57857142857145,45.370000000000005,8.165714285714285,321.57142857142856,80.28571428571429,8.071428571428571,12.357142857142858,0.2,7,5.223478358021557
2019-12-29,234.32857142857145,49.962857142857146,8.291428571428572,381.8571428571428,86.71428571428571,8.071428571428571,8.542857142857143,0.0,7,5.456724281863127
2020-01-05,271.12142857142857,56.237142857142864,13.998571428571427,435.1428571428572,79.85714285714286,7.328571428571428,11.157142857142857,0.6,7,5.602566796432998
2020-01-12,139.47714285714284,46.47714285714285,10.495714285714286,292.57142857142856,80.14285714285714,9.585714285714284,11.857142857142858,19.6,7,4.937900737350032
2020-01-19,134.74571428571429,42.70428571428572,9.997142857142858,294.42857142857144,85.85714285714286,8.371428571428572,12.94285714285714,28.8,7,4.903389404353555
2020-01-26,150.86714285714285,45.31428571428571,11.064285714285717,292.42857142857144,75.85714285714286,10.628571428571428,12.6,0.0,7,5.016399600892737
2020-02-02,115.5657142857143,47.60857142857143,10.855714285714283,254.42857142857144,77.57142857142857,9.471428571428572,12.885714285714286,16.9,7,4.74983932302307
2020-02-09,149.54571428571427,54.34857142857143,13.612857142857145,312.2857142857143,74.0,8.3,12.5,0.1,7,5.007602127264552
2020-02-16,129.7642857142857,50.06714285714286,16.094285714285714,273.0,61.285714285714285,14.0,16.414285714285715,0.0,7,4.86571961782944
2020-02-23,106.28,48.82428571428572,16.43285714285714,237.57142857142856,66.42857142857143,13.342857142857143,17.742857142857144,18.8,7,4.666077120891613
2020-03-01,90.53571428571428,42.34428571428571,14.611428571428572,207.0,76.85714285714286,10.157142857142857,18.77142857142857,9.2,7,4.50574440585008
2020-03-08,62.044285714285714,40.25714285714286,13.385714285714286,149.28571428571428,78.42857142857143,10.37142857142857,17.928571428571427,39.2,7,4.1278484157787485
2020-03-15,60.51714285714286,35.03142857142858,14.138571428571428,143.14285714285714,71.57142857142857,10.271428571428572,17.685714285714287,16.9,7,4.102926677910539
2020-03-22,77.45285714285716,43.385714285714286,16.762857142857143,182.42857142857144,70.14285714285714,8.642857142857142,20.428571428571427,2.2,7,4.349669456342003
2020-03-29,38.48285714285714,20.02285714285714,12.428571428571429,89.57142857142857,64.28571428571429,10.214285714285714,22.571428571428573,6.8,7,3.6502128731153554
2020-04-05,36.53142857142857,19.824285714285715,12.75,84.28571428571429,52.142857142857146,11.2,23.057142857142857,0.1,7,3.5981729468432126
2020-04-12,44.01857142857143,21.702857142857145,15.214285714285714,107.57142857142856,45.0,10.571428571428571,25.985714285714288,0.4,7,3.784611622790509
2020-04-19,48.34857142857143,21.38142857142857,15.918571428571427,128.14285714285714,38.71428571428572,10.9,29.514285714285712,0.0,7,3.878436675000987
2020-04-26,48.89,22.224285714285717,16.10571428571429,121.57142857142856,45.285714285714285,9.071428571428571,27.65714285714285,1.9,7,3.889572876590554
2020-05-03,43.191428571428574,16.832857142857144,16.021428571428572,118.71428571428572,59.142857142857146,12.314285714285711,28.185714285714287,25.9,7,3.765642062865248
2020-05-10,46.7,19.132857142857144,13.838571428571427,127.85714285714286,48.57142857142857,9.285714285714286,29.3,0.8,7,3.843744164674852
2020-05-17,62.76571428571429,23.722857142857144,14.98857142857143,146.14285714285714,46.57142857142857,9.94285714285714,30.485714285714288,0.6,7,4.139408973524293
2020-05-24,79.43285714285715,36.675714285714285,20.09714285714286,197.14285714285717,26.142857142857142,10.314285714285717,32.957142857142856,0.0,7,4.374912100574184
2020-05-31,38.33571428571429,23.90571428571429,13.321428571428571,133.28571428571428,41.57142857142857,13.385714285714286,32.457142857142856,9.9,7,3.646381949567525
2020-06-07,46.19571428571429,25.667142857142856,13.664285714285716,117.42857142857144,60.142857142857146,7.214285714285714,29.342857142857145,1.2,7,3.832887029406333
2020-06-14,58.957142857142856,29.22714285714286,13.537142857142856,139.57142857142858,54.142857142857146,7.7,33.142857142857146,0.1,7,4.076810787703223
2020-06-21,41.85857142857143,21.09142857142857,11.764285714285714,124.0,51.142857142857146,10.271428571428572,34.08571428571428,1.3,7,3.734296589072182
2020-06-28,41.01428571428572,20.052857142857142,11.03,108.28571428571428,62.285714285714285,10.885714285714286,32.385714285714286,7.8,7,3.713920438071705
```

## fc_backtest_forecasts.csv (1560 rows; fold = forecast year; mu, sd on the log scale; point forecast = exp(mu); sd empty only for none after round 2)
```
fold,model,date,actual,mu,sd
2017,Seasonal naive,2017-01-01,230.7142857142857,5.424572350201784,0.2935252627885994
2017,Seasonal naive,2017-01-08,207.4528571428572,5.673072867635633,0.2935252627885994
2017,Seasonal naive,2017-01-15,196.74571428571429,5.272955601553695,0.2935252627885994
2017,Seasonal naive,2017-01-22,238.02714285714288,5.6061381442692495,0.2935252627885994
2017,Seasonal naive,2017-01-29,159.2057142857143,5.6056602495177845,0.2935252627885994
2017,Seasonal naive,2017-02-05,177.6185714285714,5.080916224567838,0.2935252627885994
2017,Seasonal naive,2017-02-12,133.16857142857145,4.989820154382335,0.2935252627885994
2017,Seasonal naive,2017-02-19,139.42142857142858,4.918060417555802,0.2935252627885994
2017,Seasonal naive,2017-02-26,244.8114285714286,4.88149154060126,0.2935252627885994
2017,Seasonal naive,2017-03-05,115.93714285714285,4.90057592541159,0.2935252627885994
2017,Seasonal naive,2017-03-12,87.95,4.494988543542957,0.2935252627885994
2017,Seasonal naive,2017-03-19,106.63428571428572,4.351843530453547,0.2935252627885994
2017,Seasonal naive,2017-03-26,136.82285714285717,4.4741336378330745,0.2935252627885994
2017,Seasonal naive,2017-04-02,110.33714285714288,4.719913686298705,0.2935252627885994
2017,Seasonal naive,2017-04-09,90.86,4.759080020487912,0.2935252627885994
2017,Seasonal naive,2017-04-16,154.83714285714285,4.589809962303264,0.2935252627885994
2017,Seasonal naive,2017-04-23,133.07,4.708706181077213,0.2935252627885994
2017,Seasonal naive,2017-04-30,96.78857142857144,4.977698793849991,0.2935252627885994
2017,Seasonal naive,2017-05-07,167.48285714285717,4.50826587909523,0.2935252627885994
2017,Seasonal naive,2017-05-14,142.7271428571429,4.533689528648954,0.2935252627885994
2017,Seasonal naive,2017-05-21,144.9042857142857,4.47551697776122,0.2935252627885994
2017,Seasonal naive,2017-05-28,94.82285714285716,4.596705893290225,0.2935252627885994
2017,Seasonal naive,2017-06-04,90.08142857142856,4.5626652284606735,0.2935252627885994
2017,Seasonal naive,2017-06-11,58.47714285714285,4.260806896744107,0.2935252627885994
2017,Seasonal naive,2017-06-18,58.12714285714286,4.397565985426743,0.2935252627885994
2017,Seasonal naive,2017-06-25,57.142857142857146,4.340720892214076,0.2935252627885994
2017,Seasonal naive,2017-07-02,32.95,4.208990406904594,0.2935252627885994
2017,Seasonal naive,2017-07-09,58.0,4.106320186375232,0.2935252627885994
2017,Seasonal naive,2017-07-16,31.555714285714288,4.106367237449181,0.2935252627885994
2017,Seasonal naive,2017-07-23,31.482857142857146,3.878820716600366,0.2935252627885994
2017,Seasonal naive,2017-07-30,21.16,3.953082685984552,0.2935252627885994
2017,Seasonal naive,2017-08-06,35.28142857142857,3.800037417761567,0.2935252627885994
2017,Seasonal naive,2017-08-13,37.60285714285715,3.739979872759299,0.2935252627885994
2017,Seasonal naive,2017-08-20,33.62428571428571,3.888608147589942,0.2935252627885994
2017,Seasonal naive,2017-08-27,43.39857142857142,3.8366835060251776,0.2935252627885994
2017,Seasonal naive,2017-09-03,26.428571428571427,3.814693645594052,0.2935252627885994
2017,Seasonal naive,2017-09-10,47.17714285714286,4.040089492621601,0.2935252627885994
2017,Seasonal naive,2017-09-17,59.26285714285715,4.205332073745058,0.2935252627885994
2017,Seasonal naive,2017-09-24,44.027142857142856,4.1860551978402345,0.2935252627885994
2017,Seasonal naive,2017-10-01,72.08571428571429,4.503501260716411,0.2935252627885994
2017,Seasonal naive,2017-10-08,76.91285714285713,4.8030017901066975,0.2935252627885994
2017,Seasonal naive,2017-10-15,122.44714285714284,4.779951481566995,0.2935252627885994
2017,Seasonal naive,2017-10-22,198.3271428571429,5.030886000261812,0.2935252627885994
2017,Seasonal naive,2017-10-29,183.8942857142857,5.555470273250708,0.2935252627885994
2017,Seasonal naive,2017-11-05,187.99571428571429,6.204866517207873,0.2935252627885994
2017,Seasonal naive,2017-11-12,438.44714285714286,5.762702563348607,0.2935252627885994
2017,Seasonal naive,2017-11-19,202.21142857142857,5.614378627601472,0.2935252627885994
2017,Seasonal naive,2017-11-26,185.72,5.292040565727836,0.2935252627885994
2017,Seasonal naive,2017-12-03,205.89714285714285,5.404663824576337,0.2935252627885994
2017,Seasonal naive,2017-12-10,173.3457142857143,5.494917450639543,0.2935252627885994
2017,Seasonal naive,2017-12-17,130.51142857142858,5.301768547224268,0.2935252627885994
2017,Seasonal naive,2017-12-24,191.21714285714285,5.507518457625249,0.2935252627885994
2017,Climatology,2017-01-01,230.7142857142857,5.312465158286153,0.1543246814639469
2017,Climatology,2017-01-08,207.4528571428572,5.445645637464022,0.1543246814639469
2017,Climatology,2017-01-15,196.74571428571429,5.2755497074390885,0.1543246814639469
2017,Climatology,2017-01-22,238.02714285714288,5.42035833492514,0.1543246814639469
2017,Climatology,2017-01-29,159.2057142857143,5.328901508712694,0.1543246814639469
2017,Climatology,2017-02-05,177.6185714285714,5.086671074190454,0.1543246814639469
2017,Climatology,2017-02-12,133.16857142857145,4.999303060238789,0.1543246814639469
2017,Climatology,2017-02-19,139.42142857142858,5.000025118341554,0.1543246814639469
2017,Climatology,2017-02-26,244.8114285714286,4.962762383757507,0.1543246814639469
2017,Climatology,2017-03-05,115.93714285714285,4.883301873483066,0.1543246814639469
2017,Climatology,2017-03-12,87.95,4.453806830858239,0.1543246814639469
2017,Climatology,2017-03-19,106.63428571428572,4.400622530866001,0.1543246814639469
2017,Climatology,2017-03-26,136.82285714285717,4.357360068519439,0.1543246814639469
2017,Climatology,2017-04-02,110.33714285714288,4.63025743724717,0.1543246814639469
2017,Climatology,2017-04-09,90.86,4.512797795097862,0.1543246814639469
2017,Climatology,2017-04-16,154.83714285714285,4.558895254800113,0.1543246814639469
2017,Climatology,2017-04-23,133.07,4.6239369588823696,0.1543246814639469
2017,Climatology,2017-04-30,96.78857142857144,4.840224654088473,0.1543246814639469
2017,Climatology,2017-05-07,167.48285714285717,4.430165118642819,0.1543246814639469
2017,Climatology,2017-05-14,142.7271428571429,4.66197562052216,0.1543246814639469
2017,Climatology,2017-05-21,144.9042857142857,4.486025724604231,0.1543246814639469
2017,Climatology,2017-05-28,94.82285714285716,4.44814108115102,0.1543246814639469
2017,Climatology,2017-06-04,90.08142857142856,4.6209012801802025,0.1543246814639469
2017,Climatology,2017-06-11,58.47714285714285,4.228735821605577,0.1543246814639469
2017,Climatology,2017-06-18,58.12714285714286,4.490274494519968,0.1543246814639469
2017,Climatology,2017-06-25,57.142857142857146,4.503949807957337,0.1543246814639469
2017,Climatology,2017-07-02,32.95,4.309897686448151,0.1543246814639469
2017,Climatology,2017-07-09,58.0,4.204535837933481,0.1543246814639469
2017,Climatology,2017-07-16,31.555714285714288,4.016836433204242,0.1543246814639469
2017,Climatology,2017-07-23,31.482857142857146,4.008294799320423,0.1543246814639469
2017,Climatology,2017-07-30,21.16,3.830689769571084,0.1543246814639469
2017,Climatology,2017-08-06,35.28142857142857,3.644557423314578,0.1543246814639469
2017,Climatology,2017-08-13,37.60285714285715,3.923338202877103,0.1543246814639469
2017,Climatology,2017-08-20,33.62428571428571,4.0217326402665305,0.1543246814639469
2017,Climatology,2017-08-27,43.39857142857142,3.860035926743728,0.1543246814639469
2017,Climatology,2017-09-03,26.428571428571427,3.9456068114518006,0.1543246814639469
2017,Climatology,2017-09-10,47.17714285714286,4.209278113466985,0.1543246814639469
2017,Climatology,2017-09-17,59.26285714285715,4.213699762591812,0.1543246814639469
2017,Climatology,2017-09-24,44.027142857142856,4.322339525430501,0.1543246814639469
2017,Climatology,2017-10-01,72.08571428571429,4.321694044001896,0.1543246814639469
2017,Climatology,2017-10-08,76.91285714285713,4.652879745835973,0.1543246814639469
2017,Climatology,2017-10-15,122.44714285714284,4.877770856642746,0.1543246814639469
2017,Climatology,2017-10-22,198.3271428571429,4.862478127364415,0.1543246814639469
2017,Climatology,2017-10-29,183.8942857142857,5.308127675516218,0.1543246814639469
2017,Climatology,2017-11-05,187.99571428571429,5.610277842803404,0.1543246814639469
2017,Climatology,2017-11-12,438.44714285714286,5.614835545101827,0.1543246814639469
2017,Climatology,2017-11-19,202.21142857142857,5.5406554739672575,0.1543246814639469
2017,Climatology,2017-11-26,185.72,5.349106239055207,0.1543246814639469
2017,Climatology,2017-12-03,205.89714285714285,5.350464543499122,0.1543246814639469
2017,Climatology,2017-12-10,173.3457142857143,5.435689510272511,0.1543246814639469
2017,Climatology,2017-12-17,130.51142857142858,5.339167903260966,0.1543246814639469
2017,Climatology,2017-12-24,191.21714285714285,5.18386472681753,0.1543246814639469
2017,Climatology + AR(1),2017-01-01,230.7142857142857,5.423112446384211,0.1443701174171715
2017,Climatology + AR(1),2017-01-08,207.4528571428572,5.48347255307813,0.1525736465220863
2017,Climatology + AR(1),2017-01-15,196.74571428571429,5.288481570202944,0.1535038198616951
2017,Climatology + AR(1),2017-01-22,238.02714285714288,5.424779342343488,0.1536121659249456
2017,Climatology + AR(1),2017-01-29,159.2057142857143,5.330412915611298,0.1536248238456347
2017,Climatology + AR(1),2017-02-05,177.6185714285714,5.087187777872892,0.1536263031675802
2017,Climatology + AR(1),2017-02-12,133.16857142857145,4.99947970538689,0.153626476061881
2017,Climatology + AR(1),2017-02-19,139.42142857142858,5.000085507902163,0.1536264962688288
2017,Climatology + AR(1),2017-02-26,244.8114285714286,4.962783029096877,0.1536264986305084
2017,Climatology + AR(1),2017-03-05,115.93714285714285,4.8833089314916585,0.153626498906529
2017,Climatology + AR(1),2017-03-12,87.95,4.453809243774995,0.1536264989387887
2017,Climatology + AR(1),2017-03-19,106.63428571428572,4.400623355768266,0.1536264989425591
2017,Climatology + AR(1),2017-03-26,136.82285714285717,4.357360350528234,0.1536264989429998
2017,Climatology + AR(1),2017-04-02,110.33714285714288,4.630257533657331,0.1536264989430512
2017,Climatology + AR(1),2017-04-09,90.86,4.512797828057541,0.1536264989430573
2017,Climatology + AR(1),2017-04-16,154.83714285714285,4.558895266068017,0.153626498943058
2017,Climatology + AR(1),2017-04-23,133.07,4.62393696273452,0.1536264989430581
2017,Climatology + AR(1),2017-04-30,96.78857142857144,4.840224655405406,0.1536264989430581
2017,Climatology + AR(1),2017-05-07,167.48285714285717,4.430165119093037,0.1536264989430581
2017,Climatology + AR(1),2017-05-14,142.7271428571429,4.661975620676076,0.1536264989430581
2017,Climatology + AR(1),2017-05-21,144.9042857142857,4.48602572465685,0.1536264989430581
2017,Climatology + AR(1),2017-05-28,94.82285714285716,4.448141081169009,0.1536264989430581
2017,Climatology + AR(1),2017-06-04,90.08142857142856,4.620901280186352,0.1536264989430581
2017,Climatology + AR(1),2017-06-11,58.47714285714285,4.228735821607679,0.1536264989430581
2017,Climatology + AR(1),2017-06-18,58.12714285714286,4.490274494520687,0.1536264989430581
2017,Climatology + AR(1),2017-06-25,57.142857142857146,4.503949807957583,0.1536264989430581
2017,Climatology + AR(1),2017-07-02,32.95,4.309897686448236,0.1536264989430581
2017,Climatology + AR(1),2017-07-09,58.0,4.204535837933509,0.1536264989430581
2017,Climatology + AR(1),2017-07-16,31.555714285714288,4.016836433204252,0.1536264989430581
2017,Climatology + AR(1),2017-07-23,31.482857142857146,4.008294799320426,0.1536264989430581
2017,Climatology + AR(1),2017-07-30,21.16,3.830689769571085,0.1536264989430581
2017,Climatology + AR(1),2017-08-06,35.28142857142857,3.6445574233145774,0.1536264989430581
2017,Climatology + AR(1),2017-08-13,37.60285714285715,3.923338202877103,0.1536264989430581
2017,Climatology + AR(1),2017-08-20,33.62428571428571,4.0217326402665305,0.1536264989430581
2017,Climatology + AR(1),2017-08-27,43.39857142857142,3.860035926743728,0.1536264989430581
2017,Climatology + AR(1),2017-09-03,26.428571428571427,3.9456068114518006,0.1536264989430581
2017,Climatology + AR(1),2017-09-10,47.17714285714286,4.209278113466985,0.1536264989430581
2017,Climatology + AR(1),2017-09-17,59.26285714285715,4.213699762591812,0.1536264989430581
2017,Climatology + AR(1),2017-09-24,44.027142857142856,4.322339525430501,0.1536264989430581
2017,Climatology + AR(1),2017-10-01,72.08571428571429,4.321694044001896,0.1536264989430581
2017,Climatology + AR(1),2017-10-08,76.91285714285713,4.652879745835973,0.1536264989430581
2017,Climatology + AR(1),2017-10-15,122.44714285714284,4.877770856642746,0.1536264989430581
2017,Climatology + AR(1),2017-10-22,198.3271428571429,4.862478127364415,0.1536264989430581
2017,Climatology + AR(1),2017-10-29,183.8942857142857,5.308127675516218,0.1536264989430581
2017,Climatology + AR(1),2017-11-05,187.99571428571429,5.610277842803404,0.1536264989430581
2017,Climatology + AR(1),2017-11-12,438.44714285714286,5.614835545101827,0.1536264989430581
2017,Climatology + AR(1),2017-11-19,202.21142857142857,5.5406554739672575,0.1536264989430581
2017,Climatology + AR(1),2017-11-26,185.72,5.349106239055207,0.1536264989430581
2017,Climatology + AR(1),2017-12-03,205.89714285714285,5.350464543499122,0.1536264989430581
2017,Climatology + AR(1),2017-12-10,173.3457142857143,5.435689510272511,0.1536264989430581
2017,Climatology + AR(1),2017-12-17,130.51142857142858,5.339167903260966,0.1536264989430581
2017,Climatology + AR(1),2017-12-24,191.21714285714285,5.18386472681753,0.1536264989430581
2017,Linear regression,2017-01-01,230.7142857142857,5.4482209193639575,0.2276670741309367
2017,Linear regression,2017-01-08,207.4528571428572,5.411214937792379,0.2287482100603568
2017,Linear regression,2017-01-15,196.74571428571429,5.366038274538294,0.2298420297836624
2017,Linear regression,2017-01-22,238.02714285714288,5.312306467046801,0.2308617291374969
2017,Linear regression,2017-01-29,159.2057142857143,5.249809158984069,0.2317253835128816
2017,Linear regression,2017-02-05,177.6185714285714,5.178874563644115,0.232370451752145
2017,Linear regression,2017-02-12,133.16857142857145,5.100654660489251,0.232764246815766
2017,Linear regression,2017-02-19,139.42142857142858,5.01727725223012,0.2329080976041254
2017,Linear regression,2017-02-26,244.8114285714286,4.931830353648895,0.232834753687887
2017,Linear regression,2017-03-05,115.93714285714285,4.848169008861399,0.2326003079799676
2017,Linear regression,2017-03-12,87.95,4.770561181611868,0.2322730541501714
2017,Linear regression,2017-03-19,106.63428571428572,4.703214189512306,0.2319220097961778
2017,Linear regression,2017-03-26,136.82285714285717,4.64974281222571,0.2316073487699314
2017,Linear regression,2017-04-02,110.33714285714288,4.612651906931199,0.2313739803555017
2017,Linear regression,2017-04-09,90.86,4.592908355143422,0.2312484305852627
2017,Linear regression,2017-04-16,154.83714285714285,4.589668958964055,0.2312384361367025
2017,Linear regression,2017-04-23,133.07,4.600213366393227,0.2313344513522136
2017,Linear regression,2017-04-30,96.78857142857144,4.620106346827702,0.231512494545577
2017,Linear regression,2017-05-07,167.48285714285717,4.643584855947724,0.2317381119714673
2017,Linear regression,2017-05-14,142.7271428571429,4.664136010705171,0.2319713991003557
2017,Linear regression,2017-05-21,144.9042857142857,4.675206143619909,0.2321728499447665
2017,Linear regression,2017-05-28,94.82285714285716,4.670961949198742,0.2323094079431609
2017,Linear regression,2017-06-04,90.08142857142856,4.647014979645121,0.2323597250441751
2017,Linear regression,2017-06-11,58.47714285714285,4.6010218311886,0.2323175514760811
2017,Linear regression,2017-06-18,58.12714285714286,4.533084362610596,0.2321924827349215
2017,Linear regression,2017-06-25,57.142857142857146,4.445895894964354,0.2320078937278914
2017,Linear regression,2017-07-02,32.95,4.344608016984299,0.2317965631776996
2017,Linear regression,2017-07-09,58.0,4.23642490819104,0.2315949792189008
2017,Linear regression,2017-07-16,31.555714285714288,4.129964050042912,0.2314374588014335
2017,Linear regression,2017-07-23,31.482857142857146,4.034449893911502,0.2313510142456786
2017,Linear regression,2017-07-30,21.16,3.9588270688912544,0.2313515201638789
2017,Linear regression,2017-08-06,35.28142857142857,3.91088955785945,0.2314413942756642
2017,Linear regression,2017-08-13,37.60285714285715,3.896520716680287,0.231608858562037
2017,Linear regression,2017-08-20,33.62428571428571,3.919126239720844,0.2318288851212932
2017,Linear regression,2017-08-27,43.39857142857142,3.979319754146193,0.2320659966551842
2017,Linear regression,2017-09-03,26.428571428571427,4.074891415401575,0.2322789877687427
2017,Linear regression,2017-09-10,47.17714285714286,4.201057278280197,0.2324272656923213
2017,Linear regression,2017-09-17,59.26285714285715,4.350955320711706,0.2324779672393823
2017,Linear regression,2017-09-24,44.027142857142856,4.51632667452299,0.2324125348782438
2017,Linear regression,2017-10-01,72.08571428571429,4.688301141427807,0.2322312982947042
2017,Linear regression,2017-10-08,76.91285714285713,4.858196706938353,0.2319549605561867
2017,Linear regression,2017-10-15,122.44714285714284,5.018244486526939,0.2316226726667034
2017,Linear regression,2017-10-22,198.3271428571429,5.162162924444875,0.2312873312644703
2017,Linear regression,2017-10-29,183.8942857142857,5.285526359951189,0.2310094701798033
2017,Linear regression,2017-11-05,187.99571428571429,5.385900424469116,0.2308512996759711
2017,Linear regression,2017-11-12,438.44714285714286,5.46274655930332,0.2308719564802641
2017,Linear regression,2017-11-19,202.21142857142857,5.517126411177848,0.2311240656100076
2017,Linear regression,2017-11-26,185.72,5.5512603717456575,0.2316507641357678
2017,Linear regression,2017-12-03,205.89714285714285,5.568010173195883,0.2324819468049326
2017,Linear regression,2017-12-10,173.3457142857143,5.570361394451894,0.2336289818854459
2017,Linear regression,2017-12-17,130.51142857142858,5.560977421349445,0.2350783776295171
2017,Linear regression,2017-12-24,191.21714285714285,5.541882639104145,0.2367862689337253
2017,LSTM (small),2017-01-01,230.7142857142857,5.394306299674125,0.0280663774128252
2017,LSTM (small),2017-01-08,207.4528571428572,5.404015046237576,0.0280663774128252
2017,LSTM (small),2017-01-15,196.74571428571429,5.357218405150864,0.0280663774128252
2017,LSTM (small),2017-01-22,238.02714285714288,5.5647369614953215,0.0346171598584997
2017,LSTM (small),2017-01-29,159.2057142857143,5.328406419579286,0.0380964606371307
2017,LSTM (small),2017-02-05,177.6185714285714,5.05468478212098,0.0380964606371307
2017,LSTM (small),2017-02-12,133.16857142857145,5.020524826946454,0.0479296594903283
2017,LSTM (small),2017-02-19,139.42142857142858,5.061537001957378,0.0581093181729925
2017,LSTM (small),2017-02-26,244.8114285714286,4.991743821543103,0.0654937508657694
2017,LSTM (small),2017-03-05,115.93714285714285,4.85480058651914,0.0654937508657694
2017,LSTM (small),2017-03-12,87.95,4.413162195801879,0.0762736524683398
2017,LSTM (small),2017-03-19,106.63428571428572,4.432236528748214,0.0762736524683398
2017,LSTM (small),2017-03-26,136.82285714285717,4.41365806740778,0.1006325602270004
2017,LSTM (small),2017-04-02,110.33714285714288,4.617648803057062,0.1006325602270004
2017,LSTM (small),2017-04-09,90.86,4.51998695880474,0.1057825901934487
2017,LSTM (small),2017-04-16,154.83714285714285,4.862391084147883,0.1057825901934487
2017,LSTM (small),2017-04-23,133.07,4.756651210777906,0.1543246814639469
2017,LSTM (small),2017-04-30,96.78857142857144,4.928946019443163,0.1543246814639469
2017,LSTM (small),2017-05-07,167.48285714285717,4.547707748862978,0.1543246814639469
2017,LSTM (small),2017-05-14,142.7271428571429,4.631800423979984,0.1543246814639469
2017,LSTM (small),2017-05-21,144.9042857142857,4.451718208379167,0.1543246814639469
2017,LSTM (small),2017-05-28,94.82285714285716,4.2694840239110174,0.1543246814639469
2017,LSTM (small),2017-06-04,90.08142857142856,4.714177110501385,0.1543246814639469
2017,LSTM (small),2017-06-11,58.47714285714285,4.326030931638623,0.1543246814639469
2017,LSTM (small),2017-06-18,58.12714285714286,4.421368486937331,0.1543246814639469
2017,LSTM (small),2017-06-25,57.142857142857146,4.572155499391063,0.1543246814639469
2017,LSTM (small),2017-07-02,32.95,4.327601821084915,0.1543246814639469
2017,LSTM (small),2017-07-09,58.0,4.309373286845305,0.1543246814639469
2017,LSTM (small),2017-07-16,31.555714285714288,4.035210289885953,0.1543246814639469
2017,LSTM (small),2017-07-23,31.482857142857146,4.078887879488759,0.1543246814639469
2017,LSTM (small),2017-07-30,21.16,3.742100586198949,0.1543246814639469
2017,LSTM (small),2017-08-06,35.28142857142857,3.648332962026181,0.1543246814639469
2017,LSTM (small),2017-08-13,37.60285714285715,3.900494332361943,0.1543246814639469
2017,LSTM (small),2017-08-20,33.62428571428571,3.934500442462419,0.1543246814639469
2017,LSTM (small),2017-08-27,43.39857142857142,3.866433373726213,0.1543246814639469
2017,LSTM (small),2017-09-03,26.428571428571427,3.924841849854481,0.1543246814639469
2017,LSTM (small),2017-09-10,47.17714285714286,4.127024006866291,0.1543246814639469
2017,LSTM (small),2017-09-17,59.26285714285715,4.3292103776830695,0.1543246814639469
2017,LSTM (small),2017-09-24,44.027142857142856,4.578211354669044,0.1543246814639469
2017,LSTM (small),2017-10-01,72.08571428571429,4.419535635008054,0.1543246814639469
2017,LSTM (small),2017-10-08,76.91285714285713,4.638269446861531,0.1543246814639469
2017,LSTM (small),2017-10-15,122.44714285714284,5.306436970878472,0.1543246814639469
2017,LSTM (small),2017-10-22,198.3271428571429,5.377754218247121,0.1543246814639469
2017,LSTM (small),2017-10-29,183.8942857142857,5.546425868780941,0.1543246814639469
2017,LSTM (small),2017-11-05,187.99571428571429,5.552625461513433,0.1543246814639469
2017,LSTM (small),2017-11-12,438.44714285714286,5.374363901067023,0.1543246814639469
2017,LSTM (small),2017-11-19,202.21142857142857,5.010219498654109,0.1543246814639469
2017,LSTM (small),2017-11-26,185.72,4.6858131872367,0.1543246814639469
2017,LSTM (small),2017-12-03,205.89714285714285,4.603536005175243,0.1543246814639469
2017,LSTM (small),2017-12-10,173.3457142857143,4.802075425252763,0.1543246814639469
2017,LSTM (small),2017-12-17,130.51142857142858,5.028618431232692,0.1543246814639469
2017,LSTM (small),2017-12-24,191.21714285714285,4.96004102174914,0.1543246814639469
2017,Fourier+ARMA const,2017-01-01,230.7142857142857,5.410418684356212,0.1997901727117915
2017,Fourier+ARMA const,2017-01-08,207.4528571428572,5.347254134525266,0.2090836985077223
2017,Fourier+ARMA const,2017-01-15,196.74571428571429,5.289436682507115,0.209946966587954
2017,Fourier+ARMA const,2017-01-22,238.02714285714288,5.228037116457888,0.2100289618414049
2017,Fourier+ARMA const,2017-01-29,159.2057142857143,5.160350904275068,0.2100367658454168
2017,Fourier+ARMA const,2017-02-05,177.6185714285714,5.085989260382345,0.2100375087452656
2017,Fourier+ARMA const,2017-02-12,133.16857142857145,5.005844338299314,0.2100375794666984
2017,Fourier+ARMA const,2017-02-19,139.42142857142858,4.921842659937736,0.21003758619914
2017,Fourier+ARMA const,2017-02-26,244.8114285714286,4.836824058001749,0.2100375868400458
2017,Fourier+ARMA const,2017-03-05,115.93714285714285,4.75434011085158,0.2100375869010579
2017,Fourier+ARMA const,2017-03-12,87.95,4.678325149804665,0.210037586906866
2017,Fourier+ARMA const,2017-03-19,106.63428571428572,4.612658272309776,0.210037586907419
2017,Fourier+ARMA const,2017-03-26,136.82285714285717,4.560667019729091,0.2100375869074716
2017,Fourier+ARMA const,2017-04-02,110.33714285714288,4.524639441213481,0.2100375869074766
2017,Fourier+ARMA const,2017-04-09,90.86,4.505415437652522,0.2100375869074771
2017,Fourier+ARMA const,2017-04-16,154.83714285714285,4.5021218275047765,0.2100375869074771
2017,Fourier+ARMA const,2017-04-23,133.07,4.512099762733742,0.2100375869074771
2017,Fourier+ARMA const,2017-04-30,96.78857142857144,4.531050030665001,0.2100375869074771
2017,Fourier+ARMA const,2017-05-07,167.48285714285717,4.553394348499743,0.2100375869074771
2017,Fourier+ARMA const,2017-05-14,142.7271428571429,4.572822511760472,0.2100375869074771
2017,Fourier+ARMA const,2017-05-21,144.9042857142857,4.582969870924358,0.2100375869074771
2017,Fourier+ARMA const,2017-05-28,94.82285714285716,4.578150444353652,0.2100375869074771
2017,Fourier+ARMA const,2017-06-04,90.08142857142856,4.554060644219734,0.2100375869074771
2017,Fourier+ARMA const,2017-06-11,58.47714285714285,4.508368616048543,0.2100375869074771
2017,Fourier+ARMA const,2017-06-18,58.12714285714286,4.441114792264724,0.2100375869074771
2017,Fourier+ARMA const,2017-06-25,57.142857142857146,4.35486931465018,0.2100375869074771
2017,Fourier+ARMA const,2017-07-02,32.95,4.2546191577921455,0.2100375869074771
2017,Fourier+ARMA const,2017-07-09,58.0,4.147388828213028,0.2100375869074771
2017,Fourier+ARMA const,2017-07-16,31.555714285714288,4.041629645643317,0.2100375869074771
2017,Fourier+ARMA const,2017-07-23,31.482857142857146,3.946440012394494,0.2100375869074771
2017,Fourier+ARMA const,2017-07-30,21.16,3.870699359248533,0.2100375869074771
2017,Fourier+ARMA const,2017-08-06,35.28142857142857,3.822209101616802,0.2100375869074771
2017,Fourier+ARMA const,2017-08-13,37.60285714285715,3.806933612034964,0.2100375869074771
2017,Fourier+ARMA const,2017-08-20,33.62428571428571,3.8284229327415344,0.2100375869074771
2017,Fourier+ARMA const,2017-08-27,43.39857142857142,3.8874780866845295,0.2100375869074771
2017,Fourier+ARMA const,2017-09-03,26.428571428571427,3.982091949235909,0.2100375869074771
2017,Fourier+ARMA const,2017-09-10,47.17714285714286,4.107667127989863,0.2100375869074771
2017,Fourier+ARMA const,2017-09-17,59.26285714285715,4.257481005877827,0.2100375869074771
2017,Fourier+ARMA const,2017-09-24,44.027142857142856,4.423340821889831,0.2100375869074771
2017,Fourier+ARMA const,2017-10-01,72.08571428571429,4.596351654573229,0.2100375869074771
2017,Fourier+ARMA const,2017-10-08,76.91285714285713,4.767709763067734,0.2100375869074771
2017,Fourier+ARMA const,2017-10-15,122.44714285714284,4.929434036201776,0.2100375869074771
2017,Fourier+ARMA const,2017-10-22,198.3271428571429,5.074959060807871,0.2100375869074771
2017,Fourier+ARMA const,2017-10-29,183.8942857142857,5.199532998651251,0.2100375869074771
2017,Fourier+ARMA const,2017-11-05,187.99571428571429,5.300389412833885,0.2100375869074771
2017,Fourier+ARMA const,2017-11-12,438.44714285714286,5.376691015113094,0.2100375869074771
2017,Fourier+ARMA const,2017-11-19,202.21142857142857,5.429271312083493,0.2100375869074771
2017,Fourier+ARMA const,2017-11-26,185.72,5.46022377537758,0.2100375869074771
2017,Fourier+ARMA const,2017-12-03,205.89714285714285,5.472404533424923,0.2100375869074771
2017,Fourier+ARMA const,2017-12-10,173.3457142857143,5.468921752577643,0.2100375869074771
2017,Fourier+ARMA const,2017-12-17,130.51142857142858,5.452682142603752,0.2100375869074771
2017,Fourier+ARMA const,2017-12-24,191.21714285714285,5.426052988656513,0.2100375869074771
2017,Fourier+ARMA linear,2017-01-01,230.7142857142857,5.455738148618351,0.1966814430996452
2017,Fourier+ARMA linear,2017-01-08,207.4528571428572,5.410533093331012,0.2065017418160112
2017,Fourier+ARMA linear,2017-01-15,196.74571428571429,5.361830104549332,0.2074806581365114
2017,Fourier+ARMA linear,2017-01-22,238.02714285714288,5.306142735055698,0.2075805926710268
2017,Fourier+ARMA linear,2017-01-29,159.2057142857143,5.242327832781278,0.2075908185507798
2017,Fourier+ARMA linear,2017-02-05,177.6185714285714,5.170464870148069,0.2075918651712566
2017,Fourier+ARMA linear,2017-02-12,133.16857142857145,5.091660515380642,0.2075919722956455
2017,Fourier+ARMA linear,2017-02-19,139.42142857142858,5.008043091411698,0.207591983260139
2017,Fourier+ARMA linear,2017-02-26,244.8114285714286,4.922694846744667,0.2075919843823871
2017,Fourier+ARMA linear,2017-03-05,115.93714285714285,4.839442755223846,0.2075919844972525
2017,Fourier+ARMA linear,2017-03-12,87.95,4.7625022256588165,0.2075919845090093
2017,Fourier+ARMA linear,2017-03-19,106.63428571428572,4.696007723284075,0.2075919845102127
2017,Fourier+ARMA linear,2017-03-26,136.82285714285717,4.643488460991718,0.2075919845103359
2017,Fourier+ARMA linear,2017-04-02,110.33714285714288,4.60736029628165,0.2075919845103485
2017,Fourier+ARMA linear,2017-04-09,90.86,4.58850729731866,0.2075919845103498
2017,Fourier+ARMA linear,2017-04-16,154.83714285714285,4.586018373799698,0.2075919845103499
2017,Fourier+ARMA linear,2017-04-23,133.07,4.597127002257658,0.2075919845103499
2017,Fourier+ARMA linear,2017-04-30,96.78857142857144,4.617377581242314,0.2075919845103499
2017,Fourier+ARMA linear,2017-05-07,167.48285714285717,4.641013417942537,0.2075919845103499
2017,Fourier+ARMA linear,2017-05-14,142.7271428571429,4.661552424955928,0.2075919845103499
2017,Fourier+ARMA linear,2017-05-21,144.9042857142857,4.672491050031644,0.2075919845103499
2017,Fourier+ARMA linear,2017-05-28,94.82285714285716,4.668058151702666,0.2075919845103499
2017,Fourier+ARMA linear,2017-06-04,90.08142857142856,4.643931032227195,0.2075919845103499
2017,Fourier+ARMA linear,2017-06-11,58.47714285714285,4.597827053881927,0.2075919845103499
2017,Fourier+ARMA linear,2017-06-18,58.12714285714286,4.529896256246045,0.2075919845103499
2017,Fourier+ARMA linear,2017-06-25,57.142857142857146,4.442861854224748,0.2075919845103499
2017,Fourier+ARMA linear,2017-07-02,32.95,4.34188391003769,0.2075919845103499
2017,Fourier+ARMA linear,2017-07-09,58.0,4.234153415988206,0.2075919845103499
2017,Fourier+ARMA linear,2017-07-16,31.555714285714288,4.128255602470349,0.2075919845103499
2017,Fourier+ARMA linear,2017-07-23,31.482857142857146,4.033368616171427,0.2075919845103499
2017,Fourier+ARMA linear,2017-07-30,21.16,3.958383420094157,0.2075919845103499
2017,Fourier+ARMA linear,2017-08-06,35.28142857142857,3.911040404678253,0.2075919845103499
2017,Fourier+ARMA linear,2017-08-13,37.60285714285715,3.8971765640960174,0.2075919845103499
2017,Fourier+ARMA linear,2017-08-20,33.62428571428571,3.92016437414724,0.2075919845103499
2017,Fourier+ARMA linear,2017-08-27,43.39857142857142,3.9806012692443336,0.2075919845103499
2017,Fourier+ARMA linear,2017-09-03,26.428571428571427,4.076279590648464,0.2075919845103499
2017,Fourier+ARMA linear,2017-09-10,47.17714285714286,4.20243462968297,0.2075919845103499
2017,Fourier+ARMA linear,2017-09-17,59.26285714285715,4.352236860298919,0.2075919845103499
2017,Fourier+ARMA linear,2017-09-24,44.027142857142856,4.517467469918131,0.2075919845103499
2017,Fourier+ARMA linear,2017-10-01,72.08571428571429,4.689297083696363,0.2075919845103499
2017,Fourier+ARMA linear,2017-10-08,76.91285714285713,4.859078363950366,0.2075919845103499
2017,Fourier+ARMA linear,2017-10-15,122.44714285714284,5.0190649098879945,0.2075919845103499
2017,Fourier+ARMA linear,2017-10-22,198.3271428571429,5.162981156999438,0.2075919845103499
2017,Fourier+ARMA linear,2017-10-29,183.8942857142857,5.286389038696045,0.2075919845103499
2017,Fourier+ARMA linear,2017-11-05,187.99571428571429,5.386824201268776,0.2075919845103499
2017,Fourier+ARMA linear,2017-11-12,438.44714285714286,5.463704021836899,0.2075919845103499
2017,Fourier+ARMA linear,2017-11-19,202.21142857142857,5.518037780145052,0.2075919845103499
2017,Fourier+ARMA linear,2017-11-26,185.72,5.551992527008757,0.2075919845103499
2017,Fourier+ARMA linear,2017-12-03,205.89714285714285,5.5683836129279625,0.2075919845103499
2017,Fourier+ARMA linear,2017-12-10,173.3457142857143,5.570164679660362,0.2075919845103499
2017,Fourier+ARMA linear,2017-12-17,130.51142857142858,5.559987640230891,0.2075919845103499
2017,Fourier+ARMA linear,2017-12-24,191.21714285714285,5.539889575439574,0.2075919845103499
2017,Fourier+ARMA (selected),2017-01-01,230.7142857142857,5.334497996885141,0.1859389016893502
2017,Fourier+ARMA (selected),2017-01-08,207.4528571428572,5.36275874489405,0.1889951271077913
2017,Fourier+ARMA (selected),2017-01-15,196.74571428571429,5.415112431043251,0.1893705655600837
2017,Fourier+ARMA (selected),2017-01-22,238.02714285714288,5.439093298959808,0.1895728433130498
2017,Fourier+ARMA (selected),2017-01-29,159.2057142857143,5.408197297067528,0.189754404545396
2017,Fourier+ARMA (selected),2017-02-05,177.6185714285714,5.313595877587754,0.1899329290734678
2017,Fourier+ARMA (selected),2017-02-12,133.16857142857145,5.164520158599101,0.1901108753719344
2017,Fourier+ARMA (selected),2017-02-19,139.42142857142858,4.985126170965863,0.1902885961567302
2017,Fourier+ARMA (selected),2017-02-26,244.8114285714286,4.807216938897796,0.1904661425989316
2017,Fourier+ARMA (selected),2017-03-05,115.93714285714285,4.660988185083443,0.1906435224655326
2017,Fourier+ARMA (selected),2017-03-12,87.95,4.5667248291614095,0.1908207372697772
2017,Fourier+ARMA (selected),2017-03-19,106.63428571428572,4.529978479785905,0.1909977876221951
2017,Fourier+ARMA (selected),2017-03-26,136.82285714285717,4.5415207389666845,0.1911746740014557
2017,Fourier+ARMA (selected),2017-04-02,110.33714285714288,4.581753484068586,0.1913513968654277
2017,Fourier+ARMA (selected),2017-04-09,90.86,4.627821673923303,0.1915279566671895
2017,Fourier+ARMA (selected),2017-04-16,154.83714285714285,4.660893810929415,0.1917043538573473
2017,Fourier+ARMA (selected),2017-04-23,133.07,4.671189012215926,0.1918805888843805
2017,Fourier+ARMA (selected),2017-04-30,96.78857142857144,4.65926271107734,0.1920566621947028
2017,Fourier+ARMA (selected),2017-05-07,167.48285714285717,4.633460263897109,0.1922325742326822
2017,Fourier+ARMA (selected),2017-05-14,142.7271428571429,4.604804476065865,0.1924083254406554
2017,Fourier+ARMA (selected),2017-05-21,144.9042857142857,4.581424826957599,0.1925839162589407
2017,Fourier+ARMA (selected),2017-05-28,94.82285714285716,4.564684377859663,0.1927593471258506
2017,Fourier+ARMA (selected),2017-06-04,90.08142857142856,4.548425733670163,0.1929346184777052
2017,Fourier+ARMA (selected),2017-06-11,58.47714285714285,4.52152963137033,0.1931097307488444
2017,Fourier+ARMA (selected),2017-06-18,58.12714285714286,4.4727181393196815,0.1932846843716404
2017,Fourier+ARMA (selected),2017-06-25,57.142857142857146,4.395700485821479,0.1934594797765108
2017,Fourier+ARMA (selected),2017-07-02,32.95,4.292650668426175,0.1936341173919299
2017,Fourier+ARMA (selected),2017-07-09,58.0,4.174650755241744,0.1938085976444419
2017,Fourier+ARMA (selected),2017-07-16,31.555714285714288,4.058884660254581,0.1939829209586727
2017,Fourier+ARMA (selected),2017-07-23,31.482857142857146,3.9635931582214408,0.1941570877573419
2017,Fourier+ARMA (selected),2017-07-30,21.16,3.902645843140085,0.1943310984612748
2017,Fourier+ARMA (selected),2017-08-06,35.28142857142857,3.8817350880123302,0.1945049534894142
2017,Fourier+ARMA (selected),2017-08-13,37.60285714285715,3.897592967228144,0.1946786532588323
2017,Fourier+ARMA (selected),2017-08-20,33.62428571428571,3.9404951688209033,0.1948521981847425
2017,Fourier+ARMA (selected),2017-08-27,43.39857142857142,3.9990657657580178,0.1950255886805105
2017,Fourier+ARMA (selected),2017-09-03,26.428571428571427,4.0654995759775865,0.1951988251576663
2017,Fourier+ARMA (selected),2017-09-10,47.17714285714286,4.139117037741782,0.1953719080259152
2017,Fourier+ARMA (selected),2017-09-17,59.26285714285715,4.22675125882283,0.1955448376931495
2017,Fourier+ARMA (selected),2017-09-24,44.027142857142856,4.339640773769545,0.1957176145654593
2017,Fourier+ARMA (selected),2017-10-01,72.08571428571429,4.487845331173993,0.1958902390471439
2017,Fourier+ARMA (selected),2017-10-08,76.91285714285713,4.674222853011635,0.1960627115407228
2017,Fourier+ARMA (selected),2017-10-15,122.44714285714284,4.890314458425232,0.1962350324469466
2017,Fourier+ARMA (selected),2017-10-22,198.3271428571429,5.115939184359382,0.1964072021648078
2017,Fourier+ARMA (selected),2017-10-29,183.8942857142857,5.323063444021786,0.1965792210915518
2017,Fourier+ARMA (selected),2017-11-05,187.99571428571429,5.48299924316334,0.1967510896226872
2017,Fourier+ARMA (selected),2017-11-12,438.44714285714286,5.574728738435755,0.1969228081519969
2017,Fourier+ARMA (selected),2017-11-19,202.21142857142857,5.591607068477838,0.1970943770715484
2017,Fourier+ARMA (selected),2017-11-26,185.72,5.544080851865737,0.1972657967717039
2017,Fourier+ARMA (selected),2017-12-03,205.89714285714285,5.4572774922219525,0.1974370676411314
2017,Fourier+ARMA (selected),2017-12-10,173.3457142857143,5.363979426686674,0.1976081900668143
2017,Fourier+ARMA (selected),2017-12-17,130.51142857142858,5.295043937354143,0.1977791644340619
2017,Fourier+ARMA (selected),2017-12-24,191.21714285714285,5.270234846529169,0.1979499911265196
2017,SARIMA D=1,2017-01-01,230.7142857142857,5.623921882310018,0.239915487864264
2017,SARIMA D=1,2017-01-08,207.4528571428572,5.948605453398255,0.2449863729519903
2017,SARIMA D=1,2017-01-15,196.74571428571429,5.355710099590571,0.2482791111208592
2017,SARIMA D=1,2017-01-22,238.02714285714288,5.934580122116114,0.2504303596898547
2017,SARIMA D=1,2017-01-29,159.2057142857143,5.9040612272009945,0.2518412715119654
2017,SARIMA D=1,2017-02-05,177.6185714285714,5.151083400529475,0.2527689187185479
2017,SARIMA D=1,2017-02-12,133.16857142857145,4.971513122706882,0.2533798057827916
2017,SARIMA D=1,2017-02-19,139.42142857142858,4.877670159946065,0.2537825158374027
2017,SARIMA D=1,2017-02-26,244.8114285714286,4.907537683993182,0.2540481725562835
2017,SARIMA D=1,2017-03-05,115.93714285714285,5.159236484973674,0.254223497667472
2017,SARIMA D=1,2017-03-12,87.95,4.529861215511487,0.2543392409364327
2017,SARIMA D=1,2017-03-19,106.63428571428572,4.417255811290545,0.2544156653059642
2017,SARIMA D=1,2017-03-26,136.82285714285717,4.448913673476607,0.2544661341796188
2017,SARIMA D=1,2017-04-02,110.33714285714288,4.952910884925899,0.2544994654479197
2017,SARIMA D=1,2017-04-09,90.86,4.879800998599334,0.2545214796844537
2017,SARIMA D=1,2017-04-16,154.83714285714285,4.619385300217649,0.2545360198646395
2017,SARIMA D=1,2017-04-23,133.07,4.715149202065666,0.2545456236561022
2017,SARIMA D=1,2017-04-30,96.78857142857144,5.293065312965967,0.2545519669363574
2017,SARIMA D=1,2017-05-07,167.48285714285717,4.369658247548616,0.2545561565082368
2017,SARIMA D=1,2017-05-14,142.7271428571429,4.554085865576235,0.2545589233382545
2017,SARIMA D=1,2017-05-21,144.9042857142857,4.564888888690248,0.2545607501421671
2017,SARIMA D=1,2017-05-28,94.82285714285716,4.556703409872442,0.2545619556246897
2017,SARIMA D=1,2017-06-04,90.08142857142856,4.746447125724847,0.254562750090658
2017,SARIMA D=1,2017-06-11,58.47714285714285,4.100582256315934,0.2545632721384729
2017,SARIMA D=1,2017-06-18,58.12714285714286,4.26342799740093,0.2545636128411321
2017,SARIMA D=1,2017-06-25,57.142857142857146,4.306115062057368,0.2545638316350395
2017,SARIMA D=1,2017-07-02,32.95,4.1624243703292505,0.2545639666891873
2017,SARIMA D=1,2017-07-09,58.0,4.195908798003119,0.2545640415639615
2017,SARIMA D=1,2017-07-16,31.555714285714288,4.090722402521637,0.2545640693213525
2017,SARIMA D=1,2017-07-23,31.482857142857146,3.963943559329948,0.2545640548036623
2017,SARIMA D=1,2017-07-30,21.16,4.184710118431672,0.254563995478258
2017,SARIMA D=1,2017-08-06,35.28142857142857,3.646531578050901,0.2545638809957464
2017,SARIMA D=1,2017-08-13,37.60285714285715,3.532275090382183,0.2545636913844892
2017,SARIMA D=1,2017-08-20,33.62428571428571,3.890623239691665,0.2545633935664713
2017,SARIMA D=1,2017-08-27,43.39857142857142,3.716093068853021,0.2545629355866639
2017,SARIMA D=1,2017-09-03,26.428571428571427,3.5320570397962507,0.2545622375490763
2017,SARIMA D=1,2017-09-10,47.17714285714286,3.9479364192657167,0.2545611776780221
2017,SARIMA D=1,2017-09-17,59.26285714285715,4.077243149373704,0.2545595710723717
2017,SARIMA D=1,2017-09-24,44.027142857142856,4.207196313888347,0.2545571374450697
2017,SARIMA D=1,2017-10-01,72.08571428571429,4.501490469394099,0.2545534522168733
2017,SARIMA D=1,2017-10-08,76.91285714285713,4.713835958044302,0.254547872425283
2017,SARIMA D=1,2017-10-15,122.44714285714284,4.819224765987067,0.2545394245067023
2017,SARIMA D=1,2017-10-22,198.3271428571429,5.011472487191168,0.2545266343369893
2017,SARIMA D=1,2017-10-29,183.8942857142857,5.819621812919762,0.2545072697928994
2017,SARIMA D=1,2017-11-05,187.99571428571429,6.566718181464926,0.2544779507223341
2017,SARIMA D=1,2017-11-12,438.44714285714286,5.902105539731084,0.2544335577052704
2017,SARIMA D=1,2017-11-19,202.21142857142857,5.708106816135856,0.2543663361060395
2017,SARIMA D=1,2017-11-26,185.72,5.277268093022246,0.2542645348835032
2017,SARIMA D=1,2017-12-03,205.89714285714285,5.403171661742131,0.2541103394862845
2017,SARIMA D=1,2017-12-10,173.3457142857143,5.534869790277861,0.2538767234880161
2017,SARIMA D=1,2017-12-17,130.51142857142858,5.498770851551472,0.2535226404566488
2017,SARIMA D=1,2017-12-24,191.21714285714285,5.631941010371769,0.2529856479520987
2017,SARIMA D=0,2017-01-01,230.7142857142857,5.487128835696124,0.2409255014515284
2017,SARIMA D=0,2017-01-08,207.4528571428572,5.515634844098736,0.2933672024848072
2017,SARIMA D=0,2017-01-15,196.74571428571429,5.358407118237343,0.3309874680329981
2017,SARIMA D=0,2017-01-22,238.02714285714288,5.418775558252828,0.3595037102383793
2017,SARIMA D=0,2017-01-29,159.2057142857143,5.3848044006353,0.3817710543790053
2017,SARIMA D=0,2017-02-05,177.6185714285714,5.200556363271142,0.3994824532656348
2017,SARIMA D=0,2017-02-12,133.16857142857145,5.145587275396121,0.4137460631717585
2017,SARIMA D=0,2017-02-19,139.42142857142858,5.098660218452015,0.4253347827011896
2017,SARIMA D=0,2017-02-26,244.8114285714286,5.064204040460416,0.4348116343561397
2017,SARIMA D=0,2017-03-05,115.93714285714285,5.048010562780667,0.4425997147703713
2017,SARIMA D=0,2017-03-12,87.95,4.909612338537649,0.4490243591936215
2017,SARIMA D=0,2017-03-19,106.63428571428572,4.849553265656254,0.4543401157323991
2017,SARIMA D=0,2017-03-26,136.82285714285717,4.868565474695683,0.4587488326232745
2017,SARIMA D=0,2017-04-02,110.33714285714288,4.925058197223263,0.4624122543895368
2017,SARIMA D=0,2017-04-09,90.86,4.922492474516402,0.4654610690478392
2017,SARIMA D=0,2017-04-16,154.83714285714285,4.860226914978601,0.4680015736041582
2017,SARIMA D=0,2017-04-23,133.07,4.883214276660015,0.470120689383328
2017,SARIMA D=0,2017-04-30,96.78857142857144,4.951034379206158,0.4718898024716809
2017,SARIMA D=0,2017-05-07,167.48285714285717,4.804075388494415,0.4733677478643229
2017,SARIMA D=0,2017-05-14,142.7271428571429,4.80248979120132,0.4746031568120705
2017,SARIMA D=0,2017-05-21,144.9042857142857,4.777247312698443,0.4756363222948147
2017,SARIMA D=0,2017-05-28,94.82285714285716,4.805090983100177,0.4765006943463217
2017,SARIMA D=0,2017-06-04,90.08142857142856,4.7882313836195705,0.4772240873527518
2017,SARIMA D=0,2017-06-11,58.47714285714285,4.693728853503774,0.4778296607210232
2017,SARIMA D=0,2017-06-18,58.12714285714286,4.727876571286726,0.4783367195149818
2017,SARIMA D=0,2017-06-25,57.142857142857146,4.705963944031633,0.4787613709014477
2017,SARIMA D=0,2017-07-02,32.95,4.662626198831615,0.4791170643021364
2017,SARIMA D=0,2017-07-09,58.0,4.628186969528815,0.4794150371894263
2017,SARIMA D=0,2017-07-16,31.555714285714288,4.624126078371066,0.4796646839359412
2017,SARIMA D=0,2017-07-23,31.482857142857146,4.553931392672518,0.4798738616444099
2017,SARIMA D=0,2017-07-30,21.16,4.572206806480962,0.480049144174682
2017,SARIMA D=0,2017-08-06,35.28142857142857,4.524376441111374,0.4801960334562893
2017,SARIMA D=0,2017-08-13,37.60285714285715,4.503970839471218,0.4803191354881879
2017,SARIMA D=0,2017-08-20,33.62428571428571,4.5447619469993965,0.4804223070801756
2017,SARIMA D=0,2017-08-27,43.39857142857142,4.527194908661719,0.4805087783072094
2017,SARIMA D=0,2017-09-03,26.428571428571427,4.518574142357431,0.4805812547715128
2017,SARIMA D=0,2017-09-10,47.17714285714286,4.582397735449794,0.4806420030547404
2017,SARIMA D=0,2017-09-17,59.26285714285715,4.628821037213854,0.4806929221603483
2017,SARIMA D=0,2017-09-24,44.027142857142856,4.621503615813789,0.480735603268953
2017,SARIMA D=0,2017-10-01,72.08571428571429,4.712681917135403,0.480771379736677
2017,SARIMA D=0,2017-10-08,76.91285714285713,4.798748886394287,0.4808013689423808
2017,SARIMA D=0,2017-10-15,122.44714285714284,4.79072142295751,0.4808265073215815
2017,SARIMA D=0,2017-10-22,198.3271428571429,4.862831418845799,0.4808475797026446
2017,SARIMA D=0,2017-10-29,183.8942857142857,5.014971776728023,0.4808652438763035
2017,SARIMA D=0,2017-11-05,187.99571428571429,5.203660054727734,0.4808800511761161
2017,SARIMA D=0,2017-11-12,438.44714285714286,5.07359864492095,0.4808924637196882
2017,SARIMA D=0,2017-11-19,202.21142857142857,5.029441704318933,0.4809028688539932
2017,SARIMA D=0,2017-11-26,185.72,4.934527337467627,0.4809115912592533
2017,SARIMA D=0,2017-12-03,205.89714285714285,4.966725109853984,0.4809189030916624
2017,SARIMA D=0,2017-12-10,173.3457142857143,4.992447890844099,0.4809250324832382
2017,SARIMA D=0,2017-12-17,130.51142857142858,4.9354456639730415,0.4809301706652829
2017,SARIMA D=0,2017-12-24,191.21714285714285,4.99500711933759,0.4809344779385929
2018,Seasonal naive,2018-01-07,247.29857142857145,5.33490411936592,0.3345822524103585
2018,Seasonal naive,2018-01-14,188.26,5.281912104522604,0.3345822524103585
2018,Seasonal naive,2018-01-21,197.46,5.472384712787015,0.3345822524103585
2018,Seasonal naive,2018-01-28,148.48857142857145,5.070197166520604,0.3345822524103585
2018,Seasonal naive,2018-02-04,137.04714285714286,5.179638393945697,0.3345822524103585
2018,Seasonal naive,2018-02-11,169.39,4.891615780029702,0.3345822524103585
2018,Seasonal naive,2018-02-18,103.70857142857145,4.9375012065373065,0.3345822524103585
2018,Seasonal naive,2018-02-25,158.08285714285714,5.500488234889247,0.3345822524103585
2018,Seasonal naive,2018-03-04,104.86,4.753048172319535,0.3345822524103585
2018,Seasonal naive,2018-03-11,96.94857142857144,4.476768471183568,0.3345822524103585
2018,Seasonal naive,2018-03-18,102.21428571428572,4.669405089609958,0.3345822524103585
2018,Seasonal naive,2018-03-25,90.97,4.918687075609021,0.3345822524103585
2018,Seasonal naive,2018-04-01,97.72857142857144,4.703540613519024,0.3345822524103585
2018,Seasonal naive,2018-04-08,94.45285714285714,4.509319860331257,0.3345822524103585
2018,Seasonal naive,2018-04-15,75.25,5.042373873312019,0.3345822524103585
2018,Seasonal naive,2018-04-22,92.28,4.890875305555651,0.3345822524103585
2018,Seasonal naive,2018-04-29,103.68999999999998,4.57252892355803,0.3345822524103585
2018,Seasonal naive,2018-05-06,68.93714285714286,5.120881000611694,0.3345822524103585
2018,Seasonal naive,2018-05-13,99.39285714285714,4.960934715625462,0.3345822524103585
2018,Seasonal naive,2018-05-20,83.68285714285715,4.976073425937455,0.3345822524103585
2018,Seasonal naive,2018-05-27,98.57714285714285,4.5520104893007165,0.3345822524103585
2018,Seasonal naive,2018-06-03,80.00142857142858,4.500714023184685,0.3345822524103585
2018,Seasonal naive,2018-06-10,64.88285714285715,4.06863595749599,0.3345822524103585
2018,Seasonal naive,2018-06-17,152.4042857142857,4.06263272958742,0.3345822524103585
2018,Seasonal naive,2018-06-24,68.25857142857143,4.045554398052669,0.3345822524103585
2018,Seasonal naive,2018-07-01,38.87571428571429,3.4949912609485163,0.3345822524103585
2018,Seasonal naive,2018-07-08,51.74428571428571,4.060443010546419,0.3345822524103585
2018,Seasonal naive,2018-07-15,43.470000000000006,3.451754690993422,0.3345822524103585
2018,Seasonal naive,2018-07-22,36.80857142857143,3.4494431800043177,0.3345822524103585
2018,Seasonal naive,2018-07-29,34.582857142857144,3.052112606990099,0.3345822524103585
2018,Seasonal naive,2018-08-05,59.50428571428571,3.563356722706227,0.3345822524103585
2018,Seasonal naive,2018-08-12,39.05428571428571,3.627080035350864,0.3345822524103585
2018,Seasonal naive,2018-08-19,38.74142857142857,3.515248594998551,0.3345822524103585
2018,Seasonal naive,2018-08-26,31.807142857142857,3.77042652417224,0.3345822524103585
2018,Seasonal naive,2018-09-02,37.85428571428572,3.2744456760230114,0.3345822524103585
2018,Seasonal naive,2018-09-09,41.95,3.85390951379783,0.3345822524103585
2018,Seasonal naive,2018-09-16,33.33,4.08198275466622,0.3345822524103585
2018,Seasonal naive,2018-09-23,49.20857142857143,3.7848063268409686,0.3345822524103585
2018,Seasonal naive,2018-09-30,57.55857142857143,4.277855887151644,0.3345822524103585
2018,Seasonal naive,2018-10-07,83.38714285714286,4.342673055551451,0.3345822524103585
2018,Seasonal naive,2018-10-14,96.91142857142856,4.807679449987064,0.3345822524103585
2018,Seasonal naive,2018-10-21,140.48285714285714,5.289917903905407,0.3345822524103585
2018,Seasonal naive,2018-10-28,171.1542857142857,5.214361058339501,0.3345822524103585
2018,Seasonal naive,2018-11-04,202.76142857142847,5.236419166217525,0.3345822524103585
2018,Seasonal naive,2018-11-11,283.1485714285714,6.08323926374192,0.3345822524103585
2018,Seasonal naive,2018-11-18,173.0885714285714,5.309313826113883,0.3345822524103585
2018,Seasonal naive,2018-11-25,168.86714285714285,5.224240163151721,0.3345822524103585
2018,Seasonal naive,2018-12-02,186.70857142857145,5.3273767375758485,0.3345822524103585
2018,Seasonal naive,2018-12-09,201.8728571428572,5.155287948927893,0.3345822524103585
2018,Seasonal naive,2018-12-16,175.70142857142858,4.871460798188248,0.3345822524103585
2018,Seasonal naive,2018-12-23,261.5357142857143,5.253409655892827,0.3345822524103585
2018,Seasonal naive,2018-12-30,287.3928571428572,5.529355388650604,0.3345822524103585
2018,Climatology,2018-01-07,247.29857142857145,5.408731798097988,0.2100320523345356
2018,Climatology,2018-01-14,188.26,5.277670506466927,0.2100320523345356
2018,Climatology,2018-01-21,197.46,5.437700460879099,0.2100320523345356
2018,Climatology,2018-01-28,148.48857142857145,5.242666727981997,0.2100320523345356
2018,Climatology,2018-02-04,137.04714285714286,5.117660180775535,0.2100320523345356
2018,Climatology,2018-02-11,169.39,4.963407300169094,0.2100320523345356
2018,Climatology,2018-02-18,103.70857142857145,4.979183814406805,0.2100320523345356
2018,Climatology,2018-02-25,158.08285714285714,5.142004334134754,0.2100320523345356
2018,Climatology,2018-03-04,104.86,4.839883973095223,0.2100320523345356
2018,Climatology,2018-03-11,96.94857142857144,4.461460710966682,0.2100320523345356
2018,Climatology,2018-03-18,102.21428571428572,4.490216717113987,0.2100320523345356
2018,Climatology,2018-03-25,90.97,4.544469070882633,0.2100320523345356
2018,Climatology,2018-04-01,97.72857142857144,4.654685162671122,0.2100320523345356
2018,Climatology,2018-04-08,94.45285714285714,4.511638483508993,0.2100320523345356
2018,Climatology,2018-04-15,75.25,4.720054794304081,0.2100320523345356
2018,Climatology,2018-04-22,92.28,4.712916407773464,0.2100320523345356
2018,Climatology,2018-04-29,103.68999999999998,4.750992743911659,0.2100320523345356
2018,Climatology,2018-05-06,68.93714285714286,4.660403745965778,0.2100320523345356
2018,Climatology,2018-05-13,99.39285714285714,4.761628652223261,0.2100320523345356
2018,Climatology,2018-05-20,83.68285714285715,4.649374958381972,0.2100320523345356
2018,Climatology,2018-05-27,98.57714285714285,4.482764217200919,0.2100320523345356
2018,Climatology,2018-06-03,80.00142857142858,4.580838861181697,0.2100320523345356
2018,Climatology,2018-06-10,64.88285714285715,4.175369200235714,0.2100320523345356
2018,Climatology,2018-06-17,152.4042857142857,4.347727239542452,0.2100320523345356
2018,Climatology,2018-06-24,68.25857142857143,4.351151337989115,0.2100320523345356
2018,Climatology,2018-07-01,38.87571428571429,4.038262211281606,0.2100320523345356
2018,Climatology,2018-07-08,51.74428571428571,4.156504895471128,0.2100320523345356
2018,Climatology,2018-07-15,43.470000000000006,3.8284758524673017,0.2100320523345356
2018,Climatology,2018-07-22,36.80857142857143,3.822010926215055,0.2100320523345356
2018,Climatology,2018-07-29,34.582857142857144,3.5711640487107554,0.2100320523345356
2018,Climatology,2018-08-05,59.50428571428571,3.617490523111794,0.2100320523345356
2018,Climatology,2018-08-12,39.05428571428571,3.824585480368356,0.2100320523345356
2018,Climatology,2018-08-19,38.74142857142857,3.852904625177204,0.2100320523345356
2018,Climatology,2018-08-26,31.807142857142857,3.830166125886565,0.2100320523345356
2018,Climatology,2018-09-02,37.85428571428572,3.7218864329755377,0.2100320523345356
2018,Climatology,2018-09-09,41.95,4.090821913577266,0.2100320523345356
2018,Climatology,2018-09-16,33.33,4.169794093283282,0.2100320523345356
2018,Climatology,2018-09-23,49.20857142857143,4.143161792567324,0.2100320523345356
2018,Climatology,2018-09-30,57.55857142857143,4.307081325051812,0.2100320523345356
2018,Climatology,2018-10-07,83.38714285714286,4.549477515741132,0.2100320523345356
2018,Climatology,2018-10-14,96.91142857142856,4.854407054424185,0.2100320523345356
2018,Climatology,2018-10-21,140.48285714285714,5.00495805287808,0.2100320523345356
2018,Climatology,2018-10-28,171.1542857142857,5.276872136457311,0.2100320523345356
2018,Climatology,2018-11-04,202.76142857142847,5.4856582839414445,0.2100320523345356
2018,Climatology,2018-11-11,283.1485714285714,5.770970117981858,0.2100320523345356
2018,Climatology,2018-11-18,173.0885714285714,5.463541591349466,0.2100320523345356
2018,Climatology,2018-11-25,168.86714285714285,5.307484213754044,0.2100320523345356
2018,Climatology,2018-12-02,186.70857142857145,5.342768608191364,0.2100320523345356
2018,Climatology,2018-12-09,201.8728571428572,5.342222323157638,0.2100320523345356
2018,Climatology,2018-12-16,175.70142857142858,5.183265534903394,0.2100320523345356
2018,Climatology,2018-12-23,261.5357142857143,5.207046369842629,0.2100320523345356
2018,Climatology,2018-12-30,287.3928571428572,5.398866447956088,0.2100320523345356
2018,Climatology + AR(1),2018-01-07,247.29857142857145,5.456173863370797,0.1957222411608262
2018,Climatology + AR(1),2018-01-14,188.26,5.294919091254036,0.2082565826369702
2018,Climatology + AR(1),2018-01-21,197.46,5.443971555433,0.2098574125107656
2018,Climatology + AR(1),2018-01-28,148.48857142857145,5.244946719493727,0.2100681041886963
2018,Climatology + AR(1),2018-02-04,137.04714285714286,5.118489120803289,0.2100959385029589
2018,Climatology + AR(1),2018-02-11,169.39,4.963708679172515,0.2100996174854142
2018,Climatology + AR(1),2018-02-18,103.70857142857145,4.979293387235552,0.2101001037841874
2018,Climatology + AR(1),2018-02-25,158.08285714285714,5.142044171696971,0.2101001680651494
2018,Climatology + AR(1),2018-03-04,104.86,4.839898456899114,0.2101001765620796
2018,Climatology + AR(1),2018-03-11,96.94857142857144,4.461465976865584,0.2101001776852401
2018,Climatology + AR(1),2018-03-18,102.21428571428572,4.490218631644967,0.2101001778337042
2018,Climatology + AR(1),2018-03-25,90.97,4.544469766951612,0.2101001778533288
2018,Climatology + AR(1),2018-04-01,97.72857142857144,4.6546854157419935,0.2101001778559229
2018,Climatology + AR(1),2018-04-08,94.45285714285714,4.51163857551836,0.2101001778562658
2018,Climatology + AR(1),2018-04-15,75.25,4.720054827756068,0.2101001778563111
2018,Climatology + AR(1),2018-04-22,92.28,4.712916419935654,0.2101001778563171
2018,Climatology + AR(1),2018-04-29,103.68999999999998,4.750992748333485,0.2101001778563179
2018,Climatology + AR(1),2018-05-06,68.93714285714286,4.660403747573428,0.210100177856318
2018,Climatology + AR(1),2018-05-13,99.39285714285714,4.761628652807757,0.210100177856318
2018,Climatology + AR(1),2018-05-20,83.68285714285715,4.649374958594478,0.210100177856318
2018,Climatology + AR(1),2018-05-27,98.57714285714285,4.48276421727818,0.210100177856318
2018,Climatology + AR(1),2018-06-03,80.00142857142858,4.580838861209786,0.210100177856318
2018,Climatology + AR(1),2018-06-10,64.88285714285715,4.175369200245926,0.210100177856318
2018,Climatology + AR(1),2018-06-17,152.4042857142857,4.347727239546165,0.210100177856318
2018,Climatology + AR(1),2018-06-24,68.25857142857143,4.351151337990465,0.210100177856318
2018,Climatology + AR(1),2018-07-01,38.87571428571429,4.038262211282097,0.210100177856318
2018,Climatology + AR(1),2018-07-08,51.74428571428571,4.156504895471306,0.210100177856318
2018,Climatology + AR(1),2018-07-15,43.470000000000006,3.828475852467367,0.210100177856318
2018,Climatology + AR(1),2018-07-22,36.80857142857143,3.822010926215079,0.210100177856318
2018,Climatology + AR(1),2018-07-29,34.582857142857144,3.571164048710764,0.210100177856318
2018,Climatology + AR(1),2018-08-05,59.50428571428571,3.617490523111797,0.210100177856318
2018,Climatology + AR(1),2018-08-12,39.05428571428571,3.824585480368357,0.210100177856318
2018,Climatology + AR(1),2018-08-19,38.74142857142857,3.852904625177205,0.210100177856318
2018,Climatology + AR(1),2018-08-26,31.807142857142857,3.830166125886565,0.210100177856318
2018,Climatology + AR(1),2018-09-02,37.85428571428572,3.7218864329755377,0.210100177856318
2018,Climatology + AR(1),2018-09-09,41.95,4.090821913577266,0.210100177856318
2018,Climatology + AR(1),2018-09-16,33.33,4.169794093283282,0.210100177856318
2018,Climatology + AR(1),2018-09-23,49.20857142857143,4.143161792567324,0.210100177856318
2018,Climatology + AR(1),2018-09-30,57.55857142857143,4.307081325051812,0.210100177856318
2018,Climatology + AR(1),2018-10-07,83.38714285714286,4.549477515741132,0.210100177856318
2018,Climatology + AR(1),2018-10-14,96.91142857142856,4.854407054424185,0.210100177856318
2018,Climatology + AR(1),2018-10-21,140.48285714285714,5.00495805287808,0.210100177856318
2018,Climatology + AR(1),2018-10-28,171.1542857142857,5.276872136457311,0.210100177856318
2018,Climatology + AR(1),2018-11-04,202.76142857142847,5.4856582839414445,0.210100177856318
2018,Climatology + AR(1),2018-11-11,283.1485714285714,5.770970117981858,0.210100177856318
2018,Climatology + AR(1),2018-11-18,173.0885714285714,5.463541591349466,0.210100177856318
2018,Climatology + AR(1),2018-11-25,168.86714285714285,5.307484213754044,0.210100177856318
2018,Climatology + AR(1),2018-12-02,186.70857142857145,5.342768608191364,0.210100177856318
2018,Climatology + AR(1),2018-12-09,201.8728571428572,5.342222323157638,0.210100177856318
2018,Climatology + AR(1),2018-12-16,175.70142857142858,5.183265534903394,0.210100177856318
2018,Climatology + AR(1),2018-12-23,261.5357142857143,5.207046369842629,0.210100177856318
2018,Climatology + AR(1),2018-12-30,287.3928571428572,5.398866447956088,0.210100177856318
2018,Linear regression,2018-01-07,247.29857142857145,5.285414409732734,0.2690264783500231
2018,Linear regression,2018-01-14,188.26,5.23348539788056,0.2695397774073533
2018,Linear regression,2018-01-21,197.46,5.175109701645646,0.2700437374189722
2018,Linear regression,2018-01-28,148.48857142857145,5.110738861982933,0.2704960059972698
2018,Linear regression,2018-02-04,137.04714285714286,5.041148430291499,0.2708598683467308
2018,Linear regression,2018-02-11,169.39,4.967666454899951,0.2711113714650376
2018,Linear regression,2018-02-18,103.70857142857145,4.892290661042592,0.2712433707656577
2018,Linear regression,2018-02-25,158.08285714285714,4.817664697349892,0.2712655846310147
2018,Linear regression,2018-03-04,104.86,4.746905809049485,0.271201026900953
2018,Linear regression,2018-03-11,96.94857142857144,4.683299848762038,0.2710802163409432
2018,Linear regression,2018-03-18,102.21428571428572,4.629901348700841,0.2709349947242722
2018,Linear regression,2018-03-25,90.97,4.589093358759399,0.2707935333463092
2018,Linear regression,2018-04-01,97.72857142857144,4.562171431374023,0.270677357445847
2018,Linear regression,2018-04-08,94.45285714285714,4.54901699199398,0.2706003406963452
2018,Linear regression,2018-04-15,75.25,4.54791702799221,0.2705690031619881
2018,Linear regression,2018-04-22,92.28,4.555570440337416,0.2705833064686713
2018,Linear regression,2018-04-29,103.68999999999998,4.567298536966504,0.2706374420853006
2018,Linear regression,2018-05-06,68.93714285714286,4.577450883370417,0.270720599788923
2018,Linear regression,2018-05-13,99.39285714285714,4.57997144905123,0.2708180657680059
2018,Linear regression,2018-05-20,83.68285714285715,4.569067152048161,0.2709130229778966
2018,Linear regression,2018-05-27,98.57714285714285,4.539904581272281,0.2709891099309574
2018,Linear regression,2018-06-03,80.00142857142858,4.489253157274344,0.2710333317578417
2018,Linear regression,2018-06-10,64.88285714285715,4.4159954752734905,0.2710385792773204
2018,Linear regression,2018-06-17,152.4042857142857,4.321438000392848,0.2710049953412106
2018,Linear regression,2018-06-24,68.25857142857143,4.209376328812623,0.2709397572427806
2018,Linear regression,2018-07-01,38.87571428571429,4.085896453722207,0.2708553665831287
2018,Linear regression,2018-07-08,51.74428571428571,3.9589236325246726,0.2707670088579178
2018,Linear regression,2018-07-15,43.470000000000006,3.837559883919958,0.2706897541518375
2018,Linear regression,2018-07-22,36.80857142857143,3.731276242149687,0.270636247333315
2018,Linear regression,2018-07-29,34.582857142857144,3.64904355698306,0.2706151818583803
2018,Linear regression,2018-08-05,59.50428571428571,3.598493645063832,0.2706304790422816
2018,Linear regression,2018-08-12,39.05428571428571,3.5851999415988125,0.2706809101529153
2018,Linear regression,2018-08-19,38.74142857142857,3.6121537515187705,0.2707599833651587
2018,Linear regression,2018-08-26,31.807142857142857,3.6794903137976194,0.2708561821127789
2018,Linear regression,2018-09-02,37.85428571428572,3.784490812444485,0.2709538778998653
2018,Linear regression,2018-09-09,41.95,3.92185558649826,0.2710352466497898
2018,Linear regression,2018-09-16,33.33,4.084213830823009,0.2710832210286875
2018,Linear regression,2018-09-23,49.20857142857143,4.262809623975739,0.2710850242859438
2018,Linear regression,2018-09-30,57.55857142857143,4.448286169457172,0.2710354010140073
2018,Linear regression,2018-10-07,83.38714285714286,4.6314817380667215,0.2709385402898271
2018,Linear regression,2018-10-14,96.91142857142856,4.804152794391361,0.2708079991025566
2018,Linear regression,2018-10-21,140.48285714285714,4.959551724019911,0.2706645934240194
2018,Linear regression,2018-10-28,171.1542857142857,5.092806766265992,0.2705329606717137
2018,Linear regression,2018-11-04,202.76142857142847,5.201077513952559,0.2704379708208623
2018,Linear regression,2018-11-11,283.1485714285714,5.28348733000971,0.2704021258369834
2018,Linear regression,2018-11-18,173.0885714285714,5.340860693504386,0.2704445183158224
2018,Linear regression,2018-11-25,168.86714285714285,5.375315504784063,0.2705810662058447
2018,Linear regression,2018-12-02,186.70857142857145,5.389775088151754,0.270825016378644
2018,Linear regression,2018-12-09,201.8728571428572,5.387470359693853,0.2711865024786217
2018,Linear regression,2018-12-16,175.70142857142858,5.371498900337205,0.2716704094769676
2018,Linear regression,2018-12-23,261.5357142857143,5.344495253219904,0.2722727674777139
2018,Linear regression,2018-12-30,287.3928571428572,5.308447539118315,0.2729769286227468
2018,LSTM (small),2018-01-07,247.29857142857145,5.388508160788208,0.0257279392674246
2018,LSTM (small),2018-01-14,188.26,5.231829535594064,0.0352990730356501
2018,LSTM (small),2018-01-21,197.46,5.648214340093031,0.0352990730356501
2018,LSTM (small),2018-01-28,148.48857142857145,5.456856402465328,0.0352990730356501
2018,LSTM (small),2018-02-04,137.04714285714286,5.13504245037531,0.0370086342498864
2018,LSTM (small),2018-02-11,169.39,4.841439312936369,0.0409159400965892
2018,LSTM (small),2018-02-18,103.70857142857145,4.698299950710943,0.0409159400965892
2018,LSTM (small),2018-02-25,158.08285714285714,5.208606640984436,0.0612986758446737
2018,LSTM (small),2018-03-04,104.86,4.788187869225021,0.0644119689676918
2018,LSTM (small),2018-03-11,96.94857142857144,4.524731942588305,0.0836267929570769
2018,LSTM (small),2018-03-18,102.21428571428572,4.325783266892134,0.0874021937123709
2018,LSTM (small),2018-03-25,90.97,4.615589612648063,0.1052859234317573
2018,LSTM (small),2018-04-01,97.72857142857144,4.8692067128188885,0.1794591211147874
2018,LSTM (small),2018-04-08,94.45285714285714,4.518171885830662,0.1794591211147874
2018,LSTM (small),2018-04-15,75.25,4.6759144014068,0.1794591211147874
2018,LSTM (small),2018-04-22,92.28,4.994067424493809,0.1794591211147874
2018,LSTM (small),2018-04-29,103.68999999999998,4.708035310615856,0.2100320523345356
2018,LSTM (small),2018-05-06,68.93714285714286,4.513859045039097,0.2100320523345356
2018,LSTM (small),2018-05-13,99.39285714285714,4.384439903904501,0.2100320523345356
2018,LSTM (small),2018-05-20,83.68285714285715,4.652084767467652,0.2100320523345356
2018,LSTM (small),2018-05-27,98.57714285714285,4.433266010306961,0.2100320523345356
2018,LSTM (small),2018-06-03,80.00142857142858,4.627938712439404,0.2100320523345356
2018,LSTM (small),2018-06-10,64.88285714285715,4.062172357567338,0.2100320523345356
2018,LSTM (small),2018-06-17,152.4042857142857,4.1624716647637126,0.2100320523345356
2018,LSTM (small),2018-06-24,68.25857142857143,4.481858534108332,0.2100320523345356
2018,LSTM (small),2018-07-01,38.87571428571429,4.017259636374056,0.2100320523345356
2018,LSTM (small),2018-07-08,51.74428571428571,4.24338570677764,0.2100320523345356
2018,LSTM (small),2018-07-15,43.470000000000006,4.101856146349896,0.2100320523345356
2018,LSTM (small),2018-07-22,36.80857142857143,3.9489500503571207,0.2100320523345356
2018,LSTM (small),2018-07-29,34.582857142857144,3.708903566222405,0.2100320523345356
2018,LSTM (small),2018-08-05,59.50428571428571,3.7516980748338153,0.2100320523345356
2018,LSTM (small),2018-08-12,39.05428571428571,4.1143831413330645,0.2100320523345356
2018,LSTM (small),2018-08-19,38.74142857142857,3.889893041170901,0.2100320523345356
2018,LSTM (small),2018-08-26,31.807142857142857,3.837452977354371,0.2100320523345356
2018,LSTM (small),2018-09-02,37.85428571428572,3.7813894173556073,0.2100320523345356
2018,LSTM (small),2018-09-09,41.95,4.320462472115711,0.2100320523345356
2018,LSTM (small),2018-09-16,33.33,4.081176086260015,0.2100320523345356
2018,LSTM (small),2018-09-23,49.20857142857143,4.245198179930143,0.2100320523345356
2018,LSTM (small),2018-09-30,57.55857142857143,4.37471307240554,0.2100320523345356
2018,LSTM (small),2018-10-07,83.38714285714286,4.629474229263924,0.2100320523345356
2018,LSTM (small),2018-10-14,96.91142857142856,4.92044500989881,0.2100320523345356
2018,LSTM (small),2018-10-21,140.48285714285714,4.83360426269791,0.2100320523345356
2018,LSTM (small),2018-10-28,171.1542857142857,5.076791559322571,0.2100320523345356
2018,LSTM (small),2018-11-04,202.76142857142847,5.140659797542283,0.2100320523345356
2018,LSTM (small),2018-11-11,283.1485714285714,5.821046872667451,0.2100320523345356
2018,LSTM (small),2018-11-18,173.0885714285714,5.0252406748013545,0.2100320523345356
2018,LSTM (small),2018-11-25,168.86714285714285,5.306729752925443,0.2100320523345356
2018,LSTM (small),2018-12-02,186.70857142857145,5.501137021256482,0.2100320523345356
2018,LSTM (small),2018-12-09,201.8728571428572,5.218621585272979,0.2100320523345356
2018,LSTM (small),2018-12-16,175.70142857142858,5.246940137546662,0.2100320523345356
2018,LSTM (small),2018-12-23,261.5357142857143,5.142438546852118,0.2100320523345356
2018,LSTM (small),2018-12-30,287.3928571428572,5.152640368660512,0.2100320523345356
2018,Fourier+ARMA const,2018-01-07,247.29857142857145,5.3895900802287455,0.2374247157524943
2018,Fourier+ARMA const,2018-01-14,188.26,5.305852977088351,0.2525987241268368
2018,Fourier+ARMA const,2018-01-21,197.46,5.238117612685674,0.2545327484468855
2018,Fourier+ARMA const,2018-01-28,148.48857142857145,5.172034472114514,0.2547867623582946
2018,Fourier+ARMA const,2018-02-04,137.04714285714286,5.102943106214864,0.254820249473859
2018,Fourier+ARMA const,2018-02-11,169.39,5.030192317561943,0.2548246663046365
2018,Fourier+ARMA const,2018-02-18,103.70857142857145,4.955109809528625,0.2548252489064347
2018,Fourier+ARMA const,2018-02-25,158.08285714285714,4.880190712528149,0.2548253257551443
2018,Fourier+ARMA const,2018-03-04,104.86,4.80862639141062,0.2548253358919665
2018,Fourier+ARMA const,2018-03-11,96.94857142857144,4.743874767097245,0.2548253372290764
2018,Fourier+ARMA const,2018-03-18,102.21428571428572,4.689197619568091,0.2548253374054496
2018,Fourier+ARMA const,2018-03-25,90.97,4.647180965390507,0.2548253374287143
2018,Fourier+ARMA const,2018-04-01,97.72857142857144,4.619290882154944,0.2548253374317831
2018,Fourier+ARMA const,2018-04-08,94.45285714285714,4.60552727563094,0.2548253374321879
2018,Fourier+ARMA const,2018-04-15,75.25,4.604232549162914,0.2548253374322413
2018,Fourier+ARMA const,2018-04-22,92.28,4.61209583569165,0.2548253374322483
2018,Fourier+ARMA const,2018-04-29,103.68999999999998,4.624369947792228,0.2548253374322493
2018,Fourier+ARMA const,2018-05-06,68.93714285714286,4.635291028458622,0.2548253374322494
2018,Fourier+ARMA const,2018-05-13,99.39285714285714,4.638663755677273,0.2548253374322494
2018,Fourier+ARMA const,2018-05-20,83.68285714285715,4.62855150537937,0.2548253374322494
2018,Fourier+ARMA const,2018-05-27,98.57714285714285,4.599994287811832,0.2548253374322494
2018,Fourier+ARMA const,2018-06-03,80.00142857142858,4.549669872297565,0.2548253374322494
2018,Fourier+ARMA const,2018-06-10,64.88285714285715,4.476416488227245,0.2548253374322494
2018,Fourier+ARMA const,2018-06-17,152.4042857142857,4.381548710555602,0.2548253374322494
2018,Fourier+ARMA const,2018-06-24,68.25857142857143,4.268920174588383,0.2548253374322494
2018,Fourier+ARMA const,2018-07-01,38.87571428571429,4.144715049252007,0.2548253374322494
2018,Fourier+ARMA const,2018-07-08,51.74428571428571,4.016981341097586,0.2548253374322494
2018,Fourier+ARMA const,2018-07-15,43.470000000000006,3.894949315067898,0.2548253374322494
2018,Fourier+ARMA const,2018-07-22,36.80857142857143,3.788203891388403,0.2548253374322494
2018,Fourier+ARMA const,2018-07-29,34.582857142857144,3.705797644471706,0.2548253374322494
2018,Fourier+ARMA const,2018-08-05,59.50428571428571,3.655398768711532,0.2548253374322494
2018,Fourier+ARMA const,2018-08-12,39.05428571428571,3.642565094698568,0.2548253374322494
2018,Fourier+ARMA const,2018-08-19,38.74142857142857,3.6702213005273294,0.2548253374322494
2018,Fourier+ARMA const,2018-08-26,31.807142857142857,3.738393541413981,0.2548253374322494
2018,Fourier+ARMA const,2018-09-02,37.85428571428572,3.8442265946821976,0.2548253374322494
2018,Fourier+ARMA const,2018-09-09,41.95,3.982276818824272,0.2548253374322494
2018,Fourier+ARMA const,2018-09-16,33.33,4.145043598959085,0.2548253374322494
2018,Fourier+ARMA const,2018-09-23,49.20857142857143,4.323676171044727,0.2548253374322494
2018,Fourier+ARMA const,2018-09-30,57.55857142857143,4.508774830078353,0.2548253374322494
2018,Fourier+ARMA const,2018-10-07,83.38714285714286,4.691197574489128,0.2548253374322494
2018,Fourier+ARMA const,2018-10-14,96.91142857142856,4.862786007960081,0.2548253374322494
2018,Fourier+ARMA const,2018-10-21,140.48285714285714,5.016937257638635,0.2548253374322494
2018,Fourier+ARMA const,2018-10-28,171.1542857142857,5.148969962108982,0.2548253374322494
2018,Fourier+ARMA const,2018-11-04,202.76142857142847,5.256259205005463,0.2548253374322494
2018,Fourier+ARMA const,2018-11-11,283.1485714285714,5.338144145270946,0.2548253374322494
2018,Fourier+ARMA const,2018-11-18,173.0885714285714,5.395639349839632,0.2548253374322494
2018,Fourier+ARMA const,2018-11-25,168.86714285714285,5.431003069486344,0.2548253374322494
2018,Fourier+ARMA const,2018-12-02,186.70857142857145,5.447230219777127,0.2548253374322494
2018,Fourier+ARMA const,2018-12-09,201.8728571428572,5.447542985650095,0.2548253374322494
2018,Fourier+ARMA const,2018-12-16,175.70142857142858,5.434947352701787,0.2548253374322494
2018,Fourier+ARMA const,2018-12-23,261.5357142857143,5.411910354451933,0.2548253374322494
2018,Fourier+ARMA const,2018-12-30,287.3928571428572,5.380192438819538,0.2548253374322494
2018,Fourier+ARMA linear,2018-01-07,247.29857142857145,5.411193678330818,0.2380904188730782
2018,Fourier+ARMA linear,2018-01-14,188.26,5.328287756047553,0.253548873550548
2018,Fourier+ARMA linear,2018-01-21,197.46,5.251322819648976,0.2555502975161928
2018,Fourier+ARMA linear,2018-01-28,148.48857142857145,5.170645037097565,0.2558174363267982
2018,Fourier+ARMA linear,2018-02-04,137.04714285714286,5.0843125168652845,0.2558532301932398
2018,Fourier+ARMA linear,2018-02-11,169.39,4.993727038422378,0.2558580286654566
2018,Fourier+ARMA linear,2018-02-18,103.70857142857145,4.901945858546712,0.255858671985659
2018,Fourier+ARMA linear,2018-02-25,158.08285714285714,4.812881675359503,0.2558587582349224
2018,Fourier+ARMA linear,2018-03-04,104.86,4.730751730294179,0.2558587697982847
2018,Fourier+ARMA linear,2018-03-11,96.94857142857144,4.659571907619611,0.2558587713485747
2018,Fourier+ARMA linear,2018-03-18,102.21428571428572,4.602659976782625,0.2558587715564208
2018,Fourier+ARMA linear,2018-03-25,90.97,4.562177754272358,0.2558587715842865
2018,Fourier+ARMA linear,2018-04-01,97.72857142857144,4.538764266633289,0.2558587715880225
2018,Fourier+ARMA linear,2018-04-08,94.45285714285714,4.531312751351925,0.2558587715885234
2018,Fourier+ARMA linear,2018-04-15,75.25,4.536932320846682,0.2558587715885905
2018,Fourier+ARMA linear,2018-04-22,92.28,4.551115022368581,0.2558587715885995
2018,Fourier+ARMA linear,2018-04-29,103.68999999999998,4.568104515693424,0.2558587715886007
2018,Fourier+ARMA linear,2018-05-06,68.93714285714286,4.581437179198881,0.2558587715886009
2018,Fourier+ARMA linear,2018-05-13,99.39285714285714,4.584603560097188,0.2558587715886009
2018,Fourier+ARMA linear,2018-05-20,83.68285714285715,4.571760762287285,0.2558587715886009
2018,Fourier+ARMA linear,2018-05-27,98.57714285714285,4.538416979844403,0.2558587715886009
2018,Fourier+ARMA linear,2018-06-03,80.00142857142858,4.482009320981921,0.2558587715886009
2018,Fourier+ARMA linear,2018-06-10,64.88285714285715,4.402305553241939,0.2558587715886009
2018,Fourier+ARMA linear,2018-06-17,152.4042857142857,4.301578465414633,0.2558587715886009
2018,Fourier+ARMA linear,2018-06-24,68.25857142857143,4.184526129590197,0.2558587715886009
2018,Fourier+ARMA linear,2018-07-01,38.87571428571429,4.057939566546041,0.2558587715886009
2018,Fourier+ARMA linear,2018-07-08,51.74428571428571,3.9301477994640353,0.2558587715886009
2018,Fourier+ARMA linear,2018-07-15,43.470000000000006,3.810295595419893,0.2558587715886009
2018,Fourier+ARMA linear,2018-07-22,36.80857142857143,3.707528280718111,0.2558587715886009
2018,Fourier+ARMA linear,2018-07-29,34.582857142857144,3.6301685663262986,0.2558587715886009
2018,Fourier+ARMA linear,2018-08-05,59.50428571428571,3.584971065509348,0.2558587715886009
2018,Fourier+ARMA linear,2018-08-12,39.05428571428571,3.5765310582337357,0.2558587715886009
2018,Fourier+ARMA linear,2018-08-19,38.74142857142857,3.606906192988482,0.2558587715886009
2018,Fourier+ARMA linear,2018-08-26,31.807142857142857,3.675485414816546,0.2558587715886009
2018,Fourier+ARMA linear,2018-09-02,37.85428571428572,3.7791114507707535,0.2558587715886009
2018,Fourier+ARMA linear,2018-09-09,41.95,3.9124350612105134,0.2558587715886009
2018,Fourier+ARMA linear,2018-09-16,33.33,4.0684543509447,0.2558587715886009
2018,Fourier+ARMA linear,2018-09-23,49.20857142857143,4.239173664095123,0.2558587715886009
2018,Fourier+ARMA linear,2018-09-30,57.55857142857143,4.4163060959452825,0.2558587715886009
2018,Fourier+ARMA linear,2018-10-07,83.38714285714286,4.591942519405493,0.2558587715886009
2018,Fourier+ARMA linear,2018-10-14,96.91142857142856,4.759118135898463,0.2558587715886009
2018,Fourier+ARMA linear,2018-10-21,140.48285714285714,4.912223659055225,0.2558587715886009
2018,Fourier+ARMA linear,2018-10-28,171.1542857142857,5.047230084123807,0.2558587715886009
2018,Fourier+ARMA linear,2018-11-04,202.76142857142847,5.161720665395457,0.2558587715886009
2018,Fourier+ARMA linear,2018-11-11,283.1485714285714,5.254747999542674,0.2558587715886009
2018,Fourier+ARMA linear,2018-11-18,173.0885714285714,5.326554895629985,0.2558587715886009
2018,Fourier+ARMA linear,2018-11-25,168.86714285714285,5.378212421617226,0.2558587715886009
2018,Fourier+ARMA linear,2018-12-02,186.70857142857145,5.41123541651204,0.2558587715886009
2018,Fourier+ARMA linear,2018-12-09,201.8728571428572,5.427234170928138,0.2558587715886009
2018,Fourier+ARMA linear,2018-12-16,175.70142857142858,5.427651365494186,0.2558587715886009
2018,Fourier+ARMA linear,2018-12-23,261.5357142857143,5.413617236187793,0.2558587715886009
2018,Fourier+ARMA linear,2018-12-30,287.3928571428572,5.385935676918827,0.2558587715886009
2018,Fourier+ARMA (selected),2018-01-07,247.29857142857145,5.309789667756228,0.2205624363057983
2018,Fourier+ARMA (selected),2018-01-14,188.26,5.359552174866449,0.2243261023324612
2018,Fourier+ARMA (selected),2018-01-21,197.46,5.381247362830338,0.2270602597467765
2018,Fourier+ARMA (selected),2018-01-28,148.48857142857145,5.354735401288607,0.2290546371425751
2018,Fourier+ARMA (selected),2018-02-04,137.04714285714286,5.272923292846604,0.2305135899909882
2018,Fourier+ARMA (selected),2018-02-11,169.39,5.1436448852893815,0.2315830587059729
2018,Fourier+ARMA (selected),2018-02-18,103.70857142857145,4.987091530970469,0.2323681826356737
2018,Fourier+ARMA (selected),2018-02-25,158.08285714285714,4.829792478823225,0.2329451811323422
2018,Fourier+ARMA (selected),2018-03-04,104.86,4.69715110325341,0.2333695570368351
2018,Fourier+ARMA (selected),2018-03-11,96.94857142857144,4.606864882627014,0.23368185907438
2018,Fourier+ARMA (selected),2018-03-18,102.21428571428572,4.565120969601897,0.2339117810947961
2018,Fourier+ARMA (selected),2018-03-25,90.97,4.566445805705117,0.2340811055015287
2018,Fourier+ARMA (selected),2018-04-01,97.72857142857144,4.596861015150632,0.2342058313374679
2018,Fourier+ARMA (selected),2018-04-08,94.45285714285714,4.638977439521333,0.2342977206982259
2018,Fourier+ARMA (selected),2018-04-15,75.25,4.677173226952604,0.2343654266683544
2018,Fourier+ARMA (selected),2018-04-22,92.28,4.701180105010984,0.2344153182942292
2018,Fourier+ARMA (selected),2018-04-29,103.68999999999998,4.707138702533537,0.234452085195834
2018,Fourier+ARMA (selected),2018-05-06,68.93714285714286,4.696184503202966,0.2344791813425209
2018,Fourier+ARMA (selected),2018-05-13,99.39285714285714,4.671518364880572,0.2344991511371806
2018,Fourier+ARMA (selected),2018-05-20,83.68285714285715,4.6353843510578825,0.2345138692161831
2018,Fourier+ARMA (selected),2018-05-27,98.57714285714285,4.587275465101402,0.2345247169022697
2018,Fourier+ARMA (selected),2018-06-03,80.00142857142858,4.524082476529186,0.2345327121019375
2018,Fourier+ARMA (selected),2018-06-10,64.88285714285715,4.442043907054468,0.2345386049617183
2018,Fourier+ARMA (selected),2018-06-17,152.4042857142857,4.339584413227662,0.2345429483262637
2018,Fourier+ARMA (selected),2018-06-24,68.25857142857143,4.219741731349095,0.2345461496452373
2018,Fourier+ARMA (selected),2018-07-01,38.87571428571429,4.091025751467874,0.2345485092184224
2018,Fourier+ARMA (selected),2018-07-08,51.74428571428571,3.9661697098500346,0.2345502483775053
2018,Fourier+ARMA (selected),2018-07-15,43.470000000000006,3.85908385108266,0.2345515302539411
2018,Fourier+ARMA (selected),2018-07-22,36.80857142857143,3.781075434293788,0.2345524750841154
2018,Fourier+ARMA (selected),2018-07-29,34.582857142857144,3.737757458634132,0.2345531714891256
2018,Fourier+ARMA (selected),2018-08-05,59.50428571428571,3.727879404359554,0.2345536847881263
2018,Fourier+ARMA (selected),2018-08-12,39.05428571428571,3.7446297930512737,0.2345540631255003
2018,Fourier+ARMA (selected),2018-08-19,38.74142857142857,3.779025856495195,0.2345543419868266
2018,Fourier+ARMA (selected),2018-08-26,31.807142857142857,3.8241673026602783,0.234554547527366
2018,Fourier+ARMA (selected),2018-09-02,37.85428571428572,3.8787134477762297,0.2345546990253359
2018,Fourier+ARMA (selected),2018-09-09,41.95,3.948125967123648,0.2345548106901177
2018,Fourier+ARMA (selected),2018-09-16,33.33,4.042967437868793,0.234554892995018
2018,Fourier+ARMA (selected),2018-09-23,49.20857142857143,4.174612319267157,0.2345549536596005
2018,Fourier+ARMA (selected),2018-09-30,57.55857142857143,4.349737110269404,0.2345549983737287
2018,Fourier+ARMA (selected),2018-10-07,83.38714285714286,4.565537820283974,0.2345550313312353
2018,Fourier+ARMA (selected),2018-10-14,96.91142857142856,4.807540203589238,0.234555055623273
2018,Fourier+ARMA (selected),2018-10-21,140.48285714285714,5.051112551144321,0.2345550735282414
2018,Fourier+ARMA (selected),2018-10-28,171.1542857142857,5.266591564181686,0.2345550867254834
2018,Fourier+ARMA (selected),2018-11-04,202.76142857142847,5.426684416412435,0.2345550964527947
2018,Fourier+ARMA (selected),2018-11-11,283.1485714285714,5.513943466469667,0.2345551036225189
2018,Fourier+ARMA (selected),2018-11-18,173.0885714285714,5.52593855728152,0.2345551089071185
2018,Fourier+ARMA (selected),2018-11-25,168.86714285714285,5.476363143512947,0.2345551128022465
2018,Fourier+ARMA (selected),2018-12-02,186.70857142857145,5.391529262742191,0.2345551156732345
2018,Fourier+ARMA (selected),2018-12-09,201.8728571428572,5.303147394496333,0.2345551177893581
2018,Fourier+ARMA (selected),2018-12-16,175.70142857142858,5.239481461487986,0.2345551193490926
2018,Fourier+ARMA (selected),2018-12-23,261.5357142857143,5.217520283416137,0.2345551204987284
2018,Fourier+ARMA (selected),2018-12-30,287.3928571428572,5.238525099509518,0.2345551213460924
2018,SARIMA D=1,2018-01-07,247.29857142857145,5.409659899443629,0.267927671145212
2018,SARIMA D=1,2018-01-14,188.26,5.253543660011721,0.275386096616411
2018,SARIMA D=1,2018-01-21,197.46,5.396440760971164,0.2810729394907438
2018,SARIMA D=1,2018-01-28,148.48857142857145,5.230473473806913,0.285435132390163
2018,SARIMA D=1,2018-02-04,137.04714285714286,5.096861335633896,0.2887958409883583
2018,SARIMA D=1,2018-02-11,169.39,4.96113860869443,0.2913933334853647
2018,SARIMA D=1,2018-02-18,103.70857142857145,4.950657217484924,0.2934057763966039
2018,SARIMA D=1,2018-02-25,158.08285714285714,5.14386397435868,0.2949677846156238
2018,SARIMA D=1,2018-03-04,104.86,4.7076110864437,0.2961818581031018
2018,SARIMA D=1,2018-03-11,96.94857142857144,4.470323403391628,0.2971265005445828
2018,SARIMA D=1,2018-03-18,102.21428571428572,4.459352473259463,0.2978621045659911
2018,SARIMA D=1,2018-03-25,90.97,4.682580408780508,0.2984352878814206
2018,SARIMA D=1,2018-04-01,97.72857142857144,4.595585465043604,0.2988821289518138
2018,SARIMA D=1,2018-04-08,94.45285714285714,4.587851434749108,0.2992306058759698
2018,SARIMA D=1,2018-04-15,75.25,4.77365609029578,0.2995024485492239
2018,SARIMA D=1,2018-04-22,92.28,4.784818028896921,0.2997145542375082
2018,SARIMA D=1,2018-04-29,103.68999999999998,4.640149640249854,0.299880074399042
2018,SARIMA D=1,2018-05-06,68.93714285714286,4.846607103224174,0.3000092521245553
2018,SARIMA D=1,2018-05-13,99.39285714285714,4.710664253508525,0.3001100694453318
2018,SARIMA D=1,2018-05-20,83.68285714285715,4.65023995155809,0.3001887486529896
2018,SARIMA D=1,2018-05-27,98.57714285714285,4.5957996401825865,0.3002501412583481
2018,SARIMA D=1,2018-06-03,80.00142857142858,4.442078451294798,0.3002980301412307
2018,SARIMA D=1,2018-06-10,64.88285714285715,4.254995373223001,0.3003353644662458
2018,SARIMA D=1,2018-06-17,152.4042857142857,4.315706297818688,0.30036444241222
2018,SARIMA D=1,2018-06-24,68.25857142857143,4.226494557329829,0.3003870533162273
2018,SARIMA D=1,2018-07-01,38.87571428571429,3.9160338794931184,0.3004045881935883
2018,SARIMA D=1,2018-07-08,51.74428571428571,4.039625476283305,0.3004181255634152
2018,SARIMA D=1,2018-07-15,43.470000000000006,3.82388181199608,0.3004284979379487
2018,SARIMA D=1,2018-07-22,36.80857142857143,3.645026090073805,0.300436343112916
2018,SARIMA D=1,2018-07-29,34.582857142857144,3.4378674670624227,0.300442143442146
2018,SARIMA D=1,2018-08-05,59.50428571428571,3.770260401684317,0.3004462555290885
2018,SARIMA D=1,2018-08-12,39.05428571428571,3.7916487533070815,0.3004489321715121
2018,SARIMA D=1,2018-08-19,38.74142857142857,3.720163494015255,0.3004503379150091
2018,SARIMA D=1,2018-08-26,31.807142857142857,3.8646490748948414,0.3004505591753177
2018,SARIMA D=1,2018-09-02,37.85428571428572,3.7144246629346296,0.3004496095538936
2018,SARIMA D=1,2018-09-09,41.95,4.000060221028509,0.3004474306745238
2018,SARIMA D=1,2018-09-16,33.33,4.210431158249292,0.3004438885925707
2018,SARIMA D=1,2018-09-23,49.20857142857143,3.9932833357660784,0.3004387655554261
2018,SARIMA D=1,2018-09-30,57.55857142857143,4.398970639199341,0.300431746605975
2018,SARIMA D=1,2018-10-07,83.38714285714286,4.637761648543584,0.3004224001902676
2018,SARIMA D=1,2018-10-14,96.91142857142856,4.7645254665109125,0.3004101516453352
2018,SARIMA D=1,2018-10-21,140.48285714285714,5.145599682147696,0.300394247743475
2018,SARIMA D=1,2018-10-28,171.1542857142857,5.262247487091619,0.3003737103451821
2018,SARIMA D=1,2018-11-04,202.76142857142847,5.584530644273185,0.3003472761018363
2018,SARIMA D=1,2018-11-11,283.1485714285714,5.820026847129431,0.3003133185094096
2018,SARIMA D=1,2018-11-18,173.0885714285714,5.416519097016553,0.3002697475884057
2018,SARIMA D=1,2018-11-25,168.86714285714285,5.250433847106517,0.3002138805169127
2018,SARIMA D=1,2018-12-02,186.70857142857145,5.349096484803704,0.3001422756961475
2018,SARIMA D=1,2018-12-09,201.8728571428572,5.299264868729479,0.3000505191268388
2018,SARIMA D=1,2018-12-16,175.70142857142858,4.983164571979654,0.2999329498322835
2018,SARIMA D=1,2018-12-23,261.5357142857143,5.297781005162119,0.2997823066220706
2018,SARIMA D=1,2018-12-30,287.3928571428572,5.440385047825892,0.2971079886037641
2018,SARIMA D=0,2018-01-07,247.29857142857145,5.319606623118416,0.2751196727808198
2018,SARIMA D=0,2018-01-14,188.26,5.271042284398704,0.3195342798011806
2018,SARIMA D=0,2018-01-21,197.46,5.2986719618950335,0.3528981960231064
2018,SARIMA D=0,2018-01-28,148.48857142857145,5.149378582653403,0.3789385601203773
2018,SARIMA D=0,2018-02-04,137.04714285714286,5.157011785806478,0.3997281177561304
2018,SARIMA D=0,2018-02-11,169.39,5.046412699384085,0.4165735334160224
2018,SARIMA D=0,2018-02-18,103.70857142857145,5.038655894464204,0.4303651759478031
2018,SARIMA D=0,2018-02-25,158.08285714285714,5.189011052165819,0.4417423268974096
2018,SARIMA D=0,2018-03-04,104.86,4.944540613737077,0.4511813010349554
2018,SARIMA D=0,2018-03-11,96.94857142857144,4.844030271253157,0.4590467669987588
2018,SARIMA D=0,2018-03-18,102.21428571428572,4.8866884164681625,0.4656236976390841
2018,SARIMA D=0,2018-03-25,90.97,4.947704227654553,0.4711383296581715
2018,SARIMA D=0,2018-04-01,97.72857142857144,4.869363513083735,0.475772503261355
2018,SARIMA D=0,2018-04-08,94.45285714285714,4.798391561103644,0.4796738150590925
2018,SARIMA D=0,2018-04-15,75.25,4.948368794535177,0.4829630132880597
2018,SARIMA D=0,2018-04-22,92.28,4.892159937402613,0.4857395131509097
2018,SARIMA D=0,2018-04-29,103.68999999999998,4.786295110931943,0.488085592465403
2018,SARIMA D=0,2018-05-06,68.93714285714286,4.943345508045157,0.4900696371268009
2018,SARIMA D=0,2018-05-13,99.39285714285714,4.88683539980168,0.4917486872464416
2018,SARIMA D=0,2018-05-20,83.68285714285715,4.883923155167991,0.4931704586725861
2018,SARIMA D=0,2018-05-27,98.57714285714285,4.748744795100201,0.494374964344301
2018,SARIMA D=0,2018-06-03,80.00142857142858,4.726864614873344,0.4953958259374815
2018,SARIMA D=0,2018-06-10,64.88285714285715,4.590301293308782,0.4962613427542471
2018,SARIMA D=0,2018-06-17,152.4042857142857,4.583079828969348,0.4969953682185444
2018,SARIMA D=0,2018-06-24,68.25857142857143,4.572931788883623,0.4976180324180934
2018,SARIMA D=0,2018-07-01,38.87571428571429,4.40180154108023,0.4981463404181763
2018,SARIMA D=0,2018-07-08,51.74428571428571,4.568611692094571,0.4985946696038684
2018,SARIMA D=0,2018-07-15,43.470000000000006,4.380590603273434,0.4989751844368203
2018,SARIMA D=0,2018-07-22,36.80857142857143,4.376296557899767,0.4992981832975737
2018,SARIMA D=0,2018-07-29,34.582857142857144,4.252795790805932,0.499572389216495
2018,SARIMA D=0,2018-08-05,59.50428571428571,4.404387168729384,0.4998051940582428
2018,SARIMA D=0,2018-08-12,39.05428571428571,4.420848297283486,0.5000028639605104
2018,SARIMA D=0,2018-08-19,38.74142857142857,4.3844267880357775,0.5001707124246507
2018,SARIMA D=0,2018-08-26,31.807142857142857,4.459224279912048,0.5003132463306976
2018,SARIMA D=0,2018-09-02,37.85428571428572,4.306992863006858,0.5004342892405614
2018,SARIMA D=0,2018-09-09,41.95,4.480242743089002,0.5005370856143926
2018,SARIMA D=0,2018-09-16,33.33,4.547360429162239,0.5006243889610215
2018,SARIMA D=0,2018-09-23,49.20857142857143,4.455743244590497,0.5006985364469013
2018,SARIMA D=0,2018-09-30,57.55857142857143,4.603294762506082,0.5007615120781075
2018,SARIMA D=0,2018-10-07,83.38714285714286,4.621435855360482,0.5008150002302358
2018,SARIMA D=0,2018-10-14,96.91142857142856,4.760744023352447,0.5008604310185188
2018,SARIMA D=0,2018-10-21,140.48285714285714,4.905370481798555,0.5008990187648102
2018,SARIMA D=0,2018-10-28,171.1542857142857,4.881368301008111,0.5009317946209979
2018,SARIMA D=0,2018-11-04,202.76142857142847,4.886983308960708,0.5009596342432091
2018,SARIMA D=0,2018-11-11,283.1485714285714,5.14216141891473,0.5009832812724366
2018,SARIMA D=0,2018-11-18,173.0885714285714,4.907160462844458,0.5010033672605158
2018,SARIMA D=0,2018-11-25,168.86714285714285,4.880598984147565,0.501020428582072
2018,SARIMA D=0,2018-12-02,186.70857142857145,4.911033617859982,0.5010349207901448
2018,SARIMA D=0,2018-12-09,201.8728571428572,4.85827576509485,0.5010472308031856
2018,SARIMA D=0,2018-12-16,175.70142857142858,4.771773532034739,0.5010576872519676
2018,SARIMA D=0,2018-12-23,261.5357142857143,4.886711051126166,0.5010665692649143
2018,SARIMA D=0,2018-12-30,287.3928571428572,4.969630734305946,0.5010741139280097
2019,Seasonal naive,2019-01-06,282.41142857142853,5.510596397836895,0.3318639167816877
2019,Seasonal naive,2019-01-13,215.72,5.237823986119074,0.3318639167816877
2019,Seasonal naive,2019-01-20,239.19571428571427,5.285536032183304,0.3318639167816877
2019,Seasonal naive,2019-01-27,116.32714285714285,5.000507995204216,0.3318639167816877
2019,Seasonal naive,2019-02-03,166.56714285714287,4.92032497508269,0.3318639167816877
2019,Seasonal naive,2019-02-10,134.56428571428572,5.1322037485982905,0.3318639167816877
2019,Seasonal naive,2019-02-17,152.75857142857143,4.641584767832887,0.3318639167816877
2019,Seasonal naive,2019-02-24,90.08714285714288,5.063119307867456,0.3318639167816877
2019,Seasonal naive,2019-03-03,80.32000000000001,4.652626127144386,0.3318639167816877
2019,Seasonal naive,2019-03-10,86.03,4.574180646444166,0.3318639167816877
2019,Seasonal naive,2019-03-17,82.42142857142858,4.627071449941192,0.3318639167816877
2019,Seasonal naive,2019-03-24,79.07571428571428,4.510529781833971,0.3318639167816877
2019,Seasonal naive,2019-03-31,87.09142857142857,4.582193956711639,0.3318639167816877
2019,Seasonal naive,2019-04-07,104.12285714285711,4.548100843811397,0.3318639167816877
2019,Seasonal naive,2019-04-14,72.85857142857142,4.3208159036289855,0.3318639167816877
2019,Seasonal naive,2019-04-21,61.77,4.524827433305553,0.3318639167816877
2019,Seasonal naive,2019-04-28,88.33,4.6414056785701865,0.3318639167816877
2019,Seasonal naive,2019-05-05,85.77428571428571,4.233195116324223,0.3318639167816877
2019,Seasonal naive,2019-05-12,129.04857142857142,4.599080251350687,0.3318639167816877
2019,Seasonal naive,2019-05-19,86.87,4.427034143410322,0.3318639167816877
2019,Seasonal naive,2019-05-26,67.29142857142857,4.59083941787023,0.3318639167816877
2019,Seasonal naive,2019-06-02,78.25999999999999,4.382044491657302,0.3318639167816877
2019,Seasonal naive,2019-06-09,70.20857142857143,4.17258344618121,0.3318639167816877
2019,Seasonal naive,2019-06-16,69.01285714285714,5.026536764341959,0.3318639167816877
2019,Seasonal naive,2019-06-23,53.53857142857142,4.223303014876486,0.3318639167816877
2019,Seasonal naive,2019-06-30,56.73285714285714,3.660369744239649,0.3318639167816877
2019,Seasonal naive,2019-07-07,46.77428571428572,3.946314005068647,0.3318639167816877
2019,Seasonal naive,2019-07-14,62.93857142857143,3.772071045000701,0.3318639167816877
2019,Seasonal naive,2019-07-21,42.65,3.605730737308065,0.3318639167816877
2019,Seasonal naive,2019-07-28,42.49,3.5433581009847326,0.3318639167816877
2019,Seasonal naive,2019-08-04,34.18857142857143,4.086048338769158,0.3318639167816877
2019,Seasonal naive,2019-08-11,28.487142857142857,3.6649526196691937,0.3318639167816877
2019,Seasonal naive,2019-08-18,20.78142857142857,3.6569095331747534,0.3318639167816877
2019,Seasonal naive,2019-08-25,45.11857142857143,3.459690882712398,0.3318639167816877
2019,Seasonal naive,2019-09-01,39.64142857142857,3.633744202384664,0.3318639167816877
2019,Seasonal naive,2019-09-08,46.80571428571428,3.736478432913215,0.3318639167816877
2019,Seasonal naive,2019-09-15,50.56857142857143,3.506457892319648,0.3318639167816877
2019,Seasonal naive,2019-09-22,39.85142857142857,3.8960678243522873,0.3318639167816877
2019,Seasonal naive,2019-09-29,25.55,4.05280306288858,0.3318639167816877
2019,Seasonal naive,2019-10-06,43.25571428571429,4.423494135096081,0.3318639167816877
2019,Seasonal naive,2019-10-13,87.52285714285713,4.573797453855727,0.3318639167816877
2019,Seasonal naive,2019-10-20,111.85142857142856,4.945085468111484,0.3318639167816877
2019,Seasonal naive,2019-10-27,140.25571428571428,5.142565405353804,0.3318639167816877
2019,Seasonal naive,2019-11-03,353.36857142857144,5.312030059206812,0.3318639167816877
2019,Seasonal naive,2019-11-10,176.22285714285712,5.645971747265686,0.3318639167816877
2019,Seasonal naive,2019-11-17,297.9271428571428,5.15380343705958,0.3318639167816877
2019,Seasonal naive,2019-11-24,152.52142857142854,5.129112268815404,0.3318639167816877
2019,Seasonal naive,2019-12-01,86.82571428571428,5.22954895966294,0.3318639167816877
2019,Seasonal naive,2019-12-08,204.55428571428573,5.30763807914836,0.3318639167816877
2019,Seasonal naive,2019-12-15,184.0914285714286,5.168786125902334,0.3318639167816877
2019,Seasonal naive,2019-12-22,185.57857142857145,5.566570848885866,0.3318639167816877
2019,Seasonal naive,2019-12-29,234.32857142857145,5.660850119970929,0.3318639167816877
2019,Climatology,2019-01-06,282.41142857142853,5.434197948032715,0.2113477167849093
2019,Climatology,2019-01-13,215.72,5.267708876379964,0.2113477167849093
2019,Climatology,2019-01-20,239.19571428571427,5.399659353705149,0.2113477167849093
2019,Climatology,2019-01-27,116.32714285714285,5.182127044787552,0.2113477167849093
2019,Climatology,2019-02-03,166.56714285714287,5.068326379352324,0.2113477167849093
2019,Climatology,2019-02-10,134.56428571428572,5.005606412276393,0.2113477167849093
2019,Climatology,2019-02-17,152.75857142857143,4.894784052763326,0.2113477167849093
2019,Climatology,2019-02-24,90.08714285714288,5.122283077567929,0.2113477167849093
2019,Climatology,2019-03-03,80.32000000000001,4.793069511607513,0.2113477167849093
2019,Climatology,2019-03-10,86.03,4.489640694836053,0.2113477167849093
2019,Climatology,2019-03-17,82.42142857142858,4.524430400320788,0.2113477167849093
2019,Climatology,2019-03-24,79.07571428571428,4.535984248620467,0.2113477167849093
2019,Climatology,2019-03-31,87.09142857142857,4.636562361181251,0.2113477167849093
2019,Climatology,2019-04-07,104.12285714285711,4.520754073584595,0.2113477167849093
2019,Climatology,2019-04-14,72.85857142857142,4.620245071635307,0.2113477167849093
2019,Climatology,2019-04-21,61.77,4.6658941641564855,0.2113477167849093
2019,Climatology,2019-04-28,88.33,4.723595977576291,0.2113477167849093
2019,Climatology,2019-05-05,85.77428571428571,4.553601588555389,0.2113477167849093
2019,Climatology,2019-05-12,129.04857142857142,4.720991552005117,0.2113477167849093
2019,Climatology,2019-05-19,86.87,4.59378975463906,0.2113477167849093
2019,Climatology,2019-05-26,67.29142857142857,4.509783017368246,0.2113477167849093
2019,Climatology,2019-06-02,78.25999999999999,4.531140268800598,0.2113477167849093
2019,Climatology,2019-06-09,70.20857142857143,4.174672761722088,0.2113477167849093
2019,Climatology,2019-06-16,69.01285714285714,4.517429620742329,0.2113477167849093
2019,Climatology,2019-06-23,53.53857142857142,4.319189257210957,0.2113477167849093
2019,Climatology,2019-06-30,56.73285714285714,3.943789094521117,0.2113477167849093
2019,Climatology,2019-07-07,46.77428571428572,4.103957172870507,0.2113477167849093
2019,Climatology,2019-07-14,62.93857142857143,3.814374650600652,0.2113477167849093
2019,Climatology,2019-07-21,42.65,3.7679408789883073,0.2113477167849093
2019,Climatology,2019-07-28,42.49,3.5642125617792497,0.2113477167849093
2019,Climatology,2019-08-04,34.18857142857143,3.734629977026136,0.2113477167849093
2019,Climatology,2019-08-11,28.487142857142857,3.7846772651935656,0.2113477167849093
2019,Climatology,2019-08-18,20.78142857142857,3.803905852176592,0.2113477167849093
2019,Climatology,2019-08-25,45.11857142857143,3.737547315093024,0.2113477167849093
2019,Climatology,2019-09-01,39.64142857142857,3.699850875327819,0.2113477167849093
2019,Climatology,2019-09-08,46.80571428571428,4.002236043411254,0.2113477167849093
2019,Climatology,2019-09-15,50.56857142857143,4.003960043042373,0.2113477167849093
2019,Climatology,2019-09-22,39.85142857142857,4.081388300513565,0.2113477167849093
2019,Climatology,2019-09-29,25.55,4.243511759511004,0.2113477167849093
2019,Climatology,2019-10-06,43.25571428571429,4.51798167057987,0.2113477167849093
2019,Climatology,2019-10-13,87.52285714285713,4.784254654282071,0.2113477167849093
2019,Climatology,2019-10-20,111.85142857142856,4.98998990668643,0.2113477167849093
2019,Climatology,2019-10-27,140.25571428571428,5.243295453681435,0.2113477167849093
2019,Climatology,2019-11-03,353.36857142857144,5.442251227757787,0.2113477167849093
2019,Climatology,2019-11-10,176.22285714285712,5.739720525302815,0.2113477167849093
2019,Climatology,2019-11-17,297.9271428571428,5.386107052776994,0.2113477167849093
2019,Climatology,2019-11-24,152.52142857142854,5.262891227519384,0.2113477167849093
2019,Climatology,2019-12-01,86.82571428571428,5.314463696059258,0.2113477167849093
2019,Climatology,2019-12-08,204.55428571428573,5.333576262155319,0.2113477167849093
2019,Climatology,2019-12-15,184.0914285714286,5.1796456826531285,0.2113477167849093
2019,Climatology,2019-12-22,185.57857142857145,5.296927489603438,0.2113477167849093
2019,Climatology,2019-12-29,234.32857142857145,5.451263182359057,0.2113477167849093
2019,Climatology + AR(1),2019-01-06,282.41142857142853,5.510923945669052,0.1966460675592165
2019,Climatology + AR(1),2019-01-13,215.72,5.295796880243033,0.2094087661098057
2019,Climatology + AR(1),2019-01-20,239.19571428571427,5.409941865308989,0.211060536080215
2019,Climatology + AR(1),2019-01-27,116.32714285714285,5.185891286824776,0.2112809184320206
2019,Climatology + AR(1),2019-02-03,166.56714285714287,5.069704400468246,0.211310435728756
2019,Climatology + AR(1),2019-02-10,134.56428571428572,5.006110880952198,0.2113143912056056
2019,Climatology + AR(1),2019-02-17,152.75857142857143,4.894968729646668,0.2113149212971806
2019,Climatology + AR(1),2019-02-24,90.08714285714288,5.1223506844439886,0.2113149923378342
2019,Climatology + AR(1),2019-03-03,80.32000000000001,4.793094261265444,0.2113150018584169
2019,Climatology + AR(1),2019-03-10,86.03,4.489649755239424,0.2113150031343273
2019,Climatology + AR(1),2019-03-17,82.42142857142858,4.524433717171044,0.2113150033053197
2019,Climatology + AR(1),2019-03-24,79.07571428571428,4.5359854628595215,0.2113150033282354
2019,Climatology + AR(1),2019-03-31,87.09142857142857,4.636562805692268,0.2113150033313065
2019,Climatology + AR(1),2019-04-07,104.12285714285711,4.520754236312061,0.2113150033317181
2019,Climatology + AR(1),2019-04-14,72.85857142857142,4.6202451312068975,0.2113150033317732
2019,Climatology + AR(1),2019-04-21,61.77,4.665894185964571,0.2113150033317806
2019,Climatology + AR(1),2019-04-28,88.33,4.723595985559837,0.2113150033317816
2019,Climatology + AR(1),2019-05-05,85.77428571428571,4.553601591478022,0.2113150033317818
2019,Climatology + AR(1),2019-05-12,129.04857142857142,4.72099155307504,0.2113150033317818
2019,Climatology + AR(1),2019-05-19,86.87,4.593789755030739,0.2113150033317818
2019,Climatology + AR(1),2019-05-26,67.29142857142857,4.509783017511633,0.2113150033317818
2019,Climatology + AR(1),2019-06-02,78.25999999999999,4.53114026885309,0.2113150033317818
2019,Climatology + AR(1),2019-06-09,70.20857142857143,4.174672761741304,0.2113150033317818
2019,Climatology + AR(1),2019-06-16,69.01285714285714,4.517429620749363,0.2113150033317818
2019,Climatology + AR(1),2019-06-23,53.53857142857142,4.319189257213532,0.2113150033317818
2019,Climatology + AR(1),2019-06-30,56.73285714285714,3.94378909452206,0.2113150033317818
2019,Climatology + AR(1),2019-07-07,46.77428571428572,4.103957172870852,0.2113150033317818
2019,Climatology + AR(1),2019-07-14,62.93857142857143,3.814374650600778,0.2113150033317818
2019,Climatology + AR(1),2019-07-21,42.65,3.7679408789883535,0.2113150033317818
2019,Climatology + AR(1),2019-07-28,42.49,3.5642125617792666,0.2113150033317818
2019,Climatology + AR(1),2019-08-04,34.18857142857143,3.7346299770261417,0.2113150033317818
2019,Climatology + AR(1),2019-08-11,28.487142857142857,3.784677265193568,0.2113150033317818
2019,Climatology + AR(1),2019-08-18,20.78142857142857,3.803905852176592,0.2113150033317818
2019,Climatology + AR(1),2019-08-25,45.11857142857143,3.737547315093024,0.2113150033317818
2019,Climatology + AR(1),2019-09-01,39.64142857142857,3.699850875327819,0.2113150033317818
2019,Climatology + AR(1),2019-09-08,46.80571428571428,4.002236043411254,0.2113150033317818
2019,Climatology + AR(1),2019-09-15,50.56857142857143,4.003960043042373,0.2113150033317818
2019,Climatology + AR(1),2019-09-22,39.85142857142857,4.081388300513565,0.2113150033317818
2019,Climatology + AR(1),2019-09-29,25.55,4.243511759511004,0.2113150033317818
2019,Climatology + AR(1),2019-10-06,43.25571428571429,4.51798167057987,0.2113150033317818
2019,Climatology + AR(1),2019-10-13,87.52285714285713,4.784254654282071,0.2113150033317818
2019,Climatology + AR(1),2019-10-20,111.85142857142856,4.98998990668643,0.2113150033317818
2019,Climatology + AR(1),2019-10-27,140.25571428571428,5.243295453681435,0.2113150033317818
2019,Climatology + AR(1),2019-11-03,353.36857142857144,5.442251227757787,0.2113150033317818
2019,Climatology + AR(1),2019-11-10,176.22285714285712,5.739720525302815,0.2113150033317818
2019,Climatology + AR(1),2019-11-17,297.9271428571428,5.386107052776994,0.2113150033317818
2019,Climatology + AR(1),2019-11-24,152.52142857142854,5.262891227519384,0.2113150033317818
2019,Climatology + AR(1),2019-12-01,86.82571428571428,5.314463696059258,0.2113150033317818
2019,Climatology + AR(1),2019-12-08,204.55428571428573,5.333576262155319,0.2113150033317818
2019,Climatology + AR(1),2019-12-15,184.0914285714286,5.1796456826531285,0.2113150033317818
2019,Climatology + AR(1),2019-12-22,185.57857142857145,5.296927489603438,0.2113150033317818
2019,Climatology + AR(1),2019-12-29,234.32857142857145,5.451263182359057,0.2113150033317818
2019,Linear regression,2019-01-06,282.41142857142853,5.248135386710887,0.2577996163165506
2019,Linear regression,2019-01-13,215.72,5.1927616928348135,0.2580615977456865
2019,Linear regression,2019-01-20,239.19571428571427,5.130989324119409,0.2583153974579683
2019,Linear regression,2019-01-27,116.32714285714285,5.063621825633228,0.2585416878104431
2019,Linear regression,2019-02-03,166.56714285714287,4.991581420813969,0.2587238780163203
2019,Linear regression,2019-02-10,134.56428571428572,4.916141654397239,0.258851119159787
2019,Linear regression,2019-02-17,152.75857142857143,4.839081173366551,0.2589200783167517
2019,Linear regression,2019-02-24,90.08714285714288,4.7627224402483535,0.258935066382136
2019,Linear regression,2019-03-03,80.32000000000001,4.689837572059311,0.2589066149796869
2019,Linear regression,2019-03-10,86.03,4.623424896420628,0.2588490307932614
2019,Linear regression,2019-03-17,82.42142857142858,4.566381197355902,0.258777663108682
2019,Linear regression,2019-03-24,79.07571428571428,4.5211129478006296,0.258706554700244
2019,Linear regression,2019-03-31,87.09142857142857,4.489142440314197,0.2586468719702168
2019,Linear regression,2019-04-07,104.12285714285711,4.4707697233467165,0.2586061687553836
2019,Linear regression,2019-04-14,72.85857142857142,4.4648477267698015,0.2585882798642379
2019,Linear regression,2019-04-21,61.77,4.468716155131888,0.2585935560769273
2019,Linear regression,2019-04-28,88.33,4.478320998826386,0.2586192370808446
2019,Linear regression,2019-05-05,85.77428571428571,4.488523175542946,0.2586599249563769
2019,Linear regression,2019-05-12,129.04857142857142,4.493574842780736,0.258708251313314
2019,Linear regression,2019-05-19,86.87,4.487718572906284,0.2587558434593981
2019,Linear regression,2019-05-26,67.29142857142857,4.465845969397142,0.258794581992941
2019,Linear regression,2019-06-02,78.25999999999999,4.4241409909773255,0.2588179708503938
2019,Linear regression,2019-06-09,70.20857142857143,4.360630913643079,0.2588223115994548
2019,Linear regression,2019-06-16,69.01285714285714,4.275575054739169,0.2588073651079099
2019,Linear regression,2019-06-23,53.53857142857142,4.17163745877381,0.2587763110641471
2019,Linear regression,2019-06-30,56.73285714285714,4.053812914546223,0.2587350253250204
2019,Linear regression,2019-07-07,46.77428571428572,3.9291032268364607,0.2586908931234928
2019,Linear regression,2019-07-14,62.93857142857143,3.8059693028470982,0.2586514779712588
2019,Linear regression,2019-07-21,42.65,3.6936108544449815,0.2586233379656489
2019,Linear regression,2019-07-28,42.49,3.6011461403243112,0.2586111554123909
2019,Linear regression,2019-08-04,34.18857142857143,3.536776619617303,0.2586172002491781
2019,Linear regression,2019-08-11,28.487142857142857,3.5070240901765124,0.2586410621689152
2019,Linear regression,2019-08-18,20.78142857142857,3.516120458950879,0.2586795969763418
2019,Linear regression,2019-08-25,45.11857142857143,3.5656135960676587,0.2587271129919673
2019,Linear regression,2019-09-01,39.64142857142857,3.65422875018444,0.2587759000977311
2019,Linear regression,2019-09-08,46.80571428571428,3.7779966286111417,0.258817201618816
2019,Linear regression,2019-09-15,50.56857142857143,3.93062987710699,0.2588426166439984
2019,Linear regression,2019-09-22,39.85142857142857,4.104102838990734,0.25884573471224
2019,Linear regression,2019-09-29,25.55,4.289368304897693,0.2588236366990606
2019,Linear regression,2019-10-06,43.25571428571429,4.477131929710262,0.2587778434410601
2019,Linear regression,2019-10-13,87.52285714285713,4.65860151190835,0.2587144093276346
2019,Linear regression,2019-10-20,111.85142857142856,4.826134628120982,0.2586431147953261
2019,Linear regression,2019-10-27,140.25571428571428,4.973723206344695,0.2585760084778494
2019,Linear regression,2019-11-03,353.36857142857144,5.097275445665899,0.2585257550063545
2019,Linear regression,2019-11-10,176.22285714285712,5.194681187377575,0.25850425832995
2019,Linear regression,2019-11-17,297.9271428571428,5.265673121400231,0.2585218380583105
2019,Linear regression,2019-11-24,152.52142857142854,5.311519775746597,0.2585869233001322
2019,Linear regression,2019-12-01,86.82571428571428,5.3346042019684505,0.258705946699303
2019,Linear regression,2019-12-08,204.55428571428573,5.337952529483664,0.2588830178769775
2019,Linear regression,2019-12-15,184.0914285714286,5.32477804635764,0.2591190977737567
2019,Linear regression,2019-12-22,185.57857142857145,5.298099263545793,0.2594107314039592
2019,Linear regression,2019-12-29,234.32857142857145,5.260475756122282,0.2597487715456292
2019,LSTM (small),2019-01-06,282.41142857142853,5.283736473389743,0.036574955664179
2019,LSTM (small),2019-01-13,215.72,5.067052278689198,0.0452543297995315
2019,LSTM (small),2019-01-20,239.19571428571427,5.133903219047138,0.0466960655915946
2019,LSTM (small),2019-01-27,116.32714285714285,5.106569142842768,0.051973484742204
2019,LSTM (small),2019-02-03,166.56714285714287,4.779049991802469,0.063917518969388
2019,LSTM (small),2019-02-10,134.56428571428572,4.87845067100849,0.063917518969388
2019,LSTM (small),2019-02-17,152.75857142857143,4.8868357615477445,0.0855326825674803
2019,LSTM (small),2019-02-24,90.08714285714288,5.543970298382714,0.0855326825674803
2019,LSTM (small),2019-03-03,80.32000000000001,5.191986044407257,0.1126095480014922
2019,LSTM (small),2019-03-10,86.03,4.586625782155444,0.1166081794295593
2019,LSTM (small),2019-03-17,82.42142857142858,4.393391527009602,0.1373757178695471
2019,LSTM (small),2019-03-24,79.07571428571428,4.471234834865944,0.1373757178695471
2019,LSTM (small),2019-03-31,87.09142857142857,4.500688150692372,0.2113477167849093
2019,LSTM (small),2019-04-07,104.12285714285711,4.463372319973377,0.2113477167849093
2019,LSTM (small),2019-04-14,72.85857142857142,4.470701751609756,0.2113477167849093
2019,LSTM (small),2019-04-21,61.77,4.32233598684925,0.2113477167849093
2019,LSTM (small),2019-04-28,88.33,4.481063051344473,0.2113477167849093
2019,LSTM (small),2019-05-05,85.77428571428571,4.515444453872088,0.2113477167849093
2019,LSTM (small),2019-05-12,129.04857142857142,4.709337864130725,0.2113477167849093
2019,LSTM (small),2019-05-19,86.87,4.438592915035501,0.2113477167849093
2019,LSTM (small),2019-05-26,67.29142857142857,4.449679263161253,0.2113477167849093
2019,LSTM (small),2019-06-02,78.25999999999999,4.476867152288111,0.2113477167849093
2019,LSTM (small),2019-06-09,70.20857142857143,4.327260762325925,0.2113477167849093
2019,LSTM (small),2019-06-16,69.01285714285714,4.4402075895354125,0.2113477167849093
2019,LSTM (small),2019-06-23,53.53857142857142,4.7663875083134855,0.2113477167849093
2019,LSTM (small),2019-06-30,56.73285714285714,3.9524680373338312,0.2113477167849093
2019,LSTM (small),2019-07-07,46.77428571428572,4.473908922500024,0.2113477167849093
2019,LSTM (small),2019-07-14,62.93857142857143,3.6821354178323737,0.2113477167849093
2019,LSTM (small),2019-07-21,42.65,4.233629656782532,0.2113477167849093
2019,LSTM (small),2019-07-28,42.49,3.312890722193636,0.2113477167849093
2019,LSTM (small),2019-08-04,34.18857142857143,4.031690315279593,0.2113477167849093
2019,LSTM (small),2019-08-11,28.487142857142857,3.747347395567904,0.2113477167849093
2019,LSTM (small),2019-08-18,20.78142857142857,4.483248611072649,0.2113477167849093
2019,LSTM (small),2019-08-25,45.11857142857143,3.99519297688672,0.2113477167849093
2019,LSTM (small),2019-09-01,39.64142857142857,4.096161126380875,0.2113477167849093
2019,LSTM (small),2019-09-08,46.80571428571428,4.345266141668448,0.2113477167849093
2019,LSTM (small),2019-09-15,50.56857142857143,4.46729448520157,0.2113477167849093
2019,LSTM (small),2019-09-22,39.85142857142857,4.198916273848896,0.2113477167849093
2019,LSTM (small),2019-09-29,25.55,4.735986742447923,0.2113477167849093
2019,LSTM (small),2019-10-06,43.25571428571429,4.852954330629252,0.2113477167849093
2019,LSTM (small),2019-10-13,87.52285714285713,5.2242305677585,0.2113477167849093
2019,LSTM (small),2019-10-20,111.85142857142856,5.427038559069914,0.2113477167849093
2019,LSTM (small),2019-10-27,140.25571428571428,5.654020499177846,0.2113477167849093
2019,LSTM (small),2019-11-03,353.36857142857144,5.855743246230904,0.2113477167849093
2019,LSTM (small),2019-11-10,176.22285714285712,6.153145828445564,0.2113477167849093
2019,LSTM (small),2019-11-17,297.9271428571428,5.795105763516303,0.2113477167849093
2019,LSTM (small),2019-11-24,152.52142857142854,5.697655786843772,0.2113477167849093
2019,LSTM (small),2019-12-01,86.82571428571428,5.737553475683049,0.2113477167849093
2019,LSTM (small),2019-12-08,204.55428571428573,5.7687526022046045,0.2113477167849093
2019,LSTM (small),2019-12-15,184.0914285714286,5.612709706502248,0.2113477167849093
2019,LSTM (small),2019-12-22,185.57857142857145,5.726589585885242,0.2113477167849093
2019,LSTM (small),2019-12-29,234.32857142857145,5.8853705150565645,0.2113477167849093
2019,Fourier+ARMA const,2019-01-06,282.41142857142853,5.435498750428995,0.236758306319178
2019,Fourier+ARMA const,2019-01-13,215.72,5.323698271130144,0.2500188981822158
2019,Fourier+ARMA const,2019-01-20,239.19571428571427,5.245943085217431,0.2515010327464724
2019,Fourier+ARMA const,2019-01-27,116.32714285714285,5.17558281243397,0.251671147469583
2019,Fourier+ARMA const,2019-02-03,166.56714285714287,5.104143333938914,0.2516907296431342
2019,Fourier+ARMA const,2019-02-10,134.56428571428572,5.029708107541408,0.2516929845299464
2019,Fourier+ARMA const,2019-02-17,152.75857142857143,4.953047188485732,0.2516932441900756
2019,Fourier+ARMA const,2019-02-24,90.08714285714288,4.876278660826466,0.2516932740912131
2019,Fourier+ARMA const,2019-03-03,80.32000000000001,4.802288711791574,0.2516932775344775
2019,Fourier+ARMA const,2019-03-10,86.03,4.734320418753351,0.2516932779309866
2019,Fourier+ARMA const,2019-03-17,82.42142857142858,4.675557682969519,0.2516932779766466
2019,Fourier+ARMA const,2019-03-24,79.07571428571428,4.628683255501423,0.2516932779819045
2019,Fourier+ARMA const,2019-03-31,87.09142857142857,4.595447721217465,0.25169327798251
2019,Fourier+ARMA const,2019-04-07,104.12285714285711,4.57630609950961,0.2516932779825798
2019,Fourier+ARMA const,2019-04-14,72.85857142857142,4.570179369312692,0.2516932779825878
2019,Fourier+ARMA const,2019-04-21,61.77,4.574386827964566,0.2516932779825887
2019,Fourier+ARMA const,2019-04-28,88.33,4.5847755652048585,0.2516932779825888
2019,Fourier+ARMA const,2019-05-05,85.77428571428571,4.596048756413663,0.2516932779825888
2019,Fourier+ARMA const,2019-05-12,129.04857142857142,4.602268376392855,0.2516932779825888
2019,Fourier+ARMA const,2019-05-19,86.87,4.597483804039893,0.2516932779825888
2019,Fourier+ARMA const,2019-05-26,67.29142857142857,4.576418873617119,0.2516932779825888
2019,Fourier+ARMA const,2019-06-02,78.25999999999999,4.535138839854813,0.2516932779825888
2019,Fourier+ARMA const,2019-06-09,70.20857142857143,4.471617105658398,0.2516932779825888
2019,Fourier+ARMA const,2019-06-16,69.01285714285714,4.386129871105685,0.2516932779825888
2019,Fourier+ARMA const,2019-06-23,53.53857142857142,4.281424301781102,0.2516932779825888
2019,Fourier+ARMA const,2019-06-30,56.73285714285714,4.162630414873699,0.2516932779825888
2019,Fourier+ARMA const,2019-07-07,46.77428571428572,4.036915742826421,0.2516932779825888
2019,Fourier+ARMA const,2019-07-14,62.93857142857143,3.91291148342414,0.2516932779825888
2019,Fourier+ARMA const,2019-07-21,42.65,3.799965669286036,0.2516932779825888
2019,Fourier+ARMA const,2019-07-28,42.49,3.707299590353836,0.2516932779825888
2019,Fourier+ARMA const,2019-08-04,34.18857142857143,3.6431557122135776,0.2516932779825888
2019,Fourier+ARMA const,2019-08-11,28.487142857142857,3.614027138851089,0.2516932779825888
2019,Fourier+ARMA const,2019-08-18,20.78142857142857,3.6240500072848736,0.2516932779825888
2019,Fourier+ARMA const,2019-08-25,45.11857142857143,3.674622094280804,0.2516932779825888
2019,Fourier+ARMA const,2019-09-01,39.64142857142857,3.764285540821586,0.2516932779825888
2019,Fourier+ARMA const,2019-09-08,46.80571428571428,3.888882022677084,0.2516932779825888
2019,Fourier+ARMA const,2019-09-15,50.56857142857143,4.0419584819500605,0.2516932779825888
2019,Fourier+ARMA const,2019-09-22,39.85142857142857,4.215374307625685,0.2516932779825888
2019,Fourier+ARMA const,2019-09-29,25.55,4.400039840050099,0.2516932779825888
2019,Fourier+ARMA const,2019-10-06,43.25571428571429,4.586703706270593,0.2516932779825888
2019,Fourier+ARMA const,2019-10-13,87.52285714285713,4.766704108170202,0.2516932779825888
2019,Fourier+ARMA const,2019-10-20,111.85142857142856,4.932606869860789,0.2516932779825888
2019,Fourier+ARMA const,2019-10-27,140.25571428571428,5.078669641590721,0.2516932779825888
2019,Fourier+ARMA const,2019-11-03,353.36857142857144,5.201094901393422,0.2516932779825888
2019,Fourier+ARMA const,2019-11-10,176.22285714285712,5.298061247201869,0.2516932779825888
2019,Fourier+ARMA const,2019-11-17,297.9271428571428,5.369549488708554,0.2516932779825888
2019,Fourier+ARMA const,2019-11-24,152.52142857142854,5.417003833580517,0.2516932779825888
2019,Fourier+ARMA const,2019-12-01,86.82571428571428,5.442886099831032,0.2516932779825888
2019,Fourier+ARMA const,2019-12-08,204.55428571428573,5.450190305373699,0.2516932779825888
2019,Fourier+ARMA const,2019-12-15,184.0914285714286,5.441985219597831,0.2516932779825888
2019,Fourier+ARMA const,2019-12-22,185.57857142857145,5.421043755764578,0.2516932779825888
2019,Fourier+ARMA const,2019-12-29,234.32857142857145,5.389601848162879,0.2516932779825888
2019,Fourier+ARMA linear,2019-01-06,282.41142857142853,5.394536658065437,0.2349655259319367
2019,Fourier+ARMA linear,2019-01-13,215.72,5.271024077113676,0.2462978348241954
2019,Fourier+ARMA linear,2019-01-20,239.19571428571427,5.186421932598065,0.2473891305420475
2019,Fourier+ARMA linear,2019-01-27,116.32714285714285,5.108833716318552,0.2474966735116049
2019,Fourier+ARMA linear,2019-02-03,166.56714285714287,5.029305824016259,0.2475072946544222
2019,Fourier+ARMA linear,2019-02-10,134.56428571428572,4.9465115466112834,0.2475083438438803
2019,Fourier+ARMA linear,2019-02-17,152.75857142857143,4.861957806420007,0.247508447488274
2019,Fourier+ARMA linear,2019-02-24,90.08714285714288,4.7784056241568,0.247508457726828
2019,Fourier+ARMA linear,2019-03-03,80.32000000000001,4.6992084135910055,0.2475084587382479
2019,Fourier+ARMA linear,2019-03-10,86.03,4.627862786183997,0.2475084588381615
2019,Fourier+ARMA linear,2019-03-17,82.42142857142858,4.567579581477075,0.2475084588480315
2019,Fourier+ARMA linear,2019-03-24,79.07571428571428,4.520853460357086,0.2475084588490065
2019,Fourier+ARMA linear,2019-03-31,87.09142857142857,4.489067253817633,0.2475084588491028
2019,Fourier+ARMA linear,2019-04-07,104.12285714285711,4.472183791213362,0.2475084588491124
2019,Fourier+ARMA linear,2019-04-14,72.85857142857142,4.46857563620193,0.2475084588491133
2019,Fourier+ARMA linear,2019-04-21,61.77,4.475029932552857,0.2475084588491134
2019,Fourier+ARMA linear,2019-04-28,88.33,4.486945398958492,0.2475084588491134
2019,Fourier+ARMA linear,2019-05-05,85.77428571428571,4.498714674035576,0.2475084588491134
2019,Fourier+ARMA linear,2019-05-12,129.04857142857142,4.504260972458795,0.2475084588491134
2019,Fourier+ARMA linear,2019-05-19,86.87,4.497676597349663,0.2475084588491134
2019,Fourier+ARMA linear,2019-05-26,67.29142857142857,4.473895139948785,0.2475084588491134
2019,Fourier+ARMA linear,2019-06-02,78.25999999999999,4.429321372406659,0.2475084588491134
2019,Fourier+ARMA linear,2019-06-09,70.20857142857143,4.3623441204818185,0.2475084588491134
2019,Fourier+ARMA linear,2019-06-16,69.01285714285714,4.273667871881184,0.2475084588491134
2019,Fourier+ARMA linear,2019-06-23,53.53857142857142,4.166417455613836,0.2475084588491134
2019,Fourier+ARMA linear,2019-06-30,56.73285714285714,4.04599470512305,0.2475084588491134
2019,Fourier+ARMA linear,2019-07-07,46.77428571428572,3.9196937008374313,0.2475084588491134
2019,Fourier+ARMA linear,2019-07-14,62.93857142857143,3.796108661616403,0.2475084588491134
2019,Fourier+ARMA linear,2019-07-21,42.65,3.684392495386571,0.2475084588491134
2019,Fourier+ARMA linear,2019-07-28,42.49,3.593441509757154,0.2475084588491134
2019,Fourier+ARMA linear,2019-08-04,34.18857142857143,3.531090679358824,0.2475084588491134
2019,Fourier+ARMA linear,2019-08-11,28.487142857142857,3.503403067057448,0.2475084588491134
2019,Fourier+ARMA linear,2019-08-18,20.78142857142857,3.514126582474095,0.2475084588491134
2019,Fourier+ARMA linear,2019-08-25,45.11857142857143,3.5643724878441856,0.2475084588491134
2019,Fourier+ARMA linear,2019-09-01,39.64142857142857,3.652545198744235,0.2475084588491134
2019,Fourier+ARMA linear,2019-09-08,46.80571428571428,3.774524977868466,0.2475084588491134
2019,Fourier+ARMA linear,2019-09-15,50.56857142857143,3.924077442061194,0.2475084588491134
2019,Fourier+ARMA linear,2019-09-22,39.85142857142857,4.093439691134932,0.2475084588491134
2019,Fourier+ARMA linear,2019-09-29,25.55,4.274015143856333,0.2475084588491134
2019,Fourier+ARMA linear,2019-10-06,43.25571428571429,4.457099833713211,0.2475084588491134
2019,Fourier+ARMA linear,2019-10-13,87.52285714285713,4.6345629141486615,0.2475084588491134
2019,Fourier+ARMA linear,2019-10-20,111.85142857142856,4.799413220889409,0.2475084588491134
2019,Fourier+ARMA linear,2019-10-27,140.25571428571428,4.946200583122248,0.2475084588491134
2019,Fourier+ARMA linear,2019-11-03,353.36857142857144,5.071222870415284,0.2475084588491134
2019,Fourier+ARMA linear,2019-11-10,176.22285714285712,5.172534576002429,0.2475084588491134
2019,Fourier+ARMA linear,2019-11-17,297.9271428571428,5.249776881310286,0.2475084588491134
2019,Fourier+ARMA linear,2019-11-24,152.52142857142854,5.303869588433425,0.2475084588491134
2019,Fourier+ARMA linear,2019-12-01,86.82571428571428,5.336619555457676,0.2475084588491134
2019,Fourier+ARMA linear,2019-12-08,204.55428571428573,5.35030668777034,0.2475084588491134
2019,Fourier+ARMA linear,2019-12-15,184.0914285714286,5.347306544909269,0.2475084588491134
2019,Fourier+ARMA linear,2019-12-22,185.57857142857145,5.329798750616988,0.2475084588491134
2019,Fourier+ARMA linear,2019-12-29,234.32857142857145,5.299594207781862,0.2475084588491134
2019,Fourier+ARMA (selected),2019-01-06,282.41142857142853,5.359167517717401,0.225792836230598
2019,Fourier+ARMA (selected),2019-01-13,215.72,5.3425637362854745,0.2317345506574779
2019,Fourier+ARMA (selected),2019-01-20,239.19571428571427,5.334748210342097,0.2334591132640864
2019,Fourier+ARMA (selected),2019-01-27,116.32714285714285,5.287873794921418,0.2348000534517417
2019,Fourier+ARMA (selected),2019-02-03,166.56714285714287,5.196251370489725,0.2360862677360358
2019,Fourier+ARMA (selected),2019-02-10,134.56428571428572,5.070159292947246,0.2373591516116836
2019,Fourier+ARMA (selected),2019-02-17,152.75857142857143,4.92862619054107,0.2386243792252246
2019,Fourier+ARMA (selected),2019-02-24,90.08714285714288,4.793178187950813,0.2398828154869778
2019,Fourier+ARMA (selected),2019-03-03,80.32000000000001,4.681845026253101,0.241134668174005
2019,Fourier+ARMA (selected),2019-03-10,86.03,4.604907355651257,0.242380053136435
2019,Fourier+ARMA (selected),2019-03-17,82.42142857142858,4.563473319563104,0.2436190714521502
2019,Fourier+ARMA (selected),2019-03-24,79.07571428571428,4.550979872991782,0.2448518200298667
2019,Fourier+ARMA (selected),2019-03-31,87.09142857142857,4.556731105959433,0.2460783931309656
2019,Fourier+ARMA (selected),2019-04-07,104.12285714285711,4.569983738053471,0.2472988826491552
2019,Fourier+ARMA (selected),2019-04-14,72.85857142857142,4.583061205893211,0.2485133782174946
2019,Fourier+ARMA (selected),2019-04-21,61.77,4.592498745884663,0.2497219672888536
2019,Fourier+ARMA (selected),2019-04-28,88.33,4.598072459630495,0.2509247352098993
2019,Fourier+ARMA (selected),2019-05-05,85.77428571428571,4.600414886015543,0.2521217652914971
2019,Fourier+ARMA (selected),2019-05-12,129.04857142857142,4.59844994455685,0.2533131388760626
2019,Fourier+ARMA (selected),2019-05-19,86.87,4.587901361720041,0.2544989354020681
2019,Fourier+ARMA (selected),2019-05-26,67.29142857142857,4.561646189543607,0.2556792324658549
2019,Fourier+ARMA (selected),2019-06-02,78.25999999999999,4.511894070556588,0.2568541058808897
2019,Fourier+ARMA (selected),2019-06-09,70.20857142857143,4.43338388012958,0.2580236297345922
2019,Fourier+ARMA (selected),2019-06-16,69.01285714285714,4.326311111882888,0.2591878764428548
2019,Fourier+ARMA (selected),2019-06-23,53.53857142857142,4.197723451595027,0.2603469168023681
2019,Fourier+ARMA (selected),2019-06-30,56.73285714285714,4.06065035267586,0.2615008200408593
2019,Fourier+ARMA (selected),2019-07-07,46.77428571428572,3.9310748228235792,0.262649653865343
2019,Fourier+ARMA (selected),2019-07-14,62.93857142857143,3.823698168809036,0.2637934845084828
2019,Fourier+ARMA (selected),2019-07-21,42.65,3.747968742791665,0.264932376773149
2019,Fourier+ARMA (selected),2019-07-28,42.49,3.7058329598172026,0.2660663940752616
2019,Fourier+ARMA (selected),2019-08-04,34.18857142857143,3.69210287053907,0.2671955984849957
2019,Fourier+ARMA (selected),2019-08-11,28.487142857142857,3.697405946037008,0.2683200507664265
2019,Fourier+ARMA (selected),2019-08-18,20.78142857142857,3.71271808645517,0.2694398104156851
2019,Fourier+ARMA (selected),2019-08-25,45.11857142857143,3.733834867238936,0.2705549356976933
2019,Fourier+ARMA (selected),2019-09-01,39.64142857142857,3.764060923087528,0.271665483681541
2019,Fourier+ARMA (selected),2019-09-08,46.80571428571428,3.8139480783544375,0.272771510274567
2019,Fourier+ARMA (selected),2019-09-15,50.56857142857143,3.89792054920534,0.2738730702552021
2019,Fourier+ARMA (selected),2019-09-22,39.85142857142857,4.028750663791451,0.2749702173046265
2019,Fourier+ARMA (selected),2019-09-29,25.55,4.211695974060683,0.2760630040372961
2019,Fourier+ARMA (selected),2019-10-06,43.25571428571429,4.4403658810801065,0.277151482030385
2019,Fourier+ARMA (selected),2019-10-13,87.52285714285713,4.695935709332877,0.2782357018521912
2019,Fourier+ARMA (selected),2019-10-20,111.85142857142856,4.950293481386876,0.2793157130895504
2019,Fourier+ARMA (selected),2019-10-27,140.25571428571428,5.172420115623046,0.2803915643742991
2019,Fourier+ARMA (selected),2019-11-03,353.36857142857144,5.336194986390914,0.2814633034088269
2019,Fourier+ARMA (selected),2019-11-10,176.22285714285712,5.427265719317481,0.2825309769907576
2019,Fourier+ARMA (selected),2019-11-17,297.9271428571428,5.446825230678621,0.2835946310367928
2019,Fourier+ARMA (selected),2019-11-24,152.52142857142854,5.411051511447342,0.2846543106057543
2019,Fourier+ARMA (selected),2019-12-01,86.82571428571428,5.346299909604915,0.2857100599208573
2019,Fourier+ARMA (selected),2019-12-08,204.55428571428573,5.281462900513041,0.2867619223912452
2019,Fourier+ARMA (selected),2019-12-15,184.0914285714286,5.239796805227767,0.2878099406328162
2019,Fourier+ARMA (selected),2019-12-22,185.57857142857145,5.2326702314685685,0.2888541564883701
2019,Fourier+ARMA (selected),2019-12-29,234.32857142857145,5.257066516220405,0.2898946110471018
2019,SARIMA D=1,2019-01-06,282.41142857142853,5.5582910517762345,0.2377989172048173
2019,SARIMA D=1,2019-01-13,215.72,5.353180049688744,0.2449702118849202
2019,SARIMA D=1,2019-01-20,239.19571428571427,5.439165413485971,0.2504237540372667
2019,SARIMA D=1,2019-01-27,116.32714285714285,5.267319731133135,0.2545983198770531
2019,SARIMA D=1,2019-02-03,166.56714285714287,5.113778763908832,0.257809011336928
2019,SARIMA D=1,2019-02-10,134.56428571428572,5.082524087020149,0.2602869799220534
2019,SARIMA D=1,2019-02-17,152.75857142857143,4.936992952183282,0.2622044069848501
2019,SARIMA D=1,2019-02-24,90.08714285714288,5.123496101396255,0.2636909938626456
2019,SARIMA D=1,2019-03-03,80.32000000000001,4.720043542541436,0.264845260443274
2019,SARIMA D=1,2019-03-10,86.03,4.534420402055136,0.2657425118737902
2019,SARIMA D=1,2019-03-17,82.42142857142858,4.503654560047959,0.266440582849363
2019,SARIMA D=1,2019-03-24,79.07571428571428,4.638658785685941,0.2669840519693005
2019,SARIMA D=1,2019-03-31,87.09142857142857,4.592442562489839,0.2674073755151367
2019,SARIMA D=1,2019-04-07,104.12285714285711,4.607576772907334,0.2677372428461304
2019,SARIMA D=1,2019-04-14,72.85857142857142,4.641906780588195,0.2679943611266556
2019,SARIMA D=1,2019-04-21,61.77,4.72336708791863,0.2681948163310221
2019,SARIMA D=1,2019-04-28,88.33,4.650494289225504,0.2683511165970006
2019,SARIMA D=1,2019-05-05,85.77428571428571,4.675853946280457,0.2684729949488824
2019,SARIMA D=1,2019-05-12,129.04857142857142,4.658719313645793,0.2685680288481117
2019,SARIMA D=1,2019-05-19,86.87,4.554267315571149,0.2686421194560793
2019,SARIMA D=1,2019-05-26,67.29142857142857,4.613069423096386,0.268699863013705
2019,SARIMA D=1,2019-06-02,78.25999999999999,4.417773572031268,0.2687448389726435
2019,SARIMA D=1,2019-06-09,70.20857142857143,4.277398176834773,0.2687798337042349
2019,SARIMA D=1,2019-06-16,69.01285714285714,4.543762891856563,0.2688070142300942
2019,SARIMA D=1,2019-06-23,53.53857142857142,4.259427171069556,0.2688280630869232
2019,SARIMA D=1,2019-06-30,56.73285714285714,3.920232859298425,0.2688442828890914
2019,SARIMA D=1,2019-07-07,46.77428571428572,4.012886535964297,0.2688566771904926
2019,SARIMA D=1,2019-07-14,62.93857142857143,3.8690172350351264,0.2688660127281223
2019,SARIMA D=1,2019-07-21,42.65,3.6619515165655914,0.2688728669460859
2019,SARIMA D=1,2019-07-28,42.49,3.5101299240768475,0.2688776637688536
2019,SARIMA D=1,2019-08-04,34.18857142857143,3.8891423636592615,0.2688806998539893
2019,SARIMA D=1,2019-08-11,28.487142857142857,3.796126685252926,0.2688821629315258
2019,SARIMA D=1,2019-08-18,20.78142857142857,3.734809299374593,0.268882143534277
2019,SARIMA D=1,2019-08-25,45.11857142857143,3.783894463849687,0.2688806404356409
2019,SARIMA D=1,2019-09-01,39.64142857142857,3.77268911354627,0.268877560683512
2019,SARIMA D=1,2019-09-08,46.80571428571428,3.959774828511,0.2688727138200897
2019,SARIMA D=1,2019-09-15,50.56857142857143,4.058891610046151,0.268865800092494
2019,SARIMA D=1,2019-09-22,39.85142857142857,3.996719140070141,0.2688563918945918
2019,SARIMA D=1,2019-09-29,25.55,4.328294081320749,0.2688439072860292
2019,SARIMA D=1,2019-10-06,43.25571428571429,4.629224078723294,0.268827573939993
2019,SARIMA D=1,2019-10-13,87.52285714285713,4.705838848977825,0.2688063812719759
2019,SARIMA D=1,2019-10-20,111.85142857142856,5.072393179967007,0.268779017758854
2019,SARIMA D=1,2019-10-27,140.25571428571428,5.2213538696579125,0.2687437894947965
2019,SARIMA D=1,2019-11-03,353.36857142857144,5.542792694826699,0.2686985150284591
2019,SARIMA D=1,2019-11-10,176.22285714285712,5.7257727919936,0.268640389428541
2019,SARIMA D=1,2019-11-17,297.9271428571428,5.354955857650245,0.2685658094690273
2019,SARIMA D=1,2019-11-24,152.52142857142854,5.2172732652760265,0.2684701484741275
2019,SARIMA D=1,2019-12-01,86.82571428571428,5.313890334321316,0.2683474661697123
2019,SARIMA D=1,2019-12-08,204.55428571428573,5.310182598013602,0.2681901347983237
2019,SARIMA D=1,2019-12-15,184.0914285714286,5.024011852401532,0.267988356726773
2019,SARIMA D=1,2019-12-22,185.57857142857145,5.351866359658624,0.2677295404006357
2019,SARIMA D=1,2019-12-29,234.32857142857145,5.455051243348066,0.2634778802620696
2019,SARIMA D=0,2019-01-06,282.41142857142853,5.542723827335813,0.2695686241324401
2019,SARIMA D=0,2019-01-13,215.72,5.399501377377101,0.3083914853657932
2019,SARIMA D=0,2019-01-20,239.19571428571427,5.376980315698741,0.33787945257139
2019,SARIMA D=0,2019-01-27,116.32714285714285,5.235809390409119,0.3610378099436326
2019,SARIMA D=0,2019-02-03,166.56714285714287,5.17250246463754,0.3795988526310755
2019,SARIMA D=0,2019-02-10,134.56428571428572,5.218754895187046,0.3946782919322821
2019,SARIMA D=0,2019-02-17,152.75857142857143,5.01034251951299,0.4070471617442974
2019,SARIMA D=0,2019-02-24,90.08714285714288,5.138045952402869,0.417264512370813
2019,SARIMA D=0,2019-03-03,80.32000000000001,4.963305997343621,0.4257498442695777
2019,SARIMA D=0,2019-03-10,86.03,4.912018521898382,0.4328260293209671
2019,SARIMA D=0,2019-03-17,82.42142857142858,4.910571206387005,0.4387463937265226
2019,SARIMA D=0,2019-03-24,79.07571428571428,4.848741893376315,0.4437126760596801
2019,SARIMA D=0,2019-03-31,87.09142857142857,4.85730064850072,0.4478874208063838
2019,SARIMA D=0,2019-04-07,104.12285714285711,4.82853713247821,0.4514028164677418
2019,SARIMA D=0,2019-04-14,72.85857142857142,4.730341079352972,0.4543671715352318
2019,SARIMA D=0,2019-04-21,61.77,4.791179205603613,0.4568697683567811
2019,SARIMA D=0,2019-04-28,88.33,4.821100716557263,0.4589845710525543
2019,SARIMA D=0,2019-05-05,85.77428571428571,4.659945559479476,0.4607731038133777
2019,SARIMA D=0,2019-05-12,129.04857142857142,4.783035674767351,0.4622867157033389
2019,SARIMA D=0,2019-05-19,86.87,4.7100883038419,0.4635683833214015
2019,SARIMA D=0,2019-05-26,67.29142857142857,4.760847098525033,0.4646541596774526
2019,SARIMA D=0,2019-06-02,78.25999999999999,4.675952752797115,0.4655743483950666
2019,SARIMA D=0,2019-06-09,70.20857142857143,4.5914790641833205,0.4663544620291547
2019,SARIMA D=0,2019-06-16,69.01285714285714,4.896834420470999,0.4670160088801425
2019,SARIMA D=0,2019-06-23,53.53857142857142,4.596212701394455,0.4675771422890115
2019,SARIMA D=0,2019-06-30,56.73285714285714,4.384062638325,0.4680531987690118
2019,SARIMA D=0,2019-07-07,46.77428571428572,4.483086673328523,0.4684571456474065
2019,SARIMA D=0,2019-07-14,62.93857142857143,4.414120871939064,0.4687999545985117
2019,SARIMA D=0,2019-07-21,42.65,4.348454584805195,0.4690909141657083
2019,SARIMA D=0,2019-07-28,42.49,4.321216323116991,0.469337891828502
2019,SARIMA D=0,2019-08-04,34.18857142857143,4.515780825091848,0.4695475541823094
2019,SARIMA D=0,2019-08-11,28.487142857142857,4.357911939106075,0.4697255522278638
2019,SARIMA D=0,2019-08-18,20.78142857142857,4.351516703187603,0.4698766775152974
2019,SARIMA D=0,2019-08-25,45.11857142857143,4.276152591214378,0.4700049938823877
2019,SARIMA D=0,2019-09-01,39.64142857142857,4.336925884082191,0.4701139487129451
2019,SARIMA D=0,2019-09-08,46.80571428571428,4.371825772401636,0.4702064669790351
2019,SARIMA D=0,2019-09-15,50.56857142857143,4.285147045589338,0.4702850307885068
2019,SARIMA D=0,2019-09-22,39.85142857142857,4.425452387199024,0.4703517467131959
2019,SARIMA D=0,2019-09-29,25.55,4.4807039647287725,0.4704084028045325
2019,SARIMA D=0,2019-10-06,43.25571428571429,4.614430596968799,0.470456516897515
2019,SARIMA D=0,2019-10-13,87.52285714285713,4.667646659403814,0.4704973775495311
2019,SARIMA D=0,2019-10-20,111.85142857142856,4.801885403726144,0.4705320787481203
2019,SARIMA D=0,2019-10-27,140.25571428571428,4.872639023889728,0.4705615493440602
2019,SARIMA D=0,2019-11-03,353.36857142857144,4.933258469594273,0.4705865780171451
2019,SARIMA D=0,2019-11-10,176.22285714285712,5.054187822888111,0.4706078344568485
2019,SARIMA D=0,2019-11-17,297.9271428571428,4.872857040140084,0.4706258873347272
2019,SARIMA D=0,2019-11-24,152.52142857142854,4.862719598659045,0.4706412195566813
2019,SARIMA D=0,2019-12-01,86.82571428571428,4.8984660576274415,0.4706542412083211
2019,SARIMA D=0,2019-12-08,204.55428571428573,4.9261126697227935,0.4706653005434768
2019,SARIMA D=0,2019-12-15,184.0914285714286,4.87443069272918,0.4706746933124628
2019,SARIMA D=0,2019-12-22,185.57857142857145,5.019228817348899,0.4706826706815242
2019,SARIMA D=0,2019-12-29,234.32857142857145,5.053004176970072,0.4706894459566538
```

## fc_oneweek_forecasts.csv (728 rows; one-step forecasts, mu on the log scale)
```
year,model,date,actual,mu
2018,Persistence,2018-01-07,247.29857142857145,5.529355388650604
2018,Persistence,2018-01-14,188.26,5.510596397836895
2018,Persistence,2018-01-21,197.46,5.237823986119074
2018,Persistence,2018-01-28,148.48857142857145,5.285536032183304
2018,Persistence,2018-02-04,137.04714285714286,5.000507995204216
2018,Persistence,2018-02-11,169.39,4.92032497508269
2018,Persistence,2018-02-18,103.70857142857145,5.1322037485982905
2018,Persistence,2018-02-25,158.08285714285714,4.641584767832887
2018,Persistence,2018-03-04,104.86,5.063119307867456
2018,Persistence,2018-03-11,96.94857142857144,4.652626127144386
2018,Persistence,2018-03-18,102.21428571428572,4.574180646444166
2018,Persistence,2018-03-25,90.97,4.627071449941193
2018,Persistence,2018-04-01,97.72857142857144,4.510529781833971
2018,Persistence,2018-04-08,94.45285714285714,4.582193956711639
2018,Persistence,2018-04-15,75.25,4.548100843811397
2018,Persistence,2018-04-22,92.28,4.3208159036289855
2018,Persistence,2018-04-29,103.68999999999998,4.524827433305553
2018,Persistence,2018-05-06,68.93714285714286,4.6414056785701865
2018,Persistence,2018-05-13,99.39285714285714,4.233195116324223
2018,Persistence,2018-05-20,83.68285714285715,4.599080251350687
2018,Persistence,2018-05-27,98.57714285714285,4.427034143410322
2018,Persistence,2018-06-03,80.00142857142858,4.59083941787023
2018,Persistence,2018-06-10,64.88285714285715,4.382044491657302
2018,Persistence,2018-06-17,152.4042857142857,4.17258344618121
2018,Persistence,2018-06-24,68.25857142857143,5.026536764341959
2018,Persistence,2018-07-01,38.87571428571429,4.223303014876486
2018,Persistence,2018-07-08,51.74428571428571,3.660369744239649
2018,Persistence,2018-07-15,43.470000000000006,3.946314005068647
2018,Persistence,2018-07-22,36.80857142857143,3.772071045000701
2018,Persistence,2018-07-29,34.582857142857144,3.6057307373080656
2018,Persistence,2018-08-05,59.50428571428571,3.5433581009847326
2018,Persistence,2018-08-12,39.05428571428571,4.086048338769158
2018,Persistence,2018-08-19,38.74142857142857,3.6649526196691937
2018,Persistence,2018-08-26,31.807142857142857,3.6569095331747534
2018,Persistence,2018-09-02,37.85428571428572,3.459690882712398
2018,Persistence,2018-09-09,41.95,3.633744202384664
2018,Persistence,2018-09-16,33.33,3.736478432913216
2018,Persistence,2018-09-23,49.20857142857143,3.506457892319648
2018,Persistence,2018-09-30,57.55857142857143,3.8960678243522873
2018,Persistence,2018-10-07,83.38714285714286,4.05280306288858
2018,Persistence,2018-10-14,96.91142857142856,4.423494135096081
2018,Persistence,2018-10-21,140.48285714285714,4.573797453855727
2018,Persistence,2018-10-28,171.1542857142857,4.945085468111484
2018,Persistence,2018-11-04,202.76142857142847,5.142565405353804
2018,Persistence,2018-11-11,283.1485714285714,5.312030059206812
2018,Persistence,2018-11-18,173.0885714285714,5.645971747265686
2018,Persistence,2018-11-25,168.86714285714285,5.15380343705958
2018,Persistence,2018-12-02,186.70857142857145,5.129112268815404
2018,Persistence,2018-12-09,201.8728571428572,5.22954895966294
2018,Persistence,2018-12-16,175.70142857142858,5.30763807914836
2018,Persistence,2018-12-23,261.5357142857143,5.168786125902334
2018,Persistence,2018-12-30,287.3928571428572,5.566570848885866
2018,Climatology,2018-01-07,247.29857142857145,5.408731798097988
2018,Climatology,2018-01-14,188.26,5.277670506466927
2018,Climatology,2018-01-21,197.46,5.437700460879099
2018,Climatology,2018-01-28,148.48857142857145,5.242666727981997
2018,Climatology,2018-02-04,137.04714285714286,5.117660180775535
2018,Climatology,2018-02-11,169.39,4.963407300169094
2018,Climatology,2018-02-18,103.70857142857145,4.979183814406805
2018,Climatology,2018-02-25,158.08285714285714,5.142004334134754
2018,Climatology,2018-03-04,104.86,4.839883973095223
2018,Climatology,2018-03-11,96.94857142857144,4.461460710966682
2018,Climatology,2018-03-18,102.21428571428572,4.490216717113987
2018,Climatology,2018-03-25,90.97,4.544469070882633
2018,Climatology,2018-04-01,97.72857142857144,4.654685162671122
2018,Climatology,2018-04-08,94.45285714285714,4.511638483508993
2018,Climatology,2018-04-15,75.25,4.720054794304081
2018,Climatology,2018-04-22,92.28,4.712916407773464
2018,Climatology,2018-04-29,103.68999999999998,4.750992743911659
2018,Climatology,2018-05-06,68.93714285714286,4.660403745965778
2018,Climatology,2018-05-13,99.39285714285714,4.761628652223261
2018,Climatology,2018-05-20,83.68285714285715,4.649374958381972
2018,Climatology,2018-05-27,98.57714285714285,4.482764217200919
2018,Climatology,2018-06-03,80.00142857142858,4.580838861181697
2018,Climatology,2018-06-10,64.88285714285715,4.175369200235714
2018,Climatology,2018-06-17,152.4042857142857,4.347727239542452
2018,Climatology,2018-06-24,68.25857142857143,4.351151337989115
2018,Climatology,2018-07-01,38.87571428571429,4.038262211281606
2018,Climatology,2018-07-08,51.74428571428571,4.156504895471128
2018,Climatology,2018-07-15,43.470000000000006,3.8284758524673017
2018,Climatology,2018-07-22,36.80857142857143,3.822010926215055
2018,Climatology,2018-07-29,34.582857142857144,3.5711640487107554
2018,Climatology,2018-08-05,59.50428571428571,3.617490523111794
2018,Climatology,2018-08-12,39.05428571428571,3.824585480368356
2018,Climatology,2018-08-19,38.74142857142857,3.852904625177204
2018,Climatology,2018-08-26,31.807142857142857,3.830166125886565
2018,Climatology,2018-09-02,37.85428571428572,3.7218864329755377
2018,Climatology,2018-09-09,41.95,4.090821913577266
2018,Climatology,2018-09-16,33.33,4.169794093283282
2018,Climatology,2018-09-23,49.20857142857143,4.143161792567324
2018,Climatology,2018-09-30,57.55857142857143,4.307081325051812
2018,Climatology,2018-10-07,83.38714285714286,4.549477515741132
2018,Climatology,2018-10-14,96.91142857142856,4.854407054424185
2018,Climatology,2018-10-21,140.48285714285714,5.00495805287808
2018,Climatology,2018-10-28,171.1542857142857,5.276872136457311
2018,Climatology,2018-11-04,202.76142857142847,5.4856582839414445
2018,Climatology,2018-11-11,283.1485714285714,5.770970117981858
2018,Climatology,2018-11-18,173.0885714285714,5.463541591349466
2018,Climatology,2018-11-25,168.86714285714285,5.307484213754044
2018,Climatology,2018-12-02,186.70857142857145,5.342768608191364
2018,Climatology,2018-12-09,201.8728571428572,5.342222323157638
2018,Climatology,2018-12-16,175.70142857142858,5.183265534903394
2018,Climatology,2018-12-23,261.5357142857143,5.207046369842629
2018,Climatology,2018-12-30,287.3928571428572,5.398866447956088
2018,Climatology + AR(1),2018-01-07,247.29857142857145,5.456173863370797
2018,Climatology + AR(1),2018-01-14,188.26,5.314705575983778
2018,Climatology + AR(1),2018-01-21,197.46,5.423213400066316
2018,Climatology + AR(1),2018-01-28,148.48857142857145,5.187344072131141
2018,Climatology + AR(1),2018-02-04,137.04714285714286,5.029618157093854
2018,Climatology + AR(1),2018-02-11,169.39,4.891661835309968
2018,Climatology + AR(1),2018-02-18,103.70857142857145,5.040553399304759
2018,Climatology + AR(1),2018-02-25,158.08285714285714,5.019262928477295
2018,Climatology + AR(1),2018-03-04,104.86,4.811203622520673
2018,Climatology + AR(1),2018-03-11,96.94857142857144,4.3933790873197935
2018,Climatology + AR(1),2018-03-18,102.21428571428572,4.531198477775137
2018,Climatology + AR(1),2018-03-25,90.97,4.594225557011836
2018,Climatology + AR(1),2018-04-01,97.72857142857144,4.642345803045781
2018,Climatology + AR(1),2018-04-08,94.45285714285714,4.485282744037664
2018,Climatology + AR(1),2018-04-15,75.25,4.733311470833604
2018,Climatology + AR(1),2018-04-22,92.28,4.567764508999198
2018,Climatology + AR(1),2018-04-29,103.68999999999998,4.682608945588915
2018,Climatology + AR(1),2018-05-06,68.93714285714286,4.620561007728236
2018,Climatology + AR(1),2018-05-13,99.39285714285714,4.606307752347082
2018,Climatology + AR(1),2018-05-20,83.68285714285715,4.590276985763428
2018,Climatology + AR(1),2018-05-27,98.57714285714285,4.40192742443862
2018,Climatology + AR(1),2018-06-03,80.00142857142858,4.620131928450353
2018,Climatology + AR(1),2018-06-10,64.88285714285715,4.103093224933544
2018,Climatology + AR(1),2018-06-17,152.4042857142857,4.346714418647559
2018,Climatology + AR(1),2018-06-24,68.25857142857143,4.59794716307543
2018,Climatology + AR(1),2018-07-01,38.87571428571429,3.991780199412662
2018,Climatology + AR(1),2018-07-08,51.74428571428571,4.019113948835443
2018,Climatology + AR(1),2018-07-15,43.470000000000006,3.7520564265056096
2018,Climatology + AR(1),2018-07-22,36.80857142857143,3.801503743435517
2018,Climatology + AR(1),2018-07-29,34.582857142857144,3.492530727107188
2018,Climatology + AR(1),2018-08-05,59.50428571428571,3.607381071843594
2018,Climatology + AR(1),2018-08-12,39.05428571428571,3.994939767530069
2018,Climatology + AR(1),2018-08-19,38.74142857142857,3.7948666599928256
2018,Climatology + AR(1),2018-08-26,31.807142857142857,3.7589078882271862
2018,Climatology + AR(1),2018-09-02,37.85428571428572,3.587192177852604
2018,Climatology + AR(1),2018-09-09,41.95,4.058775906959949
2018,Climatology + AR(1),2018-09-16,33.33,4.0409648879178
2018,Climatology + AR(1),2018-09-23,49.20857142857143,3.9019916276749047
2018,Climatology + AR(1),2018-09-30,57.55857142857143,4.217244990216214
2018,Climatology + AR(1),2018-10-07,83.38714285714286,4.457029176082632
2018,Climatology + AR(1),2018-10-14,96.91142857142856,4.808603082562356
2018,Climatology + AR(1),2018-10-21,140.48285714285714,4.902936387934753
2018,Climatology + AR(1),2018-10-28,171.1542857142857,5.25510416854041
2018,Climatology + AR(1),2018-11-04,202.76142857142847,5.436828178725809
2018,Climatology + AR(1),2018-11-11,283.1485714285714,5.70784383672599
2018,Climatology + AR(1),2018-11-18,173.0885714285714,5.418095741065537
2018,Climatology + AR(1),2018-11-25,168.86714285714285,5.19487223564242
2018,Climatology + AR(1),2018-12-02,186.70857142857145,5.277917645270087
2018,Climatology + AR(1),2018-12-09,201.8728571428572,5.30105888105242
2018,Climatology + AR(1),2018-12-16,175.70142857142858,5.170691688009043
2018,Climatology + AR(1),2018-12-23,261.5357142857143,5.201782068797009
2018,Climatology + AR(1),2018-12-30,287.3928571428572,5.5295793168870455
2018,"DHR, no weather",2018-01-07,247.29857142857145,5.309789667756228
2018,"DHR, no weather",2018-01-14,188.26,5.3968065996382535
2018,"DHR, no weather",2018-01-21,197.46,5.383736299958564
2018,"DHR, no weather",2018-01-28,148.48857142857145,5.338653739844269
2018,"DHR, no weather",2018-02-04,137.04714285714286,5.196382646011795
2018,"DHR, no weather",2018-02-11,169.39,5.026717277851183
2018,"DHR, no weather",2018-02-18,103.70857142857145,4.906276071708687
2018,"DHR, no weather",2018-02-25,158.08285714285714,4.711303553607711
2018,"DHR, no weather",2018-03-04,104.86,4.660695149067454
2018,"DHR, no weather",2018-03-11,96.94857142857144,4.574069403599902
2018,"DHR, no weather",2018-03-18,102.21428571428572,4.536985747300526
2018,"DHR, no weather",2018-03-25,90.97,4.559003950029704
2018,"DHR, no weather",2018-04-01,97.72857142857144,4.581478857158527
2018,"DHR, no weather",2018-04-08,94.45285714285714,4.625904083149593
2018,"DHR, no weather",2018-04-15,75.25,4.651515023588007
2018,"DHR, no weather",2018-04-22,92.28,4.61779924794105
2018,"DHR, no weather",2018-04-29,103.68999999999998,4.6183053593657535
2018,"DHR, no weather",2018-05-06,68.93714285714286,4.6242041858392735
2018,"DHR, no weather",2018-05-13,99.39285714285714,4.537179712602354
2018,"DHR, no weather",2018-05-20,83.68285714285715,4.531534782717373
2018,"DHR, no weather",2018-05-27,98.57714285714285,4.4787302743328
2018,"DHR, no weather",2018-06-03,80.00142857142858,4.451692226014457
2018,"DHR, no weather",2018-06-10,64.88285714285715,4.366973486891729
2018,"DHR, no weather",2018-06-17,152.4042857142857,4.23907032553892
2018,"DHR, no weather",2018-06-24,68.25857142857143,4.279541255610598
2018,"DHR, no weather",2018-07-01,38.87571428571429,4.131931828915012
2018,"DHR, no weather",2018-07-08,51.74428571428571,3.9138027688188135
2018,"DHR, no weather",2018-07-15,43.470000000000006,3.8201569360748926
2018,"DHR, no weather",2018-07-22,36.80857142857143,3.738734483385991
2018,"DHR, no weather",2018-07-29,34.582857142857144,3.676731177929802
2018,"DHR, no weather",2018-08-05,59.50428571428571,3.6507427117990177
2018,"DHR, no weather",2018-08-12,39.05428571428571,3.7591652753226423
2018,"DHR, no weather",2018-08-19,38.74142857142857,3.7740262968800873
2018,"DHR, no weather",2018-08-26,31.807142857142857,3.7981470917848377
2018,"DHR, no weather",2018-09-02,37.85428571428572,3.793582672324037
2018,"DHR, no weather",2018-09-09,41.95,3.845384913740826
2018,"DHR, no weather",2018-09-16,33.33,3.934556550624941
2018,"DHR, no weather",2018-09-23,49.20857142857143,4.00211597568702
2018,"DHR, no weather",2018-09-30,57.55857142857143,4.18196959141688
2018,"DHR, no weather",2018-10-07,83.38714285714286,4.39754112439464
2018,"DHR, no weather",2018-10-14,96.91142857142856,4.668125116796925
2018,"DHR, no weather",2018-10-21,140.48285714285714,4.913920670578492
2018,"DHR, no weather",2018-10-28,171.1542857142857,5.154590206354789
2018,"DHR, no weather",2018-11-04,202.76142857142847,5.328297147898569
2018,"DHR, no weather",2018-11-11,283.1485714285714,5.426457239298548
2018,"DHR, no weather",2018-11-18,173.0885714285714,5.491554281561913
2018,"DHR, no weather",2018-11-25,168.86714285714285,5.384182440116161
2018,"DHR, no weather",2018-12-02,186.70857142857145,5.265067898012756
2018,"DHR, no weather",2018-12-09,201.8728571428572,5.187987073520931
2018,"DHR, no weather",2018-12-16,175.70142857142858,5.162811126538264
2018,"DHR, no weather",2018-12-23,261.5357142857143,5.152805103709591
2018,"DHR, no weather",2018-12-30,287.3928571428572,5.259728646845049
2018,+ lagged weather (operational),2018-01-07,247.29857142857145,5.280811692639269
2018,+ lagged weather (operational),2018-01-14,188.26,5.4068701663802585
2018,+ lagged weather (operational),2018-01-21,197.46,5.398954879043239
2018,+ lagged weather (operational),2018-01-28,148.48857142857145,5.370353492676969
2018,+ lagged weather (operational),2018-02-04,137.04714285714286,5.197377960221797
2018,+ lagged weather (operational),2018-02-11,169.39,5.044119175773326
2018,+ lagged weather (operational),2018-02-18,103.70857142857145,4.968335957607405
2018,+ lagged weather (operational),2018-02-25,158.08285714285714,4.683094847680442
2018,+ lagged weather (operational),2018-03-04,104.86,4.643035020948065
2018,+ lagged weather (operational),2018-03-11,96.94857142857144,4.565688109927662
2018,+ lagged weather (operational),2018-03-18,102.21428571428572,4.6004539178962895
2018,+ lagged weather (operational),2018-03-25,90.97,4.620788759584513
2018,+ lagged weather (operational),2018-04-01,97.72857142857144,4.583616266851051
2018,+ lagged weather (operational),2018-04-08,94.45285714285714,4.626257353412514
2018,+ lagged weather (operational),2018-04-15,75.25,4.622393969039346
2018,+ lagged weather (operational),2018-04-22,92.28,4.562673758757156
2018,+ lagged weather (operational),2018-04-29,103.68999999999998,4.655322302246812
2018,+ lagged weather (operational),2018-05-06,68.93714285714286,4.604088057303517
2018,+ lagged weather (operational),2018-05-13,99.39285714285714,4.478618639333169
2018,+ lagged weather (operational),2018-05-20,83.68285714285715,4.500790712219088
2018,+ lagged weather (operational),2018-05-27,98.57714285714285,4.500769667561629
2018,+ lagged weather (operational),2018-06-03,80.00142857142858,4.534223832622314
2018,+ lagged weather (operational),2018-06-10,64.88285714285715,4.341900573140272
2018,+ lagged weather (operational),2018-06-17,152.4042857142857,4.198450662695486
2018,+ lagged weather (operational),2018-06-24,68.25857142857143,4.291547155359321
2018,+ lagged weather (operational),2018-07-01,38.87571428571429,4.206267316459312
2018,+ lagged weather (operational),2018-07-08,51.74428571428571,3.9299779161836463
2018,+ lagged weather (operational),2018-07-15,43.470000000000006,3.828100619184461
2018,+ lagged weather (operational),2018-07-22,36.80857142857143,3.754715715923929
2018,+ lagged weather (operational),2018-07-29,34.582857142857144,3.648253758486762
2018,+ lagged weather (operational),2018-08-05,59.50428571428571,3.64691814797868
2018,+ lagged weather (operational),2018-08-12,39.05428571428571,3.778683288865617
2018,+ lagged weather (operational),2018-08-19,38.74142857142857,3.766435623923281
2018,+ lagged weather (operational),2018-08-26,31.807142857142857,3.778410466946024
2018,+ lagged weather (operational),2018-09-02,37.85428571428572,3.790690279059242
2018,+ lagged weather (operational),2018-09-09,41.95,3.836254707835573
2018,+ lagged weather (operational),2018-09-16,33.33,3.8755254316907193
2018,+ lagged weather (operational),2018-09-23,49.20857142857143,3.9991187731638655
2018,+ lagged weather (operational),2018-09-30,57.55857142857143,4.19549888367883
2018,+ lagged weather (operational),2018-10-07,83.38714285714286,4.380740775064185
2018,+ lagged weather (operational),2018-10-14,96.91142857142856,4.672366088220978
2018,+ lagged weather (operational),2018-10-21,140.48285714285714,4.856666609187492
2018,+ lagged weather (operational),2018-10-28,171.1542857142857,5.156940492293543
2018,+ lagged weather (operational),2018-11-04,202.76142857142847,5.334509750512268
2018,+ lagged weather (operational),2018-11-11,283.1485714285714,5.443059101003124
2018,+ lagged weather (operational),2018-11-18,173.0885714285714,5.537324626116959
2018,+ lagged weather (operational),2018-11-25,168.86714285714285,5.358998238352591
2018,+ lagged weather (operational),2018-12-02,186.70857142857145,5.242548963029893
2018,+ lagged weather (operational),2018-12-09,201.8728571428572,5.173364786033899
2018,+ lagged weather (operational),2018-12-16,175.70142857142858,5.155434008401029
2018,+ lagged weather (operational),2018-12-23,261.5357142857143,5.152940146541728
2018,+ lagged weather (operational),2018-12-30,287.3928571428572,5.235079867275646
2018,+ last 3 days of prior week (operational),2018-01-07,247.29857142857145,5.33105606548935
2018,+ last 3 days of prior week (operational),2018-01-14,188.26,5.395957921607566
2018,+ last 3 days of prior week (operational),2018-01-21,197.46,5.386707969617428
2018,+ last 3 days of prior week (operational),2018-01-28,148.48857142857145,5.350808920191568
2018,+ last 3 days of prior week (operational),2018-02-04,137.04714285714286,5.189206712823499
2018,+ last 3 days of prior week (operational),2018-02-11,169.39,5.042373941029907
2018,+ last 3 days of prior week (operational),2018-02-18,103.70857142857145,4.94099320789267
2018,+ last 3 days of prior week (operational),2018-02-25,158.08285714285714,4.697090778270457
2018,+ last 3 days of prior week (operational),2018-03-04,104.86,4.671645351913671
2018,+ last 3 days of prior week (operational),2018-03-11,96.94857142857144,4.595792303628607
2018,+ last 3 days of prior week (operational),2018-03-18,102.21428571428572,4.541309620119258
2018,+ last 3 days of prior week (operational),2018-03-25,90.97,4.569113393623075
2018,+ last 3 days of prior week (operational),2018-04-01,97.72857142857144,4.57230414546124
2018,+ last 3 days of prior week (operational),2018-04-08,94.45285714285714,4.604097489041223
2018,+ last 3 days of prior week (operational),2018-04-15,75.25,4.624690557182539
2018,+ last 3 days of prior week (operational),2018-04-22,92.28,4.628262161993428
2018,+ last 3 days of prior week (operational),2018-04-29,103.68999999999998,4.567484099614671
2018,+ last 3 days of prior week (operational),2018-05-06,68.93714285714286,4.579245585434946
2018,+ last 3 days of prior week (operational),2018-05-13,99.39285714285714,4.513763720820907
2018,+ last 3 days of prior week (operational),2018-05-20,83.68285714285715,4.52213581149437
2018,+ last 3 days of prior week (operational),2018-05-27,98.57714285714285,4.527246291727714
2018,+ last 3 days of prior week (operational),2018-06-03,80.00142857142858,4.497009755502515
2018,+ last 3 days of prior week (operational),2018-06-10,64.88285714285715,4.287206706802168
2018,+ last 3 days of prior week (operational),2018-06-17,152.4042857142857,4.203452514691429
2018,+ last 3 days of prior week (operational),2018-06-24,68.25857142857143,4.264435503500675
2018,+ last 3 days of prior week (operational),2018-07-01,38.87571428571429,4.215214119132933
2018,+ last 3 days of prior week (operational),2018-07-08,51.74428571428571,3.874896090741288
2018,+ last 3 days of prior week (operational),2018-07-15,43.470000000000006,3.874467885510777
2018,+ last 3 days of prior week (operational),2018-07-22,36.80857142857143,3.7460886776892073
2018,+ last 3 days of prior week (operational),2018-07-29,34.582857142857144,3.7260704104828535
2018,+ last 3 days of prior week (operational),2018-08-05,59.50428571428571,3.64269175432155
2018,+ last 3 days of prior week (operational),2018-08-12,39.05428571428571,3.742027285452066
2018,+ last 3 days of prior week (operational),2018-08-19,38.74142857142857,3.768628768445092
2018,+ last 3 days of prior week (operational),2018-08-26,31.807142857142857,3.800677343754983
2018,+ last 3 days of prior week (operational),2018-09-02,37.85428571428572,3.7733611528928543
2018,+ last 3 days of prior week (operational),2018-09-09,41.95,3.8614311227778857
2018,+ last 3 days of prior week (operational),2018-09-16,33.33,3.8792743857786354
2018,+ last 3 days of prior week (operational),2018-09-23,49.20857142857143,4.010454930027047
2018,+ last 3 days of prior week (operational),2018-09-30,57.55857142857143,4.048748578303486
2018,+ last 3 days of prior week (operational),2018-10-07,83.38714285714286,4.426064011896485
2018,+ last 3 days of prior week (operational),2018-10-14,96.91142857142856,4.692962233896221
2018,+ last 3 days of prior week (operational),2018-10-21,140.48285714285714,4.907863021013057
2018,+ last 3 days of prior week (operational),2018-10-28,171.1542857142857,5.168806617872264
2018,+ last 3 days of prior week (operational),2018-11-04,202.76142857142847,5.326333491585753
2018,+ last 3 days of prior week (operational),2018-11-11,283.1485714285714,5.38708402199153
2018,+ last 3 days of prior week (operational),2018-11-18,173.0885714285714,5.532740512038581
2018,+ last 3 days of prior week (operational),2018-11-25,168.86714285714285,5.351237881897427
2018,+ last 3 days of prior week (operational),2018-12-02,186.70857142857145,5.234769738985838
2018,+ last 3 days of prior week (operational),2018-12-09,201.8728571428572,5.203244659570666
2018,+ last 3 days of prior week (operational),2018-12-16,175.70142857142858,5.176115140272713
2018,+ last 3 days of prior week (operational),2018-12-23,261.5357142857143,5.146874617867804
2018,+ last 3 days of prior week (operational),2018-12-30,287.3928571428572,5.278226861357915
2018,+ same-week weather (ORACLE),2018-01-07,247.29857142857145,5.367128923661773
2018,+ same-week weather (ORACLE),2018-01-14,188.26,5.332645179386901
2018,+ same-week weather (ORACLE),2018-01-21,197.46,5.393511717382872
2018,+ same-week weather (ORACLE),2018-01-28,148.48857142857145,5.319547180867673
2018,+ same-week weather (ORACLE),2018-02-04,137.04714285714286,5.131008392251311
2018,+ same-week weather (ORACLE),2018-02-11,169.39,5.152212217311686
2018,+ same-week weather (ORACLE),2018-02-18,103.70857142857145,4.706336760303192
2018,+ same-week weather (ORACLE),2018-02-25,158.08285714285714,4.864490128908577
2018,+ same-week weather (ORACLE),2018-03-04,104.86,4.602787879188682
2018,+ same-week weather (ORACLE),2018-03-11,96.94857142857144,4.674082938768307
2018,+ same-week weather (ORACLE),2018-03-18,102.21428571428572,4.628401105736135
2018,+ same-week weather (ORACLE),2018-03-25,90.97,4.675022657503407
2018,+ same-week weather (ORACLE),2018-04-01,97.72857142857144,4.496167138219241
2018,+ same-week weather (ORACLE),2018-04-08,94.45285714285714,4.657217485538238
2018,+ same-week weather (ORACLE),2018-04-15,75.25,4.617571767092575
2018,+ same-week weather (ORACLE),2018-04-22,92.28,4.530215756242202
2018,+ same-week weather (ORACLE),2018-04-29,103.68999999999998,4.552034681859364
2018,+ same-week weather (ORACLE),2018-05-06,68.93714285714286,4.356162537645639
2018,+ same-week weather (ORACLE),2018-05-13,99.39285714285714,4.54618652317735
2018,+ same-week weather (ORACLE),2018-05-20,83.68285714285715,4.644797841566329
2018,+ same-week weather (ORACLE),2018-05-27,98.57714285714285,4.670232755432298
2018,+ same-week weather (ORACLE),2018-06-03,80.00142857142858,4.261273261230135
2018,+ same-week weather (ORACLE),2018-06-10,64.88285714285715,4.19507799874749
2018,+ same-week weather (ORACLE),2018-06-17,152.4042857142857,4.182547118703247
2018,+ same-week weather (ORACLE),2018-06-24,68.25857142857143,4.559911405860307
2018,+ same-week weather (ORACLE),2018-07-01,38.87571428571429,4.084465176201629
2018,+ same-week weather (ORACLE),2018-07-08,51.74428571428571,3.991836626951497
2018,+ same-week weather (ORACLE),2018-07-15,43.470000000000006,3.855714750789884
2018,+ same-week weather (ORACLE),2018-07-22,36.80857142857143,3.819854081543282
2018,+ same-week weather (ORACLE),2018-07-29,34.582857142857144,3.795128986680476
2018,+ same-week weather (ORACLE),2018-08-05,59.50428571428571,3.591157149608243
2018,+ same-week weather (ORACLE),2018-08-12,39.05428571428571,3.758391805228982
2018,+ same-week weather (ORACLE),2018-08-19,38.74142857142857,3.8154756862322254
2018,+ same-week weather (ORACLE),2018-08-26,31.807142857142857,3.7689172388684766
2018,+ same-week weather (ORACLE),2018-09-02,37.85428571428572,3.907249182358432
2018,+ same-week weather (ORACLE),2018-09-09,41.95,3.7901896576814327
2018,+ same-week weather (ORACLE),2018-09-16,33.33,3.759080547646404
2018,+ same-week weather (ORACLE),2018-09-23,49.20857142857143,3.8448364790229057
2018,+ same-week weather (ORACLE),2018-09-30,57.55857142857143,4.106468867682794
2018,+ same-week weather (ORACLE),2018-10-07,83.38714285714286,4.447774335187308
2018,+ same-week weather (ORACLE),2018-10-14,96.91142857142856,4.543453775338416
2018,+ same-week weather (ORACLE),2018-10-21,140.48285714285714,4.959052551935233
2018,+ same-week weather (ORACLE),2018-10-28,171.1542857142857,5.18284036654549
2018,+ same-week weather (ORACLE),2018-11-04,202.76142857142847,5.313752083499861
2018,+ same-week weather (ORACLE),2018-11-11,283.1485714285714,5.534374047549677
2018,+ same-week weather (ORACLE),2018-11-18,173.0885714285714,5.447209522616159
2018,+ same-week weather (ORACLE),2018-11-25,168.86714285714285,5.352572211628384
2018,+ same-week weather (ORACLE),2018-12-02,186.70857142857145,5.238252835129369
2018,+ same-week weather (ORACLE),2018-12-09,201.8728571428572,5.2062838248419645
2018,+ same-week weather (ORACLE),2018-12-16,175.70142857142858,5.202310125191636
2018,+ same-week weather (ORACLE),2018-12-23,261.5357142857143,5.202994843374706
2018,+ same-week weather (ORACLE),2018-12-30,287.3928571428572,5.302466775071327
2019,Persistence,2019-01-06,282.41142857142853,5.660850119970929
2019,Persistence,2019-01-13,215.72,5.64336497424579
2019,Persistence,2019-01-20,239.19571428571427,5.373981270469026
2019,Persistence,2019-01-27,116.32714285714285,5.477282105050224
2019,Persistence,2019-02-03,166.56714285714287,4.756406418856059
2019,Persistence,2019-02-10,134.56428571428572,5.115398488536135
2019,Persistence,2019-02-17,152.75857142857143,4.90204204555607
2019,Persistence,2019-02-24,90.08714285714288,5.028858710576035
2019,Persistence,2019-03-03,80.32000000000001,4.500777455843011
2019,Persistence,2019-03-10,86.03,4.38601865594342
2019,Persistence,2019-03-17,82.42142857142858,4.454696072633257
2019,Persistence,2019-03-24,79.07571428571428,4.411845458585364
2019,Persistence,2019-03-31,87.09142857142857,4.370405802166587
2019,Persistence,2019-04-07,104.12285714285711,4.466958469962336
2019,Persistence,2019-04-14,72.85857142857142,4.645571520614807
2019,Persistence,2019-04-21,61.77,4.288520184313964
2019,Persistence,2019-04-28,88.33,4.123417809707808
2019,Persistence,2019-05-05,85.77428571428571,4.4810798007570405
2019,Persistence,2019-05-12,129.04857142857142,4.451719261275106
2019,Persistence,2019-05-19,86.87,4.860188856196892
2019,Persistence,2019-05-26,67.29142857142857,4.464412748271829
2019,Persistence,2019-06-02,78.25999999999999,4.209032867045144
2019,Persistence,2019-06-09,70.20857142857143,4.360036616782266
2019,Persistence,2019-06-16,69.01285714285714,4.251470403700252
2019,Persistence,2019-06-23,53.53857142857142,4.2342928226427015
2019,Persistence,2019-06-30,56.73285714285714,3.980402355415933
2019,Persistence,2019-07-07,46.77428571428572,4.038353533949284
2019,Persistence,2019-07-14,62.93857142857143,3.8453336013708825
2019,Persistence,2019-07-21,42.65,4.142159194025184
2019,Persistence,2019-07-28,42.49,3.753027273937688
2019,Persistence,2019-08-04,34.18857142857143,3.74926875412672
2019,Persistence,2019-08-11,28.487142857142857,3.531891419466518
2019,Persistence,2019-08-18,20.78142857142857,3.3494528576662868
2019,Persistence,2019-08-25,45.11857142857143,3.0340597307300574
2019,Persistence,2019-09-01,39.64142857142857,3.8092939450877537
2019,Persistence,2019-09-08,46.80571428571428,3.6798747474458255
2019,Persistence,2019-09-15,50.56857142857143,3.846005295592088
2019,Persistence,2019-09-22,39.85142857142857,3.9233302653072943
2019,Persistence,2019-09-29,25.55,3.6851582533120815
2019,Persistence,2019-10-06,43.25571428571429,3.2406373166497136
2019,Persistence,2019-10-13,87.52285714285713,3.7671293468635647
2019,Persistence,2019-10-20,111.85142857142856,4.4718999837401885
2019,Persistence,2019-10-27,140.25571428571428,4.717171460062251
2019,Persistence,2019-11-03,353.36857142857144,4.943467287142965
2019,Persistence,2019-11-10,176.22285714285712,5.867511623923472
2019,Persistence,2019-11-17,297.9271428571428,5.171749427806506
2019,Persistence,2019-11-24,152.52142857142854,5.696848969557004
2019,Persistence,2019-12-01,86.82571428571428,5.02730510139861
2019,Persistence,2019-12-08,204.55428571428573,4.46390282532494
2019,Persistence,2019-12-15,184.0914285714286,5.320833396071274
2019,Persistence,2019-12-22,185.57857142857145,5.215432528607776
2019,Persistence,2019-12-29,234.32857142857145,5.223478358021557
2019,Climatology,2019-01-06,282.41142857142853,5.434197948032715
2019,Climatology,2019-01-13,215.72,5.267708876379964
2019,Climatology,2019-01-20,239.19571428571427,5.399659353705149
2019,Climatology,2019-01-27,116.32714285714285,5.182127044787552
2019,Climatology,2019-02-03,166.56714285714287,5.068326379352324
2019,Climatology,2019-02-10,134.56428571428572,5.005606412276393
2019,Climatology,2019-02-17,152.75857142857143,4.894784052763326
2019,Climatology,2019-02-24,90.08714285714288,5.122283077567929
2019,Climatology,2019-03-03,80.32000000000001,4.793069511607513
2019,Climatology,2019-03-10,86.03,4.489640694836053
2019,Climatology,2019-03-17,82.42142857142858,4.524430400320788
2019,Climatology,2019-03-24,79.07571428571428,4.535984248620467
2019,Climatology,2019-03-31,87.09142857142857,4.636562361181251
2019,Climatology,2019-04-07,104.12285714285711,4.520754073584595
2019,Climatology,2019-04-14,72.85857142857142,4.620245071635307
2019,Climatology,2019-04-21,61.77,4.6658941641564855
2019,Climatology,2019-04-28,88.33,4.723595977576291
2019,Climatology,2019-05-05,85.77428571428571,4.553601588555389
2019,Climatology,2019-05-12,129.04857142857142,4.720991552005117
2019,Climatology,2019-05-19,86.87,4.59378975463906
2019,Climatology,2019-05-26,67.29142857142857,4.509783017368246
2019,Climatology,2019-06-02,78.25999999999999,4.531140268800598
2019,Climatology,2019-06-09,70.20857142857143,4.174672761722088
2019,Climatology,2019-06-16,69.01285714285714,4.517429620742329
2019,Climatology,2019-06-23,53.53857142857142,4.319189257210957
2019,Climatology,2019-06-30,56.73285714285714,3.943789094521117
2019,Climatology,2019-07-07,46.77428571428572,4.103957172870507
2019,Climatology,2019-07-14,62.93857142857143,3.814374650600652
2019,Climatology,2019-07-21,42.65,3.7679408789883073
2019,Climatology,2019-07-28,42.49,3.5642125617792497
2019,Climatology,2019-08-04,34.18857142857143,3.734629977026136
2019,Climatology,2019-08-11,28.487142857142857,3.7846772651935656
2019,Climatology,2019-08-18,20.78142857142857,3.803905852176592
2019,Climatology,2019-08-25,45.11857142857143,3.737547315093024
2019,Climatology,2019-09-01,39.64142857142857,3.699850875327819
2019,Climatology,2019-09-08,46.80571428571428,4.002236043411254
2019,Climatology,2019-09-15,50.56857142857143,4.003960043042373
2019,Climatology,2019-09-22,39.85142857142857,4.081388300513565
2019,Climatology,2019-09-29,25.55,4.243511759511004
2019,Climatology,2019-10-06,43.25571428571429,4.51798167057987
2019,Climatology,2019-10-13,87.52285714285713,4.784254654282071
2019,Climatology,2019-10-20,111.85142857142856,4.98998990668643
2019,Climatology,2019-10-27,140.25571428571428,5.243295453681435
2019,Climatology,2019-11-03,353.36857142857144,5.442251227757787
2019,Climatology,2019-11-10,176.22285714285712,5.739720525302815
2019,Climatology,2019-11-17,297.9271428571428,5.386107052776994
2019,Climatology,2019-11-24,152.52142857142854,5.262891227519384
2019,Climatology,2019-12-01,86.82571428571428,5.314463696059258
2019,Climatology,2019-12-08,204.55428571428573,5.333576262155319
2019,Climatology,2019-12-15,184.0914285714286,5.1796456826531285
2019,Climatology,2019-12-22,185.57857142857145,5.296927489603438
2019,Climatology,2019-12-29,234.32857142857145,5.451263182359057
2019,Climatology + AR(1),2019-01-06,282.41142857142853,5.510923945669052
2019,Climatology + AR(1),2019-01-13,215.72,5.34428115202695
2019,Climatology + AR(1),2019-01-20,239.19571428571427,5.438563760394774
2019,Climatology + AR(1),2019-01-27,116.32714285714285,5.210543334009056
2019,Climatology + AR(1),2019-02-03,166.56714285714287,4.912477736726281
2019,Climatology + AR(1),2019-02-10,134.56428571428572,5.022838662430564
2019,Climatology + AR(1),2019-02-17,152.75857142857143,4.856871006049951
2019,Climatology + AR(1),2019-02-24,90.08714285714288,5.171365391550115
2019,Climatology + AR(1),2019-03-03,80.32000000000001,4.565547513305579
2019,Climatology + AR(1),2019-03-10,86.03,4.340626718366831
2019,Climatology + AR(1),2019-03-17,82.42142857142858,4.511637804412452
2019,Climatology + AR(1),2019-03-24,79.07571428571428,4.494768932094034
2019,Climatology + AR(1),2019-03-31,87.09142857142857,4.575947078396905
2019,Climatology + AR(1),2019-04-07,104.12285714285711,4.458665148076869
2019,Climatology + AR(1),2019-04-14,72.85857142857142,4.665938487718081
2019,Climatology + AR(1),2019-04-21,61.77,4.544455666077636
2019,Climatology + AR(1),2019-04-28,88.33,4.525005168609578
2019,Climatology + AR(1),2019-05-05,85.77428571428571,4.464820790374801
2019,Climatology + AR(1),2019-05-12,129.04857142857142,4.683694269592567
2019,Climatology + AR(1),2019-05-19,86.87,4.6447473770658
2019,Climatology + AR(1),2019-05-26,67.29142857142857,4.462420428850868
2019,Climatology + AR(1),2019-06-02,78.25999999999999,4.421041063259694
2019,Climatology + AR(1),2019-06-09,70.20857142857143,4.112034800836192
2019,Climatology + AR(1),2019-06-16,69.01285714285714,4.545543852306725
2019,Climatology + AR(1),2019-06-23,53.53857142857142,4.215537982235119
2019,Climatology + AR(1),2019-06-30,56.73285714285714,3.8197653203177655
2019,Climatology + AR(1),2019-07-07,46.77428571428572,4.13857550852978
2019,Climatology + AR(1),2019-07-14,62.93857142857143,3.719697225749261
2019,Climatology + AR(1),2019-07-21,42.65,3.887936888236709
2019,Climatology + AR(1),2019-07-28,42.49,3.5587529599600654
2019,Climatology + AR(1),2019-08-04,34.18857142857143,3.802375711270965
2019,Climatology + AR(1),2019-08-11,28.487142857142857,3.710458335973273
2019,Climatology + AR(1),2019-08-18,20.78142857142857,3.644578046523677
2019,Climatology + AR(1),2019-08-25,45.11857142857143,3.455720535392496
2019,Climatology + AR(1),2019-09-01,39.64142857142857,3.726116022507864
2019,Climatology + AR(1),2019-09-08,46.80571428571428,3.994923143293904
2019,Climatology + AR(1),2019-09-15,50.56857142857143,3.946766784128048
2019,Climatology + AR(1),2019-09-22,39.85142857142857,4.051871193167036
2019,Climatology + AR(1),2019-09-29,25.55,4.0984590858499885
2019,Climatology + AR(1),2019-10-06,43.25571428571429,4.150847425434247
2019,Climatology + AR(1),2019-10-13,87.52285714285713,4.50938116134817
2019,Climatology + AR(1),2019-10-20,111.85142857142856,4.875642495598834
2019,Climatology + AR(1),2019-10-27,140.25571428571428,5.143421541073392
2019,Climatology + AR(1),2019-11-03,353.36857142857144,5.332489543851038
2019,Climatology + AR(1),2019-11-10,176.22285714285712,5.8954006861125485
2019,Climatology + AR(1),2019-11-17,297.9271428571428,5.178183078217519
2019,Climatology + AR(1),2019-11-24,152.52142857142854,5.376648238543258
2019,Climatology + AR(1),2019-12-01,86.82571428571428,5.228219864445239
2019,Climatology + AR(1),2019-12-08,204.55428571428573,5.022201268555408
2019,Climatology + AR(1),2019-12-15,184.0914285714286,5.174980749216985
2019,Climatology + AR(1),2019-12-22,185.57857142857145,5.310028408436524
2019,Climatology + AR(1),2019-12-29,234.32857142857145,5.424374780055195
2019,"DHR, no weather",2019-01-06,282.41142857142853,5.359167517717401
2019,"DHR, no weather",2019-01-13,215.72,5.408189513976904
2019,"DHR, no weather",2019-01-20,239.19571428571427,5.362499539120224
2019,"DHR, no weather",2019-01-27,116.32714285714285,5.34162748163514
2019,"DHR, no weather",2019-02-03,166.56714285714287,5.102692635425558
2019,"DHR, no weather",2019-02-10,134.56428571428572,5.039589923540483
2019,"DHR, no weather",2019-02-17,152.75857142857143,4.873190745484746
2019,"DHR, no weather",2019-02-24,90.08714285714288,4.78914232115421
2019,"DHR, no weather",2019-03-03,80.32000000000001,4.596921553229215
2019,"DHR, no weather",2019-03-10,86.03,4.499736711108832
2019,"DHR, no weather",2019-03-17,82.42142857142858,4.4740488472574205
2019,"DHR, no weather",2019-03-24,79.07571428571428,4.455528019574674
2019,"DHR, no weather",2019-03-31,87.09142857142857,4.449327212387484
2019,"DHR, no weather",2019-04-07,104.12285714285711,4.476685842686624
2019,"DHR, no weather",2019-04-14,72.85857142857142,4.528278279400569
2019,"DHR, no weather",2019-04-21,61.77,4.4644725930582245
2019,"DHR, no weather",2019-04-28,88.33,4.4141273278156765
2019,"DHR, no weather",2019-05-05,85.77428571428571,4.471034067533299
2019,"DHR, no weather",2019-05-12,129.04857142857142,4.462910096854858
2019,"DHR, no weather",2019-05-19,86.87,4.5459037898111525
2019,"DHR, no weather",2019-05-26,67.29142857142857,4.4591761921344615
2019,"DHR, no weather",2019-06-02,78.25999999999999,4.354544465037239
2019,"DHR, no weather",2019-06-09,70.20857142857143,4.304081229462097
2019,"DHR, no weather",2019-06-16,69.01285714285714,4.187952968764395
2019,"DHR, no weather",2019-06-23,53.53857142857142,4.076039165251577
2019,"DHR, no weather",2019-06-30,56.73285714285714,3.912813549337822
2019,"DHR, no weather",2019-07-07,46.77428571428572,3.8217563965241736
2019,"DHR, no weather",2019-07-14,62.93857142857143,3.707889839338775
2019,"DHR, no weather",2019-07-21,42.65,3.7283167698415935
2019,"DHR, no weather",2019-07-28,42.49,3.645517770225332
2019,"DHR, no weather",2019-08-04,34.18857142857143,3.646780017085901
2019,"DHR, no weather",2019-08-11,28.487142857142857,3.6133809817196303
2019,"DHR, no weather",2019-08-18,20.78142857142857,3.5781961774425355
2019,"DHR, no weather",2019-08-25,45.11857142857143,3.502933312686342
2019,"DHR, no weather",2019-09-01,39.64142857142857,3.665308950198451
2019,"DHR, no weather",2019-09-08,46.80571428571428,3.694668045556771
2019,"DHR, no weather",2019-09-15,50.56857142857143,3.8087739102705647
2019,"DHR, no weather",2019-09-22,39.85142857142857,3.9494348757544695
2019,"DHR, no weather",2019-09-29,25.55,4.056992254010775
2019,"DHR, no weather",2019-10-06,43.25571428571429,4.1230570843829
2019,"DHR, no weather",2019-10-13,87.52285714285713,4.38609358979459
2019,"DHR, no weather",2019-10-20,111.85142857142856,4.71010184064205
2019,"DHR, no weather",2019-10-27,140.25571428571428,4.931645320153792
2019,"DHR, no weather",2019-11-03,353.36857142857144,5.097100562099376
2019,"DHR, no weather",2019-11-10,176.22285714285712,5.364680806230018
2019,"DHR, no weather",2019-11-17,297.9271428571428,5.258240893405048
2019,"DHR, no weather",2019-11-24,152.52142857142854,5.332927993156065
2019,"DHR, no weather",2019-12-01,86.82571428571428,5.152600579381066
2019,"DHR, no weather",2019-12-08,204.55428571428573,4.954795459847521
2019,"DHR, no weather",2019-12-15,184.0914285714286,5.073866939089497
2019,"DHR, no weather",2019-12-22,185.57857142857145,5.071274976492836
2019,"DHR, no weather",2019-12-29,234.32857142857145,5.112024865127882
2019,+ lagged weather (operational),2019-01-06,282.41142857142853,5.359637230135418
2019,+ lagged weather (operational),2019-01-13,215.72,5.415113061138754
2019,+ lagged weather (operational),2019-01-20,239.19571428571427,5.344845915138025
2019,+ lagged weather (operational),2019-01-27,116.32714285714285,5.3482965908549
2019,+ lagged weather (operational),2019-02-03,166.56714285714287,5.108361888507738
2019,+ lagged weather (operational),2019-02-10,134.56428571428572,5.0322975039795885
2019,+ lagged weather (operational),2019-02-17,152.75857142857143,4.867423550851587
2019,+ lagged weather (operational),2019-02-24,90.08714285714288,4.752651626209175
2019,+ lagged weather (operational),2019-03-03,80.32000000000001,4.595939764520829
2019,+ lagged weather (operational),2019-03-10,86.03,4.48304695925738
2019,+ lagged weather (operational),2019-03-17,82.42142857142858,4.48391611080587
2019,+ lagged weather (operational),2019-03-24,79.07571428571428,4.4714604414105406
2019,+ lagged weather (operational),2019-03-31,87.09142857142857,4.475086144521297
2019,+ lagged weather (operational),2019-04-07,104.12285714285711,4.460466524803529
2019,+ lagged weather (operational),2019-04-14,72.85857142857142,4.537935649426862
2019,+ lagged weather (operational),2019-04-21,61.77,4.464938665663467
2019,+ lagged weather (operational),2019-04-28,88.33,4.391403271760319
2019,+ lagged weather (operational),2019-05-05,85.77428571428571,4.4950181962158045
2019,+ lagged weather (operational),2019-05-12,129.04857142857142,4.504689606954122
2019,+ lagged weather (operational),2019-05-19,86.87,4.597997034290719
2019,+ lagged weather (operational),2019-05-26,67.29142857142857,4.438442019946054
2019,+ lagged weather (operational),2019-06-02,78.25999999999999,4.363498096076092
2019,+ lagged weather (operational),2019-06-09,70.20857142857143,4.334993904098507
2019,+ lagged weather (operational),2019-06-16,69.01285714285714,4.20250128527876
2019,+ lagged weather (operational),2019-06-23,53.53857142857142,4.109313727458879
2019,+ lagged weather (operational),2019-06-30,56.73285714285714,3.935848025950107
2019,+ lagged weather (operational),2019-07-07,46.77428571428572,3.8637521882101
2019,+ lagged weather (operational),2019-07-14,62.93857142857143,3.707619580315951
2019,+ lagged weather (operational),2019-07-21,42.65,3.7765558075756895
2019,+ lagged weather (operational),2019-07-28,42.49,3.599747762336025
2019,+ lagged weather (operational),2019-08-04,34.18857142857143,3.63059221391814
2019,+ lagged weather (operational),2019-08-11,28.487142857142857,3.583193661406807
2019,+ lagged weather (operational),2019-08-18,20.78142857142857,3.598941315306436
2019,+ lagged weather (operational),2019-08-25,45.11857142857143,3.515302467532623
2019,+ lagged weather (operational),2019-09-01,39.64142857142857,3.644834827815776
2019,+ lagged weather (operational),2019-09-08,46.80571428571428,3.685315995776973
2019,+ lagged weather (operational),2019-09-15,50.56857142857143,3.764024565148003
2019,+ lagged weather (operational),2019-09-22,39.85142857142857,3.942657898065658
2019,+ lagged weather (operational),2019-09-29,25.55,4.04424524769524
2019,+ lagged weather (operational),2019-10-06,43.25571428571429,4.149468708186806
2019,+ lagged weather (operational),2019-10-13,87.52285714285713,4.3841571342152585
2019,+ lagged weather (operational),2019-10-20,111.85142857142856,4.716158777646783
2019,+ lagged weather (operational),2019-10-27,140.25571428571428,4.938127704700038
2019,+ lagged weather (operational),2019-11-03,353.36857142857144,5.114381244435517
2019,+ lagged weather (operational),2019-11-10,176.22285714285712,5.3747730697351015
2019,+ lagged weather (operational),2019-11-17,297.9271428571428,5.281909830748628
2019,+ lagged weather (operational),2019-11-24,152.52142857142854,5.334472064798017
2019,+ lagged weather (operational),2019-12-01,86.82571428571428,5.123192838660607
2019,+ lagged weather (operational),2019-12-08,204.55428571428573,4.954231089148635
2019,+ lagged weather (operational),2019-12-15,184.0914285714286,5.0677355207695065
2019,+ lagged weather (operational),2019-12-22,185.57857142857145,5.0580475040907125
2019,+ lagged weather (operational),2019-12-29,234.32857142857145,5.076902593720429
2019,+ last 3 days of prior week (operational),2019-01-06,282.41142857142853,5.362892203792431
2019,+ last 3 days of prior week (operational),2019-01-13,215.72,5.406239524104437
2019,+ last 3 days of prior week (operational),2019-01-20,239.19571428571427,5.379841217444398
2019,+ last 3 days of prior week (operational),2019-01-27,116.32714285714285,5.356719238909676
2019,+ last 3 days of prior week (operational),2019-02-03,166.56714285714287,5.091607434700669
2019,+ last 3 days of prior week (operational),2019-02-10,134.56428571428572,5.039876747978728
2019,+ last 3 days of prior week (operational),2019-02-17,152.75857142857143,4.873274677256263
2019,+ last 3 days of prior week (operational),2019-02-24,90.08714285714288,4.795989952916109
2019,+ last 3 days of prior week (operational),2019-03-03,80.32000000000001,4.573765910997022
2019,+ last 3 days of prior week (operational),2019-03-10,86.03,4.520921547899664
2019,+ last 3 days of prior week (operational),2019-03-17,82.42142857142858,4.478410982742748
2019,+ last 3 days of prior week (operational),2019-03-24,79.07571428571428,4.456581421341188
2019,+ last 3 days of prior week (operational),2019-03-31,87.09142857142857,4.422241322409482
2019,+ last 3 days of prior week (operational),2019-04-07,104.12285714285711,4.489286410684956
2019,+ last 3 days of prior week (operational),2019-04-14,72.85857142857142,4.538374093638739
2019,+ last 3 days of prior week (operational),2019-04-21,61.77,4.44878078846137
2019,+ last 3 days of prior week (operational),2019-04-28,88.33,4.428265245780398
2019,+ last 3 days of prior week (operational),2019-05-05,85.77428571428571,4.4258951750246505
2019,+ last 3 days of prior week (operational),2019-05-12,129.04857142857142,4.452646289228369
2019,+ last 3 days of prior week (operational),2019-05-19,86.87,4.52568800905842
2019,+ last 3 days of prior week (operational),2019-05-26,67.29142857142857,4.468233904634098
2019,+ last 3 days of prior week (operational),2019-06-02,78.25999999999999,4.341505585017856
2019,+ last 3 days of prior week (operational),2019-06-09,70.20857142857143,4.311016624227833
2019,+ last 3 days of prior week (operational),2019-06-16,69.01285714285714,4.216820312997684
2019,+ last 3 days of prior week (operational),2019-06-23,53.53857142857142,4.034089622923696
2019,+ last 3 days of prior week (operational),2019-06-30,56.73285714285714,3.92997507591021
2019,+ last 3 days of prior week (operational),2019-07-07,46.77428571428572,3.8074074828319366
2019,+ last 3 days of prior week (operational),2019-07-14,62.93857142857143,3.742330530631422
2019,+ last 3 days of prior week (operational),2019-07-21,42.65,3.681164282355263
2019,+ last 3 days of prior week (operational),2019-07-28,42.49,3.6868240857404255
2019,+ last 3 days of prior week (operational),2019-08-04,34.18857142857143,3.624710248698696
2019,+ last 3 days of prior week (operational),2019-08-11,28.487142857142857,3.64627768382648
2019,+ last 3 days of prior week (operational),2019-08-18,20.78142857142857,3.52922428326413
2019,+ last 3 days of prior week (operational),2019-08-25,45.11857142857143,3.4619875752310216
2019,+ last 3 days of prior week (operational),2019-09-01,39.64142857142857,3.7093948437871136
2019,+ last 3 days of prior week (operational),2019-09-08,46.80571428571428,3.715698226088012
2019,+ last 3 days of prior week (operational),2019-09-15,50.56857142857143,3.820417528942052
2019,+ last 3 days of prior week (operational),2019-09-22,39.85142857142857,3.94207353457751
2019,+ last 3 days of prior week (operational),2019-09-29,25.55,4.072199417268207
2019,+ last 3 days of prior week (operational),2019-10-06,43.25571428571429,4.089909076424188
2019,+ last 3 days of prior week (operational),2019-10-13,87.52285714285713,4.389992080833101
2019,+ last 3 days of prior week (operational),2019-10-20,111.85142857142856,4.7265313489221805
2019,+ last 3 days of prior week (operational),2019-10-27,140.25571428571428,4.929244361943431
2019,+ last 3 days of prior week (operational),2019-11-03,353.36857142857144,5.100521594183128
2019,+ last 3 days of prior week (operational),2019-11-10,176.22285714285712,5.361215429502756
2019,+ last 3 days of prior week (operational),2019-11-17,297.9271428571428,5.251812743435043
2019,+ last 3 days of prior week (operational),2019-11-24,152.52142857142854,5.2971917531691854
2019,+ last 3 days of prior week (operational),2019-12-01,86.82571428571428,5.1585597018796046
2019,+ last 3 days of prior week (operational),2019-12-08,204.55428571428573,4.968404047684039
2019,+ last 3 days of prior week (operational),2019-12-15,184.0914285714286,5.097640028988289
2019,+ last 3 days of prior week (operational),2019-12-22,185.57857142857145,5.074131487758417
2019,+ last 3 days of prior week (operational),2019-12-29,234.32857142857145,5.128873028659806
2019,+ same-week weather (ORACLE),2019-01-06,282.41142857142853,5.35597808875955
2019,+ same-week weather (ORACLE),2019-01-13,215.72,5.434993707247946
2019,+ same-week weather (ORACLE),2019-01-20,239.19571428571427,5.399838030870583
2019,+ same-week weather (ORACLE),2019-01-27,116.32714285714285,5.239512440068485
2019,+ same-week weather (ORACLE),2019-02-03,166.56714285714287,5.063652827410647
2019,+ same-week weather (ORACLE),2019-02-10,134.56428571428572,4.892039445161513
2019,+ same-week weather (ORACLE),2019-02-17,152.75857142857143,4.818199302056225
2019,+ same-week weather (ORACLE),2019-02-24,90.08714285714288,4.660484855480858
2019,+ same-week weather (ORACLE),2019-03-03,80.32000000000001,4.571711115752366
2019,+ same-week weather (ORACLE),2019-03-10,86.03,4.541148530556252
2019,+ same-week weather (ORACLE),2019-03-17,82.42142857142858,4.446650875759064
2019,+ same-week weather (ORACLE),2019-03-24,79.07571428571428,4.554094450859378
2019,+ same-week weather (ORACLE),2019-03-31,87.09142857142857,4.408595331088791
2019,+ same-week weather (ORACLE),2019-04-07,104.12285714285711,4.590761119976648
2019,+ same-week weather (ORACLE),2019-04-14,72.85857142857142,4.565066074049738
2019,+ same-week weather (ORACLE),2019-04-21,61.77,4.37676595500646
2019,+ same-week weather (ORACLE),2019-04-28,88.33,4.359128121583243
2019,+ same-week weather (ORACLE),2019-05-05,85.77428571428571,4.636036619803538
2019,+ same-week weather (ORACLE),2019-05-12,129.04857142857142,4.449073971951503
2019,+ same-week weather (ORACLE),2019-05-19,86.87,4.522288497228607
2019,+ same-week weather (ORACLE),2019-05-26,67.29142857142857,4.451402736022774
2019,+ same-week weather (ORACLE),2019-06-02,78.25999999999999,4.536898301935088
2019,+ same-week weather (ORACLE),2019-06-09,70.20857142857143,4.410075968689771
2019,+ same-week weather (ORACLE),2019-06-16,69.01285714285714,4.315379700125485
2019,+ same-week weather (ORACLE),2019-06-23,53.53857142857142,4.118252730380329
2019,+ same-week weather (ORACLE),2019-06-30,56.73285714285714,4.176751265490984
2019,+ same-week weather (ORACLE),2019-07-07,46.77428571428572,3.938839900076948
2019,+ same-week weather (ORACLE),2019-07-14,62.93857142857143,3.759279260632812
2019,+ same-week weather (ORACLE),2019-07-21,42.65,3.7726711484832314
2019,+ same-week weather (ORACLE),2019-07-28,42.49,3.642281762540546
2019,+ same-week weather (ORACLE),2019-08-04,34.18857142857143,3.6246373626260064
2019,+ same-week weather (ORACLE),2019-08-11,28.487142857142857,3.501631936893564
2019,+ same-week weather (ORACLE),2019-08-18,20.78142857142857,3.387580677153115
2019,+ same-week weather (ORACLE),2019-08-25,45.11857142857143,3.571478017332863
2019,+ same-week weather (ORACLE),2019-09-01,39.64142857142857,3.7348912177340727
2019,+ same-week weather (ORACLE),2019-09-08,46.80571428571428,3.706981525845944
2019,+ same-week weather (ORACLE),2019-09-15,50.56857142857143,3.721058523372774
2019,+ same-week weather (ORACLE),2019-09-22,39.85142857142857,3.934367980432667
2019,+ same-week weather (ORACLE),2019-09-29,25.55,3.857832184249025
2019,+ same-week weather (ORACLE),2019-10-06,43.25571428571429,4.069042834584395
2019,+ same-week weather (ORACLE),2019-10-13,87.52285714285713,4.485265166609083
2019,+ same-week weather (ORACLE),2019-10-20,111.85142857142856,4.758488871401581
2019,+ same-week weather (ORACLE),2019-10-27,140.25571428571428,4.919637180965591
2019,+ same-week weather (ORACLE),2019-11-03,353.36857142857144,5.110424681617166
2019,+ same-week weather (ORACLE),2019-11-10,176.22285714285712,5.313140875901765
2019,+ same-week weather (ORACLE),2019-11-17,297.9271428571428,5.225933724491203
2019,+ same-week weather (ORACLE),2019-11-24,152.52142857142854,5.327943381990668
2019,+ same-week weather (ORACLE),2019-12-01,86.82571428571428,5.033916786378875
2019,+ same-week weather (ORACLE),2019-12-08,204.55428571428573,4.88917675948976
2019,+ same-week weather (ORACLE),2019-12-15,184.0914285714286,5.09538593261106
2019,+ same-week weather (ORACLE),2019-12-22,185.57857142857145,5.032741373065046
2019,+ same-week weather (ORACLE),2019-12-29,234.32857142857145,5.007868980655888
```

## fc_weekly_2020.csv (no-lockdown forecast, 95% interval, weather-adjusted median and actual, weeks of 2020)
```
date,lo95,median,hi95,weather_adj_median,actual
2020-01-05,118.42678315810193,197.52459088617573,326.99164630418403,199.5657103440318,271.12142857142857
2020-01-12,114.86578106190404,193.14153623343609,327.5177084810721,175.2833378018649,139.47714285714284
2020-01-19,113.5838762964645,188.40426364609996,318.5429808574382,167.0796240116145,134.74571428571429
2020-01-26,106.14049077950357,179.35865422451218,304.8593124013851,174.2466693632494,150.86714285714285
2020-02-02,97.24900403957253,162.7948911280826,276.5658453396509,156.5525617907848,115.5657142857143
2020-02-09,84.23362869889253,140.99979244131492,238.4328311335805,143.83476653847862,149.54571428571427
2020-02-16,71.23416205665043,120.51098805123311,205.7319231042121,111.02674720456862,129.7642857142857
2020-02-23,62.088576903384165,104.43891713845784,176.455827076084,90.54328349679928,106.28
2020-03-01,58.84517612755658,93.24994369711466,144.11956865689098,78.51444745822505,90.53571428571428
2020-03-08,54.28878444051528,85.85374296165143,132.63415045713734,73.17938920623745,62.044285714285714
2020-03-15,52.7084621383437,82.342577677099,128.1086027777061,71.19582439393858,60.51714285714286
2020-03-22,52.13891261579746,82.05007952887482,129.6037714135071,76.25560020822385,77.45285714285716
2020-03-29,53.23295421735197,82.94285077806165,128.4088387379614,68.83034424966442,38.48285714285714
2020-04-05,53.20943903381347,83.42332548474883,130.05005298446767,75.70761323558764,36.53142857142857
2020-04-12,54.33207688680345,84.39294833393966,132.68187069255123,82.9964779958391,44.01857142857143
2020-04-19,53.444537680530914,84.70664379946643,134.69444461669823,86.13531174765512,48.34857142857143
2020-04-26,53.02344176663063,84.26664629837228,133.00964430271887,77.58157766759041,48.89
2020-05-03,54.071841899268335,83.82951715737907,132.59198233270462,62.40175009689558,43.191428571428574
2020-05-10,53.25866305956278,83.6371009575867,131.65701036328747,74.82037818669444,46.7
2020-05-17,53.15160729763342,83.21962275038324,131.87337546136862,76.54892286938781,62.76571428571429
2020-05-24,52.89073300593888,82.5283076308067,126.48548520126418,94.5905803314257,79.43285714285715
2020-05-31,51.02750864528648,78.78769323859852,123.24827530236756,69.73769302755402,38.33571428571429
2020-06-07,47.57645117628432,74.27895567877677,114.95403354255195,75.08322996323705,46.19571428571429
2020-06-14,42.68315267020742,66.91795749116123,106.46550407097624,75.30407614946672,58.957142857142856
2020-06-21,37.301062229755416,58.73561650169241,92.5624494513853,60.73748006939193,41.85857142857143
2020-06-28,33.026386195671854,51.02958522591283,79.77870142348056,54.44760495334137,41.01428571428572
```



# 06 Daily data and station summary
## delhi_daily.csv (2009 rows: daily city PM2.5 and ERA5 weather used by the notebooks)
```
Date,pm25,no2,so2,aqi,aqi_bucket,rh,wind,temp,precip,imputed,log_pm25,season
2015-01-01,313.22,36.39,9.25,472.0,Severe,68,6.6,16.3,0.0,False,5.7469,Winter (Nov–Jan)
2015-01-02,186.18,32.87,6.65,454.0,Severe,83,7.0,15.2,4.2,False,5.2267,Winter (Nov–Jan)
2015-01-03,87.18,30.31,2.65,143.0,Moderate,84,5.1,15.6,0.1,False,4.468,Winter (Nov–Jan)
2015-01-04,151.84,36.91,4.63,319.0,Very Poor,78,10.2,14.4,0.0,False,5.0228,Winter (Nov–Jan)
2015-01-05,146.6,34.92,3.33,325.0,Very Poor,74,18.7,14.3,0.0,False,4.9877,Winter (Nov–Jan)
2015-01-06,149.58,37.84,3.66,318.0,Very Poor,75,12.7,15.1,0.0,False,5.0078,Winter (Nov–Jan)
2015-01-07,217.87,40.15,5.82,353.0,Very Poor,79,6.9,13.8,0.0,False,5.3839,Winter (Nov–Jan)
2015-01-08,229.9,43.16,3.31,383.0,Very Poor,80,6.9,13.0,0.0,False,5.4376,Winter (Nov–Jan)
2015-01-09,201.66,38.56,3.48,375.0,Very Poor,83,6.4,12.4,0.0,False,5.3066,Winter (Nov–Jan)
2015-01-10,221.02,46.39,5.91,376.0,Very Poor,81,9.4,11.9,0.0,False,5.3983,Winter (Nov–Jan)
2015-01-11,205.41,47.29,5.54,379.0,Very Poor,84,8.4,11.7,0.0,False,5.325,Winter (Nov–Jan)
2015-01-12,212.41,44.71,5.17,375.0,Very Poor,87,4.7,11.3,0.0,False,5.3585,Winter (Nov–Jan)
2015-01-13,197.61,45.88,5.95,366.0,Very Poor,87,8.3,11.2,0.0,False,5.2863,Winter (Nov–Jan)
2015-01-14,164.39,41.17,4.85,353.0,Very Poor,85,12.1,12.9,4.1,False,5.1022,Winter (Nov–Jan)
2015-01-15,166.19,56.7,6.94,340.0,Very Poor,84,5.6,12.0,0.0,False,5.1131,Winter (Nov–Jan)
2015-01-16,174.98,49.41,4.69,356.0,Very Poor,78,7.2,13.3,0.0,False,5.1647,Winter (Nov–Jan)
2015-01-17,196.46,53.04,5.13,360.0,Very Poor,79,7.9,13.8,0.0,False,5.2805,Winter (Nov–Jan)
2015-01-18,201.51,53.77,5.43,370.0,Very Poor,76,6.9,13.7,0.0,False,5.3058,Winter (Nov–Jan)
2015-01-19,183.35,39.88,4.21,362.0,Very Poor,75,5.6,13.1,0.0,False,5.2114,Winter (Nov–Jan)
2015-01-20,165.63,34.23,4.11,340.0,Very Poor,79,8.5,12.7,0.0,False,5.1098,Winter (Nov–Jan)
2015-01-21,159.54,22.56,7.05,338.0,Very Poor,81,11.7,12.6,3.8,False,5.0723,Winter (Nov–Jan)
2015-01-22,143.68,21.82,8.64,332.0,Very Poor,87,9.9,12.8,17.0,False,4.9676,Winter (Nov–Jan)
2015-01-23,128.73,17.35,6.77,254.0,Poor,83,5.9,14.1,0.0,False,4.8577,Winter (Nov–Jan)
2015-01-24,164.98,15.77,8.89,324.0,Very Poor,80,8.2,14.4,0.0,False,5.1058,Winter (Nov–Jan)
2015-01-25,148.59,20.83,5.96,333.0,Very Poor,75,6.8,13.7,0.0,False,5.0012,Winter (Nov–Jan)
2015-01-26,129.34,25.66,6.78,292.0,Poor,74,6.4,13.3,0.0,False,4.8624,Winter (Nov–Jan)
2015-01-27,154.2,30.39,6.42,318.0,Very Poor,69,10.4,12.9,0.0,False,5.0383,Winter (Nov–Jan)
2015-01-28,134.6,28.6,5.21,295.0,Poor,74,11.6,11.4,0.0,False,4.9023,Winter (Nov–Jan)
2015-01-29,173.13,38.34,5.53,327.0,Very Poor,68,10.2,10.9,0.0,False,5.154,Winter (Nov–Jan)
2015-01-30,178.04,38.43,6.43,345.0,Very Poor,66,12.0,11.7,0.0,False,5.182,Winter (Nov–Jan)
2015-01-31,158.59,41.36,5.03,334.0,Very Poor,65,11.8,13.1,0.0,False,5.0663,Winter (Nov–Jan)
2015-02-01,211.59,58.17,9.9,358.0,Very Poor,74,8.2,13.8,0.0,False,5.3547,Other months
2015-02-02,163.64,37.25,5.31,349.0,Very Poor,75,14.7,15.8,1.2,False,5.0977,Other months
2015-02-03,157.71,31.05,5.64,334.0,Very Poor,78,11.8,17.0,13.2,False,5.0608,Other months
2015-02-04,137.26,29.69,5.06,313.0,Very Poor,86,10.7,13.9,0.0,False,4.9219,Other months
2015-02-05,131.76,36.51,4.85,262.0,Poor,76,11.1,14.1,0.0,False,4.881,Other months
2015-02-06,151.6,67.0,9.13,303.0,Very Poor,72,5.9,13.5,0.0,False,5.0212,Other months
2015-02-07,160.75,57.69,6.91,329.0,Very Poor,69,5.8,14.8,0.0,False,5.0799,Other months
2015-02-08,145.34,50.39,8.66,323.0,Very Poor,73,6.5,15.3,2.1,False,4.9791,Other months
2015-02-09,134.67,39.18,9.7,266.0,Poor,71,9.7,15.8,0.0,False,4.9028,Other months
2015-02-10,153.07,42.2,5.81,319.0,Very Poor,67,10.3,15.1,0.0,False,5.0309,Other months
2015-02-11,116.91,53.63,7.54,334.0,Very Poor,64,7.7,14.8,0.0,False,4.7614,Other months
2015-02-12,177.98,42.73,9.2,342.0,Very Poor,69,8.5,15.2,0.0,False,5.1817,Other months
2015-02-13,167.01,44.61,7.77,341.0,Very Poor,63,10.5,16.7,0.0,False,5.1181,Other months
2015-02-14,193.96,53.81,9.36,377.0,Very Poor,63,6.3,18.8,0.0,False,5.2677,Other months
2015-02-15,184.06,58.15,9.13,391.0,Very Poor,71,4.9,18.3,0.0,False,5.2153,Other months
2015-02-16,152.62,44.22,6.79,358.0,Very Poor,70,14.0,19.8,0.0,False,5.028,Other months
2015-02-17,161.27,25.4,5.6,327.0,Very Poor,74,10.8,20.4,1.6,False,5.0831,Other months
2015-02-18,188.2,60.29,8.65,365.0,Very Poor,77,7.2,19.7,12.0,False,5.2375,Other months
2015-02-19,159.97,40.51,5.08,352.0,Very Poor,78,11.9,20.1,1.6,False,5.075,Other months
2015-02-20,144.12,34.71,5.93,317.0,Very Poor,74,10.6,21.2,0.0,False,4.9706,Other months
2015-02-21,155.38,45.11,12.24,320.0,Very Poor,75,11.3,20.6,0.0,False,5.0459,Other months
2015-02-22,124.1,31.83,5.68,279.0,Poor,69,15.9,20.6,0.0,False,4.8211,Other months
2015-02-23,141.39,38.23,9.43,281.0,Poor,77,6.7,20.2,0.0,False,4.9515,Other months
2015-02-24,170.16,48.4,9.28,354.0,Very Poor,79,7.8,20.9,0.1,False,5.1367,Other months
2015-02-25,148.19,29.28,5.94,340.0,Very Poor,79,10.5,21.4,5.2,False,4.9985,Other months
2015-02-26,140.78,20.95,6.98,323.0,Very Poor,69,7.5,18.7,0.0,False,4.9472,Other months
2015-02-27,130.42,24.75,12.12,315.0,Very Poor,68,9.0,17.0,0.0,False,4.8708,Other months
2015-02-28,105.86,20.65,12.48,310.0,Very Poor,56,9.4,18.2,0.2,False,4.6621,Other months
2015-03-01,71.83,21.42,10.99,324.0,Very Poor,83,20.8,17.1,22.9,False,4.2743,Other months
2015-03-02,53.71,13.43,3.21,226.0,Poor,93,15.7,16.3,22.8,False,3.9836,Other months
2015-03-03,83.49,23.75,5.07,266.0,Poor,86,5.7,15.7,1.0,False,4.4247,Other months
2015-03-04,91.07,24.28,4.68,200.0,Moderate,72,9.6,15.2,0.0,False,4.5116,Other months
2015-03-05,106.57,31.12,5.97,275.0,Poor,70,5.6,16.5,0.0,False,4.6688,Other months
2015-03-06,101.75,26.59,5.96,322.0,Very Poor,70,7.3,18.2,0.0,False,4.6225,Other months
2015-03-07,77.57,19.15,5.18,216.0,Poor,76,6.8,18.3,10.5,False,4.3512,Other months
2015-03-08,63.24,20.35,3.98,108.0,Moderate,79,10.6,18.3,0.9,False,4.1469,Other months
2015-03-09,76.62,18.21,4.2,197.0,Moderate,70,11.8,16.6,3.9,False,4.3389,Other months
2015-03-10,86.7,18.82,3.84,238.0,Poor,69,10.6,16.1,0.0,False,4.4625,Other months
2015-03-11,104.29,25.63,6.3,274.0,Poor,70,9.2,17.4,0.0,False,4.6472,Other months
2015-03-12,115.93,32.29,7.03,315.0,Very Poor,67,8.6,18.5,0.0,False,4.753,Other months
2015-03-13,108.66,30.75,10.65,307.0,Very Poor,76,5.9,18.9,2.9,False,4.6882,Other months
2015-03-14,67.94,29.78,10.14,208.0,Poor,79,8.2,20.0,4.1,False,4.2186,Other months
2015-03-15,38.89,17.76,4.25,165.0,Moderate,88,12.3,18.2,20.6,False,3.6607,Other months
2015-03-16,45.39,17.14,8.8,188.0,Moderate,87,11.7,18.2,6.7,False,3.8153,Other months
2015-03-17,55.55,20.96,7.19,217.0,Poor,76,11.7,19.3,0.0,False,4.0173,Other months
2015-03-18,50.59,16.6,3.6,191.0,Moderate,70,13.2,18.8,0.0,False,3.9238,Other months
2015-03-19,69.51,23.77,4.97,240.0,Poor,69,8.1,19.2,0.0,False,4.2415,Other months
2015-03-20,96.62,29.04,6.66,229.0,Poor,67,9.0,20.3,0.0,False,4.5708,Other months
2015-03-21,96.28,29.21,7.31,248.0,Poor,69,7.4,22.0,0.0,False,4.5673,Other months
2015-03-22,72.2,20.27,4.4,204.0,Poor,63,11.5,23.2,0.0,False,4.2794,Other months
2015-03-23,78.47,23.04,4.07,271.0,Poor,62,10.6,24.0,0.0,False,4.3627,Other months
2015-03-24,91.87,30.01,7.35,290.0,Poor,64,7.0,24.2,0.0,False,4.5204,Other months
2015-03-25,107.26,33.82,11.82,340.0,Very Poor,61,6.4,25.2,0.0,False,4.6753,Other months
2015-03-26,109.78,33.02,9.3,358.0,Very Poor,58,5.3,26.7,0.0,False,4.6985,Other months
2015-03-27,62.27,24.76,10.91,287.0,Poor,56,7.3,27.3,0.0,False,4.1315,Other months
2015-03-28,102.22,29.41,17.16,323.0,Very Poor,52,6.1,25.5,0.0,False,4.6271,Other months
2015-03-29,104.36,33.86,16.92,360.0,Very Poor,52,13.6,25.7,0.4,False,4.6478,Other months
2015-03-30,44.19,17.6,7.75,268.0,Poor,75,17.5,22.2,5.1,False,3.7885,Other months
2015-03-31,55.66,20.13,9.34,283.0,Poor,70,8.1,22.9,0.1,False,4.0193,Other months
2015-04-01,112.86,32.71,19.48,309.0,Very Poor,66,6.9,24.3,0.6,False,4.7261,Other months
2015-04-02,78.51,20.54,14.37,249.0,Poor,56,9.1,26.5,0.0,False,4.3632,Other months
2015-04-03,66.52,18.47,10.62,245.0,Poor,72,9.2,23.5,10.8,False,4.1975,Other months
2015-04-04,62.56,24.96,12.94,229.0,Poor,83,5.4,20.8,17.8,False,4.1361,Other months
2015-04-05,78.61,27.75,16.72,234.0,Poor,68,5.1,22.4,0.0,False,4.3645,Other months
2015-04-06,119.7,32.83,16.63,343.0,Very Poor,58,6.9,23.8,0.0,False,4.785,Other months
2015-04-07,66.09,24.47,8.34,262.0,Poor,67,6.0,22.3,5.5,False,4.191,Other months
2015-04-08,95.34,34.72,17.99,308.0,Very Poor,62,6.7,23.5,0.3,False,4.5574,Other months
2015-04-09,63.57,35.15,10.48,293.0,Poor,57,10.9,24.0,0.0,False,4.1521,Other months
2015-04-10,96.56,52.77,15.8,290.0,Poor,51,10.1,25.4,0.0,False,4.5702,Other months
2015-04-11,131.39,59.52,21.5,375.0,Very Poor,49,5.0,26.1,0.1,False,4.8782,Other months
2015-04-12,75.35,45.3,13.08,293.0,Poor,56,8.0,24.4,0.0,False,4.3221,Other months
2015-04-13,86.49,50.3,14.99,247.0,Poor,70,10.5,23.6,7.1,False,4.46,Other months
2015-04-14,77.07,42.65,14.04,232.0,Poor,70,9.3,24.2,0.6,False,4.3447,Other months
2015-04-15,98.79,47.41,13.75,316.0,Very Poor,63,8.4,25.5,0.0,False,4.593,Other months
2015-04-16,81.81,44.06,21.44,295.0,Poor,62,7.6,26.1,0.0,False,4.4044,Other months
2015-04-17,65.78,40.09,14.34,246.0,Poor,56,10.4,27.4,0.0,False,4.1863,Other months
2015-04-18,119.82,51.11,17.21,378.0,Very Poor,46,8.8,29.6,0.0,False,4.786,Other months
2015-04-19,125.53,64.73,18.02,406.0,Severe,39,6.7,31.3,0.0,False,4.8325,Other months
2015-04-20,121.51,60.41,20.98,392.0,Very Poor,38,11.1,31.5,0.1,False,4.8,Other months
2015-04-21,114.5,50.7,19.38,391.0,Very Poor,36,9.8,31.0,0.0,False,4.7406,Other months
2015-04-22,101.83,55.27,19.29,368.0,Very Poor,27,11.8,30.3,0.0,False,4.6233,Other months
2015-04-23,118.57,76.46,21.81,365.0,Very Poor,24,7.4,30.7,0.0,False,4.7755,Other months
2015-04-24,143.22,88.61,26.89,383.0,Very Poor,27,7.2,31.4,0.0,False,4.9644,Other months
2015-04-25,106.76,58.87,17.56,367.0,Very Poor,36,16.4,29.8,0.3,False,4.6706,Other months
2015-04-26,65.36,31.23,12.67,334.0,Very Poor,49,17.8,28.6,0.0,False,4.1799,Other months
2015-04-27,67.08,35.54,11.92,258.0,Poor,50,14.5,29.6,0.9,False,4.2059,Other months
2015-04-28,81.37,34.88,13.97,234.0,Poor,50,11.2,29.9,3.9,False,4.399,Other months
2015-04-29,63.76,42.98,13.98,257.0,Poor,46,8.9,29.9,0.0,False,4.1551,Other months
2015-04-30,60.56,43.9,12.85,259.0,Poor,46,14.2,30.6,1.1,False,4.1036,Other months
2015-05-01,76.1,42.99,13.1,279.0,Poor,40,11.1,30.4,0.0,False,4.332,Other months
2015-05-02,72.66,62.09,16.16,312.0,Very Poor,29,9.1,30.2,0.0,False,4.2858,Other months
2015-05-03,121.94,83.3,19.43,372.0,Very Poor,25,6.9,30.3,0.0,False,4.8035,Other months
2015-05-04,108.98,85.5,17.53,387.0,Very Poor,28,7.1,30.6,0.0,False,4.6912,Other months
2015-05-05,145.99,107.85,26.0,408.0,Severe,28,8.8,31.6,0.0,False,4.9835,Other months
2015-05-06,171.33,87.88,25.26,398.0,Very Poor,27,8.8,32.7,0.0,False,5.1436,Other months
2015-05-07,117.76,63.18,24.63,403.0,Severe,25,11.6,33.7,0.0,False,4.7686,Other months
2015-05-08,90.66,56.54,20.79,361.0,Very Poor,18,11.5,34.7,0.0,False,4.5071,Other months
2015-05-09,106.4,63.57,18.15,378.0,Very Poor,23,6.5,34.1,0.0,False,4.6672,Other months
2015-05-10,101.21,57.51,16.92,381.0,Very Poor,25,9.1,33.5,0.0,False,4.6172,Other months
2015-05-11,97.57,42.7,15.11,388.0,Very Poor,34,6.2,32.9,0.8,False,4.5806,Other months
2015-05-12,96.34,43.04,10.84,346.0,Very Poor,48,8.1,31.2,1.3,False,4.5679,Other months
2015-05-13,83.42,48.61,9.08,328.0,Very Poor,60,6.7,30.1,5.8,False,4.4239,Other months
2015-05-14,78.06,42.22,10.42,291.0,Poor,58,6.1,29.6,1.3,False,4.3575,Other months
2015-05-15,97.87,63.55,15.02,396.0,Very Poor,50,8.3,29.8,3.5,False,4.5836,Other months
2015-05-16,77.52,75.5,15.03,297.0,Poor,55,4.7,30.1,0.0,False,4.3505,Other months
2015-05-17,97.16,57.63,20.15,345.0,Very Poor,47,7.0,31.6,0.0,False,4.5764,Other months
2015-05-18,66.85,47.64,15.04,296.0,Poor,39,7.5,34.6,0.3,False,4.2025,Other months
2015-05-19,89.85,75.47,14.58,319.0,Very Poor,31,9.6,34.1,1.4,False,4.4981,Other months
2015-05-20,67.41,52.69,20.3,282.0,Poor,31,11.5,33.5,0.0,False,4.2108,Other months
2015-05-21,75.54,53.03,14.85,352.0,Very Poor,27,11.1,33.6,0.0,False,4.3247,Other months
2015-05-22,67.91,56.84,14.77,338.0,Very Poor,23,11.9,34.4,0.0,False,4.2182,Other months
2015-05-23,69.02,52.79,10.73,321.0,Very Poor,22,11.2,34.6,0.0,False,4.2344,Other months
2015-05-24,79.1,56.29,18.96,295.0,Poor,23,8.2,35.1,0.0,False,4.3707,Other months
2015-05-25,117.27,60.65,11.78,344.0,Very Poor,21,10.7,35.3,0.0,False,4.7645,Other months
2015-05-26,96.09,51.77,9.9,337.0,Very Poor,18,10.3,35.4,0.0,False,4.5653,Other months
2015-05-27,84.71,70.43,17.48,355.0,Very Poor,17,11.0,33.9,0.0,False,4.4392,Other months
2015-05-28,182.76,72.67,14.33,371.0,Very Poor,21,7.7,34.0,0.0,False,5.2082,Other months
2015-05-29,106.61,64.94,12.9,414.0,Severe,26,10.1,35.1,0.0,False,4.6692,Other months
2015-05-30,92.68,65.26,17.68,366.0,Very Poor,27,9.8,35.0,0.0,False,4.5292,Other months
2015-05-31,73.62,41.86,13.08,346.0,Very Poor,25,10.6,34.8,0.1,False,4.2989,Other months
2015-06-01,49.42,48.55,9.96,289.0,Poor,30,6.8,33.2,0.2,False,3.9004,Other months
2015-06-02,52.51,54.29,6.73,297.0,Poor,35,6.4,32.1,0.3,False,3.961,Other months
2015-06-03,65.28,65.25,6.31,268.0,Poor,42,11.2,31.2,0.5,False,4.1787,Other months
2015-06-04,85.45,62.38,5.53,259.0,Poor,48,9.1,30.8,0.0,False,4.4479,Other months
2015-06-05,83.02,62.63,4.12,327.0,Very Poor,40,8.7,32.8,0.1,False,4.4191,Other months
2015-06-06,44.54,46.37,7.37,384.0,Very Poor,35,10.8,33.1,0.0,False,3.7964,Other months
2015-06-07,85.03,77.07,9.53,299.0,Poor,31,8.8,34.3,0.0,False,4.443,Other months
2015-06-08,137.7,109.34,10.44,282.0,Poor,28,9.0,35.5,0.0,False,4.9251,Other months
2015-06-09,136.05,76.88,8.84,442.0,Severe,25,18.1,36.3,0.0,False,4.913,Other months
2015-06-10,63.77,31.27,5.91,309.0,Very Poor,33,18.9,36.3,0.5,False,4.1553,Other months
2015-06-11,115.57,32.99,6.02,270.0,Poor,34,15.0,35.8,0.1,False,4.7499,Other months
2015-06-12,83.29,36.36,5.52,239.0,Poor,37,13.3,35.4,0.0,False,4.4223,Other months
2015-06-13,73.7,52.9,5.34,214.0,Poor,38,9.7,34.1,2.4,False,4.3,Other months
2015-06-14,74.56,68.76,5.33,166.0,Moderate,69,6.2,29.0,3.7,False,4.3116,Other months
2015-06-15,106.11,72.79,6.3,234.0,Poor,69,6.1,29.4,5.6,False,4.6645,Other months
2015-06-16,132.21,81.57,6.16,331.0,Very Poor,60,5.5,31.9,0.0,False,4.8844,Other months
2015-06-17,123.56,70.96,6.95,327.0,Very Poor,58,5.1,32.7,0.4,False,4.8167,Other months
2015-06-18,132.21,94.25,9.31,313.0,Very Poor,46,5.2,34.1,0.0,False,4.8844,Other months
2015-06-19,110.65,65.21,7.8,284.0,Poor,48,8.3,34.5,0.1,False,4.7064,Other months
2015-06-20,80.31,52.7,10.22,239.0,Poor,58,17.0,32.7,1.1,False,4.3859,Other months
2015-06-21,59.73,50.78,6.11,149.0,Moderate,62,11.8,32.1,1.7,False,4.0898,Other months
2015-06-22,85.4,58.88,6.18,172.0,Moderate,62,10.5,31.9,0.6,False,4.4473,Other months
2015-06-23,101.99,61.18,7.9,226.0,Poor,56,8.3,33.1,0.0,False,4.6249,Other months
2015-06-24,126.07,60.31,8.09,261.0,Poor,70,7.4,31.1,16.8,False,4.8368,Other months
2015-06-25,37.59,44.72,7.67,188.0,Moderate,92,7.9,26.1,32.6,False,3.6267,Other months
2015-06-26,76.0,46.88,6.84,192.0,Moderate,70,10.6,29.8,0.0,False,4.3307,Other months
2015-06-27,69.46,38.55,7.28,207.0,Poor,66,13.3,31.5,0.0,False,4.2408,Other months
2015-06-28,79.84,47.19,7.53,219.0,Poor,64,8.9,32.3,0.4,False,4.38,Other months
2015-06-29,48.5,38.37,7.74,193.0,Moderate,67,15.0,30.4,0.0,False,3.8816,Other months
2015-06-30,53.79,46.06,9.15,170.0,Moderate,68,8.0,28.8,0.4,False,3.9851,Other months
2015-07-01,57.99,49.64,8.88,185.0,Moderate,70,5.3,30.0,0.8,False,4.0603,Monsoon (Jul–Sep)
2015-07-02,67.12,52.45,6.86,220.0,Poor,68,7.0,30.8,0.6,False,4.2065,Monsoon (Jul–Sep)
2015-07-03,65.25,37.09,8.91,225.0,Poor,64,12.5,32.0,0.3,False,4.1782,Monsoon (Jul–Sep)
2015-07-04,88.75,35.54,7.24,250.0,Poor,64,13.6,31.7,0.6,False,4.4858,Monsoon (Jul–Sep)
2015-07-05,135.92,36.89,6.42,282.0,Poor,68,12.3,31.5,12.3,False,4.9121,Monsoon (Jul–Sep)
2015-07-06,60.27,44.07,7.91,298.0,Poor,77,8.2,29.7,6.3,False,4.0988,Monsoon (Jul–Sep)
2015-07-07,52.2,51.7,7.82,175.0,Moderate,84,7.4,27.6,14.6,False,3.9551,Monsoon (Jul–Sep)
2015-07-08,67.92,52.69,7.94,217.0,Poor,84,6.0,28.2,16.5,False,4.2183,Monsoon (Jul–Sep)
2015-07-09,65.95,53.39,7.86,234.0,Poor,87,4.7,27.8,18.7,False,4.1889,Monsoon (Jul–Sep)
2015-07-10,47.68,46.71,8.97,188.0,Moderate,93,7.3,26.5,61.6,False,3.8645,Monsoon (Jul–Sep)
2015-07-11,29.08,51.39,8.61,253.0,Poor,91,12.5,24.8,44.1,False,3.3701,Monsoon (Jul–Sep)
2015-07-12,32.29,32.77,7.15,198.0,Moderate,89,10.9,25.4,6.4,False,3.4748,Monsoon (Jul–Sep)
2015-07-13,36.68,37.71,8.11,148.0,Moderate,80,7.0,27.9,1.6,False,3.6022,Monsoon (Jul–Sep)
2015-07-14,44.48,43.46,8.04,141.0,Moderate,77,13.4,29.4,0.8,False,3.795,Monsoon (Jul–Sep)
2015-07-15,63.79,38.05,9.62,218.0,Poor,70,15.4,30.8,0.0,False,4.1556,Monsoon (Jul–Sep)
2015-07-16,77.2,36.72,10.29,268.0,Poor,69,11.7,30.3,2.3,False,4.3464,Monsoon (Jul–Sep)
2015-07-17,77.99,42.07,12.46,232.0,Poor,86,8.0,28.1,35.2,False,4.3566,Monsoon (Jul–Sep)
2015-07-18,71.11,48.79,10.77,204.0,Poor,83,5.7,28.9,5.3,False,4.2642,Monsoon (Jul–Sep)
2015-07-19,67.39,52.87,10.4,220.0,Poor,84,6.0,28.6,12.5,False,4.2105,Monsoon (Jul–Sep)
2015-07-20,49.58,62.37,10.17,223.0,Poor,88,7.5,27.5,17.4,False,3.9036,Monsoon (Jul–Sep)
2015-07-21,40.97,46.3,12.19,218.0,Poor,81,9.7,28.8,3.4,False,3.7128,Monsoon (Jul–Sep)
2015-07-22,38.97,41.41,20.43,165.0,Moderate,82,10.1,29.0,1.8,False,3.6628,Monsoon (Jul–Sep)
2015-07-23,34.02,39.98,16.71,155.0,Moderate,76,12.5,29.4,0.3,False,3.5269,Monsoon (Jul–Sep)
2015-07-24,46.13,43.99,16.01,154.0,Moderate,80,9.8,28.8,5.6,False,3.8315,Monsoon (Jul–Sep)
2015-07-25,46.01,42.86,15.58,184.0,Moderate,81,12.1,28.7,3.2,False,3.8289,Monsoon (Jul–Sep)
2015-07-26,29.81,30.66,15.09,150.0,Moderate,77,24.3,28.1,1.6,False,3.3948,Monsoon (Jul–Sep)
2015-07-27,22.82,33.21,12.69,125.0,Moderate,75,15.6,27.6,0.0,False,3.1276,Monsoon (Jul–Sep)
2015-07-28,24.69,40.25,7.61,160.0,Moderate,75,13.3,27.7,0.2,False,3.2064,Monsoon (Jul–Sep)
2015-07-29,29.04,35.69,9.68,142.0,Moderate,74,17.0,27.4,0.0,False,3.3687,Monsoon (Jul–Sep)
2015-07-30,25.76,32.96,9.49,181.0,Moderate,79,13.7,27.6,2.1,False,3.2488,Monsoon (Jul–Sep)
2015-07-31,37.85,35.9,9.7,196.0,Moderate,76,11.4,27.8,0.5,False,3.6336,Monsoon (Jul–Sep)
2015-08-01,41.32,35.14,10.8,181.0,Moderate,84,6.7,26.8,5.5,False,3.7213,Monsoon (Jul–Sep)
2015-08-02,47.81,37.96,10.27,213.0,Poor,83,3.4,27.6,2.3,False,3.8672,Monsoon (Jul–Sep)
2015-08-03,56.02,40.17,8.75,175.0,Moderate,81,6.3,28.8,0.7,False,4.0257,Monsoon (Jul–Sep)
2015-08-04,54.46,46.74,9.72,184.0,Moderate,80,5.6,29.1,1.3,False,3.9975,Monsoon (Jul–Sep)
2015-08-05,59.13,52.78,10.41,228.0,Poor,87,4.9,28.5,7.2,False,4.0797,Monsoon (Jul–Sep)
2015-08-06,65.47,52.51,10.73,214.0,Poor,87,3.4,28.0,10.8,False,4.1816,Monsoon (Jul–Sep)
2015-08-07,64.58,48.24,10.22,254.0,Poor,89,6.3,27.6,8.4,False,4.1679,Monsoon (Jul–Sep)
2015-08-08,70.05,50.51,7.68,258.0,Poor,94,6.3,25.7,29.1,False,4.2492,Monsoon (Jul–Sep)
2015-08-09,55.51,39.47,5.83,244.0,Poor,93,6.4,25.9,53.0,False,4.0166,Monsoon (Jul–Sep)
2015-08-10,82.27,45.46,6.9,209.0,Poor,88,4.4,27.5,6.8,False,4.41,Monsoon (Jul–Sep)
2015-08-11,77.04,49.43,6.23,283.0,Poor,91,8.4,27.2,11.1,False,4.3443,Monsoon (Jul–Sep)
2015-08-12,52.45,45.71,6.69,223.0,Poor,83,7.9,28.3,0.5,False,3.9599,Monsoon (Jul–Sep)
2015-08-13,61.66,52.76,9.82,205.0,Poor,82,5.2,29.1,0.5,False,4.1216,Monsoon (Jul–Sep)
2015-08-14,65.67,50.96,10.82,252.0,Poor,85,5.7,28.7,6.4,False,4.1846,Monsoon (Jul–Sep)
2015-08-15,51.4,44.4,10.53,198.0,Moderate,88,5.2,27.9,11.1,False,3.9396,Monsoon (Jul–Sep)
2015-08-16,55.71,48.39,10.46,197.0,Moderate,89,3.5,27.3,6.5,False,4.0202,Monsoon (Jul–Sep)
2015-08-17,61.84,44.41,11.22,184.0,Moderate,83,4.6,28.7,0.3,False,4.1246,Monsoon (Jul–Sep)
2015-08-18,60.65,56.15,12.39,197.0,Moderate,84,7.5,28.9,3.2,False,4.1051,Monsoon (Jul–Sep)
2015-08-19,34.42,36.47,9.63,140.0,Moderate,78,12.4,29.0,1.8,False,3.5386,Monsoon (Jul–Sep)
2015-08-20,40.83,32.0,11.59,232.0,Poor,71,13.6,29.2,0.0,False,3.7094,Monsoon (Jul–Sep)
2015-08-21,50.97,35.87,12.09,271.0,Poor,73,9.7,28.5,0.3,False,3.9312,Monsoon (Jul–Sep)
2015-08-22,46.74,40.28,9.56,207.0,Poor,76,8.1,27.9,2.6,False,3.8446,Monsoon (Jul–Sep)
2015-08-23,44.67,33.76,9.53,127.0,Moderate,82,5.1,28.2,5.1,False,3.7993,Monsoon (Jul–Sep)
2015-08-24,37.39,44.61,10.67,123.0,Moderate,76,9.8,28.6,0.4,False,3.6214,Monsoon (Jul–Sep)
2015-08-25,52.06,39.88,9.12,175.0,Moderate,71,12.8,29.5,0.0,False,3.9524,Monsoon (Jul–Sep)
2015-08-26,57.52,37.85,9.36,245.0,Poor,72,10.5,30.0,0.0,False,4.0521,Monsoon (Jul–Sep)
2015-08-27,61.47,40.41,10.59,248.0,Poor,79,4.8,29.6,1.6,False,4.1185,Monsoon (Jul–Sep)
2015-08-28,77.76,50.74,11.92,247.0,Poor,82,5.7,29.2,0.7,False,4.3536,Monsoon (Jul–Sep)
2015-08-29,68.53,49.3,11.11,292.0,Poor,78,6.8,30.1,0.0,False,4.2273,Monsoon (Jul–Sep)
2015-08-30,57.85,39.84,10.39,266.0,Poor,75,8.5,30.1,0.2,False,4.0579,Monsoon (Jul–Sep)
2015-08-31,51.67,32.53,12.77,288.0,Poor,68,10.8,30.0,0.0,False,3.9449,Monsoon (Jul–Sep)
2015-09-01,73.78,27.42,10.45,210.0,Poor,63,11.7,29.4,0.0,False,4.3011,Monsoon (Jul–Sep)
2015-09-02,97.63,29.16,10.79,298.0,Poor,59,11.6,29.0,0.0,False,4.5812,Monsoon (Jul–Sep)
2015-09-03,99.5,35.31,9.82,315.0,Very Poor,57,10.3,29.1,0.0,False,4.6002,Monsoon (Jul–Sep)
2015-09-04,97.31,41.7,14.94,368.0,Very Poor,61,7.2,29.7,0.0,False,4.5779,Monsoon (Jul–Sep)
2015-09-05,76.43,29.5,16.93,266.0,Poor,60,11.0,28.8,0.0,False,4.3364,Monsoon (Jul–Sep)
2015-09-06,61.69,27.81,16.71,174.0,Moderate,57,9.9,28.7,0.0,False,4.1221,Monsoon (Jul–Sep)
2015-09-07,55.19,35.49,12.97,199.0,Moderate,55,10.7,29.0,0.0,False,4.0108,Monsoon (Jul–Sep)
2015-09-08,63.79,38.36,10.92,217.0,Poor,58,10.9,29.2,0.0,False,4.1556,Monsoon (Jul–Sep)
2015-09-09,58.48,36.2,11.57,238.0,Poor,56,11.3,29.4,0.0,False,4.0687,Monsoon (Jul–Sep)
2015-09-10,60.29,42.1,11.53,230.0,Poor,60,9.0,29.1,0.0,False,4.0992,Monsoon (Jul–Sep)
2015-09-11,67.35,46.81,10.98,218.0,Poor,61,7.6,28.9,0.0,False,4.2099,Monsoon (Jul–Sep)
2015-09-12,87.55,54.45,10.51,226.0,Poor,69,6.8,28.9,0.3,False,4.4722,Monsoon (Jul–Sep)
2015-09-13,84.57,45.36,9.91,202.0,Poor,69,5.7,29.9,0.0,False,4.4376,Monsoon (Jul–Sep)
2015-09-14,111.58,60.71,10.43,274.0,Poor,62,6.2,30.5,0.0,False,4.7147,Monsoon (Jul–Sep)
2015-09-15,108.78,56.31,10.4,289.0,Poor,63,6.6,30.2,0.0,False,4.6893,Monsoon (Jul–Sep)
2015-09-16,91.18,46.44,9.27,235.0,Poor,66,7.5,30.2,0.0,False,4.5128,Monsoon (Jul–Sep)
2015-09-17,104.85,60.96,11.68,285.0,Poor,72,6.8,29.6,0.4,False,4.6525,Monsoon (Jul–Sep)
2015-09-18,56.19,43.3,10.85,209.0,Poor,72,10.1,29.2,1.6,False,4.0287,Monsoon (Jul–Sep)
2015-09-19,67.62,49.83,9.75,132.0,Moderate,84,7.2,28.0,24.3,False,4.2139,Monsoon (Jul–Sep)
2015-09-20,64.38,62.73,9.27,179.0,Moderate,83,7.2,28.8,5.0,False,4.1648,Monsoon (Jul–Sep)
2015-09-21,45.65,62.69,13.55,136.0,Moderate,85,6.8,28.1,9.5,False,3.821,Monsoon (Jul–Sep)
2015-09-22,35.75,38.78,11.57,104.0,Moderate,79,11.9,28.5,2.0,False,3.5766,Monsoon (Jul–Sep)
2015-09-23,34.89,31.17,12.34,95.0,Satisfactory,75,12.2,27.0,0.3,False,3.5522,Monsoon (Jul–Sep)
2015-09-24,63.06,39.16,13.26,175.0,Moderate,67,14.0,26.9,0.0,False,4.1441,Monsoon (Jul–Sep)
2015-09-25,82.39,45.09,11.8,290.0,Poor,67,11.2,26.5,0.0,False,4.4115,Monsoon (Jul–Sep)
2015-09-26,88.08,45.96,11.17,282.0,Poor,66,8.1,27.0,0.0,False,4.4782,Monsoon (Jul–Sep)
2015-09-27,89.75,44.13,9.76,298.0,Poor,64,7.4,27.8,0.0,False,4.497,Monsoon (Jul–Sep)
2015-09-28,69.57,43.41,10.38,240.0,Poor,66,7.9,26.8,0.0,False,4.2423,Monsoon (Jul–Sep)
2015-09-29,68.34,48.19,10.68,188.0,Moderate,63,8.9,26.4,0.0,False,4.2245,Monsoon (Jul–Sep)
2015-09-30,61.08,42.91,9.59,187.0,Moderate,57,10.9,26.5,0.0,False,4.1122,Monsoon (Jul–Sep)
2015-10-01,85.7,54.68,11.42,230.0,Poor,60,7.6,26.2,0.0,False,4.4509,Other months
2015-10-02,97.62,52.53,9.77,286.0,Poor,57,8.5,26.4,0.0,False,4.5811,Other months
2015-10-03,103.58,54.93,11.41,266.0,Poor,57,7.6,27.4,0.0,False,4.6403,Other months
2015-10-04,145.97,62.84,15.08,369.0,Very Poor,57,5.5,28.0,0.0,False,4.9834,Other months
2015-10-05,180.52,75.42,17.32,375.0,Very Poor,55,6.0,28.3,0.0,False,5.1958,Other months
2015-10-06,151.57,65.07,11.35,411.0,Severe,53,7.6,28.3,0.0,False,5.021,Other months
2015-10-07,144.04,57.05,11.15,383.0,Very Poor,56,7.8,28.2,0.0,False,4.9701,Other months
2015-10-08,148.44,58.32,12.13,388.0,Very Poor,54,9.5,28.3,0.0,False,5.0002,Other months
2015-10-09,130.22,65.15,15.27,351.0,Very Poor,50,9.0,28.3,0.0,False,4.8692,Other months
2015-10-10,147.71,61.29,13.94,320.0,Very Poor,40,10.4,28.4,0.0,False,4.9953,Other months
2015-10-11,111.34,51.83,12.01,296.0,Poor,46,9.3,28.2,0.0,False,4.7126,Other months
2015-10-12,100.7,52.92,14.75,312.0,Very Poor,52,5.8,27.8,0.0,False,4.6121,Other months
2015-10-13,97.67,48.92,11.84,260.0,Poor,69,10.0,27.4,0.4,False,4.5816,Other months
2015-10-14,75.81,43.47,10.89,204.0,Poor,74,8.2,26.5,7.3,False,4.3282,Other months
2015-10-15,95.24,60.8,10.84,218.0,Poor,70,6.4,26.6,0.0,False,4.5564,Other months
2015-10-16,148.29,68.24,11.98,356.0,Very Poor,68,6.4,27.0,0.0,False,4.9992,Other months
2015-10-17,90.66,20.29,7.56,388.0,Very Poor,66,7.0,27.3,0.0,False,4.5071,Other months
2015-10-18,156.71,41.09,10.14,298.0,Poor,63,5.4,27.9,0.0,False,5.0544,Other months
2015-10-19,170.28,61.67,16.24,392.0,Very Poor,64,6.8,27.7,1.1,False,5.1374,Other months
2015-10-20,198.1,74.62,16.73,428.0,Severe,55,6.9,27.4,0.3,False,5.2888,Other months
2015-10-21,158.04,46.9,15.64,384.0,Very Poor,53,7.2,26.2,0.0,False,5.0628,Other months
2015-10-22,116.98,32.96,13.27,292.0,Poor,48,8.8,24.9,0.0,False,4.762,Other months
2015-10-23,143.73,67.38,21.35,343.0,Very Poor,49,8.6,24.2,0.0,False,4.9679,Other months
2015-10-24,169.22,71.38,18.2,383.0,Very Poor,51,5.4,25.0,0.0,False,5.1312,Other months
2015-10-25,147.65,56.46,13.81,374.0,Very Poor,52,11.4,25.6,0.0,False,4.9948,Other months
2015-10-26,101.61,47.8,20.57,263.0,Poor,57,9.6,24.9,1.5,False,4.6211,Other months
2015-10-27,113.2,49.25,21.2,334.0,Very Poor,54,6.2,24.0,0.0,False,4.7292,Other months
2015-10-28,112.89,43.78,18.61,333.0,Very Poor,72,7.2,20.5,5.5,False,4.7264,Other months
2015-10-29,95.72,57.74,24.29,262.0,Poor,65,5.8,20.9,0.0,False,4.5614,Other months
2015-10-30,108.4,42.63,18.92,236.0,Poor,71,5.5,21.4,0.0,False,4.6858,Other months
2015-10-31,245.97,35.11,17.66,340.0,Very Poor,66,4.8,22.2,0.0,False,5.5052,Other months
2015-11-01,277.53,60.17,28.58,415.0,Severe,64,4.7,23.5,0.0,False,5.6259,Winter (Nov–Jan)
2015-11-02,232.4,68.4,31.66,420.0,Severe,65,4.5,23.5,0.0,False,5.4485,Winter (Nov–Jan)
2015-11-03,244.78,82.74,29.19,407.0,Severe,67,5.5,23.2,0.0,False,5.5004,Winter (Nov–Jan)
2015-11-04,293.49,87.47,31.58,454.0,Severe,65,4.5,23.3,0.0,False,5.6818,Winter (Nov–Jan)
2015-11-05,161.78,63.78,21.21,388.0,Very Poor,67,9.8,23.0,0.2,False,5.0862,Winter (Nov–Jan)
2015-11-06,153.33,58.13,20.9,276.0,Poor,68,5.3,23.1,0.0,False,5.0326,Winter (Nov–Jan)
2015-11-07,353.86,86.59,19.96,483.0,Severe,73,4.2,22.4,0.0,False,5.8689,Winter (Nov–Jan)
2015-11-08,217.55,75.98,31.77,451.0,Severe,73,6.8,22.9,0.0,False,5.3824,Winter (Nov–Jan)
2015-11-09,201.44,79.2,40.75,378.0,Very Poor,69,6.3,23.0,0.0,False,5.3055,Winter (Nov–Jan)
2015-11-10,249.95,84.89,33.72,439.0,Severe,66,6.6,22.6,0.6,False,5.5213,Winter (Nov–Jan)
2015-11-11,219.68,55.72,25.96,431.0,Severe,54,10.8,22.1,0.0,False,5.3922,Winter (Nov–Jan)
2015-11-12,258.48,54.69,28.58,421.0,Severe,52,10.5,22.1,0.0,False,5.5548,Winter (Nov–Jan)
2015-11-13,291.66,61.66,21.15,454.0,Severe,59,8.9,22.6,0.0,False,5.6756,Winter (Nov–Jan)
2015-11-14,221.68,60.05,21.27,450.0,Severe,58,8.9,23.2,0.0,False,5.4012,Winter (Nov–Jan)
2015-11-15,214.24,83.62,22.68,367.0,Very Poor,56,4.9,23.1,0.0,False,5.3671,Winter (Nov–Jan)
2015-11-16,184.02,85.03,21.27,383.0,Very Poor,53,9.2,22.9,1.0,False,5.215,Winter (Nov–Jan)
2015-11-17,136.22,57.11,17.53,347.0,Very Poor,44,10.4,20.3,0.0,False,4.9143,Winter (Nov–Jan)
2015-11-18,188.09,74.39,21.78,369.0,Very Poor,47,8.4,19.0,0.0,False,5.2369,Winter (Nov–Jan)
2015-11-19,238.69,96.62,25.59,392.0,Very Poor,53,5.5,19.6,0.0,False,5.4752,Winter (Nov–Jan)
2015-11-20,271.42,101.44,26.81,455.0,Severe,62,5.7,19.3,0.0,False,5.6037,Winter (Nov–Jan)
2015-11-21,293.73,97.76,23.06,450.0,Severe,60,5.6,19.5,0.0,False,5.6827,Winter (Nov–Jan)
2015-11-22,247.27,92.32,20.77,478.0,Severe,62,6.0,19.1,0.0,False,5.5105,Winter (Nov–Jan)
2015-11-23,266.95,105.29,24.92,431.0,Severe,62,5.3,18.8,0.0,False,5.5871,Winter (Nov–Jan)
2015-11-24,241.61,88.74,19.65,440.0,Severe,56,8.5,19.3,0.0,False,5.4873,Winter (Nov–Jan)
2015-11-25,149.14,54.63,15.97,376.0,Very Poor,50,11.4,19.6,0.0,False,5.0049,Winter (Nov–Jan)
2015-11-26,182.5,69.29,21.35,347.0,Very Poor,50,6.5,19.9,0.0,False,5.2068,Winter (Nov–Jan)
2015-11-27,193.58,71.35,19.49,343.0,Very Poor,69,7.3,19.3,0.0,False,5.2657,Winter (Nov–Jan)
2015-11-28,172.89,47.21,17.09,362.0,Very Poor,68,9.6,19.9,0.0,False,5.1527,Winter (Nov–Jan)
2015-11-29,190.46,51.84,20.73,319.0,Very Poor,67,5.6,19.6,0.0,False,5.2494,Winter (Nov–Jan)
2015-11-30,282.76,78.48,24.51,425.0,Severe,72,5.4,20.9,0.0,False,5.6446,Winter (Nov–Jan)
2015-12-01,183.28,83.03,16.48,400.0,Very Poor,69,6.3,20.7,0.0,False,5.211,Winter (Nov–Jan)
2015-12-02,170.74,95.99,19.04,386.0,Very Poor,64,7.0,19.6,0.0,False,5.1401,Winter (Nov–Jan)
2015-12-03,190.14,92.91,19.24,385.0,Very Poor,65,9.9,18.2,0.0,False,5.2478,Winter (Nov–Jan)
2015-12-04,186.64,79.52,20.76,392.0,Very Poor,63,10.6,18.5,0.0,False,5.2292,Winter (Nov–Jan)
2015-12-05,282.01,121.11,31.36,428.0,Severe,67,4.8,17.8,0.0,False,5.6419,Winter (Nov–Jan)
2015-12-06,218.22,113.45,34.05,394.0,Very Poor,67,4.9,18.3,0.0,False,5.3855,Winter (Nov–Jan)
2015-12-07,249.8,103.77,22.34,440.0,Severe,71,6.1,18.5,0.0,False,5.5207,Winter (Nov–Jan)
2015-12-08,283.59,140.09,23.41,437.0,Severe,70,6.2,18.6,0.0,False,5.6475,Winter (Nov–Jan)
2015-12-09,250.69,93.99,21.72,431.0,Severe,72,9.6,18.3,0.0,False,5.5242,Winter (Nov–Jan)
2015-12-10,211.95,78.05,22.11,383.0,Very Poor,73,9.0,19.3,0.2,False,5.3564,Winter (Nov–Jan)
2015-12-11,198.38,64.21,18.41,377.0,Very Poor,65,7.8,17.7,0.0,False,5.2902,Winter (Nov–Jan)
2015-12-12,184.12,55.01,16.09,379.0,Very Poor,65,9.8,14.7,0.0,False,5.2156,Winter (Nov–Jan)
2015-12-13,135.42,63.9,18.89,333.0,Very Poor,63,8.5,14.2,0.0,False,4.9084,Winter (Nov–Jan)
2015-12-14,118.6,59.09,13.66,314.0,Very Poor,53,10.7,13.7,0.0,False,4.7758,Winter (Nov–Jan)
2015-12-15,88.3,40.52,14.88,174.0,Moderate,52,11.0,13.6,0.0,False,4.4807,Winter (Nov–Jan)
2015-12-16,111.45,34.44,14.56,244.0,Poor,57,6.2,12.9,0.0,False,4.7136,Winter (Nov–Jan)
2015-12-17,152.24,23.07,19.41,308.0,Very Poor,63,6.9,13.2,0.0,False,5.0255,Winter (Nov–Jan)
2015-12-18,136.75,25.24,19.87,320.0,Very Poor,62,9.6,13.3,0.0,False,4.9182,Winter (Nov–Jan)
2015-12-19,114.35,26.84,13.17,270.0,Poor,60,8.5,13.6,0.0,False,4.7393,Winter (Nov–Jan)
2015-12-20,181.67,111.18,18.97,320.0,Very Poor,62,5.6,13.2,0.0,False,5.2022,Winter (Nov–Jan)
2015-12-21,135.78,78.99,15.59,313.0,Very Poor,63,5.2,13.2,0.0,False,4.911,Winter (Nov–Jan)
2015-12-22,204.72,136.15,23.64,326.0,Very Poor,68,4.3,13.4,0.0,False,5.3216,Winter (Nov–Jan)
2015-12-23,321.52,102.69,22.66,459.0,Severe,67,7.6,12.9,0.0,False,5.7731,Winter (Nov–Jan)
2015-12-24,129.08,55.01,13.43,314.0,Very Poor,59,12.0,12.9,0.0,False,4.8604,Winter (Nov–Jan)
2015-12-25,132.56,71.91,17.57,304.0,Very Poor,53,10.6,12.1,0.0,False,4.887,Winter (Nov–Jan)
2015-12-26,158.69,88.96,21.02,310.0,Very Poor,49,11.7,13.7,0.0,False,5.067,Winter (Nov–Jan)
2015-12-27,187.01,90.57,21.41,370.0,Very Poor,55,11.8,15.4,0.0,False,5.2312,Winter (Nov–Jan)
2015-12-28,148.77,75.69,20.34,328.0,Very Poor,54,13.4,17.1,0.0,False,5.0024,Winter (Nov–Jan)
2015-12-29,159.67,73.11,21.23,331.0,Very Poor,54,13.2,17.0,0.0,False,5.0731,Winter (Nov–Jan)
2015-12-30,233.97,87.4,22.31,412.0,Severe,61,7.7,16.2,0.0,False,5.4552,Winter (Nov–Jan)
2015-12-31,240.97,72.93,24.08,433.0,Severe,66,7.4,15.3,0.0,False,5.4847,Winter (Nov–Jan)
2016-01-01,295.71,94.04,23.57,463.0,Severe,68,6.1,14.9,0.0,False,5.6894,Winter (Nov–Jan)
2016-01-02,239.21,81.22,23.33,465.0,Severe,66,7.8,14.4,0.0,False,5.4773,Winter (Nov–Jan)
2016-01-03,270.1,76.67,19.94,426.0,Severe,63,10.2,14.9,0.0,False,5.5988,Winter (Nov–Jan)
2016-01-04,339.8,133.95,27.9,496.0,Severe,66,6.0,16.0,0.0,False,5.8284,Winter (Nov–Jan)
2016-01-05,318.1,118.81,30.24,528.0,Severe,69,5.6,18.0,0.0,False,5.7624,Winter (Nov–Jan)
2016-01-06,305.51,103.78,25.78,538.0,Severe,75,7.9,18.2,0.5,False,5.722,Winter (Nov–Jan)
2016-01-07,391.54,96.36,26.47,535.0,Severe,75,5.8,17.8,0.0,False,5.9701,Winter (Nov–Jan)
2016-01-08,339.87,67.85,14.19,603.0,Severe,75,9.1,17.1,0.0,False,5.8286,Winter (Nov–Jan)
2016-01-09,158.43,60.63,17.94,408.0,Severe,63,13.0,15.7,0.0,False,5.0653,Winter (Nov–Jan)
2016-01-10,183.24,68.86,24.96,368.0,Very Poor,68,7.8,15.6,0.0,False,5.2108,Winter (Nov–Jan)
2016-01-11,227.13,76.4,23.98,404.0,Severe,72,5.9,16.1,0.0,False,5.4255,Winter (Nov–Jan)
2016-01-12,195.21,78.61,24.06,444.0,Severe,71,9.5,16.5,0.0,False,5.2741,Winter (Nov–Jan)
2016-01-13,248.59,73.18,16.73,356.0,Very Poor,76,6.3,16.0,0.0,False,5.5158,Winter (Nov–Jan)
2016-01-14,196.87,55.91,11.82,397.0,Very Poor,77,5.3,14.4,0.0,False,5.2825,Winter (Nov–Jan)
2016-01-15,178.8,45.85,10.86,371.0,Very Poor,75,8.8,13.3,0.0,False,5.1863,Winter (Nov–Jan)
2016-01-16,138.86,41.92,11.25,311.0,Very Poor,74,10.3,13.1,0.0,False,4.9335,Winter (Nov–Jan)
2016-01-17,179.48,58.56,15.89,321.0,Very Poor,77,4.3,12.8,0.0,False,5.1901,Winter (Nov–Jan)
2016-01-18,269.05,78.22,15.42,424.0,Severe,78,5.0,12.6,0.0,False,5.5949,Winter (Nov–Jan)
2016-01-19,278.2,61.04,12.59,435.0,Severe,75,6.2,12.6,0.0,False,5.6283,Winter (Nov–Jan)
2016-01-20,272.1,56.67,14.75,455.0,Severe,73,7.6,12.2,0.0,False,5.6062,Winter (Nov–Jan)
2016-01-21,196.83,52.83,11.99,398.0,Very Poor,75,8.9,11.6,0.0,False,5.2823,Winter (Nov–Jan)
2016-01-22,290.66,73.9,17.13,399.0,Very Poor,76,6.1,11.5,0.0,False,5.6722,Winter (Nov–Jan)
2016-01-23,294.3,78.21,16.81,469.0,Severe,77,5.9,12.3,0.0,False,5.6846,Winter (Nov–Jan)
2016-01-24,303.5,64.55,14.74,488.0,Severe,78,6.6,12.1,0.0,False,5.7154,Winter (Nov–Jan)
2016-01-25,217.05,66.89,16.09,401.0,Severe,80,6.9,10.7,0.0,False,5.3801,Winter (Nov–Jan)
2016-01-26,308.75,80.14,17.97,446.0,Severe,75,4.3,13.0,0.0,False,5.7325,Winter (Nov–Jan)
2016-01-27,255.94,87.93,17.09,456.0,Severe,74,5.2,15.7,0.0,False,5.5449,Winter (Nov–Jan)
2016-01-28,283.03,90.45,23.63,451.0,Severe,72,8.0,15.7,0.0,False,5.6456,Winter (Nov–Jan)
2016-01-29,311.08,117.07,29.99,501.0,Severe,72,5.5,17.1,0.2,False,5.7401,Winter (Nov–Jan)
2016-01-30,285.83,111.19,27.94,505.0,Severe,73,5.7,19.4,0.5,False,5.6554,Winter (Nov–Jan)
2016-01-31,242.05,46.17,12.4,437.0,Severe,77,10.7,17.4,0.0,False,5.4891,Winter (Nov–Jan)
2016-02-01,121.4,60.12,16.33,305.0,Very Poor,65,10.0,15.1,0.0,False,4.7991,Other months
2016-02-02,135.31,63.6,19.08,292.0,Poor,58,9.6,14.2,0.0,False,4.9076,Other months
2016-02-03,136.87,61.81,24.23,306.0,Very Poor,53,12.4,14.4,0.0,False,4.919,Other months
2016-02-04,130.76,67.45,23.7,300.0,Poor,52,11.0,14.8,0.0,False,4.8734,Other months
2016-02-05,206.72,86.15,30.2,371.0,Very Poor,58,8.6,14.7,0.0,False,5.3314,Other months
2016-02-06,224.94,85.86,26.22,408.0,Severe,59,7.9,15.8,0.0,False,5.4158,Other months
2016-02-07,170.45,72.61,20.74,343.0,Very Poor,74,9.0,15.4,4.0,False,5.1384,Other months
2016-02-08,119.57,57.0,19.21,301.0,Very Poor,74,7.5,15.0,0.0,False,4.7839,Other months
2016-02-09,181.76,65.45,19.53,322.0,Very Poor,69,8.3,15.9,0.0,False,5.2027,Other months
2016-02-10,216.55,81.98,21.61,368.0,Very Poor,67,6.1,16.3,0.0,False,5.3778,Other months
2016-02-11,150.0,70.99,21.25,349.0,Very Poor,56,9.8,17.6,0.0,False,5.0106,Other months
2016-02-12,146.03,79.43,26.86,334.0,Very Poor,65,5.4,16.6,0.0,False,4.9838,Other months
2016-02-13,110.89,56.05,20.94,333.0,Very Poor,62,10.0,16.1,0.7,False,4.7085,Other months
2016-02-14,103.57,61.73,29.71,257.0,Poor,65,9.4,15.9,0.0,False,4.6402,Other months
2016-02-15,115.7,66.8,27.44,265.0,Poor,60,7.7,15.7,0.0,False,4.751,Other months
2016-02-16,123.22,65.75,29.19,297.0,Poor,55,7.2,15.8,0.0,False,4.814,Other months
2016-02-17,135.38,80.76,37.35,289.0,Poor,54,7.8,18.0,0.2,False,4.9081,Other months
2016-02-18,148.75,76.11,26.28,310.0,Very Poor,61,7.9,20.4,1.4,False,5.0023,Other months
2016-02-19,207.1,66.45,32.25,366.0,Very Poor,66,5.7,22.7,0.0,False,5.3332,Other months
2016-02-20,150.89,47.72,20.15,345.0,Very Poor,75,7.0,21.8,14.4,False,5.0166,Other months
2016-02-21,76.12,30.51,10.43,228.0,Poor,65,14.7,19.2,0.0,False,4.3323,Other months
2016-02-22,88.73,41.47,20.79,213.0,Poor,52,15.9,18.8,0.0,False,4.4856,Other months
2016-02-23,86.17,56.77,21.27,208.0,Poor,54,10.0,19.1,0.0,False,4.4563,Other months
2016-02-24,177.64,117.04,50.44,319.0,Very Poor,58,6.1,18.6,0.0,False,5.1798,Other months
2016-02-25,131.69,81.93,21.19,315.0,Very Poor,59,8.3,19.5,0.0,False,4.8805,Other months
2016-02-26,129.66,76.82,21.44,293.0,Poor,59,6.5,20.7,0.0,False,4.8649,Other months
2016-02-27,144.98,86.59,24.43,342.0,Very Poor,60,5.5,20.6,0.0,False,4.9766,Other months
2016-02-28,163.92,76.43,21.63,338.0,Very Poor,61,6.0,21.5,0.0,False,5.0994,Other months
2016-02-29,170.12,76.4,17.63,344.0,Very Poor,62,6.9,21.9,0.0,False,5.1365,Other months
2016-03-01,213.62,102.02,25.49,370.0,Very Poor,62,4.6,22.5,0.0,False,5.3642,Other months
2016-03-02,175.63,102.23,25.53,365.0,Very Poor,62,5.4,23.3,0.0,False,5.1684,Other months
2016-03-03,165.22,100.71,33.45,348.0,Very Poor,60,6.7,23.5,0.2,False,5.1073,Other months
2016-03-04,115.55,60.47,16.6,312.0,Very Poor,51,8.1,23.8,0.0,False,4.7497,Other months
2016-03-05,53.0,48.15,19.05,214.0,Poor,59,12.1,22.4,12.2,False,3.9703,Other months
2016-03-06,47.43,55.78,15.1,165.0,Moderate,75,9.9,20.2,2.6,False,3.8593,Other months
2016-03-07,98.61,54.69,20.44,218.0,Poor,69,6.6,21.3,0.0,False,4.5912,Other months
2016-03-08,84.42,43.9,26.24,230.0,Poor,66,8.9,21.7,0.0,False,4.4358,Other months
2016-03-09,109.16,49.75,31.56,248.0,Poor,62,8.9,21.5,0.0,False,4.6928,Other months
2016-03-10,129.9,60.19,26.69,276.0,Poor,62,8.5,22.5,0.0,False,4.8668,Other months
2016-03-11,85.76,30.44,9.58,213.0,Poor,65,9.3,23.3,2.2,False,4.4516,Other months
2016-03-12,60.17,15.89,8.04,127.0,Moderate,77,10.7,21.2,22.2,False,4.0972,Other months
2016-03-13,58.95,10.63,7.25,112.0,Moderate,71,11.9,21.2,0.0,False,4.0767,Other months
2016-03-14,51.82,38.11,18.53,111.0,Moderate,77,7.4,20.6,0.9,False,3.9478,Other months
2016-03-15,81.32,34.54,20.36,193.0,Moderate,66,7.3,20.8,0.0,False,4.3984,Other months
2016-03-16,67.63,36.61,17.04,123.0,Moderate,56,11.4,20.7,0.0,False,4.2141,Other months
2016-03-17,70.86,65.89,21.48,194.0,Moderate,56,9.6,22.8,0.1,False,4.2607,Other months
2016-03-18,72.47,64.64,27.7,186.0,Moderate,59,9.9,23.8,0.0,False,4.2832,Other months
2016-03-19,103.73,77.89,30.74,242.0,Poor,60,6.3,23.9,0.5,False,4.6418,Other months
2016-03-20,95.52,57.84,20.52,267.0,Poor,56,7.2,24.7,0.0,False,4.5593,Other months
2016-03-21,58.4,36.37,15.98,207.0,Poor,45,15.2,23.9,0.0,False,4.0673,Other months
2016-03-22,47.43,31.12,13.54,176.0,Moderate,36,19.8,22.4,0.0,False,3.8593,Other months
2016-03-23,80.01,50.45,22.15,189.0,Moderate,39,13.7,23.5,0.0,False,4.3822,Other months
2016-03-24,156.01,88.44,24.44,341.0,Very Poor,47,6.6,25.0,0.0,False,5.0499,Other months
2016-03-25,137.99,85.91,32.84,325.0,Very Poor,50,7.9,26.5,0.0,False,4.9272,Other months
2016-03-26,72.44,42.51,23.86,259.0,Poor,53,13.0,25.2,0.0,False,4.2828,Other months
2016-03-27,61.75,37.18,18.09,178.0,Moderate,45,11.1,24.7,0.0,False,4.1231,Other months
2016-03-28,81.46,53.01,25.75,219.0,Poor,41,9.5,24.4,0.0,False,4.4001,Other months
2016-03-29,89.75,48.72,42.34,206.0,Poor,42,9.9,25.2,0.0,False,4.497,Other months
2016-03-30,88.68,46.74,36.91,221.0,Poor,45,6.1,26.5,0.0,False,4.485,Other months
2016-03-31,127.86,61.21,19.64,298.0,Poor,40,6.9,28.0,0.0,False,4.8509,Other months
2016-04-01,130.7,15.89,12.78,316.0,Very Poor,39,10.9,29.2,0.0,False,4.8729,Other months
2016-04-02,118.44,18.29,16.35,294.0,Poor,41,7.4,29.9,0.0,False,4.7744,Other months
2016-04-03,148.22,44.98,27.44,314.0,Very Poor,44,6.7,31.2,1.8,False,4.9987,Other months
2016-04-04,132.86,31.55,20.54,334.0,Very Poor,34,8.8,30.1,0.0,False,4.8893,Other months
2016-04-05,97.83,20.15,18.86,261.0,Poor,37,11.7,29.0,0.0,False,4.5832,Other months
2016-04-06,91.82,52.54,31.06,208.0,Poor,30,7.6,28.4,0.0,False,4.5198,Other months
2016-04-07,129.61,58.6,35.57,289.0,Poor,37,11.1,27.1,0.0,False,4.8645,Other months
2016-04-08,89.78,53.55,48.86,216.0,Poor,38,6.2,27.1,0.0,False,4.4974,Other months
2016-04-09,166.76,63.03,46.97,314.0,Very Poor,27,8.2,28.9,0.0,False,5.1166,Other months
2016-04-10,107.81,47.95,35.24,262.0,Poor,29,8.7,29.5,0.0,False,4.6804,Other months
2016-04-11,81.12,36.5,22.66,257.0,Poor,33,15.6,28.3,0.0,False,4.3959,Other months
2016-04-12,74.03,35.44,17.85,235.0,Poor,33,17.5,27.9,0.0,False,4.3045,Other months
2016-04-13,74.9,46.29,25.16,239.0,Poor,30,17.0,29.7,0.0,False,4.3162,Other months
2016-04-14,94.81,58.81,26.21,239.0,Poor,29,12.0,30.9,0.0,False,4.5519,Other months
2016-04-15,137.48,76.2,37.57,302.0,Very Poor,31,9.6,31.8,0.0,False,4.9235,Other months
2016-04-16,124.13,37.49,14.84,296.0,Poor,30,10.1,32.7,0.0,False,4.8213,Other months
2016-04-17,102.86,42.35,13.34,247.0,Poor,26,7.8,33.1,0.0,False,4.6334,Other months
2016-04-18,102.9,49.32,22.15,265.0,Poor,32,7.2,32.5,0.0,False,4.6338,Other months
2016-04-19,129.06,63.21,35.73,301.0,Very Poor,37,6.1,31.4,0.1,False,4.8603,Other months
2016-04-20,124.8,48.65,29.16,322.0,Very Poor,26,12.3,31.6,0.0,False,4.8267,Other months
2016-04-21,92.74,42.87,19.87,291.0,Poor,23,16.1,31.8,0.0,False,4.5298,Other months
2016-04-22,113.75,44.8,25.63,292.0,Poor,25,7.5,31.8,0.0,False,4.734,Other months
2016-04-23,89.52,50.78,25.65,258.0,Poor,24,11.7,29.6,0.0,False,4.4945,Other months
2016-04-24,123.59,69.92,40.96,282.0,Poor,21,10.2,28.8,0.0,False,4.817,Other months
2016-04-25,104.5,70.04,39.91,271.0,Poor,19,9.3,30.0,0.0,False,4.6492,Other months
2016-04-26,139.37,97.93,38.53,314.0,Very Poor,23,6.9,30.6,0.2,False,4.9371,Other months
2016-04-27,162.54,108.53,33.53,377.0,Very Poor,22,8.4,31.0,0.0,False,5.0909,Other months
2016-04-28,161.23,80.4,35.7,390.0,Very Poor,19,10.5,31.4,0.0,False,5.0828,Other months
2016-04-29,181.49,88.26,38.0,392.0,Very Poor,19,9.8,31.3,0.0,False,5.2012,Other months
2016-04-30,142.64,51.53,13.83,342.0,Very Poor,21,8.3,31.2,0.0,False,4.9603,Other months
2016-05-01,124.21,52.3,10.98,297.0,Poor,20,10.7,32.8,0.0,False,4.822,Other months
2016-05-02,119.47,41.26,10.0,275.0,Poor,19,7.1,34.4,0.4,False,4.7831,Other months
2016-05-03,125.36,59.73,21.42,281.0,Poor,32,10.3,32.1,1.6,False,4.8312,Other months
2016-05-04,103.08,61.77,26.13,309.0,Very Poor,48,12.9,30.9,1.0,False,4.6355,Other months
2016-05-05,65.02,46.27,18.35,262.0,Poor,50,13.0,29.3,0.1,False,4.1747,Other months
2016-05-06,54.34,55.07,20.23,194.0,Moderate,54,5.5,29.2,0.0,False,3.9953,Other months
2016-05-07,77.89,66.68,20.15,229.0,Poor,41,6.6,30.8,0.0,False,4.3553,Other months
2016-05-08,90.19,64.2,25.25,246.0,Poor,45,10.3,30.8,0.0,False,4.5019,Other months
2016-05-09,77.34,48.67,18.97,225.0,Poor,42,13.3,32.1,0.5,False,4.3482,Other months
2016-05-10,73.55,57.52,22.26,221.0,Poor,46,13.1,32.2,1.0,False,4.298,Other months
2016-05-11,66.49,52.3,16.32,185.0,Moderate,51,10.8,31.7,0.2,False,4.1971,Other months
2016-05-12,100.09,64.25,17.95,218.0,Poor,49,6.7,32.5,0.0,False,4.6061,Other months
2016-05-13,99.88,60.29,16.54,310.0,Very Poor,30,7.3,34.5,0.0,False,4.604,Other months
2016-05-14,105.51,67.71,20.49,307.0,Very Poor,30,6.9,34.9,0.0,False,4.6588,Other months
2016-05-15,128.85,57.06,18.7,325.0,Very Poor,29,7.3,34.9,0.0,False,4.8586,Other months
2016-05-16,94.89,58.46,21.19,316.0,Very Poor,25,10.0,35.2,0.0,False,4.5527,Other months
2016-05-17,92.95,62.4,27.34,302.0,Very Poor,22,10.6,35.1,0.0,False,4.5321,Other months
2016-05-18,117.64,80.57,31.96,318.0,Very Poor,23,6.9,35.3,0.0,False,4.7676,Other months
2016-05-19,94.22,67.73,27.98,300.0,Poor,36,13.7,34.8,0.3,False,4.5456,Other months
2016-05-20,70.86,52.02,12.82,246.0,Poor,43,14.5,34.6,0.3,False,4.2607,Other months
2016-05-21,78.02,48.23,13.08,255.0,Poor,53,14.7,33.9,0.0,False,4.357,Other months
2016-05-22,66.3,53.42,15.3,218.0,Poor,47,10.3,34.6,1.8,False,4.1942,Other months
2016-05-23,87.31,45.86,16.69,252.0,Poor,52,10.1,33.6,4.5,False,4.4695,Other months
2016-05-24,57.35,43.57,13.46,190.0,Moderate,59,10.6,31.7,1.8,False,4.0492,Other months
2016-05-25,105.02,50.77,13.98,256.0,Poor,53,7.9,31.6,0.6,False,4.6542,Other months
2016-05-26,111.22,48.12,11.79,311.0,Very Poor,49,6.7,32.9,0.0,False,4.7115,Other months
2016-05-27,180.71,50.38,13.73,381.0,Very Poor,37,12.0,34.8,2.0,False,5.1969,Other months
2016-05-28,109.82,34.37,15.48,409.0,Severe,37,13.4,33.9,2.3,False,4.6988,Other months
2016-05-29,42.67,35.71,10.6,269.0,Poor,54,12.7,31.2,6.9,False,3.7535,Other months
2016-05-30,56.87,50.18,11.3,187.0,Moderate,68,10.5,28.8,3.4,False,4.0408,Other months
2016-05-31,101.54,49.41,9.15,225.0,Poor,57,7.7,31.7,0.2,False,4.6205,Other months
2016-06-01,76.56,44.55,13.11,283.0,Poor,48,8.2,33.8,0.0,False,4.3381,Other months
2016-06-02,81.4,49.88,13.87,316.0,Very Poor,37,9.6,34.9,0.0,False,4.3994,Other months
2016-06-03,138.97,74.99,21.41,361.0,Very Poor,42,7.2,34.2,0.5,False,4.9343,Other months
2016-06-04,137.81,75.26,15.4,330.0,Very Poor,45,8.5,35.3,0.0,False,4.9259,Other months
2016-06-05,77.72,36.69,11.7,256.0,Poor,55,13.1,34.4,3.3,False,4.3531,Other months
2016-06-06,84.61,45.47,14.68,237.0,Poor,53,12.7,34.1,2.6,False,4.4381,Other months
2016-06-07,66.72,45.5,15.9,246.0,Poor,52,12.4,34.1,1.1,False,4.2005,Other months
2016-06-08,64.08,57.31,19.95,202.0,Poor,51,10.6,33.9,0.7,False,4.1601,Other months
2016-06-09,64.95,49.67,15.09,209.0,Poor,51,11.2,34.4,0.2,False,4.1736,Other months
2016-06-10,75.75,51.75,18.14,262.0,Poor,50,7.8,34.4,2.6,False,4.3274,Other months
2016-06-11,69.25,38.84,9.83,280.0,Poor,50,10.1,34.2,0.1,False,4.2377,Other months
2016-06-12,70.71,40.04,9.78,279.0,Poor,53,9.6,33.3,3.6,False,4.2586,Other months
2016-06-13,96.72,34.52,10.14,357.0,Very Poor,47,11.4,34.4,0.7,False,4.5718,Other months
2016-06-14,59.02,38.55,8.29,266.0,Poor,61,10.1,32.3,1.8,False,4.0779,Other months
2016-06-15,102.42,37.74,11.23,330.0,Very Poor,65,6.6,31.7,1.5,False,4.6291,Other months
2016-06-16,62.37,30.44,9.89,248.0,Poor,61,14.6,32.4,0.0,False,4.1331,Other months
2016-06-17,67.76,41.27,10.43,172.0,Moderate,62,11.2,32.6,0.2,False,4.216,Other months
2016-06-18,79.17,33.98,8.64,234.0,Poor,67,12.4,31.4,14.8,False,4.3716,Other months
2016-06-19,101.31,32.55,9.51,201.0,Poor,64,12.5,32.3,0.3,False,4.6182,Other months
2016-06-20,83.1,40.24,11.24,206.0,Poor,63,13.3,32.8,0.0,False,4.42,Other months
2016-06-21,72.33,32.04,10.54,159.0,Moderate,72,13.1,30.8,1.8,False,4.2812,Other months
2016-06-22,75.14,31.89,7.88,187.0,Moderate,69,8.0,30.9,1.4,False,4.3194,Other months
2016-06-23,91.63,37.7,8.34,228.0,Poor,63,6.5,32.8,0.0,False,4.5178,Other months
2016-06-24,100.02,45.29,9.03,284.0,Poor,58,7.8,33.8,0.6,False,4.6054,Other months
2016-06-25,67.12,50.91,10.87,310.0,Very Poor,59,12.6,34.2,0.0,False,4.2065,Other months
2016-06-26,48.0,40.57,8.71,158.0,Moderate,65,12.0,32.3,3.1,False,3.8712,Other months
2016-06-27,76.76,37.28,7.63,154.0,Moderate,67,9.5,32.1,3.3,False,4.3407,Other months
2016-06-28,80.89,40.07,9.77,187.0,Moderate,77,9.6,30.1,10.4,False,4.3931,Other months
2016-06-29,60.67,37.01,10.22,180.0,Moderate,70,9.2,32.0,10.5,False,4.1054,Other months
2016-06-30,69.65,34.17,9.43,190.0,Moderate,66,7.0,33.1,0.4,False,4.2435,Other months
2016-07-01,58.21,29.28,7.97,164.0,Moderate,73,10.8,31.8,23.3,False,4.0641,Monsoon (Jul–Sep)
2016-07-02,57.24,33.9,7.81,148.0,Moderate,86,8.4,27.7,67.9,False,4.0473,Monsoon (Jul–Sep)
2016-07-03,67.6,36.79,8.77,154.0,Moderate,91,7.8,26.9,15.1,False,4.2136,Monsoon (Jul–Sep)
2016-07-04,57.1,37.93,8.88,160.0,Moderate,81,4.2,28.8,1.2,False,4.0448,Monsoon (Jul–Sep)
2016-07-05,68.71,47.24,8.51,165.0,Moderate,75,5.5,31.0,0.3,False,4.2299,Monsoon (Jul–Sep)
2016-07-06,77.71,34.78,7.6,210.0,Poor,79,7.4,30.0,2.6,False,4.353,Monsoon (Jul–Sep)
2016-07-07,54.5,27.69,8.73,158.0,Moderate,76,8.7,30.3,1.5,False,3.9982,Monsoon (Jul–Sep)
2016-07-08,54.96,42.07,8.38,172.0,Moderate,76,6.1,30.8,2.5,False,4.0066,Monsoon (Jul–Sep)
2016-07-09,52.95,30.77,7.73,151.0,Moderate,76,7.8,30.5,1.3,False,3.9693,Monsoon (Jul–Sep)
2016-07-10,59.13,35.91,7.94,143.0,Moderate,75,5.6,31.1,0.0,False,4.0797,Monsoon (Jul–Sep)
2016-07-11,60.92,33.57,7.74,156.0,Moderate,82,9.4,29.3,4.3,False,4.1096,Monsoon (Jul–Sep)
2016-07-12,39.32,32.55,9.06,108.0,Moderate,83,9.8,29.0,15.6,False,3.6717,Monsoon (Jul–Sep)
2016-07-13,71.53,31.96,8.23,163.0,Moderate,80,7.8,29.4,3.9,False,4.2701,Monsoon (Jul–Sep)
2016-07-14,73.51,29.7,7.39,247.0,Poor,86,4.3,29.0,22.2,False,4.2974,Monsoon (Jul–Sep)
2016-07-15,52.88,29.17,6.58,123.0,Moderate,89,5.8,28.0,31.3,False,3.968,Monsoon (Jul–Sep)
2016-07-16,50.99,22.38,7.18,106.0,Moderate,95,5.3,26.5,75.4,False,3.9316,Monsoon (Jul–Sep)
2016-07-17,75.93,15.75,7.0,202.0,Poor,94,9.1,26.0,50.8,False,4.3298,Monsoon (Jul–Sep)
2016-07-18,44.08,32.85,7.31,120.0,Moderate,85,8.1,28.2,5.7,False,3.786,Monsoon (Jul–Sep)
2016-07-19,42.14,31.4,6.78,135.0,Moderate,78,11.6,29.6,1.9,False,3.741,Monsoon (Jul–Sep)
2016-07-20,56.86,34.96,9.36,245.0,Poor,70,12.0,30.8,0.0,False,4.0406,Monsoon (Jul–Sep)
2016-07-21,45.64,37.8,7.27,280.0,Poor,69,10.4,31.2,0.5,False,3.8208,Monsoon (Jul–Sep)
2016-07-22,48.36,37.42,8.63,269.0,Poor,73,6.0,30.9,0.6,False,3.8787,Monsoon (Jul–Sep)
2016-07-23,42.09,23.88,7.23,163.0,Moderate,81,9.7,28.8,5.0,False,3.7398,Monsoon (Jul–Sep)
2016-07-24,59.4,56.56,8.91,,,83,6.0,28.8,3.1,False,4.0843,Monsoon (Jul–Sep)
2016-07-25,76.29,58.4,7.93,195.0,Moderate,84,4.8,29.2,7.4,False,4.3345,Monsoon (Jul–Sep)
2016-07-26,54.5,40.48,8.2,163.0,Moderate,87,12.2,28.0,4.2,False,3.9982,Monsoon (Jul–Sep)
2016-07-27,40.55,40.86,10.82,108.0,Moderate,86,12.1,27.2,6.5,False,3.7025,Monsoon (Jul–Sep)
2016-07-28,46.44,42.81,9.95,134.0,Moderate,89,7.1,26.7,18.9,False,3.8382,Monsoon (Jul–Sep)
2016-07-29,56.16,44.18,9.87,155.0,Moderate,94,6.5,25.8,18.7,False,4.0282,Monsoon (Jul–Sep)
2016-07-30,42.7,36.78,8.69,116.0,Moderate,90,6.4,26.6,8.3,False,3.7542,Monsoon (Jul–Sep)
2016-07-31,48.03,32.5,8.01,136.0,Moderate,89,5.9,26.8,7.6,False,3.8718,Monsoon (Jul–Sep)
2016-08-01,43.47,29.86,10.33,150.0,Moderate,89,9.9,26.9,12.5,False,3.7721,Monsoon (Jul–Sep)
2016-08-02,43.55,34.87,8.23,121.0,Moderate,86,10.8,27.5,10.6,False,3.7739,Monsoon (Jul–Sep)
2016-08-03,50.86,36.14,6.96,149.0,Moderate,79,9.8,29.2,0.0,False,3.9291,Monsoon (Jul–Sep)
2016-08-04,49.04,35.93,9.03,178.0,Moderate,79,9.6,29.6,4.8,False,3.8926,Monsoon (Jul–Sep)
2016-08-05,39.3,33.68,9.36,120.0,Moderate,80,7.8,30.1,1.1,False,3.6712,Monsoon (Jul–Sep)
2016-08-06,43.86,38.29,9.81,140.0,Moderate,85,11.9,28.6,1.0,False,3.781,Monsoon (Jul–Sep)
2016-08-07,42.84,31.42,10.02,142.0,Moderate,80,9.8,28.9,2.7,False,3.7575,Monsoon (Jul–Sep)
2016-08-08,44.04,34.27,8.48,141.0,Moderate,81,11.3,29.0,4.7,False,3.7851,Monsoon (Jul–Sep)
2016-08-09,41.29,29.05,8.02,125.0,Moderate,85,11.1,27.8,6.3,False,3.7206,Monsoon (Jul–Sep)
2016-08-10,39.28,30.76,9.75,127.0,Moderate,88,11.1,27.3,10.5,False,3.6707,Monsoon (Jul–Sep)
2016-08-11,30.66,29.78,8.37,119.0,Moderate,90,7.5,26.8,14.1,False,3.423,Monsoon (Jul–Sep)
2016-08-12,42.15,34.9,8.73,111.0,Moderate,89,5.0,27.2,11.9,False,3.7412,Monsoon (Jul–Sep)
2016-08-13,56.45,43.49,7.77,132.0,Moderate,88,3.5,27.8,11.4,False,4.0334,Monsoon (Jul–Sep)
2016-08-14,40.81,42.53,12.53,149.0,Moderate,89,6.5,27.7,13.9,False,3.7089,Monsoon (Jul–Sep)
2016-08-15,39.51,32.96,8.87,166.0,Moderate,80,11.1,29.0,2.6,False,3.6766,Monsoon (Jul–Sep)
2016-08-16,49.04,28.74,7.97,274.0,Poor,73,13.5,29.4,0.8,False,3.8926,Monsoon (Jul–Sep)
2016-08-17,62.19,36.46,11.16,295.0,Poor,76,6.8,28.1,0.2,False,4.1302,Monsoon (Jul–Sep)
2016-08-18,55.55,51.48,9.22,219.0,Poor,87,4.7,27.7,7.1,False,4.0173,Monsoon (Jul–Sep)
2016-08-19,59.03,43.97,8.84,169.0,Moderate,82,6.1,28.9,1.3,False,4.078,Monsoon (Jul–Sep)
2016-08-20,48.57,35.84,8.56,174.0,Moderate,80,13.6,28.6,2.9,False,3.883,Monsoon (Jul–Sep)
2016-08-21,28.01,27.58,9.02,111.0,Moderate,78,12.0,27.9,0.0,False,3.3326,Monsoon (Jul–Sep)
2016-08-22,28.6,31.31,7.97,93.0,Satisfactory,79,9.7,27.9,0.0,False,3.3534,Monsoon (Jul–Sep)
2016-08-23,38.99,39.47,8.06,107.0,Moderate,82,7.5,28.4,0.1,False,3.6633,Monsoon (Jul–Sep)
2016-08-24,43.35,32.04,10.86,127.0,Moderate,85,14.1,27.3,12.8,False,3.7693,Monsoon (Jul–Sep)
2016-08-25,45.88,35.41,8.23,93.0,Satisfactory,85,7.4,28.4,1.3,False,3.826,Monsoon (Jul–Sep)
2016-08-26,54.13,35.61,9.57,142.0,Moderate,82,4.6,28.9,1.5,False,3.9914,Monsoon (Jul–Sep)
2016-08-27,56.56,20.84,7.91,93.0,Satisfactory,86,8.4,28.4,6.5,False,4.0353,Monsoon (Jul–Sep)
2016-08-28,57.09,28.7,7.04,224.0,Poor,84,7.5,29.0,6.3,False,4.0446,Monsoon (Jul–Sep)
2016-08-29,54.73,37.48,8.92,169.0,Moderate,89,5.3,27.5,13.7,False,4.0024,Monsoon (Jul–Sep)
2016-08-30,48.93,42.73,9.22,110.0,Moderate,88,3.3,27.1,24.3,False,3.8904,Monsoon (Jul–Sep)
2016-08-31,37.1,41.82,8.72,100.0,Satisfactory,91,6.1,26.8,18.5,False,3.6136,Monsoon (Jul–Sep)
2016-09-01,28.06,51.78,9.47,109.0,Moderate,88,5.9,27.0,7.3,False,3.3343,Monsoon (Jul–Sep)
2016-09-02,44.31,41.71,9.37,154.0,Moderate,80,10.7,28.2,0.4,False,3.7912,Monsoon (Jul–Sep)
2016-09-03,46.77,40.85,10.09,216.0,Poor,74,15.5,28.2,0.2,False,3.8452,Monsoon (Jul–Sep)
2016-09-04,57.64,31.96,9.05,262.0,Poor,73,13.7,28.2,0.0,False,4.0542,Monsoon (Jul–Sep)
2016-09-05,45.37,33.42,9.87,260.0,Poor,72,14.6,27.9,0.1,False,3.8149,Monsoon (Jul–Sep)
2016-09-06,50.42,34.74,10.61,329.0,Very Poor,70,15.6,28.2,0.0,False,3.9204,Monsoon (Jul–Sep)
2016-09-07,50.73,39.21,14.63,291.0,Poor,68,12.9,28.3,0.0,False,3.9265,Monsoon (Jul–Sep)
2016-09-08,71.72,39.69,12.02,300.0,Poor,68,12.1,28.4,0.1,False,4.2728,Monsoon (Jul–Sep)
2016-09-09,87.99,43.67,10.34,335.0,Very Poor,68,12.4,28.8,0.0,False,4.4772,Monsoon (Jul–Sep)
2016-09-10,45.7,38.14,10.81,240.0,Poor,65,13.3,29.0,0.0,False,3.8221,Monsoon (Jul–Sep)
2016-09-11,45.89,40.58,10.92,177.0,Moderate,64,11.5,28.9,0.0,False,3.8262,Monsoon (Jul–Sep)
2016-09-12,49.7,39.41,9.59,178.0,Moderate,65,11.3,28.8,0.0,False,3.906,Monsoon (Jul–Sep)
2016-09-13,57.08,43.84,10.93,193.0,Moderate,70,6.5,29.0,0.0,False,4.0445,Monsoon (Jul–Sep)
2016-09-14,47.36,45.6,11.21,150.0,Moderate,79,6.5,27.9,0.1,False,3.8578,Monsoon (Jul–Sep)
2016-09-15,79.99,54.73,11.6,215.0,Poor,75,4.7,28.7,0.0,False,4.3819,Monsoon (Jul–Sep)
2016-09-16,67.11,57.22,12.39,233.0,Poor,73,5.7,29.1,0.0,False,4.2063,Monsoon (Jul–Sep)
2016-09-17,81.9,56.8,12.78,220.0,Poor,73,4.3,28.7,0.0,False,4.4055,Monsoon (Jul–Sep)
2016-09-18,86.16,56.82,10.89,266.0,Poor,76,6.6,28.7,0.0,False,4.4562,Monsoon (Jul–Sep)
2016-09-19,75.02,67.37,14.63,192.0,Moderate,74,3.8,29.0,0.0,False,4.3178,Monsoon (Jul–Sep)
2016-09-20,94.23,86.2,16.12,264.0,Poor,67,5.3,30.0,0.0,False,4.5457,Monsoon (Jul–Sep)
2016-09-21,89.62,70.0,17.12,284.0,Poor,72,10.2,29.6,0.0,False,4.4956,Monsoon (Jul–Sep)
2016-09-22,32.73,44.35,13.44,150.0,Moderate,84,13.1,26.9,2.0,False,3.4883,Monsoon (Jul–Sep)
2016-09-23,55.64,57.24,13.77,134.0,Moderate,78,5.0,27.4,0.0,False,4.0189,Monsoon (Jul–Sep)
2016-09-24,56.46,53.66,14.63,197.0,Moderate,78,6.0,28.1,0.2,False,4.0335,Monsoon (Jul–Sep)
2016-09-25,56.64,55.69,15.5,175.0,Moderate,76,6.0,27.6,0.0,False,4.0367,Monsoon (Jul–Sep)
2016-09-26,89.09,68.3,15.11,236.0,Poor,75,5.7,28.2,0.2,False,4.4896,Monsoon (Jul–Sep)
2016-09-27,52.49,41.03,13.68,185.0,Moderate,75,6.1,28.5,0.0,False,3.9606,Monsoon (Jul–Sep)
2016-09-28,105.43,100.66,11.94,103.0,Moderate,70,5.7,29.1,0.0,False,4.658,Monsoon (Jul–Sep)
2016-09-29,101.84,63.0,15.28,289.0,Poor,74,5.7,29.0,0.1,False,4.6234,Monsoon (Jul–Sep)
2016-09-30,84.33,65.05,15.0,224.0,Poor,72,4.3,29.1,0.0,False,4.4347,Monsoon (Jul–Sep)
2016-10-01,117.28,73.71,24.55,312.0,Very Poor,71,5.7,29.7,0.0,False,4.7646,Other months
2016-10-02,81.87,59.82,16.28,234.0,Poor,73,6.2,29.7,0.3,False,4.4051,Other months
2016-10-03,103.12,66.31,12.96,282.0,Poor,77,4.9,29.3,1.7,False,4.6359,Other months
2016-10-04,159.8,78.18,13.68,351.0,Very Poor,78,4.0,29.1,1.7,False,5.0739,Other months
2016-10-05,81.71,77.96,14.4,232.0,Poor,81,5.3,28.0,7.7,False,4.4032,Other months
2016-10-06,117.86,87.85,15.09,280.0,Poor,78,4.4,28.2,0.0,False,4.7695,Other months
2016-10-07,114.06,74.99,14.63,311.0,Very Poor,72,6.3,28.5,0.0,False,4.7367,Other months
2016-10-08,132.11,76.99,14.9,408.0,Severe,65,7.7,28.3,0.0,False,4.8836,Other months
2016-10-09,144.47,92.64,17.2,416.0,Severe,64,5.7,28.0,0.0,False,4.9731,Other months
2016-10-10,125.8,88.86,17.3,387.0,Very Poor,58,7.0,27.3,0.0,False,4.8347,Other months
2016-10-11,134.84,83.87,16.52,408.0,Severe,52,9.3,26.6,0.0,False,4.9041,Other months
2016-10-12,114.3,83.3,20.1,405.0,Severe,50,9.5,26.4,0.0,False,4.7388,Other months
2016-10-13,86.93,81.11,19.17,371.0,Very Poor,47,9.2,26.0,0.0,False,4.4651,Other months
2016-10-14,94.83,87.15,20.72,375.0,Very Poor,47,7.3,25.3,0.0,False,4.5521,Other months
2016-10-15,144.98,108.83,22.1,400.0,Very Poor,53,7.3,25.3,0.0,False,4.9766,Other months
2016-10-16,132.01,89.01,24.72,430.0,Severe,52,7.6,25.5,0.0,False,4.8829,Other months
2016-10-17,149.35,94.29,27.27,425.0,Severe,52,7.4,25.7,0.0,False,5.0063,Other months
2016-10-18,161.49,95.27,22.25,438.0,Severe,52,7.2,24.8,0.0,False,5.0844,Other months
2016-10-19,140.57,91.52,24.66,428.0,Severe,53,6.7,24.9,0.0,False,4.9457,Other months
2016-10-20,135.9,90.28,24.72,425.0,Severe,42,9.4,25.5,0.0,False,4.9119,Other months
2016-10-21,161.11,88.27,26.66,496.0,Severe,43,10.9,25.9,0.0,False,5.0821,Other months
2016-10-22,140.92,84.96,20.7,472.0,Severe,46,11.3,25.9,0.0,False,4.9482,Other months
2016-10-23,182.14,90.22,19.38,470.0,Severe,49,11.5,25.3,0.0,False,5.2048,Other months
2016-10-24,164.51,88.17,21.68,454.0,Severe,49,9.7,25.2,0.0,False,5.103,Other months
2016-10-25,115.76,82.7,23.46,396.0,Very Poor,49,10.4,25.3,0.0,False,4.7515,Other months
2016-10-26,209.27,111.23,25.0,413.0,Severe,55,7.2,24.9,0.0,False,5.3436,Other months
2016-10-27,296.27,120.07,23.95,558.0,Severe,55,8.8,23.9,0.0,False,5.6913,Other months
2016-10-28,318.57,119.42,27.89,570.0,Severe,49,7.7,23.7,0.0,False,5.7638,Other months
2016-10-29,350.39,162.5,54.38,554.0,Severe,50,5.7,23.8,0.0,False,5.859,Other months
2016-10-30,355.77,112.59,40.23,522.0,Severe,62,6.4,23.3,0.0,False,5.8743,Other months
2016-10-31,434.92,113.21,71.56,520.0,Severe,62,5.6,23.6,0.0,False,6.0752,Other months
2016-11-01,394.59,120.66,33.34,550.0,Severe,64,6.0,22.7,0.0,False,5.9778,Winter (Nov–Jan)
2016-11-02,537.96,149.12,26.66,593.0,Severe,64,6.2,23.1,0.0,False,6.2878,Winter (Nov–Jan)
2016-11-03,482.4,148.92,29.4,625.0,Severe,63,5.7,23.1,0.0,False,6.1788,Winter (Nov–Jan)
2016-11-04,342.45,131.92,25.93,480.0,Severe,63,6.7,22.6,0.0,False,5.8361,Winter (Nov–Jan)
2016-11-05,588.39,113.31,22.21,603.0,Severe,62,8.4,22.5,0.0,False,6.3774,Winter (Nov–Jan)
2016-11-06,685.36,128.15,22.61,676.0,Severe,60,7.1,22.3,0.0,False,6.5299,Winter (Nov–Jan)
2016-11-07,488.57,123.36,23.88,716.0,Severe,57,9.5,22.1,0.0,False,6.1915,Winter (Nov–Jan)
2016-11-08,338.38,92.18,21.36,542.0,Severe,50,12.9,22.4,0.0,False,5.8242,Winter (Nov–Jan)
2016-11-09,307.08,103.26,21.52,455.0,Severe,51,9.5,21.7,0.0,False,5.7271,Winter (Nov–Jan)
2016-11-10,291.71,133.98,29.45,471.0,Severe,59,7.1,21.0,0.0,False,5.6758,Winter (Nov–Jan)
2016-11-11,295.88,147.03,35.04,514.0,Severe,64,7.4,21.0,0.0,False,5.69,Winter (Nov–Jan)
2016-11-12,277.67,127.18,34.7,491.0,Severe,60,7.6,21.6,0.0,False,5.6264,Winter (Nov–Jan)
2016-11-13,228.16,113.74,51.78,469.0,Severe,58,4.9,21.9,0.0,False,5.43,Winter (Nov–Jan)
2016-11-14,194.2,119.58,22.7,404.0,Severe,61,4.7,21.9,0.0,False,5.2689,Winter (Nov–Jan)
2016-11-15,236.09,116.66,21.98,379.0,Very Poor,52,6.7,21.3,0.0,False,5.4642,Winter (Nov–Jan)
2016-11-16,291.98,109.65,23.97,428.0,Severe,52,8.7,20.1,0.0,False,5.6767,Winter (Nov–Jan)
2016-11-17,351.47,96.23,21.65,504.0,Severe,50,12.5,20.0,0.0,False,5.8621,Winter (Nov–Jan)
2016-11-18,237.21,102.95,23.11,512.0,Severe,55,10.4,20.1,0.0,False,5.4689,Winter (Nov–Jan)
2016-11-19,285.71,114.11,30.47,494.0,Severe,58,7.0,19.6,0.0,False,5.655,Winter (Nov–Jan)
2016-11-20,323.74,117.17,27.23,438.0,Severe,62,6.4,19.7,0.0,False,5.7799,Winter (Nov–Jan)
2016-11-21,340.61,128.85,26.25,474.0,Severe,60,7.1,20.4,0.0,False,5.8307,Winter (Nov–Jan)
2016-11-22,281.76,111.52,25.26,471.0,Severe,53,9.9,20.6,0.0,False,5.6411,Winter (Nov–Jan)
2016-11-23,174.56,98.73,30.13,432.0,Severe,58,10.5,20.7,0.0,False,5.1623,Winter (Nov–Jan)
2016-11-24,216.1,109.5,22.29,397.0,Very Poor,56,10.2,20.0,0.0,False,5.3757,Winter (Nov–Jan)
2016-11-25,136.21,68.9,20.99,375.0,Very Poor,43,17.8,21.3,0.0,False,4.9142,Winter (Nov–Jan)
2016-11-26,113.3,70.01,23.22,330.0,Very Poor,39,17.4,22.0,0.0,False,4.73,Winter (Nov–Jan)
2016-11-27,128.7,71.29,22.68,347.0,Very Poor,42,14.8,21.5,0.0,False,4.8575,Winter (Nov–Jan)
2016-11-28,127.5,82.99,29.33,274.0,Poor,41,12.6,20.9,0.0,False,4.8481,Winter (Nov–Jan)
2016-11-29,236.58,133.28,27.59,360.0,Very Poor,55,6.2,18.7,0.0,False,5.4663,Winter (Nov–Jan)
2016-11-30,246.25,95.64,20.23,441.0,Severe,71,8.1,19.1,0.0,False,5.5063,Winter (Nov–Jan)
2016-12-01,263.61,83.15,19.08,418.0,Severe,75,6.0,19.9,0.0,False,5.5745,Winter (Nov–Jan)
2016-12-02,263.25,101.67,20.38,474.0,Severe,72,5.8,19.2,0.0,False,5.5731,Winter (Nov–Jan)
2016-12-03,196.6,97.75,23.49,419.0,Severe,62,6.6,18.2,0.0,False,5.2812,Winter (Nov–Jan)
2016-12-04,223.3,109.4,22.96,379.0,Very Poor,59,7.5,17.7,0.0,False,5.4085,Winter (Nov–Jan)
2016-12-05,204.6,78.79,23.92,389.0,Very Poor,63,8.1,18.0,0.0,False,5.3211,Winter (Nov–Jan)
2016-12-06,293.91,96.68,23.11,402.0,Severe,68,5.8,18.1,0.0,False,5.6833,Winter (Nov–Jan)
2016-12-07,283.61,81.86,23.69,472.0,Severe,72,4.8,18.2,0.0,False,5.6476,Winter (Nov–Jan)
2016-12-08,238.21,72.44,22.2,422.0,Severe,73,4.2,17.8,0.0,False,5.4732,Winter (Nov–Jan)
2016-12-09,295.62,71.44,23.47,443.0,Severe,71,4.4,18.2,0.0,False,5.6891,Winter (Nov–Jan)
2016-12-10,189.09,58.86,20.83,413.0,Severe,74,7.8,18.6,0.0,False,5.2422,Winter (Nov–Jan)
2016-12-11,199.12,50.79,22.65,351.0,Very Poor,71,5.7,19.2,0.0,False,5.2939,Winter (Nov–Jan)
2016-12-12,210.28,76.9,23.52,418.0,Severe,68,7.0,18.7,0.0,False,5.3484,Winter (Nov–Jan)
2016-12-13,209.91,76.81,21.71,413.0,Severe,72,7.3,18.1,0.0,False,5.3467,Winter (Nov–Jan)
2016-12-14,154.55,66.38,18.5,379.0,Very Poor,69,9.3,17.3,0.0,False,5.0405,Winter (Nov–Jan)
2016-12-15,167.64,61.53,20.65,359.0,Very Poor,61,11.4,16.3,0.0,False,5.1218,Winter (Nov–Jan)
2016-12-16,200.78,85.26,23.5,390.0,Very Poor,64,7.6,15.3,0.0,False,5.3022,Winter (Nov–Jan)
2016-12-17,229.35,88.54,21.22,437.0,Severe,66,8.0,15.2,0.0,False,5.4352,Winter (Nov–Jan)
2016-12-18,232.33,86.92,21.99,411.0,Severe,64,8.4,15.0,0.0,False,5.4482,Winter (Nov–Jan)
2016-12-19,236.24,88.02,21.32,443.0,Severe,63,11.1,15.3,0.0,False,5.4648,Winter (Nov–Jan)
2016-12-20,161.92,68.35,22.9,377.0,Very Poor,57,16.7,17.2,0.0,False,5.0871,Winter (Nov–Jan)
2016-12-21,131.95,66.67,22.63,317.0,Very Poor,52,14.8,17.3,0.0,False,4.8824,Winter (Nov–Jan)
2016-12-22,187.3,82.03,24.9,349.0,Very Poor,60,7.5,16.4,0.0,False,5.2327,Winter (Nov–Jan)
2016-12-23,364.15,122.88,22.09,470.0,Severe,68,3.2,16.7,0.0,False,5.8976,Winter (Nov–Jan)
2016-12-24,411.8,114.03,19.54,576.0,Severe,73,9.6,16.1,0.0,False,6.0205,Winter (Nov–Jan)
2016-12-25,232.41,59.88,19.37,412.0,Severe,78,9.1,16.2,0.0,False,5.4485,Winter (Nov–Jan)
2016-12-26,154.26,65.49,22.82,338.0,Very Poor,73,11.5,16.1,0.0,False,5.0386,Winter (Nov–Jan)
2016-12-27,213.2,93.45,24.51,319.0,Very Poor,63,10.2,15.7,0.0,False,5.3622,Winter (Nov–Jan)
2016-12-28,273.82,129.41,26.1,455.0,Severe,68,6.3,15.8,0.0,False,5.6125,Winter (Nov–Jan)
2016-12-29,339.96,108.76,21.6,524.0,Severe,76,8.7,15.8,0.0,False,5.8288,Winter (Nov–Jan)
2016-12-30,231.1,62.46,23.47,381.0,Very Poor,80,9.1,16.0,0.0,False,5.4429,Winter (Nov–Jan)
2016-12-31,211.16,56.66,23.82,338.0,Very Poor,79,9.3,15.6,0.0,False,5.3526,Winter (Nov–Jan)
2017-01-01,191.5,66.19,25.13,332.0,Very Poor,80,9.1,15.7,0.0,False,5.2549,Winter (Nov–Jan)
2017-01-02,247.79,95.55,22.29,384.0,Very Poor,82,7.0,15.5,0.0,False,5.5126,Winter (Nov–Jan)
2017-01-03,255.33,90.79,25.33,373.0,Very Poor,75,5.2,16.1,0.0,False,5.5426,Winter (Nov–Jan)
2017-01-04,248.01,91.07,23.11,439.0,Severe,74,5.8,16.6,0.0,False,5.5135,Winter (Nov–Jan)
2017-01-05,215.42,87.15,25.15,318.0,Very Poor,78,6.6,16.7,0.0,False,5.3726,Winter (Nov–Jan)
2017-01-06,194.12,65.86,20.52,390.0,Very Poor,77,10.8,16.8,1.8,False,5.2685,Winter (Nov–Jan)
2017-01-07,154.52,38.85,22.19,332.0,Very Poor,87,10.7,14.6,5.4,False,5.0403,Winter (Nov–Jan)
2017-01-08,136.98,52.31,32.22,283.0,Poor,81,8.0,13.6,0.0,False,4.9198,Winter (Nov–Jan)
2017-01-09,141.88,64.33,24.76,300.0,Poor,72,9.5,13.0,0.0,False,4.955,Winter (Nov–Jan)
2017-01-10,108.26,59.2,19.1,305.0,Very Poor,60,10.9,11.0,0.0,False,4.6845,Winter (Nov–Jan)
2017-01-11,146.04,67.72,21.36,337.0,Very Poor,58,10.7,9.7,0.0,False,4.9839,Winter (Nov–Jan)
2017-01-12,216.73,79.35,20.33,417.0,Severe,64,8.9,10.1,0.0,False,5.3787,Winter (Nov–Jan)
2017-01-13,232.37,85.07,24.71,426.0,Severe,66,9.2,10.5,0.0,False,5.4483,Winter (Nov–Jan)
2017-01-14,309.28,84.75,11.7,439.0,Severe,64,7.5,11.3,0.0,False,5.7342,Winter (Nov–Jan)
2017-01-15,222.66,63.97,17.67,382.0,Very Poor,63,6.7,13.8,0.0,False,5.4056,Winter (Nov–Jan)
2017-01-16,188.08,60.94,20.6,397.0,Very Poor,62,11.6,14.5,0.2,False,5.2369,Winter (Nov–Jan)
2017-01-17,177.67,51.44,18.44,330.0,Very Poor,76,9.7,10.7,0.0,False,5.1799,Winter (Nov–Jan)
2017-01-18,218.63,66.94,20.52,358.0,Very Poor,73,8.8,11.5,0.0,False,5.3874,Winter (Nov–Jan)
2017-01-19,227.68,55.95,20.86,376.0,Very Poor,66,13.5,12.9,0.0,False,5.4279,Winter (Nov–Jan)
2017-01-20,217.55,63.7,22.23,334.0,Very Poor,68,12.3,12.0,0.0,False,5.3824,Winter (Nov–Jan)
2017-01-21,349.98,63.36,17.93,387.0,Very Poor,66,9.5,13.2,0.1,False,5.8579,Winter (Nov–Jan)
2017-01-22,286.6,63.71,18.75,446.0,Severe,73,8.0,15.7,0.0,False,5.6581,Winter (Nov–Jan)
2017-01-23,189.45,67.27,20.61,379.0,Very Poor,71,9.2,16.3,0.0,False,5.2441,Winter (Nov–Jan)
2017-01-24,230.94,92.12,24.56,375.0,Very Poor,71,6.7,16.9,0.0,False,5.4422,Winter (Nov–Jan)
2017-01-25,241.78,88.02,23.95,450.0,Severe,75,12.9,18.4,12.8,False,5.488,Winter (Nov–Jan)
2017-01-26,135.87,50.39,22.04,340.0,Very Poor,90,11.8,16.3,33.3,False,4.9117,Winter (Nov–Jan)
2017-01-27,74.92,42.24,18.11,203.0,Poor,81,12.9,14.7,1.8,False,4.3164,Winter (Nov–Jan)
2017-01-28,109.13,45.82,18.1,236.0,Poor,82,10.0,14.2,0.0,False,4.6925,Winter (Nov–Jan)
2017-01-29,132.35,46.68,18.12,252.0,Poor,82,12.4,14.9,0.0,False,4.8854,Winter (Nov–Jan)
2017-01-30,166.71,65.43,20.29,302.0,Very Poor,84,7.3,14.8,0.0,False,5.1163,Winter (Nov–Jan)
2017-01-31,214.23,82.78,22.81,358.0,Very Poor,84,6.9,15.6,0.0,False,5.3671,Winter (Nov–Jan)
2017-02-01,136.02,64.08,19.51,317.0,Very Poor,81,9.0,14.7,0.0,False,4.9128,Other months
2017-02-02,198.24,93.86,18.84,387.0,Very Poor,79,6.3,14.7,0.0,False,5.2895,Other months
2017-02-03,194.99,88.38,19.98,438.0,Severe,82,6.9,14.7,0.0,False,5.2729,Other months
2017-02-04,186.65,62.01,17.04,407.0,Severe,79,14.6,16.8,0.0,False,5.2292,Other months
2017-02-05,146.49,49.57,18.3,312.0,Very Poor,79,13.0,17.7,3.2,False,4.987,Other months
2017-02-06,176.04,60.62,17.23,367.0,Very Poor,78,10.7,16.2,0.1,False,5.1707,Other months
2017-02-07,77.85,55.29,16.07,263.0,Poor,73,11.4,14.3,0.0,False,4.3548,Other months
2017-02-08,129.1,69.98,17.2,287.0,Poor,73,8.2,14.8,0.0,False,4.8606,Other months
2017-02-09,133.12,67.24,20.84,346.0,Very Poor,72,10.9,14.7,0.0,False,4.8913,Other months
2017-02-10,120.43,62.77,20.09,314.0,Very Poor,68,12.4,14.5,0.0,False,4.7911,Other months
2017-02-11,129.09,58.31,17.55,314.0,Very Poor,70,8.1,14.0,0.0,False,4.8605,Other months
2017-02-12,166.55,56.97,19.9,314.0,Very Poor,72,7.6,15.0,0.0,False,5.1153,Other months
2017-02-13,130.62,73.3,21.25,298.0,Poor,68,9.3,15.8,0.0,False,4.8723,Other months
2017-02-14,168.96,81.51,21.87,319.0,Very Poor,65,10.5,16.4,0.0,False,5.1297,Other months
2017-02-15,183.98,82.14,21.26,382.0,Very Poor,65,9.7,17.6,0.0,False,5.2148,Other months
2017-02-16,163.86,78.82,21.02,352.0,Very Poor,61,12.7,19.9,0.0,False,5.099,Other months
2017-02-17,112.02,72.55,19.33,309.0,Very Poor,64,12.0,20.1,0.0,False,4.7187,Other months
2017-02-18,107.13,71.98,19.29,301.0,Very Poor,66,10.2,20.6,0.0,False,4.674,Other months
2017-02-19,109.38,68.84,18.33,274.0,Poor,62,8.9,21.5,0.0,False,4.6948,Other months
2017-02-20,126.74,67.45,23.96,313.0,Very Poor,63,7.6,22.4,0.0,False,4.8421,Other months
2017-02-21,106.92,60.72,19.57,310.0,Very Poor,64,10.3,19.4,0.0,False,4.6721,Other months
2017-02-22,93.03,65.62,19.84,258.0,Poor,57,8.9,18.9,0.0,False,4.5329,Other months
2017-02-23,182.29,55.22,13.77,238.0,Poor,44,13.8,17.9,0.0,False,5.2056,Other months
2017-02-24,451.25,42.2,6.64,449.0,Severe,37,17.7,18.3,0.0,False,6.112,Other months
2017-02-25,425.22,46.64,8.41,516.0,Severe,39,16.9,19.3,0.0,False,6.0526,Other months
2017-02-26,328.23,59.34,17.55,520.0,Severe,46,13.2,18.8,0.0,False,5.7937,Other months
2017-02-27,178.5,72.8,21.66,363.0,Very Poor,48,11.2,19.4,0.0,False,5.1846,Other months
2017-02-28,149.73,94.66,28.15,362.0,Very Poor,47,5.6,22.0,0.0,False,5.0088,Other months
2017-03-01,127.9,79.46,24.07,397.0,Very Poor,56,7.3,22.2,2.9,False,4.8512,Other months
2017-03-02,114.68,69.08,23.53,280.0,Poor,62,7.4,20.3,1.3,False,4.7421,Other months
2017-03-03,67.83,56.64,19.69,206.0,Poor,46,10.3,19.7,0.0,False,4.217,Other months
2017-03-04,82.32,60.55,22.03,190.0,Moderate,43,11.4,18.4,0.0,False,4.4106,Other months
2017-03-05,90.6,61.48,25.34,210.0,Poor,43,13.4,18.8,0.0,False,4.5065,Other months
2017-03-06,91.6,64.99,26.91,201.0,Poor,43,11.9,19.4,0.0,False,4.5174,Other months
2017-03-07,112.41,65.16,30.7,243.0,Poor,46,8.0,20.5,0.0,False,4.7222,Other months
2017-03-08,134.4,49.88,24.14,267.0,Poor,50,11.3,20.5,1.2,False,4.9008,Other months
2017-03-09,106.45,39.68,20.15,245.0,Poor,64,9.6,19.1,0.3,False,4.6677,Other months
2017-03-10,68.88,33.32,17.93,165.0,Moderate,77,11.1,17.1,12.1,False,4.2324,Other months
2017-03-11,37.49,32.0,19.4,102.0,Moderate,76,10.0,16.1,1.3,False,3.6241,Other months
2017-03-12,64.42,32.11,20.11,159.0,Moderate,63,9.6,15.9,0.0,False,4.1654,Other months
2017-03-13,74.58,27.78,19.33,174.0,Moderate,53,11.7,16.2,0.0,False,4.3119,Other months
2017-03-14,102.46,34.28,22.37,270.0,Poor,53,8.2,17.5,0.0,False,4.6295,Other months
2017-03-15,112.71,42.06,23.96,397.0,Very Poor,54,9.7,18.9,0.0,False,4.7248,Other months
2017-03-16,125.8,42.18,23.59,371.0,Very Poor,52,8.3,20.3,0.0,False,4.8347,Other months
2017-03-17,114.07,38.7,21.42,328.0,Very Poor,56,11.4,19.8,0.0,False,4.7368,Other months
2017-03-18,96.39,46.65,22.29,254.0,Poor,50,8.8,20.5,0.0,False,4.5684,Other months
2017-03-19,120.43,51.65,22.89,342.0,Very Poor,55,7.8,21.5,1.3,False,4.7911,Other months
2017-03-20,121.21,49.53,22.25,367.0,Very Poor,56,11.7,21.8,0.0,False,4.7975,Other months
2017-03-21,128.51,51.94,24.38,400.0,Very Poor,48,11.9,23.5,0.0,False,4.856,Other months
2017-03-22,120.88,69.31,28.88,390.0,Very Poor,48,12.3,25.5,0.0,False,4.7948,Other months
2017-03-23,151.17,70.55,27.21,417.0,Severe,50,7.8,25.8,0.2,False,5.0184,Other months
2017-03-24,149.42,79.52,22.09,359.0,Very Poor,47,12.2,26.0,0.0,False,5.0068,Other months
2017-03-25,168.23,83.82,15.18,309.0,Very Poor,41,12.8,25.4,0.0,False,5.1253,Other months
2017-03-26,118.34,78.84,14.85,292.0,Poor,38,15.1,26.7,0.0,False,4.7736,Other months
2017-03-27,156.38,79.24,17.55,278.0,Poor,40,16.9,28.4,0.0,False,5.0523,Other months
2017-03-28,152.66,85.54,18.24,320.0,Very Poor,43,12.0,28.9,0.0,False,5.0282,Other months
2017-03-29,113.62,75.87,17.26,350.0,Very Poor,39,14.2,29.7,0.0,False,4.7329,Other months
2017-03-30,69.44,76.28,23.72,234.0,Poor,36,13.6,29.8,0.0,False,4.2405,Other months
2017-03-31,91.19,84.22,20.48,233.0,Poor,39,10.8,30.0,0.0,False,4.5129,Other months
2017-04-01,105.71,81.75,20.05,341.0,Very Poor,35,12.9,29.8,0.0,False,4.6607,Other months
2017-04-02,83.36,77.96,19.33,259.0,Poor,29,13.4,29.4,0.0,False,4.4232,Other months
2017-04-03,70.62,83.8,24.03,204.0,Poor,31,10.6,29.1,0.0,False,4.2573,Other months
2017-04-04,84.4,73.67,24.14,220.0,Poor,32,10.5,29.0,0.0,False,4.4356,Other months
2017-04-05,47.67,64.65,19.75,255.0,Poor,41,20.4,28.3,1.1,False,3.8643,Other months
2017-04-06,62.44,67.13,17.21,211.0,Poor,40,17.5,28.7,0.0,False,4.1342,Other months
2017-04-07,150.76,74.99,27.69,428.0,Severe,40,10.2,26.4,0.0,False,5.0157,Other months
2017-04-08,151.25,77.6,33.4,497.0,Severe,24,10.2,25.5,0.0,False,5.0189,Other months
2017-04-09,68.88,68.1,22.78,289.0,Poor,22,17.4,25.6,0.0,False,4.2324,Other months
2017-04-10,129.15,72.06,21.85,285.0,Poor,22,20.5,25.9,0.0,False,4.861,Other months
2017-04-11,146.59,71.58,24.49,368.0,Very Poor,24,19.1,28.1,0.0,False,4.9876,Other months
2017-04-12,107.69,61.17,32.76,304.0,Very Poor,26,15.6,29.5,0.0,False,4.6793,Other months
2017-04-13,163.97,87.79,43.82,377.0,Very Poor,27,8.8,30.3,0.0,False,5.0997,Other months
2017-04-14,184.69,110.15,50.31,418.0,Severe,28,8.6,30.9,0.0,False,5.2187,Other months
2017-04-15,176.54,102.4,42.8,355.0,Very Poor,27,10.2,31.3,0.0,False,5.1735,Other months
2017-04-16,175.23,102.55,62.6,416.0,Severe,31,8.7,31.0,0.0,False,5.1661,Other months
2017-04-17,145.22,102.55,42.39,403.0,Severe,38,10.7,31.9,0.0,False,4.9782,Other months
2017-04-18,152.84,88.05,44.15,415.0,Severe,35,8.8,32.7,0.0,False,5.0294,Other months
2017-04-19,136.35,80.08,41.33,412.0,Severe,20,11.2,33.7,0.0,False,4.9152,Other months
2017-04-20,152.99,93.15,37.38,394.0,Very Poor,25,9.7,33.7,0.0,False,5.0304,Other months
2017-04-21,130.13,103.25,30.82,357.0,Very Poor,38,10.8,33.3,0.0,False,4.8685,Other months
2017-04-22,110.54,93.8,30.11,291.0,Poor,47,8.6,32.5,2.0,True,4.7054,Other months
2017-04-23,103.42,75.05,29.4,244.0,Poor,38,10.8,31.4,0.0,False,4.6388,Other months
2017-04-24,99.09,61.32,31.95,287.0,Poor,31,11.6,30.4,2.1,False,4.596,Other months
2017-04-25,96.07,69.59,39.9,254.0,Poor,24,13.3,30.5,0.0,False,4.5651,Other months
2017-04-26,72.31,72.94,29.27,242.0,Poor,23,10.3,29.9,0.0,False,4.281,Other months
2017-04-27,93.14,73.49,46.69,223.0,Poor,24,8.4,30.6,0.0,False,4.5341,Other months
2017-04-28,109.36,68.76,39.58,243.0,Poor,29,9.5,30.4,0.3,False,4.6946,Other months
2017-04-29,126.74,85.21,54.52,237.0,Poor,30,7.1,30.8,0.0,False,4.8421,Other months
2017-04-30,80.81,65.55,46.62,275.0,Poor,34,12.1,30.0,0.1,False,4.3921,Other months
2017-05-01,85.8,70.38,56.64,183.0,Moderate,31,7.4,29.9,0.0,False,4.452,Other months
2017-05-02,198.2,108.48,50.78,370.0,Very Poor,22,5.7,31.9,0.0,False,5.2893,Other months
2017-05-03,145.74,97.21,54.83,419.0,Severe,25,8.9,31.6,0.0,False,4.9818,Other months
2017-05-04,109.91,67.76,34.97,317.0,Very Poor,25,12.9,31.6,0.0,False,4.6997,Other months
2017-05-05,207.4,75.66,46.67,455.0,Severe,26,10.4,31.7,0.0,False,5.3346,Other months
2017-05-06,204.56,92.19,51.7,435.0,Severe,24,9.2,33.2,0.0,False,5.3209,Other months
2017-05-07,220.77,92.34,45.39,468.0,Severe,23,8.6,34.5,0.0,False,5.3971,Other months
2017-05-08,183.82,94.19,52.99,442.0,Severe,23,8.1,34.2,0.0,False,5.214,Other months
2017-05-09,109.76,65.21,36.94,400.0,Very Poor,32,13.4,33.7,0.0,False,4.6983,Other months
2017-05-10,74.42,46.48,35.61,223.0,Poor,44,14.5,32.3,1.8,False,4.3097,Other months
2017-05-11,94.28,62.22,44.94,220.0,Poor,38,10.6,33.6,0.0,False,4.5463,Other months
2017-05-12,216.96,70.84,65.5,474.0,Severe,37,9.1,33.1,1.4,False,5.3797,Other months
2017-05-13,198.09,87.53,53.24,479.0,Severe,33,9.4,33.6,0.1,False,5.2887,Other months
2017-05-14,121.76,70.37,44.98,373.0,Very Poor,23,9.9,35.0,0.0,False,4.8021,Other months
2017-05-15,135.54,75.55,46.16,354.0,Very Poor,22,9.6,35.2,0.0,False,4.9093,Other months
2017-05-16,123.21,54.83,41.96,349.0,Very Poor,28,11.8,33.8,0.7,False,4.8139,Other months
2017-05-17,78.18,47.84,39.01,264.0,Poor,40,8.0,31.1,1.0,False,4.359,Other months
2017-05-18,126.04,50.3,55.11,188.0,Moderate,43,9.5,31.5,0.4,False,4.8366,Other months
2017-05-19,139.1,58.93,41.31,294.0,Poor,38,8.3,33.1,0.0,False,4.9352,Other months
2017-05-20,233.82,59.74,36.26,334.0,Very Poor,31,8.0,33.1,0.0,False,5.4546,Other months
2017-05-21,178.44,52.38,40.4,505.0,Severe,34,9.5,32.4,0.0,False,5.1843,Other months
2017-05-22,110.1,63.7,35.36,349.0,Very Poor,44,7.1,30.7,0.9,False,4.7014,Other months
2017-05-23,118.43,84.21,37.55,421.0,Severe,42,9.4,31.5,0.1,False,4.7743,Other months
2017-05-24,107.37,80.72,42.21,238.0,Poor,40,8.8,33.0,0.2,False,4.6763,Other months
2017-05-25,113.9,65.71,41.43,204.0,Poor,39,8.0,33.5,0.0,False,4.7353,Other months
2017-05-26,103.75,79.07,41.4,289.0,Poor,33,10.5,35.4,0.0,False,4.642,Other months
2017-05-27,69.88,50.12,38.55,236.0,Poor,46,15.7,32.9,0.2,False,4.2468,Other months
2017-05-28,40.33,45.6,31.5,148.0,Moderate,51,16.8,32.4,0.3,False,3.6971,Other months
2017-05-29,48.95,55.2,26.99,94.0,Satisfactory,57,13.8,29.9,2.4,False,3.8908,Other months
2017-05-30,63.27,64.11,26.15,130.0,Moderate,61,7.3,30.0,0.5,False,4.1474,Other months
2017-05-31,56.38,69.98,21.94,123.0,Moderate,57,12.4,30.9,0.2,False,4.0321,Other months
2017-06-01,95.23,97.33,23.0,192.0,Moderate,55,7.4,31.4,0.0,False,4.5563,Other months
2017-06-02,123.44,131.55,24.75,324.0,Very Poor,43,8.9,32.6,0.0,False,4.8158,Other months
2017-06-03,122.2,119.37,23.23,357.0,Very Poor,35,12.2,35.2,0.0,False,4.8057,Other months
2017-06-04,121.1,92.68,22.69,393.0,Very Poor,26,16.4,37.3,0.0,False,4.7966,Other months
2017-06-05,71.89,64.07,18.63,302.0,Very Poor,29,19.3,37.9,0.0,False,4.2751,Other months
2017-06-06,80.37,57.63,16.51,239.0,Poor,36,16.4,36.8,0.3,False,4.3866,Other months
2017-06-07,40.87,70.77,23.51,210.0,Poor,57,13.0,31.7,0.6,False,3.7104,Other months
2017-06-08,41.83,79.9,,77.0,Satisfactory,57,6.4,31.4,3.8,False,3.7336,Other months
2017-06-09,66.73,76.52,,89.0,Satisfactory,55,6.4,31.0,0.3,False,4.2007,Other months
2017-06-10,64.63,80.04,,143.0,Moderate,51,6.4,32.2,0.6,False,4.1687,Other months
2017-06-11,43.02,77.07,,80.0,Satisfactory,46,7.0,32.1,0.2,False,3.7617,Other months
2017-06-12,57.4,106.23,,92.0,Satisfactory,42,10.6,32.8,0.0,False,4.05,Other months
2017-06-13,48.6,96.64,,112.0,Moderate,37,9.8,33.7,0.1,False,3.8836,Other months
2017-06-14,62.0,86.9,,117.0,Moderate,35,12.2,34.4,0.4,False,4.1271,Other months
2017-06-15,80.14,139.09,,101.0,Moderate,48,10.6,32.9,2.2,False,4.3838,Other months
2017-06-16,51.6,80.43,,106.0,Moderate,49,6.6,31.0,0.4,False,3.9435,Other months
2017-06-17,41.96,70.93,,88.0,Satisfactory,61,7.2,30.5,7.0,False,3.7367,Other months
2017-06-18,65.19,56.65,,94.0,Satisfactory,66,8.7,30.8,3.1,False,4.1773,Other months
2017-06-19,60.9,36.63,,150.0,Moderate,65,11.7,31.4,5.5,False,4.1092,Other months
2017-06-20,35.1,99.75,,97.0,Satisfactory,70,5.6,29.7,10.2,False,3.5582,Other months
2017-06-21,58.27,63.2,,109.0,Moderate,71,10.0,28.7,2.4,False,4.0651,Other months
2017-06-22,61.93,36.35,,124.0,Moderate,68,8.3,29.1,0.0,False,4.126,Other months
2017-06-23,44.08,103.29,,,,71,7.5,29.3,5.5,False,3.786,Other months
2017-06-24,63.62,83.84,,111.0,Moderate,60,4.5,31.6,0.0,False,4.1529,Other months
2017-06-25,76.1,71.42,,148.0,Moderate,58,8.2,33.1,0.2,False,4.332,Other months
2017-06-26,51.52,53.97,,108.0,Moderate,60,11.5,33.5,2.3,False,3.942,Other months
2017-06-27,36.62,54.02,,73.0,Satisfactory,62,11.6,32.9,1.1,False,3.6006,Other months
2017-06-28,29.83,58.02,,58.0,Satisfactory,80,12.7,29.4,24.1,False,3.3955,Other months
2017-06-29,22.98,35.01,,58.0,Satisfactory,85,12.6,27.8,3.6,False,3.1346,Other months
2017-06-30,25.83,32.97,,46.0,Good,86,7.8,27.8,15.1,False,3.2515,Other months
2017-07-01,43.35,17.4,,84.0,Satisfactory,85,5.8,28.6,10.5,False,3.7693,Monsoon (Jul–Sep)
2017-07-02,20.52,11.37,,54.0,Satisfactory,86,9.3,27.9,12.4,False,3.0214,Monsoon (Jul–Sep)
2017-07-03,46.71,20.06,,49.0,Good,82,6.1,29.2,3.5,False,3.844,Monsoon (Jul–Sep)
2017-07-04,116.12,19.37,,149.0,Moderate,75,14.9,30.8,3.8,False,4.7546,Monsoon (Jul–Sep)
2017-07-05,50.81,14.86,,212.0,Poor,71,12.3,30.8,0.4,False,3.9281,Monsoon (Jul–Sep)
2017-07-06,47.17,18.32,,85.0,Satisfactory,72,8.5,30.1,1.0,False,3.8538,Monsoon (Jul–Sep)
2017-07-07,41.42,18.21,,77.0,Satisfactory,75,9.2,29.9,1.7,False,3.7238,Monsoon (Jul–Sep)
2017-07-08,45.31,23.52,,65.0,Satisfactory,72,8.0,31.0,0.1,False,3.8135,Monsoon (Jul–Sep)
2017-07-09,58.46,21.16,,108.0,Moderate,64,11.0,32.2,0.0,False,4.0683,Monsoon (Jul–Sep)
2017-07-10,41.92,18.81,,78.0,Satisfactory,60,13.5,32.0,0.4,False,3.7358,Monsoon (Jul–Sep)
2017-07-11,33.04,21.44,,59.0,Satisfactory,69,9.8,30.4,1.4,False,3.4977,Monsoon (Jul–Sep)
2017-07-12,22.35,19.98,,47.0,Good,78,12.1,28.2,1.1,False,3.1068,Monsoon (Jul–Sep)
2017-07-13,22.44,21.59,,39.0,Good,72,12.9,29.2,0.6,False,3.1108,Monsoon (Jul–Sep)
2017-07-14,30.35,38.36,,40.0,Good,73,13.5,29.7,0.6,False,3.4128,Monsoon (Jul–Sep)
2017-07-15,32.02,77.47,,56.0,Satisfactory,76,12.7,29.5,9.6,False,3.4664,Monsoon (Jul–Sep)
2017-07-16,38.77,76.98,,65.0,Satisfactory,79,9.4,29.8,5.1,False,3.6576,Monsoon (Jul–Sep)
2017-07-17,33.56,86.61,,71.0,Satisfactory,80,8.3,29.7,5.8,False,3.5133,Monsoon (Jul–Sep)
2017-07-18,37.67,126.91,,97.0,Satisfactory,79,6.6,30.2,4.3,False,3.6289,Monsoon (Jul–Sep)
2017-07-19,55.96,137.15,,118.0,Moderate,73,6.3,31.5,2.0,False,4.0246,Monsoon (Jul–Sep)
2017-07-20,28.88,61.54,,116.0,Moderate,78,11.0,29.4,14.0,False,3.3631,Monsoon (Jul–Sep)
2017-07-21,23.12,23.67,,53.0,Satisfactory,76,12.2,29.7,5.7,False,3.1407,Monsoon (Jul–Sep)
2017-07-22,18.54,19.9,,30.0,Good,79,18.3,28.4,1.8,False,2.9199,Monsoon (Jul–Sep)
2017-07-23,22.65,18.22,,37.0,Good,82,17.9,28.0,5.3,False,3.1202,Monsoon (Jul–Sep)
2017-07-24,17.52,19.95,,35.0,Good,84,15.1,27.6,6.3,False,2.8633,Monsoon (Jul–Sep)
2017-07-25,22.17,18.1,,37.0,Good,83,13.8,27.7,5.6,False,3.0987,Monsoon (Jul–Sep)
2017-07-26,20.17,21.95,,32.0,Good,80,10.5,28.7,0.7,False,3.0042,Monsoon (Jul–Sep)
2017-07-27,24.42,25.33,,41.0,Good,75,11.9,29.4,1.9,False,3.1954,Monsoon (Jul–Sep)
2017-07-28,25.71,24.07,,42.0,Good,76,14.2,29.1,0.9,False,3.2469,Monsoon (Jul–Sep)
2017-07-29,27.25,22.87,,47.0,Good,77,17.1,28.9,1.8,False,3.3051,Monsoon (Jul–Sep)
2017-07-30,10.88,20.58,,30.0,Good,80,9.2,28.5,2.3,False,2.3869,Monsoon (Jul–Sep)
2017-07-31,17.1,26.19,,29.0,Good,87,7.2,27.3,17.6,False,2.8391,Monsoon (Jul–Sep)
2017-08-01,17.24,23.4,,44.0,Good,90,10.5,26.8,4.8,False,2.8472,Monsoon (Jul–Sep)
2017-08-02,27.56,26.54,,40.0,Good,83,9.8,28.2,2.6,False,3.3164,Monsoon (Jul–Sep)
2017-08-03,27.29,29.16,,49.0,Good,77,14.0,28.9,1.0,False,3.3065,Monsoon (Jul–Sep)
2017-08-04,42.65,33.74,,50.0,Good,74,11.0,29.1,0.7,False,3.753,Monsoon (Jul–Sep)
2017-08-05,53.69,42.98,,88.0,Satisfactory,72,6.9,29.8,3.8,False,3.9832,Monsoon (Jul–Sep)
2017-08-06,61.44,41.75,,99.0,Satisfactory,79,6.9,29.5,1.3,False,4.1181,Monsoon (Jul–Sep)
2017-08-07,57.42,32.2,,110.0,Moderate,87,5.4,28.4,17.7,False,4.0504,Monsoon (Jul–Sep)
2017-08-08,36.58,29.91,,68.0,Satisfactory,86,4.9,28.6,12.5,False,3.5995,Monsoon (Jul–Sep)
2017-08-09,50.42,48.7,,73.0,Satisfactory,89,5.4,27.9,17.3,False,3.9204,Monsoon (Jul–Sep)
2017-08-10,48.6,64.0,,95.0,Satisfactory,81,11.6,28.8,10.2,False,3.8836,Monsoon (Jul–Sep)
2017-08-11,21.83,35.39,,58.0,Satisfactory,70,18.5,30.2,0.2,False,3.0833,Monsoon (Jul–Sep)
2017-08-12,23.4,52.95,,45.0,Good,69,20.6,30.0,0.3,True,3.1527,Monsoon (Jul–Sep)
2017-08-13,24.97,70.51,,,,71,15.4,29.8,0.5,True,3.2177,Monsoon (Jul–Sep)
2017-08-14,26.54,88.07,,,,69,8.1,29.7,0.2,False,3.2787,Monsoon (Jul–Sep)
2017-08-15,30.12,49.91,,59.0,Satisfactory,71,9.4,29.8,0.6,False,3.4052,Monsoon (Jul–Sep)
2017-08-16,35.23,64.66,,53.0,Satisfactory,67,12.6,30.4,0.0,False,3.5619,Monsoon (Jul–Sep)
2017-08-17,39.6,68.78,,66.0,Satisfactory,64,12.8,31.1,0.0,False,3.6788,Monsoon (Jul–Sep)
2017-08-18,46.25,60.15,,70.0,Satisfactory,65,10.8,31.1,0.0,False,3.8341,Monsoon (Jul–Sep)
2017-08-19,35.48,39.67,,70.0,Satisfactory,83,13.4,28.2,6.3,False,3.569,Monsoon (Jul–Sep)
2017-08-20,22.15,30.28,,63.0,Satisfactory,74,13.1,29.6,0.4,False,3.0978,Monsoon (Jul–Sep)
2017-08-21,25.5,24.42,,42.0,Good,78,11.8,29.2,6.2,False,3.2387,Monsoon (Jul–Sep)
2017-08-22,46.0,38.7,,,,81,8.3,28.8,6.0,False,3.8286,Monsoon (Jul–Sep)
2017-08-23,36.54,43.43,,,,86,8.3,28.0,3.8,False,3.5984,Monsoon (Jul–Sep)
2017-08-24,47.79,45.26,,58.0,Satisfactory,84,5.9,28.6,1.7,False,3.8668,Monsoon (Jul–Sep)
2017-08-25,51.33,39.3,,104.0,Moderate,86,5.6,28.1,6.7,False,3.9383,Monsoon (Jul–Sep)
2017-08-26,62.33,37.65,,,,88,4.9,27.6,26.7,False,4.1324,Monsoon (Jul–Sep)
2017-08-27,34.3,34.06,,,,83,6.3,28.6,1.8,False,3.5351,Monsoon (Jul–Sep)
2017-08-28,23.82,27.89,2.34,,,84,13.6,27.4,2.0,False,3.1705,Monsoon (Jul–Sep)
2017-08-29,15.23,69.8,,,,80,15.0,27.9,8.0,False,2.7233,Monsoon (Jul–Sep)
2017-08-30,20.5,101.89,,73.0,Satisfactory,81,14.9,28.2,4.4,False,3.0204,Monsoon (Jul–Sep)
2017-08-31,41.62,50.7,,94.0,Satisfactory,90,10.0,26.4,24.2,False,3.7286,Monsoon (Jul–Sep)
2017-09-01,25.58,26.64,,91.0,Satisfactory,88,10.0,26.5,33.7,False,3.2418,Monsoon (Jul–Sep)
2017-09-02,20.06,26.09,,88.0,Satisfactory,88,9.8,25.7,24.7,False,2.9987,Monsoon (Jul–Sep)
2017-09-03,38.19,27.32,,88.0,Satisfactory,80,6.4,27.5,0.5,False,3.6426,Monsoon (Jul–Sep)
2017-09-04,47.89,25.85,,89.0,Satisfactory,78,10.3,28.6,0.0,False,3.8689,Monsoon (Jul–Sep)
2017-09-05,35.61,30.29,,88.0,Satisfactory,77,10.1,28.5,0.1,False,3.5726,Monsoon (Jul–Sep)
2017-09-06,39.41,35.92,,88.0,Satisfactory,76,7.3,28.7,1.5,False,3.674,Monsoon (Jul–Sep)
2017-09-07,40.34,23.75,,88.0,Satisfactory,84,6.6,27.4,0.4,False,3.6973,Monsoon (Jul–Sep)
2017-09-08,51.7,16.52,,106.0,Moderate,81,6.2,28.2,0.3,False,3.9455,Monsoon (Jul–Sep)
2017-09-09,54.83,17.54,,96.0,Satisfactory,76,8.2,28.7,0.0,False,4.0042,Monsoon (Jul–Sep)
2017-09-10,60.46,19.76,,118.0,Moderate,73,5.9,29.8,0.0,False,4.102,Monsoon (Jul–Sep)
2017-09-11,63.97,20.25,,119.0,Moderate,72,6.9,29.7,0.0,False,4.1584,Monsoon (Jul–Sep)
2017-09-12,46.65,16.56,,106.0,Moderate,71,7.2,29.4,0.0,False,3.8427,Monsoon (Jul–Sep)
2017-09-13,54.77,10.76,,115.0,Moderate,69,6.5,29.8,0.0,False,4.0031,Monsoon (Jul–Sep)
2017-09-14,80.47,31.88,,142.0,Moderate,73,6.1,29.5,0.0,False,4.3879,Monsoon (Jul–Sep)
2017-09-15,64.37,34.75,,169.0,Moderate,69,7.8,29.3,0.0,False,4.1646,Monsoon (Jul–Sep)
2017-09-16,51.56,36.6,,110.0,Moderate,71,6.0,28.7,0.0,False,3.9427,Monsoon (Jul–Sep)
2017-09-17,53.05,37.33,,106.0,Moderate,69,9.8,28.7,0.0,False,3.9712,Monsoon (Jul–Sep)
2017-09-18,60.83,56.67,,99.0,Satisfactory,65,9.5,29.1,0.0,False,4.1081,Monsoon (Jul–Sep)
2017-09-19,55.55,34.72,,109.0,Moderate,74,5.8,29.5,0.1,False,4.0173,Monsoon (Jul–Sep)
2017-09-20,70.81,21.49,,137.0,Moderate,67,5.2,30.0,0.0,False,4.26,Monsoon (Jul–Sep)
2017-09-21,55.93,22.74,,144.0,Moderate,72,10.7,29.1,0.0,False,4.0241,Monsoon (Jul–Sep)
2017-09-22,11.81,22.4,,92.0,Satisfactory,85,11.7,25.6,12.4,False,2.4689,Monsoon (Jul–Sep)
2017-09-23,17.76,18.63,,83.0,Satisfactory,91,10.6,24.3,18.0,False,2.8769,Monsoon (Jul–Sep)
2017-09-24,35.5,17.01,,84.0,Satisfactory,83,11.3,25.3,0.0,False,3.5695,Monsoon (Jul–Sep)
2017-09-25,50.09,27.25,,104.0,Moderate,76,10.0,27.5,0.0,False,3.9138,Monsoon (Jul–Sep)
2017-09-26,66.12,27.52,7.13,131.0,Moderate,71,6.5,28.3,0.0,False,4.1915,Monsoon (Jul–Sep)
2017-09-27,80.94,21.39,6.62,165.0,Moderate,66,6.4,28.4,0.0,False,4.3937,Monsoon (Jul–Sep)
2017-09-28,75.4,38.55,6.08,176.0,Moderate,64,6.2,28.6,0.0,False,4.3228,Monsoon (Jul–Sep)
2017-09-29,89.38,29.45,7.17,172.0,Moderate,64,6.8,29.0,0.0,False,4.4929,Monsoon (Jul–Sep)
2017-09-30,74.2,26.08,6.64,137.0,Moderate,63,7.6,28.8,0.0,False,4.3068,Monsoon (Jul–Sep)
2017-10-01,68.47,28.66,3.46,131.0,Moderate,59,6.7,28.4,0.0,False,4.2264,Other months
2017-10-02,63.41,25.2,2.94,132.0,Moderate,57,7.0,29.0,0.0,False,4.1496,Other months
2017-10-03,69.45,26.09,5.81,115.0,Moderate,59,7.9,28.1,0.0,False,4.2406,Other months
2017-10-04,76.81,28.99,11.7,151.0,Moderate,62,7.7,28.1,0.0,False,4.3413,Other months
2017-10-05,75.73,24.45,11.96,180.0,Moderate,65,8.5,28.1,0.0,False,4.3272,Other months
2017-10-06,79.81,27.44,13.91,183.0,Moderate,56,8.9,27.9,0.0,False,4.3796,Other months
2017-10-07,70.98,25.61,22.29,193.0,Moderate,52,6.8,27.7,0.0,False,4.2624,Other months
2017-10-08,102.2,24.51,24.0,224.0,Poor,62,6.4,27.4,0.0,False,4.6269,Other months
2017-10-09,107.63,27.06,23.51,268.0,Poor,63,7.7,27.9,0.0,False,4.6787,Other months
2017-10-10,105.88,31.67,7.6,253.0,Poor,60,6.9,27.9,0.0,False,4.6623,Other months
2017-10-11,104.45,30.92,6.57,208.0,Poor,59,7.2,27.9,0.0,False,4.6487,Other months
2017-10-12,106.85,31.1,7.65,211.0,Poor,55,6.8,28.2,0.0,False,4.6714,Other months
2017-10-13,137.42,29.16,9.36,246.0,Poor,48,7.3,28.1,0.0,False,4.923,Other months
2017-10-14,147.07,30.14,14.64,319.0,Very Poor,51,7.5,28.0,0.0,False,4.9909,Other months
2017-10-15,147.83,30.0,14.31,317.0,Very Poor,52,6.6,28.0,0.0,False,4.9961,Other months
2017-10-16,152.61,58.53,23.09,310.0,Very Poor,52,7.5,27.9,0.0,False,5.0279,Other months
2017-10-17,121.7,57.08,17.44,313.0,Very Poor,51,9.3,26.5,0.0,False,4.8016,Other months
2017-10-18,152.16,63.15,27.42,310.0,Very Poor,62,7.8,26.2,0.0,False,5.0249,Other months
2017-10-19,176.17,53.51,22.15,336.0,Very Poor,63,6.6,27.3,0.0,False,5.1714,Other months
2017-10-20,426.52,54.76,36.85,497.0,Severe,58,7.1,28.0,0.0,False,6.0557,Other months
2017-10-21,213.12,50.13,20.55,404.0,Severe,53,8.5,27.1,0.0,False,5.3619,Other months
2017-10-22,146.01,55.88,24.42,338.0,Very Poor,49,8.3,27.0,0.0,False,4.9837,Other months
2017-10-23,163.35,64.25,27.79,327.0,Very Poor,55,6.7,26.5,0.0,False,5.0959,Other months
2017-10-24,188.24,81.33,23.19,366.0,Very Poor,51,10.2,25.5,0.0,False,5.2377,Other months
2017-10-25,203.03,80.62,23.77,357.0,Very Poor,46,7.0,25.1,0.0,False,5.3134,Other months
2017-10-26,178.91,90.56,24.12,328.0,Very Poor,51,7.2,24.7,0.0,False,5.1869,Other months
2017-10-27,167.54,65.44,21.24,345.0,Very Poor,60,6.4,24.0,0.0,False,5.1212,Other months
2017-10-28,198.37,84.45,27.88,379.0,Very Poor,61,6.8,24.7,0.0,False,5.2901,Other months
2017-10-29,187.82,60.61,25.08,362.0,Very Poor,61,6.5,23.9,0.0,False,5.2355,Other months
2017-10-30,196.37,69.51,23.68,340.0,Very Poor,63,6.4,23.4,0.0,False,5.28,Other months
2017-10-31,211.64,53.08,19.36,366.0,Very Poor,63,4.8,24.0,0.0,False,5.3549,Other months
2017-11-01,179.17,46.83,16.01,344.0,Very Poor,61,7.8,24.4,0.0,False,5.1883,Winter (Nov–Jan)
2017-11-02,160.69,47.7,17.19,305.0,Very Poor,69,6.5,23.9,0.0,False,5.0795,Winter (Nov–Jan)
2017-11-03,168.16,46.49,15.29,310.0,Very Poor,70,6.6,23.4,0.0,False,5.1249,Winter (Nov–Jan)
2017-11-04,190.33,47.28,18.87,345.0,Very Poor,73,7.4,22.9,0.0,False,5.2488,Winter (Nov–Jan)
2017-11-05,209.61,60.56,19.55,370.0,Very Poor,67,4.8,23.9,0.0,False,5.3452,Winter (Nov–Jan)
2017-11-06,216.53,57.27,18.74,377.0,Very Poor,64,6.3,23.7,0.0,False,5.3777,Winter (Nov–Jan)
2017-11-07,517.93,65.17,15.29,532.0,Severe,71,6.2,22.9,0.0,False,6.2498,Winter (Nov–Jan)
2017-11-08,639.19,77.51,20.46,675.0,Severe,68,7.1,22.9,0.0,False,6.4602,Winter (Nov–Jan)
2017-11-09,495.9,81.67,15.68,677.0,Severe,72,7.8,22.2,0.0,False,6.2064,Winter (Nov–Jan)
2017-11-10,370.73,80.73,17.84,597.0,Severe,68,7.8,22.1,0.0,False,5.9155,Winter (Nov–Jan)
2017-11-11,363.77,78.61,17.8,471.0,Severe,69,7.5,21.3,0.0,False,5.8965,Winter (Nov–Jan)
2017-11-12,465.08,70.1,13.94,613.0,Severe,70,7.5,21.0,0.0,False,6.1422,Winter (Nov–Jan)
2017-11-13,354.56,65.77,15.58,561.0,Severe,70,6.4,20.9,0.0,False,5.8709,Winter (Nov–Jan)
2017-11-14,254.36,56.46,13.67,444.0,Severe,66,11.9,21.1,0.0,False,5.5388,Winter (Nov–Jan)
2017-11-15,192.04,57.85,19.24,378.0,Very Poor,64,9.1,20.8,0.0,False,5.2577,Winter (Nov–Jan)
2017-11-16,191.57,53.86,22.89,357.0,Very Poor,66,8.6,20.0,0.2,False,5.2553,Winter (Nov–Jan)
2017-11-17,150.79,47.38,16.32,330.0,Very Poor,69,9.4,19.9,0.1,False,5.0159,Winter (Nov–Jan)
2017-11-18,143.51,43.91,13.3,309.0,Very Poor,67,10.7,20.2,0.1,False,4.9664,Winter (Nov–Jan)
2017-11-19,128.65,45.6,15.12,297.0,Poor,52,12.7,19.0,0.0,False,4.8571,Winter (Nov–Jan)
2017-11-20,171.34,52.73,13.7,329.0,Very Poor,50,11.6,17.0,0.0,False,5.1436,Winter (Nov–Jan)
2017-11-21,178.08,54.75,15.02,341.0,Very Poor,51,11.8,16.5,0.0,False,5.1822,Winter (Nov–Jan)
2017-11-22,177.41,54.64,18.13,348.0,Very Poor,51,11.8,16.7,0.0,False,5.1785,Winter (Nov–Jan)
2017-11-23,175.56,55.04,18.32,340.0,Very Poor,47,11.6,16.6,0.0,False,5.168,Winter (Nov–Jan)
2017-11-24,187.97,64.15,19.2,348.0,Very Poor,47,9.9,16.9,0.0,False,5.2363,Winter (Nov–Jan)
2017-11-25,185.31,76.48,17.95,347.0,Very Poor,52,9.7,17.0,0.0,False,5.222,Winter (Nov–Jan)
2017-11-26,224.37,67.6,21.01,368.0,Very Poor,61,8.4,17.0,0.0,False,5.4133,Winter (Nov–Jan)
2017-11-27,198.34,68.93,18.95,382.0,Very Poor,56,11.1,17.3,0.0,False,5.29,Winter (Nov–Jan)
2017-11-28,167.74,62.53,19.39,360.0,Very Poor,58,8.8,17.4,0.0,False,5.1224,Winter (Nov–Jan)
2017-11-29,215.17,75.37,20.1,359.0,Very Poor,63,7.3,17.8,0.0,False,5.3714,Winter (Nov–Jan)
2017-11-30,219.84,57.73,16.83,388.0,Very Poor,66,7.0,17.4,0.0,False,5.3929,Winter (Nov–Jan)
2017-12-01,190.45,56.83,17.59,377.0,Very Poor,60,5.8,17.1,0.0,False,5.2494,Winter (Nov–Jan)
2017-12-02,208.87,65.66,20.17,356.0,Very Poor,57,5.2,17.3,0.0,False,5.3417,Winter (Nov–Jan)
2017-12-03,240.87,65.83,19.92,384.0,Very Poor,53,4.4,17.4,0.0,False,5.4843,Winter (Nov–Jan)
2017-12-04,261.82,65.49,20.17,415.0,Severe,61,6.4,16.6,0.0,False,5.5677,Winter (Nov–Jan)
2017-12-05,230.56,64.61,18.29,404.0,Severe,60,6.4,17.3,0.0,False,5.4405,Winter (Nov–Jan)
2017-12-06,120.91,51.02,20.88,330.0,Very Poor,51,8.4,17.5,0.0,False,4.795,Winter (Nov–Jan)
2017-12-07,88.95,45.83,18.17,215.0,Poor,37,11.3,17.4,0.1,False,4.4881,Winter (Nov–Jan)
2017-12-08,115.08,53.85,21.69,220.0,Poor,37,11.8,16.7,0.0,False,4.7456,Winter (Nov–Jan)
2017-12-09,165.76,70.14,24.22,312.0,Very Poor,46,7.2,16.7,0.0,False,5.1105,Winter (Nov–Jan)
2017-12-10,230.34,83.94,25.97,389.0,Very Poor,60,5.4,17.0,0.0,False,5.4396,Winter (Nov–Jan)
2017-12-11,218.87,71.25,24.39,406.0,Severe,67,7.0,17.2,2.1,False,5.3885,Winter (Nov–Jan)
2017-12-12,109.18,45.94,11.71,280.0,Poor,84,5.6,16.5,5.6,False,4.693,Winter (Nov–Jan)
2017-12-13,134.99,40.27,10.81,263.0,Poor,83,6.2,14.3,0.0,False,4.9052,Winter (Nov–Jan)
2017-12-14,126.67,36.59,11.18,276.0,Poor,71,9.0,13.6,0.0,False,4.8416,Winter (Nov–Jan)
2017-12-15,127.57,34.73,9.69,292.0,Poor,70,12.5,13.0,0.0,False,4.8487,Winter (Nov–Jan)
2017-12-16,100.72,29.84,4.98,228.0,Poor,63,15.1,12.7,0.0,False,4.6123,Winter (Nov–Jan)
2017-12-17,95.58,37.37,12.68,195.0,Moderate,51,17.0,13.7,0.0,False,4.56,Winter (Nov–Jan)
2017-12-18,115.19,45.8,16.97,223.0,Poor,46,17.8,15.6,0.0,False,4.7466,Winter (Nov–Jan)
2017-12-19,168.33,54.84,23.03,291.0,Poor,59,11.2,14.7,0.0,False,5.1259,Winter (Nov–Jan)
2017-12-20,283.24,66.41,25.0,378.0,Very Poor,74,7.6,15.3,0.0,False,5.6463,Winter (Nov–Jan)
2017-12-21,293.14,61.63,22.54,467.0,Severe,79,8.0,16.2,0.0,False,5.6807,Winter (Nov–Jan)
2017-12-22,157.72,50.73,20.47,370.0,Very Poor,66,14.9,16.3,0.0,False,5.0608,Winter (Nov–Jan)
2017-12-23,117.72,50.97,19.95,253.0,Poor,59,14.0,15.7,0.0,False,4.7683,Winter (Nov–Jan)
2017-12-24,203.18,66.65,23.73,309.0,Very Poor,65,5.4,15.6,0.0,False,5.3141,Winter (Nov–Jan)
2017-12-25,259.0,58.92,23.76,398.0,Very Poor,70,8.8,15.1,0.0,False,5.5568,Winter (Nov–Jan)
2017-12-26,224.42,57.6,22.1,372.0,Very Poor,72,9.8,14.4,0.0,False,5.4135,Winter (Nov–Jan)
2017-12-27,224.27,65.61,23.17,379.0,Very Poor,66,6.9,15.2,0.0,False,5.4129,Winter (Nov–Jan)
2017-12-28,249.17,70.25,25.51,398.0,Very Poor,71,7.9,14.9,0.0,False,5.5181,Winter (Nov–Jan)
2017-12-29,227.28,59.7,25.54,399.0,Very Poor,76,8.1,14.1,0.0,False,5.4262,Winter (Nov–Jan)
2017-12-30,273.56,60.4,21.01,421.0,Severe,76,6.7,14.1,0.0,False,5.6115,Winter (Nov–Jan)
2017-12-31,306.17,66.97,17.97,451.0,Severe,75,6.8,12.9,0.0,False,5.7241,Winter (Nov–Jan)
2018-01-01,303.41,63.92,18.58,462.0,Severe,66,5.9,13.1,0.0,False,5.7151,Winter (Nov–Jan)
2018-01-02,277.48,53.73,12.43,439.0,Severe,69,5.8,13.4,0.0,False,5.6257,Winter (Nov–Jan)
2018-01-03,217.01,52.24,10.28,405.0,Severe,74,7.7,12.2,0.0,False,5.3799,Winter (Nov–Jan)
2018-01-04,248.54,61.57,14.42,394.0,Very Poor,74,7.0,11.8,0.0,False,5.5156,Winter (Nov–Jan)
2018-01-05,240.42,54.8,13.2,398.0,Very Poor,74,6.8,12.3,0.0,False,5.4824,Winter (Nov–Jan)
2018-01-06,252.57,59.12,18.15,403.0,Severe,76,7.4,12.0,0.0,False,5.5317,Winter (Nov–Jan)
2018-01-07,191.66,47.02,16.27,384.0,Very Poor,69,12.0,11.9,0.0,False,5.2557,Winter (Nov–Jan)
2018-01-08,152.98,51.6,17.15,314.0,Very Poor,70,10.8,12.1,0.0,False,5.0303,Winter (Nov–Jan)
2018-01-09,233.1,66.19,21.82,373.0,Very Poor,71,9.6,12.1,0.0,False,5.4515,Winter (Nov–Jan)
2018-01-10,186.26,60.21,18.98,366.0,Very Poor,68,14.3,13.3,0.0,False,5.2271,Winter (Nov–Jan)
2018-01-11,154.64,63.57,17.4,318.0,Very Poor,63,14.7,13.9,0.0,False,5.0411,Winter (Nov–Jan)
2018-01-12,168.87,65.3,24.03,306.0,Very Poor,58,10.9,14.8,0.0,False,5.1291,Winter (Nov–Jan)
2018-01-13,230.5,61.28,24.28,370.0,Very Poor,69,8.1,14.0,0.0,False,5.4403,Winter (Nov–Jan)
2018-01-14,191.47,54.37,22.47,365.0,Very Poor,69,9.8,13.5,0.0,False,5.2547,Winter (Nov–Jan)
2018-01-15,177.71,52.51,19.12,352.0,Very Poor,63,12.0,13.9,0.0,False,5.1802,Winter (Nov–Jan)
2018-01-16,133.56,46.86,19.06,278.0,Poor,57,12.1,14.6,0.0,False,4.8946,Winter (Nov–Jan)
2018-01-17,235.06,47.86,14.48,350.0,Very Poor,74,10.3,13.6,0.0,False,5.4598,Winter (Nov–Jan)
2018-01-18,276.25,55.08,21.02,411.0,Severe,76,7.4,15.1,0.0,False,5.6213,Winter (Nov–Jan)
2018-01-19,253.7,49.45,22.27,451.0,Severe,74,9.1,15.6,0.0,False,5.5362,Winter (Nov–Jan)
2018-01-20,152.33,38.87,14.45,351.0,Very Poor,64,11.9,14.5,0.0,False,5.026,Winter (Nov–Jan)
2018-01-21,153.61,44.09,16.91,310.0,Very Poor,57,6.8,14.1,0.0,False,5.0344,Winter (Nov–Jan)
2018-01-22,202.11,56.45,21.64,362.0,Very Poor,67,7.8,14.1,0.0,False,5.3088,Winter (Nov–Jan)
2018-01-23,160.79,47.26,14.25,343.0,Very Poor,79,11.9,13.4,6.0,False,5.0801,Winter (Nov–Jan)
2018-01-24,130.16,35.33,11.9,286.0,Poor,82,7.6,12.7,0.8,False,4.8688,Winter (Nov–Jan)
2018-01-25,111.75,40.13,6.84,267.0,Poor,79,11.6,13.1,0.0,False,4.7163,Winter (Nov–Jan)
2018-01-26,128.45,38.17,7.99,263.0,Poor,80,8.5,12.5,0.0,False,4.8555,Winter (Nov–Jan)
2018-01-27,155.2,45.14,7.94,284.0,Poor,77,9.0,12.1,0.0,False,5.0447,Winter (Nov–Jan)
2018-01-28,150.96,47.6,10.26,334.0,Very Poor,75,9.1,12.8,0.0,False,5.017,Winter (Nov–Jan)
2018-01-29,162.48,54.51,12.61,332.0,Very Poor,74,10.6,13.8,0.0,False,5.0906,Winter (Nov–Jan)
2018-01-30,126.84,47.59,14.47,300.0,Poor,68,16.7,16.3,0.0,False,4.8429,Winter (Nov–Jan)
2018-01-31,123.48,45.46,11.35,271.0,Poor,64,18.4,17.6,0.0,False,4.8161,Winter (Nov–Jan)
2018-02-01,157.33,63.88,18.67,293.0,Poor,67,10.9,17.4,0.0,False,5.0583,Other months
2018-02-02,140.35,54.28,12.25,318.0,Very Poor,72,7.8,16.8,0.0,False,4.9441,Other months
2018-02-03,115.05,51.46,14.2,277.0,Poor,60,9.1,16.3,0.0,False,4.7454,Other months
2018-02-04,133.8,46.74,13.2,284.0,Poor,59,11.0,14.4,0.0,False,4.8963,Other months
2018-02-05,163.6,63.42,14.77,313.0,Very Poor,56,8.0,14.8,0.0,False,5.0974,Other months
2018-02-06,143.29,56.51,14.94,324.0,Very Poor,52,11.5,16.0,0.0,False,4.9649,Other months
2018-02-07,131.49,54.53,14.58,287.0,Poor,53,12.4,14.4,0.0,False,4.8789,Other months
2018-02-08,186.19,74.83,13.8,334.0,Very Poor,60,9.2,13.8,0.0,False,5.2268,Other months
2018-02-09,203.33,74.5,14.35,375.0,Very Poor,60,9.1,14.4,0.0,False,5.3148,Other months
2018-02-10,209.7,99.06,13.77,378.0,Very Poor,51,6.2,16.7,0.0,False,5.3457,Other months
2018-02-11,148.13,62.4,14.45,350.0,Very Poor,57,11.4,16.2,1.6,False,4.9981,Other months
2018-02-12,72.36,33.08,8.58,218.0,Poor,79,16.6,15.8,2.9,False,4.2817,Other months
2018-02-13,103.93,46.48,10.25,189.0,Moderate,79,7.8,15.4,0.0,False,4.6437,Other months
2018-02-14,76.92,34.92,9.03,217.0,Poor,66,14.8,15.5,0.0,False,4.3428,Other months
2018-02-15,94.49,38.54,11.47,189.0,Moderate,64,15.6,16.8,0.0,False,4.5485,Other months
2018-02-16,123.19,48.33,12.49,248.0,Poor,66,11.8,17.7,0.0,False,4.8137,Other months
2018-02-17,127.8,49.9,15.01,277.0,Poor,67,11.7,18.0,0.0,False,4.8505,Other months
2018-02-18,127.27,50.94,12.17,284.0,Poor,59,9.7,17.6,0.0,False,4.8463,Other months
2018-02-19,172.55,71.76,15.25,321.0,Very Poor,58,7.6,17.4,0.0,False,5.1507,Other months
2018-02-20,167.16,68.29,14.53,335.0,Very Poor,60,8.2,19.4,0.0,False,5.119,Other months
2018-02-21,172.99,92.54,13.97,347.0,Very Poor,58,6.9,21.4,0.0,False,5.1532,Other months
2018-02-22,159.67,66.4,15.89,333.0,Very Poor,63,7.8,21.7,0.0,False,5.0731,Other months
2018-02-23,163.75,70.77,16.26,331.0,Very Poor,69,6.3,21.9,0.0,False,5.0983,Other months
2018-02-24,164.2,62.66,15.09,347.0,Very Poor,73,8.5,21.1,1.9,False,5.1011,Other months
2018-02-25,106.26,42.88,14.34,317.0,Very Poor,68,9.8,21.0,0.3,False,4.6659,Other months
2018-02-26,67.27,33.59,9.64,170.0,Moderate,63,16.8,20.5,0.0,False,4.2087,Other months
2018-02-27,85.53,43.12,10.72,167.0,Moderate,62,11.4,21.5,0.0,False,4.4489,Other months
2018-02-28,143.25,52.5,14.52,274.0,Poor,67,8.2,21.6,0.0,False,4.9646,Other months
2018-03-01,120.71,51.74,14.9,293.0,Poor,65,9.0,21.4,0.0,False,4.7934,Other months
2018-03-02,139.18,50.64,11.52,300.0,Poor,58,8.8,23.1,0.0,False,4.9358,Other months
2018-03-03,98.25,41.07,12.93,244.0,Poor,60,7.7,22.6,0.0,False,4.5875,Other months
2018-03-04,79.83,39.02,12.95,205.0,Poor,59,10.6,21.5,1.2,False,4.3799,Other months
2018-03-05,76.96,39.58,12.7,180.0,Moderate,57,10.0,20.4,0.0,False,4.3433,Other months
2018-03-06,75.45,37.92,12.99,170.0,Moderate,53,12.5,20.3,0.0,False,4.3235,Other months
2018-03-07,87.62,45.6,13.23,192.0,Moderate,52,11.6,21.1,0.0,False,4.473,Other months
2018-03-08,139.88,79.5,16.98,262.0,Poor,53,5.2,22.3,0.0,False,4.9408,Other months
2018-03-09,134.76,65.86,18.68,316.0,Very Poor,52,8.8,22.9,1.1,False,4.9035,Other months
2018-03-10,75.67,39.85,14.8,207.0,Poor,48,12.4,23.1,0.0,False,4.3264,Other months
2018-03-11,88.3,41.81,15.41,179.0,Moderate,52,11.6,23.3,0.0,False,4.4807,Other months
2018-03-12,105.29,45.32,17.48,236.0,Poor,53,10.8,23.7,0.0,False,4.6567,Other months
2018-03-13,109.22,56.5,17.22,241.0,Poor,49,9.0,25.4,0.0,False,4.6934,Other months
2018-03-14,116.62,64.82,17.39,287.0,Poor,37,8.7,25.8,0.0,False,4.7589,Other months
2018-03-15,108.98,48.86,16.08,314.0,Very Poor,42,9.8,23.8,0.0,False,4.6912,Other months
2018-03-16,111.67,41.48,16.61,269.0,Poor,48,9.7,22.7,0.0,False,4.7155,Other months
2018-03-17,81.57,32.61,13.63,218.0,Poor,40,12.3,21.9,0.0,False,4.4015,Other months
2018-03-18,82.15,31.72,17.22,177.0,Moderate,41,11.3,22.7,0.0,False,4.4085,Other months
2018-03-19,81.93,43.85,16.95,177.0,Moderate,41,8.5,23.6,0.0,False,4.4059,Other months
2018-03-20,109.99,55.71,20.52,224.0,Poor,49,6.5,24.3,0.2,False,4.7004,Other months
2018-03-21,133.53,45.33,24.36,302.0,Very Poor,56,10.7,23.6,1.6,False,4.8943,Other months
2018-03-22,83.4,33.49,17.14,226.0,Poor,56,8.3,23.0,0.3,False,4.4236,Other months
2018-03-23,64.2,34.53,12.75,171.0,Moderate,54,9.4,23.0,0.0,False,4.162,Other months
2018-03-24,78.4,37.32,14.56,183.0,Moderate,48,10.8,24.3,0.0,False,4.3618,Other months
2018-03-25,85.34,34.66,15.57,202.0,Poor,44,12.8,25.0,0.0,False,4.4466,Other months
2018-03-26,85.9,41.2,16.28,203.0,Poor,42,13.6,26.0,0.0,False,4.4532,Other months
2018-03-27,111.26,60.75,18.5,246.0,Poor,40,9.8,26.3,0.0,False,4.7119,Other months
2018-03-28,117.78,71.04,16.27,293.0,Poor,37,9.4,27.9,0.0,False,4.7688,Other months
2018-03-29,95.98,41.56,16.53,238.0,Poor,34,13.4,27.2,0.0,False,4.5641,Other months
2018-03-30,96.45,45.84,15.95,234.0,Poor,34,14.4,26.8,0.0,False,4.569,Other months
2018-03-31,101.59,44.76,16.59,269.0,Poor,47,11.9,25.7,0.0,False,4.6209,Other months
2018-04-01,75.14,37.97,14.13,217.0,Poor,45,10.7,26.5,0.0,False,4.3194,Other months
2018-04-02,96.38,48.52,16.54,217.0,Poor,45,8.5,28.0,0.0,False,4.5683,Other months
2018-04-03,101.18,51.63,17.36,239.0,Poor,44,9.0,28.7,1.7,False,4.6169,Other months
2018-04-04,111.82,52.51,16.58,244.0,Poor,43,8.3,29.2,0.0,False,4.7169,Other months
2018-04-05,152.56,60.24,19.67,329.0,Very Poor,49,6.4,28.6,2.1,False,5.0276,Other months
2018-04-06,100.5,44.92,19.96,271.0,Poor,52,6.9,27.9,1.1,False,4.6102,Other months
2018-04-07,48.46,36.94,10.48,170.0,Moderate,54,10.6,26.9,3.4,False,3.8807,Other months
2018-04-08,50.27,34.29,10.5,142.0,Moderate,55,13.0,26.7,1.3,False,3.9174,Other months
2018-04-09,49.56,39.45,10.77,133.0,Moderate,62,10.3,25.6,3.5,False,3.9032,Other months
2018-04-10,93.89,45.16,12.65,205.0,Poor,58,8.6,26.7,3.1,False,4.5421,Other months
2018-04-11,48.61,32.33,11.21,179.0,Moderate,63,12.8,25.3,2.5,False,3.8838,Other months
2018-04-12,46.21,40.94,10.07,135.0,Moderate,61,6.1,25.4,0.2,False,3.8332,Other months
2018-04-13,83.96,54.68,13.37,201.0,Poor,43,8.5,26.2,0.0,False,4.4303,Other months
2018-04-14,97.16,59.41,15.77,233.0,Poor,34,10.4,27.2,0.0,False,4.5764,Other months
2018-04-15,107.36,67.79,17.56,240.0,Poor,35,8.8,28.8,0.0,False,4.6762,Other months
2018-04-16,119.75,76.17,21.02,296.0,Poor,36,10.5,29.2,5.4,False,4.7854,Other months
2018-04-17,81.97,57.84,13.57,266.0,Poor,35,8.9,29.4,1.3,False,4.4064,Other months
2018-04-18,73.44,40.44,13.29,216.0,Poor,28,15.5,29.4,0.0,False,4.2965,Other months
2018-04-19,89.49,51.78,16.76,242.0,Poor,28,11.5,30.0,0.0,False,4.4941,Other months
2018-04-20,100.01,40.56,15.55,271.0,Poor,27,16.2,30.3,1.1,False,4.6053,Other months
2018-04-21,119.24,30.99,12.08,444.0,Severe,34,12.4,27.0,0.0,False,4.7811,Other months
2018-04-22,62.06,31.63,16.92,302.0,Very Poor,25,15.0,27.5,0.0,False,4.1281,Other months
2018-04-23,76.11,39.43,12.89,197.0,Moderate,23,13.6,28.3,0.0,False,4.3322,Other months
2018-04-24,108.64,57.07,17.01,242.0,Poor,20,10.1,30.1,0.0,False,4.688,Other months
2018-04-25,117.56,82.47,15.1,287.0,Poor,20,10.2,31.8,0.0,False,4.7669,Other months
2018-04-26,142.82,78.5,17.89,329.0,Very Poor,20,9.1,32.5,0.0,False,4.9616,Other months
2018-04-27,107.47,49.86,12.96,351.0,Very Poor,43,13.5,30.9,1.2,False,4.6772,Other months
2018-04-28,84.13,36.11,12.38,288.0,Poor,44,13.3,30.7,0.9,False,4.4324,Other months
2018-04-29,89.1,42.57,16.1,259.0,Poor,43,9.8,30.8,0.4,False,4.4898,Other months
2018-04-30,79.3,46.42,11.9,221.0,Poor,42,11.3,31.0,0.7,False,4.3732,Other months
2018-05-01,54.88,33.37,8.8,173.0,Moderate,52,17.7,30.5,10.5,False,4.0051,Other months
2018-05-02,66.74,34.14,7.65,161.0,Moderate,54,17.1,29.8,5.9,False,4.2008,Other months
2018-05-03,47.25,31.77,9.52,167.0,Moderate,58,16.1,28.7,0.0,False,3.8555,Other months
2018-05-04,49.09,30.44,9.06,146.0,Moderate,55,13.5,29.0,0.0,False,3.8937,Other months
2018-05-05,74.82,46.75,11.85,174.0,Moderate,48,7.7,30.3,0.0,False,4.3151,Other months
2018-05-06,110.48,53.69,14.61,280.0,Poor,38,10.4,31.0,0.0,False,4.7048,Other months
2018-05-07,111.95,54.75,16.31,243.0,Poor,37,8.6,30.5,0.0,False,4.7181,Other months
2018-05-08,61.0,27.66,6.97,252.0,Poor,46,9.1,27.2,3.5,False,4.1109,Other months
2018-05-09,71.99,46.09,12.35,168.0,Moderate,44,7.2,28.1,2.2,False,4.2765,Other months
2018-05-10,93.45,52.15,12.02,218.0,Poor,38,8.3,30.2,0.0,False,4.5374,Other months
2018-05-11,132.39,65.41,16.58,292.0,Poor,36,9.2,32.5,0.0,False,4.8858,Other months
2018-05-12,144.33,74.13,17.75,330.0,Very Poor,42,9.6,32.3,1.1,False,4.9721,Other months
2018-05-13,80.64,31.22,11.48,285.0,Poor,56,11.7,29.6,3.8,False,4.39,Other months
2018-05-14,49.22,40.3,11.3,174.0,Moderate,52,8.0,30.0,0.0,False,3.8963,Other months
2018-05-15,67.23,39.81,11.9,173.0,Moderate,50,8.4,31.2,0.0,False,4.2081,Other months
2018-05-16,78.74,41.79,9.25,194.0,Moderate,42,8.1,31.9,0.4,False,4.3662,Other months
2018-05-17,105.99,44.14,13.61,240.0,Poor,30,8.2,32.7,0.0,False,4.6633,Other months
2018-05-18,96.96,53.88,13.97,254.0,Poor,32,6.9,32.5,0.0,False,4.5743,Other months
2018-05-19,103.98,65.52,12.48,270.0,Poor,38,6.5,32.1,1.5,False,4.6442,Other months
2018-05-20,83.66,45.88,12.65,231.0,Poor,28,10.2,32.9,0.0,False,4.4268,Other months
2018-05-21,71.25,42.68,12.73,208.0,Poor,17,11.7,33.7,0.0,False,4.2662,Other months
2018-05-22,91.16,59.07,15.56,207.0,Poor,18,9.8,35.5,0.0,False,4.5126,Other months
2018-05-23,129.23,77.28,17.57,306.0,Very Poor,26,10.2,34.5,0.1,False,4.8616,Other months
2018-05-24,114.13,57.51,17.78,303.0,Very Poor,30,9.2,33.8,0.0,False,4.7373,Other months
2018-05-25,83.88,59.34,12.73,260.0,Poor,25,9.3,34.6,0.0,False,4.4294,Other months
2018-05-26,103.02,64.88,14.9,244.0,Poor,17,9.2,34.9,0.0,False,4.6349,Other months
2018-05-27,97.37,58.31,11.59,268.0,Poor,19,10.8,35.3,0.0,False,4.5785,Other months
2018-05-28,117.56,54.01,15.54,276.0,Poor,28,9.2,34.8,0.0,False,4.7669,Other months
2018-05-29,112.6,60.34,11.93,303.0,Very Poor,33,12.6,34.0,0.0,False,4.7238,Other months
2018-05-30,65.76,33.21,8.58,272.0,Poor,49,14.3,32.8,0.7,False,4.186,Other months
2018-05-31,71.99,40.76,9.71,223.0,Poor,45,11.1,34.3,0.0,False,4.2765,Other months
2018-06-01,79.98,30.14,8.24,196.0,Moderate,48,18.0,33.9,4.8,False,4.3818,Other months
2018-06-02,52.6,29.28,9.08,183.0,Moderate,49,15.6,33.0,0.0,False,3.9627,Other months
2018-06-03,59.52,31.51,7.79,154.0,Moderate,53,13.3,32.9,0.0,False,4.0863,Other months
2018-06-04,64.42,30.68,8.14,170.0,Moderate,45,16.0,34.9,0.0,False,4.1654,Other months
2018-06-05,61.72,27.67,7.51,160.0,Moderate,45,16.1,35.3,0.7,False,4.1226,Other months
2018-06-06,57.68,31.11,9.34,146.0,Moderate,55,12.3,33.4,0.8,False,4.0549,Other months
2018-06-07,73.77,33.8,10.1,166.0,Moderate,53,8.3,34.1,0.0,False,4.301,Other months
2018-06-08,76.78,31.27,7.75,180.0,Moderate,52,16.1,34.8,0.0,False,4.3409,Other months
2018-06-09,52.79,27.39,6.41,153.0,Moderate,69,14.0,31.5,15.2,False,3.9663,Other months
2018-06-10,67.02,34.23,7.35,153.0,Moderate,68,6.6,31.5,1.9,False,4.205,Other months
2018-06-11,73.22,34.85,6.94,186.0,Moderate,52,11.1,34.0,0.0,False,4.2935,Other months
2018-06-12,141.28,31.72,8.73,285.0,Poor,40,13.5,35.5,0.0,False,4.9507,Other months
2018-06-13,261.77,25.75,6.91,453.0,Severe,38,16.8,36.4,0.0,False,5.5675,Other months
2018-06-14,225.49,25.37,7.22,522.0,Severe,37,19.8,36.0,0.0,False,5.4183,Other months
2018-06-15,153.28,24.61,7.31,593.0,Severe,36,17.8,35.5,0.0,False,5.0323,Other months
2018-06-16,127.32,25.0,7.29,531.0,Severe,41,14.1,34.9,0.0,False,4.8467,Other months
2018-06-17,84.47,22.78,6.18,384.0,Very Poor,58,10.4,31.7,0.2,False,4.4364,Other months
2018-06-18,61.06,26.68,7.71,179.0,Moderate,55,8.2,31.1,0.6,False,4.1119,Other months
2018-06-19,52.76,26.52,6.5,146.0,Moderate,51,8.5,32.6,0.0,False,3.9658,Other months
2018-06-20,67.55,33.71,10.05,175.0,Moderate,45,5.7,34.9,0.0,False,4.2129,Other months
2018-06-21,76.98,34.82,9.73,221.0,Poor,42,7.4,35.4,0.0,False,4.3435,Other months
2018-06-22,83.98,45.06,12.38,249.0,Poor,38,5.8,36.5,0.0,False,4.4306,Other months
2018-06-23,81.33,44.23,11.68,228.0,Poor,39,8.5,35.9,0.0,False,4.3985,Other months
2018-06-24,54.15,34.98,13.73,194.0,Moderate,39,9.2,35.6,0.0,False,3.9918,Other months
2018-06-25,46.9,34.92,12.17,168.0,Moderate,36,13.2,36.3,0.0,False,3.848,Other months
2018-06-26,29.98,34.16,13.16,128.0,Moderate,52,9.3,32.9,1.8,False,3.4005,Other months
2018-06-27,52.48,31.0,10.43,126.0,Moderate,78,9.0,29.2,29.8,False,3.9604,Other months
2018-06-28,30.07,29.01,8.48,99.0,Satisfactory,81,14.5,28.6,12.6,False,3.4035,Other months
2018-06-29,37.11,30.43,9.36,90.0,Satisfactory,76,16.6,29.4,4.3,False,3.6139,Other months
2018-06-30,41.41,32.89,9.55,113.0,Moderate,79,8.5,29.6,4.9,False,3.7235,Other months
2018-07-01,34.18,28.46,8.53,102.0,Moderate,75,10.8,30.7,4.7,False,3.5316,Monsoon (Jul–Sep)
2018-07-02,34.24,25.74,8.82,111.0,Moderate,72,12.0,30.6,15.2,False,3.5334,Monsoon (Jul–Sep)
2018-07-03,44.55,37.27,10.11,122.0,Moderate,68,8.6,30.6,0.7,False,3.7966,Monsoon (Jul–Sep)
2018-07-04,45.76,31.17,10.14,128.0,Moderate,78,8.9,29.1,4.8,False,3.8234,Monsoon (Jul–Sep)
2018-07-05,50.41,38.05,11.14,130.0,Moderate,71,6.0,30.8,0.0,False,3.9202,Monsoon (Jul–Sep)
2018-07-06,57.12,36.71,10.27,147.0,Moderate,67,8.2,31.1,0.0,False,4.0452,Monsoon (Jul–Sep)
2018-07-07,61.93,34.43,10.4,155.0,Moderate,65,7.8,31.7,0.0,False,4.126,Monsoon (Jul–Sep)
2018-07-08,68.2,39.85,11.6,176.0,Moderate,61,6.3,32.9,0.0,False,4.2224,Monsoon (Jul–Sep)
2018-07-09,70.48,35.14,11.0,168.0,Moderate,64,9.6,32.9,0.1,False,4.2553,Monsoon (Jul–Sep)
2018-07-10,47.48,28.19,10.92,140.0,Moderate,67,11.8,32.8,0.3,False,3.8603,Monsoon (Jul–Sep)
2018-07-11,39.78,31.82,11.26,111.0,Moderate,72,9.6,31.8,4.5,False,3.6834,Monsoon (Jul–Sep)
2018-07-12,46.53,34.22,10.92,130.0,Moderate,80,7.9,29.6,25.5,False,3.8401,Monsoon (Jul–Sep)
2018-07-13,28.44,31.94,10.69,109.0,Moderate,82,8.3,29.1,6.6,False,3.3478,Monsoon (Jul–Sep)
2018-07-14,33.82,31.63,11.13,96.0,Satisfactory,85,8.6,28.5,6.4,False,3.5211,Monsoon (Jul–Sep)
2018-07-15,37.76,28.9,10.64,92.0,Satisfactory,83,9.4,29.4,7.4,False,3.6313,Monsoon (Jul–Sep)
2018-07-16,37.32,33.31,9.51,95.0,Satisfactory,85,9.3,29.1,10.9,False,3.6195,Monsoon (Jul–Sep)
2018-07-17,34.26,30.73,10.2,105.0,Moderate,80,9.3,30.4,3.5,False,3.534,Monsoon (Jul–Sep)
2018-07-18,37.76,29.45,11.04,114.0,Moderate,80,9.8,30.1,12.2,False,3.6313,Monsoon (Jul–Sep)
2018-07-19,35.04,27.41,11.14,106.0,Moderate,80,6.5,30.1,13.3,False,3.5565,Monsoon (Jul–Sep)
2018-07-20,37.26,33.46,10.4,90.0,Satisfactory,84,4.2,29.4,8.3,False,3.6179,Monsoon (Jul–Sep)
2018-07-21,50.21,36.48,11.2,114.0,Moderate,89,5.5,28.4,20.9,False,3.9162,Monsoon (Jul–Sep)
2018-07-22,25.81,27.55,9.85,87.0,Satisfactory,91,4.9,27.4,30.6,False,3.2508,Monsoon (Jul–Sep)
2018-07-23,32.39,28.74,10.43,80.0,Satisfactory,86,6.5,28.8,5.1,False,3.4778,Monsoon (Jul–Sep)
2018-07-24,39.3,29.15,10.78,101.0,Moderate,78,5.0,30.0,1.5,False,3.6712,Monsoon (Jul–Sep)
2018-07-25,34.7,27.58,9.99,90.0,Satisfactory,85,6.6,28.8,8.2,False,3.5467,Monsoon (Jul–Sep)
2018-07-26,32.22,25.1,9.27,90.0,Satisfactory,91,7.1,26.9,16.3,False,3.4726,Monsoon (Jul–Sep)
2018-07-27,21.75,23.41,9.13,68.0,Satisfactory,90,6.6,26.8,14.2,False,3.0796,Monsoon (Jul–Sep)
2018-07-28,37.69,21.59,9.55,71.0,Satisfactory,83,12.6,28.1,2.8,False,3.6294,Monsoon (Jul–Sep)
2018-07-29,44.03,25.02,9.37,100.0,Satisfactory,82,9.2,29.0,2.4,False,3.7849,Monsoon (Jul–Sep)
2018-07-30,39.89,25.06,8.96,122.0,Moderate,79,10.4,29.2,2.4,False,3.6861,Monsoon (Jul–Sep)
2018-07-31,50.59,28.84,9.12,135.0,Moderate,76,11.9,29.7,2.5,False,3.9238,Monsoon (Jul–Sep)
2018-08-01,55.77,26.14,9.71,155.0,Moderate,74,12.5,29.9,0.4,False,4.0212,Monsoon (Jul–Sep)
2018-08-02,71.5,25.2,10.22,215.0,Poor,70,12.0,30.5,0.2,False,4.2697,Monsoon (Jul–Sep)
2018-08-03,65.46,26.08,9.48,228.0,Poor,67,13.1,30.4,0.0,False,4.1814,Monsoon (Jul–Sep)
2018-08-04,69.75,28.77,9.61,215.0,Poor,66,12.4,30.4,0.0,False,4.2449,Monsoon (Jul–Sep)
2018-08-05,63.57,24.82,9.86,234.0,Poor,72,11.8,29.1,1.3,False,4.1521,Monsoon (Jul–Sep)
2018-08-06,50.64,26.59,9.4,166.0,Moderate,86,5.7,26.8,4.6,False,3.9247,Monsoon (Jul–Sep)
2018-08-07,44.54,26.15,10.65,123.0,Moderate,91,4.9,26.6,19.4,False,3.7964,Monsoon (Jul–Sep)
2018-08-08,36.7,25.24,9.47,108.0,Moderate,86,8.4,27.9,9.4,False,3.6028,Monsoon (Jul–Sep)
2018-08-09,36.84,24.98,9.85,102.0,Moderate,82,8.6,29.2,2.9,False,3.6066,Monsoon (Jul–Sep)
2018-08-10,46.24,34.82,9.66,111.0,Moderate,83,5.7,29.5,2.9,False,3.8338,Monsoon (Jul–Sep)
2018-08-11,32.72,24.06,8.84,106.0,Moderate,78,13.7,29.8,2.7,False,3.488,Monsoon (Jul–Sep)
2018-08-12,25.7,23.5,9.09,92.0,Satisfactory,79,9.2,28.8,2.1,False,3.2465,Monsoon (Jul–Sep)
2018-08-13,32.75,25.04,9.26,102.0,Moderate,77,5.2,29.1,2.5,False,3.4889,Monsoon (Jul–Sep)
2018-08-14,46.85,29.49,9.86,122.0,Moderate,79,6.3,29.3,1.0,False,3.847,Monsoon (Jul–Sep)
2018-08-15,43.0,23.72,8.85,128.0,Moderate,84,7.4,29.0,7.4,False,3.7612,Monsoon (Jul–Sep)
2018-08-16,36.49,29.32,10.43,109.0,Moderate,85,6.9,29.1,3.4,False,3.597,Monsoon (Jul–Sep)
2018-08-17,32.98,24.58,9.26,109.0,Moderate,83,10.1,29.4,3.4,False,3.4959,Monsoon (Jul–Sep)
2018-08-18,32.11,26.17,10.05,90.0,Satisfactory,84,7.2,29.2,6.4,False,3.4692,Monsoon (Jul–Sep)
2018-08-19,47.01,31.85,11.4,100.0,Satisfactory,87,6.0,28.9,4.9,False,3.8504,Monsoon (Jul–Sep)
2018-08-20,61.1,32.54,10.88,138.0,Moderate,86,5.3,29.2,3.6,False,4.1125,Monsoon (Jul–Sep)
2018-08-21,30.98,27.85,11.99,105.0,Moderate,85,6.6,29.5,2.5,False,3.4333,Monsoon (Jul–Sep)
2018-08-22,29.75,28.18,11.43,91.0,Satisfactory,84,5.7,29.3,10.1,False,3.3928,Monsoon (Jul–Sep)
2018-08-23,31.19,24.72,10.82,86.0,Satisfactory,88,7.6,28.3,12.4,False,3.4401,Monsoon (Jul–Sep)
2018-08-24,23.71,24.6,10.4,89.0,Satisfactory,83,10.1,28.6,9.1,False,3.1659,Monsoon (Jul–Sep)
2018-08-25,21.96,22.78,10.9,100.0,Satisfactory,79,12.5,28.5,1.8,False,3.0892,Monsoon (Jul–Sep)
2018-08-26,23.96,19.92,10.31,85.0,Satisfactory,80,8.4,28.6,1.7,False,3.1764,Monsoon (Jul–Sep)
2018-08-27,24.78,23.6,10.82,82.0,Satisfactory,89,4.2,27.5,6.0,False,3.21,Monsoon (Jul–Sep)
2018-08-28,29.26,25.52,10.84,81.0,Satisfactory,88,7.4,27.6,14.0,False,3.3762,Monsoon (Jul–Sep)
2018-08-29,36.06,26.12,10.23,88.0,Satisfactory,89,5.9,28.0,4.6,False,3.5852,Monsoon (Jul–Sep)
2018-08-30,41.26,28.28,9.97,97.0,Satisfactory,85,6.2,29.0,3.5,False,3.7199,Monsoon (Jul–Sep)
2018-08-31,47.53,25.96,9.67,127.0,Moderate,81,8.8,29.5,1.2,False,3.8614,Monsoon (Jul–Sep)
2018-09-01,45.19,28.51,10.53,132.0,Moderate,86,5.1,28.3,1.3,False,3.8109,Monsoon (Jul–Sep)
2018-09-02,40.9,23.44,9.81,116.0,Moderate,90,4.7,26.7,32.7,False,3.7111,Monsoon (Jul–Sep)
2018-09-03,42.06,27.63,9.96,89.0,Satisfactory,90,4.2,26.7,8.2,False,3.7391,Monsoon (Jul–Sep)
2018-09-04,55.72,35.94,10.8,118.0,Moderate,91,4.8,26.7,9.0,False,4.0203,Monsoon (Jul–Sep)
2018-09-05,39.77,30.63,9.62,108.0,Moderate,85,8.4,27.7,0.9,False,3.6831,Monsoon (Jul–Sep)
2018-09-06,49.44,30.88,10.13,137.0,Moderate,83,6.4,28.0,7.9,False,3.9008,Monsoon (Jul–Sep)
2018-09-07,42.11,37.91,10.75,117.0,Moderate,88,6.8,27.9,8.6,False,3.7403,Monsoon (Jul–Sep)
2018-09-08,35.45,26.65,11.38,105.0,Moderate,86,13.1,27.4,8.0,False,3.5681,Monsoon (Jul–Sep)
2018-09-09,29.1,23.58,10.98,86.0,Satisfactory,83,14.1,27.0,0.2,False,3.3707,Monsoon (Jul–Sep)
2018-09-10,36.99,29.61,11.21,92.0,Satisfactory,83,7.0,27.5,2.4,False,3.6106,Monsoon (Jul–Sep)
2018-09-11,28.33,26.0,9.77,91.0,Satisfactory,84,8.4,27.8,3.0,False,3.3439,Monsoon (Jul–Sep)
2018-09-12,28.55,24.4,10.31,96.0,Satisfactory,76,14.8,28.5,0.4,False,3.3517,Monsoon (Jul–Sep)
2018-09-13,27.49,23.21,11.24,108.0,Moderate,71,13.6,28.5,0.0,False,3.3138,Monsoon (Jul–Sep)
2018-09-14,31.38,25.18,11.21,113.0,Moderate,71,9.4,27.8,0.0,False,3.4462,Monsoon (Jul–Sep)
2018-09-15,37.48,27.72,11.74,126.0,Moderate,70,8.6,27.9,0.0,False,3.6238,Monsoon (Jul–Sep)
2018-09-16,43.09,25.92,11.14,124.0,Moderate,68,9.0,28.0,0.0,False,3.7633,Monsoon (Jul–Sep)
2018-09-17,55.86,29.15,11.12,135.0,Moderate,71,7.8,28.1,0.0,False,4.0228,Monsoon (Jul–Sep)
2018-09-18,54.94,29.8,11.95,154.0,Moderate,69,8.9,27.6,0.0,False,4.0062,Monsoon (Jul–Sep)
2018-09-19,58.63,37.36,13.43,157.0,Moderate,69,8.8,27.7,0.0,False,4.0712,Monsoon (Jul–Sep)
2018-09-20,73.3,38.16,14.41,173.0,Moderate,70,5.4,28.4,0.0,False,4.2946,Monsoon (Jul–Sep)
2018-09-21,46.73,26.7,12.74,155.0,Moderate,78,13.2,27.2,6.2,False,3.8444,Monsoon (Jul–Sep)
2018-09-22,24.29,21.72,11.11,76.0,Satisfactory,88,17.1,24.9,50.6,False,3.1901,Monsoon (Jul–Sep)
2018-09-23,30.71,19.88,11.59,69.0,Satisfactory,89,20.6,25.4,15.6,False,3.4246,Monsoon (Jul–Sep)
2018-09-24,21.46,25.07,11.08,63.0,Satisfactory,92,15.6,24.6,12.8,False,3.0662,Monsoon (Jul–Sep)
2018-09-25,21.45,25.67,10.88,63.0,Satisfactory,85,13.2,25.2,0.3,False,3.0657,Monsoon (Jul–Sep)
2018-09-26,42.83,32.38,11.59,99.0,Satisfactory,81,8.5,26.0,0.0,False,3.7572,Monsoon (Jul–Sep)
2018-09-27,71.44,37.42,12.78,151.0,Moderate,77,5.5,27.0,0.0,False,4.2689,Monsoon (Jul–Sep)
2018-09-28,83.78,44.68,12.98,200.0,Moderate,74,5.0,27.7,0.6,False,4.4282,Monsoon (Jul–Sep)
2018-09-29,92.46,46.15,13.08,229.0,Poor,74,5.5,27.2,0.0,False,4.5268,Monsoon (Jul–Sep)
2018-09-30,69.49,34.52,12.38,176.0,Moderate,73,10.0,26.6,0.0,False,4.2412,Monsoon (Jul–Sep)
2018-10-01,65.78,40.86,12.7,148.0,Moderate,72,8.9,26.6,0.0,False,4.1863,Other months
2018-10-02,76.03,36.68,12.25,186.0,Moderate,68,6.9,27.5,0.0,False,4.3311,Other months
2018-10-03,63.37,42.57,13.36,160.0,Moderate,65,5.5,26.9,0.0,False,4.149,Other months
2018-10-04,97.4,48.01,14.42,206.0,Poor,71,5.0,26.4,1.0,False,4.5788,Other months
2018-10-05,121.12,53.69,17.27,268.0,Poor,72,5.2,26.4,0.0,False,4.7968,Other months
2018-10-06,78.87,44.71,13.42,237.0,Poor,64,8.3,25.8,0.0,False,4.3678,Other months
2018-10-07,81.14,44.81,14.33,189.0,Moderate,67,7.1,25.3,0.0,False,4.3962,Other months
2018-10-08,118.6,56.21,16.13,253.0,Poor,67,4.3,26.1,0.0,False,4.7758,Other months
2018-10-09,103.26,54.24,19.67,269.0,Poor,72,9.1,26.2,0.0,False,4.6373,Other months
2018-10-10,93.36,47.73,16.55,263.0,Poor,78,11.9,25.3,0.2,False,4.5365,Other months
2018-10-11,70.42,37.74,14.54,219.0,Poor,80,10.2,24.1,1.3,False,4.2545,Other months
2018-10-12,67.93,44.48,16.06,163.0,Moderate,71,6.5,23.7,0.0,False,4.2185,Other months
2018-10-13,132.93,49.89,17.91,264.0,Poor,66,7.9,23.2,0.0,False,4.8898,Other months
2018-10-14,91.88,47.34,16.07,237.0,Poor,61,9.9,23.2,0.0,False,4.5205,Other months
2018-10-15,115.96,55.44,17.96,253.0,Poor,58,6.7,24.4,0.0,False,4.7532,Other months
2018-10-16,139.18,64.18,19.19,309.0,Very Poor,68,7.3,24.8,0.0,False,4.9358,Other months
2018-10-17,137.29,52.81,17.13,332.0,Very Poor,68,7.1,25.0,0.0,False,4.9221,Other months
2018-10-18,143.2,57.64,18.46,330.0,Very Poor,71,9.3,24.8,0.4,False,4.9642,Other months
2018-10-19,137.73,54.31,18.35,300.0,Poor,60,6.4,25.3,0.0,False,4.9253,Other months
2018-10-20,168.87,54.04,19.82,344.0,Very Poor,56,7.0,24.4,0.0,False,5.1291,Other months
2018-10-21,141.15,55.77,20.59,325.0,Very Poor,54,8.8,23.4,0.0,False,4.9498,Other months
2018-10-22,121.65,55.49,17.74,296.0,Poor,49,9.6,22.5,0.0,False,4.8011,Other months
2018-10-23,119.4,63.32,19.49,274.0,Poor,48,7.7,23.0,0.0,False,4.7825,Other months
2018-10-24,174.04,77.72,20.95,354.0,Very Poor,57,6.0,23.4,0.0,False,5.1593,Other months
2018-10-25,168.82,72.23,22.51,356.0,Very Poor,59,6.7,23.2,0.0,False,5.1288,Other months
2018-10-26,203.12,74.04,20.76,394.0,Very Poor,63,7.3,22.7,0.0,False,5.3138,Other months
2018-10-27,206.05,77.3,19.9,396.0,Very Poor,61,7.3,23.3,0.0,False,5.3281,Other months
2018-10-28,205.0,57.66,15.62,403.0,Severe,63,8.2,23.0,0.0,False,5.323,Other months
2018-10-29,231.83,62.22,16.66,397.0,Very Poor,64,7.5,22.8,0.0,False,5.446,Other months
2018-10-30,263.39,70.46,17.62,456.0,Severe,63,4.5,23.7,0.0,False,5.5736,Other months
2018-10-31,225.17,68.02,18.11,422.0,Severe,63,4.8,23.8,0.0,False,5.4169,Other months
2018-11-01,236.67,71.63,20.12,433.0,Severe,65,4.8,23.2,0.0,False,5.4667,Winter (Nov–Jan)
2018-11-02,205.44,65.98,19.65,391.0,Very Poor,67,7.1,23.5,0.1,False,5.3252,Winter (Nov–Jan)
2018-11-03,159.56,47.39,17.1,353.0,Very Poor,64,15.5,23.5,0.0,False,5.0724,Winter (Nov–Jan)
2018-11-04,97.27,34.18,15.01,238.0,Poor,61,8.9,22.3,0.0,False,4.5775,Winter (Nov–Jan)
2018-11-05,361.98,48.25,14.63,424.0,Severe,62,9.4,20.2,0.0,False,5.8916,Winter (Nov–Jan)
2018-11-06,177.88,43.78,15.37,411.0,Severe,50,13.2,20.0,0.0,False,5.1811,Winter (Nov–Jan)
2018-11-07,175.43,45.14,19.39,317.0,Very Poor,40,9.1,19.1,0.0,False,5.1672,Winter (Nov–Jan)
2018-11-08,420.3,64.57,26.52,452.0,Severe,49,4.3,20.1,0.0,False,6.041,Winter (Nov–Jan)
2018-11-09,300.91,68.25,17.41,487.0,Severe,60,5.6,20.4,0.0,False,5.7068,Winter (Nov–Jan)
2018-11-10,288.86,79.5,18.01,430.0,Severe,63,4.7,20.8,0.0,False,5.6659,Winter (Nov–Jan)
2018-11-11,256.68,70.55,16.2,454.0,Severe,61,4.8,21.8,0.0,False,5.5478,Winter (Nov–Jan)
2018-11-12,271.7,71.88,17.4,437.0,Severe,68,6.0,21.5,0.0,False,5.6047,Winter (Nov–Jan)
2018-11-13,265.06,74.72,18.72,454.0,Severe,69,6.7,22.1,0.1,False,5.58,Winter (Nov–Jan)
2018-11-14,136.2,59.36,16.02,361.0,Very Poor,72,7.3,21.5,1.1,False,4.9141,Winter (Nov–Jan)
2018-11-15,98.53,47.83,15.03,251.0,Poor,72,9.4,20.7,0.6,False,4.5904,Winter (Nov–Jan)
2018-11-16,138.49,42.41,14.2,302.0,Very Poor,61,14.5,19.1,0.0,False,4.9308,Winter (Nov–Jan)
2018-11-17,135.21,51.93,14.37,292.0,Poor,64,10.4,18.5,0.0,False,4.9068,Winter (Nov–Jan)
2018-11-18,166.43,61.82,16.29,330.0,Very Poor,64,7.0,19.8,0.0,False,5.1146,Winter (Nov–Jan)
2018-11-19,179.79,56.73,16.32,340.0,Very Poor,63,10.6,20.8,0.0,False,5.1918,Winter (Nov–Jan)
2018-11-20,224.1,63.96,16.11,367.0,Very Poor,72,7.1,20.5,0.0,False,5.4121,Winter (Nov–Jan)
2018-11-21,209.96,63.79,14.22,396.0,Very Poor,62,10.0,19.7,0.0,False,5.3469,Winter (Nov–Jan)
2018-11-22,139.02,74.93,16.89,317.0,Very Poor,58,5.9,19.6,0.0,False,4.9346,Winter (Nov–Jan)
2018-11-23,187.85,61.06,16.39,356.0,Very Poor,57,12.9,19.3,0.0,False,5.2356,Winter (Nov–Jan)
2018-11-24,107.73,46.57,15.12,296.0,Poor,53,14.9,19.3,0.0,False,4.6796,Winter (Nov–Jan)
2018-11-25,133.62,58.16,16.56,266.0,Poor,60,8.1,17.8,0.0,False,4.895,Winter (Nov–Jan)
2018-11-26,200.69,68.3,20.11,349.0,Very Poor,66,8.6,18.5,0.0,False,5.3018,Winter (Nov–Jan)
2018-11-27,205.53,78.94,18.31,396.0,Very Poor,69,6.7,19.5,0.0,False,5.3256,Winter (Nov–Jan)
2018-11-28,193.1,69.6,15.96,363.0,Very Poor,72,5.1,19.6,0.0,False,5.2632,Winter (Nov–Jan)
2018-11-29,205.17,63.68,12.76,384.0,Very Poor,72,8.5,18.6,0.0,False,5.3238,Winter (Nov–Jan)
2018-11-30,190.36,56.74,13.69,365.0,Very Poor,69,9.6,18.3,0.0,False,5.2489,Winter (Nov–Jan)
2018-12-01,147.48,56.43,14.4,335.0,Very Poor,67,9.0,17.4,0.0,False,4.9937,Winter (Nov–Jan)
2018-12-02,164.63,67.18,16.62,329.0,Very Poor,58,5.3,17.8,0.0,False,5.1037,Winter (Nov–Jan)
2018-12-03,178.87,66.91,16.52,356.0,Very Poor,61,5.0,17.7,0.0,False,5.1867,Winter (Nov–Jan)
2018-12-04,211.57,74.17,16.28,394.0,Very Poor,66,6.0,17.3,0.0,False,5.3546,Winter (Nov–Jan)
2018-12-05,181.62,65.87,15.89,374.0,Very Poor,69,6.5,16.7,0.0,False,5.2019,Winter (Nov–Jan)
2018-12-06,218.06,71.73,16.49,385.0,Very Poor,67,5.7,17.0,0.0,False,5.3848,Winter (Nov–Jan)
2018-12-07,193.81,54.83,14.11,376.0,Very Poor,70,9.7,15.9,0.0,False,5.2669,Winter (Nov–Jan)
2018-12-08,202.83,59.06,15.47,366.0,Very Poor,70,7.3,15.4,0.0,False,5.3124,Winter (Nov–Jan)
2018-12-09,226.35,65.3,18.08,389.0,Very Poor,67,6.0,15.9,0.0,False,5.4221,Winter (Nov–Jan)
2018-12-10,264.63,66.58,16.74,431.0,Severe,72,8.0,15.5,0.1,False,5.5783,Winter (Nov–Jan)
2018-12-11,274.97,68.87,15.49,464.0,Severe,68,6.1,15.5,0.0,False,5.6167,Winter (Nov–Jan)
2018-12-12,209.63,55.1,14.64,443.0,Severe,76,8.7,14.6,0.8,False,5.3453,Winter (Nov–Jan)
2018-12-13,94.29,42.59,13.07,264.0,Poor,75,7.6,14.3,0.1,False,4.5464,Winter (Nov–Jan)
2018-12-14,113.42,45.22,12.5,248.0,Poor,70,8.6,14.0,0.0,False,4.7311,Winter (Nov–Jan)
2018-12-15,122.69,47.31,13.34,274.0,Poor,68,10.8,13.8,0.0,False,4.8097,Winter (Nov–Jan)
2018-12-16,150.28,50.86,15.76,295.0,Poor,67,8.7,13.4,0.0,False,5.0125,Winter (Nov–Jan)
2018-12-17,182.78,58.08,16.14,338.0,Very Poor,69,8.4,13.0,0.0,False,5.2083,Winter (Nov–Jan)
2018-12-18,204.08,61.34,17.76,370.0,Very Poor,66,10.3,12.9,0.0,False,5.3185,Winter (Nov–Jan)
2018-12-19,205.22,63.77,17.41,370.0,Very Poor,68,9.1,12.8,0.0,False,5.3241,Winter (Nov–Jan)
2018-12-20,258.1,68.97,17.68,423.0,Severe,68,7.3,12.4,0.0,False,5.5533,Winter (Nov–Jan)
2018-12-21,252.2,66.03,15.9,422.0,Severe,69,8.8,12.1,0.0,False,5.5302,Winter (Nov–Jan)
2018-12-22,326.79,78.71,18.47,468.0,Severe,70,6.5,11.9,0.0,False,5.7893,Winter (Nov–Jan)
2018-12-23,401.58,77.63,18.21,557.0,Severe,70,7.9,12.3,0.0,False,5.9954,Winter (Nov–Jan)
2018-12-24,378.68,75.26,17.86,577.0,Severe,66,7.3,13.2,0.0,False,5.9367,Winter (Nov–Jan)
2018-12-25,268.2,61.2,14.14,475.0,Severe,66,11.0,12.2,0.0,False,5.5917,Winter (Nov–Jan)
2018-12-26,241.0,65.2,15.37,405.0,Severe,63,8.0,11.9,0.0,False,5.4848,Winter (Nov–Jan)
2018-12-27,290.1,78.43,18.03,458.0,Severe,63,6.6,12.1,0.0,False,5.6702,Winter (Nov–Jan)
2018-12-28,249.23,60.59,14.8,413.0,Severe,67,12.6,11.5,0.0,False,5.5184,Winter (Nov–Jan)
2018-12-29,248.12,64.97,16.49,420.0,Severe,64,9.9,11.2,0.0,False,5.5139,Winter (Nov–Jan)
2018-12-30,336.42,76.89,19.91,484.0,Severe,61,4.8,13.2,0.0,False,5.8184,Winter (Nov–Jan)
2018-12-31,319.69,70.54,17.38,509.0,Severe,70,9.2,12.3,0.0,False,5.7674,Winter (Nov–Jan)
2019-01-01,287.34,69.46,17.77,475.0,Severe,71,7.1,12.7,0.0,False,5.6607,Winter (Nov–Jan)
2019-01-02,331.2,75.06,18.27,501.0,Severe,71,6.9,14.1,0.0,False,5.8027,Winter (Nov–Jan)
2019-01-03,355.4,66.2,15.12,537.0,Severe,70,9.9,13.4,0.0,False,5.8732,Winter (Nov–Jan)
2019-01-04,246.46,57.53,13.22,432.0,Severe,70,7.5,12.6,0.0,False,5.5072,Winter (Nov–Jan)
2019-01-05,262.53,60.35,15.59,440.0,Severe,69,11.9,13.4,0.0,False,5.5704,Winter (Nov–Jan)
2019-01-06,174.26,51.94,13.65,371.0,Very Poor,77,8.7,13.0,2.3,False,5.1605,Winter (Nov–Jan)
2019-01-07,181.74,52.45,15.49,331.0,Very Poor,77,8.3,12.4,0.0,False,5.2026,Winter (Nov–Jan)
2019-01-08,156.26,48.95,14.67,340.0,Very Poor,75,10.2,12.2,0.0,False,5.0515,Winter (Nov–Jan)
2019-01-09,143.66,49.49,15.09,321.0,Very Poor,69,12.8,12.6,0.0,False,4.9674,Winter (Nov–Jan)
2019-01-10,165.95,58.22,16.81,317.0,Very Poor,66,8.7,12.7,0.0,False,5.1117,Winter (Nov–Jan)
2019-01-11,278.95,76.71,20.03,401.0,Severe,68,6.9,12.9,0.0,False,5.631,Winter (Nov–Jan)
2019-01-12,311.03,85.14,17.81,482.0,Severe,67,5.9,13.9,0.0,False,5.7399,Winter (Nov–Jan)
2019-01-13,272.45,66.11,17.83,464.0,Severe,72,7.5,14.5,0.0,False,5.6075,Winter (Nov–Jan)
2019-01-14,94.44,42.16,15.05,320.0,Very Poor,58,15.0,12.5,0.0,False,4.548,Winter (Nov–Jan)
2019-01-15,134.57,52.45,17.09,248.0,Poor,56,13.2,11.5,0.0,False,4.9021,Winter (Nov–Jan)
2019-01-16,271.96,83.75,20.35,383.0,Very Poor,67,6.6,11.7,0.0,False,5.6057,Winter (Nov–Jan)
2019-01-17,358.91,84.74,19.63,515.0,Severe,71,7.5,12.7,0.0,False,5.8831,Winter (Nov–Jan)
2019-01-18,237.22,68.58,14.7,437.0,Severe,72,8.7,12.0,0.0,False,5.469,Winter (Nov–Jan)
2019-01-19,262.68,77.9,18.07,411.0,Severe,67,7.1,14.4,0.0,False,5.5709,Winter (Nov–Jan)
2019-01-20,314.59,106.04,20.98,480.0,Severe,67,5.0,17.8,0.0,False,5.7513,Winter (Nov–Jan)
2019-01-21,175.49,63.04,16.82,413.0,Severe,80,14.8,16.2,6.5,False,5.1676,Winter (Nov–Jan)
2019-01-22,53.25,38.56,11.87,174.0,Moderate,86,14.2,14.8,16.9,False,3.975,Winter (Nov–Jan)
2019-01-23,135.68,48.14,14.17,186.0,Moderate,84,6.4,13.2,0.1,False,4.9103,Winter (Nov–Jan)
2019-01-24,130.59,44.11,15.29,328.0,Very Poor,81,8.1,13.7,0.3,False,4.8721,Winter (Nov–Jan)
2019-01-25,81.2,40.03,14.62,188.0,Moderate,79,8.3,12.1,0.1,False,4.3969,Winter (Nov–Jan)
2019-01-26,101.61,38.43,14.48,231.0,Poor,66,10.3,11.3,0.0,False,4.6211,Winter (Nov–Jan)
2019-01-27,136.47,45.27,15.89,275.0,Poor,66,11.7,10.1,0.0,False,4.9161,Winter (Nov–Jan)
2019-01-28,126.48,49.13,15.76,301.0,Very Poor,61,12.8,10.6,0.0,False,4.8401,Winter (Nov–Jan)
2019-01-29,142.0,51.47,18.56,297.0,Poor,60,12.5,11.1,0.0,False,4.9558,Winter (Nov–Jan)
2019-01-30,206.14,63.7,24.75,342.0,Very Poor,68,9.4,11.5,0.0,False,5.3286,Winter (Nov–Jan)
2019-01-31,204.25,65.7,20.48,397.0,Very Poor,69,11.4,13.0,0.6,False,5.3193,Winter (Nov–Jan)
2019-02-01,178.68,50.75,17.83,329.0,Very Poor,74,9.2,14.2,0.2,False,5.1856,Other months
2019-02-02,177.32,35.89,11.55,338.0,Very Poor,80,10.2,12.9,0.0,False,5.178,Other months
2019-02-03,131.1,34.53,11.7,323.0,Very Poor,81,8.7,12.6,0.0,False,4.876,Other months
2019-02-04,144.62,52.85,14.06,301.0,Very Poor,73,6.6,14.2,0.0,False,4.9741,Other months
2019-02-05,256.33,75.89,22.38,398.0,Very Poor,75,7.0,15.9,0.0,False,5.5465,Other months
2019-02-06,177.25,50.55,15.59,380.0,Very Poor,84,12.2,17.1,9.1,False,5.1776,Other months
2019-02-07,65.65,30.8,11.12,233.0,Poor,89,20.9,15.7,12.7,False,4.1843,Other months
2019-02-08,72.29,39.24,12.66,136.0,Moderate,71,9.1,12.7,0.0,False,4.2807,Other months
2019-02-09,82.5,38.31,13.25,169.0,Moderate,68,13.0,12.5,0.0,False,4.4128,Other months
2019-02-10,143.31,49.26,16.41,277.0,Poor,72,7.4,12.4,0.5,False,4.965,Other months
2019-02-11,173.61,58.56,17.52,332.0,Very Poor,73,6.5,13.2,0.0,False,5.1568,Other months
2019-02-12,208.64,66.37,19.93,357.0,Very Poor,75,5.2,15.2,0.0,False,5.3406,Other months
2019-02-13,198.26,70.04,18.61,372.0,Very Poor,73,7.0,16.5,0.4,False,5.2896,Other months
2019-02-14,153.73,53.15,14.53,350.0,Very Poor,83,14.8,16.3,4.0,False,5.0352,Other months
2019-02-15,123.46,44.28,15.38,275.0,Poor,85,6.9,15.9,4.5,False,4.8159,Other months
2019-02-16,112.34,33.33,12.92,288.0,Poor,85,8.2,14.4,0.1,False,4.7215,Other months
2019-02-17,99.27,42.59,15.14,247.0,Poor,79,11.7,14.6,0.0,False,4.5978,Other months
2019-02-18,109.11,56.12,16.78,278.0,Poor,71,11.2,16.3,0.1,False,4.6924,Other months
2019-02-19,126.12,55.44,15.93,232.0,Poor,77,6.3,16.9,0.0,False,4.8372,Other months
2019-02-20,102.3,51.88,17.16,305.0,Very Poor,82,12.5,17.0,2.6,False,4.6279,Other months
2019-02-21,73.33,47.15,20.1,158.0,Moderate,75,11.2,19.3,0.0,False,4.295,Other months
2019-02-22,73.9,33.95,13.94,191.0,Moderate,72,15.2,17.9,0.4,False,4.3027,Other months
2019-02-23,56.51,36.12,15.66,116.0,Moderate,64,14.6,15.1,0.0,False,4.0344,Other months
2019-02-24,89.34,46.26,18.99,169.0,Moderate,66,9.1,15.4,0.2,False,4.4924,Other months
2019-02-25,92.36,53.86,18.07,221.0,Poor,65,7.6,15.5,0.0,False,4.5257,Other months
2019-02-26,59.97,50.31,16.88,144.0,Moderate,67,11.7,15.6,2.8,False,4.0938,Other months
2019-02-27,47.18,35.07,12.52,112.0,Moderate,79,7.5,13.5,11.2,False,3.854,Other months
2019-02-28,96.38,45.02,16.98,198.0,Moderate,70,9.4,13.1,0.0,False,4.5683,Other months
2019-03-01,93.83,48.87,15.81,222.0,Poor,66,9.5,13.9,0.0,False,4.5415,Other months
2019-03-02,109.6,62.05,17.96,227.0,Poor,73,6.0,15.0,6.8,False,4.6968,Other months
2019-03-03,62.92,40.61,13.48,172.0,Moderate,80,8.8,15.9,4.1,False,4.1419,Other months
2019-03-04,105.93,40.1,14.75,217.0,Poor,80,7.9,16.9,0.2,False,4.6628,Other months
2019-03-05,68.86,40.05,14.26,173.0,Moderate,71,10.5,16.1,0.0,False,4.2321,Other months
2019-03-06,83.45,45.3,15.16,189.0,Moderate,63,10.7,16.7,0.0,False,4.4242,Other months
2019-03-07,104.61,51.9,16.39,228.0,Poor,62,8.2,17.1,0.0,False,4.6502,Other months
2019-03-08,92.07,51.75,17.44,220.0,Poor,58,7.9,18.6,0.0,False,4.5225,Other months
2019-03-09,73.31,40.84,17.3,194.0,Moderate,65,11.6,18.2,0.0,False,4.2947,Other months
2019-03-10,73.98,44.17,16.36,157.0,Moderate,54,9.3,17.7,0.0,False,4.3038,Other months
2019-03-11,82.17,52.91,18.44,190.0,Moderate,55,14.6,20.0,1.7,False,4.4088,Other months
2019-03-12,57.28,37.45,13.82,149.0,Moderate,57,10.9,19.6,0.0,False,4.048,Other months
2019-03-13,89.17,57.03,22.48,168.0,Moderate,63,6.9,18.3,0.0,False,4.4905,Other months
2019-03-14,111.2,48.81,17.54,281.0,Poor,72,11.1,17.2,0.3,False,4.7113,Other months
2019-03-15,74.88,41.27,16.21,183.0,Moderate,65,11.0,17.9,0.0,False,4.3159,Other months
2019-03-16,68.64,40.6,15.72,143.0,Moderate,57,10.5,18.1,0.0,False,4.2289,Other months
2019-03-17,93.61,46.88,19.96,198.0,Moderate,49,9.1,20.1,0.0,False,4.5391,Other months
2019-03-18,100.32,50.33,20.36,221.0,Poor,49,7.0,20.7,0.0,False,4.6084,Other months
2019-03-19,103.77,55.47,20.72,239.0,Poor,50,8.7,21.7,0.0,False,4.6422,Other months
2019-03-20,89.82,54.67,21.42,234.0,Poor,47,14.4,23.3,0.0,False,4.4978,Other months
2019-03-21,112.29,34.63,19.99,272.0,Poor,49,10.5,22.8,0.0,False,4.7211,Other months
2019-03-22,38.43,32.19,16.06,141.0,Moderate,40,13.2,22.0,0.0,False,3.6488,Other months
2019-03-23,55.62,34.57,17.52,131.0,Moderate,38,15.7,22.4,0.0,False,4.0185,Other months
2019-03-24,53.28,34.25,19.06,126.0,Moderate,45,12.9,24.1,0.0,False,3.9756,Other months
2019-03-25,65.0,34.84,20.19,136.0,Moderate,62,11.5,21.7,0.5,False,4.1744,Other months
2019-03-26,75.82,40.8,19.26,162.0,Moderate,57,11.2,22.3,0.0,False,4.3284,Other months
2019-03-27,78.37,49.68,20.35,177.0,Moderate,52,9.5,23.6,0.0,False,4.3614,Other months
2019-03-28,116.55,60.18,24.86,245.0,Poor,52,8.2,26.0,0.0,False,4.7583,Other months
2019-03-29,112.67,60.4,19.52,273.0,Poor,50,7.0,27.9,0.0,False,4.7245,Other months
2019-03-30,102.27,53.75,22.39,252.0,Poor,54,7.4,27.0,0.0,False,4.6276,Other months
2019-03-31,58.96,38.42,18.9,198.0,Moderate,41,14.1,26.5,0.0,False,4.0769,Other months
2019-04-01,59.08,38.55,20.09,153.0,Moderate,33,13.7,25.5,0.0,False,4.0789,Other months
2019-04-02,90.1,55.76,24.4,194.0,Moderate,39,8.6,25.5,0.0,False,4.5009,Other months
2019-04-03,85.02,54.91,21.6,208.0,Poor,39,9.4,26.3,0.0,False,4.4429,Other months
2019-04-04,119.71,63.62,29.11,260.0,Poor,40,8.2,28.0,0.0,False,4.7851,Other months
2019-04-05,125.44,64.7,28.67,284.0,Poor,41,7.1,29.4,0.0,False,4.8318,Other months
2019-04-06,96.6,48.72,23.23,269.0,Poor,47,9.3,28.8,0.0,False,4.5706,Other months
2019-04-07,152.91,44.64,21.35,315.0,Very Poor,54,10.1,28.2,0.0,False,5.0298,Other months
2019-04-08,81.3,45.87,15.1,284.0,Poor,54,11.2,26.9,0.2,False,4.3981,Other months
2019-04-09,87.74,53.88,22.03,240.0,Poor,47,8.1,28.4,0.0,False,4.4744,Other months
2019-04-10,101.94,56.82,20.84,263.0,Poor,43,7.9,29.2,0.0,False,4.6244,Other months
2019-04-11,70.25,47.54,21.51,196.0,Moderate,36,8.3,30.4,0.0,False,4.2521,Other months
2019-04-12,61.34,40.09,19.48,202.0,Poor,36,10.0,29.6,0.0,False,4.1164,Other months
2019-04-13,55.93,37.89,20.82,175.0,Moderate,38,12.0,29.9,0.0,False,4.0241,Other months
2019-04-14,51.51,36.61,20.65,150.0,Moderate,34,14.0,30.6,0.0,False,3.9418,Other months
2019-04-15,54.84,41.92,22.2,163.0,Moderate,31,11.5,31.1,0.0,False,4.0044,Other months
2019-04-16,59.08,35.01,12.59,206.0,Poor,49,12.6,26.2,0.5,False,4.0789,Other months
2019-04-17,22.14,26.84,11.1,102.0,Moderate,73,11.6,21.8,4.6,False,3.0974,Other months
2019-04-18,38.92,39.07,15.05,104.0,Moderate,67,5.6,22.5,0.1,False,3.6615,Other months
2019-04-19,71.62,47.56,21.22,151.0,Moderate,53,9.0,24.5,0.1,False,4.2714,Other months
2019-04-20,90.55,55.28,26.03,199.0,Moderate,47,7.3,26.4,0.0,False,4.5059,Other months
2019-04-21,95.24,58.95,22.16,225.0,Poor,39,9.3,28.7,0.0,False,4.5564,Other months
2019-04-22,110.16,61.72,29.31,246.0,Poor,40,9.4,30.1,0.0,False,4.7019,Other months
2019-04-23,104.17,63.45,25.76,257.0,Poor,34,8.5,32.1,0.0,False,4.646,Other months
2019-04-24,85.7,51.58,19.17,232.0,Poor,35,10.9,32.7,0.0,False,4.4509,Other months
2019-04-25,86.41,39.89,17.67,251.0,Poor,36,11.1,33.0,0.0,False,4.4591,Other months
2019-04-26,82.37,50.69,26.12,223.0,Poor,33,12.6,33.0,0.0,False,4.4112,Other months
2019-04-27,73.06,39.8,21.85,248.0,Poor,22,18.9,33.5,0.0,False,4.2913,Other months
2019-04-28,76.44,40.9,20.02,269.0,Poor,20,15.8,33.3,0.0,False,4.3365,Other months
2019-04-29,84.04,52.04,23.71,256.0,Poor,19,10.5,33.6,0.0,False,4.4313,Other months
2019-04-30,95.72,59.32,26.58,257.0,Poor,20,12.0,34.2,0.0,False,4.5614,Other months
2019-05-01,111.57,63.15,27.67,285.0,Poor,25,8.9,33.0,0.0,False,4.7147,Other months
2019-05-02,77.72,43.19,18.26,275.0,Poor,33,13.4,31.5,0.5,False,4.3531,Other months
2019-05-03,52.16,49.82,17.91,202.0,Poor,33,9.7,31.0,0.0,False,3.9543,Other months
2019-05-04,77.96,59.78,18.19,182.0,Moderate,22,13.8,31.1,0.0,False,4.3562,Other months
2019-05-05,101.25,55.16,21.93,231.0,Poor,19,14.1,31.1,0.0,False,4.6176,Other months
2019-05-06,118.9,70.81,23.72,267.0,Poor,21,10.8,32.2,0.0,False,4.7783,Other months
2019-05-07,128.78,69.77,22.77,310.0,Very Poor,20,13.3,32.3,0.0,False,4.8581,Other months
2019-05-08,143.34,60.85,25.84,389.0,Very Poor,18,13.5,34.0,0.0,False,4.9652,Other months
2019-05-09,137.2,51.13,23.46,390.0,Very Poor,19,17.1,34.2,0.0,False,4.9214,Other months
2019-05-10,95.07,38.05,17.6,333.0,Very Poor,20,16.8,34.6,0.0,False,4.5546,Other months
2019-05-11,101.83,42.02,21.6,266.0,Poor,29,13.1,32.3,0.0,False,4.6233,Other months
2019-05-12,178.22,40.68,19.36,352.0,Very Poor,30,10.8,31.9,0.0,False,5.183,Other months
2019-05-13,170.81,50.88,33.5,376.0,Very Poor,30,8.3,32.4,0.0,False,5.1406,Other months
2019-05-14,58.22,37.53,13.4,217.0,Poor,42,8.0,30.1,0.0,False,4.0642,Other months
2019-05-15,84.81,57.75,20.93,194.0,Moderate,45,7.3,30.3,0.1,False,4.4404,Other months
2019-05-16,75.45,50.99,15.36,192.0,Moderate,46,8.9,30.2,0.0,False,4.3235,Other months
2019-05-17,92.53,45.67,13.26,257.0,Poor,57,7.2,28.3,2.7,False,4.5275,Other months
2019-05-18,44.28,33.79,10.93,176.0,Moderate,60,11.9,27.4,0.2,False,3.7905,Other months
2019-05-19,81.99,45.8,17.36,168.0,Moderate,43,10.8,30.1,0.0,False,4.4066,Other months
2019-05-20,93.97,56.55,19.81,216.0,Poor,34,11.1,31.9,0.0,False,4.543,Other months
2019-05-21,77.78,47.58,20.15,206.0,Poor,31,10.6,32.6,0.0,False,4.3539,Other months
2019-05-22,64.24,51.8,16.92,167.0,Moderate,35,9.9,32.8,0.0,False,4.1626,Other months
2019-05-23,92.4,52.71,21.68,228.0,Poor,37,8.3,33.1,0.0,False,4.5261,Other months
2019-05-24,43.86,40.33,11.99,151.0,Moderate,45,12.4,30.8,0.0,False,3.781,Other months
2019-05-25,43.66,34.52,13.09,125.0,Moderate,39,15.3,31.1,0.0,False,3.7764,Other months
2019-05-26,55.13,41.51,17.94,135.0,Moderate,34,11.5,31.6,0.0,False,4.0097,Other months
2019-05-27,64.66,53.92,18.9,163.0,Moderate,27,12.0,33.7,0.0,False,4.1691,Other months
2019-05-28,65.82,61.45,20.59,175.0,Moderate,20,12.4,33.5,0.0,False,4.1869,Other months
2019-05-29,74.8,65.84,23.61,191.0,Moderate,20,10.5,34.7,0.0,False,4.3148,Other months
2019-05-30,85.21,71.8,21.99,226.0,Poor,21,9.0,35.6,0.0,False,4.4451,Other months
2019-05-31,88.57,56.83,19.82,266.0,Poor,20,10.8,36.8,0.0,False,4.4838,Other months
2019-06-01,95.4,57.24,21.54,300.0,Poor,29,10.3,35.6,0.0,False,4.5581,Other months
2019-06-02,73.36,32.22,14.15,222.0,Poor,40,13.8,35.5,0.0,False,4.2954,Other months
2019-06-03,66.94,30.33,12.64,232.0,Poor,46,15.5,34.6,0.0,False,4.2038,Other months
2019-06-04,54.95,36.0,13.67,212.0,Poor,42,14.4,34.8,0.0,False,4.0064,Other months
2019-06-05,73.35,42.68,15.82,190.0,Moderate,39,9.4,35.5,0.3,False,4.2952,Other months
2019-06-06,70.61,44.85,16.15,209.0,Poor,37,11.2,35.6,0.5,False,4.2572,Other months
2019-06-07,54.81,35.32,14.44,192.0,Moderate,42,8.6,34.1,0.0,False,4.0039,Other months
2019-06-08,69.75,51.0,13.47,184.0,Moderate,33,8.1,35.5,0.0,False,4.2449,Other months
2019-06-09,101.05,62.84,21.74,237.0,Poor,24,8.1,36.9,0.0,False,4.6156,Other months
2019-06-10,74.48,61.53,15.19,230.0,Poor,23,7.9,37.2,0.0,False,4.3105,Other months
2019-06-11,118.38,49.86,13.52,315.0,Very Poor,23,10.4,37.4,0.0,False,4.7739,Other months
2019-06-12,59.86,30.46,11.57,280.0,Poor,44,11.6,34.6,2.2,False,4.092,Other months
2019-06-13,52.66,34.53,11.79,189.0,Moderate,38,12.2,35.4,0.0,False,3.9639,Other months
2019-06-14,53.79,37.07,12.89,167.0,Moderate,29,15.2,36.0,0.0,False,3.9851,Other months
2019-06-15,81.86,47.15,17.56,217.0,Poor,22,14.5,36.5,0.0,False,4.405,Other months
2019-06-16,42.06,20.56,9.54,205.0,Poor,43,20.4,33.8,0.0,False,3.7391,Other months
2019-06-17,40.18,27.51,11.07,126.0,Moderate,47,19.0,33.5,0.0,False,3.6934,Other months
2019-06-18,30.39,32.32,8.0,119.0,Moderate,55,8.7,30.5,0.5,False,3.4141,Other months
2019-06-19,79.96,37.14,12.69,173.0,Moderate,53,7.5,31.0,0.0,False,4.3815,Other months
2019-06-20,42.76,31.19,9.7,175.0,Moderate,48,7.1,31.8,0.0,False,3.7556,Other months
2019-06-21,71.15,44.78,12.23,178.0,Moderate,47,6.3,33.3,1.2,False,4.2648,Other months
2019-06-22,68.27,44.12,14.97,185.0,Moderate,38,8.9,34.7,0.0,False,4.2235,Other months
2019-06-23,42.06,23.02,10.11,153.0,Moderate,49,14.3,34.0,0.0,False,3.7391,Other months
2019-06-24,26.29,25.93,10.74,118.0,Moderate,60,10.5,31.5,0.6,False,3.2692,Other months
2019-06-25,53.65,32.24,11.91,131.0,Moderate,62,5.4,32.1,4.8,False,3.9825,Other months
2019-06-26,67.36,37.39,12.87,161.0,Moderate,48,8.6,34.8,0.6,False,4.2101,Other months
2019-06-27,65.3,39.94,13.46,169.0,Moderate,40,11.8,34.6,0.0,False,4.179,Other months
2019-06-28,61.21,38.37,14.43,207.0,Poor,38,13.3,35.5,0.0,False,4.1143,Other months
2019-06-29,58.08,34.56,11.99,223.0,Poor,36,12.9,36.3,0.0,False,4.0618,Other months
2019-06-30,65.24,33.03,12.82,234.0,Poor,35,11.7,36.8,0.0,False,4.1781,Other months
2019-07-01,57.27,31.09,12.22,195.0,Moderate,42,6.8,36.0,0.0,False,4.0478,Monsoon (Jul–Sep)
2019-07-02,71.68,28.13,12.02,202.0,Poor,46,9.1,35.7,0.0,False,4.2722,Monsoon (Jul–Sep)
2019-07-03,39.99,26.57,9.75,162.0,Moderate,56,11.5,33.7,1.6,False,3.6886,Monsoon (Jul–Sep)
2019-07-04,36.82,29.23,9.75,111.0,Moderate,60,10.4,33.0,6.6,False,3.606,Monsoon (Jul–Sep)
2019-07-05,48.6,34.77,11.05,113.0,Moderate,72,5.9,31.0,3.7,False,3.8836,Monsoon (Jul–Sep)
2019-07-06,34.25,29.91,10.18,99.0,Satisfactory,69,7.9,31.0,0.3,False,3.5337,Monsoon (Jul–Sep)
2019-07-07,38.81,28.87,10.67,101.0,Moderate,69,4.6,31.1,2.1,False,3.6587,Monsoon (Jul–Sep)
2019-07-08,49.12,32.85,10.64,129.0,Moderate,68,5.3,31.9,4.0,False,3.8943,Monsoon (Jul–Sep)
2019-07-09,42.56,30.38,9.52,131.0,Moderate,72,8.7,30.7,4.9,False,3.7509,Monsoon (Jul–Sep)
2019-07-10,69.21,31.36,10.41,150.0,Moderate,74,9.1,31.0,7.1,False,4.2371,Monsoon (Jul–Sep)
2019-07-11,76.99,29.87,9.64,300.0,Poor,57,15.2,33.4,0.0,False,4.3437,Monsoon (Jul–Sep)
2019-07-12,76.35,26.97,8.96,294.0,Poor,51,13.6,33.4,0.5,False,4.3353,Monsoon (Jul–Sep)
2019-07-13,63.18,23.13,9.11,312.0,Very Poor,47,19.6,34.1,0.0,False,4.146,Monsoon (Jul–Sep)
2019-07-14,63.16,25.1,9.85,243.0,Poor,52,15.9,32.9,0.0,False,4.1457,Monsoon (Jul–Sep)
2019-07-15,42.04,27.17,10.39,180.0,Moderate,72,10.0,29.7,4.4,False,3.7386,Monsoon (Jul–Sep)
2019-07-16,31.51,27.54,9.64,117.0,Moderate,89,9.2,26.6,20.6,False,3.4503,Monsoon (Jul–Sep)
2019-07-17,32.06,28.44,8.91,92.0,Satisfactory,85,6.8,27.2,14.8,False,3.4676,Monsoon (Jul–Sep)
2019-07-18,32.92,37.14,8.86,98.0,Satisfactory,82,5.0,27.5,12.8,False,3.4941,Monsoon (Jul–Sep)
2019-07-19,63.02,40.79,9.95,142.0,Moderate,79,4.6,29.4,6.7,False,4.1435,Monsoon (Jul–Sep)
2019-07-20,46.43,37.1,8.6,137.0,Moderate,80,6.7,30.0,12.5,False,3.8379,Monsoon (Jul–Sep)
2019-07-21,50.57,33.89,8.83,123.0,Moderate,81,7.8,29.7,11.1,False,3.9234,Monsoon (Jul–Sep)
2019-07-22,60.38,33.03,8.95,124.0,Moderate,80,6.3,30.4,6.1,False,4.1007,Monsoon (Jul–Sep)
2019-07-23,73.08,39.89,9.05,156.0,Moderate,77,6.2,31.6,4.6,False,4.2916,Monsoon (Jul–Sep)
2019-07-24,63.26,40.29,8.83,165.0,Moderate,74,9.2,31.5,6.8,False,4.1473,Monsoon (Jul–Sep)
2019-07-25,22.79,33.52,8.76,98.0,Satisfactory,86,6.6,27.6,10.9,False,3.1263,Monsoon (Jul–Sep)
2019-07-26,30.63,31.61,8.92,94.0,Satisfactory,87,10.4,27.2,26.9,False,3.422,Monsoon (Jul–Sep)
2019-07-27,26.16,25.34,8.67,85.0,Satisfactory,90,13.5,26.6,6.0,False,3.2642,Monsoon (Jul–Sep)
2019-07-28,21.13,21.89,8.43,83.0,Satisfactory,86,14.2,28.1,7.3,False,3.0507,Monsoon (Jul–Sep)
2019-07-29,24.45,25.11,8.97,82.0,Satisfactory,79,14.4,29.2,1.3,False,3.1966,Monsoon (Jul–Sep)
2019-07-30,30.1,26.92,9.36,90.0,Satisfactory,78,12.4,28.9,0.8,False,3.4045,Monsoon (Jul–Sep)
2019-07-31,30.22,26.45,8.78,90.0,Satisfactory,78,9.7,29.0,0.5,False,3.4085,Monsoon (Jul–Sep)
2019-08-01,34.26,28.4,8.79,98.0,Satisfactory,82,9.2,29.3,2.1,False,3.534,Monsoon (Jul–Sep)
2019-08-02,35.06,30.96,8.45,95.0,Satisfactory,85,7.1,28.7,12.9,False,3.5571,Monsoon (Jul–Sep)
2019-08-03,38.54,31.0,9.43,104.0,Moderate,88,8.2,28.3,6.8,False,3.6517,Monsoon (Jul–Sep)
2019-08-04,46.69,30.9,9.96,101.0,Moderate,87,4.3,28.9,4.2,False,3.8435,Monsoon (Jul–Sep)
2019-08-05,52.2,34.64,9.37,108.0,Moderate,86,5.7,29.2,18.5,False,3.9551,Monsoon (Jul–Sep)
2019-08-06,30.04,34.68,8.26,99.0,Satisfactory,89,8.6,27.9,20.7,False,3.4025,Monsoon (Jul–Sep)
2019-08-07,32.63,31.82,9.81,104.0,Moderate,88,5.6,28.2,7.0,False,3.4852,Monsoon (Jul–Sep)
2019-08-08,27.69,28.9,10.61,99.0,Satisfactory,78,9.2,30.1,0.5,False,3.3211,Monsoon (Jul–Sep)
2019-08-09,14.59,22.08,9.3,89.0,Satisfactory,75,21.4,29.3,0.8,False,2.6803,Monsoon (Jul–Sep)
2019-08-10,16.73,22.06,8.47,75.0,Satisfactory,80,18.8,28.8,1.7,False,2.8172,Monsoon (Jul–Sep)
2019-08-11,25.53,25.93,8.65,83.0,Satisfactory,79,7.9,29.5,0.3,False,3.2399,Monsoon (Jul–Sep)
2019-08-12,20.53,26.18,8.14,80.0,Satisfactory,80,9.3,29.3,7.6,False,3.0219,Monsoon (Jul–Sep)
2019-08-13,21.68,27.12,8.37,85.0,Satisfactory,84,9.0,29.1,20.1,False,3.0764,Monsoon (Jul–Sep)
2019-08-14,33.21,31.9,8.5,93.0,Satisfactory,88,4.0,28.3,2.8,False,3.5029,Monsoon (Jul–Sep)
2019-08-15,28.78,25.03,8.51,93.0,Satisfactory,82,14.0,29.0,11.2,False,3.3597,Monsoon (Jul–Sep)
2019-08-16,15.52,21.51,8.61,73.0,Satisfactory,84,17.3,27.9,9.4,False,2.7421,Monsoon (Jul–Sep)
2019-08-17,10.24,19.1,7.67,67.0,Satisfactory,90,20.7,26.1,8.4,False,2.3263,Monsoon (Jul–Sep)
2019-08-18,15.51,20.93,8.57,66.0,Satisfactory,87,10.1,26.8,31.0,False,2.7415,Monsoon (Jul–Sep)
2019-08-19,38.55,28.59,8.6,99.0,Satisfactory,84,5.0,28.0,1.3,False,3.652,Monsoon (Jul–Sep)
2019-08-20,41.74,26.86,8.12,103.0,Moderate,82,9.6,28.5,0.8,False,3.7315,Monsoon (Jul–Sep)
2019-08-21,46.69,32.68,7.81,107.0,Moderate,78,9.9,29.3,0.0,False,3.8435,Monsoon (Jul–Sep)
2019-08-22,44.16,42.21,8.41,125.0,Moderate,84,6.3,28.6,0.8,False,3.7878,Monsoon (Jul–Sep)
2019-08-23,50.49,40.32,8.36,130.0,Moderate,82,3.5,29.2,4.0,False,3.9218,Monsoon (Jul–Sep)
2019-08-24,60.71,41.76,8.78,149.0,Moderate,83,5.8,29.1,3.9,False,4.1061,Monsoon (Jul–Sep)
2019-08-25,33.49,31.71,8.23,107.0,Moderate,88,8.2,27.5,12.9,False,3.5112,Monsoon (Jul–Sep)
2019-08-26,25.06,31.6,8.55,77.0,Satisfactory,83,8.6,28.8,0.6,False,3.2213,Monsoon (Jul–Sep)
2019-08-27,40.68,34.48,10.01,114.0,Moderate,80,6.3,29.8,0.1,False,3.7057,Monsoon (Jul–Sep)
2019-08-28,42.04,34.62,9.64,119.0,Moderate,78,8.4,30.4,0.4,False,3.7386,Monsoon (Jul–Sep)
2019-08-29,33.92,30.6,8.24,103.0,Moderate,80,9.1,30.1,1.0,False,3.524,Monsoon (Jul–Sep)
2019-08-30,43.5,32.44,9.33,110.0,Moderate,81,5.1,30.1,0.9,False,3.7728,Monsoon (Jul–Sep)
2019-08-31,57.16,40.79,9.14,123.0,Moderate,78,5.4,30.5,6.4,False,4.0459,Monsoon (Jul–Sep)
2019-09-01,35.13,32.08,8.41,123.0,Moderate,86,10.0,28.6,4.7,False,3.5591,Monsoon (Jul–Sep)
2019-09-02,46.15,31.91,8.81,105.0,Moderate,83,4.2,29.5,1.3,False,3.8319,Monsoon (Jul–Sep)
2019-09-03,70.64,36.51,8.95,131.0,Moderate,80,5.1,30.2,5.5,False,4.2576,Monsoon (Jul–Sep)
2019-09-04,73.33,36.99,9.03,165.0,Moderate,85,8.9,29.0,7.8,False,4.295,Monsoon (Jul–Sep)
2019-09-05,33.9,29.09,9.25,118.0,Moderate,82,7.8,29.4,0.6,False,3.5234,Monsoon (Jul–Sep)
2019-09-06,35.81,30.05,10.9,96.0,Satisfactory,81,7.8,29.7,0.4,False,3.5782,Monsoon (Jul–Sep)
2019-09-07,34.98,30.9,8.17,95.0,Satisfactory,85,9.1,28.8,2.1,False,3.5548,Monsoon (Jul–Sep)
2019-09-08,32.83,26.84,8.72,99.0,Satisfactory,83,6.3,29.1,0.2,False,3.4913,Monsoon (Jul–Sep)
2019-09-09,56.31,30.47,8.45,107.0,Moderate,78,4.9,30.1,0.1,False,4.0309,Monsoon (Jul–Sep)
2019-09-10,64.48,34.12,9.49,139.0,Moderate,74,5.5,30.6,0.0,False,4.1664,Monsoon (Jul–Sep)
2019-09-11,79.6,39.69,9.54,166.0,Moderate,73,5.8,31.2,0.4,False,4.377,Monsoon (Jul–Sep)
2019-09-12,57.83,34.01,8.91,158.0,Moderate,79,13.4,30.2,0.6,False,4.0575,Monsoon (Jul–Sep)
2019-09-13,33.59,29.75,8.16,103.0,Moderate,77,10.8,29.8,0.6,False,3.5142,Monsoon (Jul–Sep)
2019-09-14,26.65,26.05,8.48,85.0,Satisfactory,79,12.1,28.7,0.7,False,3.2828,Monsoon (Jul–Sep)
2019-09-15,35.52,27.77,8.55,83.0,Satisfactory,83,8.3,28.1,5.2,False,3.5701,Monsoon (Jul–Sep)
2019-09-16,56.6,36.18,8.35,111.0,Moderate,81,5.4,29.3,0.4,False,4.036,Monsoon (Jul–Sep)
2019-09-17,59.14,38.18,8.64,143.0,Moderate,80,7.8,29.2,2.0,False,4.0799,Monsoon (Jul–Sep)
2019-09-18,35.41,31.3,9.46,117.0,Moderate,80,11.2,28.5,3.0,False,3.567,Monsoon (Jul–Sep)
2019-09-19,21.74,24.15,9.29,80.0,Satisfactory,80,12.7,26.9,1.0,False,3.0792,Monsoon (Jul–Sep)
2019-09-20,40.33,31.73,10.81,96.0,Satisfactory,83,7.0,27.0,7.7,False,3.6971,Monsoon (Jul–Sep)
2019-09-21,39.23,31.43,9.63,112.0,Moderate,80,6.1,27.8,0.7,False,3.6694,Monsoon (Jul–Sep)
2019-09-22,26.51,30.66,9.32,86.0,Satisfactory,83,8.7,27.1,13.9,False,3.2775,Monsoon (Jul–Sep)
2019-09-23,34.46,30.02,9.9,89.0,Satisfactory,81,8.0,26.7,2.0,False,3.5398,Monsoon (Jul–Sep)
2019-09-24,35.88,34.98,9.19,103.0,Moderate,80,8.6,27.0,2.9,False,3.5802,Monsoon (Jul–Sep)
2019-09-25,30.52,29.99,8.94,100.0,Satisfactory,81,11.3,27.2,3.6,False,3.4184,Monsoon (Jul–Sep)
2019-09-26,22.9,27.25,10.43,87.0,Satisfactory,76,15.9,27.6,1.9,False,3.1311,Monsoon (Jul–Sep)
2019-09-27,15.66,24.52,10.3,78.0,Satisfactory,78,13.0,26.6,0.5,False,2.7511,Monsoon (Jul–Sep)
2019-09-28,22.52,26.18,10.01,78.0,Satisfactory,83,12.8,25.5,4.6,False,3.1144,Monsoon (Jul–Sep)
2019-09-29,16.91,22.84,8.85,68.0,Satisfactory,84,11.7,25.0,2.0,False,2.8279,Monsoon (Jul–Sep)
2019-09-30,29.42,27.89,8.22,75.0,Satisfactory,83,7.9,25.3,6.0,False,3.3817,Monsoon (Jul–Sep)
2019-10-01,33.92,28.0,8.5,98.0,Satisfactory,85,7.5,25.1,4.5,False,3.524,Other months
2019-10-02,40.16,29.72,8.95,105.0,Moderate,80,5.3,26.5,0.2,False,3.6929,Other months
2019-10-03,57.99,36.77,10.42,140.0,Moderate,73,4.5,27.5,0.0,False,4.0603,Other months
2019-10-04,43.07,34.07,8.34,113.0,Moderate,72,8.2,26.1,4.9,False,3.7628,Other months
2019-10-05,39.48,33.82,8.08,108.0,Moderate,66,10.4,26.1,0.0,False,3.6758,Other months
2019-10-06,58.75,36.98,8.62,127.0,Moderate,62,8.2,26.4,0.0,False,4.0733,Other months
2019-10-07,55.88,33.46,8.25,133.0,Moderate,62,10.9,26.3,0.0,False,4.0232,Other months
2019-10-08,44.85,33.4,8.91,123.0,Moderate,57,7.0,26.4,0.0,False,3.8033,Other months
2019-10-09,77.02,45.5,11.9,165.0,Moderate,61,6.3,25.5,0.0,False,4.3441,Other months
2019-10-10,100.82,50.32,13.83,208.0,Poor,59,5.9,26.4,0.0,False,4.6133,Other months
2019-10-11,98.07,48.05,11.02,243.0,Poor,54,5.7,26.6,0.0,False,4.5857,Other months
2019-10-12,103.45,48.54,11.26,235.0,Poor,57,6.6,27.3,0.0,False,4.6391,Other months
2019-10-13,132.57,51.27,12.75,282.0,Poor,52,6.8,27.7,0.0,False,4.8871,Other months
2019-10-14,116.33,50.83,11.46,285.0,Poor,58,7.5,27.0,0.0,False,4.7564,Other months
2019-10-15,133.35,58.61,13.31,291.0,Poor,62,6.2,27.1,0.0,False,4.893,Other months
2019-10-16,146.37,53.03,13.22,320.0,Very Poor,58,6.3,27.6,0.0,False,4.9861,Other months
2019-10-17,121.68,46.51,14.95,300.0,Poor,61,7.4,27.0,0.0,False,4.8014,Other months
2019-10-18,90.41,39.62,11.36,265.0,Poor,65,8.9,26.4,2.7,False,4.5044,Other months
2019-10-19,76.77,51.37,11.33,170.0,Moderate,67,5.8,25.5,2.5,False,4.3408,Other months
2019-10-20,98.05,48.83,10.64,242.0,Poor,49,9.3,25.7,0.0,False,4.5855,Other months
2019-10-21,115.16,51.05,11.11,254.0,Poor,51,10.8,25.0,0.0,False,4.7463,Other months
2019-10-22,93.51,50.05,11.7,243.0,Poor,48,12.0,24.4,0.0,False,4.5381,Other months
2019-10-23,122.12,57.92,14.08,248.0,Poor,54,8.5,24.4,0.0,False,4.805,Other months
2019-10-24,173.56,67.36,18.87,335.0,Very Poor,65,6.7,24.2,0.0,False,5.1565,Other months
2019-10-25,129.9,52.55,15.17,331.0,Very Poor,63,7.2,24.4,0.0,False,4.8668,Other months
2019-10-26,148.73,56.43,12.76,315.0,Very Poor,61,6.2,24.5,0.0,False,5.0021,Other months
2019-10-27,198.81,48.37,13.21,354.0,Very Poor,58,9.2,24.5,0.0,False,5.2923,Other months
2019-10-28,301.39,48.45,18.03,417.0,Severe,59,7.5,24.1,0.0,False,5.7084,Other months
2019-10-29,287.56,60.03,12.71,419.0,Severe,65,5.6,24.4,0.0,False,5.6614,Other months
2019-10-30,279.32,63.87,13.81,452.0,Severe,64,7.7,25.4,0.0,False,5.6324,Other months
2019-10-31,314.32,71.37,15.86,460.0,Severe,66,7.9,24.3,0.0,False,5.7504,Other months
2019-11-01,388.45,73.61,16.32,591.0,Severe,65,6.7,24.8,0.0,False,5.9622,Winter (Nov–Jan)
2019-11-02,320.26,54.1,12.88,473.0,Severe,69,9.3,24.4,0.2,False,5.7691,Winter (Nov–Jan)
2019-11-03,582.28,49.67,10.2,659.0,Severe,71,9.1,23.8,0.0,False,6.367,Winter (Nov–Jan)
2019-11-04,272.3,44.53,11.68,532.0,Severe,63,12.6,23.7,0.0,False,5.6069,Winter (Nov–Jan)
2019-11-05,190.41,44.32,13.17,385.0,Very Poor,57,12.5,22.9,0.0,False,5.2492,Winter (Nov–Jan)
2019-11-06,101.09,54.77,11.58,265.0,Poor,59,7.8,23.3,0.0,False,4.616,Winter (Nov–Jan)
2019-11-07,182.47,51.64,11.95,296.0,Poor,71,9.7,22.1,1.4,False,5.2066,Winter (Nov–Jan)
2019-11-08,154.14,52.79,14.04,346.0,Very Poor,74,7.1,21.9,0.8,False,5.0379,Winter (Nov–Jan)
2019-11-09,140.8,44.01,11.58,321.0,Very Poor,60,11.2,21.8,0.0,False,4.9473,Winter (Nov–Jan)
2019-11-10,192.35,50.35,13.95,339.0,Very Poor,60,9.5,20.8,0.0,False,5.2593,Winter (Nov–Jan)
2019-11-11,252.48,61.36,15.18,376.0,Very Poor,59,8.4,20.3,0.0,False,5.5313,Winter (Nov–Jan)
2019-11-12,384.34,66.1,14.41,475.0,Severe,62,8.2,19.6,0.0,False,5.9515,Winter (Nov–Jan)
2019-11-13,383.36,73.6,15.12,532.0,Severe,67,7.0,20.7,0.0,False,5.949,Winter (Nov–Jan)
2019-11-14,371.42,82.63,16.26,537.0,Severe,69,6.6,21.4,0.0,False,5.9173,Winter (Nov–Jan)
2019-11-15,423.52,59.35,14.14,595.0,Severe,72,9.0,21.0,0.0,False,6.0486,Winter (Nov–Jan)
2019-11-16,174.03,42.35,12.89,438.0,Severe,64,14.0,21.9,0.0,False,5.1592,Winter (Nov–Jan)
2019-11-17,96.34,33.78,10.78,273.0,Poor,61,18.4,21.7,0.0,False,4.5679,Winter (Nov–Jan)
2019-11-18,108.4,40.05,10.55,245.0,Poor,64,12.6,19.9,0.0,False,4.6858,Winter (Nov–Jan)
2019-11-19,126.92,52.79,12.05,251.0,Poor,66,9.3,19.4,0.0,False,4.8436,Winter (Nov–Jan)
2019-11-20,175.19,77.62,14.74,315.0,Very Poor,65,5.8,19.1,0.0,False,5.1659,Winter (Nov–Jan)
2019-11-21,217.7,91.65,19.85,375.0,Very Poor,67,7.1,19.6,0.0,False,5.3831,Winter (Nov–Jan)
2019-11-22,201.17,75.08,16.02,377.0,Very Poor,65,6.6,20.6,0.0,False,5.3042,Winter (Nov–Jan)
2019-11-23,130.41,52.7,11.64,334.0,Very Poor,62,10.6,20.6,0.0,False,4.8707,Winter (Nov–Jan)
2019-11-24,107.86,43.51,11.35,264.0,Poor,64,11.1,20.7,0.0,False,4.6808,Winter (Nov–Jan)
2019-11-25,122.37,53.29,13.59,269.0,Poor,67,6.6,20.0,0.0,False,4.807,Winter (Nov–Jan)
2019-11-26,114.27,53.83,17.65,284.0,Poor,67,9.5,20.1,0.9,False,4.7386,Winter (Nov–Jan)
2019-11-27,65.7,42.94,10.71,166.0,Moderate,68,7.1,19.7,0.0,False,4.1851,Winter (Nov–Jan)
2019-11-28,31.03,32.3,8.99,106.0,Moderate,83,13.4,18.3,22.1,False,3.435,Winter (Nov–Jan)
2019-11-29,53.79,41.9,10.14,89.0,Satisfactory,82,6.1,17.7,0.0,False,3.9851,Winter (Nov–Jan)
2019-11-30,96.96,45.04,9.87,175.0,Moderate,78,8.8,17.0,0.0,False,4.5743,Winter (Nov–Jan)
2019-12-01,123.66,50.39,11.39,257.0,Poor,74,8.5,15.5,0.0,False,4.8175,Winter (Nov–Jan)
2019-12-02,141.12,57.23,11.18,299.0,Poor,70,9.8,15.4,0.0,False,4.9496,Winter (Nov–Jan)
2019-12-03,140.07,60.85,11.37,302.0,Very Poor,66,10.8,15.1,0.0,False,4.9421,Winter (Nov–Jan)
2019-12-04,163.24,71.65,13.48,313.0,Very Poor,72,6.4,15.3,0.0,False,5.0952,Winter (Nov–Jan)
2019-12-05,271.99,91.53,14.48,389.0,Very Poor,74,6.6,15.4,0.0,False,5.6058,Winter (Nov–Jan)
2019-12-06,241.69,69.73,13.41,423.0,Severe,82,6.5,15.4,0.0,False,5.4877,Winter (Nov–Jan)
2019-12-07,233.79,66.41,15.4,382.0,Very Poor,79,5.7,16.0,0.0,False,5.4544,Winter (Nov–Jan)
2019-12-08,239.98,68.59,13.69,404.0,Severe,79,6.9,15.7,0.0,False,5.4806,Winter (Nov–Jan)
2019-12-09,200.33,68.28,12.34,371.0,Very Poor,73,6.2,15.3,0.0,False,5.3,Winter (Nov–Jan)
2019-12-10,236.4,72.63,12.49,377.0,Very Poor,70,7.4,15.1,0.0,False,5.4655,Winter (Nov–Jan)
2019-12-11,299.85,85.56,14.71,430.0,Severe,71,6.1,15.7,0.0,False,5.7033,Winter (Nov–Jan)
2019-12-12,284.18,64.36,12.61,471.0,Severe,78,13.3,15.6,5.9,False,5.6496,Winter (Nov–Jan)
2019-12-13,94.62,41.21,7.9,322.0,Very Poor,87,12.3,15.1,3.7,False,4.5499,Winter (Nov–Jan)
2019-12-14,78.59,41.29,9.04,179.0,Moderate,85,5.0,13.0,0.0,False,4.3642,Winter (Nov–Jan)
2019-12-15,94.67,39.9,8.5,205.0,Poor,80,8.1,13.2,0.0,False,4.5504,Winter (Nov–Jan)
2019-12-16,88.05,35.06,7.17,202.0,Poor,80,10.2,12.4,0.0,False,4.4779,Winter (Nov–Jan)
2019-12-17,93.07,32.7,7.26,178.0,Moderate,80,10.1,11.8,0.0,False,4.5334,Winter (Nov–Jan)
2019-12-18,144.0,44.41,7.98,273.0,Poor,78,9.4,11.9,0.0,False,4.9698,Winter (Nov–Jan)
2019-12-19,261.16,55.64,9.64,354.0,Very Poor,80,5.4,11.5,0.0,False,5.5651,Winter (Nov–Jan)
2019-12-20,316.09,60.58,9.92,452.0,Severe,79,5.1,13.0,0.0,False,5.756,Winter (Nov–Jan)
2019-12-21,249.87,50.24,8.52,441.0,Severe,81,6.2,13.4,0.2,False,5.5209,Winter (Nov–Jan)
2019-12-22,146.81,38.96,6.67,351.0,Very Poor,84,10.1,12.5,0.0,False,4.9891,Winter (Nov–Jan)
2019-12-23,171.47,39.83,7.0,321.0,Very Poor,82,10.5,11.8,0.0,False,5.1444,Winter (Nov–Jan)
2019-12-24,262.69,56.72,8.7,376.0,Very Poor,90,6.2,9.6,0.0,False,5.571,Winter (Nov–Jan)
2019-12-25,166.71,39.77,6.96,384.0,Very Poor,87,9.7,8.7,0.0,False,5.1163,Winter (Nov–Jan)
2019-12-26,196.97,45.08,6.99,340.0,Very Poor,84,11.2,8.4,0.0,False,5.2831,Winter (Nov–Jan)
2019-12-27,240.07,54.6,7.88,372.0,Very Poor,88,7.2,7.3,0.0,False,5.4809,Winter (Nov–Jan)
2019-12-28,275.6,55.98,10.26,425.0,Severe,90,6.5,6.7,0.0,False,5.619,Winter (Nov–Jan)
2019-12-29,326.79,57.76,10.25,455.0,Severe,86,5.2,7.3,0.0,False,5.7893,Winter (Nov–Jan)
2019-12-30,333.43,55.61,11.15,506.0,Severe,89,6.8,6.9,0.0,False,5.8094,Winter (Nov–Jan)
2019-12-31,245.53,47.5,11.03,417.0,Severe,78,6.8,7.6,0.0,False,5.5034,Winter (Nov–Jan)
2020-01-01,372.14,64.18,18.49,492.0,Severe,79,8.1,10.0,0.0,False,5.9193,Winter (Nov–Jan)
2020-01-02,327.04,64.8,19.95,485.0,Severe,79,8.6,12.9,0.0,False,5.7901,Winter (Nov–Jan)
2020-01-03,228.9,55.65,14.93,426.0,Severe,78,6.5,14.0,0.1,False,5.4333,Winter (Nov–Jan)
2020-01-04,220.6,57.67,12.85,366.0,Very Poor,82,5.4,13.4,0.5,False,5.3964,Winter (Nov–Jan)
2020-01-05,170.21,48.25,9.59,354.0,Very Poor,74,9.1,13.3,0.0,False,5.137,Winter (Nov–Jan)
2020-01-06,159.64,51.19,11.34,335.0,Very Poor,76,6.7,13.5,0.0,False,5.0729,Winter (Nov–Jan)
2020-01-07,120.31,44.9,12.74,285.0,Poor,83,9.8,14.0,2.1,False,4.7901,Winter (Nov–Jan)
2020-01-08,117.98,38.64,8.67,281.0,Poor,92,9.2,12.8,17.5,False,4.7705,Winter (Nov–Jan)
2020-01-09,89.26,32.3,7.28,231.0,Poor,78,12.0,10.5,0.0,False,4.4916,Winter (Nov–Jan)
2020-01-10,130.82,45.12,9.44,255.0,Poor,77,11.7,10.1,0.0,False,4.8738,Winter (Nov–Jan)
2020-01-11,151.1,53.28,11.65,309.0,Very Poor,77,9.3,10.3,0.0,False,5.0179,Winter (Nov–Jan)
2020-01-12,207.23,59.91,12.35,352.0,Very Poor,78,8.4,11.8,0.0,False,5.3338,Winter (Nov–Jan)
2020-01-13,218.98,55.04,11.59,381.0,Very Poor,83,10.5,14.6,16.6,False,5.389,Winter (Nov–Jan)
2020-01-14,115.62,38.08,9.24,314.0,Very Poor,86,8.6,14.0,0.3,False,4.7503,Winter (Nov–Jan)
2020-01-15,111.57,47.45,10.68,241.0,Poor,83,8.6,12.4,0.0,False,4.7147,Winter (Nov–Jan)
2020-01-16,139.06,44.21,10.44,286.0,Poor,90,7.7,12.4,11.1,False,4.9349,Winter (Nov–Jan)
2020-01-17,107.65,36.19,9.69,287.0,Poor,88,7.6,13.0,0.6,False,4.6789,Winter (Nov–Jan)
2020-01-18,125.3,43.78,9.65,262.0,Poor,89,6.3,12.5,0.2,False,4.8307,Winter (Nov–Jan)
2020-01-19,125.04,34.18,8.69,290.0,Poor,82,9.3,11.7,0.0,False,4.8286,Winter (Nov–Jan)
2020-01-20,142.18,38.21,9.65,282.0,Poor,84,8.2,12.1,0.0,False,4.9571,Winter (Nov–Jan)
2020-01-21,222.81,48.18,12.24,359.0,Very Poor,86,5.8,12.9,0.0,False,5.4063,Winter (Nov–Jan)
2020-01-22,198.88,44.3,10.95,378.0,Very Poor,82,10.1,12.5,0.0,False,5.2927,Winter (Nov–Jan)
2020-01-23,74.45,35.26,8.71,273.0,Poor,66,17.9,12.5,0.0,False,4.3101,Winter (Nov–Jan)
2020-01-24,79.83,44.0,10.73,155.0,Moderate,60,17.7,12.8,0.0,False,4.3799,Winter (Nov–Jan)
2020-01-25,136.72,56.31,12.36,251.0,Poor,74,7.7,11.8,0.0,False,4.9179,Winter (Nov–Jan)
2020-01-26,201.2,50.94,12.81,349.0,Very Poor,79,7.0,13.6,0.0,False,5.3043,Winter (Nov–Jan)
2020-01-27,209.97,67.09,14.72,365.0,Very Poor,77,8.2,14.0,0.4,False,5.347,Winter (Nov–Jan)
2020-01-28,104.45,42.01,11.12,302.0,Very Poor,83,13.2,14.2,16.0,False,4.6487,Winter (Nov–Jan)
2020-01-29,77.95,42.24,9.85,218.0,Poor,82,6.6,13.3,0.5,False,4.3561,Winter (Nov–Jan)
2020-01-30,91.56,45.04,10.06,195.0,Moderate,77,11.2,12.6,0.0,False,4.517,Winter (Nov–Jan)
2020-01-31,92.04,47.35,9.9,203.0,Poor,74,9.3,12.1,0.0,False,4.5222,Winter (Nov–Jan)
2020-02-01,112.13,44.25,10.02,244.0,Poor,74,7.7,12.3,0.0,False,4.7197,Other months
2020-02-02,120.86,45.28,10.32,254.0,Poor,76,10.1,11.7,0.0,False,4.7946,Other months
2020-02-03,138.5,53.71,11.4,297.0,Poor,74,8.3,12.0,0.0,False,4.9309,Other months
2020-02-04,188.42,64.8,15.26,336.0,Very Poor,74,8.1,13.0,0.0,False,5.2387,Other months
2020-02-05,150.08,53.35,13.31,344.0,Very Poor,74,10.3,12.9,0.0,False,5.0112,Other months
2020-02-06,118.57,51.82,12.08,277.0,Poor,75,8.2,11.7,0.0,False,4.7755,Other months
2020-02-07,150.15,58.46,14.21,307.0,Very Poor,71,6.7,12.7,0.1,False,5.0116,Other months
2020-02-08,149.67,47.55,14.39,315.0,Very Poor,75,8.5,12.4,0.0,False,5.0084,Other months
2020-02-09,151.43,50.75,14.64,310.0,Very Poor,75,8.0,12.8,0.0,False,5.0201,Other months
2020-02-10,174.4,56.48,14.83,328.0,Very Poor,73,9.1,13.2,0.0,False,5.1614,Other months
2020-02-11,176.57,60.12,14.37,347.0,Very Poor,73,8.6,13.5,0.0,False,5.1737,Other months
2020-02-12,172.12,55.96,16.24,343.0,Very Poor,68,13.2,15.9,0.0,False,5.1482,Other months
2020-02-13,95.72,41.59,16.49,279.0,Poor,57,18.9,19.2,0.0,False,4.5614,Other months
2020-02-14,73.84,34.6,13.53,186.0,Moderate,51,21.6,18.5,0.0,False,4.3019,Other months
2020-02-15,83.07,44.57,17.59,174.0,Moderate,47,16.4,17.5,0.0,False,4.4197,Other months
2020-02-16,132.63,57.15,19.61,254.0,Poor,60,10.2,17.1,0.0,False,4.8876,Other months
2020-02-17,158.69,61.17,18.85,323.0,Very Poor,56,10.8,17.5,0.0,False,5.067,Other months
2020-02-18,125.53,59.91,23.01,292.0,Poor,48,13.4,17.0,0.0,False,4.8325,Other months
2020-02-19,138.46,59.9,20.13,300.0,Poor,54,14.9,18.2,0.0,False,4.9306,Other months
2020-02-20,98.84,44.05,14.91,253.0,Poor,62,20.1,20.0,2.1,False,4.5935,Other months
2020-02-21,53.11,33.27,10.45,170.0,Moderate,84,18.2,16.2,13.4,False,3.9724,Other months
2020-02-22,63.62,41.23,13.38,104.0,Moderate,79,8.8,17.8,0.7,False,4.1529,Other months
2020-02-23,105.71,42.24,14.3,221.0,Poor,82,7.2,17.5,2.6,False,4.6607,Other months
2020-02-24,70.59,44.2,15.94,169.0,Moderate,78,8.0,17.6,0.1,False,4.2569,Other months
2020-02-25,127.75,46.76,18.24,244.0,Poor,74,9.2,18.0,0.0,False,4.8501,Other months
2020-02-26,141.81,50.67,17.61,303.0,Very Poor,74,6.6,18.6,0.0,False,4.9545,Other months
2020-02-27,107.28,46.15,14.7,270.0,Poor,76,8.1,19.1,0.0,False,4.6754,Other months
2020-02-28,83.48,33.92,11.55,214.0,Poor,74,15.8,20.3,0.0,False,4.4246,Other months
2020-02-29,60.01,33.98,12.05,144.0,Moderate,82,14.8,18.7,9.1,False,4.0945,Other months
2020-03-01,42.83,40.73,12.19,105.0,Moderate,80,8.6,19.1,0.0,False,3.7572,Other months
2020-03-02,99.34,50.23,15.81,192.0,Moderate,78,6.2,19.7,0.2,False,4.5985,Other months
2020-03-03,86.26,46.6,15.48,226.0,Poor,70,7.8,19.6,0.0,False,4.4574,Other months
2020-03-04,82.9,45.62,16.22,200.0,Moderate,72,8.6,19.2,1.0,False,4.4176,Other months
2020-03-05,31.43,32.97,11.32,112.0,Moderate,79,13.9,18.2,13.0,False,3.4478,Other months
2020-03-06,21.32,33.71,10.42,82.0,Satisfactory,86,18.2,16.4,23.3,False,3.0596,Other months
2020-03-07,40.96,35.53,11.84,77.0,Satisfactory,85,10.7,15.9,1.7,False,3.7126,Other months
2020-03-08,72.1,37.14,12.61,156.0,Moderate,79,7.2,16.5,0.0,False,4.2781,Other months
2020-03-09,58.04,32.29,13.33,138.0,Moderate,67,14.0,17.0,0.0,False,4.0611,Other months
2020-03-10,84.35,30.22,17.21,186.0,Moderate,68,6.4,17.1,0.0,False,4.435,Other months
2020-03-11,55.19,29.76,13.82,128.0,Moderate,74,14.3,18.7,2.6,False,4.0108,Other months
2020-03-12,56.92,36.74,13.68,125.0,Moderate,67,13.2,19.6,0.0,False,4.0416,Other months
2020-03-13,68.72,40.53,15.42,170.0,Moderate,65,8.3,18.7,10.0,False,4.23,Other months
2020-03-14,39.41,34.59,11.59,131.0,Moderate,82,10.2,16.4,4.2,False,3.674,Other months
2020-03-15,60.99,41.09,13.92,124.0,Moderate,78,5.5,16.3,0.1,False,4.1107,Other months
2020-03-16,61.61,41.52,14.8,148.0,Moderate,75,9.6,18.0,0.0,False,4.1208,Other months
2020-03-17,69.7,43.5,15.06,164.0,Moderate,71,10.7,18.9,0.0,False,4.2442,Other months
2020-03-18,68.93,45.86,14.93,162.0,Moderate,67,11.0,20.4,0.0,False,4.2331,Other months
2020-03-19,90.62,45.67,17.66,191.0,Moderate,71,7.7,20.8,0.2,False,4.5067,Other months
2020-03-20,90.31,51.26,19.71,209.0,Poor,69,8.1,21.2,0.4,False,4.5032,Other months
2020-03-21,82.39,46.04,18.55,205.0,Poor,70,5.3,21.7,1.6,False,4.4115,Other months
2020-03-22,78.61,29.85,16.63,198.0,Moderate,68,8.1,22.0,0.0,False,4.3645,Other months
2020-03-23,54.26,25.96,15.17,127.0,Moderate,61,5.6,22.5,0.0,False,3.9938,Other months
2020-03-24,55.85,27.07,15.81,124.0,Moderate,64,7.4,23.6,0.7,False,4.0227,Other months
2020-03-25,37.87,21.11,11.49,92.0,Satisfactory,62,10.1,23.8,0.0,False,3.6342,Other months
2020-03-26,45.69,16.58,12.82,93.0,Satisfactory,61,12.7,23.5,0.0,False,3.8219,Other months
2020-03-27,26.89,15.32,11.04,76.0,Satisfactory,74,10.7,21.4,6.0,False,3.2918,Other months
2020-03-28,21.23,17.52,10.28,51.0,Satisfactory,69,10.5,21.3,0.1,False,3.0554,Other months
2020-03-29,27.59,16.6,10.39,64.0,Satisfactory,59,14.5,21.9,0.0,False,3.3175,Other months
2020-03-30,35.08,17.52,12.47,74.0,Satisfactory,55,12.1,21.9,0.0,False,3.5576,Other months
2020-03-31,35.31,18.03,12.33,81.0,Satisfactory,56,11.4,22.7,0.1,False,3.5642,Other months
2020-04-01,32.88,19.17,13.0,80.0,Satisfactory,56,7.4,23.9,0.0,False,3.4929,Other months
2020-04-02,28.51,17.18,10.84,78.0,Satisfactory,53,14.7,23.3,0.0,False,3.3503,Other months
2020-04-03,31.36,20.07,11.99,84.0,Satisfactory,44,12.0,22.4,0.0,False,3.4455,Other months
2020-04-04,40.79,22.38,12.59,90.0,Satisfactory,48,11.8,23.2,0.0,False,3.7084,Other months
2020-04-05,51.79,24.42,16.03,103.0,Moderate,53,9.0,24.0,0.0,False,3.9472,Other months
2020-04-06,59.91,24.37,15.59,134.0,Moderate,46,10.0,26.2,0.0,False,4.0928,Other months
2020-04-07,33.12,19.27,13.46,100.0,Satisfactory,46,13.7,25.0,0.4,False,3.5001,Other months
2020-04-08,29.7,18.56,12.85,91.0,Satisfactory,46,11.9,24.9,0.0,False,3.3911,Other months
2020-04-09,36.13,21.37,14.2,89.0,Satisfactory,46,10.6,24.4,0.0,False,3.5871,Other months
2020-04-10,57.67,27.12,16.32,111.0,Moderate,47,8.4,25.7,0.0,False,4.0547,Other months
2020-04-11,53.03,23.64,18.38,126.0,Moderate,42,8.1,27.7,0.0,False,3.9709,Other months
2020-04-12,38.57,17.59,15.7,102.0,Moderate,42,11.3,28.0,0.0,False,3.6525,Other months
2020-04-13,60.6,23.4,19.86,119.0,Moderate,41,10.9,29.3,0.0,False,4.1043,Other months
2020-04-14,58.22,25.71,17.38,134.0,Moderate,41,8.7,30.1,0.0,False,4.0642,Other months
2020-04-15,58.31,24.55,14.89,152.0,Moderate,38,10.2,30.4,0.0,False,4.0658,Other months
2020-04-16,69.8,25.01,19.42,172.0,Moderate,36,10.2,30.3,0.0,False,4.2456,Other months
2020-04-17,26.93,15.83,14.08,123.0,Moderate,34,12.7,29.6,0.0,False,3.2932,Other months
2020-04-18,29.09,15.45,12.63,102.0,Moderate,38,13.8,29.0,0.0,False,3.3704,Other months
2020-04-19,35.49,19.72,13.17,95.0,Satisfactory,43,9.8,27.9,0.0,False,3.5693,Other months
2020-04-20,52.86,24.56,15.06,115.0,Moderate,45,7.6,26.8,0.4,False,3.9676,Other months
2020-04-21,37.17,19.64,15.36,102.0,Moderate,51,8.4,26.1,0.0,False,3.6155,Other months
2020-04-22,58.25,24.79,17.34,122.0,Moderate,41,7.8,27.5,0.0,False,4.0647,Other months
2020-04-23,54.71,24.83,17.39,129.0,Moderate,38,10.1,28.9,0.0,False,4.002,Other months
2020-04-24,65.91,25.62,18.62,143.0,Moderate,41,7.0,28.9,0.0,False,4.1883,Other months
2020-04-25,33.09,18.68,12.76,121.0,Moderate,43,8.1,28.5,0.5,False,3.4992,Other months
2020-04-26,40.24,17.45,16.21,119.0,Moderate,58,14.5,26.9,1.0,False,3.6949,Other months
2020-04-27,27.18,14.8,15.59,98.0,Satisfactory,69,16.4,25.4,2.8,False,3.3025,Other months
2020-04-28,41.75,17.35,17.6,105.0,Moderate,64,9.0,26.4,0.2,False,3.7317,Other months
2020-04-29,55.18,20.11,19.08,123.0,Moderate,55,7.2,28.6,0.0,False,4.0106,Other months
2020-04-30,49.96,17.61,17.42,128.0,Moderate,51,10.8,29.4,0.2,False,3.9112,Other months
2020-05-01,61.04,18.46,17.52,140.0,Moderate,54,10.7,30.5,0.0,False,4.1115,Other months
2020-05-02,34.67,14.36,13.0,127.0,Moderate,57,18.4,29.3,0.9,False,3.5459,Other months
2020-05-03,32.56,15.14,11.94,110.0,Moderate,64,13.7,27.7,21.8,False,3.4831,Other months
2020-05-04,26.63,16.95,11.92,92.0,Satisfactory,66,7.0,27.2,0.0,False,3.282,Other months
2020-05-05,56.24,21.36,16.4,117.0,Moderate,50,7.7,28.8,0.0,False,4.0296,Other months
2020-05-06,58.44,21.88,15.78,139.0,Moderate,45,7.5,28.6,0.0,False,4.068,Other months
2020-05-07,36.02,17.97,13.6,140.0,Moderate,44,10.3,28.6,0.0,False,3.5841,Other months
2020-05-08,51.09,21.66,13.82,138.0,Moderate,40,9.4,30.7,0.0,False,3.9336,Other months
2020-05-09,54.18,17.65,13.33,142.0,Moderate,41,9.9,31.6,0.0,False,3.9923,Other months
2020-05-10,44.3,16.46,12.02,127.0,Moderate,54,13.2,29.6,0.8,False,3.791,Other months
2020-05-11,43.26,19.53,12.66,113.0,Moderate,57,11.2,29.1,0.3,False,3.7672,Other months
2020-05-12,43.19,18.49,13.84,122.0,Moderate,55,10.0,29.4,0.0,False,3.7656,Other months
2020-05-13,68.8,21.34,15.41,132.0,Moderate,55,7.7,29.7,0.3,False,4.2312,Other months
2020-05-14,56.17,25.12,12.92,154.0,Moderate,53,7.3,30.5,0.0,False,4.0284,Other months
2020-05-15,47.44,23.45,13.71,125.0,Moderate,41,12.2,31.4,0.0,False,3.8595,Other months
2020-05-16,81.87,26.17,16.19,175.0,Moderate,33,12.4,31.5,0.0,False,4.4051,Other months
2020-05-17,98.63,31.96,20.19,202.0,Poor,32,8.8,31.8,0.0,False,4.5914,Other months
2020-05-18,101.02,34.76,22.11,222.0,Poor,30,10.2,31.4,0.0,False,4.6153,Other months
2020-05-19,106.63,42.67,20.41,238.0,Poor,22,7.8,32.1,0.0,False,4.6694,Other months
2020-05-20,67.8,32.8,18.96,196.0,Moderate,26,12.7,30.8,0.0,False,4.2166,Other months
2020-05-21,55.92,31.36,18.99,149.0,Moderate,26,13.7,32.2,0.0,False,4.0239,Other months
2020-05-22,94.37,45.36,26.05,199.0,Moderate,26,6.4,34.0,0.0,False,4.5472,Other months
2020-05-23,74.92,42.43,17.05,202.0,Poor,28,8.8,34.6,0.0,False,4.3164,Other months
2020-05-24,55.37,27.35,17.11,174.0,Moderate,25,12.6,35.6,0.0,False,4.014,Other months
2020-05-25,61.46,30.92,21.3,157.0,Moderate,22,12.8,35.7,0.0,False,4.1184,Other months
2020-05-26,55.38,37.79,16.82,153.0,Moderate,19,11.0,36.9,0.0,False,4.0142,Other months
2020-05-27,43.22,26.95,14.49,156.0,Moderate,21,9.9,36.5,0.0,False,3.7663,Other months
2020-05-28,39.07,17.1,11.68,174.0,Moderate,41,19.6,33.0,0.1,False,3.6654,Other months
2020-05-29,24.62,19.02,9.95,129.0,Moderate,58,20.7,30.1,4.2,False,3.2036,Other months
2020-05-30,23.09,18.51,9.95,84.0,Satisfactory,61,12.1,28.2,5.4,False,3.1394,Other months
2020-05-31,21.51,17.05,9.06,80.0,Satisfactory,69,7.6,26.8,0.2,False,3.0685,Other months
2020-06-01,41.05,22.99,14.02,100.0,Satisfactory,67,6.5,27.8,0.0,False,3.7148,Other months
2020-06-02,45.9,24.78,12.71,123.0,Moderate,62,6.5,29.0,0.0,False,3.8265,Other months
2020-06-03,50.62,28.02,15.91,123.0,Moderate,58,6.2,29.9,0.0,False,3.9243,Other months
2020-06-04,68.24,34.11,17.97,144.0,Moderate,57,7.1,29.6,0.0,False,4.223,Other months
2020-06-05,42.43,25.87,12.46,126.0,Moderate,60,8.2,29.0,0.0,False,3.7479,Other months
2020-06-06,35.14,21.25,10.69,102.0,Moderate,58,7.6,29.5,0.0,False,3.5593,Other months
2020-06-07,39.99,22.65,11.89,104.0,Moderate,59,8.4,30.6,1.2,False,3.6886,Other months
2020-06-08,46.9,25.81,15.78,112.0,Moderate,60,6.9,30.8,0.1,False,3.848,Other months
2020-06-09,64.77,32.01,15.06,138.0,Moderate,51,6.5,33.0,0.0,False,4.1708,Other months
2020-06-10,58.9,34.31,14.12,154.0,Moderate,52,7.5,33.7,0.0,False,4.0758,Other months
2020-06-11,54.69,30.94,12.74,142.0,Moderate,53,6.4,33.5,0.0,False,4.0017,Other months
2020-06-12,64.0,30.05,12.9,152.0,Moderate,52,9.0,33.8,0.0,False,4.1589,Other months
2020-06-13,52.36,25.46,10.59,132.0,Moderate,55,9.0,33.6,0.0,False,3.9581,Other months
2020-06-14,71.08,26.01,13.57,147.0,Moderate,56,8.6,33.6,0.0,False,4.2638,Other months
2020-06-15,48.69,25.95,12.57,130.0,Moderate,47,8.7,34.3,0.0,False,3.8855,Other months
2020-06-16,39.87,24.58,12.08,126.0,Moderate,48,9.4,33.8,0.1,False,3.6856,Other months
2020-06-17,34.35,16.94,10.84,110.0,Moderate,52,11.5,33.9,0.0,False,3.5366,Other months
2020-06-18,36.84,18.32,12.19,107.0,Moderate,50,10.1,34.6,0.0,False,3.6066,Other months
2020-06-19,57.6,17.78,11.98,132.0,Moderate,53,11.2,34.9,0.0,False,4.0535,Other months
2020-06-20,35.96,20.37,10.98,158.0,Moderate,54,12.0,33.7,1.2,False,3.5824,Other months
2020-06-21,39.7,23.7,11.71,105.0,Moderate,54,9.0,33.4,0.0,False,3.6814,Other months
2020-06-22,39.47,20.61,11.08,104.0,Moderate,61,7.2,31.9,1.0,False,3.6755,Other months
2020-06-23,29.02,16.39,11.09,85.0,Satisfactory,64,14.3,31.5,2.0,False,3.368,Other months
2020-06-24,30.91,16.84,11.02,71.0,Satisfactory,72,11.7,30.3,3.1,False,3.4311,Other months
2020-06-25,38.37,21.41,11.28,86.0,Satisfactory,66,5.5,31.9,0.0,False,3.6473,Other months
2020-06-26,50.01,22.06,11.66,104.0,Moderate,65,10.0,32.4,1.4,False,3.9122,Other months
2020-06-27,39.8,21.46,10.38,112.0,Moderate,57,13.6,33.7,0.1,False,3.6839,Other months
2020-06-28,59.52,21.6,10.7,196.0,Moderate,51,13.9,35.0,0.2,False,4.0863,Other months
2020-06-29,44.86,21.57,11.58,233.0,Poor,54,12.8,34.4,0.5,False,3.8035,Other months
2020-06-30,39.8,17.96,10.51,114.0,Moderate,63,12.2,32.2,0.0,False,3.6839,Other months
2020-07-01,54.01,21.05,11.15,101.0,Moderate,59,8.4,33.4,0.0,False,3.9892,Monsoon (Jul–Sep)
```

## Delhi stations: PM2.5 mean and number of days per station and year (from station_day.csv; the city series is the mean over reporting stations)
```
StationId,mean_2015,mean_2016,mean_2017,mean_2018,mean_2019,mean_2020,count_2015,count_2016,count_2017,count_2018,count_2019,count_2020
DL001,,,,219.98,106.0,79.9,,,,47.0,355.0,181.0
DL002,155.91,170.7,193.76,160.59,128.54,99.35,254.0,326.0,218.0,311.0,364.0,154.0
DL003,,,,118.89,120.71,88.77,,,,333.0,365.0,181.0
DL004,,,142.44,94.63,82.47,62.68,,,95.0,352.0,360.0,176.0
DL005,,,,117.72,131.05,104.56,,,,181.0,365.0,176.0
DL006,,,120.02,131.24,111.29,,,,114.0,260.0,288.0,
DL007,127.15,198.05,208.03,125.13,103.4,79.23,213.0,2.0,81.0,356.0,365.0,183.0
DL008,67.5,,286.13,129.33,119.06,94.21,1.0,,77.0,357.0,360.0,179.0
DL009,,,,73.4,97.5,70.81,,,,305.0,365.0,183.0
DL010,,,,106.15,109.18,86.87,,,,333.0,365.0,183.0
DL012,,,155.08,84.63,94.93,66.73,,,95.0,362.0,331.0,181.0
DL013,127.24,115.81,132.95,102.22,113.41,70.5,194.0,126.0,76.0,362.0,364.0,183.0
DL014,178.17,,188.46,124.45,109.11,98.16,3.0,,80.0,355.0,362.0,181.0
DL015,,,,144.52,128.13,98.65,,,,333.0,365.0,183.0
DL016,,,,103.02,104.23,73.77,,,,333.0,364.0,181.0
DL017,,,156.66,90.02,85.27,68.91,,,98.0,356.0,357.0,170.0
DL018,,,,101.95,93.74,73.78,,,,334.0,365.0,181.0
DL019,96.15,84.71,225.83,109.56,103.26,70.01,255.0,185.0,67.0,364.0,365.0,179.0
DL020,,,,141.85,125.59,96.96,,,,182.0,364.0,181.0
DL021,80.07,131.68,172.07,118.92,113.43,89.61,248.0,283.0,167.0,363.0,365.0,183.0
DL022,,,,86.94,92.54,72.79,,,,334.0,363.0,174.0
DL023,,,,120.73,109.02,91.0,,,,334.0,365.0,168.0
DL024,,,,120.69,123.37,96.84,,,,333.0,365.0,183.0
DL025,,,187.69,110.73,109.38,66.52,,,79.0,346.0,324.0,183.0
DL026,,,,103.73,107.29,80.64,,,,333.0,364.0,183.0
DL027,,,,99.79,99.85,72.21,,,,331.0,365.0,181.0
DL028,123.25,106.42,266.81,131.01,106.4,88.51,252.0,291.0,64.0,363.0,363.0,178.0
DL029,,,,105.23,100.41,80.23,,,,179.0,365.0,162.0
DL030,,,118.95,82.29,82.39,66.51,,,94.0,356.0,362.0,139.0
DL031,118.41,135.69,169.47,123.66,101.14,63.68,258.0,338.0,198.0,363.0,364.0,180.0
DL032,,,,127.15,128.29,103.57,,,,326.0,364.0,177.0
DL033,77.28,,203.37,112.83,118.88,66.48,77.0,,90.0,365.0,360.0,183.0
DL034,,287.28,133.36,107.17,108.33,80.41,,59.0,333.0,340.0,358.0,182.0
DL035,,,,116.62,105.55,78.18,,,,334.0,364.0,180.0
DL036,,,,92.78,90.87,66.31,,,,182.0,365.0,181.0
DL037,,,,108.63,115.01,87.75,,,,331.0,364.0,183.0
DL038,,,,136.22,135.04,96.65,,,,334.0,365.0,180.0
```



# 07 Checker and figure code

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
    offline_ = code in ("000", "")  # no network (sandbox): do not fail the numerical checks, fall back to the local copies
    ok_ = offline_ or code in ("200", "301", "302") or ("kaggle.com" in url and code in ("403", "404") and (ROOT / "data/raw/station_day.csv").exists())  # kaggle blocks scripted GETs; the slug is proven by the downloads
    local_ = (ROOT / "data/raw/city_day.csv").exists() and (ROOT / "data/raw/delhi_weather_openmeteo.json").exists()
    check(f"link reachable (or offline with local raw files present): {url}", ok_ and (not offline_ or local_), f"HTTP {code}" + (" OFFLINE, local copies used" if offline_ else ""))
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
pers = [np.abs(wk.pm25.loc[f"{y_}-01-01":f"{y_}-12-31"] - wk.pm25.shift(1).loc[f"{y_}-01-01":f"{y_}-12-31"]).mean() for y_ in (2018, 2019)]  # every test week (the previous week is in the training history)
check(f"persistence one-week MAE 2018/2019 = {pers[0]:.1f}/{pers[1]:.1f}", close(pers[0], ow.loc["Persistence", "2018"], 0.01) and close(pers[1], ow.loc["Persistence", "2019"], 0.01))
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
mth_ = lambda i_: a20_[a20_.index.month == i_].mean()  # noqa: E731  (month number i_, 1 = Jan)
chk_ = {m_: (i_, mth_(i_), o20.loc[m_, "lo95"], o20.loc[m_, "hi95"]) for i_, m_ in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun"], start=1)}
check("2020 actual Jan-Feb inside interval, Mar-Jun below it (each month compared with ITS OWN interval)",
      all(chk_[m_][2] <= chk_[m_][1] <= chk_[m_][3] for m_ in ("Jan", "Feb")) and all(chk_[m_][1] < chk_[m_][2] for m_ in ("Mar", "Apr", "May", "Jun")),
      "; ".join(f"{m_} {v[1]:.1f} vs [{v[2]:.1f},{v[3]:.1f}]" for m_, v in chk_.items()))
# station check
st_ = pd.read_csv(ROOT / "data/raw/station_day.csv", parse_dates=["Date"]); meta_ = pd.read_csv(ROOT / "data/raw/stations.csv")
xs_ = st_[st_.StationId.isin(meta_.loc[meta_.City == "Delhi", "StationId"])].dropna(subset=["PM2.5"])
nst = xs_.groupby(xs_.Date.dt.year).StationId.nunique()
cm_ = pd.concat([d.pm25, xs_.groupby("Date")["PM2.5"].mean()], axis=1, keys=["c", "s"]).dropna()
check(f"stations per year {nst.loc[2015]},{nst.loc[2016]},..,{nst.loc[2019]}; corr(city, station mean) = {cm_.corr().iloc[0, 1]:.3f}", nst.loc[2015] == 10 and nst.loc[2018] == 37 and close(cm_.corr().iloc[0, 1], 0.995, 0.002))
sc = pd.read_csv(RES / "station_check.csv", index_col=0)
check("decline 2016->2019 on slide matches station table", macros["declPanel"] == f"{abs((np.exp(sc.loc[2019, 'panel_log_anom'] - sc.loc[2016, 'panel_log_anom']) - 1) * 100):.0f}")

# ── 11. Round-2 checks (added after the external audits) ────────────────────────────────────────────────
sys.path.insert(0, str(ROOT))
from src import forecast as Fc  # noqa: E402
# (a) LSTM input windows pair every anomaly with the calendar row of ITS OWN week (alignment bug of the first version)
z_t, C_t = np.arange(12.0), np.c_[np.arange(12.0), np.arange(12.0) * 10]
w_t = Fc.lstm_window(z_t, C_t, 8)
check("LSTM window: anomaly and calendar row belong to the same week", np.array_equal(w_t[:, 0], w_t[:, 1]) and np.array_equal(w_t[:, 2], w_t[:, 0] * 10) and w_t[-1, 0] == 11)
# (b) daily paths: every simulated week averages exactly to its weekly value; band days and monthly means come from the same paths
pools_t = {m_: np.log(np.random.default_rng(m_).uniform(0.5, 1.5, (6, 7))) for m_ in range(1, 13)}
pools_t = {m_: v_ - np.log(np.exp(v_).mean(axis=1, keepdims=True)) for m_, v_ in pools_t.items()}   # mean(exp(offset)) = 1 per vector
wk_t = pd.date_range("2018-12-30", periods=54, freq="W-SUN")[1:]
paths_t = np.log(np.random.default_rng(0).uniform(30, 200, (53, 40)))
dd_t, dv_t = Fc.daily_paths(paths_t, wk_t, pools_t, 2019)
wm_t = pd.DataFrame(dv_t, index=dd_t).groupby(dd_t.to_period("W-SUN")).mean()
inner_ = wm_t.iloc[1:-1].to_numpy()  # weeks fully inside the year
check("daily paths: each simulated week's 7 days average exactly to its weekly path value", np.allclose(inner_, np.exp(paths_t[1:1 + len(inner_)]), rtol=1e-9))
check("daily paths: band days per month sum to days in the month (2019)", np.array_equal(Fc.daily_band_days(dd_t, dv_t).sum(axis=2)[0], [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]))
# (c) backtest MAEs, coverage and the loss-difference table recomputed from the saved forecast file
bf = pd.read_csv(RES / "fc_backtest_forecasts.csv", parse_dates=["date"])
bf["ae"] = (bf.actual - np.exp(bf.mu)).abs()
mae_re = bf.groupby(["model", "fold"]).ae.mean().unstack()
check("fc_backtest_mae.csv equals MAEs recomputed from fc_backtest_forecasts.csv (all models, folds)",
      all(close(mae_re.loc[m_, f_], mae_tab.loc[m_, str(f_)], 0.06) for m_ in mae_tab.index for f_ in (2017, 2018, 2019)))
s_ = bf[(bf.model == "Fourier+ARMA (selected)") & (bf.fold == 2019)]
cov_re = float(((s_.actual >= np.exp(s_.mu - 1.96 * s_.sd)) & (s_.actual <= np.exp(s_.mu + 1.96 * s_.sd))).mean())
check(f"2019 raw coverage {cov_re:.3f} recomputed from saved forecasts = stored {FC['coverage_2019_raw']:.3f}", close(cov_re, FC["coverage_2019_raw"], 1e-9))
ld = pd.read_csv(RES / "fc_loss_diff.csv")
ok_ld = True
for lab_, folds_ in [("folds 2018+2019", [2018, 2019]), ("all three folds", [2017, 2018, 2019])]:
    for m_ in mae_tab.index:
        if m_ == "Climatology":
            continue
        ea = [bf[(bf.model == m_) & (bf.fold == f_)].ae.to_numpy() for f_ in folds_]
        eb = [bf[(bf.model == "Climatology") & (bf.fold == f_)].ae.to_numpy() for f_ in folds_]
        dm_, lo_, hi_ = Fc.block_bootstrap_diff(ea, eb)
        r_ = ld[(ld.folds == lab_) & (ld.model == m_)].iloc[0]
        ok_ld &= close(dm_, r_.mean_MAE_diff_vs_climatology, 0.02) and close(lo_, r_.ci_lo, 0.1) and close(hi_, r_.ci_hi, 0.1)
check("fc_loss_diff.csv reproduced by the per-fold block bootstrap from saved forecasts", ok_ld)
# (d) one-week-ahead MAEs recomputed from the saved one-step forecasts
of = pd.read_csv(RES / "fc_oneweek_forecasts.csv")
of["ae"] = (of.actual - np.exp(of.mu)).abs()
ow_re = of.groupby(["model", "year"]).ae.mean().unstack()
check("fc_oneweek.csv MAEs recomputed from fc_oneweek_forecasts.csv", all(close(ow_re.loc[m_, y_], ow.loc[m_, str(y_)], 0.006) for m_ in ow.index for y_ in (2018, 2019)))
mb_ = of.groupby("model").ae.mean()
check("one-week MAE changes vs no-weather DHR (%): lagged, last-3-days, oracle match the slides",
      all(close(100 * (1 - mb_[k_] / mb_["DHR, no weather"]), v_, 0.06) for k_, v_ in [("+ lagged weather (operational)", FC["oneweek_gain_pct"]["lagged"]), ("+ last 3 days of prior week (operational)", FC["oneweek_gain_pct"]["last3"]), ("+ same-week weather (ORACLE)", FC["oneweek_gain_pct"]["oracle"])]))
# (e) lockdown sensitivity table arithmetic; calibration table; SARIMA D=0 constant table
ls_ = pd.read_csv(RES / "fc_lockdown_sensitivity.csv", index_col=0)
adj_ = 100 * ((1 + ls_.lockdown_gap_10wk_pct / 100) / (1 + ls_.pre_lockdown_gap_pct / 100) - 1)
check("lockdown sensitivity: pre-gap-adjusted gap = (1+gap)/(1+pre-gap)-1 for every counterfactual", close(0, np.nanmax(np.abs(adj_.to_numpy()[:-1] - ls_.lockdown_gap_adjusted_for_pre_gap_pct.to_numpy()[:-1])), 0.15))
check("lockdown headline row of the sensitivity table equals fc_lockdown.csv", close(ls_.iloc[0].lockdown_gap_10wk_pct, lk.gap_median_pct.iloc[0], 0.06))
cal_ = pd.read_csv(RES / "fc_calibration_2019.csv", index_col=0)
check("calibration: coverage up, width up, Winkler up (interval score worse) as stated in the text",
      cal_.coverage.iloc[1] > cal_.coverage.iloc[0] and cal_.width.iloc[1] > cal_.width.iloc[0] and cal_.winkler.iloc[1] > cal_.winkler.iloc[0])
d0_ = pd.read_csv(RES / "fc_sarima_d0_constant.csv", index_col=0)
check("SARIMA D=0 with/without constant table present and both far above climatology in 2018 and 2019", bool((d0_.loc[["no constant", "with constant"], ["2018", "2019"]].min().min() > 1.3 * d0_.loc["Climatology (reference)", ["2018", "2019"]].max())))
sg_ = pd.read_csv(RES / "granger_hac_seasonal.csv")
check("seasonal Granger tests: every winter/monsoon p-value < 0.001 (the report's stated bound)", bool((sg_[~sg_.test.str.startswith("Interaction")].p_value < 1e-3).all()))

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
        "fcMaeSarimaNineteen": f"{FCN['backtest']['sarima_D1_mae']['2019']:.1f}", "fcMaeSarimaSeventeen": f"{FCN['backtest']['sarima_D1_mae']['2017']:.1f}",
        "fcMaeLstmNineteen": f"{FCN['backtest']['lstm_mae']['2019']:.1f}", "fcMaeLstmEighteen": f"{FCN['backtest']['lstm_mae']['2018']:.1f}", "fcMaeSarimaZeroNineteen": f"{FCN['backtest']['sarima_D0_mae']['2019']:.1f}",
        "fcCalWidthRaw": f"{FCN['calibration_2019_all']['Model-based Gaussian']['width']:.0f}", "fcCalWidthCal": f"{FCN['calibration_2019_all']['Calibrated (season scale)']['width']:.0f}",
        "fcCalWinkRaw": f"{FCN['calibration_2019_all']['Model-based Gaussian']['winkler']:.0f}", "fcCalWinkCal": f"{FCN['calibration_2019_all']['Calibrated (season scale)']['winkler']:.0f}",
        "fcCovSeventeen": f"{FCN['backtest']['coverage_selected']['2017'] * 100:.0f}",
        "fcLockPre": f"{abs(FCN['lockdown_sensitivity']['selected spec (linear, K=5, AR1), headline']['pre_lockdown_gap_pct']):.0f}",
        "fcLockAdj": f"{abs(FCN['lockdown_sensitivity']['selected spec (linear, K=5, AR1), headline']['lockdown_gap_adjusted_for_pre_gap_pct']):.0f}",
        "fcLockPlacebo": f"{abs(FCN['lockdown_sensitivity']['PLACEBO: same weeks of 2019 vs 2019 forecast']['lockdown_gap_10wk_pct']):.0f}",
        "fcLockSensLo": f"{min(abs(v['lockdown_gap_10wk_pct']) for k, v in FCN['lockdown_sensitivity'].items() if not k.startswith('PLACEBO')):.0f}",
        "fcLockSensHi": f"{max(abs(v['lockdown_gap_10wk_pct']) for k, v in FCN['lockdown_sensitivity'].items() if not k.startswith('PLACEBO')):.0f}",
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

## slides/beamer/tables/numbers.tex (the macros used in the deck and report)
```latex
\newcommand{\pctPoor}{52}
\newcommand{\winterMean}{213}
\newcommand{\monsoonMean}{48}
\newcommand{\ratioWM}{4.4}
\newcommand{\Fs}{0.90}
\newcommand{\skewRaw}{+1.70}
\newcommand{\skewLog}{$-$0.08}
\newcommand{\sdRatioRaw}{7.9}
\newcommand{\sdRatioLog}{1.3}
\newcommand{\archRaw}{235}
\newcommand{\archLog}{36}
\newcommand{\levPlog}{0.006}
\newcommand{\boxcox}{0.045}
\newcommand{\irfWindA}{6}
\newcommand{\irfWindB}{12}
\newcommand{\irfRhA}{4}
\newcommand{\irfRhB}{7}
\newcommand{\fevdA}{6}
\newcommand{\fevdB}{30}
\newcommand{\lagWindP}{0.46}
\newcommand{\lagRhP}{0.48}
\newcommand{\sameWeekRsq}{0.14}
\newcommand{\shockWindBig}{24}
\newcommand{\shockWindBigZ}{2.3}
\newcommand{\shockWindCalm}{31}
\newcommand{\shockWindCalmZ}{1.8}
\newcommand{\janWind}{14.8}
\newcommand{\janPred}{7.4}
\newcommand{\janShock}{7.4}
\newcommand{\sdNov}{115}
\newcommand{\sdAug}{15}
\newcommand{\fcMaeSelNineteen}{25.7}
\newcommand{\fcMaeClimNineteen}{27.8}
\newcommand{\fcMaeSarimaNineteen}{27.4}
\newcommand{\fcMaeSarimaSeventeen}{53.8}
\newcommand{\fcMaeLstmNineteen}{54.4}
\newcommand{\fcMaeLstmEighteen}{28.3}
\newcommand{\fcMaeSarimaZeroNineteen}{44.1}
\newcommand{\fcCalWidthRaw}{125}
\newcommand{\fcCalWidthCal}{179}
\newcommand{\fcCalWinkRaw}{175}
\newcommand{\fcCalWinkCal}{193}
\newcommand{\fcCovSeventeen}{69}
\newcommand{\fcLockPre}{11}
\newcommand{\fcLockAdj}{35}
\newcommand{\fcLockPlacebo}{15}
\newcommand{\fcLockSensLo}{37}
\newcommand{\fcLockSensHi}{51}
\newcommand{\fcCovRaw}{90}
\newcommand{\fcCovCal}{96}
\newcommand{\fcMaSE}{8.3}
\newcommand{\fcMaCoef}{$-$0.988}
\newcommand{\fcOneLagged}{$-$2.4}
\newcommand{\fcOneLastThree}{+0.7}
\newcommand{\fcOneOracle}{+6.9}
\newcommand{\fcLockPct}{43}
\newcommand{\fcLockLo}{32}
\newcommand{\fcLockHi}{52}
\newcommand{\fcLockWxPct}{38}
\newcommand{\fcValPoorPred}{55}
\newcommand{\fcValPoorAct}{45}
\newcommand{\fcValInside}{12}
\newcommand{\declAll}{25}
\newcommand{\declPanel}{20}
\newcommand{\declWx}{18}
```

## Authors' last run: 78/78 checks passed (offline, local raw files).


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
We study daily \pmtwo{} in Delhi from January 2015 to July 2020 (CPCB monitors; ERA5 wind and humidity). \pmtwo{} has a very strong annual cycle (winter \ratioWM$\times$ the monsoon) and a slow downward drift. After removing the cycle, wind and humidity anomalies \emph{predict} \pmtwo{} for about a week (Granger causality in a VAR, robust to lag order, differencing, HAC errors and rain/temperature controls), but their information is gone at the weekly scale: no added predictive value for next week was detected in the tested specification, and even the same week's weather, unknown in advance, improves a one-week forecast by only \fcOneOracle\%. For 52-week forecasts we compare climatology, Fourier-term regression with ARMA errors, SARIMA, linear regression and a small LSTM on three expanding-window origins. No model is significantly better than climatology (a smooth Fourier+ARMA model is statistically indistinguishable from it); SARIMA with seasonal differencing is fragile, SARIMA with $D=0$ and the small LSTM are clearly worse. We fix several diagnostic and design errors found in an earlier draft (residual burn-in, missing constant, leakage), calibrate prediction interval widths out of sample (at the cost of wider intervals), and produce a monthly 2020 outlook in which the observed lockdown-period PM$_{2.5}$ is about \fcLockPct\% below the model's no-lockdown projection (descriptive, not a causal estimate; see Section on the lockdown).
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
\paragraph{Granger causality.} Joint tests that lags 1--$k$ of wind or humidity add nothing to the \pmtwo{} equation are rejected at every $k=1,\dots,7$ ($p<10^{-9}$). With HAC (Newey-West) errors the 4-lag tests give $p\approx6\times10^{-20}$ (wind) and $4\times10^{-11}$ (humidity); adding rain and temperature controls gives $9\times10^{-18}$ and $7\times10^{-8}$; adding a linear time trend or using a climatology fitted on 2015--2018 only changes nothing. Season-specific tests show both variables are significant in winter and in the monsoon (all $p<10^{-3}$; the largest is winter humidity, $p=5.4\times10^{-4}$); the interactions are weak (monsoon $\times$ humidity $p=0.20$, winter $\times$ wind $p=0.03$), so the EDA impression that humidity matters only in the monsoon is a correlation pattern, not a difference in predictive content. The reverse direction is absent for humidity and weak for wind (lag orders 1 and 2 only, $p=0.04$ and $0.02$). We call this a \emph{predictive association}: mixing height, stubble burning and fireworks are unmeasured, and the ERA5 data are one grid cell.
\begin{figure}[H]\centering\includegraphics[width=0.9\linewidth]{granger_hac.pdf}\caption{HAC Wald tests (4 lags).}\end{figure}
\paragraph{Size and timing.} A one-SD wind shock (2.5 km/h) lowers \pmtwo{} by \irfWindA--\irfWindB\% the next day, a one-SD humidity shock (5.4\% RH) by \irfRhA--\irfRhB\%, fading within about a week; the range reflects the Cholesky ordering (weather first allows same-day effects). The generalised IRF, which does not depend on ordering, gives $-12.0\%$ and $-5.2\%$ on day 1, inside or at the edge of those ranges. Weather shocks explain \fevdA--\fevdB\% of the 14-day forecast-error variance of \pmtwo{} depending on the ordering.
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{irf_range.pdf}\caption{Impulse responses of \pmtwo{} to wind and humidity shocks under both orderings.}\end{figure}
\paragraph{Horizon.} At the weekly scale, last week's wind and humidity add no detectable predictive value to last week's \pmtwo{} for predicting this week's ($\Delta R^2=0.005$, joint HAC Wald $p=0.51$) in the specification we tested. Weather is therefore a short-memory predictor, and the 52-week models use no weather.

\section{Forecasting (Q2)}\label{sec:fc}
\subsection{Models and evaluation design}
All models forecast weekly log \pmtwo{} with no weather inputs: seasonal naive; \textbf{climatology} (mean of each calendar week, benchmark); climatology + AR(1); \textbf{Fourier + ARMA} (dynamic harmonic regression: $K\le5$ yearly sine/cosine pairs, ARMA$(p,q)$ errors with $p\le2,q\le1$, and a level that is constant, linear or a random walk); SARIMA$(1,0,1)(0,1,1)_{52}$ and SARIMA$(1,0,1)(1,0,0)_{52}$ with a constant; Linear Regression on Fourier terms and a linear trend; and a small LSTM (16 units, recursive, seeded; an input-alignment bug in a first version was found by an outside audit and fixed). In the label ``Fourier+ARMA'' the errors are ARMA$(p,q)$ for the constant and linear levels and ARIMA$(p,1,q)$ for the random-walk level (selected in the 2017 and 2019 folds). Optimiser fits that do not converge are rejected. For the Fourier model, $K$ and $(p,q)$ are chosen by AICc within each level type, and the level type by validation on the last training year; this procedure was fixed in the code before the final runs, but the 2019 year had been examined in earlier iterations of the project, so 2019 is not a pristine hold-out. Evaluation uses three expanding-window origins (end of 2016, 2017, 2018), each forecasting the next 52 weeks, refitting and reselecting every time. The 2017 fold (two training years) is a stress test; 2018 and 2019 are the main evidence. Paired error differences to climatology are summarised with a circular moving-block bootstrap (8-week blocks, drawn within each forecast year, so no block crosses two origins); a plain Diebold--Mariano test on 52 weeks of one forecast path is not valid and is not used here.
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{fc_backtest.pdf}\caption{Left: the 2019 forecast of the selected model against climatology and the actual values. Right: MAE by forecast year.}\end{figure}
\subsection{Backtest results}
\begin{table}[H]\centering\footnotesize\input{../slides/beamer/tables/fc_backtest.tex}\caption{52-week-ahead MAE (\ugm{}) by forecast year; last column: bootstrap verdict against climatology over 2018 and 2019.}\end{table}
In 2019 the selected Fourier+ARMA model has an MAE of \fcMaeSelNineteen{} against \fcMaeClimNineteen{} for climatology and \fcMaeSarimaNineteen{} for the seasonal-differenced SARIMA; the SARIMA is, however, at \fcMaeSarimaSeventeen{} in the 2017 fold, where it has only two seasons to learn from. Over 2018--2019 only the seasonal naive forecast, SARIMA with $D=0$ (\fcMaeSarimaZeroNineteen{} in 2019) and the LSTM (\fcMaeLstmEighteen{} in 2018, \fcMaeLstmNineteen{} in 2019) are clearly worse than climatology (the bootstrap interval excludes 0), and SARIMA with $D=1$ is clearly worse over all three origins. For every other model, including the selected Fourier+ARMA model and the linear-trend variant (which has the lowest 2018--19 MAE, 21.9), the bootstrap interval includes 0, so we call them statistically indistinguishable from climatology. The LSTM was rerun after the alignment fix; it remains worse, but it is a small, untuned model and says nothing about neural networks in general. The honest summary: a year ahead the calendar carries almost all of the predictable signal, and with three origins the remaining models cannot be ranked.

\subsection{Diagnostics: errors in the earlier draft}
The draft's Ljung--Box test had $p\approx0$ at every lag. This was an artifact: a state-space SARIMA with $D=1$ initialises its first 52 seasonal states diffusely, so the first 52 in-sample residuals equal the level of the series (about 5 on the log scale). With them excluded (\texttt{loglikelihood\_burn}) the residuals are acceptable at lags 10 and 26 ($p=0.49,\,0.10$) but not at lag 52 ($p=0.016$). The seasonal MA coefficient is \fcMaCoef{} with a standard error far above 1: the parameter sits on the invertibility boundary and is not identified, the usual sign that the seasonal difference is unnecessary. The $D=0$ candidate in the draft had no constant, forcing the forecast toward $\log \text{PM}_{2.5}=0$; the matched comparison (same orders, same folds; notebook~04, \texttt{fc\_sarima\_d0\_constant.csv}) gives MAE 76.9/61.0/92.1 without and 44.9/42.8/44.1 with a constant for 2017/2018/2019, against 31.0/21.8/27.8 for climatology, so the constant matters a lot but D=0 stays clearly worse. The selected Fourier+ARMA model still shows autocorrelation at lags 26 and 52 in the 2019 fold ($p=0.001$ and $0.009$; lag 10 is marginal, $p=0.088$) and ARCH-LM(4) is clean ($p=0.87$): there is more seasonal structure than a few harmonics capture, which we list as a limit.

\subsection{Prediction intervals}
Model-based 95\% intervals covered \fcCovRaw\% of the 2019 weeks (2018: 94\%; the 2017 stress-test fold only \fcCovSeventeen\%); in 2019 all 5 misses were below the lower bound because 2019 was cleaner than 2015--18, so the problem is level bias as much as width. We rescale the predictive standard deviation by season (winter vs other months, shrunk toward the pooled value) using only the 2017 and 2018 errors, and re-centre only if the bias has the same sign and size $>0.5$ standard deviations in both calibration years; it did not (mean standardised errors $-0.66$ and $-0.45$), so only the scale is changed. On 2019 the coverage rises to \fcCovCal\%, but only by widening the intervals (mean width \fcCalWidthRaw{} to \fcCalWidthCal{} \ugm{}) and the Winkler interval score gets \emph{worse} (\fcCalWinkRaw{} to \fcCalWinkCal{}; lower is better): the rescaling buys nominal coverage, not better intervals. The scale factors differ by fold (1.33/1.42 for 2019, 1.09/0.95 for the 2020 forecast), so the calibration is itself uncertain, and with three origins no general reliability claim is possible. A smooth, shrunk shift added afterwards as a sensitivity (defined after seeing 2019, so not a headline) removes the level bias in 2019 (bias from $-8.5$ to $+4.3$, Winkler 161) but we do not adopt it.

\subsection{One week ahead: does weather help?}
Each year 2018 and 2019 is forecast one week at a time with parameters fitted on earlier data. \emph{Lagged weather} (last week's wind and humidity anomalies) changes the error by \fcOneLagged\%, the \emph{last three days} of the previous week by \fcOneLastThree\%, and the \emph{same week's} weather (which is observed, not forecast, and so a hindsight upper bound) by \fcOneOracle\% (Harvey--Leybourne--Newbold $p=0.07$). Weather is explanatory over days, but a poor forecasting input.
\begin{figure}[H]\centering\includegraphics[width=0.7\linewidth]{fc_oneweek.pdf}\caption{One-week-ahead MAE, 2018--19.}\end{figure}

\subsection{The 2020 outlook and its validation}
The final model is fitted on 2015--2019 (selection again inside the window: linear level, $K=5$, AR(1) errors), 5{,}000 weekly paths are simulated, calibrated, converted to daily values by adding a whole within-week offset vector (Monday--Sunday, resampled from a training week of the same month) so that every simulated week still averages exactly to its simulated weekly mean, with monthly means and band-day counts computed from the same daily paths, and classified into the CPCB \pmtwo{} bands. The same pipeline run for 2019 (data to 2018 only) places all \fcValInside{} monthly means inside the 95\% interval, but over-predicts the share of Poor-or-worse days (\fcValPoorPred\% vs \fcValPoorAct\% actual), which is the level bias again. These bands are \pmtwo{} sub-index bands, not the official AQI (the maximum over all pollutants).
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{fc_outlook.pdf}\caption{2020 outlook: monthly mean \pmtwo{} with 95\% interval and expected days per band.}\end{figure}
\begin{table}[H]\centering\scriptsize\input{../slides/beamer/tables/fc_outlook.tex}\caption{2020 outlook (\ugm{}); ``Days Poor+'' = expected days above 90 \ugm{}; Actual shown for full months only.}\end{table}
\subsection{Case study: the 2020 lockdown}
The ten Sunday-ending weeks 29 March--31 May 2020 cover 23 March--31 May (two days before the 25 March start). Observed \pmtwo{} in those weeks was about \fcLockPct\% below the model's no-lockdown median projection (95\% interval \fcLockLo--\fcLockHi\%); with the actual wind and humidity of those weeks given to the model, the gap is \fcLockWxPct\%. This is a descriptive comparison with a model projection, not a causal estimate: the model was already about \fcLockPre\% too high in the twelve weeks before the lockdown, and adjusting for that gives about \fcLockAdj\%; other level specifications give \fcLockSensLo--\fcLockSensHi\%; and the same calendar weeks of 2019 against the 2019 pipeline show a gap of \fcLockPlacebo\% (95\% interval spanning zero). The reduction is large and robust in sign, but its size is uncertain (roughly one-third to one-half).
\begin{figure}[H]\centering\includegraphics[width=0.85\linewidth]{fc_lockdown.pdf}\caption{Actual weekly \pmtwo{} in 2020 against the no-lockdown forecast and a weather-adjusted forecast.}\end{figure}

\section{Review of the project and what changed}\label{sec:review}
Three independent reviews proposed about 30 changes. We accepted the confirmed errors (diagnostic burn-in, missing constant, leakage in headline statistics, wording that over-stated causality or p-values, the PM$_{2.5}$-band versus AQI distinction, an invalid DM test) and rejected others after testing them (for example, the claim that re-anchoring the level gives 94\% coverage gives 90\% in the data; the shock-bin statistic has no Jensen bias; humidity's effect is not detectably monsoon-specific). The full log, with evidence for each claim, is \texttt{docs/REVIEW\_RESPONSES.md}.

\section{Limitations}
(i) Granger causality is predictive; boundary-layer height, stubble burning and fireworks are unmeasured, and ERA5 is a single grid cell. (ii) Three backtest origins give few independent tests; no model is significantly better than climatology, and the 2019 year was examined in earlier iterations (not a pristine hold-out). (iii) A level bias remains: 2019 was cleaner than the training years, and the calibrated intervals depend on the fold. (iv) The Fourier model leaves some autocorrelation at lags 26 and 52. (v) One city; the data end in July 2020 and the monitoring network changed during the sample; the fixed-station check uses six stations, so the decline is consistent with a genuine decline but a network effect is not fully excluded. (vi) The bands are \pmtwo{} sub-index bands, not the official AQI. (vii) The LSTM is deliberately small and is not tuned: it is a small-data baseline, not a statement about deep learning in general. (viii) The automated checker re-derives selected numbers; it does not re-run every model selection or the station download.

\section{Conclusion}
Delhi's \pmtwo{} is overwhelmingly a calendar phenomenon with a slowly falling level. Wind and humidity anomalies help for about a week, not for a year. For 52-week forecasts a smooth Fourier+ARMA model is statistically indistinguishable from climatology and more robust than SARIMA with seasonal differencing; its interval widths can be adjusted out of sample at the price of wider intervals. Against its no-lockdown projection, observed 2020 lockdown-period PM$_{2.5}$ is much lower, though the size of the gap depends on the projected level. The most valuable parts of the work are the honest accounting of what is and is not significant and the correction of diagnostic errors that would have led to wrong model choices.

\section*{Reproducibility}
\texttt{pip install -r requirements.txt}; download the CPCB files (Section~2) and run notebooks 01--04; then \texttt{make\_figures.py}, then \texttt{verify\_numbers.py} (both in \texttt{slides/beamer/}; automated re-derivation of selected numbers on the slides and in the tables) and build \texttt{main.tex} and this report with \texttt{tectonic}. Code: \texttt{src/} (data, tsa, forecast, aqi, plots).
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
    \node[sbox=pblue] (q1) at (6.0,3.6) {\textbf{Q1. Explain.} Does weather predict \pmtwo{}?\\ Daily VAR + Granger causality};
    \node[sbox=graytxt] (q2a) at (6.0,2.0) {\textbf{Q2a. Next week.} Does weather improve a 1-week forecast?};
    \node[sbox=graytxt] (q2b) at (6.0,0.4) {\textbf{Q2b. Next 12 months.} Fourier+ARMA vs SARIMA and baselines, no weather inputs};
    \node[sres=pgreen] (r1) at (12.3,3.6) {\textbf{Done:} wind and humidity Granger-cause \pmtwo{}; effects fade within about a week};
    \node[sres=pgreen] (r2) at (12.3,2.0) {\textbf{Done:} last week's weather adds no detectable value; same-week weather (unknowable in advance) helps only \fcOneOracle\%};
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
    Weekly: \emph{last} week's weather adds no detectable value to last week's \pmtwo{} for predicting this week's ($p=\lagWindP$ wind, \lagRhP\ humidity).
  \end{takeaway}
\end{frame}

% ───────────────────────── 13. What we established ─────────────────────────
\begin{frame}{What We Have Established So Far}
  \begin{itemize}\footnotesize\setlength\itemsep{3pt}
    \item \textbf{Seasonality:} a strong yearly cycle ($F_S=\Fs$; winter \ratioWM$\times$ the monsoon), so the forecasting model must be seasonal ($s=52$ weeks).
    \item \textbf{Transformation:} the log stabilises the variance (monthly spread \sdRatioRaw$\times\to$\sdRatioLog$\times$, skewness \skewRaw\ $\to$ \skewLog); log \pmtwo{} is consistent with stationarity ($d=0$), with a slow downward level drift.
    \item \textbf{Causality:} wind and humidity \textbf{Granger-cause} \pmtwo{} (robust to lag choice, differencing, robust errors, rain and temperature controls); the reverse is absent for humidity and weak for wind.
    \item \textbf{Size and timing:} a one-SD shock lowers \pmtwo{} by \irfWindA--\irfWindB\% (wind) and \irfRhA--\irfRhB\% (humidity) the next day, fading within about a week.
    \item \textbf{Horizon:} last week's weather adds no detectable value for predicting this week's \pmtwo{} ($p\approx0.5$, tested specification), so weather is a short-memory predictor and the 12-month model should not rely on it.
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
    \textbf{Headline procedure:} Fourier+ARMA (ARMA or ARIMA errors), selection inside each window; fixed in the code before the final runs, though 2019 had been examined in earlier iterations.
  \end{takeaway}
\end{frame}

\begin{frame}{52-Week Backtest: Climatology Is Hard to Beat}
  \centering
  \includegraphics[width=0.86\linewidth]{fig/fc_backtest.pdf}\\[3pt]
  \begin{takeaway}
    MAE in \ugm{}; 2019: selected \fcMaeSelNineteen\ vs climatology \fcMaeClimNineteen, SARIMA $D=1$ \fcMaeSarimaNineteen\ (but \fcMaeSarimaSeventeen\ in 2017). A year ahead, the calendar is most of the signal: a smooth Fourier model is indistinguishable from climatology, while SARIMA $D=0$ (\fcMaeSarimaZeroNineteen) and the small LSTM (\fcMaeLstmEighteen\ in 2018, \fcMaeLstmNineteen\ in 2019) are clearly worse.
  \end{takeaway}
\end{frame}

\begin{frame}{Backtest Table: Which Models Beat Climatology?}
  \centering\footnotesize
  \input{tables/fc_backtest.tex}\par\vspace{6pt}
  \begin{takeaway}
    MAE in \ugm{} (lower is better). The last column is a circular moving-block bootstrap (within each year) of the paired error differences to climatology over 2018--19: the seasonal naive, SARIMA $D=0$ and the small LSTM are \emph{clearly worse}; every other model, including the linear-trend variant with the lowest MAE, is \emph{indistinguishable} from climatology. With three origins we cannot rank them.
  \end{takeaway}
\end{frame}

\begin{frame}{Diagnostics and Intervals: Two Pitfalls Fixed}
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \begin{card}[title={Residual checks}]{pblue}\footnotesize
      \begin{itemize}\setlength\itemsep{3pt}
        \item The draft's Ljung-Box $p\approx0$ was an \textbf{artifact} (52 diffuse-initialisation residuals); removed, SARIMA passes at lags 10 and 26.
        \item The seasonal MA ($\fcMaCoef$, SE $>1$) is not identified: the seasonal difference is not needed.
        \item Limit: the Fourier model keeps some autocorrelation at lags 26, 52.
      \end{itemize}
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={Prediction intervals (95\%)}]{porange}\footnotesize
      \begin{itemize}\setlength\itemsep{3pt}
        \item Model-based intervals covered \fcCovRaw\% of 2019 weeks (2017 stress fold: \fcCovSeventeen\%). All 2019 misses were on the low side (2019 was cleaner than 2015--18).
        \item Seasonal scaling from 2017--18 errors gives \fcCovCal\% coverage on 2019, but width grows \fcCalWidthRaw$\to$\fcCalWidthCal\ \ugm{} and the Winkler score worsens (\fcCalWinkRaw$\to$\fcCalWinkCal): coverage, not sharper intervals.
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
    Fitted on 2015--2019 only. \textbf{Validation of the same pipeline on 2019:} all \fcValInside\ monthly means fell inside the 95\% interval, but the model over-predicted the share of Poor-or-worse days (\fcValPoorPred\% vs \fcValPoorAct\% actual), the same level bias as before. In 2020, Jan--Feb fall inside the interval; March--June fall below it (lockdown and the weeks after). Bands are \pmtwo{} sub-index bands, not the official AQI.
  \end{takeaway}
\end{frame}

\begin{frame}{Case Study: The 2020 Lockdown}
  \centering
  \includegraphics[width=0.88\linewidth]{fig/fc_lockdown.pdf}\\[2pt]
  \begin{takeaway}
    Over the 10 weeks ending 29 Mar--31 May (covering 23 Mar--31 May), observed \pmtwo{} was about \textbf{\fcLockPct\%} below the model's no-lockdown projection (95\% interval \fcLockLo--\fcLockHi\%); \fcLockWxPct\% with the actual weather. \emph{Not causal:} the model was already \fcLockPre\% high before the lockdown (adjusted gap \fcLockAdj\%), other level specs give \fcLockSensLo--\fcLockSensHi\%, and a 2019 placebo gives \fcLockPlacebo\% (interval spans 0).
  \end{takeaway}
\end{frame}

\begin{frame}{What We Established, and the Limits}
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \begin{card}[title={Established}]{pgreen}\scriptsize
      \begin{itemize}\setlength\itemsep{2pt}
        \item Strong yearly cycle (winter \ratioWM$\times$ the monsoon); log stabilises variance.
        \item Wind and humidity anomalies robustly \emph{predict} PM$_{2.5}$ for about a week; effect \irfWindA--\irfWindB\% (wind), \irfRhA--\irfRhB\% (humidity) the next day.
        \item Beyond a week no usable weather value was detected; Fourier+ARMA is indistinguishable from climatology; SARIMA $D=0$ and the small LSTM are worse.
        \item The 2016--19 decline looks genuine (about $-$\declPanel\% on a fixed 6-station panel); a network effect is not fully excluded.
        \item Lockdown-period PM$_{2.5}$ was about \fcLockPct\% below the model's no-lockdown projection (\fcLockSensLo--\fcLockSensHi\% across specs; descriptive).
      \end{itemize}
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={Limits}]{porange}\scriptsize
      \begin{itemize}\setlength\itemsep{2pt}
        \item Granger = predictive; mixing height, stubble burning, fireworks are unmeasured.
        \item Weather's share of 14-day error depends on the VAR ordering (\fevdA--\fevdB\%).
        \item Three origins: no model significantly beats climatology; 2019 was seen earlier.
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
76e359e Add verification pack (recompute data, code, results, claims ledger) for external audit
3397b23 Deck, report, review-response log, README, presentation script, LLM briefs, verification (65 checks)
9b351f9 Notebook 04: rolling-origin backtest, diagnostics, calibration, 1-week weather test, 2020 outlook, lockdown case study; archive SARIMA draft
2a3d6bc Notebooks 02-03: training-only headline stats, level-drift and station check, extra Granger robustness (temp, trend, seasonal, by-lag), GIRF, nested weekly test; re-executed
d671a29 src: leap-safe climatology, week index, forecasting toolkit, PM2.5-band labelling; pin requirements
982b5ab Baseline: hygiene (.gitignore, untrack pycache) and existing phase 2-3 rework, beamer deck, SARIMA draft, review inputs
```

## Review responses (every claim from five reviews, with verdict, evidence, fix; Round 2 at the end)
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

1. The headline Fourier+ARMA procedure is **not** significantly better than climatology (2018-19 MAE 24.6 vs 24.8); neither is the linear-trend variant (21.9, interval -6.1 to +0.7), so nothing beats climatology (Round 2, R12).
2. In the 2-year-training fold (2017) SARIMA D=1 collapses (MAE 54 vs 31 for climatology): another reason to avoid unnecessary seasonal differencing.
3. The calibrated 2020 forecast intervals are *narrower* than those for 2019 (scale factors 1.09/0.95 vs 1.33/1.42): the calibration is fold-dependent, which we report instead of hiding; calibration also widens intervals and worsens the Winkler score.
4. The observed March-June 2020 monthly means fall below the 95% interval; lockdown-period PM2.5 was about 43% below the model's no-lockdown median (35-51% across adjustments; a 2019 placebo gives 15%): descriptive, not causal.
5. The pipeline over-predicts the share of Poor-or-worse days in 2019 (55% vs 45%): the level bias noted above carries into the band table.

## Round 2: outside verification audits of the finished project (Gemini and GPT)
Both audits (`docs/reviews/round2/`) received `verification_pack/` and recomputed the headline numbers. Every number they recomputed matched. They also reported code bugs, checker defects and over-claims, each re-tested against the code and data before acting. Gemini's statement that it ran `verify_numbers.py` (63/65) could not have been done from the pack, which did not contain the raw data, so it is not relied on.

| # | Claim (source) | Verdict | Evidence and fix |
|---|---|---|---|
| R1 | LSTM recursive input pairs each anomaly with the calendar row of the *next* week (GPT) | **Accepted, confirmed** | `forecast.py` built the window as `Cp[j+1:] + Cf[:j+1]`. Now one helper (`lstm_window`) builds training and forecast windows, with a unit test. Rerun: MAE 36.3 / 28.3 / 54.3 (was 36.3 / 49.2 / 52.9): 2018 improves, still clearly worse than climatology over 2018-19. |
| R2 | verify_numbers checks April-June against March-May intervals (GPT) | **Accepted, confirmed** | `month == i_ + 1`. Fixed; each month now compared with its own interval and June added. Conclusion unchanged (Mar-Jun all below). |
| R3 | Persistence check skips the first test week (GPT) | **Accepted** | `.iloc[1:]` removed, tolerance 0.6 -> 0.01. |
| R4 | Link checks fail offline (Gemini) | **Accepted** | HTTP 000 is reported as offline and the local raw files are checked instead. |
| R5 | Report: seasonal Granger "p <= 5e-4"; winter humidity is 5.35e-4 (GPT) | **Accepted** | Report now says all p < 1e-3; a verify check enforces it. |
| R6 | Report: D=0 MAE "39.7 -> 30.6" with a constant has no saved evidence (GPT) | **Accepted** | Came from a planning run, not a saved result. Replaced by a matched table (`fc_sarima_d0_constant.csv`): without constant 76.9 / 61.0 / 92.1, with 44.9 / 42.8 / 44.1, climatology 31.0 / 21.8 / 27.8. |
| R7 | June 2020 omitted (GPT) | **Accepted** | June actual 46.7 < lower bound 48.7. Deck and report now say March-June; verify check extended. |
| R8 | Calibration raises coverage but widens intervals and worsens the Winkler score (GPT) | **Accepted** | Width 125 -> 179, Winkler 175 -> 193; now stated everywhere; "calibrated" reworded to "interval widths rescaled". 2017 coverage 69% is also reported. |
| R9 | "ARMA" label although the rw level is ARIMA(p,1,q) (GPT) | **Accepted** | Wording changed in definitions (label kept). |
| R10 | `_best_by_aicc` accepts non-converged fits; warnings suppressed globally (GPT) | **Accepted** | Fits with `converged = False` are rejected and counted (6 / 3 / 5 per origin); warnings now suppressed only inside the fit call. Selected specs unchanged. |
| R11 | Monthly means and band-day counts come from different draws (GPT) | **Accepted** | `daily_paths` draws a whole Mon-Sun offset vector per simulated week (mean(exp(offset)) = 1), so every week averages exactly to its simulated weekly mean; both outputs derive from the same daily paths. 2019 validation: 12/12 months inside; Poor+ 55.1% predicted vs 45.2% actual (unchanged story). |
| R12 | Block bootstrap joins forecast years (Gemini, GPT) | **Accepted; found a second bug** | Blocks are now drawn within each fold. My first version (non-circular) under-sampled the first and last weeks and gave biased intervals (it declared the linear variant and the selected model "better"); the final version is circular. Result: **no model beats climatology significantly**; the linear variant (-2.9, CI -6.1 to +0.7) is indistinguishable. Seasonal naive, SARIMA D=0 and the LSTM are clearly worse; SARIMA D=1 is worse over all three folds. |
| R13 | Constant predictive sd for linear regression and LSTM (Gemini) | **Accepted** | Linear regression: OLS prediction sd with parameter uncertainty. LSTM: sd from in-sample recursive h-step errors (non-decreasing, capped). Climatology and seasonal naive now carry an sd, so RMSE uses the mean forecast for every model. |
| R14 | Calibration threshold ignores consistent negative bias (Gemini) | **Partly** | The step rule was fixed before 2019 was seen; replacing it afterwards would tune on the test year. Added as a labelled post-hoc sensitivity: a shrunk shift gives 2019 bias +4.3, MAE 23.6, Winkler 161, but is not adopted. |
| R15 | Lockdown gap confounded by model level bias; window starts 23 Mar (both) | **Accepted** | The model was already 11% high in the 12 weeks before the lockdown. New sensitivity table: adjusted gap -35%; constant level -51%; random-walk -43%; 9-week window -42%; post-hoc shift -37%; 2019 placebo -15% (interval spans 0). Wording now "observed PM2.5 was about 43% below the model's no-lockdown median", range 37-51%, not causal. |
| R16 | Over-claims: "matches or slightly beats", "weather adds nothing", "decline is real", "cut PM2.5 by 43%", "65 checks verify every number", "pre-declared / untouched 2019", "LSTM clearly worse" (both) | **Accepted** | Reworded across deck, report, script and README; 2019 described as examined in earlier iterations. |
| R17 | Bootstrap and tests rest on only three origins (both) | **Accepted** | Stated in limitations; no stronger claim made. |
| R18 | Report omits lag-10 Ljung-Box p = 0.088 (Gemini) | **Accepted** | Added. |
| R19 | 52-week fold naming and week-53 cap (GPT) | **Accepted** | Notebook text: the 2017 fold ends 24 Dec 2017; week 53 is folded into 52; seasonal naive is 52 weeks back. |
| R20 | `verify_numbers.py` is not comprehensive (both) | **Accepted** | Described as selected checks. New checks: LSTM alignment, daily-path coherence, saved-forecast recomputation of all MAEs, bootstrap table, one-step MAEs, lockdown sensitivity arithmetic, calibration direction, D=0 table, Granger bound. |
| R21 | Fixed 6-station panel does not prove the decline is real (GPT) | **Accepted** | Wording: "consistent with a genuine decline; network effect not fully excluded". |
| R22 | Gemini: Granger "drive/explain" wording | **Accepted** | "Predictive association" throughout; deck question changed to "Does weather predict PM2.5?". |
| R23 | Gemini: LSTM strawman | **Partly** | It is a small untuned baseline, stated as such; no claim about neural networks. |

## Round 2 audit documents
### GPT
# Independent verification audit — Delhi PM2.5 (`phase4-final`)

Scope: `00_VERIFY_README.md` and supplied files 01–09. Recomputed from the **rounded** weekly data (287 records) and raw backtest predictions (1,560 records) in `06_raw_data_for_recompute.md`. Source-line pointers refer to the supplied Markdown files. No original daily CPCB/ERA5 files, station-level CSVs, actual `numbers.tex`, or simulation-path records were supplied. Consequently, statements dependent on these assets are **internally checked, not independently reproduced**. This audit does not claim to have run `verify_numbers.py` end-to-end.

## I. Ledger of 15 claims

| Ledger | Independent finding | Status |
|---|---|---|
| 1. Forecast MAE for 2017/18/19 | Independently recomputed all ten models, all three folds. Selected model 31.483/23.426/25.695; climatology 30.998/21.774/27.818; SARIMA D=1 53.827/21.083/27.452; D=0 44.874/42.834/44.103; LSTM 36.291/49.231/52.869. | **PASS** (stored forecast rows) |
| 2. Calendar-week climatology | Rebuilt group means of log weekly PM2.5 using the training years and `week_index`. Stored predictions agree to <0.00008 log units, explained by input rounding. | **PASS** |
| 3. Seasonal naive | Stored median forecasts match the observed PM2.5 52 weeks earlier exactly, across all three folds. | **PASS** |
| 4. Moving-block CI | Re-ran RNG seed=0, block length 8, 4,000 replications. Selected minus climatology (2018–19) mean difference −0.235 µg/m³, CI [−3.558,+1.806]; Fourier linear −2.942, CI [−6.430,−0.357]. | **PASS arithmetic**, inferential caveat (few origins) |
| 5. Raw/calibrated intervals | Raw selected 2019: 47/52 =90.3846%. Applying stored seasonal scale factors 1.33430955 winter, 1.42153240 non-winter: 50/52 =96.1538%. | **PASS**, calibration score worsens |
| 6. Misses by year | 2017: 10 below/6 above, 36/52=69.23%; 2018: 2 below/1 above, 49/52=94.23%; 2019: 5 below/0 above, 47/52=90.38%. | **PASS** |
| 7. One-week weather | From `05` table: no weather 22.39; lagged 22.92 (−2.4% gain), prior-last-3-days 22.24 (+0.7%), same-week oracle 20.84 (+6.9%); DM/HLN approx 0.074. Raw one-step forecasts are **not** supplied in `06`, so cannot independently recompute its errors or p-value. | **Consistent, unverified from raw** |
| 8. Daily Granger | Report values match `05` tables (base HAC p roughly 6e−20 and 4e−11; with rain/temp roughly 9e−18 and 7e−8). Full daily anomaly inputs absent; exact p-values not independently re-estimated. | **Table-consistent, not independently reproduced** |
| 9. Weekly nested weather | Independently implemented the lag-1 nested regression on supplied weekly data. R² base 0.13408324, full 0.13908401, ΔR²=0.00500077, joint HAC Wald p=0.5146397. | **PASS** |
| 10. 2019 monthly pipeline | `05` reports 12/12 monthly means inside 95% and Poor+ 55.0% predicted vs 45.2% actual. Weekly raw file cannot reconstruct daily observed counts, stochastic daily profiles, or Monte Carlo draws. | **Unverifiable from raw pack** |
| 11. Lockdown contrast | Ten weeks 29 Mar–31 May 2020: actual mean 48.66972 (from `06`) vs reported model counterfactual median 85.14075 (`05`), (actual/median−1)=−42.836%; weather-adjusted median 78.46681, −37.974%. Counterfactual simulation distribution and interval **not supplied**. | **Percent arithmetic PASS; causal meaning NOT established** |
| 12. Station-panel decline | Reported log-anomaly changes imply exp(−0.163−0.121)−1=−24.72%; fixed panel exp(−0.132−0.088)−1=−19.75%; weather-adjusted exp(−0.110−0.085)−1=−17.72%. **Required raw station_day.csv absent**: cannot verify 6-station panel or composition claims. | **Arithmetic PASS; underlying evidence unavailable** |
| 13. SARIMA diffuse burn-in | `04` reports drop initial 52 residuals, Ljung–Box p=.49 (lag10), .10 (lag26), .016 (lag52). Without original full-precision series cannot independently refit identical parameters. | **Code/output-consistent** |
| 14. Seasonal MA −.988, SE 8.26 | Reported in notebook and `05`; cannot refit exactly. Very high SE signals weak identification, rather than quantitatively proving over-differencing. | **Code/output-consistent** |
| 15. Leap-year `doy365` | Code maps Feb29 to Feb28 index, subtracts 1 from Mar1–Dec31 during leap years, giving 365-day seasonal alignment. | **PASS**, residual 53-week-compression caveat |

## II. Independently recalculated MAE (µg/m³)

| Model | 2017 | 2018 | 2019 |
|---|---:|---:|---:|
| Fourier+ARMA selected |31.483|23.426|25.695|
| Climatology |30.998|21.774|27.818|
| SARIMA D1 |53.827|21.083|27.452|
| SARIMA D0 |44.874|42.834|44.103|
| Fourier+ARMA linear |35.856|19.733|23.974|
| Climatology+AR1 |30.701|21.668|27.327|
| Fourier+ARMA const |30.593|22.048|29.262|
| Linear regression |35.893|19.991|24.944|
| LSTM |36.291|49.231|52.869|
| Seasonal naive |38.438|28.965|30.306|

Computed 287 equally spaced weekly observations (2015-01-04–2020-06-28). Weekly ln(PM2.5) differs from supplied rounded log column by no more than 0.00005.

## III. Report/deck vs tables — specific mismatches or unsupported numbers

1. **Seasonal Granger p-value overstatement** — `08_report_and_deck_text.md`, report Granger paragraph, ~line 46: claims both wind and humidity significant in winter and monsoon at *p* ≤ 5×10^-4. `05_all_results_tables.md`, `granger_hac_seasonal.csv`, winter humidity **p=0.00053516**, which is slightly GREATER than 0.0005. Change to `p < 0.001` or quote exact maximum.
2. **Missing-constant D0 MAE 39.7→30.6 unsupported** — `08` report ~line 61 says introducing constant improves validation MAE from 39.7 to 30.6; current `05` table `fc_backtest_mae.csv` lists D0 MAEs **44.9, 42.8, 44.1**, and the value 30.6 belongs to `Fourier+ARMA const`, 2017. These may refer to distinct draft configurations/horizons; without a saved matched-pair output, the exact 30.6 improvement is **not supported by current results**, and attribution solely to constant is unwarranted.
3. **2020 month omission** — Deck ~line 459 says January–February inside, March–May below interval. `05`, `fc_outlook_2020.csv` also shows **June** actual 46.695 below lower 48.702, and June is a full observed month. Include June or explain why excluded. Related plotted title “Jan–May full months” is inaccurate.
4. **Calibration is presented as improvement while interval quality worsens** — `05`, `fc_calibration_2019.csv`: raw 90.4% to calibrated 96.2% coverage, but average interval width **125.08→178.66** (+42.8%) and mean Winkler score **174.88→192.72** (+10.2%; lower is better). Code correct for coverage but the evidence does not show uniformly *better* predictive intervals.
5. **Title/model-class mismatch** — `08` calls the selected model Fourier+ARMA. `02_src_code.md`, `TREND_SPECS['rw']`, specifies **ARIMA(p,1,q) errors** for selected 2017 and 2019 folds. More accurate: Fourier regression with ARIMA errors, or DHR with candidate ARMA/ARIMA error structures.
6. **Unverifiable ‘predetermined’ claim** — `08` ~line 54 and deck ~line403 claim the headline rule was decided before test years were inspected. The prior project material already included 2019 results and iterative model development. Current code can be internally chronological while the **research process** reuses 2019 as a model development reference. Do not describe 2019 as a pristine untouched prospective holdout.
7. **Numerical statements otherwise agree** — headline MAEs, 2017–2019 interval miss counts, calibration coverage, bootstrapped loss differences, weekly ΔR² and p=.51, one-week MAE improvements *as tabulated*, forecast-day shares *as tabulated*, station-change percentages *as tabulated*, IRF and FEVD summaries *as tabulated*, and lockdown gap arithmetic match to published rounding. This is a comparison of the provided LaTeX and `05` tables, **not** a check of actual `numbers.tex` macro contents; the macro file was not included.

## IV. Confirmed code defects and verification blind spots

**P0: Recursive LSTM feature alignment** — `02_src_code.md`, `src/forecast.py`, line ~456: `cc = np.vstack([Cp, Cf[:j + 1]])[-lag:] if j else Cp` but input anomaly history `hist[-lag:]` stops at previous week. For j≥1, `cc` contains next/current week's calendar vector, one step ahead of the corresponding anomaly input. Correct to `Cf[:j]` and rerun LSTM baseline. The existing backtest MAE computed from *saved predictions* is correct, but the training/forecast implementation is wrong; do not draw general conclusions about LSTM performance from uncorrected runs. Independent refit of the code on rounded weekly data was unstable/did not reproduce stored LSTM metrics (especially 2018 and 2019), so include a complete locked environment and raw unrounded inputs for reproducibility.

**P0: Independent verifier off by one month** — `07_verification_and_figure_code.md`, `verify_numbers.py`, ~line 327: `for i_,m_ in zip((3,4,5), ['Mar','Apr','May'])` then selects `a20_.index.month==i_+1`. This checks April, May, June observed concentrations against March, April, May intervals. Fix to `index.month==i_`. A PASS from this code cannot validate the intended claim.

**P1: Persistence checker drops first week** — `07`, ~line 314: `.iloc[1:]` is applied to both actual and previous-week reference even though previous-week observations are available. It skips one complete test week. The computed persistence MAE changes, but generous tolerance currently masks the error. Check every available weekly forecast and eliminate the tolerance masking.

**P1: Non-converged model selection** — `02`, `_best_by_aicc` ~line 340 accepts any finite AICc without testing optimizer convergence. Global warning suppression hides warnings. Check `res.mle_retvals['converged']`, covariance warnings and invalid seasonal/invertibility parameters and document excluded candidates.

**P1: Incoherent daily simulations vs weekly forecasts** — `02`, `daily_band_days` ~lines 583–619 constructs daily exceedance counts from separately sampled patterns, while monthly PM2.5 means are generated from a separate weekly trajectory (`monthly_mean_paths`). Their daily profiles are not constrained to exactly reproduce that same simulation's weekly means. A single coherent daily-to-weekly simulation should produce both monthly mean and counts. The 2019 daily band validation needs raw daily data/simulation paths to independently verify.

**P1: 'Independent' verification is not comprehensive** — `07`, `verify_numbers.py` depends on original raw CPCB/ERA5, processed files, station files, and generated macro files not provided in this bundle; therefore its 65/65 claim cannot be independently rerun from this upload alone. Some checks compare saved result tables or selected model specifications rather than recomputing model selection or full uncertainty procedure. It does not fully certify weather one-step, LSTM refits, station panel, outlook simulation or every report/deck number.

**P1: Block bootstrap effective sample size** — `02`, `block_bootstrap_diff` resamples concatenated weekly loss differences across yearly origin boundaries, assuming weak stationarity. The 104 2018+19 weekly errors represent only two highly dependent forecast paths. Its percentiles reproduce as coded, but inferential significance is fragile.

**P2: Horizon/calendar naming** — A 52-step weekly forecast from 2016-12-25 ends 2017-12-24, not on 2017-12-31. This is legitimate for a fixed 52-week horizon but should not be confused with a full calendar-year forecast. `week_index` caps week 53 at 52; the baseline still matched observed stored forecasts here. Annual calendar reporting must address 53-week years explicitly. Full 2019/2020 monthly outlooks use 53 projected weeks to cover all days, which is the appropriate distinct design.

**Leakage conclusion**: Model selection in `select_dhr` and seasonal calibration uses data restricted to each backtest origin according to the supplied code. The apparent “same-week ERA5” model is explicitly marked oracle and is not used for operational forecasts. I found **no certain direct look-ahead in the main 52-week selected-model backtest**; the serious issues are (a) test-year reuse during iterative model development, (b) LSTM time-feature misalignment, and (c) uncertainty/verification design. Do not call every retrospective climatology or contemporaneous weather analysis “leakage”.

## V. Interpretative overclaims

- **“Weather adds nothing”** is stronger than a non-significant p=.515 and modest test-set accuracy changes. Better: no convincing *additional predictive benefit detected* in tested weekly specifications. In-sample Granger predictability does not establish physical causal ‘driving’.
- **“Fourier+ARMA beats climatology”** only weakly: MAE 2018–19 average selected 24.56 vs climatology 24.80; block CI includes zero. The 2017 fold slightly favors climatology. The linear trend variant is apparently stronger on 2018–19, but selecting it after reviewing test results would require new evaluation.
- **“Calibration works”** because 2019 coverage 96% omits the increase in interval width and worsening Winkler score; 2017 coverage is just 69%. No reliability guarantee over future years from three forecast origins.
- **“Lockdown cut PM2.5 by 43%”** is an unjustified causal statement. This is a comparison to a projected counterfactual (median 85.14 vs observed 48.67). Forecast model was already high by ~8.5% relative to observed January–March pre-lockdown weeks, using available weekly 2020 records. The 10 Sunday weeks cover 23 Mar–31 May, including 23–24 Mar before 25 Mar lockdown. Weather adjustment does not resolve all competing confounders. Write “observed mean was approximately 43% below the model’s no-lockdown median projection over the 10 selected weeks.”
- **“Most monitoring decline is real”** is not proven by a six-station fixed panel with differing year coverage; raw station file absent and weather covariates do not establish emissions causality.
- **“LSTM clearly worse”** as a conclusion about a fairly evaluated baseline must wait for its recursive alignment fix and a reproducible rerun. It is not evidence that deep learning generally underperforms.
- **“Monthly risk bands”** refer to PM2.5 sub-indices rather than full CPCB AQI, an appropriate distinction the revised report largely makes. Daily category probabilities derived from weekly means need a single coherent daily simulation and daily data for checking.

## VI. Priority fixes

1. Fix LSTM time-feature alignment, rerun all LSTM folds and store full-precision reproducibility inputs, seeds, PyTorch/version and outputs.
2. Fix verifier’s month off-by-one and persistence skipped-week bugs; add true raw-output recomputation checks for all 15 ledger items, including one-week forecasts, station panel and simulated monthly outlook.
3. Remove/correct report's winter-humidity p cutoff and unsubstantiated D0 validation “39.7→30.6” assertion; amend June 2020 omission.
4. Show coverage, interval width **and Winkler score** together; avoid calling wider intervals uniformly “calibrated improvement.”
5. Rebuild coherent daily trajectories whose weekly means match forecast draws; validate monthly risk-band counts from the actual historical daily series.
6. Change causal lockdown language to explicit model-based counterfactual and clearly state 10 selected weeks begin 23 March.
7. Temper significance and model-selection claims given only two main 52-step origins and reuse of the 2019 holdout; accurately label integrated DHR errors.

Source: files 00–09 uploaded for this audit. Calculated supporting CSV: `audit_recomputed_metrics.csv`.

### Gemini
# Gemini verification audit (round 2), condensed transcription

Source: pasted by the user from Gemini's reply to `verification_pack/`. Numeric tables omitted where they only confirm values already in `results/`.

**Claimed run results (not reproducible from the pack: raw CPCB/ERA5/station files were not included, so these cannot have come from the supplied files alone):** verify_numbers.py 63/65 (the two failures were live link checks); make_figures.py exit 0.

**Reproduced from the raw pack (all matched):** backtest MAEs (all models, 3 folds), climatology and seasonal naive, interval coverage and miss counts (2017 69.2% 10 below/6 above; 2018 94.2% 2/1; 2019 90.4% 5/0; calibrated 96.2%), bootstrap loss differences, one-week MAE changes, HAC Granger p-values, weekly nested test (R2 0.1341 to 0.1391, p = 0.5146), 2019 pipeline validation, lockdown arithmetic (48.67 vs 85.14 = -42.8%; weather-adjusted -38.0%), station-decline arithmetic, Ljung-Box with/without burn-in, seasonal MA -0.988 SE 8.26, doy365.

**Mismatches / discrepancies reported:**
1. verify_numbers.py makes live curl calls; fails offline.
2. Some macros rounded to integers (MAE 54, LSTM 53, D0 44; lockdown bounds).
3. Ledger said lockdown "25 Mar - 31 May"; the series uses 10 Sunday-ending weeks 29 Mar - 31 May.
4. Report Section 5.3 omits that lag 10 is only marginal (p = 0.088).

**Code findings:**
- linreg and lstm return a constant predictive sd across horizons (LSTM: one-step residual sd, hence 0% coverage in 2018).
- block_bootstrap_diff concatenates folds, blocks straddle the year boundary.
- Calibration step rule (|mean z| > 0.5 in both folds) did not re-centre in 2019 (z = -0.66, -0.45; actual 2019 -0.53).
- RMSE uses the lognormal mean for models with sd but the median for those without.

**Over-claims:** "matches or slightly beats climatology" (CI spans 0); lockdown 43% confounded with model level bias (model already high in 2019); LSTM comparison is a strawman; "drive/explain" language for Granger results.

**Prioritised fixes:** make verifier sandbox-safe; reword abstract; smooth the calibration rule; horizon-dependent sd for linreg/LSTM; sensitivity bounds for the lockdown gap (constant and random-walk level).
