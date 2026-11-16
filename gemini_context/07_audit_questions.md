# 07 Audit questions for Gemini
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
