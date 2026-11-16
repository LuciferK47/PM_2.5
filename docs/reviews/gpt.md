Executive assessment
I have reviewed the project overview, data-processing code, exploratory analysis, VAR/Granger results, SARIMA draft, previous critical review, all 16 questions, and presentation script.

My overall assessment: the project has a strong analytical foundation, but its forecasting methodology and final real-world interpretation need substantial refinement.

I would preserve most of Phases 1–3, correct several statistical claims, and make Phase 4 a rigorous comparison of interpretable seasonal forecasting models rather than a demonstration that SARIMA is marginally better than a basic baseline.
Current evidence from the 2019 holdout

52 weekly forecasts

SARIMA MAE
27.5
µg/m³

Climatology MAE
27.8
µg/m³

95% interval coverage
84.6%
44 of 52 weeks



The reported SARIMA improvement is only 0.3 µg/m³, approximately 1.1% relative to climatology. That is not convincing evidence of superior forecasting without further evaluation. Meanwhile, the predictive interval misses eight weeks rather than the roughly two or three expected under a well-calibrated 95% procedure.

My preferred strategy is to introduce dynamic harmonic regression (Fourier terms plus ARMA errors) as a serious alternative, retain SARIMA as a benchmark, fix the forecast evaluation and uncertainty estimates, and distinguish forecasts of average PM2.5 from actual AQI and daily health-risk categories.

These results come from the supplied summaries and tables. The original processed CSVs and executable notebooks were not among these nine files, so my independent checks concern the supplied calculations, code logic, and statistical interpretation rather than a complete rerun of the original analysis.
I. Where I agree with the previous critical review
I agree with its central findings:
- Data preparation is generally sound. Only two PM2.5 observations required interpolation, the weekly aggregation is documented, and 2020 was appropriately excluded from the primary VAR and 2019 holdout forecasting exercise.
- The Granger analysis has meaningful robustness checks. Wind and humidity have strong conditional predictive associations with PM2.5 after controlling for seasonal patterns. This is not proof of physical causation.
- The SARIMA diagnostics are mishandled. The first 52 residuals from the seasonally differenced state-space model should not be naively included in the Ljung–Box test. The previous review reports that correcting this produces p-values of 0.49 at lag 10 and 0.10 at lag 26.
- The near-boundary seasonal MA parameter is a warning. A fitted seasonal MA coefficient of −0.988 calls for testing models without seasonal differencing.
- The 2018 model-selection procedure is contaminated. Orders were chosen using 2015–2018, then judged on 2018. This is not a truly out-of-sample validation.
- With only four training seasons, the LSTM is unlikely to be competitive. Simpler seasonal methods deserve priority.
I also agree that interval calibration, the uncertainty around the 2019 decline, and the distinction between statistical predictability and actual public-health advisories need more attention.
II. Where I disagree or would qualify the review
1. The interval problem is not merely excessive narrowness.

I independently parsed and recalculated the 52 rounded forecast rows supplied in file 05. All eight observations outside the 95% intervals fall below the lower bound. None exceeds the upper bound.

That asymmetry matters. It suggests that a forecast-level bias or distributional shift may be a major contributor to the undercoverage. Simply widening both sides is not necessarily the best correction.

2. A seasonal MA coefficient near −1 is not proof of over-differencing.

For a model containing \((1-B^{52})\) and a seasonal MA factor close to \((1-B^{52})\), near cancellation is indeed suspicious. But model equivalence, finite-sample estimation, and the confidence interval of the coefficient matter. I would call this strong diagnostic evidence to investigate, not a definitive finding.

3. The review is too confident that corrected Ljung–Box results mean the residuals are fine.

Non-rejection at lags 10 and 26 does not establish white noise. Seasonal lag 52, residual squared autocorrelations, stability and the adequacy of predictive distributions still need checking. Moreover, at 209 training observations, removing 52 initialization observations leaves relatively little information.

4. A conventional Diebold–Mariano test cannot rescue the 2019 comparison.

The 52 forecasts are different horizons produced from essentially one annual forecast origin, not 52 independent replications of a 52-week forecasting experiment. A naive test over the 52 weekly errors would not deliver reliable evidence of long-horizon superiority.

5. The review's lognormal bias correction is incomplete.

The claimed correction of approximately 2.3% uses the fitted innovation variance, 0.046. For a long-horizon forecast, the correct lognormal mean adjustment depends on the horizon-specific predictive variance, which generally changes with the forecast horizon.
III. Important new issues the review missed
Critical: PM2.5 category is not necessarily the actual AQI category

