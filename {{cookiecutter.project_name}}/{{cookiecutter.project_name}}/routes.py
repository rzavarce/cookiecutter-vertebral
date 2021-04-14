"""Route-related configuration."""
# INTERNAL CORE HANDLERS
from core.auth import SignOnHandler
from core.websocktes import WebSocketsHandler

# YOUR OWN HANDLERS
from .handlers.status import StatusHandler, test_handler
from .handlers.monitor import MonitorHandler


EXCLUDED_ROUTES = ['/{{cookiecutter.project_name}}/api/v1/signon', ]


def setup_routes():
    """
    Register existing routes in the app instance.

    :params: application instance
    """

    return [
            ["post", "ws", WebSocketsHandler],
            ["post", "signon", SignOnHandler],
            ["get", "status", StatusHandler],
            ["post", "monitor", MonitorHandler],
            ["post", "test", test_handler],
        ]


