# 02 Notebooks 02 and 03: code and printed output

## notebooks/02_eda.ipynb

### [md 0]
# 02 · Exploratory analysis & stationarity
**Scope note.** Descriptive EDA (sections 1-5, 7) uses the full 2015-01 to 2020-07 sample, which includes the 2020
lockdown months. Every statistic that feeds a modelling decision (seasonal strength, Box-Cox, d and D) is reported
on the **training years 2015-2018** as the headline, with the full-sample value alongside.

Questions:
1. How strong is the seasonal cycle (winter smog vs monsoon clearing)?
2. How does PM2.5 move with NO₂, SO₂, humidity and wind?
3. Which transformations make the series stationary (needed for VAR/Granger and to pick SARIMAX d, D)?

### [code 1]
```python
import sys
sys.path.append("..")

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.seasonal import STL
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from src.data import PROCESSED, RAW, RESULTS, SEASONS, OTHER_SEASON
from src.aqi import pm25_category, CATEGORIES
from src.tsa import stationarity_table
from src.plots import (use_style, savefig, shade_aqi_bands, SEASON_COLORS, LABELS,
                       BLUE, ORANGE, AQUA, NEUTRAL, INK, INK_2, MUTED, SURFACE)

use_style()
daily = pd.read_csv(PROCESSED / "delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
weekly = pd.read_csv(PROCESSED / "delhi_weekly.csv", index_col="Date", parse_dates=True)
key = {}  # headline numbers for the slides
```

### [md 2]
## 1. PM2.5 over time, against CPCB AQI bands

### [code 3]
```python
fig, ax = plt.subplots(figsize=(11, 4))
ymax = 450
shade_aqi_bands(ax, ymax)
ax.plot(daily.index, daily["pm25"], color=BLUE, lw=0.6, alpha=0.45, label="Daily mean")
ax.plot(daily.index, daily["pm25"].rolling(30, center=True).mean(), color=BLUE, lw=2, label="30-day rolling mean")
ax.set_ylim(0, ymax)
ax.set_xlim(daily.index.min(), daily.index.max())
ax.set_ylabel(LABELS["pm25"])
ax.set_title("Delhi PM2.5, 2015–2020: winter peaks every year, monsoon troughs in between")
ax.legend(loc="upper left", ncols=2)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
clipped = (daily["pm25"] > ymax).sum()
ax.annotate(f"{clipped} days above {ymax} µg/m³ not shown (max {daily['pm25'].max():.0f})",
            xy=(1, -0.12), xycoords="axes fraction", ha="right", fontsize=8, color=MUTED)
savefig(fig, "01_pm25_timeseries")
plt.show()
```

output:
```
findfont: Failed to find font weight semibold for DejaVu Sans, now using 700.
<Figure size 1210x440 with 1 Axes>
```

### [code 4]
```python
cat_share = pm25_category(daily["pm25"].to_numpy()).value_counts(normalize=True).reindex(CATEGORIES) * 100
key["pct_days_poor_or_worse"] = round(float(cat_share[["Poor", "Very Poor", "Severe"]].sum()), 1)
cat_share.round(1).rename("% of days").to_frame()
```

output:
```
              % of days
Good                5.0
Satisfactory       22.5
Moderate           20.3
Poor               14.7
Very Poor          30.2
Severe              7.3
```

### [md 5]
## 2. Seasonality: month-by-month distribution (headline figure)

### [code 6]
```python
month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
by_month = [daily.loc[daily.index.month == m, "pm25"].dropna() for m in range(1, 13)]
month_season = {m: name for name, months in SEASONS.items() for m in months}
colours = [SEASON_COLORS[month_season.get(m, OTHER_SEASON)] for m in range(1, 13)]

monthly_median = daily["pm25"].groupby(daily.index.month).median()
key_ratio = monthly_median[11] / monthly_median[8]

fig, ax = plt.subplots(figsize=(10, 4.2))
bp = ax.boxplot(by_month, tick_labels=month_names, patch_artist=True, widths=0.6,
                showfliers=True, medianprops=dict(color=INK, lw=1.5),
                whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
                flierprops=dict(marker="o", markersize=2.5, markerfacecolor=MUTED, markeredgecolor="none", alpha=0.5))
for box, c in zip(bp["boxes"], colours):
    box.set(facecolor=c, edgecolor=SURFACE, linewidth=2, alpha=0.9)
ax.set_ylabel(LABELS["pm25"])
ax.set_title(f"PM2.5 by month: November median is {key_ratio:.1f}× August")
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in SEASON_COLORS.values()]
limit = ax.axhline(60, color=INK_2, lw=0.8)
ax.legend([*handles, limit], [*SEASON_COLORS.keys(), "Upper limit of CPCB 'Satisfactory' (60)"],
          loc="upper center", ncols=2)
savefig(fig, "02_monthly_boxplot")
plt.show()
```

output:
```
<Figure size 1100x462 with 1 Axes>
```

### [code 7]
```python
season_stats = daily.groupby("season")[["pm25", "wind", "rh"]].agg(["mean", "median"]).round(1)
winter, monsoon = "Winter (Nov–Jan)", "Monsoon (Jul–Sep)"
key["winter_mean_pm25"] = float(season_stats.loc[winter, ("pm25", "mean")])
key["monsoon_mean_pm25"] = float(season_stats.loc[monsoon, ("pm25", "mean")])
key["winter_to_monsoon_ratio"] = round(key["winter_mean_pm25"] / key["monsoon_mean_pm25"], 2)
monthly_median = daily["pm25"].groupby(daily.index.month).median()
key["nov_to_aug_median_ratio"] = round(float(monthly_median[11] / monthly_median[8]), 2)
season_stats.to_csv(RESULTS / "season_stats.csv")
season_stats
```

output:
```
                    pm25        wind           rh       
                    mean median mean median  mean median
season                                                  
Monsoon (Jul–Sep)   48.1   46.0  9.0    8.4  78.0   80.0
Other months       102.5   93.9  9.9    9.3  52.2   53.0
Winter (Nov–Jan)   213.3  201.4  8.6    8.1  68.6   69.0
```

### [md 8]
Winter averages **~4.4×** the monsoon PM2.5. In ERA5, winds are only modestly calmer in Oct–Dec (~8 km/h vs ~10 km/h
in Mar–Jun). The rest of the winter peak comes from things we don't measure here: a shallow mixing layer and
temperature inversions, stubble burning and heating emissions. The monsoon is the most humid season *and* the
cleanest, because rain washes particles out (wet deposition).

### [md 9]
## 3. STL decomposition (weekly log PM2.5, period = 52)

### [code 10]
```python
stl = STL(weekly["log_pm25"], period=52, robust=True).fit()
fig, axes = plt.subplots(4, 1, figsize=(10, 7), sharex=True)
parts = [("Observed (log PM2.5)", stl.observed), ("Trend", stl.trend),
         ("Seasonal (52-week)", stl.seasonal), ("Residual", stl.resid)]
for ax, (name, series) in zip(axes, parts):
    if name == "Residual":
        ax.vlines(series.index, 0, series, color=BLUE, lw=1)
    else:
        ax.plot(series.index, series, color=BLUE)
    ax.set_ylabel(name, rotation=0, ha="right", va="center")
axes[0].set_title("STL decomposition: a strong annual cycle; the trend falls from 2019 (incl. 2020 lockdown)")
fig.align_ylabels(axes)
savefig(fig, "03_stl_decomposition")
plt.show()

def stl_strengths(s):
    f = STL(s, period=52, robust=True).fit()
    v = np.var(f.resid)
    return (round(float(max(0, 1 - v / np.var(f.seasonal + f.resid))), 2),
            round(float(max(0, 1 - v / np.var(f.trend + f.resid))), 2))

key["seasonal_strength_full"], key["trend_strength_full"] = stl_strengths(weekly["log_pm25"])
key["seasonal_strength"], key["trend_strength"] = stl_strengths(weekly.loc[:"2018-12-31", "log_pm25"])  # headline: training years
print("Full sample  : F_S =", key["seasonal_strength_full"], "| F_T =", key["trend_strength_full"])
print("Training 2015-18 (headline): F_S =", key["seasonal_strength"], "| F_T =", key["trend_strength"])
```

output:
```
<Figure size 1100x770 with 4 Axes>Full sample  : F_S = 0.89 | F_T = 0.34
Training 2015-18 (headline): F_S = 0.9 | F_T = 0.09
```

### [md 11]
Seasonal strength $F_S = 1 - \mathrm{Var}(R)/\mathrm{Var}(S+R)$ is close to 1 (headline value on the 2015-2018 training weeks; the full-sample value is
shown above and is almost identical), so seasonality dominates.
This is why we use a **seasonal** ARIMA with s = 52.

### [md 12]
## 4. How PM2.5 moves with pollutants and weather

### [code 13]
```python
cols = ["pm25", "no2", "so2", "rh", "wind", "temp", "precip"]
corr = daily[cols].corr(method="spearman")
names = [LABELS[c].split(" (")[0] for c in cols]

fig, ax = plt.subplots(figsize=(6.4, 5.2))
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(cols)), names, rotation=40, ha="right")
ax.set_yticks(range(len(cols)), names)
ax.grid(False)
for i in range(len(cols)):
    for j in range(len(cols)):
        v = corr.iloc[i, j]
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                color="white" if abs(v) > 0.55 else INK)
for s in ax.spines.values():
    s.set_visible(False)
fig.colorbar(im, ax=ax, shrink=0.8, label="Spearman ρ")
ax.set_title("Spearman correlation (daily)")
savefig(fig, "04_correlation_heatmap")
plt.show()
key["spearman_pm25_wind"] = round(float(corr.loc["pm25", "wind"]), 2)
key["spearman_pm25_rh"] = round(float(corr.loc["pm25", "rh"]), 2)
```

