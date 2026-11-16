"""Slide-sized vector figures and LaTeX tables for the Beamer deck.

Each figure is drawn at the size it appears on the slide (14.6 cm wide) with 9-10 pt fonts, so labels are as
readable as the slide text. Numbers come from data/processed and results/, never typed by hand.
Run after notebooks 02-03:  .venv/bin/python slides/beamer/make_figures.py
"""
import sys
import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.dates  # noqa: F401
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from statsmodels.tsa.api import VAR
from statsmodels.tsa.seasonal import STL

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from src.aqi import band_edges  # noqa: E402
from src.plots import AXIS, AQUA, BLUE, INK, INK_2, MUTED, NEUTRAL, ORANGE, SEASON_COLORS, use_style  # noqa: E402
from src.data import SEASONS, OTHER_SEASON  # noqa: E402
from src.tsa import doy_anomaly  # noqa: E402

warnings.filterwarnings("ignore")
FIG, TAB = HERE / "fig", HERE / "tables"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)
W_CM = 14.6
CM = 1 / 2.54

use_style()
mpl.rcParams.update({
    "font.size": 10, "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.fontsize": 9,
    "axes.titlesize": 10, "axes.titleweight": "normal", "lines.linewidth": 1.8, "pdf.fonttype": 42,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
})

daily = pd.read_csv(ROOT / "data/processed/delhi_daily.csv", index_col="Date", parse_dates=True).asfreq("D")
weekly = pd.read_csv(ROOT / "data/processed/delhi_weekly.csv", index_col="Date", parse_dates=True)
RES = ROOT / "results"
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def new_fig(h_cm, nrows=1, ncols=1, w=None, **kw):
    return plt.subplots(nrows, ncols, figsize=((w or W_CM) * CM, h_cm * CM), layout="constrained", **kw)


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf")
    plt.close(fig)


def has(*names):
    return all((RES / n).exists() for n in names)


# logo.png is kept in the repo; to rebuild it: pdfimages -png -f 1 -l 1 Slides.pdf slides/beamer/logo
if (HERE / "logo-000.png").exists():
    rgb, mask = Image.open(HERE / "logo-000.png").convert("RGB"), Image.open(HERE / "logo-001.png").convert("L")
    rgb.putalpha(mask)
    rgb.save(HERE / "logo.png")

# ── 1. The problem: daily PM2.5 over CPCB AQI bands ────────────────────────────────────────────────────
fig, ax = new_fig(4.0)
ymax = 400
for name, lo, hi, colour in band_edges():
    if lo >= ymax:
        break
    ax.axhspan(lo, min(hi, ymax), color=colour, alpha=0.13, lw=0, zorder=0)
    ax.text(1.005, (lo + min(hi, ymax)) / 2, name, transform=ax.get_yaxis_transform(), va="center", fontsize=7, color=INK_2)
ax.plot(daily.index, daily["pm25"], color=BLUE, lw=0.6, alpha=0.5, label="Daily mean")
ax.plot(daily.index, daily["pm25"].rolling(30, center=True).mean(), color=BLUE, lw=2.2, label="30-day average")
ax.set_ylim(0, ymax)
ax.set_xlim(daily.index.min(), daily.index.max())
ax.set_ylabel("PM$_{2.5}$ (µg/m³)")
ax.legend(loc="upper left", ncols=2)
save(fig, "problem_aqi")

# ── 2. Seasonality: month boxplot (backup) and STL decomposition ───────────────────────────────────────
fig, ax = new_fig(5.0)
data = [daily.loc[daily.index.month == m, "pm25"].dropna() for m in range(1, 13)]
season_of_month = {m: n for n, ms in SEASONS.items() for m in ms}
bp = ax.boxplot(data, tick_labels=months, patch_artist=True, widths=0.65, showfliers=True,
                medianprops=dict(color=INK, lw=1.8), whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
                flierprops=dict(marker="o", markersize=2.5, markerfacecolor=MUTED, markeredgecolor="none", alpha=0.5))
for box, m in zip(bp["boxes"], range(1, 13)):
    box.set(facecolor=SEASON_COLORS[season_of_month.get(m, OTHER_SEASON)], edgecolor="white", linewidth=1.5)
ax.set_ylabel("PM$_{2.5}$ (µg/m³)")
ax.set_ylim(0, 720)
save(fig, "seasonal_boxplot")

stl = STL(weekly["log_pm25"], period=52, robust=True).fit()
fig, axes = new_fig(4.6, nrows=4, sharex=True)
for ax, (name, lab, s) in zip(axes, [("Observed", "log PM$_{2.5}$", stl.observed), ("Trend", "Trend", stl.trend),
                                      ("Seasonal", "Seasonal", stl.seasonal), ("Residual", "Residual", stl.resid)]):
    if name == "Residual":
        ax.vlines(s.index, 0, s, color=BLUE, lw=1.2)
    else:
        ax.plot(s.index, s, color=BLUE)
    ax.set_ylabel(lab, rotation=0, ha="right", va="center", fontsize=9, color=INK_2)
    ax.tick_params(axis="y", labelsize=8)
