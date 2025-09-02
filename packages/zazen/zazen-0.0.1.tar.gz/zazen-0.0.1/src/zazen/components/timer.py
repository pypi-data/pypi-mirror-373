"""
Timer component for App.

This module provides a Dash-based timer component that can replace the chat interface.
"""

from dash import html, dcc, Input, Output, State, callback, clientside_callback


def create_timer_layout(timer_config):
    """
    Create the timer applet layout.

    Parameters
    ----------
    timer_config : dict
        Timer configuration containing mode and duration.

    Returns
    -------
    html.Div
        The timer interface component.
    """
    mode = timer_config.get("mode", "stopwatch")
    duration = timer_config.get("duration", 0)

    if mode == "countdown":
        title = "Countdown Timer"
        initial_minutes = duration // 60
        initial_seconds = duration % 60
        initial_display = f"{initial_minutes}:{initial_seconds:02d}"
    else:
        title = "Stopwatch"
        initial_display = "0:00"

    return html.Div(
        [
            # Timer state stores
            dcc.Store(
                id="timer-state",
                data={
                    "mode": mode,
                    "duration": duration,
                    "current_time": duration if mode == "countdown" else 0,
                    "is_running": False,
                    "is_paused": False,
                },
            ),
            dcc.Store(id="timer-display-store", data=initial_display),
            # Timer interface
            html.Div(
                [
                    # Clean header
                    html.Div(
                        [
                            html.H3(
                                title,
                                style={
                                    "margin": "0",
                                    "color": "#1f2937",
                                    "fontWeight": "500",
                                    "fontSize": "1.25rem",
                                    "textAlign": "center",
                                },
                            )
                        ],
                        style={
                            "padding": "1.5rem 2rem 1rem 2rem",
                            "background": "#ffffff",
                            "borderBottom": "1px solid #f3f4f6",
                        },
                    ),
                    # Timer content
                    html.Div(
                        [
                            # Timer display
                            html.Div(
                                id="timer-display",
                                children=initial_display,
                                style={
                                    "fontSize": "4rem",
                                    "fontWeight": "300",
                                    "marginBottom": "2rem",
                                    "fontFamily": "'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace",
                                    "minWidth": "200px",
                                    "textAlign": "center",
                                    "color": "#1f2937",
                                    "letterSpacing": "0.05em",
                                },
                            ),
                            # Control buttons
                            html.Div(
                                [
                                    html.Button(
                                        "Start",
                                        id="timer-start-btn",
                                        style={
                                            "background": "#374151",
                                            "color": "white",
                                            "border": "none",
                                            "borderRadius": "8px",
                                            "padding": "12px 24px",
                                            "fontSize": "14px",
                                            "fontWeight": "500",
                                            "cursor": "pointer",
                                            "marginRight": "8px",
                                            "minHeight": "44px",
                                            "transition": "background-color 0.2s ease",
                                        },
                                    ),
                                    html.Button(
                                        "Pause",
                                        id="timer-pause-btn",
                                        style={
                                            "background": "#6b7280",
                                            "color": "white",
                                            "border": "none",
                                            "borderRadius": "8px",
                                            "padding": "12px 24px",
                                            "fontSize": "14px",
                                            "fontWeight": "500",
                                            "cursor": "pointer",
                                            "marginRight": "8px",
                                            "minHeight": "44px",
                                            "transition": "background-color 0.2s ease",
                                        },
                                    ),
                                    html.Button(
                                        "Reset",
                                        id="timer-reset-btn",
                                        style={
                                            "background": "#ffffff",
                                            "color": "#374151",
                                            "border": "1px solid #d1d5db",
                                            "borderRadius": "8px",
                                            "padding": "12px 24px",
                                            "fontSize": "14px",
                                            "fontWeight": "500",
                                            "cursor": "pointer",
                                            "marginRight": "8px",
                                            "minHeight": "44px",
                                            "transition": "all 0.2s ease",
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "center",
                                    "marginBottom": "2rem",
                                    "flexWrap": "wrap",
                                    "gap": "8px",
                                },
                            ),
                            # Close button
                            html.Div(
                                [
                                    html.Button(
                                        "Close Timer",
                                        id="timer-close-btn",
                                        style={
                                            "background": "#ffffff",
                                            "color": "#6b7280",
                                            "border": "1px solid #e5e7eb",
                                            "borderRadius": "8px",
                                            "padding": "8px 16px",
                                            "fontSize": "14px",
                                            "fontWeight": "500",
                                            "cursor": "pointer",
                                            "transition": "all 0.2s ease",
                                        },
                                    )
                                ],
                                style={"textAlign": "center"},
                            ),
                            # Interval component for timer updates
                            dcc.Interval(
                                id="timer-interval",
                                interval=1000,  # Update every second
                                n_intervals=0,
                                disabled=True,
                            ),
                        ],
                        style={
                            "padding": "2rem",
                            "background": "#ffffff",
                            "display": "flex",
                            "flexDirection": "column",
                            "alignItems": "center",
                            "justifyContent": "center",
                        },
                    ),
                ],
                style={
                    "maxWidth": "500px",
                    "margin": "2rem auto",
                    "background": "#ffffff",
                    "border": "1px solid #e5e7eb",
                    "borderRadius": "12px",
                    "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
                    "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
                },
            ),
        ],
        style={
            "height": "100%",
            "display": "flex",
            "flexDirection": "column",
            "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
            "background": "#ffffff",
        },
    )


# Timer control callbacks
@callback(
    [
        Output("timer-state", "data"),
        Output("timer-interval", "disabled"),
        Output("timer-start-btn", "children"),
        Output("timer-start-btn", "disabled"),
    ],
    [
        Input("timer-start-btn", "n_clicks"),
        Input("timer-pause-btn", "n_clicks"),
        Input("timer-reset-btn", "n_clicks"),
    ],
    [State("timer-state", "data")],
    prevent_initial_call=True,
)
def control_timer(start_clicks, pause_clicks, reset_clicks, timer_state):
    """
    Control timer start, pause, and reset functionality.

    Parameters
    ----------
    start_clicks : int
        Number of start button clicks.
    pause_clicks : int
        Number of pause button clicks.
    reset_clicks : int
        Number of reset button clicks.
    timer_state : dict
        Current timer state.

    Returns
    -------
    tuple
        Updated timer state, interval disabled status, button text, and button disabled status.
    """
    import dash

    ctx = dash.callback_context

    if not ctx.triggered:
        return timer_state, True, "Start", False

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "timer-start-btn":
        if not timer_state["is_running"]:
            # Start the timer
            timer_state["is_running"] = True
            timer_state["is_paused"] = False
            return timer_state, False, "Running...", True

    elif button_id == "timer-pause-btn":
        if timer_state["is_running"]:
            # Pause the timer
            timer_state["is_running"] = False
            timer_state["is_paused"] = True
            return timer_state, True, "Resume", False

    elif button_id == "timer-reset-btn":
        # Reset the timer
        initial_time = (
            timer_state["duration"] if timer_state["mode"] == "countdown" else 0
        )
        timer_state["current_time"] = initial_time
        timer_state["is_running"] = False
        timer_state["is_paused"] = False
        return timer_state, True, "Start", False

    return timer_state, True, "Start", False


@callback(
    [
        Output("timer-state", "data", allow_duplicate=True),
        Output("timer-display", "children"),
        Output("timer-display", "style"),
    ],
    [Input("timer-interval", "n_intervals")],
    [State("timer-state", "data")],
    prevent_initial_call=True,
)
def update_timer_display(n_intervals, timer_state):
    """
    Update the timer display every second.

    Parameters
    ----------
    n_intervals : int
        Number of interval triggers.
    timer_state : dict
        Current timer state.

    Returns
    -------
    tuple
        Updated timer state, display text, and display style.
    """
    if not timer_state["is_running"]:
        # Format current time for display
        current_time = timer_state["current_time"]
        minutes = abs(current_time) // 60
        seconds = abs(current_time) % 60
        sign = "-" if current_time < 0 else ""
        display_text = f"{sign}{minutes}:{seconds:02d}"

        # Change color if countdown is negative
        display_style = {
            "fontSize": "4rem",
            "fontWeight": "300",
            "marginBottom": "2rem",
            "fontFamily": "'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace",
            "minWidth": "200px",
            "textAlign": "center",
            "color": "#ef4444"
            if timer_state["mode"] == "countdown" and current_time <= 0
            else "#1f2937",
            "letterSpacing": "0.05em",
        }

        return timer_state, display_text, display_style

    # Update timer
    if timer_state["mode"] == "countdown":
        timer_state["current_time"] -= 1
    else:
        timer_state["current_time"] += 1

    # Format time for display
    current_time = timer_state["current_time"]
    minutes = abs(current_time) // 60
    seconds = abs(current_time) % 60
    sign = "-" if current_time < 0 else ""
    display_text = f"{sign}{minutes}:{seconds:02d}"

    # Change color if countdown reaches zero or goes negative
    display_style = {
        "fontSize": "4rem",
        "fontWeight": "300",
        "marginBottom": "2rem",
        "fontFamily": "'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace",
        "minWidth": "200px",
        "textAlign": "center",
        "color": "#ef4444"
        if timer_state["mode"] == "countdown" and current_time <= 0
        else "#1f2937",
        "letterSpacing": "0.05em",
    }

    return timer_state, display_text, display_style


# Client-side callback for sound notification when countdown reaches zero
clientside_callback(
    """
    function(timer_state) {
        if (timer_state && timer_state.mode === 'countdown' && 
            timer_state.current_time === 0 && timer_state.is_running) {
            // Play a simple beep sound
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.value = 800;
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.5);
            } catch (e) {
                console.log('Audio notification not available');
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("timer-display", "id"),
    Input("timer-state", "data"),
)
