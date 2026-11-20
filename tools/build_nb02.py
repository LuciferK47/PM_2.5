"""Builds notebooks/02_eda.ipynb (run: python tools/build_nb02.py, then execute the notebook)."""
import nbformat
from nbformat.v4 import new_code_cell as C, new_markdown_cell as M, new_notebook

cells = []
md = lambda s: cells.append(M(s))
code = lambda s: cells.append(C(s))

md("""# 02 · Exploring the data: seasonality, transformation, stationarity, ACF/PACF
Course topics used here: components of a time series, additive vs multiplicative structure, logarithm and Box–Cox, classical/STL
decomposition (Lectures 04-07), stationarity, ACF/PACF, ADF and KPSS (Lectures 08-12), differencing (Lectures 06, 18-21).

**Samples.** The *modelling sample* is 2015-01 to 2019-12. Everything that guides a modelling choice (ACF/PACF, ADF/KPSS, differencing)
uses the **training years 2015-2018 only**, so 2019 stays an unseen test year for the forecasting notebook.
2020 (the lockdown) is shown in the time plot but is **not used in any estimate** in this notebook.""")

code('''import sys
sys.path.append("..")

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.tsa.seasonal import STL
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf

from src.data import PROCESSED, RAW, RESULTS, SEASONS
from src.aqi import pm25_category, CATEGORIES
from src.tsa import stationarity_table
from src.plots import use_style, savefig, SEASON_COLORS, BLUE, ORANGE, AQUA, NEUTRAL, INK_2, MUTED

use_style()
daily = pd.read_csv(PROCESSED / "delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
weekly = pd.read_csv(PROCESSED / "delhi_weekly.csv", index_col="Date", parse_dates=True)
d_mod = daily.loc[:"2019-12-31"]                       # modelling sample, daily
w_mod = weekly.loc[:"2019-12-29"]                      # modelling sample, weekly (260 weeks)
w_tr = weekly.loc[:"2018-12-30"]                       # training years only (209 weeks)
key = {"n_days": len(daily), "n_weeks": len(weekly), "n_weeks_model": len(w_mod), "n_weeks_train": len(w_tr)}
print(len(daily), "days;", len(weekly), "weeks;", len(w_mod), "weeks 2015-2019;", len(w_tr), "weeks 2015-2018")''')

md("""## 1. The series: how bad is Delhi's PM2.5, and when?""")
code('''cat_share = pm25_category(d_mod["pm25"].to_numpy()).value_counts(normalize=True).reindex(CATEGORIES) * 100
key["pct_days_poor_or_worse"] = round(float(cat_share[["Poor", "Very Poor", "Severe"]].sum()), 1)
key["pm25_mean_2015_2019"] = round(float(d_mod["pm25"].mean()), 1)
key["pm25_max_daily"] = round(float(d_mod["pm25"].max()), 1)
fig, ax = plt.subplots(figsize=(11, 3.6))
ax.plot(daily.index, daily["pm25"], color=MUTED, lw=0.5, label="daily")
ax.plot(daily.index, daily["pm25"].rolling(30, center=True).mean(), color=BLUE, lw=2, label="30-day mean")
ax.axvspan(pd.Timestamp("2020-01-01"), daily.index[-1], color=NEUTRAL, alpha=0.3, lw=0, label="2020 (not used for fitting)")
ax.set_ylabel("PM2.5 (µg/m³)"); ax.legend(); ax.set_title("Daily PM2.5 in Delhi, 2015-2020")
savefig(fig, "01_pm25_timeseries"); plt.show()
print("share of days Poor or worse:", key["pct_days_poor_or_worse"], "%")''')

