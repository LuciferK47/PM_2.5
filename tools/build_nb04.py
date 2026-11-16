"""Builds notebooks/04_forecasting.ipynb (run: python tools/build_nb04.py, then execute the notebook)."""
import nbformat
from nbformat.v4 import new_code_cell as C, new_markdown_cell as M, new_notebook

cells = []
md = lambda s: cells.append(M(s))
code = lambda s: cells.append(C(s))

md("""# 04 · Forecasting weekly PM2.5: rolling-origin backtest, calibration, 1-week test, 2020 outlook
**What this notebook answers**
1. Which 52-week-ahead model is best, judged on three expanding-window origins (end of 2016, 2017, 2018 → forecasts for 2017, 2018, 2019)?
   Everything (Fourier order, ARMA order, level/trend treatment) is re-selected at each origin using only data before it.
2. Are the residuals clean (with the diffuse-initialisation residuals removed) and are the intervals calibrated?
3. Does weather help one week ahead, when tested fairly (lagged weather) versus with hindsight (same-week weather = oracle)?
4. What does a model fitted on 2015-2019 say about each month of 2020, and what does the gap to the lockdown months look like?

**Design rules.** Target: weekly mean PM2.5, modelled as log (so the point forecast `exp(mu)` is a *median*; mean forecasts use
`exp(mu + sd²/2)` with the horizon-specific sd). Season length 365.25/7 weeks. No weather in the 52-week models (notebook 03:
last week's weather adds nothing at the weekly scale and future weather is unknown). The 2020 lockdown never enters model selection.""")

code('''import os
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
print(F.ORIGINS)''')

md("""## 1. Models
| Model | What it is |
|---|---|
| Seasonal naive | the value 52 weeks earlier |
| Climatology | mean log PM2.5 of the same calendar week over the training years |
| Climatology + AR(1) | climatology plus an AR(1) on the weekly anomalies |
| Linear regression | OLS on 3 Fourier harmonics + a linear time trend (constant-variance intervals) |
| LSTM (small) | 1 layer, 16 units, seeded, recursive one-step on anomalies (no intervals of its own; training-residual sd) |
| Fourier+ARMA const / linear | dynamic harmonic regression: K=3 harmonics, AR(1) errors, constant or linear-trend level |
| **Fourier+ARMA (selected)** | K ∈ 1..5 and (p,q) by AICc inside each trend type (constant / linear / random-walk errors); the trend type chosen by validation on the *last training year*. **Declared as the headline procedure before looking at the test folds.** |
| SARIMA D=1 / D=0 | the benchmark from the draft: (1,0,1)(0,1,1)₅₂, and (1,0,1)(1,0,0)₅₂ **with a constant** (the draft omitted it) |""")

code('''models = {
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
print("Selected specification per origin:"); display(pd.DataFrame(specs).T[["trend", "K", "p", "q", "inner_mae"]])''')

md("""## 2. Backtest results (52 weeks ahead, MAE in µg/m³ on the original scale)
Folds 2018 and 2019 are the main evidence (3 and 4 training seasons); 2017 (only 2 training years) is a stress test. Climatology is the model to beat.""")

code('''tab = bt.pivot(index="model", columns="fold", values="MAE")
tab["mean 2018-19"] = tab[[2018, 2019]].mean(axis=1)
tab["mean all 3"] = tab[[2017, 2018, 2019]].mean(axis=1)
tab = tab.sort_values("mean 2018-19")
tab.round(1).to_csv(RESULTS / "fc_backtest_mae.csv")
display(tab.round(1))
extra = bt.groupby("model")[["RMSE", "logMAE", "MAE_winter", "MAE_other", "bias"]].mean().loc[tab.index]
extra["coverage95"] = bt.groupby("model")["coverage"].mean()
extra["winkler"] = bt.groupby("model")["winkler"].mean()
display(extra.round(2))''')

code('''# Paired loss differences against climatology: moving-block bootstrap (8-week blocks) of the weekly absolute-error differences.
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
display(ld[ld.folds == "folds 2018+2019"])''')

md("""**Reading it.** A negative difference means lower error than climatology. The interval is wide because 52 consecutive weekly errors
within one forecast path are strongly dependent: three origins are far too few for a sharp significance claim, and
we say "indistinguishable" whenever the interval contains 0. The earlier draft's 2019 comparison (SARIMA 27.5 vs climatology 27.8)
is such a case.""")

