# Presentation script and Q&A

Deck: `slides/Delhi_PM25_presentation.pdf` (21 slides + 5 backup; source `slides/beamer/main.tex`). Every number on a slide comes from `results/` and is re-derived by `slides/beamer/verify_numbers.py` (automated checks of selected numbers). The full report is `report/report.pdf`; the log of what three reviewers claimed and what we found is `docs/REVIEW_RESPONSES.md`.

## One-line pitch
"Delhi's PM2.5 repeats a huge winter peak. Weather predicts it for about a week, but not for a year. A smooth seasonal model forecasts the year ahead about as well as the calendar average does, and we show honestly where it is and is not better."

## What to say on each slide

**1. Title.** "We forecast Delhi's PM2.5. First: does weather explain it, and over what horizon? Then: how well can we forecast a week and a year ahead?"

**2. Problem.** "PM2.5 is particles under 2.5 micrometres. 52 percent of days from 2015 to 2020 were Poor or worse on India's PM2.5 band; winter averages 213 against 48 in the monsoon, 4.4 times. Note: the official AQI takes the worst pollutant; we use only the PM2.5 band."

**3. What we built.** "Q1 explain, Q2a next week, Q2b next 12 months. All three are answered. Weather has a short memory, so the 12-month model uses no weather."

**4. Data.** "CPCB PM2.5 through Kaggle, ERA5 weather (a reanalysis, observed not forecast) through Open-Meteo. 2,009 days, 2 values interpolated. Daily data for causality, weekly means for forecasting, validated on three rolling origins."

**5. STL.** "Seasonal strength 0.90 on the training years: the cycle dominates."

**6-7. Log and volatility.** "Spread grows with the level, so we model the log: monthly spread 7.9x becomes 1.3x, skewness 1.70 becomes -0.08. Some volatility clustering remains in the daily data; on the weekly forecast residuals ARCH is absent."

**8-9. Stationarity.** "ADF and KPSS have opposite null hypotheses; both are consistent with stationarity for log PM2.5, so d = 0. KPSS on the raw level hides a slow decline under the cycle: once the cycle is removed PM2.5 falls about 25 percent from 2016 to 2019. A D=1 SARIMA's seasonal MA coefficient is -0.988 with a huge standard error: the seasonal difference is not needed, so we model the cycle with Fourier terms."

**10. Granger.** "Model A uses past PM2.5; model B adds past wind and humidity; a Wald test with robust errors asks if B is better. Joint tests at every lag order 1 to 7 reject, also with rain and temperature controls. Reverse: absent for humidity, weak for wind at lag orders 1 and 2. This is predictive, not proof of a physical cause."

**11. Shock.** "A shock is the unpredictable part of today's wind. Binned by size, PM2.5 on day t+1 is 24 percent lower than on day t-1 after an unexpectedly windy day."

**12. Impulse response.** "A 1-SD wind shock cuts PM2.5 by 6 to 12 percent next day, humidity 4 to 7; the range is the variable ordering; the ordering-free generalised response sits inside it. Fades in about a week. At the weekly scale we detected no added value from last week's weather."

**13. Established.** Read the bullets; answer to Q1: robust predictive association over days.

**14. Models and design.** "Benchmarks, a Fourier-plus-ARMA family, SARIMA, linear regression and a tiny LSTM. Three expanding-window origins; everything re-selected inside each window. We fixed the headline procedure in the code before the final runs; the 2019 year had been looked at in earlier iterations, so I do not call it a pristine hold-out."

**15-16. Backtest.** "Climatology is hard to beat. In 2019 the selected model scores 25.7 against 27.8; SARIMA D=1 27.5 but 54 in the 2017 fold. Seasonal naive, SARIMA D=0 and the small LSTM are clearly worse (the LSTM is 28 in 2018 and 54 in 2019 after we fixed an alignment bug found by an outside audit). Every other model, including the linear-trend variant with the lowest 2018-19 error, is statistically indistinguishable from climatology. With three origins we cannot rank them."

**17. Diagnostics.** "The earlier draft's Ljung-Box p of zero was a bug: the first 52 residuals of a D=1 model are initialisation values. Without them the residuals pass lags 10 and 26 (lag 52: p = 0.016). Intervals: 90 percent of 2019 weeks covered (69 percent in the 2017 stress fold), all 2019 misses on the low side; seasonal rescaling from earlier years gives 96 percent, but the intervals get 43 percent wider and the Winkler score worsens (175 to 193). It buys coverage, not sharper intervals."

**18. One week ahead.** "Last week's weather: no gain (-2.4 percent). Last three days: +0.7. The same week's weather, which no one knows in advance, +6.9 percent. Weather is explanatory but a weak forecasting input."

**19. Outlook for 2020.** "Fitted on 2015-2019 only, simulated paths, converted to daily PM2.5 bands. Validated on 2019: all 12 monthly means inside the interval, but the Poor-or-worse share is over-predicted, 55 against 45 percent: the level bias. In 2020, January and February fall inside the interval; March to June fall below it."

**20. Lockdown.** "Weeks from 29 March to 31 May were about 43 percent below the no-lockdown forecast, 38 percent after adjusting for the actual wind and humidity: most of the drop is not weather. Descriptive; relies on the level of the forecast."

**21. Established and limits.** Read both cards.

**Backups:** glossary; robustness of Granger and IRF orderings; PM2.5 by month; station check (is the decline real?); outlook table.

## Likely questions and answers

**Does weather cause PM2.5?** We claim a robust *predictive* association: after removing the seasonal cycle, lagged wind and humidity improve prediction of PM2.5 in every specification. Boundary-layer height, stubble burning and fireworks are unmeasured, so this is not a causal proof.