Your src/aqi.py classifies PM2.5 concentration using CPCB pollutant breakpoints. However, India's overall AQI is obtained using the highest eligible pollutant sub-index, not PM2.5 alone. It uses the prescribed short-term concentration windows. 
airquality.cpcb.gov.in+1


The table must be labelled PM2.5-based risk band unless you also forecast the other relevant pollutants and calculate the complete AQI.



High: Granger lag-order significance is being misinterpreted

The pairwise test at lag 7 jointly tests lagged terms 1–7. It does not prove that every individual lag has a significant effect, or that the effect persists precisely seven days. Your presentation repeatedly makes that distinction unclear.



High: The 2019 decrease may be affected by changes in monitor coverage

An independent review of Delhi's monitoring network describes substantial expansion and uneven completeness during 2015–2019. A peer-reviewed Delhi study specifically notes that station coverage can affect interpretations of historical improvement. 
cseindia.org+2


Your city-average series alone cannot separate actual emissions improvement from changes in the stations contributing observations.



Medium: Seasonal indexing has calendar inconsistencies

The forecasting code caps ISO week numbers at 52, merging ISO week 53 into week 52. SARIMA uses a fixed 52-week period (364 days), whereas the calendar year is approximately 365.24 days. The daily climatology also handles leap years by capping day-of-year 366 rather than adjusting post-February dates consistently.

None is likely to invalidate the project, but these are avoidable seasonal alignment problems.



There are also two presentation-level errors worth correcting immediately. The claim that humidity remains significant at p below \(10^{-10}\) in every specification is false: after adding the rain control, the supplied value is \(2.79\times10^{-8}\). And the shock-bin table describes same-day associations; its wording must not imply the plotted comparison is necessarily a following-day response.
IV. Answers to the 16 project questions
Part A — Forecasting design
Q1. Which forecasting models should we prioritise?
For your dataset — 209 weekly training observations, approximately four complete seasonal cycles and a 52-week forecast horizon — this is my expected ranking, not an experimentally established leaderboard.
Rank	Model	Assessment
1	Fourier regression + ARMA errors	Best primary candidate. Smooth annual seasonality with relatively few parameters
2	Climatology + AR(1) anomalies	Strong, interpretable challenger; short-run corrections decay at long horizons
3	Seasonal climatology	Essential benchmark; highly competitive for annual forecasts
4	ETS/TBATS	Worth testing, particularly a parsimonious TBATS specification
5	SARIMA, \(D=0\)	Reasonable alternative; may model the seasonality without integration
6	SARIMA, \(D=1\)	Existing candidate, but near-boundary seasonal MA makes it fragile
7	Prophet-style additive model	Additional trend flexibility, but limited history for reliable changepoints
8	LSTM	Highest overfitting risk with 209 observations and a 52-step horizon

The distinction between ranks 2–6 is uncertain; any could outperform the others on a particular historical year. Importantly, the existing \(D=1\) SARIMA has already beaten climatology by a small amount on 2019.

The model I would implement first is dynamic harmonic regression:
\[
\log(PM_{2.5,t})=
\beta_0+\sum_{k=1}^{K}
\left[
a_k\sin\left(\frac{2\pi kt}{52.18}\right)+
b_k\cos\left(\frac{2\pi kt}{52.18}\right)
\right]+u_t
\]

with \(u_t\) following a low-order ARMA process, initially AR(1) or ARMA(1,1).

Try \(K=1,\ldots,5\), using AICc or properly nested time-series validation. With \(K=3\), the seasonal part uses only six Fourier coefficients rather than estimating a separate seasonal effect for every week.

Why this is attractive: your strongest established fact is the predictable annual pattern, not a reliable long-term stochastic trend. Fourier regression models that directly, without requiring a seasonal unit root.
Q2. Is the seasonal MA value of −0.988 evidence of over-differencing?
Yes, it is a warning, but not proof.

The fitted seasonal component resembles:
\[
\frac{1-0.988B^{52}}{1-B^{52}}
\]

The numerator almost cancels the seasonal differencing denominator. This suggests that the apparent seasonal integration may be unnecessary.

