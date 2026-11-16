"""Rebuild the self-contained briefs for other LLM reviewers (gemini_context/, gpt_context/) from the repo's current files.
Run: python tools/build_llm_context.py"""
from pathlib import Path
import json
import pandas as pd

R = Path(__file__).resolve().parents[1]
res = lambda n: R / "results" / n


def tab(name, idx=False, n=None):
    df = pd.read_csv(res(name)); df = df.head(n) if n else df
    return "```\n" + df.to_string(index=idx, float_format=lambda x: f"{x:.4g}") + "\n```\n"


def raw(path):
    return "```\n" + Path(path).read_text() + "\n```\n"


def code(path):
    return f"### {path}\n```python\n{(R / path).read_text()}```\n"


FC = json.loads(res("key_numbers_forecast.json").read_text())
files = {}
files["01_project_overview.md"] = (R / "README.md").read_text().replace("# Delhi PM2.5", "# 01 Project overview (README)\n\n# Delhi PM2.5", 1)
files["02_data_and_code.md"] = "# 02 Data schema and source code\n\n## daily table\n```\n" + pd.read_csv(R / "data/processed/delhi_daily.csv").head(5).round(2).to_string(index=False) + "\n```\n\n## weekly table\n```\n" + pd.read_csv(R / "data/processed/delhi_weekly.csv").head(5).round(2).to_string(index=False) + "\n```\n\n" + "\n".join(code(p) for p in ["src/data.py", "src/tsa.py", "src/aqi.py", "src/forecast.py"])
files["03_phase2_eda_results.md"] = f"""# 03 Phase 2: EDA and stationarity (notebook 02)
Season statistics:\n{tab('season_stats.csv')}Within-season correlation:\n{tab('within_season_correlation.csv')}Stationarity (full sample):\n{tab('stationarity.csv')}Stationarity (training weeks 2015-18, with lag-1 ACF):\n{tab('stationarity_train.csv')}Log justification:\n{tab('log_justification.csv', idx=True)}
Annual drift (anomaly vs training climatology):\n{tab('annual_drift.csv')}Station-network check (fixed panel, all stations, weather-adjusted):\n{tab('station_check.csv')}
Key numbers:\n{raw(res('key_numbers_eda.json'))}"""
files["04_phase3_var_granger_results.md"] = f"""# 04 Phase 3: VAR, Granger, IRF, FEVD (notebook 03)
VAR(4) on deseasonalised wind, humidity, log PM2.5 (2015-2019). Lag selection:\n{tab('var_lag_selection.csv')}Granger (VAR F-tests):\n{tab('granger_var.csv')}Robustness (BIC lag, first differences):\n{tab('granger_robustness.csv')}HAC Wald:\n{tab('granger_hac.csv')}HAC robustness (temperature, trend, training-only climatology):\n{tab('granger_hac_robust.csv')}Season-specific and interaction tests:\n{tab('granger_hac_seasonal.csv')}Joint tests by lag order:\n{tab('granger_hac_by_lag.csv')}IRF by ordering:\n{tab('irf_orderings.csv')}Generalised IRF:\n{tab('girf.csv')}FEVD by ordering:\n{tab('fevd_orderings.csv')}Weekly lag regression:\n{tab('weekly_weather_lag.csv')}Nested comparison:\n{tab('weekly_lag_nested.csv')}Key numbers:\n{raw(res('key_numbers_var.json'))}"""
files["05_phase4_forecasting_results.md"] = f"""# 05 Phase 4: forecasting (notebook 04, src/forecast.py)
Design: three expanding-window origins (train to 2016-12-25, 2017-12-31, 2018-12-30; forecast next 52 weeks). Headline procedure (fixed in code before the final runs; 2019 had been examined in earlier iterations): Fourier+ARMA with K, (p,q) by AICc inside each level type and the level type by validation on the last training year.
MAE (ug/m3):\n{tab('fc_backtest_mae.csv')}Full metrics by fold and model:\n{tab('fc_backtest_metrics.csv')}Paired loss differences vs climatology (block bootstrap):\n{tab('fc_loss_diff.csv')}Residual diagnostics (burn-in removed):\n{tab('fc_diagnostics.csv')}Calibration on 2019:\n{tab('fc_calibration_2019.csv')}One week ahead:\n{tab('fc_oneweek.csv')}2019 pipeline validation (monthly):\n{tab('fc_outlook_validation_2019_monthly.csv')}2020 outlook:\n{tab('fc_outlook_2020.csv')}Lockdown:\n{tab('fc_lockdown.csv', idx=True)}Key numbers:\n{raw(res('key_numbers_forecast.json'))}"""
files["06_review_log.md"] = "# 06 What three earlier reviews claimed and what we found\n\n" + (R / "docs/REVIEW_RESPONSES.md").read_text()
files["08_presentation_and_QA.md"] = (R / "PRESENTATION_SCRIPT.md").read_text()