output:
```
<Figure size 704x572 with 2 Axes>
```

### [code 14]
```python
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for ax, x in zip(axes, ["wind", "rh"]):
    for season, c in SEASON_COLORS.items():
        d = daily[daily["season"] == season]
        ax.scatter(d[x], d["pm25"], s=9, color=c, alpha=0.55, edgecolors="none", label=season)
    bins = pd.qcut(daily[x], 12)
    med = daily.groupby(bins, observed=True).agg(x=(x, "median"), y=("pm25", "median"))
    ax.plot(med["x"], med["y"], color=INK, lw=2, label="Binned median")
    ax.set_xlabel(LABELS[x])
    ax.set_yscale("log")
axes[0].set_ylabel(LABELS["pm25"] + ", log scale")
axes[0].set_title("Higher wind → cleaner air, in every season")
axes[1].set_title("Humidity: linked to cleaner air only in the monsoon")
fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", ncols=4, bbox_to_anchor=(0.5, 1.07))
savefig(fig, "05_pm25_vs_weather")
plt.show()
```

output:
```
<Figure size 1210x462 with 2 Axes>
```

### [md 15]
Pooled correlations mix the seasons together, so we check them **within each season**:

### [code 16]
```python
within = daily.groupby("season").apply(lambda g: pd.Series({
    "ρ(PM2.5, wind)": g["pm25"].corr(g["wind"], method="spearman"),
    "ρ(PM2.5, RH)": g["pm25"].corr(g["rh"], method="spearman"),
    "days": len(g),
})).round(2)
within.to_csv(RESULTS / "within_season_correlation.csv")
within
```

output:
```
                   ρ(PM2.5, wind)  ρ(PM2.5, RH)    days
season                                                 
Monsoon (Jul–Sep)           -0.39         -0.37   461.0
Other months                -0.30         -0.02  1057.0
Winter (Nov–Jan)            -0.47         -0.02   491.0
```

### [md 17]
* **Wind** is negatively correlated with PM2.5 in *every* season (strongest in winter). More wind means more
  dilution.
* **Humidity** is negatively correlated only in the **monsoon** (rain washout). In winter it is ≈ 0.
* These are correlations, not causes. Notebook 03 tests whether weather *predicts* PM2.5 (Granger).

### [md 18]
## 5. Autocorrelation

### [code 19]
```python
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
plot_acf(daily["log_pm25"].dropna(), lags=400, ax=axes[0], marker=None, color=BLUE,
         vlines_kwargs={"colors": BLUE, "lw": 0.6}, title="ACF, daily log PM2.5 (400 lags)")
plot_pacf(daily["log_pm25"].dropna(), lags=30, ax=axes[1], method="ywm", color=BLUE,
          vlines_kwargs={"colors": BLUE}, title="PACF, daily log PM2.5 (30 lags)")
for ax in axes:
    ax.set_xlabel("Lag (days)")
    for coll in ax.collections:
        coll.set_facecolor(NEUTRAL)
        coll.set_alpha(0.35)
axes[0].axvline(365, color=ORANGE, lw=1)
axes[0].text(368, 0.75, "1 year", color=ORANGE, fontsize=8)
savefig(fig, "06_acf_pacf")
plt.show()
```

output:
```
<Figure size 1210x396 with 2 Axes>
```

### [md 20]
The ACF decays slowly, dips negative at about 6 months and rises again near lag 365. This is the annual
cycle. The PACF cuts off after a few lags, so short-run dynamics look AR(1–2)-like.

### [md 21]
## 6. Stationarity tests: ADF + KPSS
* **ADF**, H0: unit root (non-stationary). Small p means stationary.
* **KPSS**, H0: stationary. Small p means non-stationary.

The two tests have opposite null hypotheses, so running both gives a more reliable verdict.

### [code 22]
```python
log_w = weekly["log_pm25"]
tests = {
    "Daily PM2.5 (raw)": daily["pm25"],
    "Daily log PM2.5": daily["log_pm25"],
    "Daily Δ log PM2.5": daily["log_pm25"].diff(),
    "Daily wind speed": daily["wind"],
    "Daily Δ wind speed": daily["wind"].diff(),
    "Daily rel. humidity": daily["rh"],
    "Daily Δ rel. humidity": daily["rh"].diff(),
    "Weekly log PM2.5": log_w,
    "Weekly Δ log PM2.5 (d=1)": log_w.diff(),
    "Weekly Δ₅₂ log PM2.5 (D=1)": log_w.diff(52),
    "Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1)": log_w.diff(52).diff(),
}
stationarity = stationarity_table(tests)
stationarity.to_csv(RESULTS / "stationarity.csv")
stationarity
```

output:
```
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerR
...[truncated]
```

### [md 23]
**Reading the table** (statsmodels caps the KPSS p-value at 0.1, so 0.1 means "≥ 0.1"):
* **No unit root in PM2.5.** Daily and weekly log PM2.5 *levels* pass both tests, i.e. the evidence is consistent with
  stationarity under the tests' assumptions (it is not a proof). Note that KPSS on the raw level is dominated by the large
  seasonal cycle; the slow downward drift only shows once the cycle is removed (section 6c). The annual cycle is a
  repeating, mean-reverting pattern, not a random walk.
* **Wind (daily)** is borderline: ADF rejects a unit root but KPSS rejects stationarity at 5%.
  Its first difference is clearly stationary.
* **Weekly series, full sample:** the seasonal difference Δ₅₂ gives KPSS p ≈ 0.02 (a rejection at 5%).
  That sample includes the 2019–20 decline (and the lockdown), which would also leak test-period information
  into model choices. Section 6b therefore repeats the weekly tests on the **training sample only (2015–2018)**.
* **Stationary does not mean ready for Granger.** Wind, humidity and PM2.5 all follow the same annual
  calendar. Unless we remove that shared seasonal cycle first (notebook 03), Granger tests would pick up
  "the season" instead of a real lead-lag relationship.

### [md 24]
## 6b. Stationarity on the training sample only (2015–2018, weekly)
Model-selection decisions (d, D) must not use the test year, so we repeat the weekly tests on 2015–2018.
`lag-1 ACF` guards against over-differencing: a lag-1 autocorrelation near −0.5 means the series was differenced
too much.

### [code 25]
```python
from statsmodels.tsa.stattools import acf
lw_tr = weekly.loc[:"2018-12-31", "log_pm25"]
tests_tr = {
    "Weekly log PM2.5 (train)": lw_tr,
    "Weekly Δ log PM2.5 (d=1)": lw_tr.diff(),
    "Weekly Δ₅₂ log PM2.5 (D=1)": lw_tr.diff(52),
    "Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1)": lw_tr.diff(52).diff(),
}
st_tr = stationarity_table(tests_tr)
st_tr["lag1_acf"] = [round(float(acf(s.dropna(), nlags=1)[1]), 2) for s in tests_tr.values()]
st_tr.to_csv(RESULTS / "stationarity_train.csv")
st_tr
```

output:
```
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerResult. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  adf_stat, adf_p, adf_lags, _, adf_crit, _ = adfuller(s, autolag="AIC")
/home/kushagrasingh/Music/time_anal_proj/notebooks/../src/tsa.py:12: FutureWarning: adfuller currently returns a plain tuple whose length depends on the store and autolag arguments. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an ADFullerR
...[truncated]
```

### [md 26]
**Decision:** on the training sample the log level **and** the seasonal difference Δ₅₂ both pass ADF and KPSS, so
**d = 0**. The extra first difference over-differences (lag-1 ACF ≈ −0.46, near the −0.5 warning), so it is
dropped. Whether to take the seasonal difference (**D = 0 or 1**) is decided by rolling-origin validation in
notebook 04 (never on the evaluation year), not by AIC (AIC is not comparable across different D).

### [md 27]
## 7. Why the log transform? Variance and volatility tests
If the spread of PM2.5 grows with its level (as pollution data usually does), a log transform makes the
variance roughly constant, which the SARIMAX and VAR assumptions need.

