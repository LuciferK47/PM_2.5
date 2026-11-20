"""Rolling forecast evaluation at several horizons (1, 4, 13, 26, 52 weeks ahead).

Parameters (orders, K, smoothing parameters) are estimated once a year on earlier data only (end-2017 and end-2018, the
same fits as the year-ahead backtest, with the orders in results/fc_specs.csv). Within each test year every week is a
forecast origin: the model state is updated with the actual data up to that origin (parameters fixed) and then forecasts
1..52 weeks ahead. Nothing after the origin is used. Output: results/fc_horizon_forecasts.csv, fc_horizon.csv.

    python tools/horizon.py
"""
import os
import sys
import warnings
from pathlib import Path

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from joblib import Parallel, delayed  # noqa: E402
from statsmodels.tsa.exponential_smoothing.ets import ETSModel  # noqa: E402
from statsmodels.tsa.statespace.sarimax import SARIMAX  # noqa: E402

from src import forecast as F  # noqa: E402

warnings.filterwarnings("ignore")
RES = ROOT / "results"
HS = (1, 4, 13, 26, 52)
weekly = pd.read_csv(ROOT / "data/processed/delhi_weekly.csv", index_col="Date", parse_dates=True)
y = weekly["log_pm25"].loc[:"2019-12-29"]
raw = weekly["pm25"].loc[:"2019-12-29"]
specs = pd.read_csv(RES / "fc_specs.csv")
COMB = ["Seasonal mean", "Holt-Winters", "SARIMA", "Harmonic regression"]


def sp(fold, model):
    return specs[(specs.fold == fold) & (specs.model == model)].iloc[0]


def yearly_fits(fold):
    """Fit each model once on data up to the yearly origin, with the orders chosen in the year-ahead backtest."""
    origin = F.ORIGINS[fold]
    tr = y.loc[:origin]
    s_, h_, k_ = sp(fold, "SARIMA"), sp(fold, "Holt-Winters"), sp(fold, "Harmonic regression")
    assert h_.trend == "none" and h_.init == "estimated"
    sar = F._fit(SARIMAX(tr, order=(int(s_.p), 0, int(s_.q)), seasonal_order=(int(s_.P), 1, int(s_.Q), 52)))
    har = F._fit(SARIMAX(tr, exog=F.fourier(tr.index, int(k_.K)), order=(int(k_.p), 0, int(k_.q)), trend="c"))
    hw = ETSModel(tr, error="add", trend=None, seasonal="add", seasonal_periods=52, initialization_method="estimated").fit(disp=False, maxiter=1000)
    return {"origin": origin, "tr": tr, "sar": sar, "har": har, "hw_params": hw.params, "K": int(k_.K), "sar_order": (int(s_.p), int(s_.q), int(s_.P), int(s_.Q)),
            "har_order": (int(k_.p), int(k_.q))}


def one_origin(fit, o):
    """All six forecasts for 1..52 weeks after origin o, using data up to o only."""
    yo = y.loc[:o]
    idx = pd.date_range(o + pd.Timedelta(weeks=1), periods=52, freq="W-SUN")
    out = {}
    out["Seasonal naive"] = np.array([y.loc[t - pd.Timedelta(weeks=52)] for t in idx])
    out["Seasonal mean"] = F.seasonal_mean(yo, idx)["mu"]   # re-averaged with all data up to the origin (same information as the models)
    r = fit["sar"].apply(yo)
    out["SARIMA"] = r.get_forecast(52).predicted_mean.to_numpy()
    r = fit["har"].apply(yo, exog=F.fourier(yo.index, fit["K"]))
    out["Harmonic regression"] = r.get_forecast(52, exog=F.fourier(idx, fit["K"])).predicted_mean.to_numpy()
    m = ETSModel(yo, error="add", trend=None, seasonal="add", seasonal_periods=52, initialization_method="estimated")
    out["Holt-Winters"] = np.asarray(m.smooth(fit["hw_params"]).get_prediction(start=len(yo), end=len(yo) + 51).predicted_mean)
    out["Persistence"] = np.full(52, float(yo.iloc[-1]))
    out["Combination"] = np.mean([out[n] for n in COMB], axis=0)
    rows = []
    for name, mu in out.items():
        for h in range(1, 53):
            t = idx[h - 1]
            if t in y.index:
                rows.append((o, h, t, name, float(mu[h - 1]), float(raw.loc[t])))
    return rows


