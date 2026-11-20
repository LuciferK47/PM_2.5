"""Builds notebooks/03_var_granger.ipynb (run: python tools/build_nb03.py, then execute the notebook)."""
import nbformat
from nbformat.v4 import new_code_cell as C, new_markdown_cell as M, new_notebook

cells = []
md = lambda s: cells.append(M(s))
code = lambda s: cells.append(C(s))

md("""# 03 · Does weather help? VAR and Granger causality
**Question (Q2).** Do wind speed and relative humidity carry information about PM2.5 that PM2.5's own past does not?

**Variables** (daily means, ERA5 reanalysis via Open-Meteo, Delhi grid point 28.61°N 77.21°E):
* **wind** - 10 m wind **speed** in km/h (the strength of the wind, not its direction);
* **rh** - relative humidity in %;
* **pm25** - log of daily PM2.5 (µg/m³).

**Sample.** 2015-01-01 to 2019-12-31. The 2020 lockdown is excluded because it is an emissions shock, not a weather effect.

**Method.** (1) remove the yearly cycle, (2) choose the VAR lag by AIC/BIC, (3) run Granger F-tests in both directions, (4) repeat at the weekly scale,
because the forecasting study works with weekly means. The VAR and Granger test are on the course handout (Lectures 35-37).""")

code('''import sys
sys.path.append("..")

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.api import VAR

from src.data import PROCESSED, RESULTS
from src.tsa import doy_anomaly, doy365, doy_climatology, week_index
from src.plots import use_style, savefig, BLUE, ORANGE, AQUA, INK_2, MUTED, NEUTRAL, SEASON_COLORS

warnings.filterwarnings("ignore")
use_style()
daily = pd.read_csv(PROCESSED / "delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
weekly = pd.read_csv(PROCESSED / "delhi_weekly.csv", index_col="Date", parse_dates=True)
d = daily.loc[:"2019-12-31"]; w = weekly.loc[:"2019-12-29"]
NAMES = {"wind": "Wind", "rh": "Humidity", "pm25": "PM2.5"}
key = {"n_days_var": len(d), "n_weeks_var": len(w)}
d[["wind", "rh", "pm25", "temp", "precip"]].describe().round(1)''')

md("""## 1. The three series, weekly means
Wind, humidity and PM2.5 all follow the calendar: PM2.5 peaks in winter, when wind is a little calmer and the air is drier or foggier.
That shared seasonality is the reason we cannot just correlate the raw series.""")
code('''fig, axes = plt.subplots(3, 1, figsize=(10, 6.5), sharex=True)
for ax, (c, lab, col) in zip(axes, [("pm25", "PM2.5 (µg/m³)", BLUE), ("wind", "Wind speed (km/h)", ORANGE), ("rh", "Humidity (%)", AQUA)]):
    ax.plot(w.index, w[c], color=col, lw=1.2); ax.set_ylabel(lab, fontsize=9)
savefig(fig, "05_weather_weekly"); plt.show()
within = d.groupby("season").apply(lambda g: pd.Series({"corr(PM2.5, wind)": g["pm25"].corr(g["wind"], method="spearman"),
                                                          "corr(PM2.5, humidity)": g["pm25"].corr(g["rh"], method="spearman"), "days": len(g)})).round(2)
pooled = {"corr(PM2.5, wind)": d["pm25"].corr(d["wind"], method="spearman"), "corr(PM2.5, humidity)": d["pm25"].corr(d["rh"], method="spearman")}
within.to_csv(RESULTS / "within_season_correlation.csv")
key["spearman_pm25_wind"], key["spearman_pm25_rh"] = round(float(pooled["corr(PM2.5, wind)"]), 2), round(float(pooled["corr(PM2.5, humidity)"]), 2)
print("pooled Spearman:", key["spearman_pm25_wind"], key["spearman_pm25_rh"]); within''')

