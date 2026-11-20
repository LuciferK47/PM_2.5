"""Forecasting toolkit: models for weekly log PM2.5, expanding-window backtest, metrics, simulation.

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


def seasonal_mean(y, idx):
    """Mean log PM2.5 of each calendar week over the training years. sd = training residual sd around it."""
    c = _clim(y)
    resid = y - c.reindex(week_index(y.index)).to_numpy()
    sd = float(np.sqrt(np.mean(resid ** 2)))
    return {"mu": c.reindex(week_index(idx)).to_numpy(), "sd": np.full(len(idx), sd)}


climatology = seasonal_mean  # old name


# ── Holt-Winters (Lecture 22-23) ─────────────────────────────────────────────────────────────────────────
def _fit(mod, maxiter=200):
    """Fit a statsmodels model, silencing only convergence / start-value warnings (checked through `converged`)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return mod.fit(disp=False, maxiter=maxiter)


def converged(res):
    return bool(getattr(res, "mle_retvals", {}).get("converged", True))


def holt_winters(y, idx):
    """Additive Holt-Winters (ETS) on log PM2.5 with seasonal period 52. Level + (optionally damped) trend + seasonal
    index; the trend option is chosen by AIC on the training data. Initial level and seasonal indices are estimated by
    maximum likelihood (as in Lecture 23); the heuristic start (first two years) is used only if that fails.
    Interval from the model's own forecast variance."""
    from statsmodels.tsa.exponential_smoothing.ets import ETSModel
    best = None
    for init in ("estimated", "heuristic"):            # Lecture 23 uses "estimated"; heuristic only as a fallback
        for trend, damped in [(None, False), ("add", True)]:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    r = ETSModel(y, error="add", trend=trend, damped_trend=damped, seasonal="add", seasonal_periods=52,
                                 initialization_method=init).fit(disp=False, maxiter=1000)
                except Exception:  # noqa: BLE001
                    continue
            if np.isfinite(r.aic) and converged(r) and (best is None or r.aic < best[0]):
                best = (r.aic, trend, r, init)
        if best is not None:
            break
    _, trend, r, init = best
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f = r.get_prediction(start=len(y), end=len(y) + len(idx) - 1)
        mu = np.asarray(f.predicted_mean)
        sd = np.sqrt(np.asarray(f.var_pred_mean))
    return {"mu": mu, "sd": sd, "res": r, "spec": {"trend": trend or "none", "init": init, "alpha": float(r.smoothing_level),
                                                     "gamma": float(r.smoothing_seasonal)}}


# ── SARIMA with Box-Jenkins style AIC selection (Lectures 20-21, 29) ───────────────────────────────────────
SARIMA_GRID = [(p, q, P, Q) for p in (0, 1, 2) for q in (0, 1) for (P, Q) in ((0, 1), (1, 0), (1, 1))]


def sarima_auto(y, idx):
    """SARIMA(p,0,q)(P,1,Q)_52 on log PM2.5 (D = 1: the seasonal difference removes the yearly cycle).
    (p,q,P,Q) are chosen by AIC on the training data; fits that did not converge are rejected."""
    best, rejected = None, 0
    for p, q, P, Q in SARIMA_GRID:
        try:
            r = _fit(SARIMAX(y, order=(p, 0, q), seasonal_order=(P, 1, Q, 52)))
        except Exception:  # noqa: BLE001
            rejected += 1
            continue
        if not converged(r) or not np.isfinite(r.aic):
            rejected += 1
            continue
        if best is None or r.aic < best[0]:
            best = (r.aic, (p, q, P, Q), r)
    _, spec, r = best
    f = r.get_forecast(len(idx))
    return {"mu": f.predicted_mean.to_numpy(), "sd": np.sqrt(f.var_pred_mean.to_numpy()), "res": r,
            "spec": {"p": spec[0], "q": spec[1], "P": spec[2], "Q": spec[3], "n_rejected": rejected}}


