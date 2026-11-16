# 08 Report and deck LaTeX source

## report/report.tex
```latex
% Project report, MATH F428. Build: cd report && tectonic report.tex  (numbers and figures come from ../slides/beamer after make_figures.py)
\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.3cm]{geometry}
\usepackage{graphicx,booktabs,amsmath,amssymb,hyperref,float,caption,xcolor}
\hypersetup{colorlinks=true,urlcolor=blue!60!black,linkcolor=blue!60!black}
\graphicspath{{../slides/beamer/fig/}{../figures/}}
\newcommand{\pmtwo}{PM$_{2.5}$}
\newcommand{\ugm}{$\mu$g/m$^3$}
\newcommand{\ugmm}{\ensuremath{\mu\mathrm{g/m^3}}}
\input{../slides/beamer/tables/numbers.tex}
\setlength{\parskip}{4pt}\setlength{\parindent}{0pt}
\renewcommand{\arraystretch}{1.1}
\title{Forecasting Delhi's \pmtwo{}: Seasonality, Weather Predictability and a Rolling-Origin Forecasting Study}
\author{Kushagra Singh \and Yatin JM \and Aryan Choudhary\\ BITS Pilani, Goa \,--\, MATH F428 Time Series Analysis}
\date{November 2026}
\begin{document}
\maketitle
\begin{abstract}
We study daily \pmtwo{} in Delhi from January 2015 to July 2020 (CPCB monitors; ERA5 wind and humidity). \pmtwo{} has a very strong annual cycle (winter \ratioWM$\times$ the monsoon) and a slow downward drift. After removing the cycle, wind and humidity anomalies \emph{predict} \pmtwo{} for about a week (Granger causality in a VAR, robust to lag order, differencing, HAC errors and rain/temperature controls), but their information is gone at the weekly scale: last week's weather adds nothing for this week, and even the same week's weather, unknown in advance, improves a one-week forecast by only \fcOneOracle\%. For 52-week forecasts we compare climatology, Fourier-term regression with ARMA errors, SARIMA, linear regression and a small LSTM on three expanding-window origins. A smooth Fourier+ARMA model matches or slightly beats climatology; SARIMA with seasonal differencing is fragile, and the LSTM is clearly worse. We fix several diagnostic and design errors found in an earlier draft (residual burn-in, missing constant, leakage), calibrate prediction intervals out of sample, and produce a monthly 2020 outlook that correctly flags the lockdown as a \fcLockPct\% fall below the no-lockdown forecast.
\end{abstract}

\section{Introduction}
Delhi's air is Poor or worse (PM$_{2.5}>90$ \ugm{}) on \pctPoor\% of days in our sample, and the pattern repeats every winter. We ask two questions: \textbf{Q1} (explain) does weather predict \pmtwo{}, and over what horizon? \textbf{Q2} (forecast) how well can \pmtwo{} be forecast one week and 52 weeks ahead, and which model should be trusted? The project was reviewed independently three times; every concrete claim of those reviews was re-tested on the data, and the verdicts are in \texttt{docs/REVIEW\_RESPONSES.md} (summarised in Section~\ref{sec:review}). Because the data end in July 2020, the deliverable is a \emph{historical forecasting study} (backtests for 2017--2019 and an outlook for 2020 made in December 2019), not a current health advisory.

\section{Data and cleaning}
\pmtwo{} (and NO$_2$, SO$_2$) are the CPCB city-level daily values for Delhi from the Kaggle dataset \texttt{rohanrao/air-quality-data-in-india}: 2{,}009 days, 1 Jan 2015 to 1 Jul 2020, with 2 missing \pmtwo{} values (interpolated; gaps $\le3$ days are interpolated, longer ones are left missing). Wind speed, relative humidity, temperature and precipitation are ERA5 reanalysis values for central Delhi (28.61$^\circ$N, 77.21$^\circ$E) from the Open-Meteo archive. Forecasting uses weekly means (weeks ending Sunday, 287 weeks). Modelling is on $\log$ \pmtwo{}; a back-transformed forecast $\exp(\mu)$ is a \emph{median}, and mean forecasts use $\exp(\mu_h+\sigma_h^2/2)$ with the horizon-specific $\sigma_h$. The 2020 lockdown never enters model selection.

\section{Exploratory analysis}
\subsection{Seasonality and the log transform}
Winter (Nov--Jan) averages \winterMean{} \ugm{} against \monsoonMean{} in the monsoon (\ratioWM$\times$). An STL decomposition of the weekly log series gives a seasonal strength $F_S=\Fs$ on the training years (0.89 on the full sample). The spread of daily \pmtwo{} grows with its level (monthly mean and SD correlate at 0.95; the largest monthly SD is \sdRatioRaw$\times$ the smallest); after the log it varies only \sdRatioLog$\times$ and the skewness falls from \skewRaw{} to \skewLog{}. The Box-Cox $\lambda$ is \boxcox{} (about 0.10 on the training years), i.e. close to the log. Some volatility clustering remains in the daily series (ARCH-LM \archRaw{} $\to$ \archLog{}); we check it again on the weekly forecast residuals, where it is absent (ARCH-LM(4) $p=0.87$).
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{stl.pdf}\caption{STL decomposition of weekly log \pmtwo{}.}\end{figure}

\subsection{Stationarity and the hidden drift}
ADF and KPSS (opposite null hypotheses) on 2015--2018 weekly log \pmtwo{} are both consistent with stationarity, as is the seasonal difference; a further first difference over-differences (lag-1 autocorrelation $-0.46$). So $d=0$. But KPSS on the \emph{raw level} is dominated by the large seasonal cycle. Removing a day-of-year climatology reveals a slow decline: the KPSS statistic of the anomaly is 0.90 on 2015--18 and 2.0 on 2015--19 (5\% critical value 0.46), and the mean log anomaly falls from $+0.10$ in 2016 to $-0.19$ in 2019. The level is therefore \emph{not} constant, which drives the model design in Section~\ref{sec:fc}.

\subsection{Is the decline real? A station-level check}
The city series is the mean over reporting stations (correlation 0.995 with the station-level mean), and the number of stations reporting \pmtwo{} rose from 10 and 8 (2015, 2016) to 37 (2018, 2019), so a change in the station mix could create a spurious decline. A fixed panel of six long-running stations (at least 60 days in each year) falls by \declPanel\% between 2016 and 2019, all stations by \declAll\%, and the city series after regressing out wind, humidity and temperature by \declWx\%. We conclude that most of the decline is real, while stressing that the panel is small and thin in 2017.
\begin{figure}[H]\centering\includegraphics[width=0.85\linewidth]{fc_station.pdf}\caption{Left: stations reporting; right: mean log anomaly by year for all stations, the fixed panel and the weather-adjusted city series.}\end{figure}

\section{Does weather predict \pmtwo{}? (Q1)}
Wind, humidity and log \pmtwo{} are deseasonalised with a smoothed day-of-year climatology (31-day circular window; leap years handled by mapping 29 Feb to day 59) and fitted in a VAR(4) (lag by AIC; BIC picks 2; stable, largest root modulus 0.81; portmanteau $p=0.17$).
\paragraph{Granger causality.} Joint tests that lags 1--$k$ of wind or humidity add nothing to the \pmtwo{} equation are rejected at every $k=1,\dots,7$ ($p<10^{-9}$). With HAC (Newey-West) errors the 4-lag tests give $p\approx6\times10^{-20}$ (wind) and $4\times10^{-11}$ (humidity); adding rain and temperature controls gives $9\times10^{-18}$ and $7\times10^{-8}$; adding a linear time trend or using a climatology fitted on 2015--2018 only changes nothing. Season-specific tests show both variables are significant in winter and in the monsoon ($p\le5\times10^{-4}$); the interactions are weak (monsoon $\times$ humidity $p=0.20$, winter $\times$ wind $p=0.03$), so the EDA impression that humidity matters only in the monsoon is a correlation pattern, not a difference in predictive content. The reverse direction is absent for humidity and weak for wind (lag orders 1 and 2 only, $p=0.04$ and $0.02$). We call this a \emph{predictive association}: mixing height, stubble burning and fireworks are unmeasured, and the ERA5 data are one grid cell.
\begin{figure}[H]\centering\includegraphics[width=0.9\linewidth]{granger_hac.pdf}\caption{HAC Wald tests (4 lags).}\end{figure}
\paragraph{Size and timing.} A one-SD wind shock (2.5 km/h) lowers \pmtwo{} by \irfWindA--\irfWindB\% the next day, a one-SD humidity shock (5.4\% RH) by \irfRhA--\irfRhB\%, fading within about a week; the range reflects the Cholesky ordering (weather first allows same-day effects). The generalised IRF, which does not depend on ordering, gives $-12.0\%$ and $-5.2\%$ on day 1, inside or at the edge of those ranges. Weather shocks explain \fevdA--\fevdB\% of the 14-day forecast-error variance of \pmtwo{} depending on the ordering.
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{irf_range.pdf}\caption{Impulse responses of \pmtwo{} to wind and humidity shocks under both orderings.}\end{figure}
\paragraph{Horizon.} At the weekly scale, last week's wind and humidity add nothing to last week's \pmtwo{} for predicting this week's ($\Delta R^2=0.005$, joint HAC Wald $p=0.51$). Weather is therefore a short-memory predictor, and the 52-week models use no weather.

\section{Forecasting (Q2)}\label{sec:fc}
\subsection{Models and evaluation design}
All models forecast weekly log \pmtwo{} with no weather inputs: seasonal naive; \textbf{climatology} (mean of each calendar week, benchmark); climatology + AR(1); \textbf{Fourier + ARMA} (dynamic harmonic regression: $K\le5$ yearly sine/cosine pairs, ARMA$(p,q)$ errors with $p\le2,q\le1$, and a level that is constant, linear or a random walk); SARIMA$(1,0,1)(0,1,1)_{52}$ and SARIMA$(1,0,1)(1,0,0)_{52}$ with a constant; Linear Regression on Fourier terms and a linear trend; and a small LSTM (16 units, recursive, seeded). For the Fourier model, $K$ and $(p,q)$ are chosen by AICc within each level type, and the level type by validation on the last training year; this procedure was declared the headline before any test year was inspected. Evaluation uses three expanding-window origins (end of 2016, 2017, 2018), each forecasting the next 52 weeks, refitting and reselecting every time. The 2017 fold (two training years) is a stress test; 2018 and 2019 are the main evidence. Paired error differences to climatology are summarised with a moving-block bootstrap (8-week blocks); a plain Diebold--Mariano test on 52 weeks of one forecast path is not valid and is not used here.
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{fc_backtest.pdf}\caption{Left: the 2019 forecast of the selected model against climatology and the actual values. Right: MAE by forecast year.}\end{figure}
\subsection{Backtest results}
\begin{table}[H]\centering\footnotesize\input{../slides/beamer/tables/fc_backtest.tex}\caption{52-week-ahead MAE (\ugm{}) by forecast year; last column: bootstrap verdict against climatology over 2018 and 2019.}\end{table}
In 2019 the selected Fourier+ARMA model has an MAE of \fcMaeSelNineteen{} against \fcMaeClimNineteen{} for climatology and \fcMaeSarimaNineteen{} for the seasonal-differenced SARIMA; the SARIMA is, however, at \fcMaeSarimaSeventeen{} in the 2017 fold, where it has only two seasons to learn from. Over 2018--2019 only the seasonal naive forecast, SARIMA with $D=0$ (\fcMaeSarimaZeroNineteen{} in 2019) and the LSTM (\fcMaeLstmNineteen{}) are clearly worse than climatology. The linear-trend Fourier variant is better on 2018--19 (the bootstrap interval excludes 0) but not over all three origins, and it was not the pre-declared choice, so we do not claim it. The honest summary: a year ahead the calendar carries almost all of the predictable signal, and with three origins the remaining models cannot be ranked.

\subsection{Diagnostics: errors in the earlier draft}
The draft's Ljung--Box test had $p\approx0$ at every lag. This was an artifact: a state-space SARIMA with $D=1$ initialises its first 52 seasonal states diffusely, so the first 52 in-sample residuals equal the level of the series (about 5 on the log scale). With them excluded (\texttt{loglikelihood\_burn}) the residuals are acceptable at lags 10 and 26 ($p=0.49,\,0.10$) but not at lag 52 ($p=0.016$). The seasonal MA coefficient is \fcMaCoef{} with a standard error far above 1: the parameter sits on the invertibility boundary and is not identified, the usual sign that the seasonal difference is unnecessary. The $D=0$ candidate in the draft had no constant, forcing the forecast toward $\log \text{PM}_{2.5}=0$; with a constant its validation MAE falls from 39.7 to 30.6 (but it remains the worst non-LSTM model overall). The selected Fourier+ARMA model still shows autocorrelation at lags 26 and 52 in the 2019 fold ($p=0.001$ and $0.009$) and ARCH-LM(4) is clean ($p=0.87$): there is more seasonal structure than a few harmonics capture, which we list as a limit.

\subsection{Prediction intervals}
Model-based 95\% intervals covered \fcCovRaw\% of the 2019 weeks; all misses were below the lower bound because 2019 was cleaner than 2015--18, so the problem is level bias as much as width. We rescale the predictive standard deviation by season (winter vs other months, shrunk toward the pooled value) using only the 2017 and 2018 errors, and re-centre only if the bias has the same sign and size $>0.5$ standard deviations in both calibration years; it did not (mean standardised errors $-0.66$ and $-0.45$), so only the scale is changed. On 2019 the calibrated coverage is \fcCovCal\%. The scale factors differ by fold (1.33/1.42 for 2019, 1.09/0.95 for the 2020 forecast), which shows the calibration is itself uncertain.

\subsection{One week ahead: does weather help?}
Each year 2018 and 2019 is forecast one week at a time with parameters fitted on earlier data. \emph{Lagged weather} (last week's wind and humidity anomalies) changes the error by \fcOneLagged\%, the \emph{last three days} of the previous week by \fcOneLastThree\%, and the \emph{same week's} weather (which is observed, not forecast, and so a hindsight upper bound) by \fcOneOracle\% (Harvey--Leybourne--Newbold $p=0.07$). Weather is explanatory over days, but a poor forecasting input.
\begin{figure}[H]\centering\includegraphics[width=0.7\linewidth]{fc_oneweek.pdf}\caption{One-week-ahead MAE, 2018--19.}\end{figure}

\subsection{The 2020 outlook and its validation}
The final model is fitted on 2015--2019 (selection again inside the window: linear level, $K=5$, AR(1) errors), 5{,}000 weekly paths are simulated, calibrated, converted to daily values by adding a within-week log offset resampled from the same calendar month of the training data, and classified into the CPCB \pmtwo{} bands. The same pipeline run for 2019 (data to 2018 only) places all \fcValInside{} monthly means inside the 95\% interval, but over-predicts the share of Poor-or-worse days (\fcValPoorPred\% vs \fcValPoorAct\% actual), which is the level bias again. These bands are \pmtwo{} sub-index bands, not the official AQI (the maximum over all pollutants).
\begin{figure}[H]\centering\includegraphics[width=0.95\linewidth]{fc_outlook.pdf}\caption{2020 outlook: monthly mean \pmtwo{} with 95\% interval and expected days per band.}\end{figure}
\begin{table}[H]\centering\scriptsize\input{../slides/beamer/tables/fc_outlook.tex}\caption{2020 outlook (\ugm{}); ``Days Poor+'' = expected days above 90 \ugm{}; Actual shown for full months only.}\end{table}
\subsection{Case study: the 2020 lockdown}
From 29 March to 31 May 2020 \pmtwo{} was about \fcLockPct\% below the no-lockdown forecast (95\% interval \fcLockLo--\fcLockHi\%). Using a version of the model that is given the actual wind and humidity of those weeks, the gap is \fcLockWxPct\%: most of the drop is not weather. This is descriptive; it depends on the forecast level for 2020 being right, which the interval calibration above shows is uncertain.
\begin{figure}[H]\centering\includegraphics[width=0.85\linewidth]{fc_lockdown.pdf}\caption{Actual weekly \pmtwo{} in 2020 against the no-lockdown forecast and a weather-adjusted forecast.}\end{figure}

\section{Review of the project and what changed}\label{sec:review}
Three independent reviews proposed about 30 changes. We accepted the confirmed errors (diagnostic burn-in, missing constant, leakage in headline statistics, wording that over-stated causality or p-values, the PM$_{2.5}$-band versus AQI distinction, an invalid DM test) and rejected others after testing them (for example, the claim that re-anchoring the level gives 94\% coverage gives 90\% in the data; the shock-bin statistic has no Jensen bias; humidity's effect is not detectably monsoon-specific). The full log, with evidence for each claim, is \texttt{docs/REVIEW\_RESPONSES.md}.

\section{Limitations}
(i) Granger causality is predictive; boundary-layer height, stubble burning and fireworks are unmeasured, and ERA5 is a single grid cell. (ii) Three backtest origins give few independent tests; most model differences are not significant. (iii) A level bias remains: 2019 was cleaner than the training years, and the calibrated intervals depend on the fold. (iv) The Fourier model leaves some autocorrelation at lags 26 and 52. (v) One city; the data end in July 2020 and the monitoring network changed during the sample; the fixed-station check is small. (vi) The bands are \pmtwo{} sub-index bands, not the official AQI. (vii) The LSTM is deliberately small and is not tuned: it is a small-data negative result, not a statement about deep learning in general.

\section{Conclusion}
Delhi's \pmtwo{} is overwhelmingly a calendar phenomenon with a slowly falling level. Wind and humidity anomalies help for about a week, not for a year. For 52-week forecasts a smooth Fourier+ARMA model is as good as or marginally better than climatology and more robust than SARIMA, and its uncertainty can be calibrated; the forecast correctly isolates the 2020 lockdown. The most valuable parts of the work are the honest accounting of what is and is not significant and the correction of diagnostic errors that would have led to wrong model choices.

\section*{Reproducibility}
\texttt{pip install -r requirements.txt}; download the CPCB files (Section~2) and run notebooks 01--04; then \texttt{python slides/beamer/make\_figures.py}, \texttt{python slides/beamer/verify\_numbers.py} (65 independent checks of every number on the slides) and build \texttt{slides/beamer/main.tex} and this report with \texttt{tectonic}. Code: \texttt{src/} (data, tsa, forecast, aqi, plots).
\end{document}
```

