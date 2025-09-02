"""
AIO Components - All-in-One navigation components.

This module provides reusable All-in-One (AIO) components for navigation
including navbar with user authentication state and configurable navigation links.
"""

import uuid

import dash_bootstrap_components as dbc
from dash import MATCH, Input, Output, State, callback, html, no_update

from zendo.auth import current_user, logout_user
from zendo.components.login import AuthStateAIO
from zendo.config import appname

DEFAULT_USERNAME = "X"


class NavbarAIO(dbc.Navbar):
    """
    All-in-One component for navigation bar.

    This component provides a complete navigation bar with user authentication
    state display, configurable navigation links, and customizable actions.
    It integrates with the AuthStore component to show/hide elements based on login status.
    """

    class ids:
        """Pattern-matching callback IDs for NavbarAIO subcomponents."""

        @staticmethod
        def navbar(aio_id):
            return {
                "component": "NavbarAIO",
                "subcomponent": "navbar",
                "aio_id": aio_id,
            }

        @staticmethod
        def brand_link(aio_id):
            return {
                "component": "NavbarAIO",
                "subcomponent": "brand_link",
                "aio_id": aio_id,
            }

        @staticmethod
        def action_button(aio_id, action_id):
            return {
                "component": "NavbarAIO",
                "subcomponent": "action_button",
                "aio_id": aio_id,
                "action_id": action_id,
            }

        @staticmethod
        def nav_link(aio_id, link_id):
            return {
                "component": "NavbarAIO",
                "subcomponent": "nav_link",
                "aio_id": aio_id,
                "link_id": link_id,
            }

        @staticmethod
        def user_dropdown_avatar(aio_id):
            return {
                "component": "NavbarAIO",
                "subcomponent": "user_dropdown_avatar",
                "aio_id": aio_id,
            }

        @staticmethod
        def user_dropdown_name(aio_id):
            return {
                "component": "NavbarAIO",
                "subcomponent": "user_dropdown_name",
                "aio_id": aio_id,
            }

        @staticmethod
        def user_dropdown_email(aio_id):
            return {
                "component": "NavbarAIO",
                "subcomponent": "user_dropdown_email",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        aio_id,
        brand_text=appname,
        brand_href="/",
        nav_links=None,
        auth_actions=None,
        user_actions=None,
        navbar_props=None,
        show_auth_section=True,
        fluid=False,
        **div_props,
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        # Set defaults to empty lists if not provided
        if nav_links is None:
            nav_links = []

        if auth_actions is None:
            auth_actions = []

        if user_actions is None:
            user_actions = []

        # Set default navbar properties for Bootstrap compatibility
        default_navbar_props = {
            "color": "light",
            "dark": False,
            "expand": "lg",
        }
        # Merge user-supplied properties with defaults
        navbar_props = {
            **default_navbar_props,
            **(navbar_props.copy() if navbar_props else {}),
        }

        # Create navigation links
        nav_link_elements = []
        for link in nav_links:
            default_style = {}
            link_style = {**default_style, **(link.get("style", {}))}
            if link.get("href"):
                element = dbc.NavLink(
                    link["text"],
                    id=self.ids.nav_link(aio_id, link["id"]),
                    href=link["href"],
                    style=link_style,
                )
                element = dbc.NavItem(element)
            else:
                element = dbc.Button(
                    link["text"],
                    id=self.ids.nav_link(aio_id, link["id"]),
                    style={**link_style, "background": "none", "border": "none"},
                )
            nav_link_elements.append(element)

        # Create auth action elements
        auth_action_elements = []
        for i, action in enumerate(auth_actions):
            is_last = i == len(auth_actions) - 1
            action_style = action.get("style") or {}
            if action.get("type", "link") == "button":
                element = dbc.Button(
                    action["text"],
                    id=self.ids.action_button(aio_id, action["id"]),
                    style=action_style,
                    class_name="hidden-on-login" + (" me-0" if is_last else " me-2"),
                )
            else:
                element = dbc.NavLink(
                    action["text"],
                    id=self.ids.action_button(aio_id, action["id"]),
                    href=action.get("href", "#"),
                    style=action_style,
                    className="hidden-on-login" + (" me-0" if is_last else " me-2"),
                )
                element = dbc.NavItem(element)
            auth_action_elements.append(element)

        # Create user action elements for dropdown
        user_action_elements = []
        for action in user_actions:
            # Special styling for logout button
            if action["id"] == "logout":
                element = dbc.DropdownMenuItem(
                    [
                        html.Span(
                            "⏻", style={"paddingRight": "8px", "fontSize": "12px"}
                        ),
                        html.Span(action["text"]),
                    ],
                    id=self.ids.action_button(aio_id, action["id"]),
                    style={"color": "#ef4444"},
                )
            else:
                # For other actions, create proper dropdown menu items
                if action.get("href"):
                    element = dbc.DropdownMenuItem(
                        action["text"],
                        id=self.ids.action_button(aio_id, action["id"]),
                        href=action["href"],
                        external_link=True,
                    )
                else:
                    element = dbc.DropdownMenuItem(
                        action["text"],
                        id=self.ids.action_button(aio_id, action["id"]),
                    )
            user_action_elements.append(element)

        # Create the layout using proper Bootstrap navbar structure
        super().__init__(
            dbc.Container(
                [
                    # Brand section
                    dbc.NavbarBrand(
                        html.A(
                            brand_text,
                            id=self.ids.brand_link(aio_id),
                            href=brand_href,
                            className="navbar-brand",
                            style={"textDecoration": "none", "color": "inherit"},
                        ),
                    ),
                    # Navbar toggler for mobile
                    dbc.NavbarToggler(id=f"navbar-toggler-{aio_id}"),
                    # Collapsible navbar content
                    dbc.Collapse(
                        [
                            *nav_link_elements,
                            # create a spacer between nav links and auth section
                            html.Div(className="flex-grow-1"),
                            dbc.DropdownMenu(
                                [
                                    dbc.DropdownMenuItem(
                                        [
                                            html.Div(
                                                id=self.ids.user_dropdown_name(aio_id),
                                                className="fw-bold",
                                            ),
                                            html.Div(
                                                id=self.ids.user_dropdown_email(aio_id),
                                                className="text-muted small",
                                            ),
                                        ],
                                        header=True,
                                    ),
                                    dbc.DropdownMenuItem(divider=True),
                                    # Action items
                                    *user_action_elements,
                                ],
                                label=html.Div(
                                    DEFAULT_USERNAME,
                                    id=self.ids.user_dropdown_avatar(aio_id),
                                ),
                                nav=True,
                                in_navbar=True,
                                class_name="hidden-on-logout",
                                align_end=True,
                                toggle_class_name="user-avatar-dropdown-toggle",
                            ),
                            *auth_action_elements,
                        ],
                        navbar=True,
                    ),
                ],
                fluid=fluid,
            ),
            id=self.ids.navbar(aio_id),
            **navbar_props,
        )

    @callback(
        Output(ids.user_dropdown_avatar(MATCH), "children"),
        Output(ids.user_dropdown_name(MATCH), "children"),
        Output(ids.user_dropdown_email(MATCH), "children"),
        Input(AuthStateAIO.ids.state(MATCH), "data"),
        prevent_initial_call=False,
    )
    def update_avatar(auth_data):
        if current_user and current_user.is_authenticated:
            display_name = current_user.get_full_name()
            username = current_user.username
            # Generate user avatar initials
            if display_name:
                name_parts = display_name.strip().split()
                if len(name_parts) >= 2:
                    avatar = f"{name_parts[0][0]}{name_parts[-1][0]}".upper()
                else:
                    avatar = display_name[0].upper() if display_name else "A"
            else:
                avatar = username[0].upper() if username else "A"
            email = current_user.email or f"@{username}"
            return avatar, display_name or username, email
        return "", "", ""

    @callback(
        Output(ids.navbar(MATCH), "class_name"),
        Input(AuthStateAIO.ids.state(MATCH), "data"),
        State(ids.navbar(MATCH), "class_name"),
        prevent_initial_call=False,
    )
    def update_navbar_auth_state(n_clicks, class_name):
        if class_name is None:
            class_name = "navbar-logged-out"
        if current_user and current_user.is_authenticated:
            return class_name.replace("navbar-logged-out", "navbar-logged-in").strip()
        else:
            return class_name.replace("navbar-logged-in", "navbar-logged-out").strip()

    @callback(
        Output(AuthStateAIO.ids.state(MATCH), "data"),
        Input(ids.action_button(MATCH, "logout"), "n_clicks"),
        prevent_initial_call=True,
    )
    def handle_logout(n_clicks):
        if n_clicks and logout_user():
            return False
        return no_update
