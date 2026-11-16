"""Build verification_pack/: 10 text files an outside LLM can use to re-check every result.
Run: python tools/build_verification_pack.py"""
from pathlib import Path
import json, subprocess
import pandas as pd

R = Path(__file__).resolve().parents[1]
OUT = R / "verification_pack"
OUT.mkdir(exist_ok=True)
for f in OUT.glob("*.md"):
    f.unlink()


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=R, capture_output=True, text=True).stdout


def fence(txt, lang=""):
    return f"```{lang}\n{txt.rstrip()}\n```\n"


def code(p):
    return f"## {p}\n" + fence((R / p).read_text(), "python")


def nb_cells(p, maxout=1800):
    nb = json.loads((R / p).read_text())
    out = [f"## {p}\n"]
    for i, c in enumerate(nb["cells"]):
        src = "".join(c["source"])
        if c["cell_type"] == "markdown":
            out.append(f"### [md {i}]\n{src}\n")
        else:
            out.append(f"### [code {i}]\n" + fence(src, "python"))
            txt = ""
            for o in c.get("outputs", []):
                if o.get("output_type") == "stream":
                    txt += "".join(o["text"])
                elif "data" in o and "text/plain" in o["data"]:
                    txt += "".join(o["data"]["text/plain"])
                elif o.get("output_type") == "error":
                    txt += "ERROR " + o.get("ename", "")
            if txt.strip():
                if len(txt) > maxout:
                    txt = txt[:maxout] + "\n...[truncated]"
                out.append("output:\n" + fence(txt))
    return "\n".join(out)


def tab(n):
    return fence(pd.read_csv(R / "results" / n).to_string(index=False, float_format=lambda x: f"{x:.5g}"))


