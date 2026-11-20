# Handoff: Delhi PM2.5 time-series project (MATH F428)

For a teammate who has to present and defend this project. Read sections 1-4 first (about 20 minutes); sections 5-8 are look-up material. Instructor: Prof. Anupama Sharma. Authors: Kushagra Singh, Yatin JM, Aryan Choudhary.

**This is the curriculum-aligned version.** An earlier version used many methods that are not in the course (HAC/Newey-West tests, impulse responses, variance decomposition, block bootstrap, Winkler score, an LSTM, calibrated intervals, daily simulation, PM2.5 bands). After review we rebuilt the project around what the lectures cover (decomposition, ACF/PACF, ADF/KPSS, SARIMA under Box-Jenkins, Holt-Winters, regression with ARMA errors, forecast evaluation, Diebold-Mariano, forecast combination) plus the VAR/Granger test from the course handout. The only extra tool is a block bootstrap used as a robustness line in the report.

---

## 1. What the project is

**Data.** Daily PM2.5 for Delhi (CPCB stations via Kaggle) and ERA5 weather (wind speed, relative humidity, temperature, rain), 1 Jan 2015 to 1 Jul 2020 (2,009 days). We work with **weekly means** (weeks ending Sunday): 287 weeks, seasonal period 52. Modelling years are 2015-2019; 2020 is used only in a final what-if.

**Three questions.**
1. **Q1.** Which of the course's forecasting methods forecasts weekly PM2.5 best **52 weeks ahead**, using only the series itself?
2. **Q2.** Do wind speed and relative humidity help (predict PM2.5, and improve a forecast)?
3. **Q3.** A model fitted on 2015-2019 cannot know about the 2020 lockdown. Used as a "business as usual" baseline, how far below it was PM2.5 in the lockdown weeks?