def sarima_fixed(order, sorder):
    def _m(y, idx):
        res = _fit(SARIMAX(y, order=order, seasonal_order=sorder))
        f = res.get_forecast(len(idx))
        return {"mu": f.predicted_mean.to_numpy(), "sd": np.sqrt(f.var_pred_mean.to_numpy()), "res": res}
    return _m


# ── harmonic regression with ARMA errors (Lectures 13-16: regression with autocorrelated errors) ───────────
PQ_GRID = [(0, 0), (1, 0), (2, 0), (1, 1), (2, 1)]
K_MAX = 10   # Fourier pairs searched (FPP3 allows up to m/2 = 26; 10 keeps the search fast and is never the choice)


def harmonic(y, idx, fixed=None):
    """y_t = c + sum_k [a_k sin(2 pi k t / m) + b_k cos(2 pi k t / m)] + eta_t, eta_t ~ ARMA(p,q).
    K (number of Fourier pairs, 1..K_MAX) and (p,q) are chosen by AIC on the training data."""
    if fixed is not None:
        cand = [(fixed["K"], (fixed["p"], fixed["q"]))]
    else:
        cand = list(product(range(1, K_MAX + 1), PQ_GRID))
    best, rejected = None, 0
    for K, (p, q) in cand:
        try:
            r = _fit(SARIMAX(y, exog=fourier(y.index, K), order=(p, 0, q), trend="c"))
        except Exception:  # noqa: BLE001
            rejected += 1
            continue
        if not converged(r) or not np.isfinite(r.aic):
            rejected += 1
            continue
        if best is None or r.aic < best[0]:
            best = (r.aic, K, p, q, r)
    _, K, p, q, r = best
    f = r.get_forecast(len(idx), exog=fourier(idx, K))
    return {"mu": f.predicted_mean.to_numpy(), "sd": np.sqrt(f.var_pred_mean.to_numpy()), "res": r,
            "spec": {"K": K, "p": p, "q": q, "n_rejected": rejected}}


def combine(fcs, names):
    """Equal-weight combination of log forecasts (Lecture 30). Point forecast only: no interval."""
    return {"mu": np.mean([fcs[n]["mu"] for n in names], axis=0), "sd": None}


# ── metrics ─────────────────────────────────────────────────────────────────────────────────────────────
def metrics(actual, mu, sd=None, dates=None, level=0.95):
    """Raw-scale errors e = actual - exp(mu) (the median forecast). ME = mean error (bias), MAE, RMSE, MAPE (Lecture 30).
    Coverage and mean width describe the 95% interval exp(mu +- 1.96 sd)."""
    actual, mu = np.asarray(actual, float), np.asarray(mu, float)
    med = np.exp(mu)
    e = actual - med
    out = {"ME": e.mean(), "MAE": np.abs(e).mean(), "RMSE": np.sqrt((e ** 2).mean()), "MAPE": 100 * np.abs(e / actual).mean(),
           "logMAE": np.abs(np.log(actual) - mu).mean()}
    if sd is not None:
        z = stats.norm.ppf(0.5 + level / 2)
        lo, hi = np.exp(mu - z * np.asarray(sd)), np.exp(mu + z * np.asarray(sd))
        out["coverage"] = float(((actual >= lo) & (actual <= hi)).mean())
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


def dm_test(e_a, e_b, lag=12):
    """Diebold-Mariano test (Lecture 30) of equal absolute-error loss: d_t = |e_a| - |e_b|, H0: E(d) = 0.
    The long-run variance uses a Bartlett kernel with `lag` autocovariances, because the errors of a 52-step forecast
    are strongly autocorrelated. Returns (mean loss difference, DM statistic, two-sided p from the normal)."""
    d = np.abs(np.asarray(e_a, float)) - np.abs(np.asarray(e_b, float))
    n, dbar = len(d), d.mean()
    dc = d - dbar
    lrv = np.mean(dc ** 2) + 2 * sum((1 - k / (lag + 1)) * np.mean(dc[k:] * dc[:-k]) for k in range(1, lag + 1))
    dm = dbar / np.sqrt(lrv / n)
    return float(dbar), float(dm), float(2 * stats.norm.sf(abs(dm)))


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


