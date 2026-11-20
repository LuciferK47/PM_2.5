"""Independent audit of the numbers in the deck and report.

Recomputes the headline numbers from the RAW files (data/raw/*) with code that does not use src/ (own OLS for the Granger and
weekly tests, own error metrics, own seasonal-mean and naive forecasts, own Diebold-Mariano statistic), and compares them with what the
slides use (tables/numbers.tex, tables/*.tex, results/*.csv). Prints PASS/FAIL per check; exits 1 on any FAIL.
Run: .venv/bin/python slides/beamer/verify_numbers.py
"""
import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
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


def num(s):
    """Parse a macro/table value such as '\\ensuremath{-}12.3' or '1.2$\\times10^{-5}$' to a float."""
    s = re.sub(r"\\ensuremath\{(.*?)\}", r"\1", s).replace("$", "").replace("\\%", "").replace("{,}", "")
    if s.startswith("<10^"):
        return 10.0 ** int(re.search(r"\{(-?\d+)\}", s).group(1))
    m = re.match(r"^(-?[\d.]+)\\times10\^\{(-?\d+)\}$", s.replace(" ", ""))
    return float(m.group(1)) * 10 ** int(m.group(2)) if m else float(s)


macros = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{(.*)\}$", (TAB / "numbers.tex").read_text(), re.M))
mn = lambda k: num(macros[k])  # noqa: E731

# ── 1. rebuild the data from the raw files ─────────────────────────────────────────────────────────────
raw = pd.read_csv(ROOT / "data/raw/city_day.csv", parse_dates=["Date"])
dl = raw[raw.City == "Delhi"].set_index("Date").sort_index().asfreq("D")
wx = json.loads((ROOT / "data/raw/delhi_weather_openmeteo.json").read_text())["daily"]
wx = pd.DataFrame(wx).assign(Date=lambda d: pd.to_datetime(d.time)).set_index("Date").asfreq("D")
d = pd.DataFrame({"pm25": dl["PM2.5"], "wind": wx["wind_speed_10m_mean"], "rh": wx["relative_humidity_2m_mean"], "temp": wx["temperature_2m_mean"],
                  "rain": wx["precipitation_sum"]})
n_missing = int(d.pm25.isna().sum())
d["pm25"] = d["pm25"].interpolate(method="time", limit=3, limit_area="inside")
check("2,009 daily records", len(d) == 2009 and d.index.min() == pd.Timestamp("2015-01-01") and d.index.max() == pd.Timestamp("2020-07-01"))
check("2 PM2.5 values missing (then interpolated)", n_missing == 2 and d.pm25.notna().all(), f"missing={n_missing}")
check("weather has no gaps", d[["wind", "rh", "temp", "rain"]].notna().all().all())
d["lpm"] = np.log(d.pm25)
dm_ = d.loc[:"2019-12-31"]
proc = pd.read_csv(ROOT / "data/processed/delhi_daily.csv", index_col="Date", parse_dates=True)
check("processed daily PM2.5/wind/humidity equal independent rebuild", np.allclose(proc.pm25, d.pm25) and np.allclose(proc.wind, d.wind) and np.allclose(proc.rh, d.rh))
wk = d[["pm25"]].resample("W-SUN").mean().assign(n=d.pm25.resample("W-SUN").count())
wk = wk[wk.n >= 4]
procw = pd.read_csv(ROOT / "data/processed/delhi_weekly.csv", index_col="Date", parse_dates=True)
check("287 weekly means, equal independent rebuild", len(wk) == 287 and np.allclose(wk.pm25, procw.pm25))
lw = np.log(wk.pm25)
check("macros: nDays/nWeeks", macros["nDays"].replace("{,}", "") == "2009" and macros["nWeeks"] == "287")