md("""## 2. Seasonality by month""")
code('''month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
by_month = [d_mod.loc[d_mod.index.month == m, "pm25"].dropna() for m in range(1, 13)]
month_season = {m: n for n, ms in SEASONS.items() for m in ms}
colours = [SEASON_COLORS[month_season.get(m, "Other months")] for m in range(1, 13)]
fig, ax = plt.subplots(figsize=(10, 4))
bp = ax.boxplot(by_month, tick_labels=month_names, patch_artist=True, widths=0.65,
                medianprops=dict(color="black", lw=1.8), flierprops=dict(markersize=2, alpha=0.4))
for b, c in zip(bp["boxes"], colours):
    b.set(facecolor=c, edgecolor="white")
ax.set_ylabel("PM2.5 (µg/m³)"); ax.set_title("PM2.5 by calendar month, 2015-2019")
savefig(fig, "02_monthly_boxplot"); plt.show()
season_stats = d_mod.groupby("season")[["pm25", "wind", "rh"]].agg(["mean", "median"]).round(1)
winter, monsoon = "Winter (Nov–Jan)", "Monsoon (Jul–Sep)"
key["winter_mean_pm25"] = float(season_stats.loc[winter, ("pm25", "mean")])
key["monsoon_mean_pm25"] = float(season_stats.loc[monsoon, ("pm25", "mean")])
key["winter_to_monsoon_ratio"] = round(key["winter_mean_pm25"] / key["monsoon_mean_pm25"], 2)
season_stats.to_csv(RESULTS / "season_stats.csv")
season_stats''')

md("""## 3. Why the logarithm? (Lecture 06: multiplicative structure)
If the size of the seasonal swings grows with the level, the series is *multiplicative*: x = T × S × R. Taking logs turns it into
an additive one. A simple check: compute the **mean and the standard deviation of PM2.5 within each calendar month**; if the SD
rises with the mean, the log is appropriate. After the log the SD should no longer depend on the mean.""")
code('''pm = d_mod["pm25"].dropna(); lg = np.log(pm)
bm = pd.DataFrame({"mean_raw": pm.groupby(pm.index.month).mean(), "sd_raw": pm.groupby(pm.index.month).std(),
                   "mean_log": lg.groupby(lg.index.month).mean(), "sd_log": lg.groupby(lg.index.month).std()})
bm.index.name = "month"; bm.round(3).to_csv(RESULTS / "monthly_mean_sd.csv")
log_tests = pd.DataFrame({
    "raw PM2.5": [stats.skew(pm), np.corrcoef(bm["mean_raw"], bm["sd_raw"])[0, 1], bm["sd_raw"].max() / bm["sd_raw"].min()],
    "log PM2.5": [stats.skew(lg), np.corrcoef(bm["mean_log"], bm["sd_log"])[0, 1], bm["sd_log"].max() / bm["sd_log"].min()],
}, index=["Skewness", "corr(monthly mean, monthly SD)", "Max / min monthly SD"])
log_tests.round(2).to_csv(RESULTS / "log_justification.csv")
key["boxcox_lambda_weekly_train"] = round(float(stats.boxcox(w_tr["pm25"])[1]), 3)
key["skew_raw"], key["skew_log"] = round(float(stats.skew(pm)), 2), round(float(stats.skew(lg)), 2)
key["corr_mean_sd_raw"], key["corr_mean_sd_log"] = [round(float(x), 2) for x in log_tests.iloc[1]]
key["sd_ratio_raw"], key["sd_ratio_log"] = [round(float(x), 1) for x in log_tests.iloc[2]]
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
for ax, (m, s, t) in zip(axes, [(bm.mean_raw, bm.sd_raw, "Raw PM2.5"), (bm.mean_log, bm.sd_log, "log PM2.5")]):
    ax.scatter(m, s, color=BLUE, s=40)
    for mo, (xx, yy) in enumerate(zip(m, s), 1):
        ax.annotate(month_names[mo - 1], (xx, yy), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("monthly mean"); ax.set_ylabel("monthly SD"); ax.set_title(t)
savefig(fig, "02b_mean_sd_log"); plt.show()
log_tests.round(2)''')

md("""The SD of raw PM2.5 moves almost one-for-one with its mean across months (correlation ≈ 0.95); after the log this link disappears.
Box-Cox with λ close to 0 confirms that the log is the right member of the family (Lecture 06). **All models below work on log PM2.5.**""")

