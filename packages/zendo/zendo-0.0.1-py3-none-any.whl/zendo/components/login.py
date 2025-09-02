"""
AIO Components - All-in-One authentication components.

This module provides reusable All-in-One (AIO) components for user authentication
including registration and login forms with built-in validation and callbacks.
"""

import uuid

from dash import MATCH, Input, Output, State, callback, dcc, html, no_update
import dash_bootstrap_components as dbc


from ..auth import authenticate_user, login_user


class AuthStateAIO(dcc.Store):
    class ids:
        """Pattern-matching callback IDs for AuthStateAIO subcomponents."""

        @staticmethod
        def state(aio_id: str):
            return {
                "component": "AuthStateAIO",
                "subcomponent": "auth_state",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(self, aio_id: str = None):
        super().__init__(id=self.ids.state(aio_id), data=False)


class LoginUserAIO(dbc.Card):
    class ids:
        """Pattern-matching callback IDs for LoginUserAIO subcomponents."""

        @staticmethod
        def form(aio_id):
            return {
                "component": "LoginUserAIO",
                "subcomponent": "form",
                "aio_id": aio_id,
            }

        @staticmethod
        def username_input(aio_id):
            return {
                "component": "LoginUserAIO",
                "subcomponent": "username_input",
                "aio_id": aio_id,
            }

        @staticmethod
        def password_input(aio_id):
            return {
                "component": "LoginUserAIO",
                "subcomponent": "password_input",
                "aio_id": aio_id,
            }

        @staticmethod
        def submit_button(aio_id):
            return {
                "component": "LoginUserAIO",
                "subcomponent": "submit_button",
                "aio_id": aio_id,
            }

        @staticmethod
        def alert(aio_id):
            return {
                "component": "LoginUserAIO",
                "subcomponent": "alert",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        aio_id=None,
        form_props=None,
        card_props=None,
        title="Login",
        username_label="Username or Email",
        submit_button_text="Login",
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())
        # Merge user-supplied properties with defaults
        form_props = form_props if form_props else {}
        card_props = card_props if card_props else {}
        super().__init__(
            [
                # Clean header
                dbc.CardHeader(title),
                # Form content
                dbc.CardBody(
                    [
                        html.Div(
                            id=self.ids.alert(aio_id),
                            style={"display": "none"},
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dbc.Label(username_label),
                                        dbc.Input(
                                            id=self.ids.username_input(aio_id),
                                            type="text",
                                            placeholder="Enter username or email",
                                        ),
                                    ],
                                    style={"marginBottom": "1rem"},
                                ),
                                html.Div(
                                    [
                                        dbc.Label("Password"),
                                        dbc.Input(
                                            id=self.ids.password_input(aio_id),
                                            type="password",
                                            placeholder="Enter password",
                                        ),
                                    ],
                                    style={"marginBottom": "1rem"},
                                ),
                            ],
                            id=self.ids.form(aio_id),
                            **form_props,
                        ),
                    ],
                    class_name="py-0 pt-3",
                ),
                dbc.CardFooter(
                    [
                        dbc.Button(
                            submit_button_text,
                            id=self.ids.submit_button(aio_id),
                        ),
                    ],
                ),
            ],
            **card_props,
        )

    @callback(
        Output(ids.alert(MATCH), "children"),
        Output(ids.alert(MATCH), "style"),
        Output(ids.username_input(MATCH), "value"),
        Output(ids.password_input(MATCH), "value"),
        Output(AuthStateAIO.ids.state(MATCH), "data", allow_duplicate=True),
        Input(ids.submit_button(MATCH), "n_clicks"),
        State(ids.username_input(MATCH), "value"),
        State(ids.password_input(MATCH), "value"),
        State(AuthStateAIO.ids.state(MATCH), "data"),
        prevent_initial_call=True,
    )
    def handle_login(n_clicks, username, password, login_state):
        if not n_clicks:
            return no_update
        # Validation
        if not username or not password:
            return (
                "Please fill in all fields.",
                create_alert_style(True),
                no_update,
                no_update,
                no_update,
            )

        # Attempt authentication
        success, message, user = authenticate_user(username, password)

        if success:
            # Store user info and clear form
            login_user(user)
            return (
                f"Welcome back, {user.get_full_name()}!",
                create_alert_style(False),
                "",
                "",
                True,
            )
        else:
            return (
                message,
                create_alert_style(True),
                no_update,
                "",
                no_update,
            )


def create_alert_style(is_error=True):
    return {
        "background": "#fef2f2" if is_error else "#f0f9ff",
        "border": "1px solid #fecaca" if is_error else "1px solid #bae6fd",
        "borderRadius": "8px",
        "padding": "12px 16px",
        "marginBottom": "1rem",
        "color": "#dc2626" if is_error else "#0369a1",
        "fontSize": "14px",
        "display": "block",
    }