# ── 2. motivation and seasonality (modelling sample 2015-2019) ─────────────────────────────────────────
share = float((dm_.pm25 > 90).mean() * 100)
check("share of days in the Poor band or worse (PM2.5 > 90), 2015-2019 only", macros["pctPoor"] == f"{share:.0f}", f"{share:.1f}%")
check("2015-2019 mean PM2.5", macros["pmMean"] == f"{dm_.pm25.mean():.0f}", f"{dm_.pm25.mean():.1f}")
w_mean = dm_.pm25[dm_.index.month.isin([11, 12, 1])].mean(); m_mean = dm_.pm25[dm_.index.month.isin([7, 8, 9])].mean()
check("winter / monsoon means and ratio", macros["winterMean"] == f"{w_mean:.0f}" and macros["monsoonMean"] == f"{m_mean:.0f}" and macros["ratioWM"] == f"{w_mean / m_mean:.1f}",
      f"{w_mean:.1f} / {m_mean:.1f}")

# ── 3. logarithm: skewness, mean-SD link ───────────────────────────────────────────────────────────────
lp = dm_.lpm
g_raw = [x.values for _, x in dm_.pm25.groupby(dm_.index.month)]; g_log = [x.values for _, x in lp.groupby(lp.index.month)]
mr, sr, ml, sl = [g.mean() for g in g_raw], [g.std(ddof=1) for g in g_raw], [g.mean() for g in g_log], [g.std(ddof=1) for g in g_log]
check("skewness raw / log", macros["skewRaw"] == f"{stats.skew(dm_.pm25.values):.2f}" and mn("skewLog") == round(stats.skew(lp.values), 2), f"{stats.skew(dm_.pm25.values):.3f} / {stats.skew(lp.values):.3f}")
check("corr(monthly mean, SD) raw / log", macros["corrRaw"] == f"{np.corrcoef(mr, sr)[0, 1]:.2f}" and mn("corrLog") == round(np.corrcoef(ml, sl)[0, 1], 2),
      f"{np.corrcoef(mr, sr)[0, 1]:.3f} / {np.corrcoef(ml, sl)[0, 1]:.3f}")
check("max/min monthly SD raw / log", macros["sdRatioRaw"] == f"{max(sr) / min(sr):.1f}" and macros["sdRatioLog"] == f"{max(sl) / min(sl):.1f}", f"{max(sr) / min(sr):.2f} / {max(sl) / min(sl):.2f}")

# ── 4. STL on the weekly modelling sample 2015-2019 ────────────────────────────────────────────────────
stl = STL(lw.loc[:"2019-12-29"], period=52, robust=True).fit()
fs_ = max(0, 1 - np.var(stl.resid) / np.var(stl.seasonal + stl.resid)); ft_ = max(0, 1 - np.var(stl.resid) / np.var(stl.trend + stl.resid))
check("seasonal / trend strength", macros["Fs"] == f"{fs_:.2f}" and macros["Ft"] == f"{ft_:.2f}", f"{fs_:.3f} / {ft_:.3f}")
check("seasonal swing factor", macros["seasRatio"] == f"{np.exp(stl.seasonal.max() - stl.seasonal.min()):.0f}", f"{np.exp(stl.seasonal.max() - stl.seasonal.min()):.1f}")
ann = dm_.pm25.groupby(dm_.index.year).mean()
check("decline 2016 -> 2019 (annual means)", macros["declAll"] == f"{abs(100 * (ann[2019] / ann[2016] - 1)):.0f}", f"{100 * (ann[2019] / ann[2016] - 1):.1f}%")

