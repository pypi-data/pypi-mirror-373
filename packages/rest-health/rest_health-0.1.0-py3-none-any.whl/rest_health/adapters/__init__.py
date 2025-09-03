"""Framework adapters for rest-health."""

# Import adapters conditionally to avoid requiring dependencies
try:
    from .fastapi import create_fastapi_healthcheck

    __all__ = ["create_fastapi_healthcheck"]
except ImportError:
    __all__ = []

try:
    from .flask import create_flask_healthcheck

    __all__.append("create_flask_healthcheck")
except ImportError:
    pass