I would:
1. Fit \(D=0\) with Fourier terms plus ARMA errors.
2. Fit a simpler \(D=0\) seasonal ARIMA, such as \((1,0,1)(1,0,0)_{52}\).
3. Retain the existing \((1,0,1)(0,1,1)_{52}\) as a benchmark.
4. Compare parameter stability, residual diagnostics, rolling-origin errors and interval coverage.
The Fourier model is my preferred alternative; 52 unrestricted seasonal dummies are less attractive with only four observed years, although regularised or smoothed seasonal effects are reasonable.
Q3. How should we handle the downward trend?
The series reports yearly PM2.5 means of 137.5 in 2016, 126.4 in 2017, 114.5 in 2018 and 108.1 in 2019.

That is consistent with a decrease, but it does not establish whether the cause is cleaner air, station-network changes or both.

The independent literature supports treating monitoring-network changes as a real concern, rather than merely a hypothetical issue. 
MDPI+1


I recommend three sensitivity experiments:
- Trend comparison: constant level versus linear trend versus damped trend, selected using historical forecast accuracy.
- Fixed-station robustness: construct an annual series using only stations with sufficiently complete data across the relevant years, if station-level data can be obtained.
- Recent-period comparison: compare the same calendar months across years, and evaluate whether results change when older years receive less weight.
Do not compare the first half of 2020 directly with complete prior years as evidence of an underlying downward trend; it is both seasonally incomplete and affected by the lockdown.

Avoid fitting an unconstrained linear downward trend and extrapolating it indefinitely. That could produce implausibly low long-range concentrations.
Q4. How should the 95% prediction intervals be fixed?
My recommended approach is bias-aware, seasonally calibrated predictive simulation, not an elaborate neural quantile model.

A sensible order of operations:
1. Fix the forecasting mean model first.
2. Examine forecast errors on the log scale by season and horizon.
3. Estimate seasonal residual variability with shrinkage toward a pooled variance, rather than 12 independent monthly variances.
4. Simulate future paths, preferably using a residual or block bootstrap that preserves temporal dependence.
5. Calibrate using earlier validation forecasts only, then report untouched-period coverage and interval scores.
Your eight misses being exclusively below the lower interval bound makes the level-bias investigation particularly important.

I would not claim distribution-free 95% conditional coverage from conventional conformal prediction here. With only two or three largely overlapping annual validation paths, the calibration sample is far too limited for a reliable horizon-specific guarantee.

Report both empirical coverage and interval width or weighted interval score. An interval wide enough to include almost everything is not necessarily useful.
Q5. What rolling-origin evaluation should we use?
Keep the existing 2019 results, but add expanding-window evaluations with the same 52-step forecast horizon.
Forecast origin	Training period	Next 52 weekly predictions
25 Dec 2016	104 weeks	1 Jan–24 Dec 2017
31 Dec 2017	157 weeks	7 Jan–30 Dec 2018
30 Dec 2018	209 weeks	6 Jan–29 Dec 2019

The first fold is intentionally difficult because it has only two training seasons. Treat that as a robustness stress test and show results separately from the better-supported 2018 and 2019 folds.

For every origin, reselect orders and Fourier complexity using only information available up to that origin. Do not use 2018 to select a model that is subsequently evaluated as though 2018 were unseen.

Compare each model using raw-scale MAE, RMSE, log-scale MAE, winter MAE, bias, interval coverage and interval score.

For significance testing, a paired loss-differential analysis with serial-dependence-aware uncertainty, such as a block bootstrap or HAC-based Diebold–Mariano approach, is preferable to a naive paired t-test. But these data provide too few effectively independent annual experiments for a trustworthy strong significance claim.

Report the loss differential and uncertainty, but be willing to conclude that two models are statistically indistinguishable.
Q6. Should we forecast weekly, daily or monthly pollution?
That depends on what the final advisory claims.
Intended output	Best target
Annual seasonal outlook	Weekly mean PM2.5
Month-by-month average pollution outlook	Monthly mean PM2.5, directly or by aggregating forecast paths
Number of Poor/Very Poor/Severe days	Daily PM2.5
Actual official AQI probabilities	All necessary pollutant sub-indices, or a separately validated AQI model

For your course project, I would retain weekly forecasting as the primary statistical exercise and make a monthly PM2.5 risk outlook, rather than incorrectly presenting weekly averages as daily AQI categories.

For example, generate many simulated weekly PM2.5 trajectories, then compute the monthly mean for every trajectory. From that distribution report the median, 95% interval and probability of a monthly PM2.5 mean exceeding a clearly stated threshold.

If you want the expected number of severe days, you will need a daily model or a calibrated within-week distribution. Weekly means alone cannot recover daily extremes.
Q7. How should we test whether weather improves one-week forecasts?
Use three explicitly different experiments.
Experiment	Weather known at prediction time?	Interpretation
Lagged weekly wind and humidity	Yes	Genuine operational one-week forecast
Archived forecasts of next week's weather	Yes, if real forecast archives are available	Operational weather-informed forecast
Actual same-week ERA5 weather	No	Oracle or hindsight-assisted upper bound