**Is humidity only important in the monsoon?** Not as a predictive effect. Both variables are significant in winter and in the monsoon (p <= 5e-4); the monsoon-by-humidity interaction is not significant (p = 0.20). The correlation pattern in the EDA differs by season; the Granger effect does not detectably differ.

**Why are the p-values so small? Aren't they inflated?** The plain F-tests (1e-29) assume independent errors, which is false; we use HAC errors (1e-20 to 1e-11) and a rain/temperature control (down to 7e-8). We quote them as "significant", not as precise numbers.

**Why does the reverse PM2.5 -> wind appear at lags 1-2?** Possibly a shared stagnation regime (low wind and high PM2.5 on consecutive days). We have no boundary-layer data, so we call it unproven. It vanishes at lag order 3 and above and is absent in the full VAR F-test.

**Why Fourier + ARMA instead of SARIMA?** A SARIMA with a seasonal difference spends 52 of 209 points on differencing, and its seasonal MA hits -0.988 with a very large standard error (unidentified); it collapses in the 2017 fold (MAE 54). Fourier terms use 10 parameters for the yearly cycle.

**Is the Fourier model really better than climatology?** No: it is statistically indistinguishable (2018-19 MAE 24.6 vs 24.8; the bootstrap interval spans zero). The linear-trend variant has the lowest 2018-19 MAE (21.9) but its interval also spans zero, and we did not choose it in advance. Our message is "as good as climatology, more robust than SARIMA", not "better".

**Why is the LSTM so bad?** About 200 weekly points and a recursive 52-step forecast: it learns little beyond the mean cycle and drifts. An outside audit found an input-alignment bug in our first version; it is fixed and the model was rerun (MAE 36/28/54). It is a small-data baseline, not a statement about deep learning in general.

**Is the decline over 2016-2019 real or a change in monitors?** Both are possible: stations reporting rose from 10 and 8 to 37. A fixed panel of six long-running stations still falls about 20 percent (all stations 25, weather-adjusted 18). Consistent with a genuine decline, but a network effect is not fully excluded: the panel is small and thin in 2017.

**What does the "monthly outlook" mean? Is it the AQI?** It is a PM2.5 sub-index band outlook: the official AQI is the maximum over pollutants. Weekly paths plus a whole within-week offset vector (so each simulated week keeps its weekly mean) give daily values; monthly means and expected days per band come from the same paths; validated on 2019, where the Poor-or-worse share is over-predicted.

**Why didn't you re-centre the forecast for the 2019 bias?** The bias had the same sign in both calibration years (-0.66 and -0.45 SD) but the smaller one is below our pre-set 0.5 SD threshold; we decided the rule before seeing 2019 and report the bias rather than tune it.

**Why is the 2020 interval narrower than 2019's?** The calibration scale factors come from the two preceding folds and differ by year (1.33/1.42 vs 1.09/0.95): calibration itself is uncertain with this little data.

**Why not a Diebold-Mariano test for the 52-week comparison?** The 52 errors are one forecast path (strongly dependent), not 52 replications; we use a block bootstrap over three origins and say "indistinguishable". DM (HLN) is used only for the genuine one-step comparison.

**Did you use the test year to choose anything?** No: the Fourier order, ARMA order and level treatment are chosen inside each training window (inner validation on its last year). The earlier draft chose D on 2018 after an in-sample order search; that overlap is gone. Headline STL / Box-Cox are on the training years.

**What did the outside audits find in round 2?** An LSTM input-alignment bug (fixed, rerun), a month off-by-one and a skipped week in our own checker (fixed), a wrong p-value bound and an unsupported D=0 number in the report (replaced by a matched table), June 2020 omitted, a bootstrap that joined forecast years (now within-year, circular), constant-width intervals for linear regression and the LSTM (now horizon-specific), and over-claims (reworded). See `docs/REVIEW_RESPONSES.md`.

**What was wrong with the draft?** (1) Ljung-Box on the 52 initial residuals; (2) no constant in the D=0 model; (3) full-sample statistics quoted as headline; (4) wording ("drives", "p<1e-10 everywhere", "AQI"); (5) a weekday index that merged ISO week 53; (6) leap-year day-of-year. All fixed; see `docs/REVIEW_RESPONSES.md`.

**Why is the forecast for 2020 and not for the next 12 months from today?** Our data end in July 2020; a current advisory would need newer, consistently monitored data. This is a historical forecasting study with a real out-of-sample check (Jan-Jun 2020).

## Numbers to remember
- 2,009 days; 52% Poor or worse; winter 213 vs monsoon 48 (4.4x); STL strength 0.90 (training), 0.89 (full)
- Log: skew 1.70 -> -0.08; monthly spread 7.9x -> 1.3x; drift about -25% (2016 -> 2019)
- Granger (HAC, 4 lags): wind p ~ 6e-20, humidity ~ 4e-11 (with rain+temperature: 9e-18, 7e-8); IRF day 1: wind -6 to -12%, humidity -4 to -7%; FEVD 6-30%
- Backtest MAE 2017/2018/2019: Fourier+ARMA 31.5/23.4/25.7; climatology 31.0/21.8/27.8; SARIMA D=1 53.8/21.1/27.5; LSTM 36.3/28.3/54.3; nothing significantly better than climatology
- Coverage 2019: 90% raw, 96% rescaled (width +43%, Winkler 175 to 193); one week ahead: -2.4% / +0.7% / +6.9% (oracle)
- Lockdown: -43% vs the model's no-lockdown median (95% -52 to -32), weather-adjusted -38%, pre-gap-adjusted -36%, across specs -37 to -51%, 2019 placebo -15% (interval spans 0): descriptive, not causal