md("""## 2. Remove the seasonal cycle ("deseasonalise")
For each calendar day of the year we compute the **average over the five years** (smoothed with a 31-day window) - the *seasonal mean* of
that day - and subtract it. What remains is the **anomaly**: how much higher or lower than usual for that time of year the value is.
We deseasonalise PM2.5 on the log scale. Anomalies are what Granger causality should be tested on: otherwise "it is winter" would
make wind and PM2.5 look related at every lag.""")
code('''anom = pd.DataFrame({"wind": doy_anomaly(d["wind"]), "rh": doy_anomaly(d["rh"]), "pm25": doy_anomaly(d["log_pm25"]),
                     "temp": doy_anomaly(d["temp"]), "rain": doy_anomaly(d["precip"])})
assert anom.notna().all().all()
clim = doy_climatology(d["log_pm25"])
fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
axes[0].plot(d.index, d["log_pm25"], color=NEUTRAL, lw=0.8, label="daily log PM2.5")
axes[0].plot(d.index, clim.reindex(doy365(d.index)).to_numpy(), color=BLUE, lw=2, label="seasonal mean (day-of-year average)")
axes[0].legend(loc="lower left", ncols=2)
axes[1].plot(anom.index, anom["pm25"], color=BLUE, lw=0.8); axes[1].axhline(0, color=INK_2, lw=0.8)
axes[1].set_ylabel("anomaly"); axes[1].set_title("PM2.5 anomaly = log PM2.5 - seasonal mean")
savefig(fig, "07_deseasonalise"); plt.show()
anom.describe().round(2)''')

md("""## 3. Choosing the VAR lag by AIC and BIC (Lecture 29)
A VAR(p) predicts each variable from the previous *p* days of **all** three variables. With the three-variable system the AIC and BIC are
computed for p = 0..10; the lag with the smallest value is preferred (AIC is the less severe penalty, BIC the stronger one).""")
code('''model = VAR(anom[["wind", "rh", "pm25"]])
order = model.select_order(maxlags=10)
lag_table = pd.DataFrame({"AIC": [order.ics["aic"][p] for p in range(11)], "BIC": [order.ics["bic"][p] for p in range(11)]}, index=pd.Index(range(11), name="lag p (days)"))
lag_table.round(4).to_csv(RESULTS / "var_lag_selection.csv")
p = int(order.selected_orders["aic"])
res = model.fit(p)
white = res.test_whiteness(nlags=p + 10)
key.update({"var_lag_aic": p, "var_lag_bic": int(order.selected_orders["bic"]), "var_stable": bool(res.is_stable()),
            "portmanteau_p": round(float(white.pvalue), 3)})
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.plot(lag_table.index, lag_table["AIC"], marker="o", color=BLUE, label="AIC"); ax.plot(lag_table.index, lag_table["BIC"], marker="s", color=ORANGE, label="BIC")
ax.axvline(p, color=MUTED, ls=":"); ax.set_xlabel("VAR lag p (days)"); ax.set_ylabel("information criterion"); ax.legend()
savefig(fig, "08_var_lag"); plt.show()
print(key); lag_table.round(3)''')

md("""## 4. Granger causality: F-tests in both directions
**Granger causality** asks a *prediction* question: after we have used the past of PM2.5 (and of the other variable) to predict PM2.5 today,
do the past values of wind **add** any predictive information? Formally, in the PM2.5 equation
$$P_t = c + \\sum_{i=1}^{p} a_i P_{t-i} + \\sum_{i=1}^{p} b_i W_{t-i} + \\sum_{i=1}^{p} d_i H_{t-i} + u_t,$$
the null hypothesis "wind does not Granger-cause PM2.5" is $H_0: b_1=\\dots=b_p=0$. It is tested with an **F-test** (the usual test for
whether a group of regression coefficients is zero). A small p-value means wind's past improves the prediction of PM2.5. It does **not** mean
wind is irrelevant when the p-value is large for the reverse direction, and it is a statement about *prediction*, not a proof of physical cause.""")
code('''rows = []
for causing, caused in [("wind", "pm25"), ("rh", "pm25"), (["wind", "rh"], "pm25"), ("pm25", "wind"), ("pm25", "rh")]:
    t = res.test_causality(caused, causing, kind="f")
    rows.append({"direction": " + ".join(NAMES[c] for c in np.atleast_1d(causing)) + " → " + NAMES[caused],
                 "F": round(float(t.test_statistic), 2), "df": f"({int(t.df[0])}, {int(t.df[1])})", "p_value": float(t.pvalue)})
granger = pd.DataFrame(rows); granger.to_csv(RESULTS / "granger_var.csv", index=False)
key["granger"] = {r["direction"]: r["p_value"] for r in rows}
granger.assign(p_value=granger.p_value.map("{:.2e}".format))''')

