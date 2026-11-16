# 05 Phase 4: SARIMA draft (next_phase/), code, outputs and status

STATUS: draft only. The notebook `04_sarima.ipynb` was saved WITHOUT executed outputs; the three weekly 12-month result tables below were produced by an earlier run. The one-week-ahead comparison (SARIMA vs SARIMAX with weather vs persistence) has NOT been produced (results/metrics_1week.csv, sarimax_weather_coef.csv, key_numbers_sarima.json do not exist). LSTM and Linear Regression baselines are not written yet.

## What the draft does
Weekly log PM2.5, s=52, train 2015-2018 (209 weeks), test 2019 (52 weeks). Baselines: seasonal naive (same week last year), climatology (train mean of that week-of-year on log scale, then exp), persistence (1-week only). Grid of 72 SARIMA(p,0,q)(P,D,Q)52 models (p,q in 0..2; (P,Q) in 4 combos; D in 0,1), ranked by AIC/BIC within each D (for D=1 the grid uses simple_differencing). D is picked on validation year 2018 (fit 2015-2017). Final model fit on 2015-2018, 52-step forecast with exp() of the log-scale 95% interval. Diagnostics: Ljung-Box, ARCH-LM, Shapiro. 

## Outputs
Grid: 71 of 72 converged. Best D=1 models by AIC (nobs=157 after simple differencing, so AIC is not comparable with D=0, where nobs=209 and the best AIC is far higher):
```
 D  p  q  P  Q  aic  bic  nobs  converged
 1  1  1  0  1 39.4 51.7   157       True
 1  1  2  0  1 40.3 55.6   157       True
 1  2  1  0  1 40.5 55.8   157       True
 1  2  2  0  1 40.6 58.9   157       True
 1  1  1  1  1 41.2 56.5   157       True
```
Best D=0 models:
```
 D  p  q  P  Q  aic  bic  nobs  converged
 0  1  1  1  1 58.9 75.6   209       True
 0  2  1  1  1 59.5 79.6   209       True
 0  2  2  1  1 61.1 84.5   209       True
 0  1  2  1  1 61.1 81.1   209       True
 0  2  0  1  1 64.7 81.5   209       True
```
D choice on validation (fit 2015-2017, forecast 2018, MAE in ug/m3):
```
 D            order  MAE  RMSE
 0 (1,0,1)(1,0,1)52 39.7  43.6
 1 (1,0,1)(0,1,1)52 21.1  28.6
```

=> D=1, order (1,0,1)(0,1,1)52.

**Test 2019, 52-week-ahead (original ug/m3):**
```
                   Unnamed: 0  MAE  RMSE
SARIMA(1, 0, 1)x(0, 1, 1)[52] 27.5  40.5
               Seasonal naive 30.3  44.2
                  Climatology 27.8  41.1
```

95% interval empirical coverage on 2019 actuals: **84.6%** (nominal 95%). Mean forecast error (actual - forecast): SARIMA -14.7, climatology -12.6, seasonal naive -6.4 (all over-predict: 2019 was cleaner than 2015-2018).
Fitted parameters (re-fit by the reviewer): ar.L1 0.883, ma.L1 -0.633, ma.S.L52 **-0.988**, sigma2 0.046.

Ljung-Box file in next_phase/ (ljungbox.csv): every p-value is ~0 (49 lags, 0% above 0.05). See file 06: this is an artifact, not model failure.

