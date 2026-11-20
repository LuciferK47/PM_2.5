"""Figures, LaTeX tables and number macros for the deck and the report.

Figures come in two sizes: PROFILE=deck (default; drawn at the size they appear on a slide) and PROFILE=report (drawn at one
column / full text width of the two-column report), so fonts stay legible in both. Every number comes from data/processed and
results/, never typed by hand.   Run after notebooks 02-04:
    .venv/bin/python slides/beamer/make_figures.py && PROFILE=report .venv/bin/python slides/beamer/make_figures.py
"""
import json
import os
import sys
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.dates as mdates  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from src import forecast as F  # noqa: E402
from src.plots import AXIS, AQUA, BLUE, INK, INK_2, MUTED, NEUTRAL, ORANGE, SEASON_COLORS, use_style  # noqa: E402
from src.data import SEASONS, OTHER_SEASON  # noqa: E402

warnings.filterwarnings("ignore")
PROFILE = os.environ.get("PROFILE", "deck")          # "deck" (slides) or "report" (two-column paper)
FIG, TAB = HERE / ("fig" if PROFILE == "deck" else "fig_report"), HERE / "tables"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)
W_CM = 14.6 if PROFILE == "deck" else 17.0
SINGLE_CM = 8.4   # one report column
K = 1.15 if PROFILE == "deck" else 1.0
CM = 1 / 2.54


def fs(x):
    """Scale a hard-coded font size for the profile (the report never goes below 7 pt)."""
    return x * K if PROFILE == "deck" else max(x, 7.0)


use_style()
mpl.rcParams.update({
    "font.size": 10 * K, "axes.labelsize": 10 * K, "xtick.labelsize": 9 * K, "ytick.labelsize": 9 * K, "legend.fontsize": 9 * K,
    "axes.titlesize": 9 * K, "axes.titleweight": "normal", "lines.linewidth": 1.8, "pdf.fonttype": 42,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
})

daily = pd.read_csv(ROOT / "data/processed/delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
weekly = pd.read_csv(ROOT / "data/processed/delhi_weekly.csv", index_col="Date", parse_dates=True)
RES = ROOT / "results"
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MODELS = ["Seasonal naive", "Seasonal mean", "Holt-Winters", "SARIMA", "Harmonic regression", "Combination"]
COL = {"Seasonal naive": NEUTRAL, "Seasonal mean": MUTED, "Holt-Winters": AQUA, "SARIMA": ORANGE, "Harmonic regression": BLUE,
       "Combination": "#7a4fd1"}


def new_fig(h_cm, nrows=1, ncols=1, w=None, single=False, half=False, **kw):
    if PROFILE == "report" and (single or half):
        w, h_cm = SINGLE_CM, h_cm * 1.25
    elif PROFILE == "deck":
        h_cm *= 1.0                       # every deck figure is drawn at the full text width
    return plt.subplots(nrows, ncols, figsize=((w or W_CM) * CM, h_cm * CM), layout="constrained", **kw)


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)


# logo.png is kept in the repo
if (HERE / "logo-000.png").exists():
    rgb, mask = Image.open(HERE / "logo-000.png").convert("RGB"), Image.open(HERE / "logo-001.png").convert("L")
    rgb.putalpha(mask)
    rgb.save(HERE / "logo.png")


def jl(name):
    return json.loads((RES / name).read_text())


eda, var, fcn = jl("key_numbers_eda.json"), jl("key_numbers_var.json"), jl("key_numbers_forecast.json")
y = weekly["log_pm25"]; raw = weekly["pm25"]
fb = pd.read_csv(RES / "fc_backtest_forecasts.csv", parse_dates=["date"])
f20 = pd.read_csv(RES / "fc_2020_forecasts.csv", parse_dates=["date"])
LOCK0, LOCK1 = pd.Timestamp("2020-03-25"), pd.Timestamp("2020-05-31")


# ═══ 1. Exploring the data ════════════════════════════════════════════════════════════════════════════
fig, ax = new_fig(4.4, single=True)
ax.plot(daily.index, daily["pm25"], color=MUTED, lw=0.6, label="daily")
ax.plot(daily.index, daily["pm25"].rolling(30, center=True, min_periods=15).mean(), color=BLUE, lw=1.8, label="30-day mean")
ax.axvspan(pd.Timestamp("2020-01-01"), daily.index[-1], color=NEUTRAL, alpha=0.35, lw=0)
ax.text(pd.Timestamp("2020-04-01"), 560, "2020\n(not used\nto fit)", ha="center", va="top", fontsize=fs(7.5), color=INK_2)
ax.set_ylabel("PM$_{2.5}$ ($\\mu$g/m$^3$)"); ax.legend(loc="upper left", frameon=False, ncols=2)
ax.set_xlim(daily.index[0], daily.index[-1])
save(fig, "daily_ts")

d_mod = daily.loc[:"2019-12-31"]
fig, ax = new_fig(5.0, single=True)
data = [d_mod.loc[d_mod.index.month == m, "pm25"].dropna() for m in range(1, 13)]
smap = {m: n for n, ms in SEASONS.items() for m in ms}
bp = ax.boxplot(data, tick_labels=(months if PROFILE == "deck" else [m[0] for m in months]), patch_artist=True, widths=0.65,
                medianprops=dict(color=INK, lw=1.8), whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
                flierprops=dict(marker="o", markersize=2.5, markerfacecolor=MUTED, markeredgecolor="none", alpha=0.5))
for box, m in zip(bp["boxes"], range(1, 13)):
    box.set(facecolor=SEASON_COLORS[smap.get(m, OTHER_SEASON)], edgecolor="white", linewidth=1.5)
ax.set_ylabel("PM$_{2.5}$ ($\\mu$g/m$^3$)"); ax.set_ylim(0, 720)
save(fig, "seasonal_boxplot")