save(fig, "stl")

# ── 3. Why log: histograms of raw vs log PM2.5 with the best-fitting normal curve ─────────────────────
from scipy import stats as _st  # noqa: E402
pm = daily["pm25"].dropna()
lg = np.log(pm)
fig, axes = new_fig(4.1, ncols=2)
for ax, s, ttl, c, xl in [(axes[0], pm, "Raw PM$_{2.5}$", ORANGE, "µg/m³"), (axes[1], lg, "log PM$_{2.5}$", BLUE, "log units")]:
    ax.hist(s, bins=40, density=True, color=c, alpha=0.8, edgecolor="white", linewidth=0.5)
    xs = np.linspace(s.min(), s.max(), 300)
    ax.plot(xs, _st.norm.pdf(xs, s.mean(), s.std()), color=INK, lw=1.6, label="normal curve with same mean and SD")
    sk = float(((s - s.mean()) ** 3).mean() / s.std(ddof=0) ** 3)
    ax.set_title(f"{ttl}: skewness {sk:+.2f}", loc="left", color=INK)
    ax.set_xlabel(xl)
    ax.set_yticks([])
    ax.grid(False)
h_, l_ = axes[0].get_legend_handles_labels()
fig.legend(h_, l_, loc="outside lower center", frameon=False, fontsize=8)
save(fig, "why_log")

# ── 4. Volatility: monthly SD, raw vs log ──────────────────────────────────────────────────────────────
bm = pd.read_csv(RES / "monthly_mean_sd.csv", index_col=0)
fig, axes = new_fig(3.1, ncols=2)
for ax, col, ttl, c, ylab in [(axes[0], "sd_raw", "Raw PM$_{2.5}$", ORANGE, "SD (µg/m³)"),
                              (axes[1], "sd_log", "log PM$_{2.5}$", BLUE, "SD (log units)")]:
    ax.bar(range(1, 13), bm[col], color=c, width=0.7)
    ax.set_xticks(range(1, 13), [m[0] for m in months])
    ratio = bm[col].max() / bm[col].min()
    ax.set_title(f"{ttl}: largest / smallest = {ratio:.1f}×", loc="left", color=INK)
    ax.set_ylabel(ylab, fontsize=9)
    ax.grid(axis="x", visible=False)
save(fig, "volatility_sd")