The current draft implements the third option, not the second. ERA5 historical reanalysis is not an archived weather forecast.

At the end of each Sunday, predict the following Sunday's weekly mean using the previous week's pollution, the previous week's weather, and calendar features. Test predictions over 2019 sequentially, allowing the model to incorporate past observed pollution as each week passes.

Also tune the short-horizon model independently; the SARIMA order selected for an entire 52-week forecasting path need not be optimal for next-week prediction.

Report whether any improvement from weather is out-of-sample and practically meaningful, not just whether its fitted coefficients are significant.
Part B — VAR, Granger causality and interpretation
Q8. Is the weather-to-PM2.5 Granger conclusion well supported?
Yes, as a finding of conditional predictive association. No, as a demonstrated physical causal effect.

The evidence is reasonably strong:
Specification	Wind → PM2.5	Humidity → PM2.5
VAR(4), standard F-test	\(1.73\times10^{-29}\)	\(1.11\times10^{-11}\)
VAR(2), BIC selection	\(5.85\times10^{-32}\)	\(4.58\times10^{-13}\)
VAR(4), HAC Wald test	\(8.38\times10^{-20}\)	\(2.94\times10^{-11}\)
HAC, with rain control	\(4.17\times10^{-19}\)	\(2.79\times10^{-8}\)

These are the supplied p-values, not independently rerun tests.

The weakest link is not statistical significance. It is the interpretation of a restricted observational model with omitted meteorological and emissions-related variables.

Boundary-layer height, temperature, regional transport and changing emissions could affect both weather measurements and PM2.5. They could alter estimated coefficients even when p-values remain very small.

I would retain the result but change the conclusion to:
After removing the estimated seasonal cycle, lagged wind and humidity anomalies significantly improve the in-sample prediction of Delhi's PM2.5 anomalies in several VAR specifications. This supports short-horizon Granger predictability but does not establish physical causation.

One further point: in-sample Granger significance does not guarantee improved out-of-sample forecast accuracy. Your Phase 4 experiment should test that distinction.
Q9. Are Cholesky impulse responses defensible?
Yes, provided they are presented as identification-dependent model results.

Your two orderings produce:
Metric	Weather-first ordering	PM2.5-first ordering
Wind, day-1 response	−11.9%	−5.9%
Humidity, day-1 response	−6.8%	−4.0%
Weather share of 14-day FEVD	29.9%	6.3%

Those are large differences. The FEVD figures are not confidence bounds around a single estimated causal contribution.

I recommend retaining the Cholesky results and adding generalised impulse responses as one ordering-invariant robustness analysis. A local-projection model with lagged controls and HAC errors would be a worthwhile extension if time remains, but it would still not prove causality without credible shock identification.

Also include confidence intervals for the impulse-response curves. Point estimates alone are insufficient for strong statements about effect magnitude or duration.
Q10. What is the best additional analysis of humidity?
A season-interacted regression of the PM2.5 anomaly equation provides the best benefit for the effort.

The existing evidence suggests different humidity relationships across monsoon and other months. You can test this without fitting a complicated nonlinear VAR.

Use the existing lag structure and add interactions between lagged humidity anomalies and a monsoon indicator. Then conduct a joint HAC Wald test of whether those interaction coefficients equal zero.

This addresses the question:

Does lagged humidity contain different predictive information during the monsoon?

If you have time, repeat with winter versus non-winter periods.

I would skip threshold VARs, neural nonlinear Granger models and regime-switching VARs. They introduce substantial complexity and model-selection uncertainty without clearly improving the core course-project result.
Q11. Should KPSS rejection change the main VAR specification?
It should trigger a robustness analysis, not automatically force the primary model to use first differences.

For the PM2.5 anomaly, ADF rejects a unit root, whereas KPSS rejects level stationarity. This can arise from deterministic drift, structural breaks, residual seasonality or other departures from the assumed stationary process.

My recommended sequence is:
1. Fit the existing anomaly VAR.
2. Add a pre-specified deterministic time trend or year-level controls as a sensitivity specification.
3. Examine parameter stability and residual stationarity.
4. Retain the first-differenced VAR as a robustness check.
Do not interpret ADF rejection as proof of stationarity, nor KPSS rejection as proof that the series is integrated.

