import rich.traceback

from .pacs_app import PacsApp


def main() -> None:
    rich.traceback.install(width=200)
    PacsApp().run()


if __name__ == "__main__":
    main()