bm = pd.read_csv(RES / "monthly_mean_sd.csv", index_col=0)
fig, axes = new_fig(4.4, ncols=2)
for ax, (m_, s_, t_) in zip(axes, [(bm.mean_raw, bm.sd_raw, f"Raw PM$_{{2.5}}$ (corr. {eda['corr_mean_sd_raw']:.2f})"),
                                    (bm.mean_log, bm.sd_log, f"log PM$_{{2.5}}$ (corr. {eda['corr_mean_sd_log']:.2f})")]):
    ax.scatter(m_, s_, color=BLUE, s=22)
    for mo, (xx, yy) in enumerate(zip(m_, s_), 1):
        ax.annotate(months[mo - 1][:3], (xx, yy), fontsize=fs(7), xytext=(3, 2), textcoords="offset points", color=INK_2)
    ax.set_xlabel("monthly mean"); ax.set_title(t_, loc="left")
axes[0].set_ylabel("monthly SD")
save(fig, "mean_sd")

stlc = pd.read_csv(RES / "stl_components.csv", index_col=0, parse_dates=True)
fig, axes = new_fig(5.2, nrows=4, sharex=True, single=True)
for ax, (c, lab) in zip(axes, [("observed", "log PM$_{2.5}$"), ("trend", "Trend"), ("seasonal", "Seasonal"), ("resid", "Remainder")]):
    if c == "resid":
        ax.vlines(stlc.index, 0, stlc[c], color=BLUE, lw=1.2)
    else:
        ax.plot(stlc.index, stlc[c], color=BLUE)
    ax.set_ylabel(lab, rotation=0, ha="right", va="center", fontsize=fs(9), color=INK_2)
    ax.tick_params(axis="y", labelsize=fs(7.5))
save(fig, "stl")


def acf_panel(ax, vals, title, n, lags=60):
    ax.vlines(range(1, lags + 1), 0, vals[1:lags + 1], color=BLUE, lw=1.4)
    ax.axhline(0, color=INK_2, lw=0.8)
    ax.axhspan(-1.96 / np.sqrt(n), 1.96 / np.sqrt(n), color=NEUTRAL, alpha=0.35, lw=0)
    ax.set_xlabel("lag (weeks)"); ax.set_title(title, loc="left"); ax.set_ylim(-1, 1)


acf_, pacf_ = pd.read_csv(RES / "acf_weekly_train.csv", index_col=0), pd.read_csv(RES / "pacf_weekly_train.csv", index_col=0)
fig, axes = new_fig(4.6, ncols=2)
acf_panel(axes[0], acf_["log PM2.5"].to_numpy(), "ACF of log PM$_{2.5}$", eda["n_weeks_train"])
acf_panel(axes[1], pacf_["log PM2.5"].to_numpy(), "PACF of log PM$_{2.5}$", eda["n_weeks_train"])
for xx in (26, 52):
    axes[0].axvline(xx, color=ORANGE, ls=":", lw=1.2)
save(fig, "acf_pacf")
fig, axes = new_fig(4.6, ncols=2)
acf_panel(axes[0], acf_["52-week difference"].to_numpy(), "ACF after seasonal difference", eda["n_weeks_train"] - 52)
acf_panel(axes[1], pacf_["52-week difference"].to_numpy(), "PACF after seasonal difference", eda["n_weeks_train"] - 52)
save(fig, "acf_pacf_d52")
fig, axes = new_fig(6.5, nrows=2, ncols=2, sharey=True)
for j, (col, nn, lab) in enumerate((("log PM2.5", eda["n_weeks_train"], "log PM$_{2.5}$"), ("52-week difference", eda["n_weeks_train"] - 52, "$\\nabla_{52}$ log PM$_{2.5}$"))):
    acf_panel(axes[j, 0], acf_[col].to_numpy(), "ACF of " + lab, nn)
    acf_panel(axes[j, 1], pacf_[col].to_numpy(), "PACF of " + lab, nn)
for xx in (26, 52):
    axes[0, 0].axvline(xx, color=ORANGE, ls=":", lw=1.2)
for ax in axes[0]:
    ax.set_xlabel("")
for ax in axes.ravel():
    ax.set_ylim(-0.7, 1)
save(fig, "acf_grid")

# ═══ 2. Benchmarks and the harmonic curve ══════════════════════════════════════════════════════════════
from src.tsa import week_index  # noqa: E402
tr_y = y.loc[:"2018-12-30"]; tr_raw = raw.loc[:"2018-12-30"]
wk_idx = pd.Series(week_index(tr_y.index), index=tr_y.index)
fig, ax = new_fig(4.8, single=True, half=True)
for yr, c in zip((2015, 2016, 2017, 2018), (NEUTRAL, "#cfcfc7", "#a8a8a0", MUTED)):
    s = tr_raw[tr_raw.index.year == yr]; ax.plot(wk_idx[s.index], s, color=c, lw=1.0, label=str(yr))
smean = np.exp(tr_y.groupby(wk_idx).mean())
ax.plot(smean.index, smean, color=BLUE, lw=2.6, label="mean")
ax.set_xlabel("calendar week"); ax.set_ylabel("PM$_{2.5}$ ($\\mu$g/m$^3$)"); fig.legend(*ax.get_legend_handles_labels(), loc="outside upper center", ncols=5, frameon=False, fontsize=fs(8))
ax.set_ylim(0, 620)
save(fig, "year_curves")

Xf = lambda ix, Kk: F.fourier(ix, Kk)  # noqa: E731
fig, ax = new_fig(3.8, single=True, half=True)
ax.plot(smean.index, smean, color=NEUTRAL, lw=1.4, label="seasonal mean")
wkset = tr_y.index[:52]
import statsmodels.api as sm  # noqa: E402
for Kk, c in ((1, AQUA), (2, ORANGE), (4, BLUE)):
    X = sm.add_constant(Xf(tr_y.index, Kk)); b = sm.OLS(tr_y.to_numpy(), X).fit()
    ref = pd.date_range("2018-01-07", periods=52, freq="W-SUN")
    curve = np.exp(b.predict(sm.add_constant(Xf(ref, Kk), has_constant="add")))
    ax.plot(week_index(ref), curve, color=c, lw=2.0, label=f"K = {Kk}")
