"""Entry point for running MyClip as a module."""

from .app import App


def main() -> None:
    """Main entry point."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