## Forecast table (full, weekly, 2019)
```
      Date  actual  forecast  lo95  hi95  seasonal_naive  climatology
2019-01-06   282.4     259.4 162.7 413.4           247.3        229.1
2019-01-13   215.7     211.3 130.7 341.5           188.3        194.0
2019-01-20   239.2     230.2 140.9 376.1           197.5        221.3
2019-01-27   116.3     193.9 117.7 319.4           148.5        178.1
2019-02-03   166.6     166.3 100.3 275.6           137.0        158.9
2019-02-10   134.6     161.2  96.8 268.5           169.4        149.2
2019-02-17   152.8     139.4  83.4 233.0           103.7        133.6
2019-02-24    90.1     167.9 100.2 281.6           158.1        167.7
2019-03-03    80.3     112.2  66.8 188.5           104.9        120.7
2019-03-10    86.0      93.2  55.3 156.8            96.9         89.1
2019-03-17    82.4      90.3  53.6 152.3           102.2         92.2
2019-03-24    79.1     103.4  61.3 174.5            91.0         93.3
2019-03-31    87.1      98.7  58.5 166.8            97.7        103.2
2019-04-07   104.1     100.2  59.3 169.4            94.5         91.9
2019-04-14    72.9     103.7  61.4 175.4            75.2        101.5
2019-04-21    61.8     112.5  66.5 190.4            92.3        106.3
2019-04-28    88.3     104.6  61.8 177.1           103.7        112.6
2019-05-05    85.8     107.3  63.4 181.6            68.9         95.0
2019-05-12   129.0     105.5  62.3 178.6            99.4        112.3
2019-05-19    86.9      95.0  56.1 160.9            83.7         98.9
2019-05-26    67.3     100.8  59.5 170.7            98.6         90.9
2019-06-02    78.3      82.9  49.0 140.4            80.0         92.9
2019-06-09    70.2      72.1  42.5 122.0            64.9         65.0
2019-06-16    69.0      94.0  55.5 159.3           152.4         91.6
2019-06-23    53.5      70.8  41.8 119.9            68.3         75.1
2019-06-30    56.7      50.4  29.8  85.4            38.9         51.6
2019-07-07    46.8      55.3  32.7  93.7            51.7         60.6
2019-07-14    62.9      47.9  28.3  81.1            43.5         45.3
2019-07-21    42.6      38.9  23.0  66.0            36.8         43.3
2019-07-28    42.5      33.5  19.7  56.7            34.6         35.3
2019-08-04    34.2      48.9  28.9  82.8            59.5         41.9
2019-08-11    28.5      44.5  26.3  75.4            39.1         44.0
2019-08-18    20.8      41.9  24.7  70.9            38.7         44.9
2019-08-25    45.1      44.0  26.0  74.5            31.8         42.0
2019-09-01    39.6      43.5  25.7  73.7            37.9         40.4
2019-09-08    46.8      52.4  31.0  88.8            42.0         54.7
2019-09-15    50.6      57.9  34.2  98.1            33.3         54.8
2019-09-22    39.9      54.4  32.1  92.2            49.2         59.2
2019-09-29    25.6      75.8  44.8 128.4            57.6         69.7
2019-10-06    43.3     102.4  60.5 173.5            83.4         91.7
2019-10-13    87.5     110.6  65.3 187.3            96.9        119.6
2019-10-20   111.9     159.6  94.2 270.2           140.5        146.9
2019-10-27   140.3     185.2 109.4 313.6           171.2        189.3
2019-11-03   353.4     255.4 150.8 432.4           202.8        231.0
2019-11-10   176.2     306.7 181.1 519.2           283.1        311.0
2019-11-17   297.9     211.7 125.0 358.3           173.1        218.4
2019-11-24   152.5     184.4 109.0 312.1           168.9        193.0
2019-12-01    86.8     203.1 120.1 343.7           186.7        203.3
2019-12-08   204.6     202.4 119.6 342.3           201.9        207.2
2019-12-15   184.1     152.0  89.9 257.0           175.7        177.6
2019-12-22   185.6     211.0 124.9 356.6           261.5        199.7
2019-12-29   234.3     233.9 139.6 392.1           287.4        233.1
```

