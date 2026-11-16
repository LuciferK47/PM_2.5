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
F["00_VERIFY_README.md"] = f"""# 00 Verification pack: how to re-check everything
Project: Delhi PM2.5 time-series study (MATH F428). Branch `phase4-final`. You already have (or can get) the earlier briefing; this pack is **different**: it holds the raw material to *recompute and re-check* every number, not a summary.

## What to do
1. Take the headline claims in file 01 and **recompute each from the raw data in file 06** (weekly table and raw backtest forecasts). Report any mismatch.
2. Read the code (files 02-04, 07) for errors: leakage, off-by-one in horizons/weeks, wrong test, wrong formula.
3. Compare every number in the report/deck (file 08) against the tables (file 05). Report any number that is not in the tables or differs.
4. Judge whether each conclusion follows from the evidence, and which are over-claims.
Be specific: cite file, section, number. If you cannot run code, check by reasoning and by hand arithmetic where possible. Do not just agree.

## Files
| File | Content |
|---|---|
| 01_claims_ledger.md | every headline claim, its stated value, and where it comes from |
| 02_src_code.md | full source of src/ (data, tsa, aqi, forecast) |
| 03_notebooks_02_03_code.md | EDA and VAR/Granger notebooks: code plus printed output |
| 04_notebook_04_code.md | forecasting notebook: code plus printed output |
| 05_all_results_tables.md | every results/*.csv (except raw forecasts) and key_numbers json |
| 06_raw_data_for_recompute.md | weekly data table (287 rows) + raw backtest forecasts (fold, model, date, actual, mu, sd) |
| 07_verification_and_figure_code.md | verify_numbers.py (65 checks) and make_figures.py |
| 08_report_and_deck_text.md | LaTeX source of the written report and the Beamer deck |
| 09_changes_and_review_log.md | git history, what changed vs the original draft, and the review-response log |

## Setup facts
- Weekly series: W-SUN weeks, 287 weeks 2015-01-04 to 2020-07; log of the weekly mean PM2.5. Train 2015-2018 / expanding window.
- Origins: 2016-12-25, 2017-12-31, 2018-12-30, each forecasting 52 weeks. Point forecast = median exp(mu). Mean = exp(mu + sd^2/2).
- Verification already done by the authors: verify_numbers.py passes 65/65 (file 07). Treat that as a claim to test, not as proof.

## Output format
(i) numbers you reproduced (with your values), (ii) mismatches, (iii) code bugs, (iv) over-claims, (v) prioritised fixes.
"""

K = json.loads((R / "results/key_numbers_forecast.json").read_text())
F["01_claims_ledger.md"] = f"""# 01 Claims ledger (what the deck/report states, and how to check it)
Check each row. 'Source' tells you which file holds the evidence; 'Recompute' says how.

| # | Claim | Source | Recompute |
|---|---|---|---|
| 1 | Backtest MAE 2017/18/19: selected Fourier+ARMA 31.5/23.4/25.7; climatology 31.0/21.8/27.8; SARIMA D=1 53.8/21.1/27.5; SARIMA D=0 about 44; LSTM 36/49/53 | 05 (fc_backtest_mae.csv) | file 06 raw forecasts: mean |actual - exp(mu)| per fold and model |
| 2 | Climatology = mean of log PM2.5 by week index (1-52) over training years, forecast exp(mean) | 02 (forecast.py climatology) | file 06 weekly table |
| 3 | Seasonal naive = same week of the previous year | 02 | file 06 |
| 4 | Selected model not significantly better than climatology (block-bootstrap CI covers 0) | 05 (fc_loss_diff.csv) | resample loss differences, blocks of 8 weeks |
| 5 | 2019 95% interval coverage 90% raw, 96% after seasonal rescaling | 05 (fc_calibration_2019.csv) | share of actuals in [exp(mu-1.96 sd), exp(mu+1.96 sd)] (file 06) |
| 6 | Selected model raw 95% intervals, 2019: 5 misses, all below the lower bound; 2018: 2 below, 1 above; 2017 (stress test): 10 below, 6 above, coverage 69% | 05, 06 | count actual < lower vs > upper per fold (authors' recount: coverage 0.69/0.94/0.90) |
| 7 | One-week-ahead MAE change vs no-weather model: lagged weather -2.4%, last-3-days +0.7%, oracle same-week +6.9% (HLN-DM p about 0.07) | 05 (fc_oneweek.csv) | see 04 notebook cell for the one-step design |
| 8 | Wind/humidity Granger-cause PM2.5 for about a week, robust to rain, temperature, trend, training-only climatology | 05 (granger_*.csv) | 03 notebook; HAC Wald code in src |
| 9 | Weekly nested lag test adds nothing: delta R2 = 0.005, p = 0.51 | 05 (weekly_lag_nested.csv) | 03 notebook section 9 |
| 10 | 2019 pipeline test: 12/12 monthly means inside 95% interval; Poor-or-worse days 55% predicted vs 45% actual | 05 (fc_outlook_validation_2019_*.csv) | file 06 + 04 notebook |
| 11 | Lockdown (25 Mar - 31 May 2020): actual mean 48.7 is 43% below counterfactual median (95% -52% to -32%); weather-adjusted -38% | 05 (fc_lockdown.csv) | 1 - 48.7/median |
| 12 | PM2.5 decline 2016 to 2019: all stations -25%, fixed 6-station panel -20%, weather-adjusted -18% | 05 (station_check.csv) | 02 notebook section 8; needs data/raw/station_day.csv (not included) |
| 13 | Ljung-Box on SARIMA residuals is distorted by the 52 diffuse burn-in residuals; after removing them lags 10/26 pass, lag 52 p = 0.016 | 05 (fc_diagnostics.csv) | 04 notebook |
| 14 | Seasonal MA = -0.988 is unidentified (SE 8.26) | 04 notebook output | 04 notebook |
| 15 | Leap-year fix: day 366 mapped to 365 consistently | 02 (tsa.py doy365) | read code |

Key forecast numbers stored by the notebook:
{fence(json.dumps(K, indent=1))}
"""

