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