### [code 28]
```python
from scipy import stats
from statsmodels.stats.diagnostic import het_arch

pm = daily["pm25"].dropna()
lg = np.log(pm)
by_month = pd.DataFrame({
    "mean": pm.groupby(pm.index.month).mean(),
    "sd_raw": pm.groupby(pm.index.month).std(),
    "sd_log": lg.groupby(lg.index.month).std(),
})
groups_raw = [g.to_numpy() for _, g in pm.groupby(pm.index.month)]
groups_log = [g.to_numpy() for _, g in lg.groupby(lg.index.month)]
lev_raw, lev_log = stats.levene(*groups_raw, center="median"), stats.levene(*groups_log, center="median")
arch_raw, arch_log = het_arch(pm.diff().dropna() - pm.diff().mean(), nlags=7), het_arch(lg.diff().dropna() - lg.diff().mean(), nlags=7)
log_tests = pd.DataFrame({
    "raw PM2.5": [stats.skew(pm), np.corrcoef(by_month["mean"], by_month["sd_raw"])[0, 1],
                  by_month["sd_raw"].max() / by_month["sd_raw"].min(), lev_raw.statistic, lev_raw.pvalue,
                  arch_raw[0], arch_raw[1]],
    "log PM2.5": [stats.skew(lg), np.corrcoef(by_month["mean"], by_month["sd_log"])[0, 1],
                  by_month["sd_log"].max() / by_month["sd_log"].min(), lev_log.statistic, lev_log.pvalue,
                  arch_log[0], arch_log[1]],
}, index=["Skewness", "corr(monthly mean, monthly SD)", "Max / min monthly SD", "Levene F (equal variance across months)",
          "Levene p-value", "ARCH-LM statistic (7 lags, on daily change)", "ARCH-LM p-value"])
log_tests.to_csv(RESULTS / "log_justification.csv")
by_month.to_csv(RESULTS / "monthly_mean_sd.csv")
key["boxcox_lambda_daily"] = round(float(stats.boxcox(pm)[1]), 3)
key["boxcox_lambda_weekly"] = round(float(stats.boxcox(weekly["pm25"])[1]), 3)
key["boxcox_lambda_daily_train"] = round(float(stats.boxcox(pm.loc[:"2018-12-31"])[1]), 3)
key["boxcox_lambda_weekly_train"] = round(float(stats.boxcox(weekly.loc[:"2018-12-31", "pm25"])[1]), 3)
print("Box-Cox lambda (0 means log):", key["boxcox_lambda_daily"], "daily,", key["boxcox_lambda_weekly"], "weekly")
log_tests.round(4)
```

output:
```
/home/kushagrasingh/Music/time_anal_proj/.venv/lib64/python3.12/site-packages/statsmodels/stats/diagnostic.py:997: FutureWarning: acorr_lm currently returns a plain tuple whose length depends on the store argument. In release 0.16 or after July 2027, whichever is later, the default behavior will switch to always returning an LMTestResult NamedTuple. Set result_object=True to switch now, or result_object=False to keep the current behavior and silence this warning.
  return acorr_lm(
Box-Cox lambda (0 means log): 0.045 daily, 0.028 weekly
                                             raw PM2.5  log PM2.5
Skewness                                        1.7041    -0.0772
corr(monthly mean, monthly SD)                  0.9512    -0.0666
Max / min monthly SD                            7.9030     1.3406
Levene F (equal variance across months)        49.6327     2.3989
Levene p-value                                  0.0000     0.0059
ARCH-LM statistic (7 lags, on daily change)   235.1849    36.4343
ARCH-LM p-value                                 0.0000     0.0000
```

### [md 29]
**Reading it:** the monthly SD of raw PM2.5 moves almost one-for-one with its mean (corr 0.95, SD varies 7.9×
between months). After the log the correlation is about zero and the spread varies only 1.3×. The Box-Cox
estimate λ ≈ 0.03–0.05 (full sample; ≈ 0.10 on the 2015–2018 training years) is close to 0, which is exactly the log transform. Some volatility clustering remains
(ARCH-LM still rejects), so the weekly forecast-model residuals are re-checked in notebook 04 (burn-in residuals removed).

### [md 30]
## 6c. Level drift: is there a slow decline hidden under the seasonal cycle?
The annual mean of PM2.5 fell from 138 (2016) to 108 µg/m³ (2019). KPSS on the raw level does not see it (the seasonal
cycle dominates the long-run variance), but it does once the cycle is removed. The climatology below is fitted on 2015-2018 only.

### [code 31]
```python
from statsmodels.tsa.stattools import kpss
from src.tsa import doy_anomaly
lg = daily["log_pm25"]
an_tr = doy_anomaly(lg, ref=lg.loc[:"2018-12-31"])           # climatology from the training years only
drift = pd.DataFrame({"mean PM2.5 (µg/m³)": daily["pm25"].groupby(daily.index.year).mean().round(1),
                      "mean log anomaly": an_tr.groupby(an_tr.index.year).mean().round(3)})
drift.to_csv(RESULTS / "annual_drift.csv")
import warnings as _w
with _w.catch_warnings():
    _w.simplefilter("ignore")
    key["kpss_stat_level_daily_log"] = round(float(kpss(lg.dropna(), regression="c", nlags="auto")[0]), 3)
    key["kpss_stat_anomaly_train_2015_2018"] = round(float(kpss(an_tr.loc[:"2018-12-31"].dropna(), regression="c", nlags="auto")[0]), 3)
    key["kpss_stat_anomaly_2015_2019"] = round(float(kpss(an_tr.loc[:"2019-12-31"].dropna(), regression="c", nlags="auto")[0]), 3)
print({k: v for k, v in key.items() if k.startswith("kpss_stat")}, "(5% critical value 0.463)")
drift
```

output:
```
{'kpss_stat_level_daily_log': 0.366, 'kpss_stat_anomaly_train_2015_2018': 0.896, 'kpss_stat_anomaly_2015_2019': 1.997} (5% critical value 0.463)
      mean PM2.5 (µg/m³)  mean log anomaly
Date                                      
2015               117.3             0.017
2016               138.5             0.103
2017               124.5            -0.043
2018               115.0            -0.077
2019               108.5            -0.185
2020                80.3            -0.496
```

### [md 32]
**Reading it:** the log anomaly falls from about +0.1 (2016) to about -0.15 (2019): a drift of roughly -20% to -25% over three
years, on top of a stable seasonal cycle. This is why the forecasting notebook must treat level/trend explicitly instead of
assuming a constant mean. Section 8 asks whether the drift is real air-quality improvement or a change in which monitors are counted.

### [md 33]
## 8. Is the 2016-2019 decline real? Station-network check
The Kaggle `city_day` Delhi value is the average over whatever stations reported that day. The number of reporting
stations grew sharply (see below), so a decline could partly be a change in the *mix* of stations. We test this with
`station_day.csv` (same Kaggle dataset, download command in the README): (1) confirm `city_day` = mean of stations,
(2) rebuild the annual series from a **fixed panel** of stations that reported in every year 2015-2019,
(3) remove the weather effect from the city series.

### [code 34]
```python
stn = pd.read_csv(RAW / "station_day.csv", parse_dates=["Date"])
meta = pd.read_csv(RAW / "stations.csv")
x = stn[stn.StationId.isin(meta.loc[meta.City == "Delhi", "StationId"])].dropna(subset=["PM2.5"]).copy()
x["year"] = x["Date"].dt.year
n_stations = x.groupby("year")["StationId"].nunique()
st_mean = x.groupby("Date")["PM2.5"].mean()
cmp_ = pd.concat([daily["pm25"], st_mean], axis=1, keys=["city_day", "station_mean"]).dropna()
key["city_vs_station_mean_corr"] = round(float(cmp_.corr().iloc[0, 1]), 4)
key["stations_by_year"] = {int(k): int(v) for k, v in n_stations.items()}
print("corr(city_day, mean of stations) =", key["city_vs_station_mean_corr"], "| stations reporting PM2.5 per year:", key["stations_by_year"])

days = x[x.year <= 2019].groupby(["StationId", "year"]).size().unstack(fill_value=0).reindex(columns=range(2015, 2020), fill_value=0)
panel = list(days.index[(days >= 60).all(axis=1)])
key["panel_stations"] = panel
print("fixed panel (>= 60 PM2.5 days in every year 2015-2019):", panel)

def annual_anomaly(df, min_stn=3):
    g = df.groupby("Date")["PM2.5"].agg(["mean", "count"])
    g = g[g["count"] >= min_stn]
    lg_ = np.log(g["mean"]).asfreq("D").interpolate(limit=3).dropna()
    an = doy_anomaly(lg_, ref=lg_.loc["2015":"2019"])
    return an.groupby(an.index.year).mean(), g["mean"].groupby(g.index.year).mean(), g["mean"].groupby(g.index.year).size()

a_all, m_all, _ = annual_anomaly(x)
a_pan, m_pan, d_pan = annual_anomaly(x[x.StationId.isin(panel)])

# weather-adjusted city series: regress log-PM2.5 anomaly on wind/rh/temp anomalies, 2015-2019, then average residuals by year
ref = slice("2015", "2019")
A = pd.DataFrame({c: doy_anomaly(daily[c].loc[ref]) for c in ["wind", "rh", "temp"]})
A["y"] = doy_anomaly(daily["log_pm25"].loc[ref]); A = A.dropna()
import statsmodels.api as sm
fit = sm.OLS(A["y"], sm.add_constant(A[["wind", "rh", "temp"]])).fit()
a_wx = fit.resid.groupby(fit.resid.index.year).mean()

station_check = pd.DataFrame({"stations": n_stations, "all_mean_pm25": m_all.round(1), "all_log_anom": a_all.round(3),
                              "panel_mean_pm25": m_pan.round(1), "panel_days": d_pan, "panel_log_anom": a_pan.round(3),
                              "weather_adj_log_anom": a_wx.round(3)}).loc[2015:2019]
station_check.to_csv(RESULTS / "station_check.csv")
chg = lambda s: round(float((np.exp(s.loc[2019] - s.loc[2016]) - 1) * 100), 1)
key["decline_2016_2019_pct"] = {"all_stations": chg(a_all), "fixed_panel": chg(a_pan), "weather_adjusted": chg(a_wx)}
print(key["decline_2016_2019_pct"])
station_check
```