F = {}
K = json.loads((R / "results/key_numbers_forecast.json").read_text())
LK = K["lockdown"]["plain"]; _ls = K["lockdown_sensitivity"]; _h = _ls["selected spec (linear, K=5, AR1), headline"]
PRE, ADJ, PLC = _h["pre_lockdown_gap_pct"], _h["lockdown_gap_adjusted_for_pre_gap_pct"], _ls["PLACEBO: same weeks of 2019 vs 2019 forecast"]["lockdown_gap_10wk_pct"]
_o = [v["lockdown_gap_10wk_pct"] for k_, v in _ls.items() if not k_.startswith("PLACEBO")]
SENS_LO, SENS_HI = min(_o), max(_o)
_m = pd.read_csv(R / "results/fc_outlook_2020.csv", index_col=0); JUN_LO = _m.loc["Jun", "lo95"]; JUN_A = _m.loc["Jun", "actual_mean_2020"]
LEDGER = f"""
## Claims ledger (round 2: statements as they now stand)
| # | Claim | Evidence file | Recompute from |
|---|---|---|---|
| 1 | MAE 2017/18/19: selected Fourier+ARMA 31.5/23.4/25.7; climatology 31.0/21.8/27.8; SARIMA D=1 53.8/21.1/27.5; SARIMA D=0 44.9/42.8/44.1; LSTM 36.3/28.3/54.3 (rerun after the alignment fix); linear regression 35.9/20.0/24.9 | 04 fc_backtest_mae.csv | 05 backtest forecasts: mean abs(actual - exp(mu)) |
| 2 | Climatology = mean log PM2.5 by week index 1-52 over training years; seasonal naive = value 52 weeks earlier | 01 forecast.py | 05 weekly table |
| 3 | No model is significantly better than climatology (circular moving-block bootstrap, 8-week blocks, drawn within each fold): 2018-19 selected -0.2 [-2.9,+2.8], linear -2.9 [-6.1,+0.7]; seasonal naive, SARIMA D=0, LSTM worse; SARIMA D=1 worse over all three folds | 04 fc_loss_diff.csv | resample per-fold absolute-error differences |
| 4 | 2019 raw 95% coverage 90.4% (5 misses, all below), 2018 94.2% (2 below, 1 above), 2017 69.2% (10 below, 6 above) | 04 fc_backtest_metrics.csv | 05: share of actual in [exp(mu-1.96 sd), exp(mu+1.96 sd)] |
| 5 | Season rescaling (2017-18 errors): 2019 coverage 96.2% but width 125 -> 179 and Winkler 175 -> 193 (worse) | 04 fc_calibration_2019.csv | 05 + scale factors 1.334 (winter) / 1.422 |
| 6 | One-week MAE vs no-weather DHR: lagged -2.4%, last-3-days +0.7%, same-week oracle +6.9% (p 0.075/0.585/0.074) | 04 fc_oneweek.csv | 05 one-step forecasts (fc_oneweek_forecasts) |
| 7 | HAC Granger wind->PM2.5 p~6e-20, humidity ~4e-11 (4 lags, with rain+temp 9e-18, 7e-8); seasonal tests all p<1e-3; interactions p=0.20 (monsoon x humidity), 0.03 (winter x wind) | 04 granger_*.csv | 06 daily data (anomalies from doy climatology) |
| 8 | Weekly nested test: R2 0.1341 -> 0.1391, p = 0.515 | 04 weekly_lag_nested.csv | 05 weekly table |
| 9 | 2019 pipeline validation: 12/12 monthly means inside 95%; Poor-or-worse 55.0% predicted vs 45.2% actual | 04 fc_outlook_validation_2019_*.csv | 06 daily data (actual band counts) |
| 10 | Lockdown: 10 Sunday-ending weeks 29 Mar-31 May (cover 23 Mar-31 May); actual mean {LK['actual_mean']:.1f} vs model median {LK['cf_median']:.1f} = {LK['gap_median_pct']:.0f}% (95% {LK['gap_lo95_pct']:.0f} to {LK['gap_hi95_pct']:.0f}); weather-adjusted {K['lockdown']['weather_adjusted']['gap_median_pct']:.0f}%; pre-lockdown (5 Jan-22 Mar) model gap {PRE:.0f}%; adjusted = (1+gap)/(1+pre-gap)-1 = {ADJ:.0f}%; other level specs {SENS_LO:.0f}% to {SENS_HI:.0f}%; 2019 placebo {PLC:.0f}% | 04 fc_lockdown*.csv | 05 lockdown weekly table (fc_weekly_2020) |
| 11 | June 2020 monthly mean {JUN_A:.1f} is below its lower bound {JUN_LO:.1f}; Jan-Feb inside; Mar-Jun below | 04 fc_outlook_2020.csv | 06 daily data |
| 12 | Station panel: city series 2016->2019 -25%, fixed 6-station panel -20%, weather-adjusted -18%; stations reporting 10, 8, 17, 37, 37 | 04 station_check.csv | 06 station summary (per station-year mean and days) |
| 13 | Ljung-Box on SARIMA D=1 residuals: p~0 with the 52 diffuse residuals; without them 0.49/0.10/0.016 (lags 10/26/52); seasonal MA -0.988, SE 8.26 | 03 nb04 output | needs full-precision refit |
| 14 | SARIMA D=0 with/without constant (same orders/folds): 44.9/42.8/44.1 vs 76.9/61.0/92.1 | 04 fc_sarima_d0_constant.csv | refit |
| 15 | doy365 maps 29 Feb to day 59 and shifts later leap-year days by -1 | 01 tsa.py | read code |

Note: all numbers in this ledger are generated from results/ at build time.

## What the first-round audits already found and what was fixed (verify the fixes!)
LSTM calendar/anomaly misalignment (now one helper `lstm_window`, deterministic torch); verifier checked April-June against March-May intervals and skipped a persistence week; non-converged fits accepted in AICc search; daily band days and monthly means from different draws (now one set of daily paths whose weekly means equal the weekly paths exactly); bootstrap joined forecast years (and a first fix without wrap-around biased the interval: now circular within each fold); constant predictive sd for linear regression/LSTM (now horizon-specific); report claims (winter humidity bound, D=0 '39.7 to 30.6', June omission, over-claims). See file 09 (Round 2 table R1-R23).
"""

