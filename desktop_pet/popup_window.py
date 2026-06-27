"""Frameless speech-bubble popup for typing to the desktop pet."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class InteractionPopup(QDialog):
    """A small frameless dialog with a text input and speech bubble.

    Appears 60 px above the pet's current position.  When the user presses
    Enter the text is shown in a speech-bubble label; after a fixed timeout
    the dialog closes and the pet returns to IDLE.
    """

    def __init__(self, pet: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pet = pet
        self._talk_timer: QTimer | None = None

        self._setup_ui()
        self._position_above_pet()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(
            """
            InteractionPopup {
                background: #1a1a1a;
                border: 2px solid #00ff00;
                border-radius: 6px;
            }
            QLineEdit {
                background: #1a1a1a;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 13px;
                border: none;
                padding: 6px;
            }
            QLabel#speech {
                background: #1a1a1a;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 13px;
                border: 2px solid #00ff00;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton {
                background: #1a1a1a;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 13px;
                border: 1px solid #00ff00;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background: #00ff00;
                color: #1a1a1a;
            }
            """
        )

        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setBlurRadius(12)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(  # type: ignore[call-arg]
            __import__("PyQt6.QtGui", fromlist=["QColor"]).QColor(0, 0, 0, 160)
        )
        self.setGraphicsEffect(self._shadow)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Escribele al lorito...")
        self._input.returnPressed.connect(self._on_enter_pressed)

        self._speech_label = QLabel()
        self._speech_label.setObjectName("speech")
        self._speech_label.setWordWrap(True)
        self._speech_label.setVisible(False)
        self._speech_label.setFixedWidth(220)

        self._send_btn = QPushButton("Enviar")
        self._send_btn.clicked.connect(self._on_enter_pressed)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.addWidget(self._input)
        input_row.addWidget(self._send_btn)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)
        root.addLayout(input_row)
        root.addWidget(self._speech_label)

        self.setFixedWidth(300)

    def _position_above_pet(self) -> None:
        pet_pos = self._pet.mapToGlobal(self._pet.rect().topLeft())
        x = pet_pos.x() + (self._pet.width() - self.width()) // 2
        y = pet_pos.y() - self.height() - 60
        self.move(x, y)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_enter_pressed(self) -> None:
        """Switch pet to TALK, show text, then auto-close after 3 s."""
        text = self._input.text().strip()
        if not text:
            return

        self._input.setVisible(False)
        self._send_btn.setVisible(False)
        self._speech_label.setText(text)
        self._speech_label.setVisible(True)

        self.adjustSize()
        self._position_above_pet()

        # Tell pet to switch to TALK (import here to avoid circular)
        import animation_manager as am
        self._pet.anim_state.set_state(am.State.TALK)  # type: ignore[union-attr]

        self._talk_timer = QTimer(self)
        self._talk_timer.setSingleShot(True)
        self._talk_timer.timeout.connect(self._close_popup)
        self._talk_timer.start(3000)

    def _close_popup(self) -> None:
        import animation_manager as am
        self._pet.anim_state.set_state(am.State.IDLE)  # type: ignore[union-attr]
        self.accept()

    def closeEvent(self, event: __import__("PyQt6.QtCore", fromlist=["QEvent"]).QEvent) -> None:  # type: ignore[name-defined]  # noqa
        if self._talk_timer is not None:
            self._talk_timer.stop()
        super().closeEvent(event)