# ── 5. Stationarity: weekly log PM2.5 (training years) with rolling mean and SD ────────────────────────
lw_tr = weekly.loc[:"2018-12-31", "log_pm25"]
roll_m, roll_s = lw_tr.rolling(52).mean(), lw_tr.rolling(52).std()
fig, axes = new_fig(3.9, nrows=2, sharex=True, height_ratios=[1.7, 1])
axes[0].plot(lw_tr.index, lw_tr, color=NEUTRAL, lw=1.3, label="Weekly log PM$_{2.5}$")
axes[0].plot(roll_m.index, roll_m, color=BLUE, lw=2.4, label="52-week rolling mean")
axes[0].set_ylabel("log PM$_{2.5}$", fontsize=9)
axes[0].set_ylim(2.8, 6.8)
axes[1].plot(roll_s.index, roll_s, color=ORANGE, lw=2.4, label="52-week rolling SD")
axes[1].set_ylabel("SD", fontsize=9)
axes[1].set_ylim(0, 1.0)
import matplotlib.dates as mdates
axes[1].xaxis.set_major_locator(mdates.YearLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
h0, l0 = axes[0].get_legend_handles_labels()
h1, l1 = axes[1].get_legend_handles_labels()
fig.legend(h0 + h1, l0 + l1, loc="outside upper center", ncols=3, frameon=False)
save(fig, "stationarity")

# ── 6. Granger tests with robust (HAC) errors ──────────────────────────────────────────────────────────
if has("granger_hac.csv"):
    gh = pd.read_csv(RES / "granger_hac.csv")
    pick = [("Wind → PM2.5", "PM2.5, wind, humidity", "Wind → PM$_{2.5}$"),
            ("Humidity → PM2.5", "PM2.5, wind, humidity", "Humidity → PM$_{2.5}$"),
            ("Humidity → PM2.5", "+ rain control", "Humidity → PM$_{2.5}$, rain controlled"),
            ("Rain → PM2.5", "+ rain control", "Rain → PM$_{2.5}$ (given wind, humidity)"),
            ("PM2.5 → Wind", "PM2.5, wind, humidity", "PM$_{2.5}$ → Wind"),
            ("PM2.5 → Humidity", "PM2.5, wind, humidity", "PM$_{2.5}$ → Humidity")]
    rows = [(lab.replace(' → ', r' $\to$ '), float(gh[(gh.direction == d_) & (gh.spec == s_)].p_value.iloc[0])) for d_, s_, lab in pick][::-1]
    fig, ax = new_fig(4.1)
    score = [-np.log10(p) for _, p in rows]
    ax.barh([r[0] for r in rows], score, color=[BLUE if p < 0.05 else NEUTRAL for _, p in rows], height=0.5)
    ax.axvline(-np.log10(0.05), color=ORANGE, lw=1.6)
    ax.text(-np.log10(0.05) + 0.3, len(rows) - 0.35, "p = 0.05", color=ORANGE, fontsize=8, va="bottom")
    for i, (s_, (_, p)) in enumerate(zip(score, rows)):
        if p < 1e-10:
            lab = r"$p<10^{-10}$"
        elif p < 1e-3:
            m_, e_ = f"{p:.0e}".split("e")
            lab = rf"$p={m_}\times10^{{{int(e_)}}}$"
        else:
            lab = f"p = {p:.2f}, not significant"
        ax.text(max(s_ + 0.3, 2.0), i, lab, va="center", fontsize=8, color=INK)
    ax.set_xlim(0, 27)
    ax.set_xlabel("Evidence: $-\\log_{10}(p)$ (longer = stronger)")
    ax.grid(axis="y", visible=False)
    save(fig, "granger_hac")

# ── 7. What a shock is, and what happens after one ─────────────────────────────────────────────────────
d = daily.loc[:"2019-12-31"]
anom = pd.DataFrame({"wind": doy_anomaly(d["wind"]), "rh": doy_anomaly(d["rh"]), "pm25": doy_anomaly(d["log_pm25"])})
var4 = VAR(anom).fit(4)
wind_clim = d["wind"] - anom["wind"]
wind_pred = wind_clim.loc[var4.fittedvalues.index] + var4.fittedvalues["wind"]
resid = var4.resid
z = resid / resid.std()
fig, axes = new_fig(4.6, ncols=2, width_ratios=[1.1, 1])
seg = slice("2019-01-14", "2019-01-27")
ax = axes[0]
ax.plot(d.loc[seg].index, d.loc[seg, "wind"], color=ORANGE, marker="o", ms=4, label="Actual wind")
ax.plot(wind_pred.loc[seg].index, wind_pred.loc[seg], color=INK_2, ls="--", marker="s", ms=3, label="Predicted from the past")
t0 = pd.Timestamp("2019-01-21")
ax.annotate("", xy=(t0, d.loc[t0, "wind"]), xytext=(t0, wind_pred.loc[t0]), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.4))
ax.text(t0, 20.3, f"expected {wind_pred.loc[t0]:.1f}, actual {d.loc[t0, 'wind']:.1f}\nshock = +{d.loc[t0, 'wind'] - wind_pred.loc[t0]:.1f} km/h", fontsize=8, ha="center", va="center")
ax.set_ylabel("Wind speed (km/h)")
ax.set_ylim(3, 23)
ticks = pd.date_range("2019-01-14", "2019-01-27", freq="4D")
ax.set_xticks(ticks)
ax.set_xticklabels([x.strftime("%d %b") for x in ticks])
ax.set_title("Shock = actual minus predicted", loc="left", color=INK)
ax = axes[1]
edges = [-np.inf, -1.5, -0.75, -0.25, 0.25, 0.75, 1.5, np.inf]
fut = anom["pm25"].shift(-1) - anom["pm25"].shift(1)  # change in log PM2.5 from day t-1 to day t+1
curves = {}
for nm, col, lab in [("wind", ORANGE, "wind shock"), ("rh", AQUA, "humidity shock")]:
    zz = z[nm]
    bins = pd.cut(zz, edges)
    g = pd.DataFrame({"z": zz, "y": fut.loc[zz.index], "bin": bins}).dropna().groupby("bin", observed=True)
    xm = g["z"].mean().to_numpy()
    ym, ys, n = g["y"].mean().to_numpy(), g["y"].std().to_numpy(), g["y"].count().to_numpy()
    se = ys / np.sqrt(n)
    ax.errorbar(xm + (0.04 if nm == "rh" else -0.04), (np.exp(ym) - 1) * 100, yerr=[(np.exp(ym) - np.exp(ym - 1.96 * se)) * 100, (np.exp(ym + 1.96 * se) - np.exp(ym)) * 100],
                color=col, marker="o", ms=4.5, lw=1.5, capsize=2.5, label=lab)
    curves[nm] = {"z": xm.round(2).tolist(), "pct": ((np.exp(ym) - 1) * 100).round(1).tolist(), "n": n.tolist()}