def dm_nw(e_a, e_b, h):
    """Diebold-Mariano test of equal absolute error. h-step forecast errors made at consecutive origins overlap, so the
    long-run variance of d_t = |e_a| - |e_b| uses a Bartlett kernel with h - 1 lags (capped at n/3 when there are few
    forecasts) and biased autocovariances (always a valid, non-negative variance); the reference is the normal
    distribution, as in the year-ahead test. With few forecasts the p-values are approximate."""
    from scipy import stats
    d = np.abs(np.asarray(e_a, float)) - np.abs(np.asarray(e_b, float))
    n = len(d)
    L = int(min(h - 1, n // 3))
    dc = d - d.mean()
    lrv = np.sum(dc ** 2) / n + 2 * sum((1 - k / (L + 1)) * np.sum(dc[k:] * dc[:-k]) / n for k in range(1, L + 1))
    dm = d.mean() / np.sqrt(lrv / n)
    return float(dm), float(2 * stats.norm.sf(abs(dm))), L


if __name__ == "__main__":
    last = y.index[-1]
    rows = []
    for fold, nxt in (() if "--score" in sys.argv else ((2018, 2019), (2019, None))):
        fit = yearly_fits(fold)
        start = pd.Timestamp(fit["origin"])
        stop = pd.Timestamp(F.ORIGINS[nxt]) - pd.Timedelta(weeks=1) if nxt else last - pd.Timedelta(weeks=1)
        origins = pd.date_range(start, stop, freq="W-SUN")
        print(fold, "fit", fit["sar_order"], fit["har_order"], "K", fit["K"], "origins", len(origins), flush=True)
        res = [one_origin(fit, o) for o in origins]
        rows += [r + (fold,) for batch in res for r in batch]
    if "--score" in sys.argv:
        df = pd.read_csv(RES / "fc_horizon_forecasts.csv", parse_dates=["origin", "target"])
    else:
        df = pd.DataFrame(rows, columns=["origin", "h", "target", "model", "mu", "actual", "fold"])
    assert (df.target > df.origin).all() and (df.h == ((df.target - df.origin).dt.days // 7)).all()
    assert (df.origin >= pd.Timestamp(F.ORIGINS[2018])).all()
    df.to_csv(RES / "fc_horizon_forecasts.csv", index=False)

    models = ["Persistence", "Seasonal naive", "Seasonal mean", "Holt-Winters", "SARIMA", "Harmonic regression", "Combination"]
    out = []
    for h in HS:
        d = df[df.h == h].assign(e=lambda x: x.actual - np.exp(x.mu))
        piv = d.pivot(index="target", columns="model", values="e")[models]
        base = piv["Seasonal mean"]
        for m in models:
            mae = piv[m].abs().mean()
            dm, p, L = (np.nan, np.nan, 0) if m == "Seasonal mean" else dm_nw(piv[m].to_numpy(), base.to_numpy(), h)
            out.append({"h": h, "model": m, "n": len(piv), "MAE": mae, "MAE % of seasonal mean": 100 * mae / base.abs().mean(),
                        "ME": piv[m].mean(), "DM": dm, "DM p": p, "lags": L})
    tab = pd.DataFrame(out)
    tab.round(4).to_csv(RES / "fc_horizon.csv", index=False)
    print(tab.pivot(index="model", columns="h", values="MAE").round(1).reindex(models))
    print(tab.pivot(index="model", columns="h", values="MAE % of seasonal mean").round(0).reindex(models))
    print(tab.pivot(index="model", columns="h", values="DM p").round(3).reindex(models))
