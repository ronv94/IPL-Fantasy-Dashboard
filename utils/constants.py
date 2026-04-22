import os

# ─── App Settings ────────────────────────────────────────────────────────────
APP_TITLE = "IPL Rasiya 2026"
TOTAL_MATCHES = 74

# ─── Database ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "fantasy.db")

# ─── Team Color Palette (assigned in order when teams are added) ─────────────
TEAM_COLORS = [
    "#FF6B35",  # Vivid Orange
    "#FFD23F",  # Bright Yellow
    "#06D6A0",  # Emerald Green
    "#118AB2",  # Cerulean Blue
    "#EF476F",  # Hot Pink
    "#8338EC",  # Electric Purple
    "#3A86FF",  # Royal Blue
    "#F72585",  # Magenta
    "#4CC9F0",  # Sky Cyan
    "#FB5607",  # Burnt Orange
    "#80ED99",  # Mint Green
    "#E9FF70",  # Lime
    "#FF006E",  # Rose
    "#FFBE0B",  # Amber
    "#00F5D4",  # Aqua
]

# ─── Chart Theme ─────────────────────────────────────────────────────────────
CHART_FONT = "Montserrat, sans-serif"
CHART_BG = "rgba(0,0,0,0)"
CHART_PAPER_BG = "rgba(0,0,0,0)"
CHART_GRID_COLOR = "rgba(255,255,255,0.08)"
CHART_TEXT_COLOR = "#E0E0E0"
CHART_HEIGHT = 420

CHART_LAYOUT_DEFAULTS = dict(
    font=dict(family=CHART_FONT, color=CHART_TEXT_COLOR),
    paper_bgcolor=CHART_PAPER_BG,
    plot_bgcolor=CHART_BG,
    margin=dict(l=50, r=30, t=50, b=50),
    height=CHART_HEIGHT,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(size=11),
    ),
    xaxis=dict(gridcolor=CHART_GRID_COLOR, zeroline=False),
    yaxis=dict(gridcolor=CHART_GRID_COLOR, zeroline=False),
)

# ─── Awards Configuration ────────────────────────────────────────────────────
CENTURION_THRESHOLD = 500  # Points in a single match to earn "Centurion"
STREAK_MIN_LENGTH = 3  # Minimum matches for a hot/cold streak
ROLLING_WINDOW = 5  # Matches for rolling average
POWER_RANKING_DECAY = 0.92  # Exponential decay factor (closer to 1 = slower decay)