ax.set_xlabel("calendar week"); ax.set_ylabel("PM$_{2.5}$ ($\\mu$g/m$^3$)"); fig.legend(*ax.get_legend_handles_labels(), loc="outside upper center", ncols=4, frameon=False, fontsize=fs(8)); ax.set_ylim(0, 380)
save(fig, "harmonic_k")

# ═══ 3. SARIMA residuals (refit the identification model, ~15 s) ═══════════════════════════════════════
from statsmodels.tsa.statespace.sarimax import SARIMAX  # noqa: E402
rD = F._fit(SARIMAX(tr_y, order=(1, 0, 1), seasonal_order=(0, 1, 1, 52)))
e = pd.Series(np.asarray(rD.resid), index=tr_y.index).iloc[int(rD.loglikelihood_burn):]
from statsmodels.tsa.stattools import acf as _acf  # noqa: E402
fig, axes = new_fig(4.3, ncols=2, width_ratios=[1.3, 1])
axes[0].plot(tr_y.index[-len(e):], e, color=BLUE, lw=1.2); axes[0].axhline(0, color=INK_2, lw=0.8); axes[0].set_title("Residuals", loc="left")
axes[0].xaxis.set_major_locator(mdates.YearLocator()); axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
a_ = _acf(e, nlags=40)
axes[1].vlines(range(1, 41), 0, a_[1:], color=BLUE, lw=1.4); axes[1].axhline(0, color=INK_2, lw=0.8)
axes[1].axhspan(-1.96 / np.sqrt(len(e)), 1.96 / np.sqrt(len(e)), color=NEUTRAL, alpha=0.35, lw=0)
axes[1].set_title("Residual ACF", loc="left"); axes[1].set_xlabel("lag (weeks)")
save(fig, "sarima_resid")

# ═══ 4. Weather ═══════════════════════════════════════════════════════════════════════════════════════
from src.tsa import doy_anomaly, doy_climatology, doy365  # noqa: E402
w_mod = weekly.loc[:"2019-12-29"]
fig, axes = new_fig(5.6, nrows=3, sharex=True, single=True)
for ax, (c, lab, col) in zip(axes, [("pm25", "PM$_{2.5}$", BLUE), ("wind", "Wind km/h", ORANGE), ("rh", "RH %", AQUA)]):
    ax.plot(w_mod.index, w_mod[c], color=col, lw=1.2); ax.set_ylabel(lab, fontsize=fs(8))
    ax.tick_params(axis="y", labelsize=fs(7.5))
save(fig, "weather_weekly")

fig, axes = new_fig(4.8, nrows=2, sharex=True, single=True)
lg = d_mod["log_pm25"]; clim = doy_climatology(lg)
axes[0].plot(lg.index, lg, color=NEUTRAL, lw=0.7, label="daily")
axes[0].plot(lg.index, clim.reindex(doy365(lg.index)).to_numpy(), color=BLUE, lw=1.8, label="seasonal mean")
axes[0].set_ylabel("log PM$_{2.5}$"); fig.legend(*axes[0].get_legend_handles_labels(), loc="outside upper center", ncols=2, frameon=False, fontsize=fs(8))
an = doy_anomaly(lg); axes[1].plot(an.index, an, color=BLUE, lw=0.8); axes[1].axhline(0, color=INK_2, lw=0.8); axes[1].set_ylabel("anomaly")
save(fig, "deseason")

lag = pd.read_csv(RES / "var_lag_selection.csv", index_col=0)
fig, ax = new_fig(4.4, single=True, half=True)
ax.plot(lag.index, lag["AIC"], marker="o", color=BLUE, label="AIC"); ax.plot(lag.index, lag["BIC"], marker="s", color=ORANGE, label="BIC")
ax.axvline(var["var_lag_aic"], color=MUTED, ls=":"); ax.set_xlabel("VAR lag $p$ (days)"); ax.set_ylabel("criterion")
ax.scatter([var["var_lag_aic"]], [lag["AIC"].loc[var["var_lag_aic"]]], s=120, facecolors="none", edgecolors=BLUE, zorder=4)
ax.scatter([var["var_lag_bic"]], [lag["BIC"].loc[var["var_lag_bic"]]], s=120, facecolors="none", edgecolors=ORANGE, zorder=4)
fig.legend(*ax.get_legend_handles_labels(), loc="outside upper center", ncols=2, frameon=False, fontsize=fs(8))
ax.set_ylim(2.3, 3.0)
save(fig, "var_lag")

# ═══ 5. Backtest forecasts ═════════════════════════════════════════════════════════════════════════════
def panel(ax, fold, m, title=None, band=True):
    o = fb[(fb.fold == fold) & (fb.model == m)]
    ax.plot(o.date, o.actual, color=ORANGE, lw=1.0, marker="o", ms=2.2, label="actual")
    if band and o.sd.notna().all():
        ax.fill_between(o.date, np.exp(o.mu - 1.96 * o.sd), np.exp(o.mu + 1.96 * o.sd), color=COL[m], alpha=0.16, lw=0)
    ax.plot(o.date, np.exp(o.mu), color=COL[m], lw=1.9, label=m)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b")); ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 7)))
    ax.set_title(title or m, loc="left"); ax.set_ylim(0, 520)


for name, trio in (("fc19_1", ("Seasonal naive", "Seasonal mean", "Holt-Winters")), ("fc19_2", ("SARIMA", "Harmonic regression", "Combination"))):
    fig, axes = new_fig(4.8, ncols=3, sharey=True)
    for ax, m in zip(axes, trio):
        panel(ax, 2019, m, m + (" (no band)" if m == "Combination" else ""))
    axes[0].set_ylabel("PM$_{2.5}$ ($\\mu$g/m$^3$)")
    save(fig, name)

