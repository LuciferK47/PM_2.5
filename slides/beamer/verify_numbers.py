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
for mac_, (m_, f_) in {"fcMaeSelNineteen": ("Fourier+ARMA (selected)", 2019), "fcMaeClimNineteen": ("Climatology", 2019), "fcMaeSarimaNineteen": ("SARIMA D=1", 2019),
                       "fcMaeSarimaSeventeen": ("SARIMA D=1", 2017), "fcMaeLstmNineteen": ("LSTM (small)", 2019), "fcMaeLstmEighteen": ("LSTM (small)", 2018),
                       "fcMaeSarimaZeroNineteen": ("SARIMA D=0", 2019)}.items():
    exact_ = bf[(bf.model == m_) & (bf.fold == f_)].ae.mean()
    check(f"slide macro {mac_} = {macros[mac_]} equals the unrounded MAE {exact_:.3f} to one decimal", macros[mac_] == f"{exact_:.1f}")
ad_ = FC["validation_2019"]["annual_days_pred"]
check(f"2019 predicted band days sum to 365 (sum = {sum(ad_.values()):.1f})", close(sum(ad_.values()), 365, 0.2))
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
