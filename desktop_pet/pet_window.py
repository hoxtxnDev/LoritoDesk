"""DesktopPet — frameless, transparent, draggable pet window."""

from pathlib import Path

from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QMouseEvent, QPixmap
from PyQt6.QtWidgets import QLabel, QWidget

from animation_manager import AnimationManager, State
from behavior_engine import trigger_bounce, trigger_random_walk
from popup_window import InteractionPopup


class DesktopPet(QWidget):
    """Main desktop pet widget with transparency, dragging and animation."""

    ASSETS_DIR = Path(__file__).parent / "assets"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._drag_offset: QPoint = QPoint()
        self._popup: InteractionPopup | None = None

        self._setup_window()
        self._setup_assets()
        self._setup_timers()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------
    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._label = QLabel(self)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def _setup_assets(self) -> None:
        self.anim_state = AnimationManager(self.ASSETS_DIR)
        first_frame = self.anim_state.next_frame()
        self._label.setPixmap(first_frame)
        self._label.resize(first_frame.size())
        self.resize(first_frame.size())

    def _setup_timers(self) -> None:
        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(100)
        self._anim_timer.timeout.connect(self._update_frame)
        self._anim_timer.start()

        self._behave_timer = QTimer(self)
        self._behave_timer.setSingleShot(True)
        self._behave_timer.timeout.connect(self._on_behave_tick)
        self._schedule_next_walk()

        self._react_timer: QTimer | None = None

    # ------------------------------------------------------------------
    # Animation loop
    # ------------------------------------------------------------------
    def _update_frame(self) -> None:
        pix = self.anim_state.next_frame()
        self._label.setPixmap(pix)

    # ------------------------------------------------------------------
    # Behaviour timer
    # ------------------------------------------------------------------
    def _schedule_next_walk(self) -> None:
        import random
        interval = random.randint(8000, 20000)
        self._behave_timer.start(interval)

    def _on_behave_tick(self) -> None:
        if self.anim_state.state != State.WALK:
            trigger_random_walk(self)
        self._schedule_next_walk()

    # ------------------------------------------------------------------
    # Mouse events — drag / right-click / double-click
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._open_popup()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        self.anim_state.set_state(State.REACT)
        trigger_bounce(self)

        self._react_timer = QTimer(self)
        self._react_timer.setSingleShot(True)
        self._react_timer.timeout.connect(
            lambda: self.anim_state.set_state(State.IDLE)
        )
        self._react_timer.start(1500)

        event.accept()

    # ------------------------------------------------------------------
    # Popup
    # ------------------------------------------------------------------
    def _open_popup(self) -> None:
        if self._popup is not None:
            return
        self._popup = InteractionPopup(self)
        self._popup.finished.connect(self._on_popup_closed)
        self._popup.show()

    def _on_popup_closed(self) -> None:
        self._popup = None

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    def closeEvent(self, event: __import__("PyQt6.QtCore", fromlist=["QEvent"]).QEvent) -> None:  # type: ignore[name-defined]  # noqa
        self._anim_timer.stop()
        self._behave_timer.stop()
        if self._react_timer is not None:
            self._react_timer.stop()
        super().closeEvent(event)