fig, axes = new_fig(4.5, ncols=3, sharey=True)
for ax, m in zip(axes, ("Holt-Winters", "SARIMA", "Harmonic regression")):
    panel(ax, 2019, m, m)
    sm_ = fb[(fb.fold == 2019) & (fb.model == "Seasonal mean")]
    ax.plot(sm_.date, np.exp(sm_.mu), color=INK_2, lw=1.2, ls="--", label="seasonal mean")
axes[0].set_ylabel("PM$_{2.5}$ ($\\mu$g/m$^3$)")
h_, l_ = axes[0].get_legend_handles_labels()
fig.legend([h_[0], axes[1].get_lines()[-1], h_[1]], ["actual 2019", "seasonal mean", "forecast (95% band)"], loc="outside upper center", ncols=3, frameon=False, fontsize=fs(8))
save(fig, "fc19_models")

if PROFILE == "report":
    fig, axes = new_fig(8.2, nrows=2, ncols=3, sharex=True, sharey=True)
    for ax, m in zip(axes.ravel(), MODELS):
        panel(ax, 2019, m, m)
    for ax in axes[:, 0]:
        ax.set_ylabel("PM$_{2.5}$ ($\\mu$g/m$^3$)")
    save(fig, "fc19_all")

fig, axes = new_fig(5.2, ncols=2, sharey=True)
for ax, fold in zip(axes, (2017, 2018)):
    for m in ("Seasonal mean", "Holt-Winters", "SARIMA", "Harmonic regression"):
        o = fb[(fb.fold == fold) & (fb.model == m)]; ax.plot(o.date, np.exp(o.mu), color=COL[m], lw=1.5, label=m)
    o = fb[(fb.fold == fold) & (fb.model == "Seasonal mean")]
    ax.plot(o.date, o.actual, color="black", lw=1.0, marker="o", ms=2.0, label="actual")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b")); ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
    ax.set_title(str(fold), loc="left"); ax.set_ylim(0, 520)
axes[0].set_ylabel("Weekly PM$_{2.5}$ ($\\mu$g/m$^3$)")
axes[1].legend(fontsize=fs(7), ncols=1, loc="upper right", frameon=False)
save(fig, "fc_other")

mae = pd.read_csv(RES / "fc_backtest_mae.csv", index_col=0)
fig, ax = new_fig(5.0, single=True)
x_ = np.arange(len(MODELS)); w_ = 0.27
for k, (fo, c) in enumerate([(2017, NEUTRAL), (2018, AQUA), (2019, BLUE)]):
    ax.bar(x_ + (k - 1) * w_, [mae.loc[m, str(fo)] for m in MODELS], w_, color=c, label=str(fo))
ax.set_xticks(x_, ["Naive", "Seasonal\nmean", "Holt-\nWinters", "SARIMA", "Harmonic", "Combin."], fontsize=fs(7.5))
ax.set_ylabel("MAE ($\\mu$g/m$^3$)"); ax.set_ylim(0, 70); ax.legend(title="forecast year", ncols=3, frameon=False, loc="upper left", fontsize=fs(7.5), title_fontsize=fs(7.5))
save(fig, "fc_mae")

# one week ahead
ow = pd.read_csv(RES / "fc_oneweek.csv", index_col=0)
fig, ax = new_fig(4.4, single=True)
labs_ = ["Persistence", "Seasonal\nmean", "Harmonic,\nno weather", "+ last week's\nweather", "+ same-week\n(not known\nin advance)"]
vals = [ow.loc[m, "both years"] for m in ow.index]
bars = ax.bar(range(len(vals)), vals, color=[NEUTRAL, NEUTRAL, BLUE, AQUA, ORANGE])
for i, v in enumerate(vals):
    ax.text(i, v + 0.4, f"{v:.1f}", ha="center", fontsize=fs(8))
ax.set_xticks(range(len(vals)), labs_, fontsize=fs(7.5), **({} if PROFILE == "deck" else dict(rotation=35, ha="right")))
ax.set_ylabel("MAE ($\\mu$g/m$^3$)"); ax.set_ylim(0, max(vals) * 1.15)
save(fig, "fc_oneweek")

# ═══ 6. 2020 what-if ═══════════════════════════════════════════════════════════════════════════════════
fig, ax = new_fig(4.6, single=True)
a20 = f20[f20.model == "Seasonal mean"]
for m in ("Seasonal mean", "Holt-Winters", "SARIMA", "Harmonic regression"):
    o = f20[f20.model == m]; ax.plot(o.date, np.exp(o.mu), color=COL[m], lw=1.6, label=m)
ax.plot(a20.date, a20.actual, color="black", lw=1.5, marker="o", ms=3, label="actual 2020")
ax.axvspan(LOCK0, LOCK1, color=NEUTRAL, alpha=0.3, lw=0)
ax.text(LOCK0 + (LOCK1 - LOCK0) / 2, 285, "lockdown", ha="center", fontsize=fs(8), color=INK_2)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b")); ax.set_ylabel("Weekly PM$_{2.5}$ ($\\mu$g/m$^3$)")
fig.legend(*ax.get_legend_handles_labels(), loc="outside upper center", ncols=3, frameon=False, fontsize=fs(8)); ax.set_ylim(0, 320)
save(fig, "fc_lockdown")