F["02_src_code.md"] = "# 02 Source code (src/)\n\n" + "\n".join(code(f"src/{n}") for n in ["data.py", "tsa.py", "aqi.py", "forecast.py"])
F["03_notebooks_02_03_code.md"] = "# 03 Notebooks 02 and 03: code and printed output\n\n" + nb_cells("notebooks/02_eda.ipynb") + "\n\n" + nb_cells("notebooks/03_var_granger.ipynb")
F["04_notebook_04_code.md"] = "# 04 Notebook 04: forecasting, code and printed output\n\n" + nb_cells("notebooks/04_forecasting.ipynb", 2500)

skip = {"fc_backtest_forecasts.csv"}
parts = ["# 05 All results tables (results/)\n"]
for p in sorted((R / "results").glob("*.csv")):
    if p.name in skip:
        continue
    parts.append(f"## {p.name}\n" + tab(p.name))
for p in sorted((R / "results").glob("*.json")):
    parts.append(f"## {p.name}\n" + fence(p.read_text()))
F["05_all_results_tables.md"] = "\n".join(parts)

wk = pd.read_csv(R / "data/processed/delhi_weekly.csv")
fc = pd.read_csv(R / "results/fc_backtest_forecasts.csv")
F["06_raw_data_for_recompute.md"] = f"""# 06 Raw data for recomputation
## delhi_weekly.csv ({len(wk)} rows; pm25 = weekly mean ug/m3, log_pm25 = log of it; n_days = daily obs in the week)
{fence(wk.round(4).to_csv(index=False))}
## fc_backtest_forecasts.csv ({len(fc)} rows; fold = forecast year; mu, sd on log scale; point forecast = exp(mu))
{fence(fc.round(4).to_csv(index=False))}
"""

F["07_verification_and_figure_code.md"] = "# 07 Verification and figure code\n\n" + code("slides/beamer/verify_numbers.py") + "\n" + code("slides/beamer/make_figures.py") + "\n## verify_numbers.py last output\n" + fence("65/65 checks passed (authors' run, 2026-11-16)")
F["08_report_and_deck_text.md"] = "# 08 Report and deck LaTeX source\n\n## report/report.tex\n" + fence((R / "report/report.tex").read_text(), "latex") + "\n## slides/beamer/main.tex\n" + fence((R / "slides/beamer/main.tex").read_text(), "latex")
F["09_changes_and_review_log.md"] = (
    "# 09 Changes and review log\n\n## git log (main..HEAD)\n" + fence(sh("git log main..HEAD --format='%h %s'"))
    + "\n## diffstat of source and notebook changes\n" + fence(sh("git diff --stat main..HEAD -- src tools notebooks | tail -30"))
    + "\n## diff of src/tsa.py and src/aqi.py vs main\n" + fence(sh("git diff main..HEAD -- src/tsa.py src/aqi.py"), "diff")
    + "\n## Review responses (each earlier claim, verdict, evidence)\n" + (R / "docs/REVIEW_RESPONSES.md").read_text()
)

for k, v in F.items():
    (OUT / k).write_text(v)
tot = sum(len(v) for v in F.values())
(OUT / "ALL_IN_ONE.md").write_text("\n\n".join(F.values()))
print(len(F), "files +ALL_IN_ONE;", f"{tot/1e3:.0f} KB total")
for k, v in F.items():
    print(f"{k:42s}{len(v)/1e3:7.1f} KB")