# ── 5. ACF, ADF, KPSS on the training weeks (2015-2018) ────────────────────────────────────────────────
tr = lw.loc[:"2018-12-30"]
check("train sample = 209 weeks", len(tr) == 209 and macros["nTrain"] == "209")
a = acf(tr, nlags=52)
check("ACF of log PM2.5 at lags 1, 26, 52", macros["acfOne"] == f"{a[1]:.2f}" and mn("acfHalf") == round(a[26], 2) and macros["acfYear"] == f"{a[52]:.2f}", f"{a[1]:.3f} {a[26]:.3f} {a[52]:.3f}")
t52 = tr.diff(52).dropna()
check("ACF of seasonal difference at lag 1", macros["acfDOne"] == f"{acf(t52, nlags=1)[1]:.2f}", f"{acf(t52, nlags=1)[1]:.3f}")
check("ACF of seasonal difference at lag 52 is negative", acf(t52, nlags=52)[52] < 0, f"{acf(t52, nlags=52)[52]:.2f}")
for lab, s_, pk, kk in (("log level", tr, "adfPLog", "kpssLog"), ("seasonal difference", t52, "adfPDiff", "kpssDiff")):
    ap, ks = adfuller(s_, autolag="AIC")[1], kpss(s_, regression="c", nlags="auto")[0]
    check(f"ADF p / KPSS stat, {lab}", close(np.log10(ap), np.log10(mn(pk)), 0.03) and close(ks, mn(kk), 0.0011) and ap < 0.05 and ks < 0.463, f"p={ap:.2e}, KPSS={ks:.3f}")

# ── 5b. SARIMA identification: same differencing, Ljung-Box df, harmonic K, Holt-Winters start ─────────
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox

idn = pd.read_csv(RES / "fc_sarima_identification.csv", index_col=0)
check("all SARIMA candidates in the AIC table share d = 0, D = 1 (AIC is only comparable on the same differencing)",
      all(re.search(r"\(\d,0,\d\)\(\d,1,\d\)52", n) for n in idn.index), str(list(idn.index)))
fitC = SARIMAX(tr, order=(1, 0, 1), seasonal_order=(0, 1, 1, 52)).fit(disp=False, maxiter=200)
rowC = idn[idn.index.str.contains(r"\(1,0,1\)\(0,1,1\)52")].iloc[0]
check("AIC of (1,0,1)(0,1,1)52 refit independently", close(fitC.aic, rowC.AIC, 0.2), f"{fitC.aic:.2f} vs {rowC.AIC}")
e_ = pd.Series(np.asarray(fitC.resid)).iloc[int(fitC.loglikelihood_burn):]
lb_ = acorr_ljungbox(e_, lags=[10, 26, 52], model_df=3, return_df=True)["lb_pvalue"]
lbf = pd.read_csv(RES / "fc_sarima_ljungbox.csv", index_col=0).iloc[:, 1]
check("Ljung-Box p-values with model_df = 3 (ar, ma, seasonal ma), first 52 residuals dropped",
      all(close(lb_[k], lbf.loc[k], 0.003) for k in (10, 26, 52)) and macros["lbTen"] == f"{lb_[10]:.2f}" and macros["lbFiftyTwo"] == f"{lb_[52]:.3f}", str(lb_.round(3).to_dict()))
sp_ = pd.read_csv(RES / "fc_specs.csv")
check("harmonic K is below the search bound (K_MAX = 10) at every origin", (sp_[sp_.model == "Harmonic regression"].K < 10).all(), str(sp_[sp_.model == "Harmonic regression"].K.tolist()))
check("Holt-Winters initial state estimated by maximum likelihood (Lecture 23) at every origin", (sp_[sp_.model == "Holt-Winters"].init == "estimated").all())

# ── 6. weather: VAR lag choice, Granger F-tests and the weekly nested test (own OLS) ──────────────────
def clim_anom(s, window=31):
    doy = np.where(s.index.is_leap_year & (s.index.dayofyear > 59), s.index.dayofyear - 1, s.index.dayofyear)
    clim = s.groupby(doy).mean().reindex(range(1, 366)).interpolate()
    half = window // 2
    padded = pd.concat([clim.iloc[-half:], clim, clim.iloc[:half]]).rolling(window, center=True).mean().iloc[half:-half]
    return s - padded.reindex(doy).to_numpy()