win = pd.read_csv(RES / "fc_lockdown_windows.csv"); lk = pd.read_csv(RES / "fc_lockdown.csv", index_col=0)
fig, ax = new_fig(4.6, single=True)
for i, m in enumerate(MODELS):
    g = win[win.model == m].gap_pct
    ax.scatter(np.full(len(g), i) + np.random.default_rng(0).uniform(-0.18, 0.18, len(g)), g, s=6, color=MUTED, alpha=0.6, linewidths=0)
    ax.scatter(i, lk.loc[m, "lockdown gap (%)"], s=45, color=ORANGE, zorder=3, label="2020 lockdown weeks" if i == 0 else None)
    ax.scatter(i, lk.loc[m, "same weeks of 2019 (%)"], s=40, marker="D", color=BLUE, zorder=3, label="same weeks, 2019" if i == 0 else None)
ax.axhline(0, color=INK_2, lw=0.8)
ax.set_xticks(range(len(MODELS)), ["Naive", "Seasonal\nmean", "Holt-\nWinters", "SARIMA", "Harmonic", "Combin."], fontsize=fs(7.5))
ax.set_ylabel("gap (%)"); fig.legend(*ax.get_legend_handles_labels(), frameon=False, loc="outside upper center", ncols=2, fontsize=fs(8))
save(fig, "lock_gap")


# ═══ tables ════════════════════════════════════════════════════════════════════════════════════════════
def sci(p):
    if p < 1e-12:
        return r"\ensuremath{<10^{-12}}"
    if p < 1e-3:
        m, e = f"{p:.1e}".split("e")
        return rf"\ensuremath{{{m}\times10^{{{int(e)}}}}}"
    return f"{p:.3f}" if p < 0.1 else f"{p:.2f}"


def write(name, spec, header, rows):
    """Fully boxed table (course-report style): vertical rules between columns, a rule under every row."""
    cols = "|" + "|".join(spec) + "|"
    body = " \\\\\\hline\n".join(" & ".join(str(c) for c in r) for r in rows)
    (TAB / f"{name}.tex").write_text(f"\\begin{{tabular}}{{{cols}}}\n\\hline\n{header} \\\\\\hline\n{body} \\\\\\hline\n\\end{{tabular}}\n")


neg = lambda v, d=1: f"{v:.{d}f}".replace("-", r"\ensuremath{-}")  # noqa: E731
tex_pm = lambda s: s.replace("→", r"$\to$").replace("PM2.5", r"PM$_{2.5}$")  # noqa: E731

for f_ in TAB.glob("*.tex"):
    if f_.name != "numbers.tex":
        f_.unlink()

am = pd.read_csv(RES / "annual_means.csv", index_col=0)
rows = [[str(yr), f"{r.iloc[0]:.0f}", ("--" if yr == 2016 else neg(r.iloc[1], 0) + "\\%")] for yr, r in am.iterrows()]
write("annual", "lrr", r"\textbf{Year} & \textbf{Mean PM$_{2.5}$ ($\mu$g/m$^3$)} & \textbf{vs 2016}", rows)

lt = pd.read_csv(RES / "log_justification.csv", index_col=0)
rows = [[lab, f"{lt.loc[k].iloc[0]:.2f}", f"{lt.loc[k].iloc[1]:.2f}"] for k, lab in
        [("Skewness", "Skewness"), ("corr(monthly mean, monthly SD)", "Correlation of monthly mean and monthly SD"),
         ("Max / min monthly SD", "Largest / smallest monthly SD")]]
write("log_tests", "lrr", r"\textbf{Check} & \textbf{Raw} & \textbf{Log}", rows)

st = pd.read_csv(RES / "stationarity_train.csv", index_col=0)
rows = []
for k, lab in (("log PM2.5", r"log PM$_{2.5}$"), ("52-week difference of log PM2.5", r"$\nabla_{52}$ log PM$_{2.5}$")):
    r = st.loc[k]
    rows.append([lab, f"{r['adf_stat']:.2f}", sci(r["adf_p"]), f"{r['kpss_stat']:.3f}", "0.463"])
write("stationarity", "lrrrr", r"\textbf{Weekly series, 2015--18} & \textbf{ADF stat} & \textbf{ADF $p$} & \textbf{KPSS stat} & \textbf{KPSS 5\% crit.}", rows)

idn = pd.read_csv(RES / "fc_sarima_identification.csv", index_col=0)
rows = [[mname.replace("ARIMA", r"ARIMA"), f"{r.AIC:.1f}", f"{r.BIC:.1f}"] for mname, r in idn.iterrows()]
write("sarima_ident", "lrr", r"\textbf{Candidate (log PM$_{2.5}$, 2015--18)} & \textbf{AIC} & \textbf{BIC}", rows)

lb = pd.read_csv(RES / "fc_sarima_ljungbox.csv", index_col=0)
rows = [[str(i), sci(r.iloc[0]), sci(r.iloc[1])] for i, r in lb.iterrows()]
write("ljungbox", "lrr", r"\textbf{Ljung--Box lag} & \textbf{$p$, all residuals} & \textbf{$p$, first 52 dropped}", rows)

specs = pd.read_csv(RES / "fc_specs.csv")
rows = []
for fo in (2017, 2018, 2019):
    h = specs[(specs.fold == fo) & (specs.model == "Harmonic regression")].iloc[0]
    s = specs[(specs.fold == fo) & (specs.model == "SARIMA")].iloc[0]
    hw = specs[(specs.fold == fo) & (specs.model == "Holt-Winters")].iloc[0]
    rows.append([str(fo), f"{int(h.K)} pairs, ARMA({int(h.p)},{int(h.q)})", f"({int(s.p)},0,{int(s.q)})({int(s.P)},1,{int(s.Q)})$_{{52}}$", f"{hw.trend}, $\\alpha$={hw.alpha:.2f}"])
write("specs", "llll", r"\textbf{Forecast year} & \textbf{Harmonic (by AIC)} & \textbf{SARIMA (by AIC)} & \textbf{Holt-Winters trend}", rows)

