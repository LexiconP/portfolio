from .core.container import Container


container = Container()
app = container.create_app()


if __name__ == "__main__":
    app = container.create_app()