The full-sample climatology is acceptable for a retrospective explanatory exercise, provided that use is explicitly disclosed. It is not acceptable for constructing genuinely out-of-sample forecasting features.
Q12. Which additional variables matter most?
I would prioritise them as follows:
Variable	Scientific value	Implementation priority
Temperature	Important meteorological control; already available	1
Boundary-layer height	Highly relevant to dilution, dispersion and pollution trapping	2
Regional fire counts	Useful for investigating seasonal emissions and transport	3
NO2	Possible emissions proxy, but interpretation is complicated	4

Temperature should be added first because it is already in your processed data. Boundary-layer height is arguably the more informative physical variable, but obtaining and aligning it adds work.

NO2 needs particular care: it may itself respond to weather and share emissions sources with PM2.5. Conditioning on it does not automatically give a cleaner estimate of weather's causal effect.

Could the main conclusion change? The direction and magnitude of the weather coefficients could change, and some individual significance tests might weaken. I would not predict the outcome without running the expanded model.
Part C — Methodology and reporting
Q13. Is the log transformation sufficiently justified?
Yes. This is one of the better-supported choices in the project.
Before log transformation
7.90×
Ratio of maximum to minimum monthly standard deviation

After log transformation
1.34×
Ratio of maximum to minimum monthly standard deviation


The improvement in variance stability is substantial, even though the Levene test continues to reject equality of variance.

One distinction the previous review underemphasised: the reported ARCH-LM statistic of 36.43 was calculated on daily log changes, not on the final weekly SARIMA innovations.

It does not prove that the final weekly forecasting model needs GARCH.

My recommendation is to retain the log transform, examine properly initialized weekly model residuals, and first try seasonal or robust uncertainty calibration. With 209 weekly training points, I would not make GARCH a priority.
Q14. Which presentation claims must change?
These are the corrections I would make before another presentation.
Current statement or interpretation	Recommended correction
“Weather drives PM2.5.”	“Weather anomalies have robust short-horizon predictive associations with PM2.5.”
“Significant at every lag from 1 to 7 days.”	“The joint Granger tests remain significant when the maximum lag order varies from 1 to 7.”
“p below \(10^{-9}\)” for all wind/humidity tests	State the exact test and p-value; some are substantially larger, though still significant
“A windier day is followed by 24% lower PM2.5” from shock bins	Describe the displayed same-day shock association, not an unverified next-day effect
“Both ADF and KPSS prove stationarity.”	They provide evidence consistent with stationarity under their tested assumptions
“2020 is excluded.”	Specify that it is excluded from VAR and the forecasting test, but included in certain full-sample EDA results
“95% confidence interval” for future observations	Use 95% prediction interval
“AQI category from weekly mean PM2.5”	Use “PM2.5-derived risk band” and explain that official AQI is different

Two additional Q&A improvements would make the presentation more defensible.

First, explain why the simple baseline is so strong: the estimated seasonal component accounts for much of the variation, so there may be limited additional information available for predicting a year ahead.

Second, distinguish predictive significance, predictive accuracy and causal interpretation. These are three separate questions, and being able to explain that distinction will strengthen your defence considerably.
Q15. What should we do with only two weeks remaining?
My answer is to prioritise a small number of rigorous, completed experiments rather than a large collection of partially implemented models. The detailed plan appears in Section V below.

The seven workstreams are: correct statistical claims, repair the forecast code, implement sound validation, introduce strong seasonal competitors, calibrate uncertainty, produce a valid monthly outlook, and complete targeted VAR robustness checks plus reproducibility work.
Q16. What matters more than anything else we have discussed?
The definition and date of the forecast itself.

Your project data stop in July 2020. Your reported forecasting experiment predicts 2019 using information through 2018.

That is a perfectly valid historical forecasting experiment, but it is not a current 12-month outlook in November 2026.

You must choose and clearly state one of two deliverables:

Option A — Historical forecasting study: evaluate forecasts for 2017–2019 and produce a clearly dated retrospective 12-month forecast exercise. This can be academically rigorous without requiring current data.

Option B — Operational planning outlook: extend the dataset through a recent date, use a consistent monitoring methodology, and construct a genuinely forward-looking forecast from that date.

I favour Option A if the course is mainly assessing time-series theory and the deadline is close. Option B is appropriate only if the assignment explicitly requires a contemporary advisory.

A second fundamental issue is the 52-week horizon itself. Weather can be strongly informative over several days and yet contribute little predictive skill a year ahead. This is not a contradiction; it is an important time-scale-dependent result that could become one of the project's strongest conclusions.