ax.axhline(0, color=INK_2, lw=0.9)
ax.axvline(0, color=MUTED, lw=0.9, ls=":")
ax.set_xlabel("Shock size (SDs; 0 = as predicted)")
ax.set_ylabel("PM$_{2.5}$ change (%)")
ax.set_title("Bigger shock, bigger fall in PM$_{2.5}$", loc="left", color=INK)
ax.set_ylim(-34, 50)
ax.legend(loc="upper right", fontsize=8)
save(fig, "shock_example")
import json
(RES / "shock_binned.json").write_text(json.dumps({"curves": curves, "jan21_shock_kmh": float(d.loc[t0, "wind"] - wind_pred.loc[t0]),
                                                  "jan21_wind": float(d.loc[t0, "wind"]), "jan21_pred": float(wind_pred.loc[t0])}, indent=1))

# ── 8. Impulse responses, with the range across the two orderings ──────────────────────────────────────
H = 10
idx = {c: i for i, c in enumerate(anom.columns)}
irf = var4.irf(H)
se_ = irf.stderr(orth=True)
alt_order = ["pm25", "wind", "rh"]
var_alt = VAR(anom[alt_order]).fit(4)
irf_alt = var_alt.irf(H).orth_irfs
sd = np.sqrt(np.diag(var4.sigma_u))
fig, axes = new_fig(4.3, ncols=2, sharey=True)
for ax, imp, c, ttl in [(axes[0], "wind", ORANGE, f"+1 SD wind shock ({sd[idx['wind']]:.1f} km/h)"),
                        (axes[1], "rh", AQUA, f"+1 SD humidity shock ({sd[idx['rh']]:.1f}% RH)")]:
    r, s = irf.orth_irfs[:H + 1, idx["pm25"], idx[imp]], se_[:H + 1, idx["pm25"], idx[imp]]
    pct = (np.exp(r) - 1) * 100
    lo, hi = (np.exp(r - 1.96 * s) - 1) * 100, (np.exp(r + 1.96 * s) - 1) * 100
    alt = (np.exp(irf_alt[:H + 1, alt_order.index("pm25"), alt_order.index(imp)]) - 1) * 100
    h = np.arange(H + 1)
    ax.fill_between(h, lo, hi, color=c, alpha=0.18, lw=0)
    ax.plot(h, pct, color=c, marker="o", ms=4, label="Weather ordered first (95% band)")
    ax.plot(h, alt, color=INK_2, ls="--", marker="s", ms=3, label="PM$_{2.5}$ ordered first (lagged effect only)")
    ax.axhline(0, color=INK_2, lw=0.9)
    ax.set_title(ttl, loc="left", color=INK)
    ax.set_xlabel("Days after the shock")
axes[0].set_ylabel("PM$_{2.5}$ change (%)")
axes[0].set_ylim(-14.5, 3)
h_, l_ = axes[0].get_legend_handles_labels()
fig.legend(h_, l_, loc="outside lower center", ncols=2, frameon=False, fontsize=8)
save(fig, "irf_range")

# ── tables ─────────────────────────────────────────────────────────────────────────────────────────────
def sci(p):
    if p < 1e-3:
        m, e = f"{p:.1e}".split("e")
        return rf"${m}\times10^{{{int(e)}}}$"
    return f"{p:.3f}" if p < 0.1 else f"{p:.2f}"


def write(name, spec, header, rows):
    body = " \\\\\n".join(" & ".join(str(c) for c in r) for r in rows)
    (TAB / f"{name}.tex").write_text(f"\\begin{{tabular}}{{{spec}}}\n\\toprule\n{header} \\\\\n\\midrule\n{body} \\\\\n\\bottomrule\n\\end{{tabular}}\n")


tex_pm = lambda s: s.replace("→", r"$\to$").replace("PM2.5", r"PM$_{2.5}$")  # noqa: E731

# stationarity (training years)
st = pd.read_csv(RES / "stationarity_train.csv", index_col=0)
labs = {"Weekly log PM2.5 (train)": r"log PM$_{2.5}$ (level)", "Weekly Δ₅₂ log PM2.5 (D=1)": r"seasonal difference $\Delta_{52}$",
        "Weekly Δ Δ₅₂ log PM2.5 (d=1, D=1)": r"$\Delta\Delta_{52}$ (over-differenced)"}
rows = []
for k, lab in labs.items():
    r = st.loc[k]
    rows.append([lab, f"{r['adf_stat']:.2f}", f"{r['adf_crit_5%']:.2f}", sci(r["adf_p"]), f"{r['kpss_p']:.2f}", f"{r['lag1_acf']:.2f}"])
write("stationarity", "lrrrrr", r"\textbf{Weekly series, 2015--18} & \textbf{ADF stat} & \textbf{5\% crit.} & \textbf{ADF $p$} & \textbf{KPSS $p$} & \textbf{lag-1 ACF}", rows)

# variance / volatility tests with plain-English column
lt = pd.read_csv(RES / "log_justification.csv", index_col=0)
q = {"corr(monthly mean, monthly SD)": r"Does spread grow with level? (corr.\ of monthly mean and SD)",
     "Levene F (equal variance across months)": r"Is the spread equal in all 12 months? (Levene $F$)",
     "ARCH-LM statistic (7 lags, on daily change)": r"Do big changes cluster in time? (ARCH-LM)"}
