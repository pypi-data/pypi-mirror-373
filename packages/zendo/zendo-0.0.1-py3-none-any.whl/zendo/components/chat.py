"""
Chat component for App.

This module provides a chat interface component that can handle
both commands and regular text input.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from dash import Input, Output, callback, dcc, html, MATCH


__all__ = ["ChatHistoryAIO"]


class ChatHistoryAIO(html.Div):
    class ids:
        def messages(aio_id: str) -> str:
            return {
                "component": "ChatHistoryAIO",
                "subcomponent": "messages",
                "id": aio_id,
            }

        def store(aio_id: str) -> str:
            return {
                "component": "ChatHistoryAIO",
                "subcomponent": "store",
                "id": aio_id,
            }

    ids = ids

    def __init__(self, aio_id: str, data: list[dict[str, Any]] | None = None):
        """
        Create the chat applet layout.

        Parameters
        ----------
        data : list[dict[str, Any]], optional
            Initial chat history to display, by default None.

        Returns
        -------
        html.Div
            The chat applet component.
        """
        if not data:
            data = []

        super().__init__(
            [
                # Chat messages area
                html.Div(
                    id=self.ids.messages(aio_id),
                    children=[
                        create_message_bubble(
                            "Hello! How can I help you today? You can type messages or use commands like /time, /calc, /timer, etc.",
                            sender="assistant",
                            timestamp="Now",
                        )
                    ],
                    style={
                        "flex": "1",
                        "overflow-y": "auto",
                        "background": "#ffffff",
                        "padding": "0",
                        "display": "flex",
                        "flex-direction": "column-reverse",
                    },
                ),
                # Chat history store
                dcc.Store(
                    id=self.ids.store(aio_id),
                    data=data,
                ),
            ],
            style={
                "height": "100%",
                "display": "flex",
                "flex-direction": "column",
                "background": "#ffffff",
            },
        )

    @callback(
        Output(ids.messages(MATCH), "children"),
        Input(ids.store(MATCH), "data"),
        prevent_initial_call=False,
    )
    def update_chat_messages(chat_history):
        """
        Update the chat messages display based on chat history.

        Parameters
        ----------
        chat_history : list
            Current chat history.

        Returns
        -------
        list
            Updated message components.
        """
        if not chat_history:
            return [
                create_message_bubble(
                    "Hello! How can I help you today? You can type messages.",
                    sender="assistant",
                    timestamp="Now",
                )
            ]

        # Create message bubbles (reversed order for column-reverse layout)
        message_components = []

        for msg in reversed(chat_history):
            bubble = create_message_bubble(
                msg["message"], msg["sender"], msg["timestamp"]
            )

            message_components.append(bubble)

        return message_components


def create_message_bubble(
    message: str,
    sender: str | None = "user",
    timestamp: datetime | None = None,
):
    """
    Create a message bubble component.

    Parameters
    ----------
    message : str
        The message content.
    sender : str, optional
        The sender type ('user' or 'assistant'), by default "user".
    timestamp : str, optional
        The message timestamp, by default None.

    Returns
    -------
    html.Div
        A div component containing the styled message bubble.
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M")

    is_user = sender == "user"

    # Minimal message container
    return html.Div(
        [
            html.Div(
                [
                    # Simple avatar
                    html.Div(
                        "U" if is_user else "A",
                        style={
                            "width": "28px",
                            "height": "28px",
                            "border-radius": "50%",
                            "background": "#6b7280" if is_user else "#374151",
                            "color": "white",
                            "display": "flex",
                            "align-items": "center",
                            "justify-content": "center",
                            "font-size": "12px",
                            "font-weight": "500",
                            "flex-shrink": "0",
                        },
                    ),
                    # Message content
                    html.Div(
                        [
                            html.Div(
                                message,
                                style={
                                    "color": "#1f2937",
                                    "font-size": "14px",
                                    "line-height": "1.5",
                                    "white-space": "pre-wrap",
                                    "word-wrap": "break-word",
                                },
                            ),
                            html.Div(
                                timestamp,
                                style={
                                    "color": "#9ca3af",
                                    "font-size": "11px",
                                    "margin-top": "4px",
                                },
                            ),
                        ],
                        style={
                            "margin-left": "12px",
                            "flex": "1",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "align-items": "flex-start",
                    "max-width": "48rem",
                    "margin": "0 auto",
                    "padding": "1rem",
                },
            )
        ],
        style={
            "background": "#f9fafb" if not is_user else "#ffffff",
            "borderBottom": "1px solid #f3f4f6" if not is_user else "none",
        },
    )