V. Prioritised two-week plan
The following is the sequence I would recommend for the team. Each workstream has a tangible output, so it is clear when the task is finished.
01

Days 1–2: Fix confirmed statistical and code problems

Correct the Ljung–Box initialization issue, rerun residual checks at lags 10, 26 and 52, and ensure AIC comparisons use consistent likelihood conventions. Repair the seasonal calendar indexing and clearly identify which analyses include 2020.

Deliverable: fully executed Phase 4 notebook with trustworthy diagnostic tables



02

Days 2–4: Establish a defensible evaluation design

Implement expanding-window origins for 2017, 2018 and 2019. Refit models using only historical information, and produce horizon-specific and season-specific error metrics. Record model selection separately from evaluation.

Deliverable: common backtest function and model-comparison table



03

Days 4–6: Build the two most informative alternative models

Implement Fourier + ARMA, with \(K=1\) to \(5\), and a climatology + AR(1) anomaly model. Compare against the existing SARIMA and a simpler \(D=0\) candidate. Keep seasonal naive and climatology as baselines.

Deliverable: reproducible comparison of at least five meaningful approaches



04

Days 7–8: Diagnose bias and calibrate prediction intervals

Investigate the eight lower-bound misses in 2019. Compare bias and dispersion by season, construct simulated predictive intervals and validate their calibration on historical forecasts.

Deliverable: forecast-interval chart and coverage/width comparison



05

Days 9–10: Build the monthly advisory correctly

Aggregate weekly predictive paths into monthly mean PM2.5 distributions. Include the estimated mean or median, prediction interval and clearly labelled PM2.5 threshold-exceedance probabilities. Do not claim to forecast complete official AQI.

Deliverable: 12-row monthly outlook table with methodology note



06

Days 10–12: Add targeted causal and short-horizon robustness

Add temperature to the Granger analysis, test a monsoon–humidity interaction, and complete a genuinely operational lagged-weather one-week forecast comparison. If easy, add generalised IRFs.

Deliverable: one concise robustness table and one revised interpretation paragraph



07

Days 13–14: Consolidate and prepare for evaluation

Execute every notebook from a clean environment, commit the code and results, stop tracking cache files, update the README and slides, verify numerical claims, and prepare short answers to likely examiner questions.

Deliverable: reproducible final repository, report and presentation



Suggested final comparison table
Use one table with this structure in the report, populated only after the new experiments have been run.
Model	2017 MAE	2018 MAE	2019 MAE	95% coverage
Seasonal naive	—	—	30.3	—
Climatology	—	—	27.8	—
Climatology + AR(1)	—	—	—	—
Fourier + ARMA	—	—	—	—
SARIMA \(D=0\)	—	—	—	—
SARIMA \(D=1\)	—	—	27.5	84.6%

The dashes are deliberately unfilled; the uploaded project does not contain these additional results. Interval coverage is not available for the baselines in the supplied tables.What I would leave out
I would not spend substantial time tuning an LSTM, implementing Prophet, experimenting with many neural architectures or building a complex GARCH model. Those might add model names to the report, but they are unlikely to provide as much insight as a properly evaluated Fourier model or a well-calibrated interval.

If the assignment explicitly requires Linear Regression and LSTM baselines, implement them in a clearly limited way, explain the constraints, and do not let them displace the principal analysis.
VI. My proposed final storyline
Your strongest defensible project narrative is:
From short-term meteorological predictability to long-term seasonal forecasting
1. Delhi's PM2.5 exhibits a strong annual seasonal pattern.
2. Wind and humidity anomalies contain significant short-horizon predictive information, although the relationships are observational and their interpretation depends on modelling assumptions.
3. For annual forecasts, future weather is not directly observed, and historical calendar patterns form a strong baseline.
4. SARIMA provides one useful model, but its apparent improvement must be tested against simpler alternatives using fair historical evaluations.
5. The final product is a probabilistic PM2.5 outlook that reports uncertainty rather than pretending to predict individual pollution episodes precisely.

That storyline is academically stronger than trying to prove that SARIMA, or any other sophisticated model, must outperform a simple seasonal benchmark.

My final recommendation: Make Fourier + ARMA the main new modelling experiment, use rolling-origin validation to decide whether it genuinely adds value, and make scientifically correct prediction intervals and monthly risk reporting the centrepiece of the final milestone. The most impressive outcome would not necessarily be the lowest MAE; it would be a convincing demonstration that the model choice, uncertainty and interpretation are justified by the evidence.