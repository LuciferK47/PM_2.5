# Presentation script and Q&A

Deck: `slides/Delhi_PM25_presentation.pdf` (14 slides + 3 backup; source `slides/beamer/main.tex`).
Every number in the deck is generated from `results/` and re-checked by `slides/beamer/verify_numbers.py` (52 checks).

## One-line pitch
"Delhi's PM2.5 repeats a huge winter peak every year. We first tested whether weather (wind and humidity) actually drives it. It does, over the next few days. In the next phase we use that to build and compare forecasting models for the coming 12 months."

## What to say on each slide

**1. Title.** "We are forecasting Delhi's PM2.5 air pollution. Today: what we have established. Next phase: the forecasting models."

**2. The problem.** "PM2.5 means particles under 2.5 micrometres that reach the lungs and blood, measured in micrograms per cubic metre. India's AQI colours these bands. 52 percent of days from 2015 to 2020 were Poor or worse, and it repeats every year: winter averages 213, the monsoon 48, so winter is 4.4 times higher."

**3. What we are building (say the intent clearly here).** "Two questions. Q1: does weather drive PM2.5? That is done, using a VAR model and Granger causality. Q2: what will PM2.5 be next? That is the next phase, on two horizons: next week, where weather may help, and the next 12 months, where weather is unknown, so we will not use weather inputs. The final output is a month-by-month AQI outlook for health advisories."

**4. Data.** "PM2.5 from CPCB, India's pollution board, through Kaggle; wind and humidity from ERA5, a reanalysis, meaning observations blended into a weather model to give a gap-free record. Links are on the slide. 2,009 days from January 2015 to July 2020, only 2 PM2.5 values interpolated. We use daily data for causality and weekly means, 287 weeks, for forecasting. Train 2015 to 2018, test 2019; the 2020 lockdown is excluded."

**5. STL.** "STL splits the series into trend, seasonal and residual. Seasonal strength is 0.89 on a scale where 1 is purely seasonal, so the yearly cycle dominates and the forecasting model must be seasonal with period 52 weeks."

**6. Why logs.** "PM2.5 moves by percentages: its spread is about 115 in November but 15 in August. Raw data has a heavy right tail, skewness 1.70. The log is close to a bell curve, skewness minus 0.08. The Box-Cox estimate is 0.045, close to 0, which is exactly the log."

**7. Volatility tests.** "Volatility is how much values swing. Raw spread differs 7.9 times between months and tracks the level; after the log only 1.3 times. Honest note: small differences remain. The equal-spread test still gives p = 0.006 and the ARCH test, which asks whether big swings cluster, drops from 235 to 36 but is still significant. So we re-check the model residuals later."

**8. Stationarity.** "Stationary means mean, spread and autocorrelation do not drift, so past patterns still apply. Weekly log PM2.5 on the training years has a flat rolling mean and a modestly varying spread: a repeating yearly pattern, not a drifting trend."

**9. ADF and KPSS.** "Two tests with opposite null hypotheses. ADF: H0 is a unit root; a small p supports stationarity. KPSS: H0 is stationary; a large p supports it. Both pass for log PM2.5 and its seasonal difference, so d = 0. A further difference over-differences, with lag-1 autocorrelation minus 0.46. Whether to use the seasonal difference D is decided in the next phase on a validation year, not the test year."

**10. Granger causality.** "X Granger-causes Y if past X improves the forecast of Y beyond Y's own past. We compare Model A (past PM2.5 only) with Model B (plus past wind and humidity) using a Wald test with robust errors. We removed the seasonal cycle first. Wind and humidity help predict PM2.5 at every lag from 1 to 7 days, p below 10 to the minus 9, and humidity still matters after controlling for rain. The reverse is absent for humidity and weak for wind, only at 1 to 2 lags. This is predictive causality, not proof of a physical cause."

**11. What is a shock.** "A shock is the part of today's wind or humidity that the model could not predict from the previous 4 days. On 21 January 2019 the model expected 7.4 km/h and the wind was 14.8, a shock of plus 7.4. One SD is a typical shock: 2.5 km/h for wind, 5.4 percent for humidity. Grouping all days by shock size, an unexpectedly windier day is followed by PM2.5 about 24 percent lower, a calmer one by about 32 percent higher."

**12. Impulse response.** "This traces PM2.5 after a one-SD shock. The size depends on the ordering assumption: weather first lets a shock act on the same day; PM2.5 first allows lagged effects only. Wind cuts PM2.5 by 6 to 12 percent the next day, humidity 4 to 7 percent, fading within about a week. At the weekly scale, last week's weather adds nothing to predict this week's PM2.5."

**13. Established so far.** Read the five bullets; end with: "Answer to Q1: yes, weather drives PM2.5 over the following days."

