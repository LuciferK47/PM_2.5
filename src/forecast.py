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
