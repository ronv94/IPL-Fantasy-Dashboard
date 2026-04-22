# 🏏 IPL Rasiya 2026 — Fantasy Dashboard

A competitive fantasy cricket dashboard for your IPL friend group. Track standings, compare teams, discover who's on fire, and fuel the rivalry.

## Features

- **Overview** — Live leaderboard, cumulative points race, match results
- **Stats** — Score distributions, heatmaps, consistency metrics, transfer efficiency
- **Head-to-Head** — Radar comparison, match-by-match bars, win records
- **Power Rankings** — Weighted rankings, hot/cold streaks, form guide, season awards
- **Admin** — Password-protected panel to enter scores, manage teams

## Quick Start

```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set admin password (optional, defaults to "rasiya2026")
export ADMIN_PASSWORD="your_password"

# Run
python app.py
```

Open http://127.0.0.1:8050 → go to Admin → add teams → enter scores.

## Tech Stack

Dash · Plotly · SQLite · Bootstrap (Darkly) · Montserrat font

## Deployment (Render)

Set `ADMIN_PASSWORD` in Render environment variables. The app starts with `gunicorn app:server`.
