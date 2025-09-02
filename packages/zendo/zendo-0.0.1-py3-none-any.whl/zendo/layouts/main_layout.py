from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, ClassVar, Type, TypedDict
import uuid

import dash
from dash import (
    MATCH,
    ClientsideFunction,
    Input,
    Output,
    State,
    callback,
    clientside_callback,
    dcc,
    html,
)

from zendo import auth
from zendo.services.applet_state import (
    create_applet,
    get_applet,
    list_applets,
    update_applet,
)


@dataclass
class Applet:
    name: ClassVar[str]
    description: ClassVar[str | None] = None
    aliases: ClassVar[list[str] | None] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    class ids:
        @staticmethod
        def state(aio_id: str) -> dict:
            return {
                "component": "Applet",
                "subcomponent": "state",
                "aio_id": aio_id,
            }

        @staticmethod
        def container(aio_id: str) -> dict:
            return {
                "component": "Applet",
                "subcomponent": "container",
                "aio_id": aio_id,
            }

    def render(self, aio_id: str) -> html.Div:
        return html.Div(
            [
                dcc.Store(id=Applet.ids.state(aio_id), data={}),
                self.layout(),
            ],
            id=Applet.ids.container(aio_id),
        )

    def init_state(self) -> dict[str, Any]:
        """Initialize the state for the applet."""
        return {}

    def process(
        self, input: str, state: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        raise NotImplementedError("Applet must implement process method.")

    def layout(self) -> html.Div:
        raise NotImplementedError("Applet must implement layout method.")


class ChatHistory(Applet):
    name: ClassVar[str] = "chat_history"
    description: ClassVar[str] = "Displays the chat history."
    aliases: ClassVar[list[str]] = ["history", "chats"]

    def process(
        self, input: str, state: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        history: list = (state or {}).get("history", [])
        history.append(input)
        state["history"] = history
        return state

    def layout(self) -> html.Div:
        return html.Div(
            [
                html.P("Chat History Applet"),
                html.P(id=self.id),
            ]
        )


class AppletRegistry(Mapping[str, Type[Applet]]):
    def __init__(self):
        self._applets = {}
        self._aliases = {}
        # add default applets
        self.register(ChatHistory)

    def __getitem__(self, key: str) -> Type[Applet]:
        return self._applets[self._aliases.get(key, key)]

    def __iter__(self):
        return iter(self._applets)

    def __len__(self) -> int:
        return len(self._applets)

    def register(self, applet: Type[Applet]):
        self._applets[applet.name] = applet
        for alias in applet.aliases or []:
            self._aliases[alias] = applet.name


class AppStateDict(TypedDict):
    mode: str
    current_applet: str | None


class MainLayout(html.Div):
    class ids:
        @staticmethod
        def state(aio_id: str) -> dict:
            return {
                "component": "MainLayout",
                "subcomponent": "state",
                "aio_id": aio_id,
            }

        @staticmethod
        def content(aio_id: str) -> dict:
            return {
                "component": "MainLayout",
                "subcomponent": "content",
                "aio_id": aio_id,
            }

        @staticmethod
        def input_textarea(aio_id: str) -> dict:
            return {
                "component": "MainLayout",
                "subcomponent": "input_textarea",
                "aio_id": aio_id,
            }

        @staticmethod
        def send_button(aio_id: str) -> dict:
            return {
                "component": "MainLayout",
                "subcomponent": "send_button",
                "aio_id": aio_id,
            }

        @staticmethod
        def cmd_enter_trigger(aio_id: str) -> dict:
            return {
                "component": "MainLayout",
                "subcomponent": "cmd_enter_trigger",
                "aio_id": aio_id,
            }

    ids = ids

    applets: ClassVar[AppletRegistry] = AppletRegistry()

    def __init__(self, aio_id: str):
        super().__init__(
            [
                # Store for app state (chat is default, timer can be opened)
                dcc.Store(
                    id=self.ids.state(aio_id),
                    data={"mode": "chat", "history": []},
                ),
                # content area
                html.Div(
                    id=self.ids.content(aio_id),
                    style={
                        "flex": "1",
                        "overflow": "hidden",
                        "background": "#ffffff",
                    },
                ),
                # Generic input area
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    dcc.Textarea(
                                        id=self.ids.input_textarea(aio_id),
                                        placeholder="Type a message or command...",
                                        rows=1,
                                        style={
                                            "width": "100%",
                                            "border": "1px solid #ccc",
                                            "borderRadius": "6px",
                                            "resize": "none",
                                            "fontSize": "14px",
                                            "maxHeight": "8rem",
                                            "overflowY": "hidden",
                                        },
                                        className="left-scroll",
                                    ),
                                    className="grow-wrap",
                                    style={
                                        "maxHeight": "8rem",
                                        "overflowY": "hidden",
                                    },
                                ),
                                html.Button(
                                    "↑",
                                    id=self.ids.send_button(aio_id),
                                    n_clicks=0,
                                    style={
                                        "position": "absolute",
                                        "right": "8px",
                                        "bottom": "8px",
                                        "background": "#374151",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "6px",
                                        "width": "28px",
                                        "height": "28px",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "cursor": "pointer",
                                        "fontSize": "14px",
                                        "fontWeight": "bold",
                                    },
                                ),
                            ],
                            style={
                                "position": "relative",
                                "maxWidth": "48rem",
                                "margin": "0 auto",
                            },
                        )
                    ],
                    style={
                        "padding": "1rem",
                        "background": "#ffffff",
                    },
                ),
                # Hidden div to trigger send on Cmd+Enter
                dcc.Store(id=self.ids.cmd_enter_trigger(aio_id), data=0),
            ],
            style={
                "height": "calc(100vh - 62px)",  # Account for navbar height
                "display": "flex",
                "flexDirection": "column",
                "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
                "background": "#ffffff",
            },
        )

    # Callback to clear input field when message is sent
    @callback(
        Output(ids.input_textarea(MATCH), "value"),
        Input(ids.send_button(MATCH), "n_clicks"),
        State(ids.input_textarea(MATCH), "value"),
        prevent_initial_call=True,
    )
    def clear_input_on_send(send_clicks: int | None, message: str):
        if not send_clicks:
            return dash.no_update
        if message and message.strip():
            return ""
        return dash.no_update

    clientside_callback(
        ClientsideFunction(namespace="mainLayout", function_name="inputUpdate"),
        Output(ids.cmd_enter_trigger(MATCH), "data"),
        Input(ids.input_textarea(MATCH), "value"),
        Input(ids.input_textarea(MATCH), "id"),
        State(ids.send_button(MATCH), "id"),
        State(ids.cmd_enter_trigger(MATCH), "data"),
        prevent_initial_call=False,
    )

    @callback(
        Output(ids.content(MATCH), "children"),
        Input(ids.state(MATCH), "data"),
    )
    def update_current_content(app_state: AppStateDict):
        history = app_state.get("history", [])
        if not history:
            # If no history, return an empty div
            chats_div = html.Div(
                "No messages yet. Start chatting!",
                style={"padding": "1rem", "textAlign": "center"},
            )
        if app_state["mode"] == "chat":
            # Render chat history
            chats_div = html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                f"{msg['role']}: {msg['content']}",
                                className="chat-message",
                                style={
                                    "marginBottom": "0.5rem",
                                    "padding": "0.5rem",
                                    "borderRadius": "8px",
                                    "backgroundColor": "#f1f1f1",
                                },
                            )
                            for msg in history
                        ],
                        style={
                            "padding": "1rem",
                            "overflowY": "auto",
                            "height": "calc(100vh - 150px)",
                        },
                    )
                ],
                style={"padding": "1rem"},
            )
        return chats_div

    # Callback to handle input from the message input field
    @callback(
        Output(ids.state(MATCH), "data"),
        Input(ids.send_button(MATCH), "n_clicks"),
        State(ids.input_textarea(MATCH), "value"),
        State(ids.state(MATCH), "data"),
        prevent_initial_call=True,
    )
    def process_input_and_update_state(
        send_clicks: int | None, message: str, app_state: AppStateDict
    ):
        current_user = auth.current_user

        # Check authentication
        if not current_user or not current_user.is_authenticated:
            return dash.no_update

        message = message.strip() if message else ""

        if not message or message == "":
            return dash.no_update

        history: list = app_state.setdefault("history", [])

        history.append(
            {
                "role": "user",
                "content": message,
                "user": current_user.username,
            }
        )

        if message.startswith("/"):
            cmd = list(map(str.strip, message[1:].strip().split(" ")))
            if cmd[0] == "help":
                history.append(
                    {
                        "role": "system",
                        "content": "Available commands: /help, /avail, /new <applet_name>, /list, /state, /switch <applet_id>, /send <message>",
                    }
                )
            elif cmd[0] == "avail":
                history.append(
                    {
                        "role": "system",
                        "content": "Available applets: "
                        + ", ".join(MainLayout.applets.keys()),
                    }
                )
            elif cmd[0] == "new":
                applet_name = cmd[1]
                applet_class = MainLayout.applets.get(applet_name)
                success, msg, applet_state = False, "Applet not found.", None
                if applet_class:
                    applet = applet_class()
                    success, msg, applet_state = create_applet(
                        id=applet.id,
                        user_id=current_user.id,
                        applet_name=applet_name,
                        state_data=applet.init_state(),
                    )
                    app_state["current_applet"] = applet_state.id
                if success:
                    history.append(
                        {
                            "role": "system",
                            "content": f"Created and switched to applet: {applet_name} of type {applet_class}.",
                        }
                    )
                else:
                    history.append(
                        {
                            "role": "system",
                            "content": f"Error creating applet: {msg}",
                        }
                    )
            elif cmd[0] == "list":
                applets_list = []
                success, msg, applets = list_applets(user_id=current_user.id)
                for applet in applets:
                    applets_list.append(f"{applet.applet_name}({applet.id})")
                history.append(
                    {
                        "role": "system",
                        "content": "Current applets: " + ", ".join(applets_list)
                        if applets_list
                        else "No applets available.",
                    }
                )
            elif cmd[0] == "state":
                applet_id = app_state.get("current_applet")
                if applet_id:
                    success, msg, applet_state = get_applet(
                        user_id=current_user.id, applet_id=applet_id
                    )
                    if success:
                        history.append(
                            {
                                "role": "system",
                                "content": f"Applet state for {applet_state.applet_name} ({applet_id}): {applet_state.state_data}",
                            }
                        )
                    else:
                        history.append(
                            {
                                "role": "system",
                                "content": f"Error retrieving applet state: {msg}",
                            }
                        )
                else:
                    history.append(
                        {
                            "role": "system",
                            "content": "No current applet to show state.",
                        }
                    )
            elif cmd[0] == "switch":
                if len(cmd) < 2:
                    history.append(
                        {
                            "role": "system",
                            "content": "Usage: /switch <applet_id>",
                        }
                    )
                else:
                    applet_id = cmd[1]
                    success, msg, applet_state = get_applet(
                        user_id=current_user.id, applet_id=applet_id
                    )
                    if success:
                        app_state["current_applet"] = applet_state.id
                        history.append(
                            {
                                "role": "system",
                                "content": f"Switched to applet: {applet_state.applet_name} ({applet_id})",
                            }
                        )
                    else:
                        history.append(
                            {
                                "role": "system",
                                "content": f"Error switching to applet: {msg}",
                            }
                        )
            elif cmd[0] == "send":
                applet_id = app_state.get("current_applet")
                if applet_id:
                    success, msg, applet_state = get_applet(
                        user_id=current_user.id, applet_id=applet_id
                    )
                    if success:
                        applet_class = MainLayout.applets.get(applet_state.applet_name)
                        if applet_class:
                            try:
                                real_message = message[len(cmd[0]) + 1 :].strip()
                                applet = applet_class(id=applet_id)
                                new_state = applet.process(
                                    real_message, applet_state.state_data
                                )
                                print("New state:", new_state)
                                success, msg, _ = update_applet(
                                    user_id=current_user.id,
                                    applet_id=applet_id,
                                    state_data=new_state,
                                )
                                if success:
                                    history.append(
                                        {
                                            "role": "system",
                                            "content": f"Message sent to applet {applet_state.applet_name}: {real_message}",
                                        }
                                    )
                                else:
                                    history.append(
                                        {
                                            "role": "system",
                                            "content": f"Error updating applet state: {msg}",
                                        }
                                    )
                            except Exception as e:
                                history.append(
                                    {
                                        "role": "system",
                                        "content": str(e),
                                    }
                                )
                        else:
                            history.append(
                                {
                                    "role": "system",
                                    "content": f"Applet {applet_state.applet_name} not found.",
                                }
                            )
                    else:
                        history.append(
                            {
                                "role": "system",
                                "content": f"Error retrieving applet: {msg}",
                            }
                        )
                else:
                    history.append(
                        {
                            "role": "system",
                            "content": "No current applet to send message to.",
                        }
                    )
        else:
            # Regular message, add to history
            history.append(
                {
                    "role": "assistant",
                    "content": "You said: " + message,
                }
            )

        app_state["history"] = history

        return app_state