output:
```
corr(city_day, mean of stations) = 0.995 | stations reporting PM2.5 per year: {2015: 10, 2016: 8, 2017: 17, 2018: 37, 2019: 37, 2020: 36}
fixed panel (>= 60 PM2.5 days in every year 2015-2019): ['DL002', 'DL013', 'DL019', 'DL021', 'DL028', 'DL031']
{'all_stations': -24.7, 'fixed_panel': -19.7, 'weather_adjusted': -17.7}
      stations  all_mean_pm25  all_log_anom  panel_mean_pm25  panel_days  \
2015        10          110.0         0.073            111.7         262   
2016         8          138.3         0.121            135.2         342   
2017        17          149.4         0.051            190.0         125   
2018        37          114.7        -0.054            121.6         365   
2019        37          108.2        -0.163            110.9         365   

      panel_log_anom  weather_adj_log_anom  
2015           0.040                 0.056  
2016           0.088                 0.085  
2017           0.020                -0.006  
2018           0.010                -0.026  
2019          -0.132                -0.110
```

### [code 35]
```python
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
axes[0].bar(n_stations.loc[2015:2019].index, n_stations.loc[2015:2019], color=NEUTRAL, width=0.6)
axes[0].set_title("Stations reporting PM2.5 in Delhi"); axes[0].set_ylabel("Stations")
for lab, s, c in [("All stations", a_all, BLUE), ("Fixed panel (6 stations)", a_pan, ORANGE), ("City series, weather-adjusted", a_wx, AQUA)]:
    axes[1].plot(s.loc[2015:2019].index, s.loc[2015:2019], marker="o", color=c, label=lab)
axes[1].axhline(0, color=INK_2, lw=0.8); axes[1].set_ylabel("Mean log-PM2.5 anomaly")
axes[1].set_title("Decline persists on a fixed station panel"); axes[1].legend(fontsize=8)
for ax in axes: ax.set_xticks(range(2015, 2020))
savefig(fig, "12_station_check"); plt.show()
```

output:
```
<Figure size 1210x418 with 2 Axes>
```

### [md 36]
**Reading it:** the city series equals the mean of the stations (corr 0.995), and the station count jumped from 8-10 (2015-16)
to 37 (2018-19), so a mix effect is *possible*. But the fixed panel of six long-running stations shows a decline of the
same sign and a similar size (see `decline_2016_2019_pct`: about -25% all stations, -20% fixed panel, -18% weather-adjusted), and so does the weather-adjusted city series. (The `all_mean_pm25` column averages only days with at least 3 reporting stations, so it is not directly comparable with the city-day annual means in section 6c; the log anomalies are the comparable quantity.)
So most of the decline is a **real drift in the level**, partly (not fully) confirmed by consistent monitors; the 2017 panel
is thin (about 125 days) and the panel is only six stations, so we do not claim a precise magnitude. Consequence for modelling:
the level cannot be treated as constant; notebook 04 compares constant, linear and random-walk level handling on validation years.

### [code 37]
```python
(RESULTS / "key_numbers_eda.json").write_text(json.dumps(key, indent=2))
key
```

output:
```
{'pct_days_poor_or_worse': 52.2,
 'winter_mean_pm25': 213.3,
 'monsoon_mean_pm25': 48.1,
 'winter_to_monsoon_ratio': 4.43,
 'nov_to_aug_median_ratio': 4.9,
 'seasonal_strength_full': 0.89,
 'trend_strength_full': 0.34,
 'seasonal_strength': 0.9,
 'trend_strength': 0.09,
 'spearman_pm25_wind': -0.24,
 'spearman_pm25_rh': -0.2,
 'boxcox_lambda_daily': 0.045,
 'boxcox_lambda_weekly': 0.028,
 'boxcox_lambda_daily_train': 0.097,
 'boxcox_lambda_weekly_train': 0.108,
 'kpss_stat_level_daily_log': 0.366,
 'kpss_stat_anomaly_train_2015_2018': 0.896,
 'kpss_stat_anomaly_2015_2019': 1.997,
 'city_vs_station_mean_corr': 0.995,
 'stations_by_year': {2015: 10,
  2016: 8,
  2017: 17,
  2018: 37,
  2019: 37,
  2020: 36},
 'panel_stations': ['DL002', 'DL013', 'DL019', 'DL021', 'DL028', 'DL031'],
 'decline_2016_2019_pct': {'all_stations': -24.7,
  'fixed_panel': -19.7,
  'weather_adjusted': -17.7}}
```


## notebooks/03_var_granger.ipynb

### [md 0]
# 03 · VAR model & Granger causality
**Question:** do wind speed and humidity *Granger-cause* PM2.5? In other words, does knowing past weather
improve the prediction of PM2.5 beyond what PM2.5's own past gives?

**Setup**
* Daily data, **2015-01-01 → 2019-12-31**. The 2020 COVID lockdown is left out because it is an
  emissions shock, not a weather effect.
* System: `wind`, `rh` and `pm25` (log). All three are **deseasonalised first**.
* Why deseasonalise? Wind, humidity and PM2.5 all follow the same calendar. Without removing that, Granger
  would mostly detect "it's winter" instead of a real lead-lag effect.
* Method: subtract each variable's smoothed day-of-year climatology (31-day circular window).
* Robustness check: repeat the analysis using plain first differences.

### [code 1]
```python
import sys
sys.path.append("..")

import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.api import VAR

from src.data import PROCESSED, RESULTS
from src.tsa import doy_climatology, doy_anomaly, doy365, week_index, stationarity_table, pairwise_granger
from src.plots import use_style, savefig, VAR_COLORS, BLUE, ORANGE, AQUA, INK, INK_2, MUTED, NEUTRAL, SURFACE

warnings.filterwarnings("ignore", category=FutureWarning)
use_style()
daily = pd.read_csv(PROCESSED / "delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
d = daily.loc[:"2019-12-31"]
key = {"var_sample": f"{d.index.min().date()} to {d.index.max().date()} ({len(d)} days)"}
NAMES = {"wind": "Wind", "rh": "Humidity", "pm25": "PM2.5"}
```

### [md 2]
## 1. Remove the seasonal cycle

### [code 3]
```python
anom = pd.DataFrame({
    "wind": doy_anomaly(d["wind"]),
    "rh": doy_anomaly(d["rh"]),
    "pm25": doy_anomaly(d["log_pm25"]),
})
assert anom.notna().all().all()

clim = doy_climatology(d["log_pm25"])
fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
axes[0].plot(d.index, d["log_pm25"], color=NEUTRAL, lw=0.8, label="Daily log PM2.5")
axes[0].plot(d.index, clim.reindex(doy365(d.index)).to_numpy(), color=BLUE, lw=2,
             label="Seasonal climatology (day-of-year mean)")
axes[0].set_title("Step 1: remove the shared seasonal cycle before testing causality")
axes[0].legend(loc="lower left", ncols=2)
axes[1].plot(anom.index, anom["pm25"], color=BLUE, lw=0.8)
axes[1].axhline(0, color=INK_2, lw=0.8)
axes[1].set_ylabel("Anomaly")
axes[1].set_title("PM2.5 anomaly = log PM2.5 − climatology (used in the VAR)")
axes[1].xaxis.set_major_locator(mdates.YearLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
savefig(fig, "07_deseasonalise")
plt.show()
```

output:
```
findfont: Failed to find font weight semibold for DejaVu Sans, now using 700.
<Figure size 1100x550 with 2 Axes>
```

### [code 4]
```python
anom_stationarity = stationarity_table({f"{NAMES[c]} anomaly": anom[c] for c in anom})
anom_stationarity.to_csv(RESULTS / "stationarity_anomalies.csv")
anom_stationarity
```

output:
```
                     n  adf_stat         adf_p  adf_lags  adf_crit_1%  \
series                                                                  
Wind anomaly      1826   -19.557  0.000000e+00         3       -3.434   
Humidity anomaly  1826   -12.558  2.140000e-23         3       -3.434   
PM2.5 anomaly     1826    -6.576  7.710000e-09        18       -3.434   

                  adf_crit_5%  adf_crit_10%  kpss_stat  kpss_p  \
series                                                           
Wind anomaly           -2.863        -2.568      1.048    0.01   
Humidity anomaly       -2.863        -2.568      0.222    0.10   
PM2.5 anomaly          -2.863        -2.568      2.035    0.01   

                                                    verdict  
series                                                       
Wind anomaly      Mixed (ADF says stationary, KPSS rejects)  
Humidity anomaly                                 Stationary  
PM2.5 anomaly     Mixed (ADF says stationary, KPSS rejects)
```

### [md 5]
ADF strongly rejects a unit root for all three anomaly series (statistics far below the 1% critical value
of about −3.4). KPSS still flags wind and PM2.5, because with n ≈ 1,800 it reacts to small slow drifts
(e.g. the PM2.5 decline in 2019). We therefore fit the VAR on the anomalies, and in Section 6 we re-run
everything on **first differences**, which pass both tests, to check the conclusion is the same.

### [md 6]
## 2. Lag-order selection

