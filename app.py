import dash
from dash import Dash, html, dcc
import dash_mantine_components as dmc

from utils.db import init_db
from utils.cache import cache
from utils.components import create_navbar
from utils.constants import APP_TITLE

# Initialize database on startup
init_db()

# ─── Dash App ────────────────────────────────────────────────────────────────

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        *dmc.styles.ALL,
        "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap",
    ],
    suppress_callback_exceptions=True,
    title=APP_TITLE,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server
cache.init_app(server)

# ─── Layout ──────────────────────────────────────────────────────────────────

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={
        "fontFamily": "Montserrat, sans-serif",
        "primaryColor": "orange",
    },
    children=html.Div(
        [
            create_navbar(),
            html.Div(
                dash.page_container,
                className="main-container",
            ),
        ],
        className="app-wrapper",
    ),
)

# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
