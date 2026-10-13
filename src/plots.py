"""Shared figure style: recessive hairline chrome, thin marks, fixed categorical colour order."""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

from .aqi import band_edges

FIGURES = Path(__file__).resolve().parents[1] / "figures"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

# Categorical slots, always assigned in this order
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
NEUTRAL = "#b5b4ad"  # de-emphasised "everything else"

SEASON_COLORS = {"Winter (Nov–Jan)": ORANGE, "Monsoon (Jul–Sep)": BLUE, "Other months": NEUTRAL}
VAR_COLORS = {"pm25": BLUE, "wind": ORANGE, "rh": AQUA}
LABELS = {
    "pm25": "PM2.5 (µg/m³)", "log_pm25": "log PM2.5", "no2": "NO₂ (µg/m³)", "so2": "SO₂ (µg/m³)",
    "rh": "Relative humidity (%)", "wind": "Wind speed (km/h)", "temp": "Temperature (°C)",
    "precip": "Precipitation (mm)", "aqi": "AQI",
}


def use_style():
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": ["Noto Sans", "DejaVu Sans"],  # DejaVu supplies glyphs Noto lacks (e.g. →)
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": INK_2,
        "axes.titlesize": 12,
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.titlecolor": INK,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "grid.linestyle": "-",
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2,
        "lines.linewidth": 1.5,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "figure.dpi": 110,
    })


def savefig(fig, name):
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / f"{name}.png", dpi=200, bbox_inches="tight")


def shade_aqi_bands(ax, ymax, label_x=None, alpha=0.10):
    """Shade CPCB AQI category bands behind a PM2.5 axis and name each band at the right edge."""
    for name, lo, hi, colour in band_edges():
        if lo >= ymax:
            break
        top = min(hi, ymax)
        ax.axhspan(lo, top, color=colour, alpha=alpha, lw=0, zorder=0)
        ax.text(1.005, (lo + top) / 2, name, transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=8, color=INK_2)
