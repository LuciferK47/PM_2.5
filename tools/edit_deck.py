from pathlib import Path
p = Path("slides/beamer/main.tex"); s = p.read_text()
def sub(old, new, count=1):
    global s
    assert s.count(old) >= 1, old[:60]
    s = s.replace(old, new) if count == 0 else s.replace(old, new, count)

sub("Time-series analysis with VAR, Granger causality and SARIMA", "Time-series analysis: VAR, Granger causality and seasonal forecasting")
sub(r"\date{October 2026}", r"\date{November 2026}")
sub(r"October 2026}};", r"November 2026}};")
sub(r"(Poor starts above 90 \ugm{}).", r"(Poor starts above 90 \ugm{}). The official AQI takes the worst pollutant; we use the PM$_{2.5}$ band only.")
# slide 3
sub(r"\textbf{Q2a. Next week.} SARIMAX with that week's wind and humidity", r"\textbf{Q2a. Next week.} Does weather improve a 1-week forecast?")
sub(r"\textbf{Q2b. Next 12 months.} SARIMA, no weather inputs", r"\textbf{Q2b. Next 12 months.} Fourier+ARMA vs SARIMA and baselines, no weather inputs")
sub(r"\node[sres=graytxt] (r2) at (12.3,2.0) {\textbf{Next phase:} test whether weather improves a 1-week forecast};", r"\node[sres=pgreen] (r2) at (12.3,2.0) {\textbf{Done:} yesterday's weather adds nothing; same-week weather (unknowable in advance) helps only \fcOneOracle\%};")
sub(r"\node[sres=graytxt] (r3) at (12.3,0.4) {\textbf{Next phase:} 52-week forecast, validated on 2019};", r"\node[sres=pgreen] (r3) at (12.3,0.4) {\textbf{Done:} 52-week forecasts backtested on 2017--19; outlook for 2020};")
sub(r"The final output is a month-by-month AQI outlook for health advisories.", r"The final output is a month-by-month PM$_{2.5}$ outlook with prediction intervals.")
# slide 4
sub(r"lockdown: excluded", r"lockdown: case study only")
sub(r"\textbf{Daily} data for causality, \textbf{weekly means} (287 weeks) for forecasting.", r"\textbf{Daily} data for causality, \textbf{weekly means} (287 weeks) for forecasting, validated on three expanding-window origins (forecast years 2017, 2018, 2019).")
# slide 5, 8, 8b
sub(r"$F_S=\mathbf{\Fs}$: the yearly cycle dominates", r"$F_S=\mathbf{\Fs}$ (2015--18 weeks): the yearly cycle dominates")
sub(r"so the yearly cycle is a repeating pattern, not a drifting trend.", r"so the yearly cycle is a repeating pattern. Once the cycle is removed, a slow \emph{downward drift} appears (about $-$\declAll\% from 2016 to 2019), so the level is not constant.")
sub(r"\textbf{Both tests pass} for log \pmtwo{} and for its seasonal difference $\Rightarrow$ $d=0$.", r"\textbf{Both tests are consistent with stationarity} for log \pmtwo{} and its seasonal difference $\Rightarrow$ $d=0$.")
sub(r"\textbf{Seasonal difference $D$} (0 or 1) is chosen in the next phase, when we fit the seasonal models, using a validation year, not the test year.", r"A seasonal difference $D=1$ is not needed: a $D=1$ SARIMA's seasonal MA coefficient is $\fcMaCoef$ with standard error \fcMaSE, the sign of over-differencing, so we model the cycle with Fourier terms instead.")
sub(r"Wind and humidity help predict \pmtwo{} at every lag from 1 to 7 days ($p<10^{-9}$; bars: 4 lags), and humidity still matters given rain. The reverse is absent for humidity and weak for wind (lags 1--2 only, $p\approx0.02$--$0.04$).", r"Wind and humidity help predict \pmtwo{} in joint tests at every lag order from 1 to 7 days ($p<10^{-9}$; bars: 4 lags), also given rain and temperature. The reverse is absent for humidity and weak for wind (lag orders 1--2 only, $p\approx0.02$--$0.04$).")
sub(r"\pmtwo{} is \textbf{\shockWindBig\%} lower the next day than the day before; after a calmer one ($-$\shockWindCalmZ\,SD), \textbf{\shockWindCalm\%} higher.", r"\pmtwo{} on the following day is \textbf{\shockWindBig\%} lower than on the day before the shock (change from day $t-1$ to $t+1$); after a calmer one ($-$\shockWindCalmZ\,SD), \textbf{\shockWindCalm\%} higher.")
sub(r"\emph{last} week's weather adds nothing to predict this week's \pmtwo{}", r"\emph{last} week's weather adds nothing to last week's \pmtwo{} for predicting this week's")
sub(r"log \pmtwo{} is stationary on the training years, so $d=0$.", r"log \pmtwo{} is consistent with stationarity ($d=0$), with a slow downward level drift.")
sub(r"\textbf{Causality:} wind and humidity \textbf{Granger-cause} \pmtwo{} (robust to lag choice, differencing, robust errors and a rain control); the reverse is absent for humidity and weak for wind.", r"\textbf{Causality:} wind and humidity \textbf{Granger-cause} \pmtwo{} (robust to lag choice, differencing, robust errors, rain and temperature controls); the reverse is absent for humidity and weak for wind.")
sub(r"Answer to Q1: \textbf{yes}, weather (wind, humidity) drives \pmtwo{} over the following days, which is the evidence that justifies testing weather inputs in the forecasting models next.", r"Answer to Q1: wind and humidity have a \textbf{robust predictive association} with \pmtwo{} over the following days (predictive, not proof of physical cause).")