code('''sel_name = SEL
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
ax.set_xticks(x, [s.replace("Fourier+ARMA (selected)", "Fourier+ARMA\\n(selected)").replace(" ", "\\n", 1) for s in show], fontsize=7)
ax.set_ylabel("MAE (µg/m³)"); ax.legend(title="fold", fontsize=8); ax.set_title("MAE by fold")
savefig(fig, "13_backtest"); plt.show()''')

md("""## 3. Residual diagnostics (the draft's Ljung–Box result was an artifact)
`SARIMAX` with `D=1` initialises the first 52 seasonal states diffusely, so the first 52 in-sample residuals are as large as the series level
(about 5 on the log scale) and must be excluded (`res.loglikelihood_burn`). The draft ran Ljung–Box on all residuals and got p ≈ 0 at every lag.
Below: the same model with and without the exclusion, next to the selected Fourier+ARMA model, all fitted on 2015–2018.""")

code('''from statsmodels.tsa.statespace.sarimax import SARIMAX
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
display(par)''')

md("""**Reading it.** With the burn-in removed the SARIMA residuals are fine at lags 10 and 26, but the seasonal parameter is not identified:
the seasonal MA coefficient is near −1 with a standard error larger than its value, which is the signature of differencing a series that
does not need it (a deterministic seasonal pattern). Residual structure at lag 52 and in the Fourier model is reported honestly in the table
(see `LB_p_lag52`); no GARCH-type model is needed since ARCH-LM on the weekly residuals does not reject.""")

md("""## 4. Interval calibration
The draft's 95% interval covered only 85% of 2019 weeks and all misses were below the lower bound, so part of the problem is **level bias**
(2019 was cleaner than the training years), not only width. We calibrate with a rule fixed in advance and tested out of sample:
* compute standardised log errors `z = (log actual − mu)/sd` on the two *earlier* folds;
* scale the sd by season (winter vs other) with shrinkage toward the pooled value (k = 26 pseudo-weeks);
* **re-centre only if** the bias has the same sign in both calibration folds and |mean z| > 0.5. Otherwise leave the centre alone, since a level
  shift that flips sign across years cannot be corrected by the past.""")

code('''def standardized(fold, model=SEL):
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
key["calibration_rule_2019"] = rule19; key["coverage_2019_raw"] = float(cal_tab.iloc[0]["coverage"]); key["coverage_2019_calibrated"] = float(cal_tab.iloc[1]["coverage"])''')

md("""## 5. One week ahead: does weather help when tested fairly?
Each test year (2018, 2019) is forecast one week at a time. Parameters are fitted once, on all data before that year; each week the model sees all earlier
observed PM2.5 (a true one-step forecast). The selected model for that origin (from §1) is the "no weather" version; weather variables are weekly anomalies from a
climatology fitted on data before the test year.

| Variant | Weather information | Available in practice? |
|---|---|---|
| lagged weather | last week's mean wind and humidity anomaly | yes |
| last 3 days | mean anomaly of the last 3 days (Fri–Sun) of the previous week | yes |
| **same-week (oracle)** | the forecast week's own observed wind and humidity | **no**, hindsight upper bound (ERA5 reanalysis is not a forecast) |""")

code('''def weather_frame(train_end):
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
key["oneweek_mae"] = piv["both years"].round(2).to_dict()''')

code('''# coefficients of the oracle model on the 2019 origin, for interpretation
_, fit_or = one_step(2019, ["wind_same", "rh_same"])
coef = pd.DataFrame({"coef": fit_or.params[["wind_same", "rh_same"]], "p": fit_or.pvalues[["wind_same", "rh_same"]]}).round(4)
coef.to_csv(RESULTS / "fc_oneweek_oracle_coef.csv"); display(coef)
gain = lambda a, b: round(100 * (1 - piv.loc[a, "both years"] / piv.loc[b, "both years"]), 1)
key["oneweek_gain_pct"] = {"lagged": gain("+ lagged weather (operational)", base), "last3": gain("+ last 3 days of prior week (operational)", base),
                           "oracle": gain("+ same-week weather (ORACLE)", base)}
print(key["oneweek_gain_pct"], "(% MAE reduction vs no-weather DHR; positive = better)")''')

md("""**Reading it.** The operational variants (lagged weather) are compared with the model that has no weather; the oracle variant shows how much
accuracy would be available if the week's weather were known in advance. The Diebold–Mariano p-values use genuine one-step errors (Harvey–Leybourne–Newbold
small-sample correction), so unlike the 52-step comparison the test is valid here.""")

