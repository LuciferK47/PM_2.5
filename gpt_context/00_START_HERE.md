# START HERE: briefing for GPT

You are being given the full context of a university time-series project so you can act as a **critical reviewer / advisor**.
You cannot open the original zip, so everything you need is in these 9 text files (the original project is not needed).

## Your role
1. Read all files in order. Do not start giving opinions until you have read file 06 (critical review) and 07 (open questions).
2. Give an independent opinion: where do you agree or disagree with the review in 06? What did the authors (and the previous reviewer) miss?
3. Answer the questions in 07, with concrete recommendations (model choices, tests, fixes), and flag anything statistically wrong.
4. Be specific and numerical where possible. If you disagree with a number or method, say why.

## Project in 5 lines
- MATH F428 Time Series Analysis course project, BITS Pilani Goa. Authors: Kushagra Singh, Yatin JM, Aryan Choudhary.
- City: Delhi. Variable: daily PM2.5 (CPCB monitors, via Kaggle) 2015-01-01 to 2020-07-01, plus ERA5 weather (wind, humidity, temp, rain).
- Phases 1-3 are DONE and presented: data cleaning, EDA (seasonality, log transform, stationarity), VAR + Granger causality + impulse responses.
- Phase 4 (NEXT, only a draft exists): SARIMA(X) forecasting of weekly log PM2.5, baselines (seasonal naive, climatology, Linear Regression, LSTM), final 12-month forecast with 95% intervals and a monthly AQI advisory table.
- Design decision from phases 1-3: weather only matters for days, so the 12-month model uses NO weather inputs.

## File index (read in this order)
| File | Content |
|---|---|
| 00_START_HERE.md | this file |
| 01_project_overview.md | goal, data, split, design decisions, status, repo layout, timeline |
| 02_data_and_code.md | data schema + samples, and the full source code of `src/` (cleaning, stationarity tests, plotting helpers) |
| 03_phase2_eda_results.md | EDA and stationarity: method, every number, interpretation |
| 04_phase3_var_granger_results.md | VAR / Granger / HAC / IRF / FVED: method, every number, interpretation |
| 05_phase4_sarima_draft.md | the draft SARIMA code (verbatim), its outputs, baselines table, 2019 forecast table |
| 06_critical_review.md | independent critical analysis: what is solid, what is wrong or weak, with evidence |
| 07_open_questions_for_gpt.md | the specific questions we want your opinion on |
| 08_presentation_and_QA.md | the talk script and Q&A the team prepared (shows the claims being made publicly) |

## Conventions
- "anomaly" = value minus smoothed day-of-year climatology. "HAC" = Newey-West robust errors. "IRF/FEVD" = impulse response / forecast-error variance decomposition.
- Train = 2015-2018, test = 2019 (weekly). The 2020 lockdown is excluded from the test and the VAR.
- All numbers quoted come from files in the repo's `results/` directory; they are reproduced in files 03-05.