rows = [[lab, f"{lt.loc[k].iloc[0]:.2f}", f"{lt.loc[k].iloc[1]:.2f}"] for k, lab in q.items()]
write("log_tests", "lrr", r"\textbf{Question the test asks} & \textbf{Raw} & \textbf{Log}", rows)

# Granger (HAC) robustness, for the backup slide
if has("granger_hac.csv"):
    gh = pd.read_csv(RES / "granger_hac.csv")
    rows = [[tex_pm(r["direction"]), tex_pm(r["spec"]), f"{r['wald_chi2']:.1f}", sci(r["p_value"])] for _, r in gh.iterrows()]
    write("granger_robust", "llrr", r"\textbf{Direction} & \textbf{Model} & \textbf{Wald $\chi^2$} & \textbf{$p$ (HAC)}", rows)

# IRF/FEVD under both orderings, for the backup slide
if has("irf_orderings.csv", "fevd_orderings.csv"):
    io = pd.read_csv(RES / "irf_orderings.csv")
    fo = pd.read_csv(RES / "fevd_orderings.csv")
    rows = []
    for shock in ["Wind", "Humidity"]:
        a = io[(io.shock == shock) & io.ordering.str.startswith("weather")].iloc[0]
        b = io[(io.shock == shock) & io.ordering.str.startswith("PM2.5")].iloc[0]
        w_ = fo[(fo.variable == shock) & fo.ordering.str.startswith("weather")].share_h14_pct.iloc[0]
        p_ = fo[(fo.variable == shock) & fo.ordering.str.startswith("PM2.5")].share_h14_pct.iloc[0]
        rows.append([f"+1 SD {shock.lower()} shock", f"{a.day1_pct:.0f}\\%", f"{b.day1_pct:.0f}\\%", f"{w_:.0f}\\%", f"{p_:.0f}\\%"])
    write("orderings", "lcccc", r"\textbf{Shock} & \textbf{Day 1: W-first} & \textbf{Day 1: P-first} & \textbf{14-day share: W-first} & \textbf{14-day share: P-first}", rows)

# ── Phase 4 (forecasting) figures, tables and numbers ─────────────────────────────────────────────────
import json as _json  # noqa: E402