### [code 7]
```python
model = VAR(anom)
order = model.select_order(maxlags=14)
lag_table = pd.DataFrame({ic: [getattr(order, "ics")[ic][p] for p in range(15)] for ic in ["aic", "bic", "hqic", "fpe"]})
lag_table.index.name = "lag"
lag_table.round(4).to_csv(RESULTS / "var_lag_selection.csv")
print("Selected orders:", {k: int(v) for k, v in order.selected_orders.items()})
lag_table.style.highlight_min(axis=0, props="font-weight:bold; background-color:#cde2fb")
```

output:
```
Selected orders: {'aic': 4, 'bic': 2, 'hqic': 3, 'fpe': 4}
<pandas.io.formats.style.Styler at 0x7fbd8d5e9d00>
```

### [code 8]
```python
p = int(order.selected_orders["aic"])
res = model.fit(p)
whiteness = res.test_whiteness(nlags=p + 10)
key.update({
    "var_lag_aic": p, "var_lag_bic": int(order.selected_orders["bic"]),
    "var_stable": bool(res.is_stable()),
    "portmanteau_p": round(float(whiteness.pvalue), 3),
})
print(f"VAR({p}) — stable: {res.is_stable()} | Portmanteau test (H0: residuals white, {p + 10} lags): p = {whiteness.pvalue:.3f}")
```

output:
```
VAR(4) — stable: True | Portmanteau test (H0: residuals white, 14 lags): p = 0.168
```

### [md 9]
AIC picks **p = 4 days**, BIC picks 2 and HQIC picks 3. We use the AIC lag, and Section 6 checks the
result under the BIC lag too. The fitted VAR is **stable** and its residuals pass the multivariate
Portmanteau test (no autocorrelation left), so the model is adequate for inference.

### [md 10]
### Stability: companion-matrix eigenvalues must lie inside the unit circle

### [code 11]
```python
eig = 1 / res.roots
fig, ax = plt.subplots(figsize=(4.2, 4.2))
theta = np.linspace(0, 2 * np.pi, 400)
ax.plot(np.cos(theta), np.sin(theta), color=MUTED, lw=1)
ax.scatter(eig.real, eig.imag, s=40, color=BLUE, edgecolors=SURFACE, linewidths=2, zorder=3)
ax.set_aspect("equal")
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.set_title(f"VAR({p}) is stable: max |λ| = {np.abs(eig).max():.2f}")
ax.set_xlabel("Real")
ax.set_ylabel("Imaginary")
savefig(fig, "08_var_stability")
plt.show()
key["max_eigen_modulus"] = round(float(np.abs(eig).max()), 3)
```

output:
```
<Figure size 462x462 with 1 Axes>
```

### [md 12]
## 3. Granger causality tests (from the fitted VAR)
H0: all lagged coefficients of the *causing* variable in the *caused* variable's equation are zero.

### [code 13]
```python
def granger_rows(results, label):
    rows = []
    for causing, caused in [("wind", "pm25"), ("rh", "pm25"), (["wind", "rh"], "pm25"), ("pm25", "wind"), ("pm25", "rh")]:
        t = results.test_causality(caused, causing, kind="f")
        name = " + ".join(NAMES[c] for c in np.atleast_1d(causing))
        rows.append({
            "spec": label, "direction": f"{name} → {NAMES[caused]}",
            "F": round(t.test_statistic, 2), "df": f"({t.df[0]}, {t.df[1]})", "p_value": t.pvalue,
            "verdict (5%)": "Granger-causes" if t.pvalue < 0.05 else "No evidence",
        })
    return rows

granger = pd.DataFrame(granger_rows(res, f"Anomalies, VAR({p})"))
granger.to_csv(RESULTS / "granger_var.csv", index=False)
granger.style.format({"p_value": "{:.2e}"})
```

output:
```
<pandas.io.formats.style.Styler at 0x7fbd8d5eb290>
```

### [md 14]
**Result:** the direction is one-way. Weather → PM2.5 is highly significant (p ≪ 0.001).
PM2.5 → weather, the reverse direction, is **not** significant. That is the physically expected pattern:
pollution does not change the next day's wind, but wind does disperse pollution.

### [md 15]
### Pairwise Granger tests across lags 1–7 days

### [code 16]
```python
pairs = [("wind", "pm25"), ("rh", "pm25"), ("pm25", "wind"), ("pm25", "rh")]
pw = pairwise_granger(anom, pairs, maxlag=7)
pw.index = [f"{NAMES[a]} → {NAMES[b]}" for a, b in pairs]
pw.to_csv(RESULTS / "granger_pairwise_lags.csv")

score = -np.log10(pw.clip(lower=1e-30))
fig, ax = plt.subplots(figsize=(8.5, 3))
im = ax.imshow(score.clip(upper=10), cmap="Blues", vmin=0, vmax=10, aspect="auto")
ax.set_xticks(range(7), [str(c) for c in pw.columns])
ax.set_yticks(range(len(pw)), pw.index)
ax.set_xlabel("Lag (days)")
ax.grid(False)
for s in ax.spines.values():
    s.set_visible(False)
for i in range(pw.shape[0]):
    for j in range(pw.shape[1]):
        v = pw.iloc[i, j]
        txt = "<1e-10" if v < 1e-10 else (f"{v:.0e}" if v < 0.001 else f"{v:.3f}")
        ax.text(j, i, txt, ha="center", va="center", fontsize=8,
                color="white" if score.iloc[i, j] > 5 else INK, fontweight="bold" if v < 0.05 else "normal")
fig.colorbar(im, ax=ax, label="−log₁₀ p  (capped at 10)", shrink=0.9)
ax.set_title("Pairwise Granger p-values: weather → PM2.5 at every lag order; PM2.5 → humidity at none")
savefig(fig, "09_granger_pvalues")
plt.show()
```

output:
```
<Figure size 935x330 with 2 Axes>
```

### [md 17]
Bold means p < 0.05. In pairwise tests, PM2.5 → wind is weakly significant at short lags. Once humidity is
also in the model (the full VAR above), that disappears (p ≈ 0.13), so it is not robust.
Each column is a **joint** test that lags 1..k of the cause add nothing (k = column label); it does not say that each individual
lag k is significant. A possible reason for a short-lag PM2.5 → wind signal in the bivariate test is a shared multi-day
stagnation regime (shallow boundary layer, low wind) that is not measured here; we do not claim it as a physical effect.

### [md 18]
## 4. Impulse responses: how much does PM2.5 respond to a weather shock?
These are orthogonalised (Cholesky) IRFs with ordering wind → humidity → PM2.5, so weather is allowed to
affect PM2.5 on the same day. The response of log PM2.5 is converted to a **% change**.

### [code 19]
```python
H = 14
irf = res.irf(H)
idx = {c: i for i, c in enumerate(anom.columns)}
se = irf.stderr(orth=True)
shock_sd = np.sqrt(np.diag(res.sigma_u))

fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
irf_summary = {}
for ax, imp in zip(axes, ["wind", "rh"]):
    r = irf.orth_irfs[:, idx["pm25"], idx[imp]]
    s = se[:, idx["pm25"], idx[imp]]
    pct, lo, hi = [(np.exp(x) - 1) * 100 for x in (r, r - 1.96 * s, r + 1.96 * s)]
    h = np.arange(H + 1)
    c = VAR_COLORS[imp]
    ax.fill_between(h, lo, hi, color=c, alpha=0.18, lw=0, label="95% CI")
    ax.plot(h, pct, color=c, lw=2, marker="o", markersize=4, label="Response")
    ax.axhline(0, color=INK_2, lw=0.8)
    k = int(np.argmin(pct))
    ax.annotate(f"{pct[k]:.1f}% on day {k}", xy=(k, pct[k]), xytext=(k + 2.5, pct[k] - 1),
                fontsize=9, color=INK, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    unit = "km/h" if imp == "wind" else "% RH"
    ax.set_title(f"+1 SD {NAMES[imp].lower()} shock ({shock_sd[idx[imp]]:.1f} {unit}) → PM2.5")
    ax.set_xlabel("Days after shock")
    irf_summary[imp] = {"peak_pct": round(float(pct[k]), 1), "peak_day": k,
                        "shock_sd": round(float(shock_sd[idx[imp]]), 2), "unit": unit}
axes[0].set_ylabel("Change in PM2.5 (%)")
axes[0].legend(loc="lower right")
savefig(fig, "10_irf_weather_to_pm25")
plt.show()
key["irf"] = irf_summary
irf_summary
```

output:
```
<Figure size 1210x418 with 2 Axes>{'wind': {'peak_pct': -12.0, 'peak_day': 1, 'shock_sd': 2.54, 'unit': 'km/h'},
 'rh': {'peak_pct': -6.7, 'peak_day': 1, 'shock_sd': 5.43, 'unit': '% RH'}}
```

### [md 20]
## 5. Forecast-error variance decomposition of PM2.5
How much of the uncertainty in future PM2.5 comes from each variable's shocks?

