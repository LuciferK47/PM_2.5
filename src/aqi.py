"""CPCB (India) National AQI PM2.5 sub-index bands for 24-hour average PM2.5 (µg/m³).

The official AQI is the MAXIMUM sub-index over all pollutants, so a band here is a "PM2.5 sub-index band", not the AQI.
"""
import numpy as np
import pandas as pd

# (category, upper PM2.5 bound in µg/m³, AQI range, CPCB colour)
CPCB_PM25_BANDS = [
    ("Good",         30,     "0–50",    "#00B050"),
    ("Satisfactory", 60,     "51–100",  "#92D050"),
    ("Moderate",     90,     "101–200", "#E6C200"),
    ("Poor",         120,    "201–300", "#FF9900"),
    ("Very Poor",    250,    "301–400", "#FF0000"),
    ("Severe",       np.inf, "401–500", "#C00000"),
]
CATEGORIES = [b[0] for b in CPCB_PM25_BANDS]


def pm25_category(pm25):
    """Map PM2.5 concentration(s) to the CPCB AQI category name."""
    edges = [-np.inf] + [b[1] for b in CPCB_PM25_BANDS]
    return pd.cut(pd.Series(pm25), bins=edges, labels=CATEGORIES, right=True)


def band_edges():
    """(category, lower, upper, colour) tuples for shading plots."""
    lower = 0
    out = []
    for name, upper, _, colour in CPCB_PM25_BANDS:
        out.append((name, lower, upper, colour))
        lower = upper
    return out


def band_probabilities(mu, sd):
    """P(PM2.5 in each band) for a lognormal log-PM2.5 ~ N(mu, sd^2). Returns array (len(CATEGORIES),)."""
    from scipy.stats import norm
    edges = [b[1] for b in CPCB_PM25_BANDS[:-1]]
    cdf = np.r_[0.0, norm.cdf((np.log(edges) - mu) / sd), 1.0]
    return np.diff(cdf)
