"""Entry point for the Whack-A-Mole Pygame application."""

from game.app import GameApp


def main() -> None:
    """Create the game window and start the main loop."""
    app = GameApp()
    app.run()


if __name__ == "__main__":
    main()
