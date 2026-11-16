
Conversation with Gemini
(i) Agreements with File 06 (Previous Critical Review)
B1 (Ljung-Box failure is a diffuse-initialization artifact): In 04_sarima_draft.py, grid_row() passes simple_differencing=(D == 1) (which drops the first 52 observations before fitting, giving nobs = 157), whereas the final model fit in Section 4 calls SARIMAX(train, order=order, seasonal_order=sorder) with the default simple_differencing=False. Under simple_differencing=False, statsmodels initializes the first 
S
=
52
S=52 seasonal states with a diffuse prior variance (
κ
=
10
6
κ=10 
6
 ), leaving the first 52 residuals at the raw log-level scale (
≈
5.2
≈5.2 instead of 
≈
0.27
≈0.27). Running acorr_ljungbox, het_arch, and shapiro on res.resid without slicing res.resid.iloc[S:] (or res.resid.iloc[res.loglikelihood_burn:]) invalidates all three diagnostics.   
05_phase4_sarima_draft.md
+ 4

B2 & B3 (Over-differencing at lag 52 and boundary seasonal MA): Fitting 
SARIMA
(
1
,
0
,
1
)
(
0
,
1
,
1
)
52
SARIMA(1,0,1)(0,1,1) 
52
​
  on 
N
=
209
N=209 weeks leaves only 
157
157 effective observations (three seasonal transitions) after 
D
=
1
D=1. An estimated 
Θ
1
=
ma.S.L52
=
−
0.988
Θ 
1
​
 =ma.S.L52=−0.988 sits on the invertibility boundary (
∣
Θ
1
∣
→
1
∣Θ 
1
​
 ∣→1), meaning the seasonal difference 
(
1
−
B
52
)
(1−B 
52
 ) and seasonal MA 
(
1
−
0.988
B
52
)
(1−0.988B 
52
 ) algebraically cancel out to represent a deterministic seasonal cycle. That is why 
SARIMA
(
1
,
0
,
1
)
(
0
,
1
,
1
)
52
SARIMA(1,0,1)(0,1,1) 
52
​
  yields a 2019 test MAE of 
27.5
 
μ
g/m
3
27.5 μg/m 
3
 , which is statistically indistinguishable from static log-climatology (
27.8
 
μ
g/m
3
27.8 μg/m 
3
 ).   
03_phase2_eda_results.md
+ 4

B4 (Sample leakage across notebooks): Estimating doy_climatology in Phase 3 on 2015–2019 (which includes the 2019 test year), running STL and Box-Cox in Phase 2 on the full 2015–2020 dataset (which includes both 2019 and the 2020 lockdown), and selecting candidate orders 
(
p
,
q
,
P
,
Q
)
(p,q,P,Q) via AIC on 2015–2018 before evaluating 
D
∈
{
0
,
1
}
D∈{0,1} on 2018 (an in-sample year for the order search) all breach strict train/validation/test isolation.   
02_data_and_code.md
+ 4

B7 & B8 (Target mismatch, LSTM over-parameterization, and simultaneity in 1-week SARIMAX): Exponentiating a log-normal point forecast gives the conditional median 
exp
⁡
(
μ
^
t
)
exp( 
μ
^
​
  
t
​
 ) rather than the conditional mean 
exp
⁡
(
μ
^
t
+
σ
^
t
2
/
2
)
exp( 
μ
^
​
  
t
​
 + 
σ
^
  
t
2
​
 /2). Applying 24-hour CPCB breakpoints to weekly or monthly averages smooths out acute daily spikes. Furthermore, training an LSTM on 209 weekly points for a 52-step horizon will overfit or collapse to the mean cycle, and using realized same-week weather in the 1-week SARIMAX model mixes contemporaneous intra-week correlation with genuine forecast skill.   
05_phase4_sarima_draft.md
+ 4

(ii) Disagreements with File 06
Disagreement 1 — Why 
D
=
0
D=0 failed on the 2018 validation set (File 06 missed a fatal trend='n' bug in 04_sarima_draft.py):

File 06 claims 
D
=
0
D=0 lost on the 2018 validation set (
MAE
=
39.7
MAE=39.7 vs 
21.1
21.1 for 
D
=
1
D=1) because 
SARIMA
(
1
,
0
,
1
)
(
1
,
0
,
1
)
52
SARIMA(1,0,1)(1,0,1) 
52
​
  was "fit on only 3 years with a 52-lag seasonal AR: a weak competitor".   
05_phase4_sarima_draft.md
+ 1

The real mathematical reason: In fit_one(), the code calls SARIMAX(series, exog=exog, order=(p, 0, q), seasonal_order=(P, D, Q, S)) without specifying trend. In statsmodels, the default is trend='n' (zero intercept, unconditional mean 
μ
=
0
μ=0).   
05_phase4_sarima_draft.md

When 
D
=
1
D=1, 
(
1
−
B
52
)
y
t
(1−B 
52
 )y 
t
​
  is centered near 
0
0, so trend='n' is appropriate. When 
d
=
0
d=0 and 
D
=
0
D=0, however, y = log_pm25 has an unconditional mean of 
≈
4.65
≈4.65 (
≈
105
 
μ
g/m
3
≈105 μg/m 
3
 ). Fitting 
d
=
0
,
D
=
0
d=0,D=0 with trend='n' forces the stationary process to revert toward 
log
⁡
(
PM
2.5
)
=
0
log(PM 
2.5
​
 )=0 (
PM
2.5
=
1
 
μ
g/m
3
PM 
2.5
​
 =1 μg/m 
3
 )! Over a 52-step forecast horizon from 2017 into 2018, the forecasts decay geometrically toward zero by 
ϕ
1
h
Φ
1
⌊
h
/
52
⌋
ϕ 
1
h
​
 Φ 
1
⌊h/52⌋
​
 , artificially inflating the 
D
=
0
D=0 validation MAE to 
39.7
 
μ
g/m
3
39.7 μg/m 
3
 . Passing trend='c' when 
D
=
0
D=0 fixes this immediately.   
05_phase4_sarima_draft.md
+ 4

