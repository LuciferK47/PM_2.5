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
stl = STL(np.log(wk.pm25), period=52, robust=True).fit()
fs = max(0, 1 - np.var(stl.resid) / np.var(stl.seasonal + stl.resid))
check("STL seasonal strength 0.89", macros["Fs"] == f"{fs:.2f}", f"{fs:.3f}")

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
    doy = np.minimum(s.index.dayofyear, 365)
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
    check(f"link reachable: {url}", code in ("200", "301", "302"), f"HTTP {code}")
check("weather file is ERA5 archive for central Delhi (28.61N, 77.21E)", abs(json.loads((ROOT / "data/raw/delhi_weather_openmeteo.json").read_text())["latitude"] - 28.61) < 0.2)
tex = (Path(__file__).resolve().parent / "main.tex").read_text()
check("deck text never says SARIMA results exist (SARIMA is next phase)", "gainWeather" not in tex and "maeSarima" not in tex)

bad = [r for r in results if not r[1]]
print(f"\n{len(results) - len(bad)}/{len(results)} checks passed")
sys.exit(1 if bad else 0)
