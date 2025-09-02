"""
AIO Components - All-in-One authentication components.

This module provides reusable All-in-One (AIO) components for user authentication
including registration and login forms with built-in validation and callbacks.
"""

import re
import uuid

from dash import MATCH, Input, Output, State, callback, dcc, html, no_update
import dash_bootstrap_components as dbc

from ..auth import register_user

EMAIL_REGEX_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
EMAIL_REGEX_PATTERN_ERROR = "Invalid email format. Please enter a valid email address."
USERNAME_REGEX_PATTERN = r"^[a-zA-Z0-9_-]{3,20}$"
USERNAME_REGEX_PATTERN_ERROR = (
    "Username must be 3-20 characters long and can only contain letters, "
    "numbers, underscores, and hyphens."
)
PASSWORD_MISMATCH_ERROR = "Passwords do not match. Please try again."
PASSWORD_LENGTH_ERROR = "Password must be at least 6 characters long."


class RegisterUserAIO(dbc.Card):
    class ids:
        @staticmethod
        def form(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "form",
                "aio_id": aio_id,
            }

        @staticmethod
        def username_input(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "username_input",
                "aio_id": aio_id,
            }

        @staticmethod
        def email_input(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "email_input",
                "aio_id": aio_id,
            }

        @staticmethod
        def password_input(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "password_input",
                "aio_id": aio_id,
            }

        @staticmethod
        def confirm_password_input(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "confirm_password_input",
                "aio_id": aio_id,
            }

        @staticmethod
        def first_name_input(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "first_name_input",
                "aio_id": aio_id,
            }

        @staticmethod
        def last_name_input(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "last_name_input",
                "aio_id": aio_id,
            }

        @staticmethod
        def submit_button(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "submit_button",
                "aio_id": aio_id,
            }

        @staticmethod
        def alert(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "alert",
                "aio_id": aio_id,
            }

        @staticmethod
        def store(aio_id):
            return {
                "component": "RegisterUserAIO",
                "subcomponent": "store",
                "aio_id": aio_id,
            }

    ids = ids

    def __init__(
        self,
        aio_id=None,
        form_props=None,
        card_props=None,
        title="Register",
        show_name_fields=True,
        submit_button_text="Register",
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        # Merge user-supplied properties with defaults
        form_props = form_props if form_props else {}
        card_props = card_props if card_props else {}

        # Build form fields with clean styling
        form_fields = [
            html.Div(
                [
                    dbc.Label("Username", html_for=self.ids.username_input(aio_id)),
                    dbc.Input(
                        id=self.ids.username_input(aio_id),
                        type="text",
                        placeholder="Enter username",
                    ),
                ],
            ),
            html.Div(
                [
                    dbc.Label(
                        "Email",
                        html_for=self.ids.email_input(aio_id),
                    ),
                    dbc.Input(
                        id=self.ids.email_input(aio_id),
                        type="email",
                        placeholder="Enter email",
                    ),
                ],
            ),
        ]

        # Add name fields if requested
        if show_name_fields:
            form_fields.extend(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label(
                                        "First Name",
                                        html_for=self.ids.first_name_input(aio_id),
                                    ),
                                    dbc.Input(
                                        id=self.ids.first_name_input(aio_id),
                                        type="text",
                                        placeholder="Enter first name",
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label(
                                        "Last Name",
                                        html_for=self.ids.last_name_input(aio_id),
                                    ),
                                    dbc.Input(
                                        id=self.ids.last_name_input(aio_id),
                                        type="text",
                                        placeholder="Enter last name",
                                    ),
                                ],
                                width=6,
                            ),
                        ],
                    ),
                ]
            )

        # Add password fields
        form_fields.extend(
            [
                html.Div(
                    [
                        dbc.Label(
                            "Password",
                            html_for=self.ids.password_input(aio_id),
                        ),
                        dbc.Input(
                            id=self.ids.password_input(aio_id),
                            type="password",
                            placeholder="Enter password",
                        ),
                    ],
                ),
                html.Div(
                    [
                        dbc.Label(
                            "Confirm Password",
                            html_for=self.ids.confirm_password_input(aio_id),
                        ),
                        dbc.Input(
                            id=self.ids.confirm_password_input(aio_id),
                            type="password",
                            placeholder="Confirm password",
                        ),
                    ],
                ),
            ]
        )
        super().__init__(
            [
                # Clean header
                dbc.CardHeader(title),
                # Form content
                dbc.CardBody(
                    [
                        # Alert
                        html.Div(
                            id=self.ids.alert(aio_id),
                            style={"display": "none"},
                        ),
                        # Form
                        html.Div(
                            form_fields,
                            id=self.ids.form(aio_id),
                            **form_props,
                        ),
                        dcc.Store(
                            id=self.ids.store(aio_id),
                            data={"show_name_fields": show_name_fields},
                        ),
                    ],
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
        [
            Output(ids.alert(MATCH), "children"),
            Output(ids.alert(MATCH), "style"),
            Output(ids.username_input(MATCH), "value"),
            Output(ids.email_input(MATCH), "value"),
            Output(ids.password_input(MATCH), "value"),
            Output(ids.confirm_password_input(MATCH), "value"),
            Output(ids.first_name_input(MATCH), "value"),
            Output(ids.last_name_input(MATCH), "value"),
        ],
        Input(ids.submit_button(MATCH), "n_clicks"),
        [
            State(ids.username_input(MATCH), "value"),
            State(ids.email_input(MATCH), "value"),
            State(ids.password_input(MATCH), "value"),
            State(ids.confirm_password_input(MATCH), "value"),
            State(ids.first_name_input(MATCH), "value"),
            State(ids.last_name_input(MATCH), "value"),
            State(ids.store(MATCH), "data"),
        ],
        prevent_initial_call=True,
    )
    def handle_registration(
        n_clicks,
        username,
        email,
        password,
        confirm_password,
        first_name,
        last_name,
        store_data,
    ):
        """
        Handle user registration form submission.

        Parameters
        ----------
        n_clicks : int
            Number of times submit button was clicked.
        username : str
            Username input value.
        email : str
            Email input value.
        password : str
            Password input value.
        confirm_password : str
            Confirm password input value.
        first_name : str
            First name input value.
        last_name : str
            Last name input value.
        store_data : dict
            Component configuration data.

        Returns
        -------
        tuple
            Alert message, style, and cleared form values.
        """
        if not n_clicks:
            return no_update

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

        # Validation
        if not username or not email or not password:
            return (
                "Please fill in all required fields.",
                create_alert_style(True),
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # user name should be alphanumeric and can include underscores and hyphens
        if not re.match(USERNAME_REGEX_PATTERN, username):
            return (
                USERNAME_REGEX_PATTERN_ERROR,
                create_alert_style(True),
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )

        # validate email format using regex
        if not re.match(EMAIL_REGEX_PATTERN, email):
            return (
                EMAIL_REGEX_PATTERN_ERROR,
                create_alert_style(True),
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        if password != confirm_password:
            return (
                PASSWORD_MISMATCH_ERROR,
                create_alert_style(True),
                no_update,
                no_update,
                "",
                "",
                no_update,
                no_update,
            )

        if len(password) < 6:
            return (
                PASSWORD_LENGTH_ERROR,
                create_alert_style(True),
                no_update,
                no_update,
                "",
                "",
                no_update,
                no_update,
            )

        # Attempt registration
        success, message, user = register_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name if first_name else None,
            last_name=last_name if last_name else None,
        )

        if success:
            # Clear form on success
            return (
                message,
                create_alert_style(False),
                "",
                "",
                "",
                "",
                "",
                "",
            )
        else:
            return (
                message,
                create_alert_style(True),
                no_update,
                no_update,
                "",
                "",
                no_update,
                no_update,
            )