rm, mm_, pm_, me_ = [pd.read_csv(RES / f"fc_backtest_{k}.csv", index_col=0) for k in ("rmse", "mae", "mape", "me")]
rows = []
for m in MODELS:
    rows.append([m, f"{mm_.loc[m, '2017']:.1f}", f"{mm_.loc[m, '2018']:.1f}", f"{mm_.loc[m, '2019']:.1f}", f"{mm_.loc[m, 'mean 2018-19']:.1f}",
                 f"{rm.loc[m, 'mean 2018-19']:.1f}", f"{pm_.loc[m, 'mean 2018-19']:.0f}", neg(me_.loc[m, "mean 2018-19"])])
write("acc", "lrrrrrrr", r"\textbf{Model} & \textbf{2017} & \textbf{2018} & \textbf{2019} & \textbf{MAE} & \textbf{RMSE} & \textbf{MAPE\%} & \textbf{ME}", rows)

dmt = pd.read_csv(RES / "fc_dm.csv", index_col=0)
cov = pd.read_csv(RES / "fc_coverage.csv", index_col=0)
rows = []
for m in MODELS:
    p_ = "--" if m == "Seasonal mean" else f"{dmt.loc[m, 'DM p-value']:.2f}"
    c_ = "--" if np.isnan(cov.loc[m, "2019"]) else f"{100 * cov.loc[m, '2019']:.0f}\\%"
    rows.append([m, f"{mm_.loc[m, 'mean 2018-19']:.1f}", neg(me_.loc[m, "mean 2018-19"]), p_, c_])
write("key", "lrrrr", r"\textbf{Model} & \textbf{MAE 18--19} & \textbf{ME 18--19} & \textbf{DM $p$ vs mean} & \textbf{coverage 2019}", rows)
rows = [[m, neg(r["mean MAE difference vs seasonal mean"]), neg(r["DM"], 2), f"{r['DM p-value']:.3f}", f"[{neg(r['bootstrap lo95'])}, {neg(r['bootstrap hi95'])}]"] for m, r in dmt.iterrows()]
write("dm_full", "lrrrr", r"\textbf{Model vs seasonal mean} & \textbf{mean diff.} & \textbf{DM} & \textbf{$p$} & \textbf{bootstrap 95\%}", rows)
rows = [r[:4] for r in rows]
write("dm", "lrrr", r"\textbf{Model vs seasonal mean} & \textbf{mean diff.} & \textbf{DM} & \textbf{$p$}", rows)

cov = pd.read_csv(RES / "fc_coverage.csv", index_col=0); wd = pd.read_csv(RES / "fc_width.csv", index_col=0)
rows = [[m, *(f"{100 * cov.loc[m, c]:.0f}\\%" for c in ("2017", "2018", "2019")), f"{wd.loc[m, '2019']:.0f}"] for m in MODELS if not np.isnan(cov.loc[m, "2019"])]
write("cover", "lrrrr", r"\textbf{Model} & \textbf{2017} & \textbf{2018} & \textbf{2019} & \textbf{width 2019}", rows)

lg_ = pd.read_csv(RES / "var_lag_selection.csv", index_col=0).loc[0:8]
rows = [[str(p), f"{r.AIC:.3f}", f"{r.BIC:.3f}"] for p, r in lg_.iterrows()]
write("varlag", "lrr", r"\textbf{lag $p$} & \textbf{AIC} & \textbf{BIC}", rows)

gv = pd.read_csv(RES / "granger_var.csv"); gc = pd.read_csv(RES / "granger_var_controls.csv")
rows = [[tex_pm(r["direction"]), f"{r['F']:.1f}", sci(r["p_value"])] for _, r in gv.iterrows()]
rows += [[tex_pm(r["direction"]).replace("(with temperature and rain)", r"(+ temp., rain)"), f"{r['F']:.1f}", sci(r["p_value"])] for _, r in gc.iterrows()]
write("granger", "lrr", r"\textbf{Direction (VAR(4), daily anomalies)} & \textbf{$F$} & \textbf{$p$}", rows)

nst = pd.read_csv(RES / "weekly_lag_nested.csv").iloc[0]
rows = [[r"$P_t$ on $P_{t-1}$", f"{nst.iloc[0]:.3f}", "--"],
        [r"$+\,W_{t-1},H_{t-1}$ (last week's weather)", f"{nst.iloc[1]:.3f}", f"$F={nst['F']:.2f}$, $p={nst['p_value']:.2f}$"],
        [r"weather of the same week only", f"{nst['R2 same-week weather only']:.3f}", "not known in advance"]]
write("nested", "lrr", r"\textbf{Weekly regression (anomalies)} & \textbf{$R^2$} & \textbf{test}", rows)

row_names = {"Persistence": "Persistence", "Seasonal mean": "Seasonal mean", "Harmonic, no weather": "Harmonic, no weather",
             "+ last week's weather": "+ last week's weather", "+ same-week weather (oracle)": "+ same-week weather (unknown)"}
rows = [[row_names[m], f"{r['2018']:.1f}", f"{r['2019']:.1f}", f"{r['both years']:.1f}", ("--" if np.isnan(r["DM p vs no weather"]) else f"{r['DM p vs no weather']:.2f}")]
        for m, r in ow.iterrows()]
write("oneweek", "lrrrr", r"\textbf{One-week-ahead model} & \textbf{MAE 2018} & \textbf{MAE 2019} & \textbf{MAE both} & \textbf{DM $p$}", rows)

rows = []
for m in MODELS:
    r = lk.loc[m]
    rows.append([m, f"{r['MAE Jan-Feb 2020']:.1f}", neg(r["bias Jan-Mar 2020 (%)"], 0) + "\\%", neg(r["lockdown gap (%)"], 0) + "\\%",
                 neg(r["same weeks of 2019 (%)"], 0) + "\\%", f"{neg(r['typical 10-week gap 2017-19: 5th pct'], 0)} to {neg(r['typical 10-week gap 2017-19: 95th pct'], 0)}\\%"])
