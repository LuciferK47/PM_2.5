# START HERE: briefing for GPT
You cannot open the original project, so everything is in these text files. The project (Delhi PM2.5 time-series study, MATH F428) is **finished**; your job is a **final independent audit**.
## Context in 5 lines
- Daily PM2.5 for Delhi 2015-2020 (CPCB) + ERA5 weather. Q1: does weather predict PM2.5? Q2: how well can PM2.5 be forecast 1 and 52 weeks ahead?
- Weather has a short-memory predictive association (days); at 52 weeks climatology is hard to beat; a Fourier+ARMA model matches/slightly beats it; SARIMA/LSTM do not help.
- Data end July 2020, so it is a historical forecasting study (2017-19 backtests + 2020 outlook).
- A draft had several bugs and over-claims; three reviewers (Claude, Gemini, GPT) found them; each claim was re-tested (file 06).
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