# replace the final 'Limits and Next Phase' frame with the forecasting slides
a = s.index(r"\begin{frame}{Limits and Next Phase}")
b = s.index(r"% ───────────────────────── Backup A: glossary")
new = r'''\begin{frame}{Forecasting: Models and How We Test Them}
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
  \vspace{4pt}\centering
  \begin{tikzpicture}[x=1.0cm,y=0.5cm,font=\scriptsize]
    \foreach \i/\tr/\te in {0/4/2, 1/6/2, 2/8/2} {
      \fill[pblue] (0,-\i) rectangle (\tr,-\i+0.38); \fill[porange] (\tr,-\i) rectangle (\tr+\te,-\i+0.38);}
    \node[anchor=west,text=graytxt] at (6.4,0) {origin 1: train 2015--16, forecast 2017};
    \node[anchor=west,text=graytxt] at (8.4,-1) {origin 2: train 2015--17, forecast 2018};
    \node[anchor=west,text=graytxt] at (10.4,-2) {origin 3: train 2015--18, forecast 2019};
  \end{tikzpicture}\\[3pt]
  \begin{takeaway}
    \textbf{Pre-declared headline:} Fourier+ARMA with selection inside each window (no peeking at the test year). Other variants are reported as comparisons, not cherry-picked.
  \end{takeaway}
\end{frame}

\begin{frame}{52-Week Backtest: Climatology Is Hard to Beat}
  \centering
  \includegraphics[width=0.92\linewidth]{fig/fc_backtest.pdf}\\[2pt]
  {\scriptsize\input{tables/fc_backtest.tex}}\\[2pt]
  \begin{takeaway}
    MAE in \ugm{}. On 2019 the selected model scores \fcMaeSelNineteen\ vs \fcMaeClimNineteen\ for climatology, and SARIMA $D=1$ \fcMaeSarimaNineteen\ (but \fcMaeSarimaSeventeen\ in 2017). Differences to climatology are mostly \emph{indistinguishable}: a year ahead, the calendar is most of the signal. $D=0$ SARIMA (\fcMaeSarimaZeroNineteen) and the LSTM (\fcMaeLstmNineteen) are clearly worse.
  \end{takeaway}
\end{frame}

\begin{frame}{Diagnostics and Intervals: Two Pitfalls Fixed}
  \begin{columns}[T,onlytextwidth]
    \column{0.485\linewidth}
    \begin{card}[title={Residual checks}]{pblue}\small
      \begin{itemize}\setlength\itemsep{3pt}
        \item The draft's Ljung-Box $p\approx0$ was an \textbf{artifact}: the first 52 residuals of a $D=1$ model are diffuse-initialisation values. Removed, the SARIMA residuals pass at lags 10 and 26.
        \item The seasonal MA ($\fcMaCoef$, SE \fcMaSE) is not identified: the seasonal difference is not needed.
        \item Honest limit: the Fourier model still shows some autocorrelation at lags 26 and 52.
      \end{itemize}
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={Prediction intervals (95\%)}]{porange}\small
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
    \begin{card}[title={Established}]{pgreen}\footnotesize
      \begin{itemize}\setlength\itemsep{2pt}
        \item Strong yearly cycle (winter \ratioWM$\times$ the monsoon); log stabilises variance.
        \item Wind and humidity anomalies robustly \emph{predict} PM$_{2.5}$ for about a week; effect \irfWindA--\irfWindB\% (wind), \irfRhA--\irfRhB\% (humidity) the next day.
        \item At a weekly-to-yearly horizon weather adds nothing usable; a Fourier+ARMA model matches or slightly beats climatology; SARIMA, LSTM do not help.
        \item The 2016--19 decline is real (about $-$\declPanel\% on a fixed station panel).
        \item The lockdown cut PM$_{2.5}$ by about \fcLockPct\% relative to forecast.
      \end{itemize}
    \end{card}
    \column{0.485\linewidth}
    \begin{card}[title={Limits}]{porange}\footnotesize
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

'''
s = s[:a] + new + s[b:]
# glossary + backup slides
sub(r"\textbf{AQI}: India's Air Quality Index, CPCB categories.", r"\textbf{AQI}: India's Air Quality Index (worst pollutant); we use only the PM$_{2.5}$ band.")
sub(r"\textbf{SARIMA(X)} (next phase): seasonal ARIMA, optionally with external regressors such as weather.", r"\textbf{SARIMA}: seasonal ARIMA. \textbf{Fourier+ARMA}: yearly sine/cosine terms + ARMA errors. \textbf{Climatology}: the average of each calendar week. \textbf{MAE}: mean absolute error.")
backup = r'''
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
'''
c = s.index(r"\end{document}")
s = s[:c] + backup + "\n" + s[c:]
p.write_text(s)
print("ok")
