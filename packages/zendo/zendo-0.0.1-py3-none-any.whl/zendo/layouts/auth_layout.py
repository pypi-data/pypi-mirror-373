import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, callback, html, ctx

from zendo.components import LoginUserAIO, NavbarAIO, RegisterUserAIO


class AuthLayout(html.Div):
    class ids:
        @staticmethod
        def content(aio_id: str) -> dict:
            return {
                "component": "AuthLayout",
                "subcomponent": "content",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(self, aio_id: str):
        super().__init__(
            [
                html.Div(
                    id=self.ids.content(aio_id),
                    style={"width": "400px"},
                ),
            ],
            className="d-flex flex-column align-items-center justify-content-center",
            style={
                "minHeight": "calc(100vh - 62px)",  # Account for navbar height
            },
        )

    @callback(
        Output(ids.content(MATCH), "children"),
        Input(NavbarAIO.ids.action_button(MATCH, "login"), "n_clicks"),
        Input(NavbarAIO.ids.action_button(MATCH, "register"), "n_clicks"),
        prevent_initial_call=True,
    )
    def update_auth_view(login_clicks, register_clicks):
        """
        Update the authentication view based on navbar button clicks.

        Parameters
        ----------
        login_clicks : int
            Number of times login button was clicked.
        register_clicks : int
            Number of times register button was clicked.
        current_view : str
            Current view state.

        Returns
        -------
        tuple
            Updated auth container and view state.
        """
        aio_id = None
        if ctx.triggered:
            aio_id = ctx.triggered_id["aio_id"]
            action_id = ctx.triggered_id["action_id"]
            if "register" == action_id:
                return RegisterUserAIO(aio_id=aio_id)
        # Fallback
        return LoginUserAIO(aio_id=aio_id)