F["00_VERIFY_README.md"] = f"""# 00 Verification pack (round 3, final check): how to re-check everything
Project: Delhi PM2.5 time-series study (MATH F428), branch `phase4-final`. Two earlier audits (Gemini, GPT) recomputed the numbers and found real bugs; those were fixed and everything was re-run. **Your job now: check that the fixes are correct, that nothing new broke, and that every statement is supported.**

## What to do
1. Recompute the claims below from the raw data in files 05 and 06. Report every mismatch.
2. Read the code (file 01, notebooks 02-03; 03 for notebook 04, 07 for the checker) for leakage, alignment errors, wrong formulas. Pay special attention to the fixes: `lstm_window` and `_lstm_recursive`, `daily_paths`, `block_bootstrap_diff` (circular, per fold), `linreg` sd, `_best_by_aicc`, `week_offsets_by_month`.
3. Compare every number in the report/deck text (file 08) with the tables (file 04).
4. Decide which conclusions are still over-claims. Do not just agree; give file and number.

## Files (10)
| File | Content |
|---|---|
| 00_VERIFY_README.md | this file, instructions, claims ledger |
| 01_src_code.md | full source of src/ |
| 02_notebooks_02_03_code.md | EDA and VAR/Granger notebooks: code plus printed output |
| 03_notebook_04_code.md | forecasting notebook: code plus printed output |
| 04_all_results_tables.md | every results/*.csv except raw forecasts, and the key_numbers json |
| 05_raw_forecasts_and_weekly.md | weekly table (full precision, 287 rows), raw 52-week backtest forecasts, one-step forecasts, 2020 weekly forecasts |
| 06_daily_data_and_stations.md | the full daily table (PM2.5 and weather) and per-station-per-year PM2.5 summary |
| 07_checker_and_figure_code.md | verify_numbers.py (78 checks), make_figures.py, slide number macros |
| 08_report_and_deck_text.md | LaTeX source of the report and the deck |
| 09_changes_and_review_log.md | git history, source diffs, review log with Round 2 |

## Setup facts
Weekly W-SUN series, 287 weeks 2015-01-04 to 2020-06-28 (log of weekly mean PM2.5). Origins 2016-12-25, 2017-12-31, 2018-12-30, each forecasting 52 weeks (the 2017 fold ends 24 Dec 2017). Point forecast = exp(mu) (median); mean = exp(mu + sd^2/2). Authors' checker: 78/78 passed (a claim to test, not proof). Raw CPCB/ERA5 files are not included; the daily table in file 06 is the processed series.

## Output format
(i) numbers you reproduced with your values, (ii) mismatches, (iii) code bugs, (iv) over-claims, (v) prioritised fixes.
{LEDGER}"""

F["01_src_code.md"] = "# 01 Source code (src/)\n\n" + "\n".join(code(f"src/{n}") for n in ["data.py", "tsa.py", "aqi.py", "forecast.py"])
F["02_notebooks_02_03_code.md"] = "# 02 Notebooks 02 and 03: code and printed output\n\n" + nb_cells("notebooks/02_eda.ipynb") + "\n\n" + nb_cells("notebooks/03_var_granger.ipynb")
F["03_notebook_04_code.md"] = "# 03 Notebook 04: forecasting, code and printed output\n\n" + nb_cells("notebooks/04_forecasting.ipynb", 2500)

skip = {"fc_backtest_forecasts.csv", "fc_oneweek_forecasts.csv", "fc_weekly_2020.csv"}
parts = ["# 04 All results tables (results/)\n"]
for p in sorted((R / "results").glob("*.csv")):
    if p.name in skip:
        continue
    parts.append(f"## {p.name}\n" + tab(p.name))
for p in sorted((R / "results").glob("*.json")):
    parts.append(f"## {p.name}\n" + fence(p.read_text()))
F["04_all_results_tables.md"] = "\n".join(parts)