FCN = _json.loads((RES / "key_numbers_forecast.json").read_text()) if has("key_numbers_forecast.json") else None
if FCN is not None:
    from matplotlib.patches import Patch  # noqa: E402
    fb = pd.read_csv(RES / "fc_backtest_forecasts.csv", parse_dates=["date"])
    fm = pd.read_csv(RES / "fc_backtest_metrics.csv")
    SELN = "Fourier+ARMA (selected)"

    # 1. backtest: 2019 forecast + MAE by fold
    f19s = fb[(fb.fold == 2019) & (fb.model == SELN)].set_index("date")
    f19c = fb[(fb.fold == 2019) & (fb.model == "Climatology")].set_index("date")
    fig, axes = new_fig(5.0, ncols=2, width_ratios=[1.5, 1])
    ax = axes[0]
    ax.fill_between(f19s.index, np.exp(f19s.mu - 1.96 * f19s.sd), np.exp(f19s.mu + 1.96 * f19s.sd), color=BLUE, alpha=0.18, lw=0, label="95% interval")
    ax.plot(f19s.index, np.exp(f19s.mu), color=BLUE, label="Fourier+ARMA")
    ax.plot(f19c.index, np.exp(f19c.mu), color=NEUTRAL, ls="--", lw=1.3, label="Climatology")
    ax.plot(f19s.index, f19s.actual, color=ORANGE, marker="o", ms=2.5, lw=1.2, label="Actual 2019")
    ax.set_ylabel("Weekly PM$_{2.5}$ ($\\mu$g/m$^3$)")
    ax.set_title("52-week forecast made on 30 Dec 2018", loc="left", color=INK)
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%b")); ax.set_ylim(0, 470); ax.legend(fontsize=6.5, ncols=2, loc="upper center")
    ax = axes[1]
    show = [("Climatology", "Clim."), (SELN, "Fourier"), ("SARIMA D=1", "SARIMA1"), ("SARIMA D=0", "SARIMA0"), ("LSTM (small)", "LSTM")]
    x_ = np.arange(len(show)); w_ = 0.27
    for k, (fo, c) in enumerate([(2017, NEUTRAL), (2018, AQUA), (2019, BLUE)]):
        ax.bar(x_ + (k - 1) * w_, [fm[(fm.fold == fo) & (fm.model == m)].MAE.iloc[0] for m, _ in show], w_, color=c, label=str(fo))
    ax.set_xticks(x_, [s for _, s in show], fontsize=6.5); ax.set_ylabel("MAE ($\\mu$g/m$^3$)"); ax.set_ylim(0, 80); ax.legend(title="forecast year", fontsize=6.5, title_fontsize=6.5, ncols=3, loc="upper left")
    ax.set_title("Error by forecast year", loc="left", color=INK)
    save(fig, "fc_backtest")

    # 2. one week ahead
    ow = pd.read_csv(RES / "fc_oneweek.csv", index_col=0)
    order_ = ["Persistence", "Climatology", "Climatology + AR(1)", "DHR, no weather", "+ lagged weather (operational)", "+ last 3 days of prior week (operational)", "+ same-week weather (ORACLE)"]
    labs_ = ["Persis-\ntence", "Clima-\ntology", "Clim.\n+AR(1)", "Fourier\nARMA", "+ lagged\nweather", "+ last 3\ndays", "+ same-week\n(oracle)"]
    fig, ax = new_fig(4.4)
    ax.bar(range(7), [ow.loc[m, "both years"] for m in order_], color=[NEUTRAL, NEUTRAL, NEUTRAL, BLUE, AQUA, AQUA, ORANGE], width=0.65)
    for i, m in enumerate(order_):
        ax.text(i, ow.loc[m, "both years"] + 0.4, f"{ow.loc[m, 'both years']:.1f}", ha="center", fontsize=8)
    ax.set_xticks(range(7), labs_, fontsize=7.5); ax.set_ylabel("MAE ($\\mu$g/m$^3$)"); ax.set_ylim(0, 35)
    ax.set_title("2018--19, one week ahead (lower is better)", loc="left", color=INK)
    save(fig, "fc_oneweek")

    # 3. 2020 outlook
    o20 = pd.read_csv(RES / "fc_outlook_2020.csv", index_col=0)
    fig, axes = new_fig(5.0, ncols=2, width_ratios=[1.3, 1])
    ax = axes[0]; xs = np.arange(12)
    ax.fill_between(xs, o20["lo95"], o20["hi95"], color=BLUE, alpha=0.18, lw=0)
    ax.plot(xs, o20["median"], color=BLUE, marker="o", ms=3.5, label="Forecast (median, 95% interval)")
    ok = o20["actual_days_covered"] >= 25
    ax.plot(xs[ok.to_numpy()], o20.loc[ok, "actual_mean_2020"], color=ORANGE, marker="s", ms=3.5, label="Actual 2020")
    for yv in (60, 90, 120):
        ax.axhline(yv, color=MUTED, lw=0.6, ls=":")
    ax.set_xticks(xs, [m[0] for m in months]); ax.set_ylabel("Monthly PM$_{2.5}$"); ax.legend(fontsize=7, loc="upper center")
    ax.set_title("Forecast made in Dec 2019", loc="left", color=INK)
    ax = axes[1]
    cols = {"Good": "#00B050", "Satisfactory": "#92D050", "Moderate": "#E6C200", "Poor": "#FF9900", "Very Poor": "#FF0000", "Severe": "#C00000"}
    bot = np.zeros(12)
    for c in cols:
        v = o20[f"days_{c}"].to_numpy(); ax.bar(xs, v, bottom=bot, color=cols[c], width=0.8); bot += v
    ax.set_xticks(xs, [m[0] for m in months]); ax.set_ylabel("Expected days"); ax.set_title("Days per PM$_{2.5}$ band", loc="left", color=INK)
    fig.legend([Patch(color=c) for c in cols.values()], list(cols), loc="outside lower center", ncols=6, frameon=False, fontsize=7)
    save(fig, "fc_outlook")

    # 4. lockdown
    w20 = pd.read_csv(RES / "fc_weekly_2020.csv", index_col=0, parse_dates=True) if has("fc_weekly_2020.csv") else None
    if w20 is not None:
        fig, ax = new_fig(4.6)
        ax.fill_between(w20.index, w20.lo95, w20.hi95, color=BLUE, alpha=0.18, lw=0, label="95% interval (no lockdown)")
        ax.plot(w20.index, w20["median"], color=BLUE, label="No-lockdown forecast")
        ax.plot(w20.index, w20.weather_adj_median, color=AQUA, ls="--", label="Weather-adjusted forecast")
        ax.plot(w20.index, w20.actual, color=ORANGE, marker="o", ms=3, label="Actual 2020")
        ax.axvspan(pd.Timestamp("2020-03-25"), pd.Timestamp("2020-05-31"), color=NEUTRAL, alpha=0.25, lw=0)
        ax.text(pd.Timestamp("2020-04-27"), ax.get_ylim()[1] * 0.93, "lockdown", ha="center", fontsize=8, color=INK_2)
        ax.set_ylabel("Weekly PM$_{2.5}$ ($\\mu$g/m$^3$)"); ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%b")); ax.legend(fontsize=7.5, ncols=2, loc="upper right")
        save(fig, "fc_lockdown")

    # 5. station check
    sc = pd.read_csv(RES / "station_check.csv", index_col=0)
    fig, axes = new_fig(4.2, ncols=2)
    axes[0].bar(sc.index, sc.stations, color=NEUTRAL, width=0.6); axes[0].set_title("Stations reporting PM$_{2.5}$", loc="left", color=INK)
    for lab, col, c in [("All stations", "all_log_anom", BLUE), ("Fixed 6-station panel", "panel_log_anom", ORANGE), ("City, weather-adjusted", "weather_adj_log_anom", AQUA)]:
        axes[1].plot(sc.index, sc[col], marker="o", ms=3.5, color=c, label=lab)
    axes[1].axhline(0, color=INK_2, lw=0.8); axes[1].set_ylabel("Mean log anomaly"); axes[1].legend(fontsize=7)
    axes[1].set_title("The decline persists on fixed monitors", loc="left", color=INK)
    save(fig, "fc_station")

    # tables
    ld = pd.read_csv(RES / "fc_loss_diff.csv"); ld = ld[ld.folds == "folds 2018+2019"].set_index("model")
    mae = pd.read_csv(RES / "fc_backtest_mae.csv", index_col=0)
    rows = []
    for m, lab in [("Climatology", "Climatology (benchmark)"), ("Climatology + AR(1)", r"Climatology + AR(1)"), ("Linear regression", "Linear regression"),
                   (SELN, "Fourier+ARMA (selected)"), ("SARIMA D=1", r"SARIMA $D=1$"), ("SARIMA D=0", r"SARIMA $D=0$ (+constant)"), ("LSTM (small)", "LSTM (small)"), ("Seasonal naive", "Seasonal naive")]:
        v = ld.loc[m, "verdict"] if m in ld.index else "reference"
        rows.append([lab] + [f"{mae.loc[m, c]:.1f}" for c in ["2017", "2018", "2019", "mean 2018-19"]] + [v])
    write("fc_backtest", "lrrrrl", r"\textbf{Model} & \textbf{2017} & \textbf{2018} & \textbf{2019} & \textbf{Mean 18--19} & \textbf{vs climatology}", rows)
    rows = []
    for m_, r in o20.iterrows():
        pp = r["days_Poor"] + r["days_Very Poor"] + r["days_Severe"]
        act = f"{r['actual_mean_2020']:.0f}" if r["actual_days_covered"] >= 25 else "--"
        rows.append([m_, f"{r['median']:.0f}", f"{r['lo95']:.0f}--{r['hi95']:.0f}", f"{r['P(mean>90)'] * 100:.0f}\\%", f"{pp:.0f}", act])
    write("fc_outlook", "lrrrrr", r"\textbf{Month} & \textbf{Median} & \textbf{95\% interval} & \textbf{P(mean$>$90)} & \textbf{Days Poor+} & \textbf{Actual}", rows)

    ck = pd.read_csv(RES / "fc_calibration_2019.csv", index_col=0)
    nums_fc = {
        "fcMaeSelNineteen": f"{FCN['backtest']['mae_selected']['2019']:.1f}", "fcMaeClimNineteen": f"{FCN['backtest']['mae_climatology']['2019']:.1f}",
        "fcMaeSarimaNineteen": f"{FCN['backtest']['sarima_D1_mae']['2019']:.1f}", "fcMaeSarimaSeventeen": f"{FCN['backtest']['sarima_D1_mae']['2017']:.0f}",
        "fcMaeLstmNineteen": f"{FCN['backtest']['lstm_mae']['2019']:.0f}", "fcMaeSarimaZeroNineteen": f"{FCN['backtest']['sarima_D0_mae']['2019']:.0f}",
        "fcCovRaw": f"{FCN['coverage_2019_raw'] * 100:.0f}", "fcCovCal": f"{FCN['coverage_2019_calibrated'] * 100:.0f}",
        "fcMaSE": f"{FCN['sarima_D1_maS_se']:.1f}", "fcMaCoef": f"{FCN['sarima_D1_maS_coef']:.3f}".replace("-", "$-$"),
        "fcOneLagged": f"{FCN['oneweek_gain_pct']['lagged']:+.1f}".replace("-", "$-$"), "fcOneLastThree": f"{FCN['oneweek_gain_pct']['last3']:+.1f}".replace("-", "$-$"),
        "fcOneOracle": f"{FCN['oneweek_gain_pct']['oracle']:+.1f}",
        "fcLockPct": f"{abs(FCN['lockdown']['plain']['gap_median_pct']):.0f}", "fcLockLo": f"{abs(FCN['lockdown']['plain']['gap_hi95_pct']):.0f}", "fcLockHi": f"{abs(FCN['lockdown']['plain']['gap_lo95_pct']):.0f}",
        "fcLockWxPct": f"{abs(FCN['lockdown']['weather_adjusted']['gap_median_pct']):.0f}",
        "fcValPoorPred": f"{FCN['validation_2019']['poor_or_worse_pred_pct']:.0f}", "fcValPoorAct": f"{FCN['validation_2019']['poor_or_worse_actual_pct']:.0f}",
        "fcValInside": f"{FCN['validation_2019']['months_actual_inside_95']}",
    }
    sk = _json.loads((RES / "key_numbers_eda.json").read_text())
    nums_fc.update({"declAll": f"{abs(sk['decline_2016_2019_pct']['all_stations']):.0f}", "declPanel": f"{abs(sk['decline_2016_2019_pct']['fixed_panel']):.0f}",
                    "declWx": f"{abs(sk['decline_2016_2019_pct']['weather_adjusted']):.0f}"})
    FC_NUMS = nums_fc