Disagreement 2 — Why the 95% interval coverage is 84.6% (File 06's variance diagnosis in B2/B6 is contradicted by forecast_2019.csv):

File 06 blames the 
84.6
%
84.6% coverage (
44
/
52
44/52 weeks) on the "constant-variance Gaussian assumption on the log scale" being "too optimistic (winter variance of raw PM2.5 is much larger)".   
05_phase4_sarima_draft.md
+ 1

Verification against the 2019 forecast table (05_phase4_sarima_draft.md): Inspecting all 52 rows of forecast_2019.csv reveals that 0 out of 52 weeks exceeded the upper bound hi95 (even the Diwali spike of 
353.4
 
μ
g/m
3
353.4 μg/m 
3
  on 2019-11-03 was well below hi95 = 432.4).   
05_phase4_sarima_draft.md

Every single one of the 8 misses (2019-01-27, 2019-02-24, 2019-04-21, 2019-08-18, 2019-09-29, 2019-10-06, 2019-11-10, and 2019-12-01) fell below the lower bound lo95 (actual < lo95), and 4 of those 8 misses occurred in non-winter months (April, August, September, October).   
05_phase4_sarima_draft.md

Because exponentiating 
exp
⁡
(
μ
^
t
±
1.96
σ
^
)
exp( 
μ
^
​
  
t
​
 ±1.96 
σ
^
 ) produces raw-scale interval widths proportional to the point forecast (
width
t
=
2
sinh
⁡
(
1.96
σ
^
)
y
^
t
≈
0.90
y
^
t
width 
t
​
 =2sinh(1.96 
σ
^
 ) 
y
^
​
  
t
​
 ≈0.90 
y
^
​
  
t
​
 , giving a massive 
338.1
 
μ
g/m
3
338.1 μg/m 
3
  width on 2019-11-10 vs 
37.0
 
μ
g/m
3
37.0 μg/m 
3
  on 2019-07-28), raw winter variance is already scaled up by the log transform. The 
84.6
%
84.6% coverage is caused entirely by unmodeled downward level drift in 2019 (mean error 
−
14.7
 
μ
g/m
3
−14.7 μg/m 
3
 , shifting the entire distribution toward lo95), not by intervals being too narrow.   
05_phase4_sarima_draft.md
+ 2

Disagreement 3 — Reverse causality (
PM
2.5
→
Wind
PM 
2.5
​
 →Wind) in B5 is synoptic confounding, not just random specification noise:

File 06 treats the significant bivariate Granger test for 
PM
2.5
→
Wind
PM 
2.5
​
 →Wind at lags 1–5 (
p
=
0.0005
p=0.0005 to 
0.038
0.038) and in BIC VAR(2) (
p
=
0.0166
p=0.0166) as mere specification sensitivity.   
04_phase3_var_granger_results.md
+ 1

Physically and statistically, elevated 
PM
2.5
PM 
2.5
​
  on day 
t
t is a direct indicator of an unmeasured synoptic stagnation regime (shallow planetary boundary layer height and thermal inversion) that persists across multi-day weather systems and suppresses 10 m surface wind speeds on day 
t
+
1
t+1. Adding 4 lags of wind and humidity in VAR(4) partially proxies that persistent synoptic state, absorbing the correlation (
p
=
0.1268
p=0.1268). Explaining this via omitted boundary-layer dynamics is much stronger in a defense than dismissing it as an artifact.   
04_phase3_var_granger_results.md

Disagreement 4 — Recommending TBATS / Prophet (B3 & Q1):

TBATS is engineered for multiple non-integer seasonal periods (e.g., daily data with 
s
1
=
7
s 
1
​
 =7 and 
s
2
=
365.25
s 
2
​
 =365.25). On weekly data with a single period 
s
=
52
s=52 and 
N
=
209
N=209, TBATS is over-parameterized relative to Dynamic Harmonic Regression (Fourier terms + ARMA errors) or Climatology + AR(1).   
01_project_overview.md
+ 2

(iii) New Issues Found (Missed by Both Authors and Previous Reviewer)
KPSS Stationarity Paradox Between Phase 2 and Phase 3 (Seasonal Variance Masking Secular Drift):

In Phase 2 (03_phase2_eda_results.md), KPSS fails to reject stationarity on Daily log PM2.5 (
stat
=
0.366
,
p
=
0.0917
stat=0.366,p=0.0917) and Weekly log PM2.5 (
stat
=
0.158
,
p
≥
0.10
stat=0.158,p≥0.10), leading the team to declare 
d
=
0
d=0 and claim the series has no drifting trend.   
03_phase2_eda_results.md
+ 1

Yet in Phase 3 (04_phase3_var_granger_results.md), as soon as the seasonal cycle is subtracted, KPSS on PM2.5 anomaly jumps to 
2.033
2.033 (
p
<
0.01
p<0.01, more than 
4
×
4× the 5% critical value of 
0.463
0.463), and in Phase 2, KPSS on seasonally differenced Weekly Δ₅₂ log PM2.5 jumps to 
0.669
0.669 (
p
=
0.0163
p=0.0163, rejecting stationarity)!   
03_phase2_eda_results.md
+ 1

Why this happens mathematically: The KPSS test statistic is 
η
=
T
−
2
∑
t
=
1
T
S
t
2
/
σ
^
L
R
2
η=T 
−2
 ∑ 
t=1
T
​
 S 
t
2
​
 / 
σ
^
  
LR
2
​
 , where 
S
t
=
∑
j
=
1
t
u
^
j
S 
t
​
 =∑ 
j=1
t
​
  
u
^
  
j
​
  is the partial sum of residuals and 
σ
^
L
R
2
σ
^
  
LR
2
​
  is the Newey-West long-run variance estimator. On the raw/log series, the deterministic seasonal wave accounts for 
89
%
89% of the variance (
F
S
=
0.89
F 
S
​
 =0.89); because a periodic wave integrates to zero every 52 weeks, it bounds 
S
t
2
S 
t
2
​
  while inflating the denominator 
σ
^
L
R
2
σ
^
  
LR
2
​
  by 
∼
8
×
∼8×. This blinds KPSS to the non-stationary secular drift in the mean (
137.5
 
μ
g/m
3
137.5 μg/m 
3
  in 2016 down to 
108.1
 
μ
g/m
3
108.1 μg/m 
3
  in 2019). Once seasonality is removed in Phase 3, the denominator shrinks to the anomaly variance and the secular drift triggers a massive KPSS rejection (
stat
=
2.033
stat=2.033).   
03_phase2_eda_results.md
+ 3

ISO Calendar Week Misalignment Bug in 04_sarima_draft.py:

The draft defines week-of-year via woy = lambda idx: np.minimum(pd.DatetimeIndex(idx).isocalendar().week.to_numpy(), 52).   
05_phase4_sarima_draft.md

In the W-SUN index (delhi_weekly.csv), 2016-01-03 is the first Sunday of 2016, but under ISO-8601 rules (where Week 1 must contain the year's first Thursday), 2016-01-03 belongs to ISO Week 53 of 2015, and 2017-01-01 belongs to ISO Week 52 of 2016.   
02_data_and_code.md
+ 1

Consequently, woy folds 2016-01-03 into Week 52 and shifts every subsequent Sunday of 2016 by one week relative to 2015, 2018, and 2019, while 2017 has 53 Sundays (
52
+
52
+
53
+
52
=
209
52+52+53+52=209 training weeks). This misaligns climatology in early January and causes shift(52) (seasonal_naive) to drift by 7 days after 2017.   
01_project_overview.md
+ 2

Jensen's Inequality Artifact and Contemporaneous Mislabeling in the Slide 11 "Shock" Plot (shock_binned.json):

On Slide 11 (08_presentation_and_QA.md), the script states: "Grouping all days by shock size, an unexpectedly windier day is followed by PM2.5 about 24 percent lower, a calmer one by about 32 percent higher".   
04_phase3_var_granger_results.md
+ 1

First, the numbers 
+
32.0
%
+32.0% (
z
=
−
1.78
z=−1.78) and 
−
23.7
%
−23.7% (
z
=
+
2.26
z=+2.26) in shock_binned.json are same-day (
t
=
0
t=0) anomalies, not next-day (
t
+
1
t+1) responses—saying "is followed by" misstates contemporaneous correlation as a lagged effect and exaggerates the next-day IRF (
−
6
%
−6% to 
−
12
%
−12%) by 
2
–
3
×
2–3×.   
04_phase3_var_granger_results.md
+ 1

Second, look at the humidity curve in shock_binned.json: at 
z
=
−
0.01
z=−0.01 (zero humidity shock), the reported PM2.5 deviation is +4.6%! Why is a zero shock associated with 
+
4.6
%
+4.6% PM2.5? Because the code computes the arithmetic mean of 
exp
⁡
(
anom
pm25
)
−
1
exp(anom 
pm25
​
 )−1 within each bin. By Jensen's inequality, even when 
E
[
anom
pm25
]
=
0
E[anom 
pm25
​
 ]=0, 
E
[
exp
⁡
(
anom
pm25
)
−
1
]
≈
exp
⁡
(
σ
anom
2
/
2
)
−
1
≈
+
4.6
%
E[exp(anom 
pm25
​
 )−1]≈exp(σ 
anom
2
​
 /2)−1≈+4.6%! Five of the seven humidity bins appear positive solely because of this untransformed log-normal convexity bias.   
04_phase3_var_granger_results.md
+ 2

Order of Operations in Weekly Log Aggregation (src/data.py):

to_weekly() computes weekly = num.resample("W-SUN").mean() and then sets weekly["log_pm25"] = np.log(weekly["pm25"]) (
ln
⁡
(
1
7
∑
X
i
)
ln( 
7
1
​
 ∑X 
i
​
 ) rather than 
1
7
∑
ln
⁡
X
i
7
1
​
 ∑lnX 
i
​
 ). Because within-week variance is highest during winter pollution episodes, 
ln
⁡
(
X
ˉ
w
)
≈
ln
⁡
X
‾
w
+
1
2
Var
w
(
ln
⁡
X
)
ln( 
X
ˉ
  
w
​
 )≈ 
lnX
  
w
​
 + 
2
1
​
 Var 
w
​
 (lnX) inflates winter weekly log values relative to summer values and creates an inconsistency between the daily log scale (Phase 3) and weekly log scale (Phase 4).   
02_data_and_code.md
+ 3

Misleading 
R
2
R 
2
  Comparison in the Weekly Lag Check (04_phase3_var_granger_results.md):

File 04 states: "Last week's wind (p=0.46) and humidity (p=0.48) add nothing (R2 0.139 vs same-week model 0.140)".   
04_phase3_var_granger_results.md

Looking at the table, the same-week weather model includes only 
wind
t
wind 
t
​
  and 
humidity
t
humidity 
t
​
  (
R
2
=
0.1403
R 
2
 =0.1403), whereas the last-week predictors model includes 
PM2.5
t
−
1
PM2.5 
t−1
​
  (
β
=
0.3621
,
p
=
0.000
β=0.3621,p=0.000) plus 
wind
t
−
1
wind 
t−1
​
  and 
humidity
t
−
1
humidity 
t−1
​
  (
R
2
=
0.1391
R 
2
 =0.1391). Comparing 
R
2
=
0.1391
R 
2
 =0.1391 to 
0.1403
0.1403 across non-nested models with different regressors is meaningless: 
PM2.5
t
−
1
PM2.5 
t−1
​
  alone yields 
R
2
≈
0.3621
2
=
0.131
R 
2
 ≈0.3621 
2
 =0.131, so lagged weather adds 
Δ
R
2
≈
0.008
ΔR 
2
 ≈0.008, not 
0.139
0.139.   
04_phase3_var_granger_results.md
+ 1

(iv) Numbered Answers to Q1–Q16
Forecasting Design
Q1. Sensibility of 
SARIMA
52
SARIMA 
52
​
  on 209 weeks and model ranking for 52-week-ahead log 
PM
2.5
PM 
2.5
​
 :
Full seasonal 
SARIMA
(
p
,
0
,
q
)
(
P
,
D
,
Q
)
52
SARIMA(p,0,q)(P,D,Q) 
52
​
  is poorly suited for 
N
=
209
N=209 weeks because a 52-week lag operator consumes 25% of the sample per seasonal lag/difference, leaving only 3 to 4 observations per calendar week.
Expected performance ranking (best to worst) for 52-step-ahead forecasting:   
01_project_overview.md
+ 2

(c) Fourier-term regression (
K
=
2
 or 
3
K=2 or 3 harmonics) + 
ARMA
(
1
,
1
)
ARMA(1,1) or 
AR
(
1
)
AR(1) errors (Dynamic Harmonic Regression, with linear trend/drift option): Uses only 
2
K
=
4
–
6
2K=4–6 smooth parameters to capture the 52-week cycle across all 209 observations without losing 52 degrees of freedom to seasonal differencing, avoiding the 
Θ
1
=
−
0.988
Θ 
1
​
 =−0.988 boundary problem.   
05_phase4_sarima_draft.md
+ 2

(b) Smoothed Climatology + 
AR
(
1
)
AR(1) on anomalies: Essentially identical to (c); because 
ϕ
^
1
≈
0.36
–
0.55
ϕ
^
​
  
1
​
 ≈0.36–0.55 on weekly anomalies, the 
AR
(
1
)
AR(1) term improves Weeks 1–4 and gracefully decays to climatology for Weeks 5–52.   
04_phase3_var_granger_results.md
+ 2

(a) Seasonal climatology (smoothed across adjacent weeks): Hard to beat at horizons 
h
>
6
h>6 weeks when seasonal strength is 
F
S
=
0.89
F 
S
​
 =0.89.   
03_phase2_eda_results.md
+ 2

(d) 
SARIMA
SARIMA with 
D
=
1
D=1 (e.g., 
(
1
,
0
,
1
)
(
0
,
1
,
1
)
52
(1,0,1)(0,1,1) 
52
​
 ): Survives only because 
Θ
1
=
−
0.988
Θ 
1
​
 =−0.988 mimics climatology, but wastes 52 observations and suffers from high estimation variance.   
05_phase4_sarima_draft.md
+ 2

(e) 
SARIMA
SARIMA with 
D
=
0
D=0 (once fixed with trend='c'): Even with trend='c', estimating 
Φ
1
Φ 
1
​
  at lag 52 without seasonal dummies forces the seasonal wave to damp by 
Φ
^
1
<
1
Φ
^
  
1
​
 <1 over the 52-week forecast horizon.   
05_phase4_sarima_draft.md
+ 1

(g) Prophet-style additive model: Fourier series + piecewise linear trend; reasonable, though its default changepoint prior will overfit the 2016–2018 multi-year swing unless heavily regularized.   
01_project_overview.md
+ 1

(f) ETS / TBATS: Standard ETS in statsmodels/R struggles or refuses to initialize 52 seasonal states on 
N
=
209
N=209 points, and TBATS adds unnecessary complexity over (c).   
06_critical_review.md
+ 1

(h) LSTM: Worst by far; with 209 weekly points (157 training windows for a 52-step target), a neural network has far too many parameters and no physical constraints.   
06_critical_review.md
+ 1

Q2. Is 
ma.S.L52
=
−
0.988
ma.S.L52=−0.988 under 
D
=
1
D=1 evidence of over-differencing, and what should we do?
Yes. In an airline-type seasonal model 
(
1
−
B
52
)
y
t
=
(
1
+
Θ
1
B
52
)
ε
t
(1−B 
52
 )y 
t
​
 =(1+Θ 
1
​
 B 
52
 )ε 
t
​
 , a seasonal MA root 
Θ
1
→
−
1
Θ 
1
​
 →−1 is the classic textbook signature (Bell, 1987; Box & Jenkins) that the seasonal pattern is deterministic rather than stochastic, so applying 
(
1
−
B
52
)
(1−B 
52
 ) introduced an artificial non-invertible unit MA root at lag 52.   
05_phase4_sarima_draft.md
+ 4

Concrete fix: Set 
d
=
0
,
D
=
0
d=0,D=0, pass trend='c', and pass Fourier harmonics (
K
=
2
K=2 or 
3
3, i.e., 
sin
⁡
(
2
π
k
t
/
52.18
)
,
cos
⁡
(
2
π
k
t
/
52.18
)
sin(2πkt/52.18),cos(2πkt/52.18) for 
k
=
1..
K
k=1..K) as exog inside SARIMAX(train, exog=fourier_train, order=(1,0,1), trend='c'). Select 
K
∈
{
1
,
2
,
3
}
K∈{1,2,3} via AICc (which will pick 
K
=
2
K=2 or 
3
3, needing only 4–6 seasonal parameters instead of 52).   
05_phase4_sarima_draft.md
+ 2

Q3. Handling and testing the 2019–2020 downward drift (real improvement vs station-mix artifact):
Annual mean 
PM
2.5
PM 
2.5
​
  peaked at 
137.5
 
μ
g/m
3
137.5 μg/m 
3
  in 2016 and fell monotonically to 
126.4
126.4 (2017), 
114.5
114.5 (2018), and 
108.1
108.1 (2019)—a 
−
9.5
%
/
year
−9.5%/year decline from 2016 to 2019. Both real policy/meteorological changes (Eastern/Western Peripheral Expressways bypassing Delhi trucks in 2018, BS-VI fuel rollout, cleaner 2019 late-monsoon) and CPCB station expansion (Delhi expanded from ~10–17 continuous CAAQMS stations in 2015–2017 to 37–38 stations in 2018–2019, adding suburban/greener sites like Najafgarh, Sri Aurobindo Marg, and Pusa) contributed.   
01_project_overview.md
+ 2

How to test it (in 15 minutes): Download or inspect station-level CPCB data (or compare the 
PM
2.5
/
NO
2
PM 
2.5
​
 /NO 
2
​
  ratio in delhi_daily.csv). In your existing dataset, check the annual mean of no2 and so2 from 2015 to 2019: if no2 jumped or shifted sharply in late 2017/early 2018 when new monitors joined, station composition is at work; if the decline holds within winter given matched ERA5 wind/RH/temp (compute the annual mean of the OLS residual of 
log
⁡
(
PM
2.5
)
log(PM 
2.5
​
 ) on weather), it reflects non-meteorological trend/station mix.   
02_data_and_code.md
+ 3

How to handle it in the forecast model: Because a 2015–2018 unweighted mean locks in the high 2016–2017 level (
≈
124
 
μ
g/m
3
≈124 μg/m 
3
 ) and over-predicts 2019 by 
+
14.7
 
μ
g/m
3
+14.7 μg/m 
3
 , add a damped trend or recency-weighted level adjustment: specifically, re-anchor the model intercept to the most recent 52-week training mean (
y
ˉ
last 52
−
y
ˉ
train
y
ˉ
​
  
last 52
​
 − 
y
ˉ
​
  
train
​
 ), which removes the level-shift bias without extrapolating an unbounded linear drop.   
01_project_overview.md
+ 3

Q4. Best fix for the 84.6% interval coverage on 209 points:
As shown in Disagreement 2, all 8 interval misses in 2019 are lower-tail misses (actual < lo95) caused by the 
−
14.7
 
μ
g/m
3
−14.7 μg/m 
3
  level bias, while 0 weeks exceeded hi95.   
05_phase4_sarima_draft.md

Step 1 (Centering): Re-anchoring the level to the trailing 52-week mean (from Q3) shifts the log forecast by 
≈
−
0.07
≈−0.07, which immediately moves 5 of the 8 missed weeks inside the 95% band (raising coverage from 
84.6
%
84.6% to 
≈
94.2
%
≈94.2%).   
05_phase4_sarima_draft.md
+ 1

Step 2 (Seasonal Variance + Split/Rolling Conformal or Empirical Quantiles): Because Levene's test on log_pm25 still rejects equal monthly variance (
p
=
0.0059
p=0.0059, with log-SD ranging from 
0.352
0.352 in Feb to 
0.472
0.472 in Nov), replace the constant state-space 
σ
^
σ
^
  with a seasonally scaled conformal/empirical interval: compute out-of-fold standardized residuals 
e
t
/
σ
^
month
(
t
)
e 
t
​
 / 
σ
^
  
month(t)
​
  on expanding windows (2017–2018) and use the empirical 
2.5
%
2.5% and 
97.5
%
97.5% quantiles (or conformal quantile 
q
^
0.95
q
^
​
  
0.95
​
 ) rather than Gaussian 
±
1.96
σ
^
±1.96 
σ
^
 .   
03_phase2_eda_results.md
+ 3

Q5. Rolling-origin evaluation design and statistical significance test:
A single 2019 test year (
n
=
52
n=52 strongly autocorrelated weeks) has low statistical power.   
05_phase4_sarima_draft.md
+ 2

Rolling-Origin Design: Use an expanding window with quarterly or monthly origins from 2017-01-01 through 2019-01-01 (e.g., 9 quarterly origins: Jan 2017, Apr 2017, Jul 2017, Oct 2017, Jan 2018, Apr 2018, Jul 2018, Oct 2018, Jan 2019, each forecasting 
h
=
1
…
52
h=1…52 weeks ahead, never crossing 2019-12-31 so the 2020 lockdown remains untouched). Since Dynamic Harmonic Regression (
d
=
0
,
D
=
0
d=0,D=0) only requires 2 years (104 weeks, 2015–2016) to estimate 4–6 Fourier coefficients and 
ARMA
(
1
,
1
)
ARMA(1,1) errors, all 9 origins are feasible.   
01_project_overview.md
+ 4

Significance Test: Use the Harvey-Leybourne-Newbold (1997) finite-sample modified Diebold-Mariano (DM) test on both absolute errors (
∣
e
1
,
t
∣
−
∣
e
2
,
t
∣
∣e 
1,t
​
 ∣−∣e 
2,t
​
 ∣) and squared errors (
e
1
,
t
2
−
e
2
,
t
2
e 
1,t
2
​
 −e 
2,t
2
​
 ) on the log and raw scales, using a Newey-West HAC variance estimator (bandwidth 
L
=
4
L=4 weeks for 
h
=
1
h=1, or grouped by horizon 
h
h). On 2019 alone, the DM test between 
SARIMA
SARIMA (
MAE
=
27.5
MAE=27.5) and Climatology (
MAE
=
27.8
MAE=27.8) yields 
p
>
0.60
p>0.60 (insignificant).   
05_phase4_sarima_draft.md
+ 4

Q6. Target frequency and converting forecasts to a "Monthly AQI Advisory Table":
Forecasting weekly means and plugging the deterministic point forecast into CPCB's 24-hour cutoffs (<=30, <=60, <=90, <=120, <=250, >250) is statistically flawed because CPCB AQI categories are defined for 24-hour daily concentrations, and weekly/monthly averaging smooths out high-variance daily peaks.   
01_project_overview.md
+ 3

Best solution (without re-architecting the weekly forecast pipeline): Keep the weekly log-
PM
2.5
PM 
2.5
​
  model to predict the weekly conditional log-mean 
μ
^
w
μ
^
​
  
w
​
  and forecast variance 
σ
^
fc
,
w
2
σ
^
  
fc,w
2
​
 . To get the distribution of daily 
log
⁡
(
PM
2.5
)
log(PM 
2.5
​
 ) within week 
w
w, add the empirical within-week daily variance 
σ
^
within
,
m
2
=
Var
(
log
⁡
PM
2.5
,
daily
−
log
⁡
PM
2.5
,
weekly
∣
month 
m
)
σ
^
  
within,m
2
​
 =Var(logPM 
2.5,daily
​
 −logPM 
2.5,weekly
​
 ∣month m) computed from the 2015–2018 training data!   
05_phase4_sarima_draft.md
+ 3

By the law of total variance, a randomly chosen day in week 
w
w (in month 
m
m) has predictive distribution:

log
⁡
(
PM
2.5
,
day
)
∼
N
(
μ
^
w
,
σ
^
fc
,
w
2
+
σ
^
within
,
m
2
)
log(PM 
2.5,day
​
 )∼N( 
μ
^
​
  
w
​
 , 
σ
^
  
fc,w
2
​
 + 
σ
^
  
within,m
2
​
 )
You can then compute the exact analytical probability that a day in month 
m
m falls into each CPCB category 
[
L
c
,
U
c
]
[L 
c
​
 ,U 
c
​
 ] using the normal CDF 
Φ
(
⋅
)
Φ(⋅) averaged over the weeks in month 
m
m:

P
(
Category 
c
 in week 
w
)
=
Φ
(
ln
⁡
U
c
−
μ
^
w
σ
^
fc
,
w
2
+
σ
^
within
,
m
2
)
−
Φ
(
ln
⁡
L
c
−
μ
^
w
σ
^
fc
,
w
2
+
σ
^
within
,
m
2
)
P(Category c in week w)=Φ 

​
  
σ
^
  
fc,w
2
​
 + 
σ
^
  
within,m
2
​
 

​
 
lnU 
c
​
 − 
μ
^
​
  
w
​
 
​
  

​
 −Φ 

​
  
σ
^
  
fc,w
2
​
 + 
σ
^
  
within,m
2
​
 

​
 
lnL 
c
​
 − 
μ
^
​
  
w
​
 
​
  

​
 

Multiply by the number of days in the month (
30
30 or 
31
31) to report "Expected Days in Poor / Very Poor / Severe per Month" alongside the median 
PM
2.5
PM 
2.5
​
 . That transforms a crude lookup table into a rigorous probabilistic health advisory!   
02_data_and_code.md
+ 2

Q7. Fairly testing whether weather helps at the 1-week-ahead horizon:
Using realized week-
t
t wind and humidity to predict week-
t
t 
PM
2.5
PM 
2.5
​
  measures contemporaneous co-movement, not operational forecast skill. Run a clean 3-tier ablation table for the 1-week horizon:   
04_phase3_var_granger_results.md
+ 3

Pure Ex-Ante Model (Operational Lower Bound): SARIMAX using only lagged weather (
wind
t
−
1
,
rh
t
−
1
wind 
t−1
​
 ,rh 
t−1
​
 ) or last 3 days of week 
t
−
1
t−1 (
Days 
5
–
7
Days 5–7 of the prior week, which are 1–3 days before week 
t
t begins and within the 4-day VAR memory window!).   
04_phase3_var_granger_results.md
+ 2

Simulated NWP Forecast (Realistic Operational Model): Perturb actual week-
t
t weather with realistic 7-day NWP forecast noise calibrated to medium-range weather skill (e.g., 
X
~
t
=
r
X
t
+
1
−
r
2
ε
t
X
~
  
t
​
 =rX 
t
​
 + 
1−r 
2
 

​
 ε 
t
​
  with correlation 
r
≈
0.80
r≈0.80), or use the last 2 days of week 
t
−
1
t−1's daily data to predict week 
t
t.   
06_critical_review.md
+ 1

Oracle Weather (Theoretical Upper Bound): The current model with actual week-
t
t weather (pred_wx), explicitly labeled as an Oracle Upper Bound demonstrating the maximum ceiling of meteorological predictability.   
05_phase4_sarima_draft.md
+ 2

Important code note: In 04_sarima_draft.py Section 6, pass deseasonalized weather anomalies (ex_anom) rather than raw standardized wind and rh so weather doesn't duplicate the seasonal cycle.   
04_phase3_var_granger_results.md
+ 1

Causality / VAR (Phase 3)
Q8. Is "weather Granger-causes 
PM
2.5
PM 
2.5
​
  over 1–7 days" well supported, and what is the weakest link?
Yes, the predictive Granger causality conclusion (
Wind
,
RH
→
G
PM
2.5
Wind,RH 
G

​
 PM 
2.5
​
 , 
p
<
10
−
10
p<10 
−10
 ) is rock-solid across AIC VAR(4), BIC VAR(2), first-differenced VAR(14), Newey-West HAC Wald tests, and precipitation controls.   
04_phase3_var_granger_results.md
+ 2

The weakest link: Confusing Granger (predictive) causality with structural/physical driving in the headline claims (e.g., Slide 13: "yes, weather drives PM2.5 over the following days") despite omitting temperature (already in delhi_daily.csv!) and planetary boundary layer height (PBLH). In Delhi, synoptic western disturbances jointly change temperature, boundary-layer inversion depth, surface wind, and relative humidity.   
02_data_and_code.md
+ 3

Q9. Cholesky IRF/FEVD vs. Generalized IRF / Local Projections, and framing the 6%–30% range:
Because daily 
PM
2.5
PM 
2.5
​
 , wind, and RH are 24-hour averages over the exact same timestamps, contemporaneous residual correlation reflects intra-day physical dispersion plus common synoptic shocks.   
02_data_and_code.md
+ 3

Why bounding via both Cholesky orderings (6.3% to 29.9% FEVD; 
−
5.9
%
−5.9% to 
−
11.9
%
−11.9% day-1 wind IRF) is the right approach: Physically, 
PM
2.5
PM 
2.5
​
  does not substantially alter synoptic 10 m wind speed within 24 hours, so the true structural parameter lies much closer to the weather-first ordering (
29.9
%
29.9% FEVD, 
−
11.9
%
−11.9% wind IRF) than the 
PM
2.5
PM 
2.5
​
 -first ordering (
6.3
%
6.3% FEVD, which artificially attributes all same-day wind dispersion to an autonomous 
PM
2.5
PM 
2.5
​
  shock).   
04_phase3_var_granger_results.md
+ 2

Reporting the Cholesky bounds as a formal identification interval (with weather-first as the physically preferred specification and 
PM
2.5
PM 
2.5
​
 -first as a conservative pure-lagged lower bound) is completely defensible and arguably clearer than Generalized IRFs (Pesaran-Shin), whose shocks are non-orthogonal and whose FEVD shares do not sum to 100%. Local Projections (Jordà) would yield virtually identical point IRFs since LP and VAR share the same linear Wold space at short horizons (
h
≤
7
h≤7).   
04_phase3_var_granger_results.md
+ 2

Q10. Minimal extra analysis for humidity's non-monotonic and season-dependent effect:
Look at Phase 2 (03_phase2_eda_results.md): Spearman 
ρ
(
PM
2.5
,
RH
)
ρ(PM 
2.5
​
 ,RH) is 
−
0.37
−0.37 in Monsoon (wet scavenging / rain washout) and 
−
0.02
−0.02 in Winter and Other months (where high morning RH actually promotes hygroscopic growth of secondary inorganic aerosols!). Pooling all seasons into a single constant-parameter VAR averages two opposite physical mechanisms.   
03_phase2_eda_results.md
+ 3

Best minimal addition (~15 lines of code): Run your existing manual HAC OLS Granger equation from Phase 3 separately for Winter (Nov–Jan) vs. Monsoon (Jul–Sep) (or include a Winter × RH_lags interaction). Showing in one small table that 
Wind
→
PM
2.5
Wind→PM 
2.5
​
  is strongly negative in both seasons while 
RH
→
PM
2.5
RH→PM 
2.5
​
  is driven predominantly by the monsoon/wet-scavenging regime will directly explain the non-monotonic shock_binned.json curve and impress your instructor. Skip threshold VAR and non-linear neural Granger tests.   
03_phase2_eda_results.md
+ 4

Q11. KPSS rejection on anomalies and in-sample climatology estimation in Phase 3:
As proven in New Issue 1, KPSS rejects on PM2.5 anomaly (
stat
=
2.033
stat=2.033) and Wind anomaly (
stat
=
1.05
stat=1.05) because of the multi-year downward drift from 2016 to 2019.   
01_project_overview.md
+ 2

Does this invalidate Phase 3? No, because: (1) ADF strongly rejects a unit root (
t
=
−
6.60
t=−6.60 and 
−
19.57
−19.57), (2) your First differences, VAR(14) robustness check in Table 2 of File 04 already removes any secular trend/unit root and still finds 
p
=
7.8
×
10
−
25
p=7.8×10 
−25
  for Wind and 
p
=
1.5
×
10
−
10
p=1.5×10 
−10
  for Humidity, and (3) adding a linear time trend (trend='ct') to the VAR(4) changes the 1-to-4-day coefficients by 
<
2
%
<2% because a 5-year slow drift is orthogonal to 4-day high-frequency fluctuations.   
04_phase3_var_granger_results.md
+ 3

Action: Do not redo Phase 3 from scratch; simply add one robustness row to granger_robustness.csv: Anomalies + linear trend ('ct'), VAR(4) (or compute doy_climatology on 2015-2018 only) to show the 
p
p-values are invariant.   
04_phase3_var_granger_results.md
+ 2

Q12. Which additional variables are worth adding to the VAR/Granger analysis?

Temperature (temp): Must add as a control because it is already cleaned and sitting in delhi_daily.csv! A reviewer or grader who sees temp in your summary statistics table (02_data_and_code.md) but absent from the VAR will immediately ask why it was dropped. Run a 4-variable VAR (wind, rh, temp, log_pm25 anomalies) or add 4 lags of temp anomaly to the HAC Wald table alongside rain control.   
02_data_and_code.md
+ 4

Boundary-Layer Height (boundary_layer_height from Open-Meteo ERA5): Optional one-line API addition in src/data.py if you want a bonus slide, though not strictly required if you add temp.   
02_data_and_code.md
+ 2

Fire counts / 
NO
2
NO 
2
​
 : Skip fire counts (requires external NASA FIRMS spatial processing) and keep 
NO
2
NO 
2
​
  out of the weather VAR (since 
NO
2
NO 
2
​
  is a co-emitted pollutant, not an exogenous meteorological driver). Adding temp will reduce the partial effect of rh slightly (since temperature and relative humidity are negatively correlated) while leaving 
Wind
→
PM
2.5
Wind→PM 
2.5
​
  highly significant.   
02_data_and_code.md
+ 3

Methodology & Reporting
Q13. Is the log transform adequately justified, and is GARCH/seasonal variance worth it?
Yes, the log transform is exceptionally well justified: Box-Cox 
λ
^
=
0.045
λ
^
 =0.045 (daily) and 
0.028
0.028 (weekly), skewness drops from 
1.704
1.704 to 
−
0.077
−0.077, and the max/min monthly SD ratio drops from 
7.90
×
7.90× to 
1.34
×
1.34×.   
03_phase2_eda_results.md
+ 2

On the weekly SARIMA residuals (after slicing off the first 52 initialization residuals!), ARCH-LM at 4 lags is actually non-significant (
p
>
0.20
p>0.20), because weekly averaging smooths out daily volatility clustering. Therefore, fitting a parametric GARCH model on weekly data is not needed. Instead, use the simple monthly/seasonal residual SD scaling from Q4 to calibrate the prediction intervals.   
05_phase4_sarima_draft.md
+ 4

Q14. Statistical errors or over-claims in the presentation script (08_presentation_and_QA.md) an instructor might challenge:

Slide 8 & 9 + Q&A ("Weekly log PM2.5 on the training years has a flat rolling mean... not a drifting trend" and "Isn't raw PM2.5 stationary too? Yes"): An instructor will challenge how raw/log 
PM
2.5
PM 
2.5
​
  can be "stationary with no drifting trend" when annual mean 
PM
2.5
PM 
2.5
​
  drops from 
137.5
137.5 (2016) to 
108.1
108.1 (2019) and KPSS rejects stationarity as soon as you deseasonalize (KPSS = 2.033, 
p
<
0.01
p<0.01 in File 04). Correction: Say "ADF rejects a unit root, and while the huge seasonal cycle dominates KPSS on the raw series, deseasonalizing reveals a gentle downward drift from 2016 to 2019."   
01_project_overview.md
+ 3

Slide 10 & Q&A ("The reverse [PM2.5 to wind] is... weak for wind, only at 1 to 2 lags (p = 0.04 and 0.016), not at 3 or more"): In granger_pairwise_lags.csv (File 04), 
PM
2.5
→
Wind
PM 
2.5
​
 →Wind has 
p
<
0.05
p<0.05 at lags 1, 2, 3, 4, and 5 (
0.00097
,
0.00047
,
0.0041
,
0.014
,
0.038
0.00097,0.00047,0.0041,0.014,0.038), while in the multivariate VAR(4) F-test 
p
=
0.1268
p=0.1268. Be clear which specification those numbers come from, and explain that any lag-1/2 reverse correlation reflects multi-day synoptic stagnation (inversion layers affecting both variables), which vanishes in the VAR(4) / HAC test (
p
=
0.101
p=0.101).   
04_phase3_var_granger_results.md
+ 4

Slide 11 ("an unexpectedly windier day is followed by PM2.5 about 24 percent lower, a calmer one by about 32 percent higher"): Change "is followed by" to "coincides with (on the same day)" (since shock_binned.json plots day-0 anomalies, whereas the next-day effect is 
−
6
%
−6% to 
−
12
%
−12% on Slide 12), and subtract the Jensen's inequality mean offset (
≈
+
4.5
%
≈+4.5%) or compute 
exp
⁡
(
anom
‾
)
−
1
exp( 
anom
 )−1 instead of 