md("""## 4. Decomposition: STL on 2015-2019 (Lectures 06-07)
Weekly log PM2.5 = trend + seasonal (period 52) + remainder. Seasonal strength (Hyndman & Athanasopoulos, FPP3) is
$F_S = \\max\\{0,\\; 1 - \\mathrm{Var}(R)/\\mathrm{Var}(S+R)\\}$, between 0 (no seasonality) and 1 (everything is seasonal).
The same formula with the trend, $F_T = \\max\\{0, 1-\\mathrm{Var}(R)/\\mathrm{Var}(T+R)\\}$, measures trend strength.
STL is fitted on **2015-2019 only**: the 2020 lockdown weeks would otherwise drag the end of the trend down.""")
code('''stl = STL(w_mod["log_pm25"], period=52, robust=True).fit()
S, T, R = stl.seasonal, stl.trend, stl.resid
key["seasonal_strength"] = round(float(max(0, 1 - R.var() / (S + R).var())), 2)
key["trend_strength"] = round(float(max(0, 1 - R.var() / (T + R).var())), 2)
key["stl_seasonal_range_log"] = round(float(S.max() - S.min()), 2)
key["stl_seasonal_ratio"] = round(float(np.exp(S.max() - S.min())), 1)
pd.DataFrame({"observed": stl.observed, "trend": T, "seasonal": S, "resid": R}).to_csv(RESULTS / "stl_components.csv")
fig, axes = plt.subplots(4, 1, figsize=(10, 7), sharex=True)
for ax, (n, s) in zip(axes, [("Observed (log PM2.5)", stl.observed), ("Trend", T), ("Seasonal", S), ("Remainder", R)]):
    ax.plot(s.index, s, color=BLUE, lw=1.2); ax.set_ylabel(n, fontsize=8)
savefig(fig, "03_stl_decomposition"); plt.show()
print({k: key[k] for k in ("seasonal_strength", "trend_strength", "stl_seasonal_ratio")})''')

md("""### The level is drifting down
Annual means of PM2.5 (and of the log, after removing the day-of-year average) fall over 2016-2019. We will not model this explicitly
(a constant level is used) and will see in the results that it makes the models over-predict 2019.""")
code('''ann = pd.DataFrame({"mean PM2.5 (µg/m³)": d_mod["pm25"].groupby(d_mod.index.year).mean().round(1)})
ann["% vs 2016"] = (100 * (ann.iloc[:, 0] / ann.loc[2016].iloc[0] - 1)).round(1)
ann.to_csv(RESULTS / "annual_means.csv")
key["annual_means"] = ann.iloc[:, 0].to_dict()
key["decline_2016_2019_pct"] = float(ann.loc[2019, "% vs 2016"])
ann''')

md("""## 5. Is the series stationary? ACF, PACF, ADF, KPSS (Lectures 08-12) - training years 2015-2018
We look at the series first (ACF/PACF), then run the formal tests.
* **ADF** - null hypothesis: the series has a **unit root** (it wanders like a random walk). Small p rejects the null.
* **KPSS** - null hypothesis: the series is **stationary around a constant mean**. Small p rejects the null.
They have opposite nulls, so we want ADF to reject and KPSS not to reject. (Lecture 12.)""")
code('''y_tr = w_tr["log_pm25"]; d52 = y_tr.diff(52).dropna()
LAGS = 60
acf_df = pd.DataFrame({"log PM2.5": acf(y_tr, nlags=LAGS), "52-week difference": acf(d52, nlags=LAGS)})
pacf_df = pd.DataFrame({"log PM2.5": pacf(y_tr, nlags=LAGS, method="ywm"), "52-week difference": pacf(d52, nlags=LAGS, method="ywm")})
acf_df.to_csv(RESULTS / "acf_weekly_train.csv"); pacf_df.to_csv(RESULTS / "pacf_weekly_train.csv")
key["acf_lag1"], key["acf_lag26"], key["acf_lag52"] = [round(float(acf_df["log PM2.5"].iloc[k]), 2) for k in (1, 26, 52)]
key["acf_d52_lag1"], key["acf_d52_lag52"] = [round(float(acf_df["52-week difference"].iloc[k]), 2) for k in (1, 52)]
key["pacf_lag1"], key["pacf_lag2"], key["pacf_lag3"] = [round(float(pacf_df["log PM2.5"].iloc[k]), 2) for k in (1, 2, 3)]
fig, axes = plt.subplots(2, 2, figsize=(11, 6))
for j, (s, name) in enumerate([(y_tr, "log PM2.5"), (d52, "52-week difference of log PM2.5")]):
    plot_acf(s, lags=LAGS, ax=axes[0, j], marker=None, color=BLUE, vlines_kwargs={"colors": BLUE}, title=f"ACF: {name}")
    plot_pacf(s, lags=LAGS, ax=axes[1, j], method="ywm", marker=None, color=BLUE, vlines_kwargs={"colors": BLUE}, title=f"PACF: {name}")
fig.tight_layout(); savefig(fig, "06_acf_pacf"); plt.show()
print("ACF of log PM2.5 at lags 1, 26, 52:", key["acf_lag1"], key["acf_lag26"], key["acf_lag52"])''')