def write(folder, who, names):
    d = R / folder; d.mkdir(exist_ok=True)
    for old in d.glob("*.md"):
        old.unlink()
    for k, v in files.items():
        (d / k).write_text(v)
    (d / "00_START_HERE.md").write_text(f"""# START HERE: briefing for {who}
You cannot open the original project, so everything is in these text files. The project (Delhi PM2.5 time-series study, MATH F428) is **finished**; your job is a **final independent audit**.
## Context in 5 lines
- Daily PM2.5 for Delhi 2015-2020 (CPCB) + ERA5 weather. Q1: does weather predict PM2.5? Q2: how well can PM2.5 be forecast 1 and 52 weeks ahead?
- Weather has a short-memory predictive association (days); at 52 weeks climatology is hard to beat; no model is significantly better than it (Fourier+ARMA is indistinguishable); SARIMA D=0 and a small LSTM are worse.
- Data end July 2020, so it is a historical forecasting study (2017-19 backtests + 2020 outlook).
- A draft had bugs and over-claims; reviews by Claude, Gemini and GPT (two rounds, the second a recomputation audit) found them; each claim was re-tested and fixed (file 06).
- Everything (code, tables, numbers) is included. Be critical and specific; do not just agree.
## Files
| File | Content |
|---|---|
| 01_project_overview.md | README: status, data, results, layout |
| 02_data_and_code.md | data samples and full source of src/ |
| 03_phase2_eda_results.md | EDA, stationarity, drift, station check |
| 04_phase3_var_granger_results.md | VAR, Granger (many robustness rows), IRF/GIRF, FEVD |
| 05_phase4_forecasting_results.md | backtest, diagnostics, calibration, 1-week test, 2020 outlook, lockdown |
| 06_review_log.md | every earlier claim with verdict and evidence |
| 07_audit_questions.md | what we want you to audit |
| 08_presentation_and_QA.md | the talk script and Q&A (the public claims) |
""")
    (d / "07_audit_questions.md").write_text(f"""# 07 Audit questions for {who}
Answer each concretely (numbers, named tests, alternative code). Say where you disagree with file 06.
1. Is anything in the *design* of the backtest still leaky (selection of K, p, q, level; calibration folds; the pre-declared headline)? Is declaring the headline model "before looking" credible given the code history?
2. No model is significantly better than climatology (circular block bootstrap within folds); the linear-trend variant has the lowest 2018-19 MAE but its interval spans 0. Is our wording ("statistically indistinguishable from climatology, more robust than SARIMA") honest and sufficient? What additional test would settle it with 5.5 years of data?
3. Calibration raises 2019 coverage 90% -> 96% but widens intervals 43% and worsens the Winkler score. Is the rule (season scale with shrinkage k=26; re-centre only if same sign and |mean z|>0.5 in both folds) defensible, and is the wording honest? The 2019 vs 2020 scale factors differ (1.33/1.42 vs 1.09/0.95); what does that imply for the 2020 intervals?
4. Is the daily-band conversion (weekly simulated paths + resampled within-week log offsets by calendar month) statistically sound? It over-predicted Poor-or-worse days in 2019 (55% vs 45%): is that just level bias or a flaw in the offset model?
5. Station check: is a fixed 6-station panel (>=60 days in each year) a fair test of whether the decline is real? What would you do instead with the data in hand?
6. VAR/Granger: any remaining error in HAC implementation, the season-interaction test, the generalised IRF (Psi_h Sigma e_j / sqrt(sigma_jj)), or the weekly nested test?
7. Lockdown: the gap is -43% (adjusted for the model's pre-lockdown bias -35%; level specs -37% to -51%; 2019 placebo -15%). Is the descriptive wording sufficient? What would a reviewer attack?
8. Which statements in the deck/script (file 08) are still over-claims?
9. List the top 5 remaining weaknesses ranked by how much they could change a conclusion, with the fix for each that could be done in two days.
10. Anything we missed.
Format: (i) agreements, (ii) disagreements with reasons, (iii) new issues, (iv) numbered answers, (v) prioritised fixes.
""")
    if who == "GPT":
        allp = [d / n for n in sorted(x.name for x in d.glob("0*.md"))]
        (d / "ALL_IN_ONE.md").write_text("\n".join(f"\n=================== FILE: {p.name} ===================\n{p.read_text()}" for p in allp))


write("gemini_context", "Gemini", None)
write("gpt_context", "GPT", None)
print("ok", {k: len(v) for k, v in files.items()})