A = pd.DataFrame({"wind": clim_anom(dm_.wind), "rh": clim_anom(dm_.rh), "pm25": clim_anom(dm_.lpm), "temp": clim_anom(dm_.temp), "rain": clim_anom(dm_.rain)})


def lagged(df, cols, p, off):
    return np.column_stack([df[c].shift(k).to_numpy()[off:] for k in range(1, p + 1) for c in cols])


def ols_rss(y_, X_):
    X_ = np.column_stack([np.ones(len(y_)), X_]); b = np.linalg.lstsq(X_, y_, rcond=None)[0]; r = y_ - X_ @ b
    return float(r @ r), X_.shape[1]


# information criteria of a 3-variable VAR(p) on a common sample (first 10 observations dropped)
cols3 = ["wind", "rh", "pm25"]; OFF = 10; T = len(A) - OFF; K_ = 3
ic = {}
for p in range(0, 11):
    Y = A[cols3].to_numpy()[OFF:]
    X = lagged(A, cols3, p, OFF) if p else np.zeros((T, 0))
    X = np.column_stack([np.ones(T), X]); B = np.linalg.lstsq(X, Y, rcond=None)[0]; U = Y - X @ B; S = U.T @ U / T
    npar = K_ * (K_ * p + 1)
    ic[p] = (np.log(np.linalg.det(S)) + 2 * npar / T, np.log(np.linalg.det(S)) + npar * np.log(T) / T)
p_aic, p_bic = min(ic, key=lambda k: ic[k][0]), min(ic, key=lambda k: ic[k][1])
check("VAR lag by AIC / BIC", str(p_aic) == macros["varLagAic"] and str(p_bic) == macros["varLagBic"], f"AIC p={p_aic}, BIC p={p_bic}")


def granger(target, cause, controls, p=4):
    off = p
    y_ = A[target].to_numpy()[off:]
    own = [target] + controls
    Xr = lagged(A, own, p, off); Xu = np.column_stack([Xr, lagged(A, [cause], p, off)])
    rr, _ = ols_rss(y_, Xr); ru, ku = ols_rss(y_, Xu); n = len(y_)
    F = ((rr - ru) / p) / (ru / (n - ku))
    return F, float(stats.f.sf(F, p, n - ku))


Fw, pw = granger("pm25", "wind", ["rh"]); Fh, ph = granger("pm25", "rh", ["wind"])
check("Granger wind -> PM2.5 and humidity -> PM2.5 significant, p < 1e-9", pw < 1e-9 and ph < 1e-9 and mn("gWindP") < 1e-9 and mn("gRhP") < 1e-9, f"{pw:.1e} / {ph:.1e}")
Fw_, pw_ = granger("pm25", "wind", ["rh", "temp", "rain"]); Fh_, ph_ = granger("pm25", "rh", ["wind", "temp", "rain"])
check("Granger with temperature and rain controls still significant", pw_ < 1e-6 and ph_ < 1e-6 and mn("gWindPc") < 1e-6 and mn("gRhPc") < 1e-6, f"{pw_:.1e} / {ph_:.1e}")
Frw, prw = granger("wind", "pm25", ["rh"]); Frh, prh = granger("rh", "pm25", ["wind"])
check("reverse directions not significant (5%)", prw > 0.05 and prh > 0.05 and mn("gRevWindP") > 0.05 and mn("gRevRhP") > 0.05, f"{prw:.2f} / {prh:.2f}")

# weekly nested test
wm = pd.DataFrame({"p": lw, "w": wx["wind_speed_10m_mean"].resample("W-SUN").mean(), "h": wx["relative_humidity_2m_mean"].resample("W-SUN").mean()}).loc[lw.index]
wm = wm.loc[:"2019-12-29"]


