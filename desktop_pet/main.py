"""Entry point for the Lorito desktop pet application."""

import sys

from PyQt6.QtWidgets import QApplication

from pet_window import DesktopPet


def main() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    pet = DesktopPet()
    pet.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