### [code 21]
```python
fevd = pd.DataFrame(res.fevd(H).decomp[idx["pm25"]] * 100, columns=[NAMES[c] for c in anom.columns],
                    index=pd.RangeIndex(1, H + 1, name="horizon (days)"))
fevd.round(1).to_csv(RESULTS / "fevd_pm25.csv")

fig, ax = plt.subplots(figsize=(9, 3.4))
bottom = np.zeros(H)
for col, var in [("PM2.5", "pm25"), ("Wind", "wind"), ("Humidity", "rh")]:
    ax.bar(fevd.index, fevd[col], bottom=bottom, color=VAR_COLORS[var], edgecolor=SURFACE, linewidth=2,
           width=0.8, label=f"{col} shocks")
    bottom += fevd[col].to_numpy()
ax.set_ylim(0, 100)
ax.set_xlabel("Forecast horizon (days)")
ax.set_ylabel("Share of PM2.5 forecast\nerror variance (%)")
ax.set_xticks(fevd.index)
weather_share = fevd.loc[H, "Wind"] + fevd.loc[H, "Humidity"]
ax.set_title(f"Weather first ordering: weather shocks explain {weather_share:.0f}% by day {H} (≈6% if PM2.5 is ordered first, see §8)")
ax.legend(loc="upper center", ncols=3, bbox_to_anchor=(0.5, -0.22))
savefig(fig, "11_fevd_pm25")
plt.show()
key["fevd_weather_share_h14"] = round(float(weather_share), 1)
key["fevd_wind_h14"] = round(float(fevd.loc[H, "Wind"]), 1)
key["fevd_rh_h14"] = round(float(fevd.loc[H, "Humidity"]), 1)
fevd.loc[[1, 3, 7, 14]].round(1)
```

output:
```
<Figure size 990x374 with 1 Axes>                Wind  Humidity  PM2.5
horizon (days)                       
1               13.3       3.0   83.7
3               22.2       8.3   69.6
7               20.6       9.3   70.0
14              20.5       9.5   70.0
```

### [md 22]
## 6. Robustness checks
1. Same anomalies, with the **BIC** lag.
2. **First differences** instead of anomalies. These pass both ADF and KPSS (notebook 02), with the lag
   chosen by AIC.

### [code 23]
```python
res_bic = model.fit(int(order.selected_orders["bic"]))
diffs = pd.DataFrame({"wind": d["wind"].diff(), "rh": d["rh"].diff(), "pm25": d["log_pm25"].diff()}).dropna()
model_d = VAR(diffs)
p_d = int(model_d.select_order(maxlags=14).selected_orders["aic"])
res_d = model_d.fit(p_d)

robust = pd.DataFrame(
    granger_rows(res, f"Anomalies, VAR({p}) [AIC]")
    + granger_rows(res_bic, f"Anomalies, VAR({res_bic.k_ar}) [BIC]")
    + granger_rows(res_d, f"First differences, VAR({p_d}) [AIC]")
)
robust.to_csv(RESULTS / "granger_robustness.csv", index=False)
robust.pivot(index="direction", columns="spec", values="p_value").map(lambda v: f"{v:.1e}")
```

output:
```
spec                    Anomalies, VAR(2) [BIC] Anomalies, VAR(4) [AIC]  \
direction                                                                 
Humidity → PM2.5                        5.1e-13                 1.2e-11   
PM2.5 → Humidity                        5.9e-01                 6.2e-01   
PM2.5 → Wind                            1.5e-02                 1.2e-01   
Wind + Humidity → PM2.5                 4.4e-37                 2.8e-33   
Wind → PM2.5                            3.7e-32                 1.1e-29   

spec                    First differences, VAR(14) [AIC]  
direction                                                 
Humidity → PM2.5                                 1.5e-10  
PM2.5 → Humidity                                 2.8e-01  
PM2.5 → Wind                                     5.7e-01  
Wind + Humidity → PM2.5                          1.0e-27  
Wind → PM2.5                                     7.8e-25
```

### [md 24]
**Weather → PM2.5 is significant in every specification.** PM2.5 → humidity is never significant.
PM2.5 → wind is borderline only with the shortest (BIC) lag and vanishes otherwise.

### [md 25]
## 7. Stronger checks on the Granger result
The daily series have autocorrelated, changing-variance errors (the ARCH test in notebook 02 flagged this), which
can make ordinary F-test p-values look too small. We therefore re-test with **HAC (Newey-West) standard
errors** (robust to autocorrelation and changing variance), and we add **rain** as a control to see whether
humidity only stands in for rain.

### [code 26]
```python
import statsmodels.api as sm

P = p  # VAR lag order chosen above
rain = doy_anomaly(d["precip"])
dfa = anom.assign(rain=rain)


def lagmat(df, cols, lags):
    return pd.concat({f"{c}_l{k}": df[c].shift(k) for c in cols for k in range(1, lags + 1)}, axis=1)


def hac_granger(target, causes, controls):
    cols = [target, *controls]
    X = lagmat(dfa, cols, P)
    data = pd.concat([dfa[target], X], axis=1).dropna()
    fit = sm.OLS(data[target], sm.add_constant(data.drop(columns=target))).fit(cov_type="HAC", cov_kwds={"maxlags": 10})
    hyp = ", ".join(" = 0, ".join(f"{c}_l{k}" for k in range(1, P + 1)) + " = 0" for c in causes)
    w = fit.wald_test(", ".join(f"{c}_l{k} = 0" for c in causes for k in range(1, P + 1)), scalar=True)
    return float(w.statistic), float(w.pvalue)


rows = []
for spec, controls in [("PM2.5, wind, humidity", ["pm25", "wind", "rh"]), ("+ rain control", ["pm25", "wind", "rh", "rain"])]:
    for cause in ["wind", "rh"] + (["rain"] if "rain" in controls else []):
        stat, pv = hac_granger("pm25", [cause], controls)
        rows.append({"spec": spec, "direction": f"{NAMES.get(cause, 'Rain')} → PM2.5", "wald_chi2": round(stat, 1), "p_value": pv})
for cause in ["pm25"]:
    for target in ["wind", "rh"]:
        stat, pv = hac_granger(target, [cause], ["pm25", "wind", "rh"])
        rows.append({"spec": "PM2.5, wind, humidity", "direction": f"PM2.5 → {NAMES[target]}", "wald_chi2": round(stat, 1), "p_value": pv})
granger_hac = pd.DataFrame(rows)
granger_hac.to_csv(RESULTS / "granger_hac.csv", index=False)
granger_hac.style.format({"p_value": "{:.2e}"})
```

output:
```
<pandas.io.formats.style.Styler at 0x7fbd89305910>
```

### [md 27]
With robust errors, weather → PM2.5 is still overwhelmingly significant (wind p ≈ 1e-19; humidity p ≈ 3e-11, and 3e-8 once rain is a
control) and the reverse is not.
**Humidity stays significant after controlling for rain, and rain itself adds nothing** once wind and humidity are
in, so we do *not* claim the humidity effect is simply rain washout.
We quote p-values as "p < 10⁻¹⁰": beyond that, extra digits are not meaningful.

### [md 28]
### 7b. More robustness: temperature, a trend, a training-only climatology, season-specific effects, and lag order
Everything below uses the same manual HAC (Newey-West, 10 lags) Wald test as above, one equation at a time with P = 4 lags.

### [code 29]
```python
def design(frame, target, controls, P, trend=False, inter=None):
    cols = list(dict.fromkeys([target, *controls]))
    X = lagmat(frame, cols, P)
    if trend:
        X["trend"] = np.arange(len(frame)) / 365.25
    for name, (var, mask) in (inter or {}).items():
        for k in range(1, P + 1):
            X[f"{var}_l{k}_x_{name}"] = frame[var].shift(k) * mask
        X[name] = mask.astype(float)
    return X


def hac_wald2(frame, target, causes, controls, P, trend=False, rows=None, inter=None, test=None):
    data = pd.concat([frame[target], design(frame, target, controls, P, trend, inter)], axis=1).dropna()
    if rows is not None:
        data = data.loc[data.index.intersection(rows)]
    fit = sm.OLS(data[target], sm.add_constant(data.drop(columns=target))).fit(cov_type="HAC", cov_kwds={"maxlags": 10})
    names = test or [f"{c}_l{k}" for c in causes for k in range(1, P + 1)]
    w = fit.wald_test(", ".join(f"{n} = 0" for n in names), scalar=True)
    return float(w.statistic), float(w.pvalue), int(fit.nobs)


frame_all = anom.assign(rain=doy_anomaly(d["precip"]), temp=doy_anomaly(d["temp"]))
train_ref = d.loc[:"2018-12-31"]
frame_tr = pd.DataFrame({"wind": doy_anomaly(d["wind"], ref=train_ref["wind"]), "rh": doy_anomaly(d["rh"], ref=train_ref["rh"]),
                         "pm25": doy_anomaly(d["log_pm25"], ref=train_ref["log_pm25"])})
base3 = ["pm25", "wind", "rh"]
rows = []
def add(spec, direction, frame, target, causes, controls, **kw):
    s, pv, n = hac_wald2(frame, target, causes, controls, P, **kw)
    rows.append({"spec": spec, "direction": direction, "wald_chi2": round(s, 1), "p_value": pv, "n": n})
for c, nm in [("wind", "Wind"), ("rh", "Humidity")]:
    add("baseline (P=4)", f"{nm} → PM2.5", frame_all, "pm25", [c], base3)
    add("+ temperature control", f"{nm} → PM2.5", frame_all, "pm25", [c], base3 + ["temp"])
    add("+ rain and temperature", f"{nm} → PM2.5", frame_all, "pm25", [c], base3 + ["rain", "temp"])
    add("+ linear time trend", f"{nm} → PM2.5", frame_all, "pm25", [c], base3, trend=True)
    add("climatology from 2015-2018 only", f"{nm} → PM2.5", frame_tr, "pm25", [c], base3)
add("+ temperature control", "Temperature → PM2.5", frame_all, "pm25", ["temp"], base3 + ["temp"])
for t, nm in [("wind", "Wind"), ("rh", "Humidity")]:
    add("baseline (P=4)", f"PM2.5 → {nm}", frame_all, t, ["pm25"], base3)
    add("+ linear time trend", f"PM2.5 → {nm}", frame_all, t, ["pm25"], base3, trend=True)
robust2 = pd.DataFrame(rows)
robust2.to_csv(RESULTS / "granger_hac_robust.csv", index=False)
robust2.style.format({"p_value": "{:.2e}"})
```