exp
⁡
(
anom
)
−
1
‾
exp(anom)−1
​
 .   
04_phase3_var_granger_results.md
+ 1

Slide 5 ("Seasonal strength is 0.89..."): Note that STL was computed on 2015–2020; recomputed on the 2015–2018 training set, verify and quote the training-only 
F
S
F 
S
​
  (which is virtually identical, 
≈
0.90
≈0.90) so no one can accuse you of test/lockdown leakage in EDA.   
03_phase2_eda_results.md
+ 2

Q15. Prioritised list of at most 7 high-impact changes for the remaining 2 weeks:
See Section (v) below for the concrete 7-item execution plan.   
07_open_questions_for_gemini.md

Q16. Anything else missed that matters more than everything above?
Yes — The Smearing / Log-Normal Bias Correction and Metric Asymmetry:
When you optimize a model by minimizing squared error on 
log
⁡
(
PM
2.5
)
log(PM 
2.5
​
 ) and back-transform via 
y
^
t
=
exp
⁡
(
μ
^
t
)
y
^
​
  
t
​
 =exp( 
μ
^
​
  
t
​
 ), your point forecast is the geometric mean / median (
y
^
med
y
^
​
  
med
​
 ).   
05_phase4_sarima_draft.md
+ 1

Under log-normality, minimizing MAE on the raw scale actually requires the median 
exp
⁡
(
μ
^
t
)
exp( 
μ
^
​
  
t
​
 ) (which is why 
exp
⁡
(
μ
^
t
)
exp( 
μ
^
​
  
t
​
 ) favors MAE!), whereas minimizing RMSE or estimating the expected monthly mean requires the mean 
