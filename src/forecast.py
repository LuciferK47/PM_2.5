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