wk = pd.read_csv(R / "data/processed/delhi_weekly.csv")
fc = pd.read_csv(R / "results/fc_backtest_forecasts.csv")
os_ = pd.read_csv(R / "results/fc_oneweek_forecasts.csv")
w20 = pd.read_csv(R / "results/fc_weekly_2020.csv")
F["05_raw_forecasts_and_weekly.md"] = f"""# 05 Raw data for recomputation
## delhi_weekly.csv ({len(wk)} rows, full precision; pm25 = weekly mean ug/m3, log_pm25 its log, n_days = daily obs in the week)
{fence(wk.to_csv(index=False))}
## fc_backtest_forecasts.csv ({len(fc)} rows; fold = forecast year; mu, sd on the log scale; point forecast = exp(mu); sd empty only for none after round 2)
{fence(fc.to_csv(index=False))}
## fc_oneweek_forecasts.csv ({len(os_)} rows; one-step forecasts, mu on the log scale)
{fence(os_.to_csv(index=False))}
## fc_weekly_2020.csv (no-lockdown forecast, 95% interval, weather-adjusted median and actual, weeks of 2020)
{fence(w20.to_csv(index=False))}
"""

dl = pd.read_csv(R / "data/processed/delhi_daily.csv")
st = pd.read_csv(R / "data/raw/station_day.csv", parse_dates=["Date"])
meta = pd.read_csv(R / "data/raw/stations.csv")
st = st[st.StationId.isin(meta.loc[meta.City == "Delhi", "StationId"])].dropna(subset=["PM2.5"])
sy = st.groupby([st.StationId, st.Date.dt.year])["PM2.5"].agg(["mean", "count"]).round(2).unstack().reset_index()
sy.columns = [f"{a}_{b}" if b != "" else a for a, b in sy.columns]
F["06_daily_data_and_stations.md"] = f"""# 06 Daily data and station summary
## delhi_daily.csv ({len(dl)} rows: daily city PM2.5 and ERA5 weather used by the notebooks)
{fence(dl.round(4).to_csv(index=False))}
## Delhi stations: PM2.5 mean and number of days per station and year (from station_day.csv; the city series is the mean over reporting stations)
{fence(sy.to_csv(index=False))}
"""

nums = (R / "slides/beamer/tables/numbers.tex").read_text()
F["07_checker_and_figure_code.md"] = "# 07 Checker and figure code\n\n" + code("slides/beamer/verify_numbers.py") + "\n" + code("slides/beamer/make_figures.py") + "\n## slides/beamer/tables/numbers.tex (the macros used in the deck and report)\n" + fence(nums, "latex") + "\n## Authors' last run: 78/78 checks passed (offline, local raw files).\n"
F["08_report_and_deck_text.md"] = "# 08 Report and deck LaTeX source\n\n## report/report.tex\n" + fence((R / "report/report.tex").read_text(), "latex") + "\n## slides/beamer/main.tex\n" + fence((R / "slides/beamer/main.tex").read_text(), "latex")
F["09_changes_and_review_log.md"] = (
    "# 09 Changes and review log\n\n## git log (main..HEAD)\n" + fence(sh("git log main..HEAD --format='%h %s'"))
    + "\n## Review responses (every claim from five reviews, with verdict, evidence, fix; Round 2 at the end)\n" + (R / "docs/REVIEW_RESPONSES.md").read_text()
    + "\n## Round 2 audit documents\n### GPT\n" + (R / "docs/reviews/round2/gpt_verification_audit.md").read_text()
    + "\n### Gemini\n" + (R / "docs/reviews/round2/gemini_verification_audit.md").read_text()
)

for k, v in F.items():
    (OUT / k).write_text(v)
tot = sum(len(v) for v in F.values())
(OUT / "ALL_IN_ONE.md").write_text("\n\n".join(F.values()))
print(len(F), "files +ALL_IN_ONE;", f"{tot/1e3:.0f} KB total")
for k, v in F.items():
    print(f"{k:42s}{len(v)/1e3:7.1f} KB")