output:
```
<pandas.io.formats.style.Styler at 0x7fbd89887cb0>
```

### [md 30]
**Season-specific effects.** The EDA suggested humidity matters mainly in the monsoon. We test (a) the cause in each season
subsample, and (b) a joint Wald test that the season interactions (monsoon × humidity lags, winter × wind lags) are zero.

### [code 31]
```python
m_ = frame_all.index.month
winter, monsoon = frame_all.index[np.isin(m_, [11, 12, 1])], frame_all.index[np.isin(m_, [7, 8, 9])]
srows = []
for sname, ridx in [("Winter (Nov–Jan)", winter), ("Monsoon (Jul–Sep)", monsoon)]:
    for c, nm in [("wind", "Wind"), ("rh", "Humidity")]:
        s, pv, n = hac_wald2(frame_all, "pm25", [c], base3, P, rows=ridx)
        srows.append({"test": f"{nm} → PM2.5, {sname} only", "wald_chi2": round(s, 1), "p_value": pv, "n": n})
mon_mask = pd.Series(np.isin(m_, [7, 8, 9]), index=frame_all.index)
win_mask = pd.Series(np.isin(m_, [11, 12, 1]), index=frame_all.index)
inter = {"mon": ("rh", mon_mask), "win": ("wind", win_mask)}
for label, tn in [("monsoon × humidity lags = 0", [f"rh_l{k}_x_mon" for k in range(1, P + 1)]),
                  ("winter × wind lags = 0", [f"wind_l{k}_x_win" for k in range(1, P + 1)])]:
    s, pv, n = hac_wald2(frame_all, "pm25", [], base3, P, inter=inter, test=tn)
    srows.append({"test": f"Interaction: {label}", "wald_chi2": round(s, 1), "p_value": pv, "n": n})
seasonal = pd.DataFrame(srows)
seasonal.to_csv(RESULTS / "granger_hac_seasonal.csv", index=False)
seasonal.style.format({"p_value": "{:.2e}"})
```

output:
```
<pandas.io.formats.style.Styler at 0x7fbd898707a0>
```

### [md 32]
**Joint tests at lag order k = 1..7** (HAC, three-variable system). The slides quote these, so they are now saved.

### [code 33]
```python
lrows = []
for pl in range(1, 8):
    for cause, target, nm in [("wind", "pm25", "Wind → PM2.5"), ("rh", "pm25", "Humidity → PM2.5"),
                              ("pm25", "wind", "PM2.5 → Wind"), ("pm25", "rh", "PM2.5 → Humidity")]:
        s, pv, n = hac_wald2(frame_all, target, [cause], base3, pl)
        lrows.append({"direction": nm, "lag_order": pl, "wald_chi2": round(s, 1), "p_value": pv})
by_lag = pd.DataFrame(lrows)
by_lag.to_csv(RESULTS / "granger_hac_by_lag.csv", index=False)
by_lag.pivot(index="direction", columns="lag_order", values="p_value").map(lambda v: f"{v:.1e}")
```

output:
```
lag_order               1        2        3        4        5        6  \
direction                                                                
Humidity → PM2.5  1.2e-10  5.4e-12  1.4e-11  3.5e-11  7.0e-11  2.0e-11   
PM2.5 → Humidity  2.2e-01  6.5e-01  5.4e-01  5.5e-01  5.1e-01  2.2e-01   
PM2.5 → Wind      3.8e-02  1.5e-02  6.5e-02  9.6e-02  2.0e-01  2.6e-01   
Wind → PM2.5      2.9e-10  1.2e-21  1.2e-20  6.0e-20  2.8e-19  2.5e-19   

lag_order               7  
direction                  
Humidity → PM2.5  2.8e-11  
PM2.5 → Humidity  4.4e-01  
PM2.5 → Wind      2.3e-01  
Wind → PM2.5      9.7e-19
```

### [md 34]
**Reading it:** weather → PM2.5 survives temperature and rain controls, a linear trend and a training-only climatology, so the
result is not an artifact of the 2019 decline or of the in-sample climatology. By season, wind and humidity are each
significant in **both** winter and monsoon (p ≤ 5e-4). The interaction tests are the formal comparison: monsoon × humidity
p = 0.20 (humidity's predictive content is *not* detectably different in the monsoon) and winter × wind p = 0.03 (weak
evidence that wind matters differently in winter). So the EDA impression that humidity matters only in the monsoon is a
*correlation* pattern; it is not confirmed as a difference in predictive effect, and we do not claim it.
The reverse direction (PM2.5 → wind) is significant only at lag orders 1-2 (p = 0.04, 0.02) and not from lag order 3 on.

### [md 35]
## 8. Does the shock size depend on the variable ordering?
Orthogonalised impulse responses assume an ordering: variables earlier in the list can affect later ones on the
**same day**. Wind and humidity first (weather → PM2.5 on the same day) gives weather the maximum credit.
PM2.5 first allows only *lagged* weather effects (the conservative case). We report both as a range.

### [code 36]
```python
irf_rows, fevd_rows = [], []
for label, order in [("weather first (wind, rh, pm25)", ["wind", "rh", "pm25"]), ("PM2.5 first (pm25, wind, rh)", ["pm25", "wind", "rh"])]:
    r_o = VAR(anom[order]).fit(p)
    irf_o = r_o.irf(H).orth_irfs
    fe_o = r_o.fevd(H).decomp[order.index("pm25")]
    for imp in ["wind", "rh"]:
        resp = (np.exp(irf_o[:, order.index("pm25"), order.index(imp)]) - 1) * 100
        irf_rows.append({"ordering": label, "shock": NAMES[imp], "day0_pct": resp[0], "day1_pct": resp[1], "day2_pct": resp[2],
                         "day3_pct": resp[3], "day5_pct": resp[5]})
    for j, v in enumerate(order):
        fevd_rows.append({"ordering": label, "variable": NAMES[v], "share_h1_pct": fe_o[0, j] * 100, "share_h14_pct": fe_o[H - 1, j] * 100})
irf_ord = pd.DataFrame(irf_rows).round(1)
fevd_ord = pd.DataFrame(fevd_rows).round(1)
irf_ord.to_csv(RESULTS / "irf_orderings.csv", index=False)
fevd_ord.to_csv(RESULTS / "fevd_orderings.csv", index=False)
display(irf_ord)
fevd_ord
```

output:
```
                         ordering     shock  day0_pct  day1_pct  day2_pct  \
0  weather first (wind, rh, pm25)      Wind      -9.2     -12.0      -4.7   
1  weather first (wind, rh, pm25)  Humidity      -4.5      -6.7      -5.7   
2    PM2.5 first (pm25, wind, rh)      Wind       0.0      -5.9      -1.1   
3    PM2.5 first (pm25, wind, rh)  Humidity       0.0      -4.0      -4.1   

   day3_pct  day5_pct  
0      -1.9      -0.3  
1      -4.0      -1.4  
2       0.9       1.0  
3      -2.7      -0.7                           ordering  variable  share_h1_pct  share_h14_pct
0  weather first (wind, rh, pm25)      Wind          13.3           20.5
1  weather first (wind, rh, pm25)  Humidity           3.0            9.5
2  weather first (wind, rh, pm25)     PM2.5          83.7           70.0
3    PM2.5 first (pm25, wind, rh)     PM2.5         100.0           93.7
4    PM2.5 first (pm25, wind, rh)      Wind           0.0            3.1
5    PM2.5 first (pm25, wind, rh)  Humidity           0.0            3.3
```

### [md 37]
**Reading it:** the next-day effect of a +1 SD wind shock is about −6% (lagged effect only) to −12% (including
same-day effects); humidity −4% to −7%. Weather's share of 14-day forecast-error variance ranges from about
6% (PM2.5 first) to about 30% (weather first). So the honest statement is "**weather accounts for a modest but
real share, roughly 6–30% depending on the assumed ordering**", not a single number.

### [md 38]
### 8b. Generalised impulse responses and confidence bands for both orderings
The Pesaran–Shin generalised IRF does not depend on the variable ordering: the response to a 1-SD shock to variable j is
Ψ_h Σ e_j / sqrt(σ_jj). It is the natural cross-check for the Cholesky range above (shocks are not orthogonal, so shares are not additive).