## Draft code (verbatim, next_phase/04_sarima_draft.py)
```python
# %% [markdown]
# # 04 · Preliminary SARIMA / SARIMAX models (weekly log PM2.5)
# **Aim:** (a) a 12-month (52-week) forecast and (b) a measure of how much weather helps at a 1-week horizon.
#
# **Design (from notebooks 02–03)**
# * Weekly series (week ending Sunday), **s = 52**, modelled on **log PM2.5**.
# * Split: train 2015-01 → 2018-12 (209 weeks), test 2019 (52 weeks). The 2020 lockdown is excluded.
# * **d = 0** (the log level passes ADF and KPSS on the training sample). **D ∈ {0, 1}** is chosen on a
#   *validation* year (2018, models fitted on 2015–2017), never on the test year.
# * **12-month forecast: no weather inputs.** Notebook 03 showed last week's weather does not predict this week's
#   PM2.5, and future weather is unknown a year ahead.
# * **1-week-ahead: with and without same-week wind and humidity.** The "with weather" version assumes the week's
#   weather is known (e.g. from a weather forecast), so it is an *upper bound* for what weather can add.
# * Forecasts are made on the log scale and back-transformed with exp(). That gives a **median** forecast (the
#   mean would be slightly higher). Intervals are exp() of the log-scale 95% interval, so they are asymmetric.

# %%
import sys
sys.path.append("..")

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from scipy import stats
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch

from src.data import PROCESSED, RESULTS
from src.plots import use_style, BLUE, ORANGE, INK_2, NEUTRAL

warnings.filterwarnings("ignore")
use_style()
S = 52
weekly = pd.read_csv(PROCESSED / "delhi_weekly.csv", index_col="Date", parse_dates=True).asfreq("W-SUN")
y = weekly["log_pm25"]
raw = weekly["pm25"]
train, test = y.loc[:"2018-12-31"], y.loc["2019-01-01":"2019-12-31"]
assert len(train) == 209 and len(test) == 52 and y.notna().all()
key = {"n_train": len(train), "n_test": len(test)}

# %% [markdown]
# ## 1. Baselines the SARIMA model has to beat
# * **Seasonal naive:** the value from the same week one year earlier.
# * **Climatology:** the average (on the log scale, then exp) of that calendar week over the training years.
# * **Persistence** (for the 1-week-ahead test only): last week's value.

# %%
woy = lambda idx: np.minimum(pd.DatetimeIndex(idx).isocalendar().week.to_numpy(), 52)  # noqa: E731
clim_log = train.groupby(woy(train.index)).mean()
baseline = pd.DataFrame(index=test.index)
baseline["actual"] = raw.loc[test.index]
baseline["seasonal_naive"] = raw.shift(S).loc[test.index]
baseline["climatology"] = np.exp(clim_log.reindex(woy(test.index)).to_numpy())
baseline["persistence"] = raw.shift(1).loc[test.index]


def metrics(pred, actual):
    e = actual - pred
    return {"MAE": float(np.abs(e).mean()), "RMSE": float(np.sqrt((e ** 2).mean()))}


{k: {m: round(v, 1) for m, v in metrics(baseline[k], baseline["actual"]).items()} for k in ["seasonal_naive", "climatology"]}

# %% [markdown]
# ## 2. Order search: SARIMA(p, 0, q)(P, D, Q)₅₂, ranked by AIC and BIC
# Grid: p, q ∈ {0, 1, 2}; (P, Q) ∈ {(0,0), (1,0), (0,1), (1,1)}; D ∈ {0, 1}. 72 models, fitted on the training
# years. For speed the D = 1 grid uses simple differencing (the series is differenced once at lag 52 before
# fitting). **AIC and BIC are only comparable between models with the same D** (different numbers of observations).

# %%
def fit_one(series, p, q, P, Q, D, exog=None, simple=False, maxiter=100):
    mod = SARIMAX(series, exog=exog, order=(p, 0, q), seasonal_order=(P, D, Q, S), simple_differencing=simple)
    return mod.fit(disp=False, maxiter=maxiter)


def grid_row(p, q, P, Q, D):
    try:
        r = fit_one(train, p, q, P, Q, D, simple=(D == 1))
        return dict(D=D, p=p, q=q, P=P, Q=Q, aic=r.aic, bic=r.bic, nobs=int(r.nobs), converged=bool(r.mle_retvals.get("converged", False)))
    except Exception as e:  # noqa: BLE001
        return dict(D=D, p=p, q=q, P=P, Q=Q, aic=np.nan, bic=np.nan, nobs=0, converged=False)


combos = [(p, q, P, Q, D) for D in (0, 1) for p in (0, 1, 2) for q in (0, 1, 2) for P, Q in ((0, 0), (1, 0), (0, 1), (1, 1))]
grid = pd.DataFrame(Parallel(n_jobs=8)(delayed(grid_row)(*c) for c in combos))
grid.to_csv(RESULTS / "sarima_grid.csv", index=False)
print("models:", len(grid), "| converged:", int(grid["converged"].sum()), "| failed:", int(grid["aic"].isna().sum()))
top = {D: grid[(grid.D == D) & grid.converged].sort_values("aic").head(5) for D in (0, 1)}
pd.concat(top.values()).round(1)

# %% [markdown]
# Only models that converged are ranked. The best model by AIC and by BIC (within each D) is recorded below.

# %%
best = {}
for D in (0, 1):
    g = grid[(grid.D == D) & grid.converged]
    best[D] = {"aic": g.sort_values("aic").iloc[0].to_dict(), "bic": g.sort_values("bic").iloc[0].to_dict()}
    print(f"D={D}: best AIC = SARIMA({int(best[D]['aic']['p'])},0,{int(best[D]['aic']['q'])})({int(best[D]['aic']['P'])},{D},{int(best[D]['aic']['Q'])})52 "
          f"(AIC {best[D]['aic']['aic']:.1f}) | best BIC = ({int(best[D]['bic']['p'])},0,{int(best[D]['bic']['q'])})({int(best[D]['bic']['P'])},{D},{int(best[D]['bic']['Q'])})52 (BIC {best[D]['bic']['bic']:.1f})")

# %% [markdown]
# ## 3. Choosing D on a validation year (2018), not on the test year
# For each D, take its best-AIC order, fit on 2015–2017 and forecast the 52 weeks of 2018. The D with the lower
# validation MAE is used. (The order search above did see 2018 in-sample but never 2019.)

# %%
tr_sub, val = y.loc[:"2017-12-31"], y.loc["2018-01-01":"2018-12-31"]
assert len(val) == 52
val_rows = []
for D in (0, 1):
    b = best[D]["aic"]
    r = fit_one(tr_sub, int(b["p"]), int(b["q"]), int(b["P"]), int(b["Q"]), D)
    fc = np.exp(r.get_forecast(52).predicted_mean.to_numpy())
    val_rows.append({"D": D, "order": f"({int(b['p'])},0,{int(b['q'])})({int(b['P'])},{D},{int(b['Q'])})52", **{k: round(v, 1) for k, v in metrics(fc, raw.loc[val.index].to_numpy()).items()}})
val_sn = metrics(raw.shift(S).loc[val.index].to_numpy(), raw.loc[val.index].to_numpy())
val_tab = pd.DataFrame(val_rows)
val_tab.to_csv(RESULTS / "sarima_D_choice.csv", index=False)
D_star = int(val_tab.sort_values("MAE").iloc[0]["D"])
key["D_chosen"] = D_star
key["validation_seasonal_naive_MAE"] = round(val_sn["MAE"], 1)
print("Validation (2018):"); print(val_tab); print("seasonal naive on 2018:", {k: round(v, 1) for k, v in val_sn.items()}, "| chosen D =", D_star)

# %% [markdown]
# ## 4. Final model: fit on 2015–2018, forecast 2019 (52 weeks)

# %%
b = best[D_star]["aic"]
order = (int(b["p"]), 0, int(b["q"]))
sorder = (int(b["P"]), D_star, int(b["Q"]), S)
spec = f"SARIMA{order}x{sorder[:3]}[{S}]"
res = SARIMAX(train, order=order, seasonal_order=sorder).fit(disp=False, maxiter=200)
fc = res.get_forecast(52)
ci = fc.conf_int(alpha=0.05)
fcdf = pd.DataFrame({"actual": raw.loc[test.index], "forecast": np.exp(fc.predicted_mean.to_numpy()),
                     "lo95": np.exp(ci.iloc[:, 0].to_numpy()), "hi95": np.exp(ci.iloc[:, 1].to_numpy()),
                     "seasonal_naive": baseline["seasonal_naive"], "climatology": baseline["climatology"]}, index=test.index)
fcdf.to_csv(RESULTS / "forecast_2019.csv")
cover = float(((fcdf.actual >= fcdf.lo95) & (fcdf.actual <= fcdf.hi95)).mean())
m12 = pd.DataFrame({name: metrics(fcdf[col], fcdf["actual"]) for name, col in
                    [(spec, "forecast"), ("Seasonal naive", "seasonal_naive"), ("Climatology", "climatology")]}).T.round(1)
m12.to_csv(RESULTS / "metrics_12month.csv")
key.update({"final_model": spec, "coverage_95": round(cover, 3), "ci_width_first_week": round(float(fcdf.hi95.iloc[0] - fcdf.lo95.iloc[0]), 1),
            "ci_width_last_week": round(float(fcdf.hi95.iloc[-1] - fcdf.lo95.iloc[-1]), 1)})
print(spec, "| 95% interval coverage of 2019 actuals:", round(cover, 2))
m12

# %%
fig, ax = plt.subplots(figsize=(10, 4))
ax.fill_between(fcdf.index, fcdf.lo95, fcdf.hi95, color=BLUE, alpha=0.18, lw=0, label="95% interval")
ax.plot(fcdf.index, fcdf.forecast, color=BLUE, lw=2, label=f"Forecast: {spec}")
ax.plot(fcdf.index, fcdf.actual, color=ORANGE, lw=1.6, marker="o", ms=3, label="Actual 2019")
ax.plot(fcdf.index, fcdf.climatology, color=NEUTRAL, lw=1.2, ls="--", label="Climatology")
ax.set_ylabel("Weekly mean PM2.5 (µg/m³)")
ax.legend(ncols=2)
ax.set_title("12-month (52-week) forecast for 2019 vs actual")
plt.show()

# %% [markdown]
# ## 5. Residual diagnostics: are the residuals white noise?
# **Ljung-Box** tests H₀: no autocorrelation up to lag k (large p-values are good). **ARCH-LM** tests whether large
# residuals cluster (changing variance).

# %%
resid = pd.Series(res.resid, index=train.index)
df_model = order[0] + order[2] + sorder[0] + sorder[2]
lb = acorr_ljungbox(resid, lags=list(range(df_model + 1, 53)), model_df=df_model, return_df=True)
lb.to_csv(RESULTS / "ljungbox.csv")
arch_lm, arch_p, _, _ = het_arch(resid, nlags=4)
shapiro = stats.shapiro(resid)
key.update({"ljungbox_share_p_above_0.05": round(float((lb["lb_pvalue"] > 0.05).mean()), 2), "ljungbox_min_p": round(float(lb["lb_pvalue"].min()), 3),
            "ljungbox_p_lag10": round(float(lb.loc[10, "lb_pvalue"]), 3) if 10 in lb.index else None,
            "ljungbox_p_lag26": round(float(lb.loc[26, "lb_pvalue"]), 3) if 26 in lb.index else None,
            "ljungbox_p_lag52": round(float(lb.loc[52, "lb_pvalue"]), 3),
            "arch_lm_p": round(float(arch_p), 3), "shapiro_p": round(float(shapiro.pvalue), 3)})
fig, ax = plt.subplots(figsize=(9, 3.2))
ax.vlines(lb.index, 0, lb["lb_pvalue"], color=BLUE, lw=1)
ax.scatter(lb.index, lb["lb_pvalue"], color=BLUE, s=14, zorder=3)
ax.axhline(0.05, color=ORANGE, lw=1.5)
ax.set_ylim(0, 1.02); ax.set_xlabel("Lag (weeks)"); ax.set_ylabel("Ljung-Box p-value")
plt.show()
{k: key[k] for k in key if k.startswith(("ljung", "arch", "shapiro"))}

# %% [markdown]
# ## 6. One-week-ahead test: does same-week weather help?
# Parameters are fixed from the training fit. For each 2019 week the model sees all earlier weeks, then predicts
# that week (so no future information is used). The SARIMAX version additionally uses that week's standardised
# wind and humidity, which is only possible if the weather is known (for example from a weather forecast).

# %%
ex_cols = ["wind", "rh"]
ex = (weekly[ex_cols] - weekly.loc[train.index, ex_cols].mean()) / weekly.loc[train.index, ex_cols].std()
y_all = y.loc[:"2019-12-31"]


def one_step(exog):
    kw = {} if exog is None else {"exog": exog.loc[train.index]}
    r_tr = SARIMAX(train, order=order, seasonal_order=sorder, **kw).fit(disp=False, maxiter=200)
    kw_all = {} if exog is None else {"exog": exog.loc[y_all.index]}
    r_all = SARIMAX(y_all, order=order, seasonal_order=sorder, **kw_all).smooth(r_tr.params)
    pr = r_all.get_prediction(start=test.index[0], dynamic=False).predicted_mean
    assert np.abs(pr.to_numpy() - test.to_numpy()).mean() < 1.0, "one-step predictions are not on the log-level scale"
    return r_tr, np.exp(pr.to_numpy())


r_plain, pred_plain = one_step(None)
r_wx, pred_wx = one_step(ex[ex_cols])
os_tab = pd.DataFrame({
    "Persistence (last week)": metrics(baseline["persistence"], baseline["actual"]),
    "Seasonal naive": metrics(baseline["seasonal_naive"], baseline["actual"]),
    f"{spec} (no weather)": metrics(pred_plain, baseline["actual"]),
    f"{spec} + same-week wind & humidity": metrics(pred_wx, baseline["actual"]),
}).T.round(1)
os_tab.to_csv(RESULTS / "metrics_1week.csv")
wx_coef = pd.DataFrame({"coef": r_wx.params[ex_cols], "p_value": r_wx.pvalues[ex_cols]}).round(4)
wx_coef.to_csv(RESULTS / "sarimax_weather_coef.csv")
gain = 100 * (1 - os_tab.iloc[3]["MAE"] / os_tab.iloc[2]["MAE"])
key["one_week_mae_gain_from_weather_pct"] = round(float(gain), 1)
os_tab
wx_coef

# %% [markdown]
# **Reading it:** see the table. "Gain from weather" is the MAE reduction of the weather model over the same model
# without weather. It uses the *actual* same-week weather, so in practice (with imperfect weather forecasts) the
# gain would be smaller.

# %%
(RESULTS / "key_numbers_sarima.json").write_text(json.dumps(key, indent=2, ensure_ascii=False, default=str))
key
```