code('''# robustness: add temperature and rain anomalies to the system (5 variables), same lag
m5 = VAR(anom[["wind", "rh", "pm25", "temp", "rain"]]); r5 = m5.fit(p)
rows5 = []
for causing in ("wind", "rh"):
    t = r5.test_causality("pm25", causing, kind="f")
    rows5.append({"direction": f"{NAMES[causing]} → PM2.5 (with temperature and rain)", "F": round(float(t.test_statistic), 2), "p_value": float(t.pvalue)})
rob = pd.DataFrame(rows5); rob.to_csv(RESULTS / "granger_var_controls.csv", index=False)
key["granger_controls"] = {r["direction"]: r["p_value"] for r in rows5}
rob.assign(p_value=rob.p_value.map("{:.2e}".format))''')

md("""**Result.** Wind and humidity each Granger-cause PM2.5 (p far below 0.001), also with temperature and rain in the system. The reverse
direction is not significant (PM2.5 → wind p = 0.12, PM2.5 → humidity p = 0.62). The physically sensible pattern: wind and moisture move the
pollution, pollution does not move tomorrow's wind. Note that "H0: wind adds nothing *given the past of P and H*" being rejected means wind's
past is a useful extra predictor; it does not say wind is the only or main driver.""")

md("""## 5. The weekly scale (what the forecasting study uses)
Our forecasts use **weekly** means. Does last week's wind and humidity help predict this week's PM2.5, once last week's PM2.5 is known?
We deseasonalise the weekly series (subtract the average of the same week of the year), then compare two regressions with an F-test:

* **Model 0:** $P_t = c + a\\,P_{t-1} + e_t$
* **Model 1:** $P_t = c + a\\,P_{t-1} + b\\,W_{t-1} + d\\,H_{t-1} + e_t$

and also report the *same-week* regression $P_t$ on $W_t, H_t$ (weather observed in the same week: only possible with hindsight).""")
code('''wk = w[["log_pm25", "wind", "rh"]].copy()
wk_an = wk - wk.groupby(week_index(wk.index)).transform("mean").to_numpy()
L = pd.concat([wk_an["log_pm25"].shift(1), wk_an["wind"].shift(1), wk_an["rh"].shift(1)], axis=1, keys=["pm25_l1", "wind_l1", "rh_l1"])
dfm = pd.concat([wk_an["log_pm25"].rename("pm25"), L, wk_an[["wind", "rh"]]], axis=1).dropna()
m0 = sm.OLS(dfm["pm25"], sm.add_constant(dfm[["pm25_l1"]])).fit()
m1 = sm.OLS(dfm["pm25"], sm.add_constant(dfm[["pm25_l1", "wind_l1", "rh_l1"]])).fit()
ftest = m1.compare_f_test(m0)                       # (F, p, df_diff)
same = sm.OLS(dfm["pm25"], sm.add_constant(dfm[["wind", "rh"]])).fit()
nested = pd.DataFrame({"R2 model 0 (last week's PM2.5)": [m0.rsquared], "R2 model 1 (+ last week's wind, humidity)": [m1.rsquared],
                       "delta R2": [m1.rsquared - m0.rsquared], "F": [ftest[0]], "p_value": [ftest[1]], "n_weeks": [len(dfm)],
                       "R2 same-week weather only": [same.rsquared]})
nested.round(4).to_csv(RESULTS / "weekly_lag_nested.csv", index=False)
key["weekly_nested"] = {k: round(float(v), 4) for k, v in nested.iloc[0].items()}
print(key["weekly_nested"]); nested.round(4)''')

md("""**Reading it.** At the **daily** scale the past of wind and humidity helps predict PM2.5 (Section 4). After averaging over a week and
conditioning on last week's PM2.5, last week's wind and humidity add essentially nothing (ΔR² is tiny, p is large), whereas the **same-week**
weather is related to PM2.5 (the daily effect, averaged). So weather matters **within days**, but its information is *used up* inside a week;
a forecast one week or one year ahead cannot use it, and the future weather would itself have to be forecast first.
Notebook 04 tests the same question in terms of forecast error (one week ahead).""")

code('''key["granger"] = {k: float(f"{v:.3g}") for k, v in key["granger"].items()}
key["granger_controls"] = {k: float(f"{v:.3g}") for k, v in key["granger_controls"].items()}
(RESULTS / "key_numbers_var.json").write_text(json.dumps(key, indent=2))
key''')

nb = new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
nbformat.write(nb, "notebooks/03_var_granger.ipynb")
print("wrote notebooks/03_var_granger.ipynb", len(cells), "cells")