## slides/beamer/main.tex
```latex
% Delhi PM2.5: progress presentation, MATH F428.
% Build: python make_figures.py && tectonic main.tex   (numbers in the slides come from tables/numbers.tex)
\documentclass[aspectratio=169,11pt]{beamer}
\usepackage{graphicx}
\usepackage{tikz}
\usetikzlibrary{positioning,arrows.meta,shapes.misc,calc}
\usepackage{booktabs}
\usepackage[most]{tcolorbox}
\usepackage{hyperref}
\hypersetup{colorlinks=true,urlcolor=blue!70!black,linkcolor=blue!70!black}

% ── palette (same blue / orange / aqua as the figures) ─────────────────────────────────────────────────
\definecolor{navy}{HTML}{12284C}
\definecolor{pblue}{HTML}{2A78D6}
\definecolor{porange}{HTML}{EB6834}
\definecolor{paqua}{HTML}{1BAF7A}
\definecolor{pgreen}{HTML}{2E8B57}
\definecolor{lightbg}{HTML}{EEF3FA}
\definecolor{graytxt}{HTML}{5B6573}

\usetheme{default}
\usefonttheme{professionalfonts}
\setbeamertemplate{navigation symbols}{}
\setbeamercolor{normal text}{fg=black}
\setbeamercolor{structure}{fg=pblue}
\setbeamercolor{frametitle}{bg=navy,fg=white}
\setbeamerfont{frametitle}{size=\large,series=\bfseries}
\setbeamersize{text margin left=0.7cm,text margin right=0.7cm}
\setbeamertemplate{itemize item}{\color{pblue}$\blacktriangleright$}
\setbeamertemplate{itemize subitem}{\color{pblue}$\bullet$}
\setlength{\leftmargini}{1.1em}

% slim navy title bar
\setbeamertemplate{frametitle}{%
  \nointerlineskip
  \begin{beamercolorbox}[wd=\paperwidth,ht=0.85cm,dp=0.25cm,leftskip=0.7cm]{frametitle}
    \usebeamerfont{frametitle}\insertframetitle
  \end{beamercolorbox}\vspace{0.05cm}}

% footer: course | topic, small logo, page number
\setbeamertemplate{footline}{%
  \leavevmode\hbox to\paperwidth{%
    \hspace*{0.7cm}\raisebox{0.12cm}{\color{graytxt}\tiny MATH F428 $\cdot$ Delhi PM$_{2.5}$ forecasting $\cdot$ K.\ Singh, Y.\ JM, A.\ Choudhary (BITS Goa)}\hfill
    \raisebox{0.03cm}{\includegraphics[height=0.36cm]{logo.png}}\hspace*{0.25cm}%
    \raisebox{0.12cm}{\color{graytxt}\tiny\insertframenumber\,/\,\inserttotalframenumber}\hspace*{0.7cm}}%
  \vskip0.04cm}

% boxes: definition (light), takeaway (navy)
\newtcolorbox{defbox}[1]{enhanced,colback=lightbg,colframe=pblue,boxrule=0pt,leftrule=2.5pt,arc=1pt,
  left=5pt,right=5pt,top=2pt,bottom=2pt,before skip=3pt,after skip=3pt,fontupper=\footnotesize,
  before upper={\textbf{\textcolor{pblue}{#1}}\;}}
\newtcolorbox{takeaway}{enhanced,colback=navy,colupper=white,boxrule=0pt,arc=2pt,
  left=6pt,right=6pt,top=3pt,bottom=3pt,before skip=3pt,after skip=0pt,fontupper=\small}
\newtcolorbox{card}[2][]{enhanced,colback=white,colframe=#2,coltitle=white,colbacktitle=#2,boxrule=0.6pt,
  arc=2pt,fonttitle=\bfseries\small,fontupper=\small,left=5pt,right=5pt,top=3pt,bottom=3pt,#1}

\tikzset{
  sbox/.style={draw=#1,rounded corners=2pt,line width=0.9pt,fill=white,align=left,inner sep=4pt,text width=5.1cm,minimum height=1.25cm},
  sres/.style={draw=#1,rounded corners=2pt,line width=0.9pt,fill=#1!8,align=left,inner sep=4pt,text width=4.0cm,minimum height=1.25cm},
  gbox/.style={draw=#1,rounded corners=2pt,fill=#1!8,line width=0.8pt,align=center,inner sep=3pt,text width=3.9cm},
  sarr/.style={-{Stealth[length=2.2mm]},line width=0.9pt,color=graytxt}}
\newcommand{\pmtwo}{PM$_{2.5}$}
\newcommand{\ugm}{$\mu$g/m$^3$}
\renewcommand{\arraystretch}{1.1}
\setlength{\parskip}{0pt}\setlength{\parindent}{0pt}
\input{tables/numbers.tex}

\title{Forecasting Delhi's PM$_{2.5}$ Air Pollution}
\author{Kushagra Singh \and Yatin JM \and Aryan Choudhary}
\date{November 2026}

\begin{document}

% ───────────────────────── 1. Title ─────────────────────────
\begin{frame}[plain]
  \begin{tikzpicture}[remember picture,overlay]
    \fill[navy] (current page.south west) rectangle (current page.north east);
    \fill[porange] ([xshift=0.9cm,yshift=-2.15cm]current page.north west) rectangle +(1.4cm,0.09cm);
    \node[anchor=north west,text=white,text width=12cm,inner sep=0] at ([xshift=0.9cm,yshift=-2.4cm]current page.north west)
      {{\fontsize{24}{28}\selectfont\bfseries Forecasting Delhi's PM$_{2.5}$\\[2pt] Air Pollution}\\[8pt]
       {\large Time-series analysis: VAR, Granger causality and seasonal forecasting}\\[14pt]
       {\normalsize Kushagra Singh \;$\cdot$\; Yatin JM \;$\cdot$\; Aryan Choudhary}\\[3pt]
       {\small BITS Pilani, Goa \;$\cdot$\; MATH F428 Project Presentation \;$\cdot$\; November 2026}};
    \node[anchor=south west,text=white!85!navy,text width=10cm,inner sep=0] at ([xshift=0.9cm,yshift=0.8cm]current page.south west)
      {\small Can weather explain Delhi's smog, and can we forecast it a year ahead?};
    \node[anchor=north east,fill=white,circle,inner sep=2pt] at ([xshift=-0.8cm,yshift=-0.8cm]current page.north east)
      {\includegraphics[height=1.5cm]{logo.png}};
  \end{tikzpicture}
\end{frame}

% ───────────────────────── 2. The problem ─────────────────────────
\begin{frame}{The Problem: Delhi's Air Is Unhealthy Most of the Year}
  \centering
  \includegraphics[width=\linewidth]{fig/problem_aqi.pdf}\\[3pt]
  \begin{defbox}{PM$_{2.5}$ and AQI:}
    particles under 2.5 $\mu$m that reach the lungs and blood, in \ugm{} (micrograms per m$^3$). \textbf{AQI} = India's colour-coded Air Quality Index; the bands show its PM$_{2.5}$ categories (Poor starts above 90 \ugm{}). The official AQI takes the worst pollutant; we use the PM$_{2.5}$ band only.
  \end{defbox}
  \begin{takeaway}
    \textbf{\pctPoor\%} of days (2015--2020) were Poor or worse, and the pattern repeats yearly: winter averages \textbf{\winterMean} \ugm{}, the monsoon \textbf{\monsoonMean}: winter is \textbf{\ratioWM$\times$} higher.
  \end{takeaway}
\end{frame}

% ───────────────────────── 3. What we are building ─────────────────────────
\begin{frame}{What We Are Building: Two Questions, Two Time Horizons}
  \centering
  \begin{tikzpicture}[x=1cm,y=1cm,font=\footnotesize]
    \node[draw=navy,fill=navy,text=white,rounded corners=2pt,align=center,text width=2.3cm,minimum height=3.6cm,inner sep=4pt] (data)
      at (1.15,2.0) {\bfseries Data\\[3pt]\footnotesize daily \pmtwo{}, wind, humidity\\ 2015--2020\\[3pt] weekly means for forecasting};
    \node[sbox=pblue] (q1) at (6.0,3.6) {\textbf{Q1. Explain.} Does weather drive \pmtwo{}?\\ Daily VAR + Granger causality};
    \node[sbox=graytxt] (q2a) at (6.0,2.0) {\textbf{Q2a. Next week.} Does weather improve a 1-week forecast?};
    \node[sbox=graytxt] (q2b) at (6.0,0.4) {\textbf{Q2b. Next 12 months.} Fourier+ARMA vs SARIMA and baselines, no weather inputs};
    \node[sres=pgreen] (r1) at (12.3,3.6) {\textbf{Done:} wind and humidity Granger-cause \pmtwo{}; effects fade within about a week};
    \node[sres=pgreen] (r2) at (12.3,2.0) {\textbf{Done:} yesterday's weather adds nothing; same-week weather (unknowable in advance) helps only \fcOneOracle\%};
    \node[sres=pgreen] (r3) at (12.3,0.4) {\textbf{Done:} 52-week forecasts backtested on 2017--19; outlook for 2020};
    \draw[sarr] (data.east) -- ++(0.35,0) |- (q1.west);
    \draw[sarr] (data.east) -- (q2a.west);
    \draw[sarr] (data.east) -- ++(0.35,0) |- (q2b.west);
    \draw[sarr] (q1) -- (r1); \draw[sarr] (q2a) -- (r2); \draw[sarr] (q2b) -- (r3);
  \end{tikzpicture}\\[4pt]
  \begin{takeaway}
    \textbf{Why two horizons?} Q1 shows a weather shock moves \pmtwo{} for only about a week: weather may help a short-term forecast, but it is unknown a year ahead, so the 12-month model will use no weather inputs.
    The final output is a month-by-month PM$_{2.5}$ outlook with prediction intervals.
  \end{takeaway}
\end{frame}

% ───────────────────────── 4. Data ─────────────────────────
\begin{frame}{Data: CPCB Air Quality and ERA5 Weather}
  \footnotesize
  \begin{tabular}{@{}p{3.7cm}p{1.8cm}p{1.1cm}p{6.6cm}@{}}
    \toprule
    \textbf{Variable} & \textbf{Source} & \textbf{Unit} & \textbf{Role in the project} \\
    \midrule
    \pmtwo{} & CPCB & \ugm{} & What we explain and forecast \\
    Wind speed & ERA5 & km/h & Disperses pollution: candidate driver \\
    Relative humidity & ERA5 & \% & Moisture, fog, rain: candidate driver \\
    Other (NO$_2$, SO$_2$, temp., rain) & CPCB, ERA5 & various & Context; rain used as a control \\
    \bottomrule
  \end{tabular}\\[5pt]
  \footnotesize
  \begin{itemize}\setlength\itemsep{2pt}
    \item \textbf{CPCB} (India's pollution board): \href{https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india}{\textbf{Kaggle: Air Quality Data in India}}, Delhi rows.
    \item \textbf{ERA5} = a \emph{reanalysis} (observations blended into a weather model, gap-free): \href{https://open-meteo.com/en/docs/historical-weather-api}{\textbf{Open-Meteo Historical API}}, central Delhi.
    \item \textbf{2{,}009 days}, 1 Jan 2015 -- 1 Jul 2020; 2 \pmtwo{} values interpolated. \textbf{Daily} data for causality, \textbf{weekly means} (287 weeks) for forecasting; validated on three rolling origins.
  \end{itemize}
  \vspace{1pt}
  \centering
  \begin{tikzpicture}[x=2.2cm,font=\scriptsize]
    \fill[pblue] (0,0) rectangle (4,0.55);        \node[text=white] at (2,0.275) {\textbf{Train: 2015--2018} (model fitting and selection)};
    \fill[porange] (4,0) rectangle (5,0.55);      \node[text=white] at (4.5,0.275) {\textbf{Test: 2019}};
    \fill[gray!45] (5,0) rectangle (5.5,0.55);    \node at (5.25,0.275) {2020};
    \foreach \y/\l in {0/2015,1/2016,2/2017,3/2018,4/2019,5/2020} \node[text=graytxt,anchor=north] at (\y,-0.02) {\l};
    \node[text=graytxt,anchor=south,align=center] at (5.25,0.58) {lockdown: case study only};
  \end{tikzpicture}
\end{frame}

% ───────────────────────── 5. Seasonality / STL ─────────────────────────
\begin{frame}{Seasonality: STL Decomposition of Weekly log PM$_{2.5}$}
  \centering
  \includegraphics[width=\linewidth]{fig/stl.pdf}\\[3pt]
  \begin{defbox}{STL.}
    Splits a series into \emph{trend} + \emph{seasonal} (repeats every year) + \emph{residual} (what is left).
    Seasonal strength $F_S=1-\mathrm{Var}(\text{residual})/\mathrm{Var}(\text{seasonal}+\text{residual})$: 0 = no seasonality, 1 = purely seasonal.
  \end{defbox}
  \begin{takeaway}
    $F_S=\mathbf{\Fs}$ (2015--18 weeks): the yearly cycle dominates, so the model must be \textbf{seasonal} (period $s=52$ weeks).
  \end{takeaway}
\end{frame}

% ───────────────────────── 6. Why log ─────────────────────────
\begin{frame}{Why Take Logs? Raw PM$_{2.5}$ Is Spiky and Skewed}
  \centering
  \includegraphics[width=\linewidth]{fig/why_log.pdf}\\[3pt]
  \begin{defbox}{Log transform.}
    PM$_{2.5}$ moves by \emph{percentages}: the spread of daily values (SD) is about \sdNov\ \ugm{} in November but only \sdAug\ in August. On a log scale equal percentage changes are equal distances, so the spread stops depending on the level.
  \end{defbox}
  \begin{takeaway}
    Raw PM$_{2.5}$ has a heavy right tail (skewness \skewRaw); the log is close to a bell curve (skewness \skewLog). The Box-Cox estimate $\lambda\approx\boxcox$ ($\lambda=0$ is the log) agrees.
  \end{takeaway}
\end{frame}

% ───────────────────────── 7. Volatility ─────────────────────────
\begin{frame}{Volatility Tests: Does the Spread Depend on the Level?}
  \centering
  \includegraphics[width=\linewidth]{fig/volatility_sd.pdf}\\[2pt]
  {\scriptsize\input{tables/log_tests.tex}}\\[3pt]
  \begin{takeaway}
    \textbf{Volatility} = how much values swing. In raw units the spread differs \sdRatioRaw$\times$ between months and tracks the level (corr.\ 0.95); after the log it differs only \sdRatioLog$\times$.
    Small differences remain (equal-spread test $p=\levPlog$; ARCH \archRaw\,$\to$\,\archLog, still significant), so we re-check the model residuals.
  \end{takeaway}
\end{frame}

% ───────────────────────── 8. Stationarity (idea) ─────────────────────────
\begin{frame}{Stationarity: Can the Past Predict the Future?}
  \centering
  \includegraphics[width=\linewidth]{fig/stationarity.pdf}\\[3pt]
  \begin{defbox}{Stationary}
    = the mean, spread and autocorrelation do not drift over time, so patterns learned from the past still apply. ARIMA-type models need it; if a series drifts, we \emph{difference} it ($d$ = ordinary difference, $D$ = difference at the seasonal lag).
  \end{defbox}
  \begin{takeaway}
    Weekly log \pmtwo{} (2015--18): the rolling mean is flat and the rolling spread varies only modestly, so the yearly cycle is a repeating pattern. Without the cycle a slow \emph{downward drift} appears (about $-$\declAll\% 2016--19). (The log is for variance, not stationarity.)
  \end{takeaway}
\end{frame}

% ───────────────────────── 8b. ADF / KPSS ─────────────────────────
\begin{frame}{Testing Stationarity with ADF and KPSS, and Choosing $d$ and $D$}
  \centering
  {\footnotesize\input{tables/stationarity.tex}}\par\vspace{5pt}
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \begin{card}[title={ADF test (Augmented Dickey-Fuller)}]{pblue}\footnotesize
      H$_0$: \emph{unit root} (the series wanders, non-stationary).\\ $p<0.05$ rejects H$_0$, which supports stationarity.
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={KPSS test}]{porange}\footnotesize
      H$_0$: the series \emph{is} stationary.\\ $p>0.05$ keeps H$_0$ (the printed 0.10 means ``$\ge0.10$'').
    \end{card}
  \end{columns}
  \vspace{4pt}
  \begin{takeaway}
    \textbf{Both tests are consistent with stationarity} for log \pmtwo{} and its seasonal difference $\Rightarrow$ $d=0$. A further difference over-differences (lag-1 autocorrelation $-0.46$, near the $-0.5$ warning level) and is dropped.
    A seasonal difference $D=1$ is not needed: a $D=1$ SARIMA's seasonal MA coefficient is $\fcMaCoef$ with a standard error above 1, the sign of over-differencing, so we model the cycle with Fourier terms instead.
  \end{takeaway}
\end{frame}

% ───────────────────────── 9. Granger ─────────────────────────
\begin{frame}{Does Weather Predict PM$_{2.5}$? Granger Causality in a VAR}
  \centering
  \begin{tikzpicture}[font=\scriptsize]
    \node[gbox=graytxt] (a) at (2.15,0) {\textbf{Model A:} predict today's \pmtwo{} from\\ past \pmtwo{} only};
    \node[gbox=pblue] (b) at (7.3,0) {\textbf{Model B:} past \pmtwo{} \textbf{+ past wind and humidity}\\(last 4 days)};
    \node[draw=navy,rounded corners=2pt,fill=navy,text=white,align=center,inner sep=3pt,text width=3.5cm] (c) at (12.5,0) {Is B significantly better?\\ \emph{Wald test, robust errors}};
    \draw[sarr] (a) -- (b); \draw[sarr] (b) -- (c);
  \end{tikzpicture}\\[3pt]
  \includegraphics[width=\linewidth]{fig/granger_hac.pdf}\\[2pt]
  \begin{takeaway}
    \textbf{Mainly one way.} Wind and humidity help predict \pmtwo{} in joint tests at every lag order from 1 to 7 days ($p<10^{-9}$; bars: 4 lags), also given rain and temperature. The reverse is absent for humidity and weak for wind (lag orders 1--2 only, $p\approx0.02$--$0.04$). {\footnotesize Predictive, not proof of cause.}
  \end{takeaway}
\end{frame}

% ───────────────────────── 10. Shock ─────────────────────────
\begin{frame}{What Is a ``Shock''? An Unexpected Change in Weather}
  \centering
  \includegraphics[width=\linewidth]{fig/shock_example.pdf}\\[3pt]
  \begin{defbox}{Shock.}
    the part of today's wind (or humidity) the model could \emph{not} predict from the previous 4 days (plus the seasonal level). \textbf{SD} = typical shock size: 1 SD $\approx$ 2.5 km/h (wind), 5.4\% (humidity).
  \end{defbox}
  \begin{takeaway}
    Grouping all days by shock size: after an unexpectedly windier day (+\shockWindBigZ\,SD), \pmtwo{} is \textbf{\shockWindBig\%} lower on day $t+1$ than on day $t-1$; after a calmer one ($-$\shockWindCalmZ\,SD), \textbf{\shockWindCalm\%} higher.
  \end{takeaway}
\end{frame}

% ───────────────────────── 11. IRF ─────────────────────────
\begin{frame}{Impulse Response: How Long Does a Weather Shock Matter?}
  \centering
  \includegraphics[width=\linewidth]{fig/irf_range.pdf}\\[3pt]
  \begin{defbox}{Impulse response.}
    The model's predicted path of \pmtwo{} after a one-SD shock. \textbf{Ordering:} weather first lets a shock move \pmtwo{} on the same day; \pmtwo{} first allows lagged effects only. We show both.
  \end{defbox}
  \begin{takeaway}
    A one-SD wind shock cuts \pmtwo{} by \irfWindA--\irfWindB\% the next day, humidity by \irfRhA--\irfRhB\%; both fade within about a week.
    Weekly: \emph{last} week's weather adds nothing to last week's \pmtwo{} for predicting this week's ($p=\lagWindP$ wind, \lagRhP\ humidity).
  \end{takeaway}
\end{frame}

% ───────────────────────── 13. What we established ─────────────────────────
\begin{frame}{What We Have Established So Far}
  \begin{itemize}\footnotesize\setlength\itemsep{3pt}
    \item \textbf{Seasonality:} a strong yearly cycle ($F_S=\Fs$; winter \ratioWM$\times$ the monsoon), so the forecasting model must be seasonal ($s=52$ weeks).
    \item \textbf{Transformation:} the log stabilises the variance (monthly spread \sdRatioRaw$\times\to$\sdRatioLog$\times$, skewness \skewRaw\ $\to$ \skewLog); log \pmtwo{} is consistent with stationarity ($d=0$), with a slow downward level drift.
    \item \textbf{Causality:} wind and humidity \textbf{Granger-cause} \pmtwo{} (robust to lag choice, differencing, robust errors, rain and temperature controls); the reverse is absent for humidity and weak for wind.
    \item \textbf{Size and timing:} a one-SD shock lowers \pmtwo{} by \irfWindA--\irfWindB\% (wind) and \irfRhA--\irfRhB\% (humidity) the next day, fading within about a week.
    \item \textbf{Horizon:} last week's weather adds nothing for predicting this week's \pmtwo{} ($p\approx0.5$), so weather is a short-memory driver and the 12-month model should not rely on it.
  \end{itemize}
  \vspace{4pt}
  \begin{takeaway}
    Answer to Q1: wind and humidity have a \textbf{robust predictive association} with \pmtwo{} over the following days (predictive, not proof of physical cause).
  \end{takeaway}
\end{frame}

% ───────────────────────── 14. Limits and next phase ─────────────────────────
\begin{frame}{Forecasting: Models and How We Test Them}
  \footnotesize
  \begin{columns}[T,onlytextwidth]
    \column{0.52\linewidth}
    \begin{card}[title={Models (weekly log \pmtwo{}, no weather inputs)}]{pblue}\scriptsize
      \begin{itemize}\setlength\itemsep{1pt}
        \item \textbf{Benchmarks:} seasonal naive; \textbf{climatology} (mean of each calendar week); climatology + AR(1).
        \item \textbf{Fourier + ARMA:} $K\le5$ yearly harmonics + ARMA errors; level = constant, linear or random walk, all chosen \emph{inside} each training window.
        \item \textbf{SARIMA} $D=1$ and $D=0$ (with constant), Linear Regression, a tiny LSTM (16 units).
      \end{itemize}
    \end{card}
    \column{0.45\linewidth}
    \begin{card}[title={Test design}]{porange}\scriptsize
      \begin{itemize}\setlength\itemsep{1pt}
        \item \textbf{Rolling origins:} train to end-2016, 2017, 2018; forecast the next 52 weeks each time; refit and re-select every time.
        \item Main evidence: 2018 and 2019; 2017 (2 training years) is a stress test.
        \item Compare to climatology with a block-bootstrap of paired errors; say ``indistinguishable'' when the interval contains 0.
      \end{itemize}
    \end{card}
  \end{columns}
  \vspace{0pt}\centering
  \begin{tikzpicture}[x=0.72cm,y=0.38cm,font=\scriptsize]
    \foreach \i/\tr/\te in {0/4/2, 1/6/2, 2/8/2} {
      \fill[pblue] (0,-\i) rectangle (\tr,-\i+0.38); \fill[porange] (\tr,-\i) rectangle (\tr+\te,-\i+0.38);}
    \node[anchor=west,text=graytxt] at (6.4,0) {origin 1: train 2015--16, forecast 2017};
    \node[anchor=west,text=graytxt] at (8.4,-1) {origin 2: train 2015--17, forecast 2018};
    \node[anchor=west,text=graytxt] at (10.4,-2) {origin 3: train 2015--18, forecast 2019};
  \end{tikzpicture}\\[3pt]
  \begin{takeaway}
    \textbf{Pre-declared headline:} Fourier+ARMA, selection inside each window. Other variants are comparisons, not cherry-picks.
  \end{takeaway}
\end{frame}

\begin{frame}{52-Week Backtest: Climatology Is Hard to Beat}
  \centering
  \includegraphics[width=0.86\linewidth]{fig/fc_backtest.pdf}\\[3pt]
  \begin{takeaway}
    MAE in \ugm{}; 2019: selected \fcMaeSelNineteen\ vs climatology \fcMaeClimNineteen, SARIMA $D=1$ \fcMaeSarimaNineteen\ (but \fcMaeSarimaSeventeen\ in 2017). A year ahead, the calendar is most of the signal: a smooth Fourier model matches climatology, while SARIMA $D=0$ (\fcMaeSarimaZeroNineteen) and the LSTM (\fcMaeLstmNineteen) are clearly worse.
  \end{takeaway}
\end{frame}

\begin{frame}{Backtest Table: Which Models Beat Climatology?}
  \centering\footnotesize
  \input{tables/fc_backtest.tex}\par\vspace{6pt}
  \begin{takeaway}
    MAE in \ugm{} (lower is better). The last column is a moving-block bootstrap of the paired error differences to climatology over the 2018 and 2019 forecasts: the seasonal naive, SARIMA $D=0$ and the LSTM are \emph{clearly worse}. The linear-trend Fourier variant looks better on 2018--19 but not over all three origins, and it was not our pre-declared choice, so we do not claim it. With three origins we cannot rank the rest.
  \end{takeaway}
\end{frame}

\begin{frame}{Diagnostics and Intervals: Two Pitfalls Fixed}
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \begin{card}[title={Residual checks}]{pblue}\footnotesize
      \begin{itemize}\setlength\itemsep{3pt}
        \item The draft's Ljung-Box $p\approx0$ was an \textbf{artifact}: the first 52 residuals of a $D=1$ model are diffuse-initialisation values. Removed, the SARIMA residuals pass at lags 10 and 26.
        \item The seasonal MA ($\fcMaCoef$, SE $>1$) is not identified: the seasonal difference is not needed.
        \item Honest limit: the Fourier model still shows some autocorrelation at lags 26 and 52.
      \end{itemize}
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={Prediction intervals (95\%)}]{porange}\footnotesize
      \begin{itemize}\setlength\itemsep{3pt}
        \item Model-based intervals covered \fcCovRaw\% of 2019 weeks. All misses were on the low side (2019 was cleaner than 2015--18).
        \item Scaling the spread by season, using only 2017--18 errors, gives \fcCovCal\% coverage on 2019. We re-centre only if the bias had the same sign and was large in both earlier years; it was not.
      \end{itemize}
    \end{card}
  \end{columns}
  \vspace{6pt}
  \begin{takeaway}
    Two earlier ``problems'' were measurement errors, not model failures. Residual structure and a falling level (see the station check) remain real limits.
  \end{takeaway}
\end{frame}

\begin{frame}{One Week Ahead: Does Weather Help?}
  \centering
  \includegraphics[width=0.82\linewidth]{fig/fc_oneweek.pdf}\\[2pt]
  \begin{takeaway}
    Using \emph{last} week's wind and humidity changes the error by \fcOneLagged\% (last 3 days: \fcOneLastThree\%): no gain. Using the \emph{same} week's weather, which is unknown in advance (ERA5 is observed, not forecast), improves by only \fcOneOracle\% ($p\approx0.07$). Weather is explanatory over days, but a poor forecasting input.
  \end{takeaway}
\end{frame}

\begin{frame}{Outlook for 2020, Month by Month}
  \centering
  \includegraphics[width=0.95\linewidth]{fig/fc_outlook.pdf}\\[2pt]
  \begin{takeaway}
    Fitted on 2015--2019 only. \textbf{Validation of the same pipeline on 2019:} all \fcValInside\ monthly means fell inside the 95\% interval, but the model over-predicted the share of Poor-or-worse days (\fcValPoorPred\% vs \fcValPoorAct\% actual), the same level bias as before. In 2020, Jan--Feb fall inside the interval; March--May fall below it (lockdown). Bands are \pmtwo{} sub-index bands, not the official AQI.
  \end{takeaway}
\end{frame}

\begin{frame}{Case Study: The 2020 Lockdown}
  \centering
  \includegraphics[width=0.88\linewidth]{fig/fc_lockdown.pdf}\\[2pt]
  \begin{takeaway}
    From 29 Mar to 31 May 2020, \pmtwo{} was about \textbf{\fcLockPct\%} below the no-lockdown forecast (95\% interval \fcLockLo--\fcLockHi\%). Adjusting the forecast for the actual wind and humidity of those weeks, the gap is \textbf{\fcLockWxPct\%}: most of the drop is not weather. Descriptive: it relies on the model's 2020 level being right.
  \end{takeaway}
\end{frame}

\begin{frame}{What We Established, and the Limits}
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \begin{card}[title={Established}]{pgreen}\scriptsize
      \begin{itemize}\setlength\itemsep{2pt}
        \item Strong yearly cycle (winter \ratioWM$\times$ the monsoon); log stabilises variance.
        \item Wind and humidity anomalies robustly \emph{predict} PM$_{2.5}$ for about a week; effect \irfWindA--\irfWindB\% (wind), \irfRhA--\irfRhB\% (humidity) the next day.
        \item At a weekly-to-yearly horizon weather adds nothing usable; a Fourier+ARMA model matches or slightly beats climatology; SARIMA, LSTM do not help.
        \item The 2016--19 decline is real (about $-$\declPanel\% on a fixed station panel).
        \item The lockdown cut PM$_{2.5}$ by about \fcLockPct\% relative to forecast.
      \end{itemize}
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={Limits}]{porange}\scriptsize
      \begin{itemize}\setlength\itemsep{2pt}
        \item Granger = predictive; mixing height, stubble burning, fireworks are unmeasured.
        \item Weather's share of 14-day error depends on the VAR ordering (\fevdA--\fevdB\%).
        \item Three backtest origins: few independent tests; most model differences are not significant.
        \item Level bias in 2019; residual autocorrelation at long lags.
        \item One city; data end in mid-2020; ERA5 is a grid cell; PM$_{2.5}$ band $\ne$ official AQI.
      \end{itemize}
    \end{card}
  \end{columns}
\end{frame}

% ───────────────────────── Backup A: glossary ─────────────────────────
\appendix
\begin{frame}{Backup: Glossary of Terms}
  \footnotesize
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \textbf{PM$_{2.5}$}: particles under 2.5 $\mu$m, \ugm{}.\\[2pt]
    \textbf{AQI}: India's Air Quality Index (worst pollutant); we use only the PM$_{2.5}$ band.\\[2pt]
    \textbf{Reanalysis (ERA5)}: observations blended into a weather model.\\[2pt]
    \textbf{STL, $F_S$}: trend/seasonal/residual split; seasonal strength.\\[2pt]
    \textbf{Log transform}: makes percentage swings equal; stabilises variance.\\[2pt]
    \textbf{Volatility}: how much values swing; \textbf{ARCH-LM} tests clustering of big swings; \textbf{Levene} tests equal spread.\\[2pt]
    \textbf{Stationary}: no drift in mean, spread or autocorrelation; \textbf{ADF/KPSS} test it.
    \column{0.485\linewidth}
    \textbf{VAR}: each variable predicted from past values of all variables.\\[2pt]
    \textbf{Granger causality}: past X improves the forecast of Y.\\[2pt]
    \textbf{HAC errors}: standard errors robust to autocorrelation and changing variance.\\[2pt]
    \textbf{Shock}: the unpredictable part of a variable today; \textbf{SD} = its typical size.\\[2pt]
    \textbf{Impulse response}: path of PM$_{2.5}$ after a shock; \textbf{FEVD}: share of forecast error due to each variable.\\[2pt]
    \textbf{SARIMA}: seasonal ARIMA. \textbf{Fourier+ARMA}: yearly sine/cosine terms + ARMA errors. \textbf{Climatology}: the average of each calendar week. \textbf{MAE}: mean absolute error.
  \end{columns}
\end{frame}

% ───────────────────────── Backup B: robustness ─────────────────────────
\begin{frame}{Backup: How Robust Is the Weather Result?}
  \centering\scriptsize\setlength{\tabcolsep}{4pt}
  \input{tables/granger_robust.tex}\par\vspace{2pt}
  \input{tables/orderings.tex}\par
  {\tiny W-first = weather ordered first; P-first = PM$_{2.5}$ ordered first.}\par\vspace{1pt}
  \begin{takeaway}
    Robust (HAC) tests agree with the plain tests. The reverse direction (PM$_{2.5}$ $\to$ wind) is weakly significant at 1--2 lags only. The size of a shock's effect and weather's share of forecast error depend on the VAR ordering, so we report ranges, not single values.
  \end{takeaway}
\end{frame}

% ───────────────────────── Backup C: boxplot ─────────────────────────
\begin{frame}{Backup: PM$_{2.5}$ by Month}
  \centering
  \includegraphics[width=\linewidth]{fig/seasonal_boxplot.pdf}\\[2pt]
  \begin{takeaway}
    Box = middle 50\% of days, line = median, dots = unusually high days. Orange: winter (Nov--Jan); blue: monsoon (Jul--Sep).
  \end{takeaway}
\end{frame}


% ───────────────────────── Backup D/E: station check, outlook table ─────────────────────────
\begin{frame}{Backup: Is the 2016--19 Decline Real? Station Check}
  \centering
  \includegraphics[width=0.85\linewidth]{fig/fc_station.pdf}\\[2pt]
  \begin{takeaway}
    The city series is the mean of the stations (corr.\ 0.995) and the number of stations rose from 8--10 to 37, so a mix effect is possible. But a fixed panel of six long-running stations falls by \declPanel\%, all stations by \declAll\%, and the weather-adjusted city series by \declWx\% (2016 $\to$ 2019): most of the decline is real.
  \end{takeaway}
\end{frame}

\begin{frame}{Backup: 2020 Outlook Table}
  \centering\scriptsize\setlength{\tabcolsep}{5pt}
  \input{tables/fc_outlook.tex}\par\vspace{2pt}
  {\tiny Monthly mean \pmtwo{} (\ugm{}); P(mean$>$90) = probability the monthly mean exceeds 90; Days Poor+ = expected days with daily \pmtwo{} above 90 (PM$_{2.5}$ band, not official AQI). Actual shown for full months only.}
\end{frame}

\end{document}
```