write("lock", "lrrrrr", r"\textbf{Model} & \textbf{MAE Jan--Feb} & \textbf{bias to Mar} & \textbf{lockdown gap} & \textbf{2019 same weeks} & \textbf{usual gap range}", rows)

# ═══ number macros ═════════════════════════════════════════════════════════════════════════════════════
W3 = {"2017": "Seventeen", "2018": "Eighteen", "2019": "Nineteen", "mean 2018-19": "Avg"}
SHORT = {"Seasonal naive": "Naive", "Seasonal mean": "Mean", "Holt-Winters": "HW", "SARIMA": "Sarima", "Harmonic regression": "Harm", "Combination": "Comb"}
nums = {
    "nDays": f"{eda['n_days']:,}".replace(",", "{,}"), "nWeeks": str(eda["n_weeks"]), "nWeeksModel": str(eda["n_weeks_model"]), "nTrain": str(eda["n_weeks_train"]),
    "pctPoor": f"{eda['pct_days_poor_or_worse']:.0f}", "pmMean": f"{eda['pm25_mean_2015_2019']:.0f}",
    "winterMean": f"{eda['winter_mean_pm25']:.0f}", "monsoonMean": f"{eda['monsoon_mean_pm25']:.0f}", "ratioWM": f"{eda['winter_to_monsoon_ratio']:.1f}",
    "skewRaw": f"{eda['skew_raw']:.2f}", "skewLog": neg(eda["skew_log"], 2), "corrRaw": f"{eda['corr_mean_sd_raw']:.2f}", "corrLog": neg(eda["corr_mean_sd_log"], 2),
    "sdRatioRaw": f"{eda['sd_ratio_raw']:.1f}", "sdRatioLog": f"{eda['sd_ratio_log']:.1f}", "Fs": f"{eda['seasonal_strength']:.2f}", "Ft": f"{eda['trend_strength']:.2f}",
    "seasRatio": f"{eda['stl_seasonal_ratio']:.0f}", "declAll": f"{abs(eda['decline_2016_2019_pct']):.0f}",
    "acfOne": f"{eda['acf_lag1']:.2f}", "acfHalf": neg(eda["acf_lag26"], 2), "acfYear": f"{eda['acf_lag52']:.2f}", "acfDOne": f"{eda['acf_d52_lag1']:.2f}",
    "adfPLog": sci(eda["adf_p_log"]), "kpssLog": f"{eda['kpss_stat_log']:.3f}", "adfPDiff": sci(eda["adf_p_d52"]), "kpssDiff": f"{eda['kpss_stat_d52']:.3f}",
    "stnFirst": str(eda["stations_by_year"]["2015"]), "stnSecond": str(eda["stations_by_year"]["2016"]), "stnLast": str(eda["stations_by_year"]["2019"]),
    "varLagAic": str(var["var_lag_aic"]), "varLagBic": str(var["var_lag_bic"]), "portP": f"{var['portmanteau_p']:.2f}",
    "spearWind": neg(var["spearman_pm25_wind"], 2), "spearRh": neg(var["spearman_pm25_rh"], 2),
    "gWindP": sci(var["granger"]["Wind → PM2.5"]), "gRhP": sci(var["granger"]["Humidity → PM2.5"]), "gBothP": sci(var["granger"]["Wind + Humidity → PM2.5"]),
    "gRevWindP": f"{var['granger']['PM2.5 → Wind']:.2f}", "gRevRhP": f"{var['granger']['PM2.5 → Humidity']:.2f}",
    "gWindPc": sci(var["granger_controls"]["Wind → PM2.5 (with temperature and rain)"]), "gRhPc": sci(var["granger_controls"]["Humidity → PM2.5 (with temperature and rain)"]),
    "nestRone": f"{nst.iloc[0]:.3f}", "nestRtwo": f"{nst.iloc[1]:.3f}", "nestDR": f"{nst['delta R2']:.3f}", "nestP": f"{nst['p_value']:.2f}", "nestRsame": f"{nst['R2 same-week weather only']:.2f}",
    "sarMA": neg(fcn["sarima_seasonal_ma"], 2), "sarMASE": f"{fcn['sarima_seasonal_ma_se']:.0f}",
    "lbAll": sci(fcn["lb_all_lag10"]), "lbTen": f"{fcn['lb_drop_lag10']:.2f}", "lbTwentySix": f"{fcn['lb_drop_lag26']:.2f}", "lbFiftyTwo": f"{fcn['lb_drop_lag52']:.3f}",
}
for m, sh in SHORT.items():
    for c, w in W3.items():
        nums[f"mae{sh}{w}"] = f"{mm_.loc[m, c]:.1f}"
    nums[f"rmse{sh}Avg"] = f"{rm.loc[m, 'mean 2018-19']:.1f}"; nums[f"mape{sh}Avg"] = f"{pm_.loc[m, 'mean 2018-19']:.0f}"; nums[f"me{sh}Avg"] = neg(me_.loc[m, "mean 2018-19"])
    if not np.isnan(cov.loc[m, "2019"]):
        for c, w in W3.items():
            if c in cov.columns:
                nums[f"cov{sh}{w}"] = f"{100 * cov.loc[m, c]:.0f}"
for m, r in dmt.iterrows():
    nums[f"dmP{SHORT[m]}"] = f"{r['DM p-value']:.2f}"; nums[f"dmD{SHORT[m]}"] = neg(r["mean MAE difference vs seasonal mean"])
bestm = mm_["mean 2018-19"].idxmin()
for c, w in (("2017", "Seventeen"), ("2018", "Eighteen"), ("2019", "Nineteen")):
    cc = cov[c].dropna()
    nums[f"covMin{w}"] = f"{100 * cc.min():.0f}"; nums[f"covMax{w}"] = f"{100 * cc.max():.0f}"
