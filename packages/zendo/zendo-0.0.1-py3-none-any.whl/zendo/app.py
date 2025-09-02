"""
A Dash-based chat interface application with authentication.

This module provides a web-based chat interface using Dash 2.0+ framework
with Bootstrap components for styling and integrated user authentication.
"""

import os

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, html

from zendo import auth
from zendo.auth import login_manager
from zendo.components import AuthStateAIO, NavbarAIO
from zendo.constants import APP_ID, APP_MAIN_CONTENT_ID
from zendo.layouts import AuthLayout, MainLayout
from zendo.models import db
from zendo.config import appname


def create_app():
    """
    Create and configure the Dash application.

    Returns
    -------
    dash.Dash
        Configured Dash application instance.
    """
    app = dash.Dash(
        __name__,
        # external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
    )

    app.title = appname

    # Configure SQLAlchemy
    database_path = os.path.join(os.getcwd(), "data", "database.db")
    app.server.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_path}"
    app.server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.server.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "your-secret-key-here"
    )
    # Initialize SQLAlchemy with the Flask server
    db.init_app(app.server)
    login_manager.init_app(app.server)
    # Create database tables
    with app.server.app_context():
        db.create_all()
    app.layout = create_layout()
    return app


def create_layout():
    """
    Create the main layout for the application.

    Returns
    -------
    html.Div
        The main layout component containing navbar and content.
    """
    return html.Div(
        [
            AuthStateAIO(aio_id=APP_ID),
            # Navigation bar
            NavbarAIO(
                aio_id=APP_ID,
                brand_text=appname,
                nav_links=[],
                auth_actions=[
                    {
                        "text": "Login",
                        "id": "login",
                        "type": "button",
                    },
                    {
                        "text": "Register",
                        "id": "register",
                        "type": "button",
                    },
                ],
                user_actions=[
                    {
                        "text": "Logout",
                        "id": "logout",
                        "type": "button",
                    },
                ],
                fluid=True,
            ),
            # Main content area
            html.Div(id=APP_MAIN_CONTENT_ID, style={"flex": "1", "overflow": "auto"}),
        ],
        style={
            "height": "100vh",
            "display": "flex",
            "flexDirection": "column",
            "fontDamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
            "background": "#ffffff",
        },
    )


@callback(
    Output(APP_MAIN_CONTENT_ID, "children"),
    Input(AuthStateAIO.ids.state(APP_ID), "data"),
    prevent_initial_call=False,
)
def update_main_content(_):
    """
    Update main content based on authentication state.

    Parameters
    ----------
    _ : int, optional
        Authentication data from LoginUserAIO.

    Returns
    -------
    tuple
        Updated main content and page state.
    """
    if auth.current_user and auth.current_user.is_authenticated:
        # User is authenticated, show main interface
        return MainLayout(aio_id=APP_ID)
    # User is not authenticated, show auth interface
    return AuthLayout(aio_id=APP_ID)


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8051)