fig_cell = '''fig, ax = plt.subplots(figsize=(8, 3.6))
labs = [m.replace(" (operational)", "").replace(" (ORACLE)", "\\n(oracle)") for m in order_]
vals = [piv.loc[m, "both years"] for m in order_]
cols_ = [NEUTRAL, NEUTRAL, NEUTRAL, BLUE, AQUA, AQUA, ORANGE]
ax.bar(range(len(vals)), vals, color=cols_)
ax.set_xticks(range(len(vals)), labs, fontsize=7, rotation=20, ha="right")
ax.set_ylabel("One-week-ahead MAE, 2018-19 (µg/m³)")
ax.set_title("Weather helps one week ahead only when the week's own weather is known")
savefig(fig, "14_oneweek"); plt.show()'''
code(fig_cell)

md("""## 6. Final outlook for 2020 and validation of the method on 2019
**Procedure (identical for both).** Fit the headline procedure on the years before the target year; simulate 5,000 weekly paths from the fitted model
(53 weeks so every calendar day is covered); apply the calibration rule (fitted only on earlier folds); convert weekly paths to daily PM2.5 by adding a
resampled within-week offset `log(daily) − log(weekly mean)` drawn from the same calendar month of the training data; classify each day into the CPCB
PM2.5 sub-index bands. This yields (a) the median and 95% interval of each month's mean PM2.5 and (b) the expected number of days per band.
**This is a PM2.5 band, not the official AQI** (the AQI is the maximum sub-index over all pollutants).
2019 is a genuine out-of-sample test of the whole pipeline; 2020 is the deliverable.""")

code('''def pipeline(origin, year, folds_for_cal, n=5000):
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
assert np.allclose(P19["bands"].sum(axis=2)[0], [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])''')

code('''# 2020 deliverable: selection on data to 2019-12-29, calibration from folds 2018 and 2019
P20 = pipeline("2019-12-29", 2020, [2018, 2019])
mt20 = month_table(P20, 2020)
assert np.allclose(P20["bands"].sum(axis=2)[0], [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
a20 = daily.loc["2020"]["pm25"].dropna()
mt20["actual_mean_2020"] = a20.groupby(a20.index.month).mean().reindex(range(1, 13)).to_numpy()
mt20["actual_days_covered"] = a20.groupby(a20.index.month).count().reindex(range(1, 13)).to_numpy()
mt20.round(3).to_csv(RESULTS / "fc_outlook_2020.csv")
key["outlook_2020_spec"] = {k: v for k, v in P20["spec"].items() if k not in ("inner_mae", "res")}; key["outlook_2020_rule"] = P20["rule"]
display(mt20.round(2))''')

code('''fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.35, 1]})
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
savefig(fig, "15_outlook_2020"); plt.show()''')

md("""## 7. Case study: the 2020 lockdown
Delhi's lockdown began on 25 March 2020. We compare the actual weekly PM2.5 of the ten weeks ending 29 March – 31 May with the no-lockdown forecast made on
29 Dec 2019 (calibrated, as above). A second counterfactual uses a version of the same model *with the actual 2020 same-week wind and humidity* (fitted on 2015–2019),
to separate the weather contribution from the rest. Both are descriptive: they rely on the model being right about the level for 2020 (see §4).""")

code('''lock_idx = pd.date_range("2020-03-29", "2020-05-31", freq="W-SUN")
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
savefig(fig, "16_lockdown"); plt.show()''')

md("""## 8. Summary numbers""")
code('''m_sel = bt[bt.model == SEL].set_index("fold"); m_clim = bt[bt.model == "Climatology"].set_index("fold")
key["backtest"] = {"mae_selected": m_sel["MAE"].round(2).to_dict(), "mae_climatology": m_clim["MAE"].round(2).to_dict(),
                   "coverage_selected": m_sel["coverage"].round(3).to_dict(),
                   "sarima_D1_mae": bt[bt.model == "SARIMA D=1"].set_index("fold")["MAE"].round(2).to_dict(),
                   "sarima_D0_mae": bt[bt.model == "SARIMA D=0"].set_index("fold")["MAE"].round(2).to_dict(),
                   "lstm_mae": bt[bt.model == "LSTM (small)"].set_index("fold")["MAE"].round(2).to_dict(),
                   "specs": {int(f): {k: v for k, v in s.items() if k != "inner_mae"} for f, s in specs.items()}}
key["diagnostics_selected_2019_fold"] = {k: round(float(v), 4) for k, v in diag.iloc[0].items() if k != "LB_p_lag10_ALL_residuals (draft's mistake)"}
(RESULTS / "key_numbers_forecast.json").write_text(json.dumps(key, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
key''')

nb = new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
nbformat.write(nb, "notebooks/04_forecasting.ipynb")
print("written", len(cells))
