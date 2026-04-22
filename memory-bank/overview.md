# IPL Fantasy Dashboard Repo Memory

- App: Plotly Dash app for IPL fantasy league insights, multi-page layout.
- Entry point: app.py
- Core modules: utils/constants.py, utils/db.py, utils/models.py, utils/calculations.py, utils/chart_helpers.py, utils/components.py
- Pages: pages/overview.py, pages/stats.py, pages/head_to_head.py, pages/power_rankings.py, pages/admin.py
- Styling/assets: assets/custom.css; assets/ipl_rasiya_logo.png present in repo
- Data store: SQLite DB at data/fantasy.db (ignored by git)
- Local run: python app.py
- Docker workflow: make build, make up, make stop, make logs, make shell
- Makefile uses docker compose under the hood; PORT can be overridden, e.g. make up PORT=8060
- Compose file: docker-compose.yaml
- Dockerfile serves app with gunicorn app:server on port 8050
- Render deploy config exists in render.yaml using gunicorn app:server
- Current app behavior: admin page is open directly, no password gate
- Repo ignores: .venv, __pycache__, .DS_Store, data/fantasy.db, common Python caches