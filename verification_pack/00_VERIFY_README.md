# 00 Verification pack: how to re-check everything
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