**The story in one paragraph.** PM2.5 in Delhi has a huge yearly cycle (winter 217 vs monsoon 48 ug/m3, seasonal strength 0.90). The variance grows with the level, so we take logs. The ACF shows a yearly wave, so the series is not stationary in the mean (ADF/KPSS do not see this: they look for unit roots). We compare six methods on three expanding-window origins (forecast 2017, 2018, 2019, each 52 weeks). The combination has the lowest MAE in 2018-19 (23.8 vs 24.8 for the seasonal mean, 24.3 SARIMA, 24.5 harmonic, 25.7 Holt-Winters, 29.6 naive), but no model is significantly better than the seasonal mean (combination: Diebold-Mariano p = 0.08); only the seasonal naive is significantly worse (p = 0.03). SARIMA fails with only two training years (MAE 72.3 in 2017). Wind and humidity Granger-cause PM2.5 over days (p about 1e-29 and 1e-11) but add nothing at the weekly scale (p = 0.47) and make one-week forecasts slightly worse (+2.6%, p = 0.04). In the 2020 lockdown weeks PM2.5 was 44-50% below the business-as-usual forecast (34-41% after adjusting for the models' earlier bias), beyond the ordinary ten-week error of the better models. This is descriptive, not causal.

**What the project does not claim.** It is a historical study (data end in July 2020), not an advisory. Granger causality is predictive, not physical. The lockdown number is model-relative.

## 2. Data and its quirks

| Item | Detail |
|---|---|
| PM2.5 | CPCB `city_day.csv` (Kaggle `rohanrao/air-quality-data-in-india`), Delhi, mean over reporting stations. Two missing days are interpolated (gaps up to 3 days). |
| Weather | Open-Meteo ERA5 archive at 28.61N 77.21E. **Wind = wind speed at 10 m in km/h (not direction).** Humidity = relative humidity in %. A reanalysis at one grid point, not a station measurement. |
| Bad-air share | 54% of days in 2015-2019 have PM2.5 above 90 ug/m3 (CPCB sub-index band Poor or worse; this is the PM2.5 sub-index band, not the multi-pollutant AQI). |
| Weekly series | Weeks end on Sunday; weeks with fewer than 4 PM2.5 days are dropped (the partial last week), leaving 287. |
| Calendar week | `week_index` (in `src/tsa.py`) = day-of-year of the week's Thursday on a 365-day scale, in 7-day blocks, capped at 52: week 53 folds into week 52 and Feb 29 is mapped to Feb 28. |
| Station count | The Delhi value is the mean over reporting stations; the count went 10, 8, 17, 37, 37 (2015-2019). Part of the 2016-19 decline may be a change of station mix. Listed as a limitation, not analysed. |
| 2020 | The lockdown began 25 March 2020. The ten Sunday-ending weeks 29 Mar - 31 May cover 23 Mar - 31 May. 2020 is never used to fit or select anything. |

## 3. Repository map and how to run it

```
data/raw/          city_day.csv, station_day.csv, stations.csv, delhi_weather_openmeteo.json
data/processed/    delhi_daily.csv, delhi_weekly.csv
src/               data.py, tsa.py (ADF/KPSS, day-of-year anomaly, week index),
                   forecast.py (the six models, backtest, metrics, DM test, block bootstrap)
notebooks/         01_data_prep, 02_eda, 03_var_granger, 04_forecasting (executed)
tools/             build_nb02.py, build_nb03.py, build_nb04.py (regenerate the notebooks),
                   extract_notes.py (SPEAKER_NOTES.md from the slides)
results/           CSV/JSON; fc_* files belong to the forecasting study
slides/beamer/     main.tex (deck), notes.tex (notes version), make_figures.py, verify_numbers.py, tables/
report/            report.tex
SPEAKER_NOTES.md   what to say on each slide
```

**Order to run** (full commands in `README.md`): create the environment from `requirements.txt` (Python 3.12), download the Kaggle files into `data/raw/`, run notebooks 01 to 04 (04 takes 15-25 minutes because SARIMA with period 52 is slow; it uses 8 processes), then

```
cd slides/beamer
python make_figures.py                   # deck figures (slide size), tables/*.tex and numbers.tex
PROFILE=report python make_figures.py    # report figures (column / page width)
python verify_numbers.py                 # independent re-derivation; must end "checks passed"
tectonic main.tex                        # deck
tectonic notes.tex                       # speaker notes (slide thumbnail + text)
cd ../../report && tectonic report.tex
python ../tools/extract_notes.py         # writes ../SPEAKER_NOTES.md
```

Every number on the slides and in the report is a macro in `tables/numbers.tex` or a generated table; nothing is typed by hand. `verify_numbers.py` recomputes them from the raw files with separate code (own OLS for the Granger and weekly tests, own seasonal-mean and naive forecasts, own error metrics, own Diebold-Mariano statistic) and fails on any mismatch.

## 4. Theory primer: what each method is, why we used it, what to watch for

Lecture numbers refer to `Class_Slides/` (handout topics in brackets).

### 4.1 Components, log and Box-Cox (Lectures 04-07)
A series = trend + seasonal + remainder. **Additive:** x = T + S + R. **Multiplicative:** x = T x S x R; taking logs makes it additive. *Check used here:* compute the mean and SD of PM2.5 within each calendar month; if the SD rises with the mean (correlation 0.94 raw, -0.09 after log), the structure is multiplicative and the log is right. Box-Cox with lambda near 0 (we get 0.11 on training weeks) is the same idea. *Watch for:* a transformation changes the scale; it does not remove trend or seasonality. Forecasts of log PM2.5 give the **median** after exp(); the mean is exp(mu + sigma^2/2).

### 4.2 STL and seasonal strength (Lectures 06-07)
STL splits weekly log PM2.5 into trend, seasonal (period 52) and remainder with LOESS smoothing. **Seasonal strength** F_S = max(0, 1 - Var(R)/Var(S + R)): 0 means no seasonality, 1 means purely seasonal; ours is 0.90. Trend strength F_T = 0.18. It is computed from the STL output, nothing more. We fit STL on 2015-2019 only: including 2020 would bend the end of the trend because of the lockdown.

### 4.3 Stationarity, ACF, PACF, ADF, KPSS (Lectures 08-12)
A stationary series has constant mean, variance and autocovariance. The **ACF** of log PM2.5 decays slowly, is -0.43 at lag 26 and +0.68 at lag 52: a yearly wave, so the mean depends on the season. The PACF has spikes at lags 1-2 only. **ADF**: null is a unit root (reject for stationarity). **KPSS**: null is stationarity (reject for a unit root). Our series rejects ADF (p = 5e-4) and does not reject KPSS (0.058 < 0.463), yet it is seasonal: *these tests detect unit roots and slow trends, not a regular seasonal swing, so the ACF is the informative tool.* The seasonal difference x_t - x_{t-52} removes the wave; its ACF at lag 52 turns negative (-0.34), the first hint of over-differencing.

### 4.4 Decomposition-based benchmarks (Lecture 06)
- **Seasonal naive:** forecast = value of the same week one year earlier (includes last year's noise).
- **Seasonal mean** (we call it that; the earlier name "climatology" confused people): for calendar week w, the average of log PM2.5 over all training years. It is the classical decomposition's seasonal index. It differs from the naive forecast because it averages all years. Example, week 3: training values 188, 272, 238, 197 -> naive 197, seasonal mean 221.

### 4.5 Holt-Winters (Lectures 22-23)
Additive seasonal exponential smoothing on log PM2.5, m = 52: level L_t = alpha(x_t - I_{t-m}) + (1-alpha)L_{t-1}; seasonal index I_t = delta(x_t - L_t) + (1-delta)I_{t-m}; forecast = L_t + I_{t-m+h}. Initial level and seasonal indices are estimated by maximum likelihood (as in Lecture 23); a damped trend is allowed and chosen by AIC (it never wins). *Peculiarity:* with 2-4 years of data the fitted seasonal smoothing parameter delta is about 0 (7e-5 at every origin), so the seasonal index is learnt once and barely updated, and the level (alpha about 0.27) does the tracking. Its accuracy then depends on how typical the first years were: MAE 44.7 (2017), 19.2 (2018, the best that year), 32.2 (2019). Its difference from the seasonal mean is not significant (p = 0.57).

### 4.6 SARIMA and Box-Jenkins (Lectures 15-21, 24-29)
SARIMA(p,d,q)(P,D,Q)_s with seasonal difference (1-B^52). We use d = 0, D = 1 and choose (p,q,P,Q) from a small grid by **AIC** (AIC = 2r - 2 ln L, r parameters, L the likelihood; BIC uses r ln n). *Box-Jenkins:* identify (ACF/PACF, differencing) -> estimate -> check residuals (Ljung-Box) -> forecast. Prediction intervals use the psi-weights: Var = sigma^2(1 + sum psi_j^2) (Lecture 28).
*Peculiarities (important, expect questions):*
1. **Diffuse initialisation.** A state-space model with D = 1 starts with a diffuse prior on its first 52 seasonal states, so the first 52 "residuals" equal the series itself. Ljung-Box with them kept gives p of about 0 at every lag; with them dropped (and the 3 fitted ARMA terms deducted from the degrees of freedom) it passes at lags 10 and 26 (p = 0.49, 0.10) but not at lag 52 (p = 0.016): a yearly pattern is still left. The first version of the project mistook this artifact for a bad model.
2. **Seasonal MA coefficient -0.99** with a standard error of about 8: on the boundary of invertibility, not identified. A seasonal MA(1) near -1 is the standard sign of over-differencing (the yearly pattern is fixed, so differencing injects artificial MA structure). This motivates modelling the seasonal pattern directly.
3. **Short data.** With two training years the seasonal difference leaves one year of information; SARIMA's 2017 MAE is 72.3 (seasonal mean 31.0) and its interval covers only 23% of weeks.

### 4.7 Harmonic regression with ARMA errors (Lectures 13-16; FPP3 sec. 10.5)
x_t = c + sum_k [a_k sin(2 pi k t/m) + b_k cos(2 pi k t/m)] + eta_t, eta_t ~ ARMA(p,q), m = 365.25/7. A regression with autocorrelated errors in which the yearly shape has only 2K parameters (K <= 10, chosen with (p,q) by AIC; K = 6, 6, 7 at the three origins, so the search is not cut off). *"Doesn't a Fourier fit just reproduce the past?"* No: K pairs are 2K numbers describing a smooth curve (K = 1 is one wave, K = 4 already follows the winter peak), versus 52 free values for the seasonal mean. It is the direct alternative to differencing.

### 4.8 Forecast combination (Lecture 30)
Equal-weight average of the log forecasts of the seasonal mean, Holt-Winters, SARIMA and harmonic regression. No interval (we only combine point forecasts). The lecture notes that a combination is not guaranteed to be better than every member.

### 4.9 Evaluation: expanding-window backtest, error measures, intervals (Lectures 23, 28, 30)
Three origins (end of 2016, 2017, 2018) forecast the next 52 weeks. At every origin each model is refitted and **all choices are redone with earlier data only**. Errors e = actual - forecast on the original scale: **ME** (bias; negative = over-prediction), **MAE**, **RMSE**, **MAPE**. **Coverage** = share of test weeks inside the 95% interval exp(mu +/- 1.96 sd). Only three test years: honest conclusions are "cannot be told apart", not rankings. 2019 was looked at in earlier project iterations (all selection in the code uses only earlier data).

### 4.10 Diebold-Mariano test (Lecture 30)
d_t = |e_a| - |e_b|; H0: E(d_t) = 0; DM = mean(d)/sqrt(V/N). Errors of a 52-step forecast are strongly autocorrelated, so V is a long-run variance with a Bartlett kernel (12 lags). A large p means "cannot be told apart", not "equal". We pool 2018-19 and compare with the seasonal mean. For one-step forecasts the Harvey-Leybourne-Newbold small-sample version is used. As a robustness check the report also gives an 8-week circular block bootstrap interval of the same difference.

### 4.11 VAR and Granger causality (handout lectures 35-37)
**Anomalies:** subtract each calendar day's smoothed average over the five years (the seasonal mean of that day). Needed because wind, humidity and PM2.5 all follow the calendar; without it any test mostly detects "it is winter". **VAR(p):** each of (wind, humidity, log PM2.5) is regressed on the last p days of all three. p is chosen by AIC (4) and BIC (2); we use 4; the residuals pass a portmanteau test (p = 0.17). **Granger test:** in the PM2.5 equation, H0: all lag-1..p wind coefficients are zero, tested by an F-test. Rejection means wind's past improves the *prediction* of PM2.5 given PM2.5's and humidity's past; it is not proof of a physical cause, and it does not say wind is the only driver. Reverse directions (PM2.5 -> wind, humidity) are not significant (p = 0.12, 0.62).
**Weekly scale:** on deseasonalised weekly data, adding last week's wind and humidity to last week's PM2.5 changes R^2 from 0.123 to 0.128 (F-test p = 0.47): nothing. Same-week weather has R^2 = 0.17 but is only known with hindsight.
**One week ahead:** harmonic model one-step forecasts: no weather 21.5, + last week's weather 22.1 (+2.6%, DM p = 0.04: slightly *worse*), + same-week weather (oracle, unusable) 20.0; persistence 30.7, seasonal mean 24.8.
**Reconciling "weather predicts" with "weather adds nothing":** different time scales. Weather moves PM2.5 over a few days; the effect is gone within a week, so for weekly or yearly forecasts it adds nothing (a yearly forecast would also need a weather forecast first).

### 4.12 The 2020 what-if (Q3)
A model fitted on 2015-2019 cannot predict a lockdown. We use 2020 two ways: **January-February** is a genuine out-of-sample test (MAE 28-42, larger than in 2017-19 because actual values already ran 7-17% below the forecasts, the same level bias seen in earlier years); **the ten lockdown weeks** compare actual (49 ug/m3) with the business-as-usual forecast (86-97 depending on the model): gap -44% to -50%; after removing each model's Jan-Mar bias, -34% to -41%. *Yardstick:* the same ten-week gap for every window of the 2017-19 backtests (harmonic model: 5th-95th percentile -31% to +23%, lowest -36%) and for the same calendar weeks of 2019 (-4% to -21%). For the seasonal mean, harmonic regression, combination and naive no ordinary window is as low as 2020; for Holt-Winters and SARIMA, whose 2017 forecasts were poor, a few are (3% and 1% of windows). Descriptive, not causal.

## 5. Results (numbers and where they live)

| Item | Value | File |
|---|---|---|
| Winter / monsoon mean, ratio | 217 / 48 ug/m3, 4.5x | `results/season_stats.csv`, `key_numbers_eda.json` |
| Seasonal / trend strength (STL 2015-19) | 0.90 / 0.18 | `key_numbers_eda.json` |
| Log: corr(monthly mean, SD) raw / log | 0.94 / -0.09 | `log_justification.csv` |
| ACF lag 1 / 26 / 52 | 0.87 / -0.43 / 0.68 | `acf_weekly_train.csv` |
| ADF p, KPSS (log level, train) | 5e-4, 0.058 | `stationarity_train.csv` |
| SARIMA candidates AIC, all d = 0, D = 1 (A-E) | 73.2, 53.9, 39.4 (best), 45.2, 57.5 | `fc_sarima_identification.csv` |
| Seasonal MA coefficient | -0.99 (SE about 8) | `key_numbers_forecast.json` |
| MAE 2017 / 2018 / 2019 | naive 38.4/29.0/30.3; mean 31.0/21.8/27.8; HW 44.7/19.2/32.2; SARIMA 72.3/21.1/27.5; harmonic 29.4/22.5/26.4; combination 38.2/20.1/27.6 (2018-19 mean: 29.6, 24.8, 25.7, 24.3, 24.5, 23.8) | `fc_backtest_mae.csv` |
| ME 2018-19 (all negative) | -8 to -15 | `fc_backtest_me.csv` |
| DM vs seasonal mean (2018-19) | naive +4.8 (p 0.03), HW +0.9 (0.57), SARIMA -0.5 (0.49), harmonic -0.3 (0.74), combination -0.9 (0.08) | `fc_dm.csv` |
| Coverage 2017 / 2018 / 2019 | mean 62/92/81, SARIMA 23/94/85, harmonic 65/92/87 (%) | `fc_coverage.csv` |
| VAR lag AIC / BIC | 4 / 2 | `var_lag_selection.csv` |
| Granger p: wind, humidity -> PM2.5 | 1e-29, 1e-11 (still < 1e-8 with temperature, rain) | `granger_var.csv`, `granger_var_controls.csv` |
| Weekly nested test | R^2 0.123 -> 0.128, p = 0.47 | `weekly_lag_nested.csv` |
| One-week MAE | persistence 30.7, mean 24.8, harmonic 21.5, + last week's weather 22.1, oracle 20.0 | `fc_oneweek.csv` |
| Lockdown gap (10 weeks) | -44% to -50% (adjusted -34% to -41%) | `fc_lockdown.csv`, `fc_lockdown_windows.csv` |

The speaker notes (`SPEAKER_NOTES.md`) repeat the relevant numbers slide by slide.

## 6. Limitations and peculiarities (the full honest list)

- **Few independent tests.** Three annual origins cannot rank similar models. 2017 has only two training years (stress test). 2019 was looked at in earlier iterations of the project; selection in the code uses only earlier data.
- **Level drift not modelled.** Annual means fall 22% from 2016 to 2019, so every model over-predicts (ME < 0) and intervals are too narrow in 2019 (81-87% coverage) and 2017 (23-89%). The station count also changed (10 -> 37).
- **SARIMA is fragile on short data** (see 4.6), and AIC across different differencing is only a rough guide.
- **Holt-Winters' frozen seasonal index** (alpha-delta fit near 0) is a property of this short sample, not a bug.
- **Median vs mean.** exp(mu) is the median of PM2.5; MAE is computed on it.
- **Weather is a reanalysis at one grid point**; boundary-layer height, stubble burning and fireworks are unmeasured. Granger causality is predictive only.
- **Lockdown gap is model-relative** and descriptive; other things changed in 2020 too. The bias adjustment assumes the pre-lockdown bias would have persisted.
- **Interval for the combination** is not defined (point forecast only).
- **Runtime/seeds.** The models are deterministic; the block bootstrap (report robustness line) uses a fixed seed. Notebook 04 takes 15-25 minutes.

## 7. What changed from the earlier version (so you can answer "what did you change?")

| Earlier | Now | Why |
|---|---|---|
| "Climatology" benchmark | "Seasonal mean", explained with a worked example | The name and definition confused readers; it is the classical seasonal index |
| Dynamic harmonic regression with level types, AICc, inner validation year | Harmonic regression with ARMA errors, constant level, K and (p,q) by AIC | Matches the course (L29 AIC) and is simpler |
| Fixed SARIMA(1,0,1)(0,1,1) and a D = 0 variant | SARIMA with orders chosen by AIC from a grid at each origin | The Box-Jenkins identify-estimate-check cycle |
| Linear regression, Climatology + AR(1), LSTM | Holt-Winters and a forecast combination | In the course (L22-23, L30); the LSTM was not |
| Winkler score, calibrated intervals, simulation, PM2.5 bands | ME/MAE/RMSE/MAPE, coverage, DM test | In the course (L30, L28) |
| HAC Wald tests, shocks, impulse responses, FEVD | VAR lag table (AIC/BIC), plain Granger F-tests both ways, weekly nested test | Out of syllabus; the earlier slides read as jargon |
| 2020 "outlook" with monthly intervals and band-days | 2020 as a what-if against a business-as-usual baseline, with a yardstick | A model fitted before 2020 cannot forecast a lockdown |
| STL on 2015-2020 weeks (trend bent by 2020) | STL on 2015-2019 | 2020 is not a modelling year |
| Holt-Winters started from a heuristic (first two years) | Initial state estimated by maximum likelihood (Lecture 23) | The heuristic start handicapped the model (MAE 2018: 24.2 -> 19.2) |
| Harmonic regression search K <= 5 (K = 5 chosen at every origin) | K <= 10; K = 6, 6, 7 chosen | The old search stopped at its own upper bound |
| SARIMA candidates with different differencing in one AIC table | Five candidates with the same d = 0, D = 1 | AIC is only comparable on the same differenced data |
| Ljung-Box with 2 degrees of freedom deducted | 3 (ar, ma, seasonal ma) | Matches the three fitted ARMA parameters |
| Poor-days share computed on all days incl. 2020 | 2015-2019 only (54%) | The label said 2015-2019 |
| 46 dense slides without notes | slide-by-slide notes (`SPEAKER_NOTES.md`, `notes.tex`) | Each slide has a structure and a script |
| 57-page deck with section-overview slides, lecture numbers and one slide per model | 28 slides + 4 backup slides: one plain slide for the three models, one 2x2 ACF/PACF slide, one 2019-forecast slide, lecture numbers and "course" wording removed; equations, AIC table, harmonic curve and DM formula moved to the backup | Shorter, no jargon; backup is used only if asked |

## 8. Likely viva questions (short answers)

1. **Why weekly?** Daily data are noisy; weekly means give a clean seasonal period s = 52 for the seasonal models.
2. **Why log?** Seasonal swings grow with the level (corr. of monthly SD and mean 0.94); after log it is -0.09. Multiplicative -> additive (L06).
3. **What is F_S and where does it come from?** From the STL decomposition: 1 - Var(remainder)/Var(seasonal + remainder) = 0.90.
4. **ADF and KPSS pass, yet you say it is non-stationary. Contradiction?** No: they test for a unit root / constant mean, not for a regular yearly swing; the ACF shows the yearly wave.
5. **Why the seasonal difference, and why is it a problem?** It removes the yearly cycle, but with a fixed yearly pattern it over-differences (seasonal MA = -0.99, ACF at lag 52 = -0.34).
6. **What is the difference between seasonal naive and seasonal mean?** Naive repeats last year's value; the mean averages that week over all training years (noise averages out).
7. **Does the Fourier fit just copy the past?** No: 2K parameters describe a smooth curve; the seasonal mean has 52.
8. **Why is SARIMA not the winner?** Ties with the seasonal mean with three or more years (24.3 vs 24.8) but fails with two (72.3); over-differenced.
9. **Why is Holt-Winters erratic?** Its seasonal smoothing parameter is about 0, so the seasonal index is learnt once and barely updated; MAE 44.7, 19.2, 32.2 across the three years, not significantly different from the seasonal mean (p = 0.57).
10. **What do the Ljung-Box results on the first 52 residuals mean?** They are not forecast errors (diffuse initialisation); drop them.
11. **What does coverage tell you?** Share of weeks inside the 95% interval; ours are too narrow when the level drifts (2019: 81-92%, 2017 SARIMA 23%).
12. **What does the DM test say?** No model is significantly better than the seasonal mean (the combination's 0.9 edge has p = 0.08); only the seasonal naive is significantly worse (p = 0.03).
13. **What is a Granger test? What is the null?** F-test that the past of X adds no prediction of Y beyond Y's (and the other variables') past. Not a physical cause.
14. **Why did you deseasonalise first?** All three series share the seasonal cycle; otherwise the test mostly detects "it is winter".
15. **How did you pick VAR(4)?** AIC minimum at 4, BIC at 2 (VAR slide; lag table in the report); residuals pass the portmanteau test.
16. **Weather predicts daily but not weekly; contradiction?** Different time scales; the daily effect is gone within a week.
17. **Why do you call the 2020 result a what-if?** A model fitted on 2015-2019 cannot predict a lockdown; after March it is a business-as-usual baseline.
18. **How do you know the lockdown gap is not just forecast error?** Compare with the ten-week gaps in 2017-19 (harmonic: -31% to +24%, lowest -35%) and with the same weeks of 2019 (-15%).
19. **Why the median?** exp() of the log forecast is the median; the mean is exp(mu + sigma^2/2).
20. **What would you do with more time?** More forecast origins/years, model the level drift, add a boundary-layer-height or stubble-burning variable, and check with a longer sample.

## 9. Glossary

**Anomaly:** value minus its seasonal mean. **AIC/BIC:** information criteria (fit minus parameter penalty), smaller is better. **Business as usual:** the model's path without the lockdown. **Coverage:** share of actual values inside the prediction interval. **DM test:** Diebold-Mariano test of equal forecast accuracy. **ERA5:** ECMWF reanalysis (modelled weather). **Expanding window:** training set grows at each forecast origin. **F_S:** STL seasonal strength. **Granger causality:** predictive usefulness. **Harmonic regression:** regression on sines/cosines of the yearly period. **Holt-Winters:** exponential smoothing with trend and seasonality. **Ljung-Box:** test for leftover autocorrelation in residuals. **ME/MAE/RMSE/MAPE:** mean error/mean absolute error/root mean squared error/mean absolute percentage error. **Median forecast:** exp(forecast of the log). **SARIMA:** seasonal ARIMA. **Seasonal mean:** average of the same calendar week across training years. **Seasonal naive:** same week last year. **STL:** seasonal-trend decomposition using LOESS. **VAR:** vector autoregression.

## 10. Appendix: references and how each was verified

The report cites 23 references. **Crossref** = DOI looked up at `api.crossref.org/works/<doi>` and authors, title, year, journal, volume, issue and pages compared with the bibliography entry (first 17 on 17 Nov 2026, the six marked * on 20 Nov 2026).

| # | Reference | How verified | Result |
|---|---|---|---|
| 1 | CPCB, National Air Quality Index, Oct 2014 | web search of the NIUA-hosted copy; PM2.5 breakpoints confirmed on a page citing CPCB | confirmed; PDF not fetchable, cited by title and issuer |
| 2 | Box, Jenkins, Reinsel, Ljung, *Time Series Analysis: Forecasting and Control*, 5th ed., Wiley, 2015 | confirmed as the course textbook (Handout) | confirmed |
| 3 | Rao, Kaggle "Air Quality Data in India (2015-2020)" | page returns HTTP 200; title and owner confirmed | confirmed |
| 4 | Hersbach et al. 2020, ERA5, QJRMS 146(730):1999-2049 | Crossref 10.1002/qj.3803 | match |
| 5 | Zippenfenig 2023, Open-Meteo.com Weather API, Zenodo | DOI 10.5281/zenodo.7970649 from open-meteo.com licence page; resolves via doi.org; not in Crossref (DataCite) | confirmed (concept DOI) |
| 6 | Cleveland et al. 1990, STL, J. Official Statistics 6(1):3-73 | statsmodels/stlplus documentation cite exactly this; no DOI | confirmed |
| 7 | Box and Cox 1964, JRSS-B 26(2):211-243 | Crossref 10.1111/j.2517-6161.1964.tb00553.x | match |
| 8 | Dickey and Fuller 1979, JASA 74(366a):427-431 | Crossref 10.1080/01621459.1979.10482531 | match |
| 9 | Kwiatkowski et al. 1992, J. Econometrics 54(1-3):159-178 | Crossref 10.1016/0304-4076(92)90104-Y | match |
| 10 | Sims 1980, Econometrica 48(1):1-48 | Crossref 10.2307/1912017 | match |
| 11 | Granger 1969, Econometrica 37(3):424-438 | Crossref 10.2307/1912791 | match |
| 12 | Hyndman and Athanasopoulos, FPP3, sec. 10.5 | otexts.com/fpp3/dhr.html fetched | confirmed (authorship standard, not printed on the page) |
| 13 | Tashman 2000, Int. J. Forecasting 16(4):437-450 | Crossref 10.1016/S0169-2070(00)00065-0 | match |
| 14 | Diebold and Mariano 1995, JBES 13(3):253-263 | Crossref 10.1080/07350015.1995.10524599 | match |
| 15 | Harvey, Leybourne, Newbold 1997, Int. J. Forecasting 13(2):281-291 | Crossref 10.1016/S0169-2070(96)00719-4 | match |
| 16 | Ljung and Box 1978, Biometrika 65(2):297-303 | Crossref 10.1093/biomet/65.2.297 | match |
| 17 | Mahato, Pal, Ghosh 2020, Sci. Total Environ. 730:139086 | Crossref 10.1016/j.scitotenv.2020.139086 | match |
| 18* | Holt 2004, Int. J. Forecasting 20(1):5-10 (reprint of the 1957 memorandum) | Crossref 10.1016/j.ijforecast.2003.09.015 | match |
| 19* | Winters 1960, Management Science 6(3):324-342 | Crossref 10.1287/mnsc.6.3.324 | match |
| 20* | Akaike 1974, IEEE Trans. Automatic Control 19(6):716-723 | Crossref 10.1109/TAC.1974.1100705 | match |
| 21* | Schwarz 1978, Ann. Statist. 6(2):461-464 | Crossref 10.1214/aos/1176344136 | match |
| 22* | Box and Pierce 1970, JASA 65(332):1509-1526 | Crossref 10.1080/01621459.1970.10481180 | match |
| 23* | Bates and Granger 1969, J. Oper. Res. Soc. 20(4):451-468 | Crossref 10.1057/jors.1969.103 | match |

References from the earlier version that are no longer cited (Engle 1982, Newey-West 1987, Pesaran-Shin 1998, Lutkepohl 2005, Hurvich-Tsai 1989, Hochreiter-Schmidhuber 1997, Winkler 1972, Gneiting-Raftery 2007, Kunsch 1989, Durbin-Koopman 2012) were dropped together with the methods they supported.
