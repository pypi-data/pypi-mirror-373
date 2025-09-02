from typing import Final

from airflow.www.utils import UIAlert

DASHBOARD_UIALERTS: Final[list[UIAlert]] = [
    UIAlert("Welcome to Airflow Standalone Mode", category="warning"),
]
STATE_COLORS: Final[dict[str, str]] = {
    "deferred": "#a9a9a9",  # Dark Gray
    "failed": "#c94c4c",  # Muted Red
    "queued": "#d3d3d3",  # Light Gray
    "removed": "#f5f5f5",  # Lighter Gray
    "restarting": "#7f7f7f",  # Medium Gray
    "running": "#5f9ea0",  # Cadet Blue
    "scheduled": "#f0e68c",  # Khaki
    "shutdown": "#696969",  # Dim Gray
    "skipped": "#b0c4de",  # Light Steel Blue
    "success": "#8fbc8f",  # Dark Sea Green
    "up_for_reschedule": "#add8e6",  # Light Blue
    "up_for_retry": "#ffdead",  # Navajo White
    "upstream_failed": "#ffa07a",  # Light Salmon
}