md("""**Reading the plots.** The ACF of log PM2.5 decays slowly, turns negative near lag 26 (half a year: summer vs winter) and returns to a positive
peak near lag 52. That *yearly wave* is the footprint of seasonality, so the mean of the series depends on the time of year.
A weekly series with a fixed yearly pattern is therefore **not stationary in the mean**, even if it has no random-walk behaviour.
The PACF has large spikes at lags 1-2 only, which suggests short-run AR(1-2) dynamics on top of the seasonal pattern.""")
code('''tests = {"log PM2.5": y_tr, "52-week difference of log PM2.5": d52}
st = stationarity_table(tests)
st_out = st[["n", "adf_stat", "adf_p", "kpss_stat", "kpss_p", "verdict"]].copy()
st_out["kpss_crit_5pct"] = 0.463
st_out.to_csv(RESULTS / "stationarity_train.csv")
key["adf_p_log"], key["kpss_stat_log"] = float(st.loc["log PM2.5", "adf_p"]), float(st.loc["log PM2.5", "kpss_stat"])
key["adf_p_d52"], key["kpss_stat_d52"] = float(st.loc["52-week difference of log PM2.5", "adf_p"]), float(st.loc["52-week difference of log PM2.5", "kpss_stat"])
st_out''')

md("""**Reading the table.** ADF rejects a unit root for log PM2.5 (so there is no random-walk behaviour at lag 1), and KPSS does not reject
level-stationarity. These tests look only for a *unit root* or a *constant mean over the whole sample*; they are not designed to detect a
mean that moves up and down regularly through the year. **The ACF is therefore the more informative tool here**: it shows the
yearly cycle, which is why we model the seasonal pattern explicitly.

After a **seasonal difference** $\\nabla_{52}x_t = x_t - x_{t-52}$ (Lecture 20) the yearly wave is gone from the ACF (right-hand panels) and both
tests pass again. A further ordinary difference would *over-difference* (lag-1 ACF near −0.5), so we use $d=0$ with the seasonal difference $D=1$
as the SARIMA candidate, and compare with modelling the seasonal pattern directly (harmonic regression) in notebook 04.""")

md("""## 6. Data note: the number of monitoring stations changed
The Delhi series is the average over the monitoring stations that reported each day. The count changed from 10 and 8 stations (2015-16) to 37
(2018-19), so part of the 2016-19 decline may reflect a different station mix. We do not analyse this further; it is listed as a limitation.""")
code('''stn = pd.read_csv(RAW / "station_day.csv", parse_dates=["Date"]); meta = pd.read_csv(RAW / "stations.csv")
x = stn[stn.StationId.isin(meta.loc[meta.City == "Delhi", "StationId"])].dropna(subset=["PM2.5"])
n_st = x.groupby(x["Date"].dt.year)["StationId"].nunique()
key["stations_by_year"] = {int(k): int(v) for k, v in n_st.loc[2015:2019].items()}
n_st.loc[2015:2019]''')

code('''(RESULTS / "key_numbers_eda.json").write_text(json.dumps(key, indent=2))
key''')

nb = new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
nbformat.write(nb, "notebooks/02_eda.ipynb")
print("wrote notebooks/02_eda.ipynb", len(cells), "cells")