def calendar_week(idx):
    thu = pd.DatetimeIndex(idx) - pd.Timedelta(days=3)
    doy = np.where(thu.is_leap_year & (thu.dayofyear > 59), thu.dayofyear - 1, thu.dayofyear).clip(1, 365)
    return np.minimum((doy - 1) // 7 + 1, 52)


wmk = wm - wm.groupby(calendar_week(wm.index)).transform("mean")
dfn = pd.DataFrame({"y": wmk.p, "p1": wmk.p.shift(1), "w1": wmk.w.shift(1), "h1": wmk.h.shift(1), "w0": wmk.w, "h0": wmk.h}).dropna()
r0, k0 = ols_rss(dfn.y.to_numpy(), dfn[["p1"]].to_numpy()); r1, k1 = ols_rss(dfn.y.to_numpy(), dfn[["p1", "w1", "h1"]].to_numpy())
tss = float(((dfn.y - dfn.y.mean()) ** 2).sum()); n = len(dfn)
Fn = ((r0 - r1) / 2) / (r1 / (n - k1)); pn = float(stats.f.sf(Fn, 2, n - k1))
check("weekly nested test: R2 0.123 -> 0.128, p 0.47", macros["nestRone"] == f"{1 - r0 / tss:.3f}" and macros["nestRtwo"] == f"{1 - r1 / tss:.3f}" and macros["nestP"] == f"{pn:.2f}",
      f"{1 - r0 / tss:.4f} -> {1 - r1 / tss:.4f}, p={pn:.3f}")
rs, _ = ols_rss(dfn.y.to_numpy(), dfn[["w0", "h0"]].to_numpy())
check("same-week weather R2", macros["nestRsame"] == f"{1 - rs / tss:.2f}", f"{1 - rs / tss:.3f}")

# ── 7. forecasts: seasonal naive and seasonal mean rebuilt independently; metrics recomputed by hand ──
ORIG = {2017: "2016-12-25", 2018: "2017-12-31", 2019: "2018-12-30"}
fb = pd.read_csv(RES / "fc_backtest_forecasts.csv", parse_dates=["date"])
raw_w = wk.pm25
cw = pd.Series(calendar_week(lw.index), index=lw.index)


def seasonal_mean_fc(train, idx):
    c = train.groupby(cw.loc[train.index]).mean().reindex(range(1, 53)).interpolate(limit_direction="both")
    return c.reindex(calendar_week(idx)).to_numpy()


def mae_of(act, mu):
    return float(np.mean(np.abs(act - np.exp(mu))))


tab = pd.read_csv(RES / "fc_backtest_mae.csv", index_col=0)
for fold, org in ORIG.items():
    trn = lw.loc[:org]; idx = pd.date_range(trn.index[-1] + pd.Timedelta(weeks=1), periods=52, freq="W-SUN")
    act = raw_w.loc[idx].to_numpy()
    naive = np.log(raw_w.shift(52).loc[idx].to_numpy()) if False else trn.iloc[-52:].to_numpy()
    check(f"seasonal naive MAE {fold}", close(mae_of(act, naive), tab.loc["Seasonal naive", str(fold)], 0.06), f"{mae_of(act, naive):.2f}")
    check(f"seasonal mean MAE {fold}", close(mae_of(act, seasonal_mean_fc(trn, idx)), tab.loc["Seasonal mean", str(fold)], 0.06), f"{mae_of(act, seasonal_mean_fc(trn, idx)):.2f}")

# hand-recomputed metrics for every model from the saved forecasts
bad = []
M = pd.read_csv(RES / "fc_backtest_metrics.csv")
for (fold, model), g in fb.groupby(["fold", "model"]):
    e = g.actual.to_numpy() - np.exp(g.mu.to_numpy())
    row = M[(M.fold == fold) & (M.model == model)].iloc[0]
    vals = {"ME": e.mean(), "MAE": np.abs(e).mean(), "RMSE": np.sqrt((e ** 2).mean()), "MAPE": 100 * np.abs(e / g.actual.to_numpy()).mean()}
    if g.sd.notna().all():
        z = stats.norm.ppf(0.975); lo, hi = np.exp(g.mu - z * g.sd), np.exp(g.mu + z * g.sd)
        vals["coverage"] = float(((g.actual >= lo) & (g.actual <= hi)).mean())
    if any(not close(v, row[k], 1e-6 * max(1, abs(v)) + 1e-9) for k, v in vals.items()):
        bad.append((fold, model))
check("ME/MAE/RMSE/MAPE/coverage recomputed by hand for all 18 model-fold forecasts", not bad and fb.groupby(["fold", "model"]).ngroups == 18, str(bad))
check("every forecast covers 52 weeks after its origin and all actuals equal the raw weeks",
      all(len(g) == 52 and g.date.min() > pd.Timestamp(ORIG[f]) for (f, m), g in fb.groupby(["fold", "model"])) and np.allclose(fb.actual, raw_w.reindex(fb.date).to_numpy()))
comb = fb.pivot_table(index=["fold", "date"], columns="model", values="mu")
cmb = comb[["Seasonal mean", "Holt-Winters", "SARIMA", "Harmonic regression"]].mean(axis=1)
check("combination = average of the four log forecasts", np.allclose(cmb.to_numpy(), comb["Combination"].to_numpy()))

# macros equal the table values
mae_t, rmse_t = tab, pd.read_csv(RES / "fc_backtest_rmse.csv", index_col=0)
SH = {"Seasonal naive": "Naive", "Seasonal mean": "Mean", "Holt-Winters": "HW", "SARIMA": "Sarima", "Harmonic regression": "Harm", "Combination": "Comb"}
ok = True
for m, sh in SH.items():
    for c, w in (("2017", "Seventeen"), ("2018", "Eighteen"), ("2019", "Nineteen"), ("mean 2018-19", "Avg")):
        ok &= macros[f"mae{sh}{w}"] == f"{mae_t.loc[m, c]:.1f}"
check("MAE macros equal results/fc_backtest_mae.csv", ok)

# Diebold-Mariano by hand (Bartlett, 12 lags) on the pooled 2018-19 errors
def err(model, folds):
    return np.concatenate([(g.actual.to_numpy() - np.exp(g.mu.to_numpy())) for (f, m), g in fb.groupby(["fold", "model"]) if m == model and f in folds])


dmt = pd.read_csv(RES / "fc_dm.csv", index_col=0)
for m in dmt.index:
    dd_ = np.abs(err(m, (2018, 2019))) - np.abs(err("Seasonal mean", (2018, 2019)))
    n_, db = len(dd_), dd_.mean(); dc = dd_ - db
    lrv = np.mean(dc ** 2) + 2 * sum((1 - k / 13) * np.mean(dc[k:] * dc[:-k]) for k in range(1, 13))
    st_ = db / np.sqrt(lrv / n_); p_ = 2 * stats.norm.sf(abs(st_))
    check(f"Diebold-Mariano vs seasonal mean, {m}: mean diff {db:.2f}, DM {st_:.2f}, p {p_:.3f}", close(db, dmt.loc[m].iloc[0], 0.002) and close(st_, dmt.loc[m, "DM"], 0.01) and close(p_, dmt.loc[m, "DM p-value"], 0.002))
check("no model significantly better than the seasonal mean (slide claim)", all(not (dmt.loc[m, "DM p-value"] < 0.05 and dmt.loc[m].iloc[0] < 0) for m in dmt.index))
check("macros: DM p-values for naive / Holt-Winters / SARIMA", macros["dmPNaive"] == f"{dmt.loc['Seasonal naive', 'DM p-value']:.2f}" and macros["dmPHW"] == f"{dmt.loc['Holt-Winters', 'DM p-value']:.2f}" and macros["dmPSarima"] == f"{dmt.loc['SARIMA', 'DM p-value']:.2f}")
check("every model over-predicts on average in 2018-19 (ME < 0, slide claim)", all(fb[(fb.fold.isin([2018, 2019])) & (fb.model == m)].pipe(lambda g: (g.actual - np.exp(g.mu)).mean()) < 0 for m in SH))

# ── 8. one week ahead (persistence and seasonal mean rebuilt) ──────────────────────────────────────────
ow = pd.read_csv(RES / "fc_oneweek.csv", index_col=0)
pers, sm_ = [], []
for yr in (2018, 2019):
    org = ORIG[yr]; trn = lw.loc[:org]
    idx = lw.loc[f"{yr}-01-01":f"{yr}-12-31"].index; idx = idx[idx > pd.Timestamp(org)]
    pers.append(np.abs(raw_w.loc[idx].to_numpy() - raw_w.shift(1).loc[idx].to_numpy()))
    sm_.append(np.abs(raw_w.loc[idx].to_numpy() - np.exp(seasonal_mean_fc(trn, idx))))
check("one-week persistence MAE", close(np.concatenate(pers).mean(), ow.loc["Persistence", "both years"], 0.002) and macros["onePers"] == f"{np.concatenate(pers).mean():.1f}", f"{np.concatenate(pers).mean():.2f}")
check("one-week seasonal-mean MAE", close(np.concatenate(sm_).mean(), ow.loc["Seasonal mean", "both years"], 0.002), f"{np.concatenate(sm_).mean():.2f}")
oof = pd.read_csv(RES / "fc_oneweek_forecasts.csv", parse_dates=["date"])
bad_ = [(y_, m) for (y_, m), g in oof.groupby(["year", "model"]) if not close(np.abs(g.actual - np.exp(g.mu)).mean(), ow.loc[m, str(y_)], 0.002)]
check("one-week MAE table recomputed from saved forecasts", not bad_, str(bad_))
check("last week's weather does not improve one-week MAE; oracle does (slide claims)", ow.loc["+ last week's weather", "both years"] > ow.loc["Harmonic, no weather", "both years"] > ow.loc["+ same-week weather (oracle)", "both years"])

# ── 9. 2020 what-if: seasonal mean rebuilt, lockdown gap and windows ───────────────────────────────────
f20 = pd.read_csv(RES / "fc_2020_forecasts.csv", parse_dates=["date"]); lk = pd.read_csv(RES / "fc_lockdown.csv", index_col=0)
idx20 = pd.date_range("2020-01-05", "2020-06-28", freq="W-SUN")
mu_sm = seasonal_mean_fc(lw.loc[:"2019-12-29"], idx20)
check("2020 seasonal-mean forecast rebuilt from 2015-2019 only", np.allclose(mu_sm, f20[f20.model == "Seasonal mean"].mu.to_numpy(), atol=1e-9))
act20 = raw_w.reindex(idx20).to_numpy()
lock = (idx20 >= "2020-03-29") & (idx20 <= "2020-05-31"); pre = idx20 <= "2020-03-22"
check("ten lockdown weeks", int(lock.sum()) == 10 and int(pre.sum()) == 12)
gap_sm = act20[lock].mean() / np.exp(mu_sm)[lock].mean() - 1
check("lockdown gap, seasonal mean", close(100 * gap_sm, lk.loc["Seasonal mean", "lockdown gap (%)"], 0.06), f"{100 * gap_sm:.1f}%")
for m in lk.index:
    g = f20[f20.model == m]; f = np.exp(g.mu.to_numpy())
    gp = act20[lock].mean() / f[lock].mean() - 1; pb = act20[pre].mean() / f[pre].mean() - 1
    check(f"lockdown gap and pre-lockdown bias recomputed, {m}", close(100 * gp, lk.loc[m, "lockdown gap (%)"], 0.06) and close(100 * pb, lk.loc[m, "bias Jan-Mar 2020 (%)"], 0.06) and close(100 * ((1 + gp) / (1 + pb) - 1), lk.loc[m, "gap after removing pre-lockdown bias (%)"], 0.06))
check("actual lockdown mean", macros["lockActual"] == f"{act20[lock].mean():.0f}", f"{act20[lock].mean():.1f}")
win = pd.read_csv(RES / "fc_lockdown_windows.csv")
ww = []
for (fold, m), g in fb.groupby(["fold", "model"]):
    a_, f_ = g.actual.to_numpy(), np.exp(g.mu.to_numpy())
    ww += [100 * (a_[s:s + 10].mean() / f_[s:s + 10].mean() - 1) for s in range(0, 43)]
check("10-week window gaps: 774 = 6 models x 3 years x 43 windows, equal recomputation", len(win) == 774 and np.allclose(sorted(win.gap_pct.to_numpy()), sorted(ww), atol=1e-6))
check("harmonic: no ordinary window as low as the lockdown gap (slide claim)", win[win.model == "Harmonic regression"].gap_pct.min() > lk.loc["Harmonic regression", "lockdown gap (%)"])

# ── 10. slides, notes and documents: structure ──────────────────────────────────────────────────────
main = (Path(__file__).resolve().parent / "main.tex").read_text(); body = main[main.index("\\begin{document}"):]
frames = body.count("\\begin{frame}"); notes = len(re.findall(r"\\note\{", body))
check("deck has 33-38 frames and every frame has a speaker note", 33 <= frames <= 38 and notes == frames, f"{frames} frames, {notes} notes")


def balanced(t, i):
    depth, j = 0, i
    while j < len(t):
        depth += t[j] == "{"; depth -= t[j] == "}"; j += 1
        if depth == 0:
            return t[i + 1:j - 1]
    return ""


bare = []
for m in re.finditer(r"\\note\{", body):
    txt = balanced(body, m.end() - 1)
    txt = re.sub(r"\\[A-Za-z]+", " ", txt)                                    # drop macros (their numbers are generated)
    txt = re.sub(r"Lectures? [\d, and-]+", " ", txt)                           # lecture numbers
    txt = re.sub(r"\b20(1[5-9]|20)\b", " ", txt)                              # years
    txt = txt.replace("PM2.5", " ")
    bare += [t_ for t_ in re.findall(r"\d+(?:\.\d+)?", txt) if t_ not in ("26", "52", "95", "365.25")]
check("speaker notes contain no hand-typed numbers (all numbers come from macros)", not bare, str(sorted(set(bare))[:15]))
forbidden = ["Wold", "Levene", "ARCH", "HAC", "Newey", "impulse", "FEVD", "Winkler", "bootstrap", "LSTM", "AICc", "calibrat", "Cholesky"]
slide_text = re.sub(r"\\note\{", "\\note{", body)
hits = [w for w in forbidden if w in re.sub(r"\\note\{.*?\}\s*\n\\end\{frame\}", "", body, flags=re.S)]
check("no out-of-syllabus terms on the slides", not hits, str(hits))
tabs_ok = all((TAB / f"{n}.tex").read_text().startswith("\\begin{tabular}") for n in ("acc", "key", "dm", "cover", "lock", "oneweek", "granger", "stationarity"))
check("generated tables exist and are boxed tabulars", tabs_ok)
docs = (ROOT / "README.md").read_text() + (ROOT / "HANDOFF.md").read_text()
strip = lambda v: re.sub(r"\\ensuremath\{(.*?)\}", r"\1", v).replace("$", "")  # noqa: E731
miss = [k for k in ("maeNaiveAvg", "maeMeanAvg", "maeHWAvg", "maeSarimaAvg", "maeHarmAvg", "maeCombAvg", "maeSarimaSeventeen", "lockActual", "pctPoor", "Fs") if strip(macros[k]) not in docs]
check("key numbers quoted in README/HANDOFF equal the macros", not miss, str(miss))

bad = [n for n, ok, _ in results if not ok]
print(f"\n{len(results) - len(bad)}/{len(results)} checks passed")
sys.exit(1 if bad else 0)
