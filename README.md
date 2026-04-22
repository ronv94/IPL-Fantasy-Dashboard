# 🏏 IPL Rasiya 2026 — Fantasy Dashboard

A competitive fantasy cricket dashboard for your IPL friend group. Track standings, compare teams, discover who's on fire, and fuel the rivalry.

## Features

- **Overview** — Live leaderboard, cumulative points race, match results
- **Stats** — Score distributions, heatmaps, consistency metrics, transfer efficiency
- **Head-to-Head** — Radar comparison, match-by-match bars, win records
- **Power Rankings** — Weighted rankings, hot/cold streaks, form guide, season awards
- **Admin** — Admin panel to enter scores and manage teams

## Quick Start

```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

Open http://127.0.0.1:8050 → go to Admin → add teams → enter scores.

## Docker

Build and run with Docker:

```bash
make build
make up
```

The app will be available at `http://127.0.0.1:8050`.

`make up` uses Docker Compose under the hood.

Stop it with:

```bash
make stop
```

Useful commands:

```bash
make logs
make shell
make stop
make restart
make rm-image
```

You can override the default port at runtime:

```bash
make up PORT=8060
```

## Tech Stack

Dash · Plotly · SQLite · Bootstrap (Darkly) · Montserrat font

## Deployment (Render)

The app starts with `gunicorn app:server`.