nums["bestAvgModel"] = bestm
for m, sh in SHORT.items():
    if not np.isnan(wd.loc[m, "2019"]):
        nums[f"width{sh}Nineteen"] = f"{wd.loc[m, '2019']:.0f}"; nums[f"width{sh}Seventeen"] = f"{wd.loc[m, '2017']:.0f}"
nums["hwGamma"] = sci(float(specs[(specs.fold == 2019) & (specs.model == "Holt-Winters")].gamma.iloc[0]))
nums["hwAlpha"] = f"{float(specs[(specs.fold == 2019) & (specs.model == 'Holt-Winters')].alpha.iloc[0]):.2f}"
# one week ahead
nums.update({"onePers": f"{ow.loc['Persistence', 'both years']:.1f}", "oneMean": f"{ow.loc['Seasonal mean', 'both years']:.1f}", "oneNo": f"{ow.loc['Harmonic, no weather', 'both years']:.1f}",
             "oneLag": f"{ow.loc[chr(43) + ' last week' + chr(39) + 's weather', 'both years']:.1f}", "oneOracle": f"{ow.loc['+ same-week weather (oracle)', 'both years']:.1f}",
             "oneLagPct": neg(ow.loc["+ last week's weather", "change vs no weather (%)"]), "oneOraclePct": neg(ow.loc["+ same-week weather (oracle)", "change vs no weather (%)"]),
             "oneLagP": f"{ow.loc[chr(43) + ' last week' + chr(39) + 's weather', 'DM p vs no weather']:.2f}", "oneOracleP": f"{ow.loc['+ same-week weather (oracle)', 'DM p vs no weather']:.2f}"})
# 2020
H = lk.loc["Harmonic regression"]; Sm = lk.loc["Seasonal mean"]
nums.update({"lockActual": f"{H['actual lockdown mean']:.0f}", "lockFcHarm": f"{H['forecast lockdown mean']:.0f}", "lockFcMean": f"{Sm['forecast lockdown mean']:.0f}",
             "lockGapHarm": neg(H["lockdown gap (%)"], 0), "lockGapMean": neg(Sm["lockdown gap (%)"], 0),
             "lockGapMin": neg(lk["lockdown gap (%)"].max(), 0), "lockGapMax": neg(lk["lockdown gap (%)"].min(), 0),
             "lockPreHarm": neg(H["bias Jan-Mar 2020 (%)"], 0), "lockAdjMin": neg(lk["gap after removing pre-lockdown bias (%)"].max(), 0), "lockAdjMax": neg(lk["gap after removing pre-lockdown bias (%)"].min(), 0), "lockAdjHarm": neg(H["gap after removing pre-lockdown bias (%)"], 0),
             "lockPlaceboHarm": neg(H["same weeks of 2019 (%)"], 0), "janMaeMin": f"{lk['MAE Jan-Feb 2020'].min():.0f}", "janMaeMax": f"{lk['MAE Jan-Feb 2020'].max():.0f}", "preBiasLo": f"{abs(lk['bias Jan-Mar 2020 (%)'].max()):.0f}", "preBiasHi": f"{abs(lk['bias Jan-Mar 2020 (%)'].min()):.0f}", "preBiasMin": neg(lk["bias Jan-Mar 2020 (%)"].max(), 0), "preBiasMax": neg(lk["bias Jan-Mar 2020 (%)"].min(), 0), "janMaeHarm": f"{H['MAE Jan-Feb 2020']:.1f}", "janMaeMean": f"{Sm['MAE Jan-Feb 2020']:.1f}",
             "lockUsualLo": neg(win[win.model == "Harmonic regression"].gap_pct.quantile(0.05), 0), "lockUsualHi": neg(win[win.model == "Harmonic regression"].gap_pct.quantile(0.95), 0),
             "lockWinMinHarm": neg(win[win.model == "Harmonic regression"].gap_pct.min(), 0), "lockWinMin": neg(win.gap_pct.min(), 0), "lockWinMax": neg(win.gap_pct.max(), 0)})
# worked example: calendar week 3 (mid-January)
EXW = 3
exs = {yr: float(tr_raw[(tr_raw.index.year == yr) & (week_index(tr_raw.index) == EXW)].iloc[0]) for yr in (2015, 2016, 2017, 2018)}
nums.update({"exWeek": str(EXW), **{f"exY{chr(97 + i)}": f"{v:.0f}" for i, v in enumerate(exs.values())},
             "exMean": f"{np.exp(np.mean(np.log(list(exs.values())))):.0f}", "exNaive": f"{exs[2018]:.0f}"})
nums["declWeeks"] = str(len(weekly.loc["2020-01-01":]))
for L_, r_ in idn.iterrows():
    nums[f"aic{L_[0]}"] = f"{r_.AIC:.1f}"
nums["aicBest"] = f"{idn.AIC.min():.1f}"; nums["aicGap"] = f"{np.sort(idn.AIC.to_numpy())[1] - idn.AIC.min():.1f}"
kk_ = specs[specs.model == "Harmonic regression"].K
nums["kHarmLo"], nums["kHarmHi"] = f"{int(kk_.min())}", f"{int(kk_.max())}"
for m_, sh_ in (("Holt-Winters", "HW"), ("SARIMA", "Sarima"), ("Harmonic regression", "Harm"), ("Seasonal mean", "Mean")):
    g_ = win[win.model == m_].gap_pct
    nums[f"lockShare{sh_}"] = f"{100 * (g_ <= lk.loc[m_, 'lockdown gap (%)']).mean():.0f}"
    nums[f"lockShareAdj{sh_}"] = f"{100 * (g_ <= lk.loc[m_, 'gap after removing pre-lockdown bias (%)']).mean():.0f}"
    nums[f"lockMin{sh_}"] = neg(g_.min(), 0)
(TAB / "numbers.tex").write_text("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in nums.items()) + "\n")
print("figures:", sorted(p.name for p in FIG.glob("*.pdf")))
print("numbers:", len(nums))