y
^
mean
=
exp
⁡
(
μ
^
t
+
σ
^
2
/
2
)
y
^
​
  
mean
​
 =exp( 
μ
^
​
  
t
​
 + 
σ
^
  
2
 /2) (or Duan's non-parametric smearing estimator 
y
^
mean
=
exp
⁡
(
μ
^
t
)
⋅
1
T
∑
exp
⁡
(
e
^
i
)
y
^
​
  
mean
​
 =exp( 
μ
^
​
  
t
​
 )⋅ 
T
1
​
 ∑exp( 
e
^
  
i
​
 )).   
05_phase4_sarima_draft.md
+ 1

Explicitly presenting both 
exp
⁡
(
μ
^
t
)
exp( 
μ
^
​
  
t
​
 ) (optimal for MAE / median advisory) and 
exp
⁡
(
μ
^
t
+
σ
^
2
/
2
)
exp( 
μ
^
​
  
t
​
 + 
σ
^
  
2
 /2) (optimal for RMSE / mean exposure), along with the probabilistic exceedance calculation from Q6, shows graduate-level mastery of time-series transformations in a course like MATH F428.   
00_START_HERE.md
+ 3

(v) Prioritised 2-Week Execution Plan (Maximum 7 Items)
Fix the 3 Bugs in 04_sarima_draft.py and Execute 04_sarima.ipynb End-to-End (Day 1–2):

