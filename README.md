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

For durable admin data on Render, deploy on a paid web service with a persistent disk.
The included [render.yaml](/Users/ronakpatel/Python Learning - GitHub/IPL Fantasy/IPL-Fantasy-Dashboard-1/render.yaml) is configured for this setup:

- `plan: starter` because Render disks are not available on the free web service.
- A persistent disk is mounted at `/opt/render/project/src/data`.
- `FANTASY_DB_PATH` points SQLite at `/opt/render/project/src/data/fantasy.db`.

That means all teams, scores, transfers, and match metadata entered from Admin are stored in the SQLite file on the attached Render disk and survive restarts and redeploys.

Notes:

- Persistent disks are billed separately by Render.
- A service with an attached disk runs as a single instance and does not support zero-downtime deploys.
- If you already have a local `data/fantasy.db`, copy it to the Render disk after first deploy if you want to seed production with existing data.