### [code 39]
```python
Psi = res.ma_rep(H)
Sig = np.asarray(res.sigma_u)
names = list(anom.columns)
ip = names.index("pm25")
girf_rows = []
for imp in ["wind", "rh"]:
    j_ = names.index(imp)
    resp = np.array([Psi[h_][ip] @ Sig[:, j_] / np.sqrt(Sig[j_, j_]) for h_ in range(H + 1)])
    pct_ = (np.exp(resp) - 1) * 100
    girf_rows.append({"shock": NAMES[imp], **{f"day{h_}_pct": round(float(pct_[h_]), 1) for h_ in (0, 1, 2, 3, 5)}})
girf = pd.DataFrame(girf_rows); girf.to_csv(RESULTS / "girf.csv", index=False)

ci_rows = []
for label, order_ in [("weather first (wind, rh, pm25)", ["wind", "rh", "pm25"]), ("PM2.5 first (pm25, wind, rh)", ["pm25", "wind", "rh"])]:
    r_o = VAR(anom[order_]).fit(p)
    i_o = r_o.irf(H); se_o = i_o.stderr(orth=True)
    for imp in ["wind", "rh"]:
        a_, b_ = order_.index("pm25"), order_.index(imp)
        r, s = i_o.orth_irfs[:, a_, b_], se_o[:, a_, b_]
        for h_ in range(H + 1):
            ci_rows.append({"ordering": label, "shock": NAMES[imp], "h": h_, "pct": (np.exp(r[h_]) - 1) * 100,
                            "lo": (np.exp(r[h_] - 1.96 * s[h_]) - 1) * 100, "hi": (np.exp(r[h_] + 1.96 * s[h_]) - 1) * 100})
irf_ci = pd.DataFrame(ci_rows).round(2); irf_ci.to_csv(RESULTS / "irf_ci.csv", index=False)
print("Generalised IRF (day-by-day % change in PM2.5):"); display(girf)
irf_ci[irf_ci.h == 1]
```

output:
```
Generalised IRF (day-by-day % change in PM2.5):
      shock  day0_pct  day1_pct  day2_pct  day3_pct  day5_pct
0      Wind      -9.2     -12.0      -4.7      -1.9      -0.3
1  Humidity      -3.3      -5.2      -5.1      -3.8      -1.4                          ordering     shock  h    pct     lo     hi
1   weather first (wind, rh, pm25)      Wind  1 -11.98 -13.28 -10.66
16  weather first (wind, rh, pm25)  Humidity  1  -6.74  -8.05  -5.41
31    PM2.5 first (pm25, wind, rh)      Wind  1  -5.90  -7.07  -4.72
46    PM2.5 first (pm25, wind, rh)  Humidity  1  -3.99  -5.16  -2.80
```

### [md 40]
The generalised response lies between the two Cholesky bounds, as expected. The day-1 bands (above) exclude zero for wind in both
orderings, so the reported ranges are not just point estimates.

### [md 41]
## 9. Does last week's weather help predict this week's PM2.5? (weekly scale)
The daily effect fades within about 5 days. For a 12-month forecast we need to know whether weather still helps at
the weekly scale. We deseasonalise the weekly series (week-of-year mean from 2015–2018) and regress this week's
PM2.5 anomaly on last week's PM2.5, wind and humidity anomalies, with HAC errors.

### [code 42]
```python
weekly = pd.read_csv(PROCESSED / "delhi_weekly.csv", index_col="Date", parse_dates=True)
wk = weekly.loc[:"2018-12-31", ["log_pm25", "wind", "rh"]].copy()
woy = week_index(wk.index)
wk_an = wk - wk.groupby(woy).transform("mean").to_numpy()
same = sm.OLS(wk_an["log_pm25"], sm.add_constant(wk_an[["wind", "rh"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
lagd = pd.concat([wk_an["log_pm25"].shift(1), wk_an["wind"].shift(1), wk_an["rh"].shift(1)], axis=1, keys=["pm25_lag1", "wind_lag1", "rh_lag1"])
lag_fit = sm.OLS(wk_an["log_pm25"], sm.add_constant(lagd), missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": 4})
weekly_lag = pd.DataFrame({
    "model": ["same-week weather"] * 2 + ["last-week predictors"] * 3,
    "term": ["wind", "humidity", "PM2.5 (last week)", "wind (last week)", "humidity (last week)"],
    "coef": [same.params["wind"], same.params["rh"], lag_fit.params["pm25_lag1"], lag_fit.params["wind_lag1"], lag_fit.params["rh_lag1"]],
    "p_value": [same.pvalues["wind"], same.pvalues["rh"], lag_fit.pvalues["pm25_lag1"], lag_fit.pvalues["wind_lag1"], lag_fit.pvalues["rh_lag1"]],
})
weekly_lag["r2_model"] = [same.rsquared] * 2 + [lag_fit.rsquared] * 3
weekly_lag.round(4).to_csv(RESULTS / "weekly_weather_lag.csv", index=False)

# Nested comparison: does adding last week's wind + humidity improve on last week's PM2.5 alone?
base = sm.OLS(wk_an["log_pm25"], sm.add_constant(lagd[["pm25_lag1"]]), missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": 4})
wald = lag_fit.wald_test("wind_lag1 = 0, rh_lag1 = 0", scalar=True)
nested = pd.DataFrame({"R2_lagged_pm25_only": [base.rsquared], "R2_plus_lagged_weather": [lag_fit.rsquared],
                       "delta_R2": [lag_fit.rsquared - base.rsquared], "joint_wald_p_weather": [float(wald.pvalue)]})
nested.round(4).to_csv(RESULTS / "weekly_lag_nested.csv", index=False)
display(nested.round(4))
weekly_lag.round(4)
```

output:
```
   R2_lagged_pm25_only  R2_plus_lagged_weather  delta_R2  joint_wald_p_weather
0               0.1341                  0.1391     0.005                0.5146                  model                  term    coef  p_value  r2_model
0     same-week weather                  wind -0.0402   0.0013    0.1403
1     same-week weather              humidity -0.0105   0.0000    0.1403
2  last-week predictors     PM2.5 (last week)  0.3621   0.0000    0.1391
3  last-week predictors      wind (last week)  0.0066   0.4576    0.1391
4  last-week predictors  humidity (last week) -0.0013   0.4799    0.1391
```

### [md 43]
**Reading it:** *same-week* weather is significantly related to PM2.5 (the daily effect, averaged over a week),
but **last week's weather adds nothing** once last week's PM2.5 is known: the nested comparison above shows ΔR² ≈ 0 and a
joint HAC Wald p-value far above 0.05. (The two R² values in the first table belong to different, non-nested models, so
they are not compared with each other.) So weather helps explain and
very-short-term-predict PM2.5, but it cannot be forecast a year ahead, so the 12-month model uses no weather
regressors. Weather's short-horizon value is quantified in notebook 04.

### [md 44]
## Conclusions
* **Wind and humidity anomalies have a strong, robust predictive association with PM2.5 (Granger):** joint tests are
  significant at every lag order 1-7, with HAC errors, with BIC lag, with first differences, with rain and temperature
  controls and with a linear trend. The reverse direction is not robust (it depends on the specification).
* **Size and timing:** a +1 SD wind shock (≈2.5 km/h) lowers PM2.5 by ≈6–12% the next day (range across
  orderings); a +1 SD humidity shock (≈5.4% RH) by ≈4–7%. Effects fade within about 5 days.
* **Share of forecast uncertainty:** ≈6–30% at 14 days, depending on the ordering assumption.
* **Horizon:** last week's weather does not add to last week's PM2.5 for predicting this week's PM2.5, so weather is a
  short-horizon tool and the 12-month model uses none.
* **Caveat:** this is *predictive* causality in a restricted observational model. Unmeasured drivers (mixing-layer height,
  stubble burning, fireworks) could confound it, and an in-sample Granger result does not guarantee out-of-sample skill
  (tested in notebook 04).

### [code 45]
```python
key["granger"] = {r["direction"]: float(f"{r['p_value']:.3g}") for r in granger.to_dict("records")}
key["granger_hac"] = {r["direction"] + " | " + r["spec"]: float(f"{r['p_value']:.3g}") for r in granger_hac.to_dict("records")}
(RESULTS / "key_numbers_var.json").write_text(json.dumps(key, indent=2, ensure_ascii=False))
key
```

output:
```
{'var_sample': '2015-01-01 to 2019-12-31 (1826 days)',
 'var_lag_aic': 4,
 'var_lag_bic': 2,
 'var_stable': True,
 'portmanteau_p': 0.168,
 'max_eigen_modulus': 0.813,
 'irf': {'wind': {'peak_pct': -12.0,
   'peak_day': 1,
   'shock_sd': 2.54,
   'unit': 'km/h'},
  'rh': {'peak_pct': -6.7, 'peak_day': 1, 'shock_sd': 5.43, 'unit': '% RH'}},
 'fevd_weather_share_h14': 30.0,
 'fevd_wind_h14': 20.5,
 'fevd_rh_h14': 9.5,
 'granger': {'Wind → PM2.5': 1.08e-29,
  'Humidity → PM2.5': 1.16e-11,
  'Wind + Humidity → PM2.5': 2.76e-33,
  'PM2.5 → Wind': 0.122,
  'PM2.5 → Humidity': 0.617},
 'granger_hac': {'Wind → PM2.5 | PM2.5, wind, humidity': 5.95e-20,
  'Humidity → PM2.5 | PM2.5, wind, humidity': 3.52e-11,
  'Wind → PM2.5 | + rain control': 2.81e-19,
  'Humidity → PM2.5 | + rain control': 3.04e-08,
  'Rain → PM2.5 | + rain control': 0.877,
  'PM2.5 → Wind | PM2.5, wind, humidity': 0.0956,
  'PM2.5 → Humidity | PM2.5, wind, humidity': 0.546}}
```
