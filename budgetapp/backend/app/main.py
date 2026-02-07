"""Application entrypoint for FastAPI."""

from .core.container import Container


# Build a single app instance for ASGI servers.
container = Container()
app = container.create_app()