**14. Limits and next phase.** "Limits: Granger is predictive causality and mixing height, stubble burning and fireworks are not measured; weather's share of 14-day error is 6 to 30 percent depending on ordering; one city, data end mid-2020. Next: SARIMA(X) with AIC/BIC search and residual checks; baselines (seasonal naive, climatology, Linear Regression, LSTM) compared by test MAE on 2019; the final 12-month forecast with 95 percent intervals and a monthly AQI table."

## Likely questions and answers

**What is the project about?** Forecasting Delhi's PM2.5, after first testing whether wind and humidity drive it, so we know whether to use weather in the forecasting models.

**Why is there no forecast yet?** We split the work in two phases: first understand the data and the weather link (done); next fit and validate the SARIMA models. Doing the analysis first changed the design: weather only matters for days, so the 12-month model should not use it.

**Why logs?** The spread of PM2.5 grows with its level (corr. 0.95 between monthly mean and monthly SD, spread 7.9 times across months). The log makes the spread nearly constant (1.3 times) and removes the skew (1.70 to minus 0.08). Box-Cox lambda 0.045 is near 0.

**What does the volatility test show, and is the log enough?** It removes most of the level dependence, but the equal-spread test (p = 0.006) and ARCH (36, p about 6e-6) still reject. We will check the model residuals and add a variance model if needed.

**What is stationarity and which tests?** No drift in mean, spread or autocorrelation. ADF (H0 unit root) and KPSS (H0 stationary). Both pass for log PM2.5 and its seasonal difference on 2015 to 2018.

**Isn't raw PM2.5 stationary too?** Yes, it passes ADF and KPSS in our checks (ADF p = 0.0015, KPSS p at least 0.10). The log is for variance, not for stationarity.

**Why did you not use the seasonal difference twice (d = 1 and D = 1)?** The lag-1 autocorrelation is minus 0.46, close to the minus 0.5 warning level for over-differencing, and the series already passes the tests.

**What is a shock?** The unpredictable part of today's value given the past (the VAR residual). One SD is its typical size.

**What is an impulse response, and why a range?** The path of PM2.5 after a one-SD shock. It depends on the Cholesky ordering. We report weather-first and PM2.5-first, so wind is 6 to 12 percent, humidity 4 to 7 percent on day 1.

**Does it prove wind causes lower PM2.5?** No. Granger causality is predictive. Mixing height, stubble burning and fireworks are not in the data.

**Is the reverse direction (PM2.5 to wind) significant?** Weakly at 1 to 2 lags (p = 0.04 and 0.016), not at 3 or more (0.07 to 0.2); PM2.5 to humidity never (p at least 0.2). Weather to PM2.5 is significant at every lag from 1 to 7 (p below 1e-9).

**Why deseasonalise before Granger?** All series follow the calendar. Without removing it the test mostly detects "it is winter". We subtract a smoothed day-of-year mean.

**Why robust (HAC) errors?** The residuals are autocorrelated and their variance changes (ARCH), which can make ordinary p-values too small. HAC errors correct for that. Our manual implementation matches the software.

**Does humidity just stand in for rain?** No: with rain as a control, humidity stays significant (p = 3e-8) and rain adds nothing (p = 0.86).

**What does "6 to 30 percent" mean?** The share of the 14-day forecast-error variance of PM2.5 due to weather shocks in the VAR; 6 percent if PM2.5 is ordered first, 30 percent if weather is first.

**Why is weather not used for the 12-month forecast?** Its effect lasts about a week, last week's weather does not predict this week's PM2.5 (p = 0.46 and 0.48), and future weather is unknown a year ahead.

**Why weekly data for forecasting?** A 12-month horizon is 52 steps with a clear seasonal period of 52, which keeps the model fast and stable.

**What data and reliability?** CPCB through Kaggle; ERA5 reanalysis (a grid-cell estimate for central Delhi, not a station reading). A station dataset would be a good robustness check.

**Why train on 2015 to 2018 and test on 2019?** One full seasonal cycle for testing, and it keeps the 2020 lockdown (an emissions shock) out of the test.

## Numbers to remember
- 2,009 days; 52% of days Poor or worse; winter 213 vs monsoon 48 (4.4x); STL strength 0.89
- Log: skewness 1.70 to minus 0.08; monthly spread 7.9x to 1.3x; Box-Cox 0.045
- Training weeks 209: ADF stat minus 4.28 (level), minus 4.53 (seasonal difference); KPSS p at least 0.10; double-difference ACF minus 0.46
- Granger (4 lags, HAC): wind p = 8e-20, humidity 3e-11 (with rain control 3e-8), rain 0.86; reverse 0.10 (wind), 0.55 (humidity)
- 1 SD: wind 2.5 km/h, humidity 5.4%; day-1 effect wind minus 6 to minus 12%, humidity minus 4 to minus 7%; weather share 6 to 30%
- 21 Jan 2019: expected 7.4, actual 14.8, shock plus 7.4 km/h