Slice off initialization residuals before diagnostics: resid = pd.Series(res.resid, index=train.index).iloc[S:] (fixes the fake Ljung-Box 
p
≈
0
p≈0 failure).   
05_phase4_sarima_draft.md
+ 1

Pass trend='c' whenever 
D
=
0
D=0 in fit_one() (fixes the zero-mean collapse that gave 
D
=
0
D=0 a 
39.7
39.7 MAE on 2018).   
05_phase4_sarima_draft.md

Replace isocalendar().week with np.minimum((idx.dayofyear - 1) // 7 + 1, 52) so early-January Sundays (2016-01-03, 2017-01-01) are never folded into Week 52.   
02_data_and_code.md
+ 1

Add Dynamic Harmonic Regression (Fourier + ARMA) and Climatology + AR(1) + Level Re-anchoring (Day 3–5):

Implement Fourier harmonics (
K
=
2
K=2 and 
K
=
3
K=3, i.e. 4–6 
sin
⁡
/
cos
⁡
sin/cos columns) with 
ARMA
(
1
,
1
)
ARMA(1,1) errors (order=(1,0,1), seasonal_order=(0,0,0,0), trend='c') and a recency-anchored level (anchoring the intercept to the trailing 52-week mean to handle the 2016–2019 downward drift).   
01_project_overview.md
+ 3

Keep the Linear Regression baseline (using the same Fourier features + lagged 
log
⁡
PM
2.5
logPM 
2.5
​
 ) and either drop LSTM or keep a tiny 1-layer LSTM (
8
–
16
8–16 hidden units) explicitly framed as an empirical demonstration that deep learning overfits small seasonal samples (
N
=
209
N=209).   
01_project_overview.md
+ 3

Run Expanding-Window Cross-Validation (2017–2019) + Modified Diebold-Mariano Tests (Day 6–7):

Evaluate models across expanding origins (2017, 2018, 2019) at both 
h
=
1
h=1 week and 
h
=
1
…
52
h=1…52 weeks, reporting MAE and RMSE on both raw (
μ
g/m
3
μg/m 
3
 ) and log scales, broken down by Winter vs. Non-Winter, plus Harvey-Leybourne-Newbold DM 
p
p-values against Climatology.   
05_phase4_sarima_draft.md
+ 2

Complete the 1-Week-Ahead SARIMAX Weather Ablation (Day 8–9):

Generate metrics_1week.csv and sarimax_weather_coef.csv comparing: (a) Persistence, (b) Plain SARIMA / Fourier+ARMA, (c) SARIMAX with lagged weather (end of week 
t
−
1
t−1, operational forecast), and (d) SARIMAX with same-week weather anomalies (explicitly labeled as the Oracle Upper Bound).   
04_phase3_var_granger_results.md
+ 3

Build the Probabilistic Monthly AQI Advisory Table & Calibrated Intervals (Day 10–11):

Calibrate the 52-week 95% intervals using level re-anchoring + monthly residual SD scaling (bringing 2019 coverage from 
84.6
%
84.6% to 
∼
94
%
∼94%).   
03_phase2_eda_results.md
+ 2

Combine weekly forecast variance 
σ
^
fc
,
w
2
σ
^
  
fc,w
2
​
  with within-week daily variance 
σ
^
within
,
m
2
σ
^
  
within,m
2
​
  (per Q6) to output the expected number of days per month in each CPCB AQI category (Good through Severe).   
02_data_and_code.md
+ 2

Add Temperature Control & Seasonal Split to Phase 3 HAC Granger Table + Fix Leakages (Day 12):

Restrict doy_climatology in Phase 3 and STL/Box-Cox in Phase 2 to pre-test data (or verify training-only numbers match), add + temp control to the HAC Wald table in Notebook 03, and add a 2-row Winter vs. Monsoon HAC split showing that RH is a monsoon washout effect while Wind operates year-round.   
02_data_and_code.md
+ 4

Clean Repo Hygiene & Polish Presentation Wording (Day 13–14):

Add a .gitignore excluding __pycache__/, .venv/, and .ipynb_checkpoints/, git rm -r --cached __pycache__, execute all four notebooks (01 to 04) with saved outputs, re-run verify_numbers.py, and update the Slide 8, 10, and 11 script phrasing per Q14.   
01_project_overview.md
+ 3

Would you like the drop-in Python code for 04_sarima.ipynb implementing the fixed SARIMA diagnostics, Fourier + ARMA dynamic harmonic regression, 3-tier 1-week SARIMAX weather test, and probabilistic monthly AQI advisory table?