else:
    FC_NUMS = {}

print("figures:", sorted(p.name for p in FIG.glob("*.pdf")))

# ── numbers used in the slide text (single source of truth) ────────────────────────────────────────────
import json  # noqa: E402

def jl(name):
    return json.loads((RES / name).read_text())


eda, var_k = jl("key_numbers_eda.json"), jl("key_numbers_var.json")
nums = {
    "pctPoor": f"{eda['pct_days_poor_or_worse']:.0f}", "winterMean": f"{eda['winter_mean_pm25']:.0f}", "monsoonMean": f"{eda['monsoon_mean_pm25']:.0f}",
    "ratioWM": f"{eda['winter_to_monsoon_ratio']:.1f}", "Fs": f"{eda['seasonal_strength']:.2f}",
}
lt_ = pd.read_csv(RES / "log_justification.csv", index_col=0)
nums.update({
    "skewRaw": f"{lt_.loc['Skewness'].iloc[0]:+.2f}", "skewLog": f"{lt_.loc['Skewness'].iloc[1]:+.2f}".replace("-", "$-$"),
    "sdRatioRaw": f"{lt_.loc['Max / min monthly SD'].iloc[0]:.1f}", "sdRatioLog": f"{lt_.loc['Max / min monthly SD'].iloc[1]:.1f}",
    "archRaw": f"{lt_.loc['ARCH-LM statistic (7 lags, on daily change)'].iloc[0]:.0f}", "archLog": f"{lt_.loc['ARCH-LM statistic (7 lags, on daily change)'].iloc[1]:.0f}",
    "levPlog": f"{lt_.loc['Levene p-value'].iloc[1]:.3f}", "boxcox": f"{eda['boxcox_lambda_daily']:.3f}",
})
io_, fo_ = pd.read_csv(RES / "irf_orderings.csv"), pd.read_csv(RES / "fevd_orderings.csv")
wk_ = pd.read_csv(RES / "weekly_weather_lag.csv")
neg = lambda x: f"{abs(x):.0f}"  # noqa: E731
nums.update({
    "irfWindA": neg(io_[(io_.shock == "Wind") & io_.ordering.str.startswith("PM2.5")].day1_pct.iloc[0]),
    "irfWindB": neg(io_[(io_.shock == "Wind") & io_.ordering.str.startswith("weather")].day1_pct.iloc[0]),
    "irfRhA": neg(io_[(io_.shock == "Humidity") & io_.ordering.str.startswith("PM2.5")].day1_pct.iloc[0]),
    "irfRhB": neg(io_[(io_.shock == "Humidity") & io_.ordering.str.startswith("weather")].day1_pct.iloc[0]),
    "fevdA": f"{fo_[fo_.ordering.str.startswith('PM2.5') & (fo_.variable != 'PM2.5')].share_h14_pct.sum():.0f}",
    "fevdB": f"{fo_[fo_.ordering.str.startswith('weather') & (fo_.variable != 'PM2.5')].share_h14_pct.sum():.0f}",
    "lagWindP": f"{wk_[wk_.term == 'wind (last week)'].p_value.iloc[0]:.2f}", "lagRhP": f"{wk_[wk_.term == 'humidity (last week)'].p_value.iloc[0]:.2f}",
    "sameWeekRsq": f"{wk_[wk_.model == 'same-week weather'].r2_model.iloc[0]:.2f}",
})
sb = jl("shock_binned.json")
nums.update({"shockWindBig": f"{abs(sb['curves']['wind']['pct'][-1]):.0f}", "shockWindBigZ": f"{sb['curves']['wind']['z'][-1]:.1f}",
             "shockWindCalm": f"{sb['curves']['wind']['pct'][0]:.0f}", "shockWindCalmZ": f"{abs(sb['curves']['wind']['z'][0]):.1f}",
             "janWind": f"{sb['jan21_wind']:.1f}", "janPred": f"{sb['jan21_pred']:.1f}", "janShock": f"{sb['jan21_shock_kmh']:.1f}"})
bm_ = pd.read_csv(RES / "monthly_mean_sd.csv", index_col=0)
nums.update({"sdNov": f"{bm_.loc[11, 'sd_raw']:.0f}", "sdAug": f"{bm_.loc[8, 'sd_raw']:.0f}"})
nums.update(FC_NUMS)
(TAB / "numbers.tex").write_text("\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in nums.items()) + "\n")
print("numbers:", len(nums))
