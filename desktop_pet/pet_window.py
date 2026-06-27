"""DesktopPet — frameless, transparent, draggable pet window."""

from pathlib import Path

from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QPixmap, QShortcut, QKeySequence
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

from animation_manager import AnimationManager, State
from behavior_engine import trigger_bounce, trigger_random_walk

ESC_TIMEOUT_MS = 800
from popup_window import InteractionPopup, PET_SIZE_DEFAULT


class DesktopPet(QWidget):
    """Main desktop pet widget with transparency, dragging and animation."""

    ASSETS_DIR = Path(__file__).parent / "assets"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._drag_offset: QPoint = QPoint()
        self._popup: InteractionPopup | None = None
        self._pet_scale: int = PET_SIZE_DEFAULT  # height in px
        self._esc_count: int = 0

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

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._label = QLabel(self)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._esc_timer = QTimer(self)
        self._esc_timer.setSingleShot(True)
        self._esc_timer.timeout.connect(lambda: setattr(self, '_esc_count', 0))

    def _setup_assets(self) -> None:
        self.anim_state = AnimationManager(self.ASSETS_DIR, target_height=self._pet_scale)
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
    # Resize the pet (called from the size slider in popup)
    # ------------------------------------------------------------------
    def resize_pet(self, target_height: int) -> None:
        """Re-scale all sprite frames and resize the window."""
        self._pet_scale = target_height
        self.anim_state.set_target_height(target_height)
        # Actualizar tamaño visual con el primer frame disponible
        first = self.anim_state.next_frame()
        self._label.setPixmap(first)
        self._label.resize(first.size())
        self.resize(first.size())

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
    # Mouse events
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
    # Key event — double Esc closes the app
    # ------------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is None:
            return
        if event.key() == Qt.Key.Key_Escape:
            self._esc_count += 1
            if self._esc_count >= 2:
                QApplication.quit()
            else:
                self._esc_timer.start(ESC_TIMEOUT_MS)
        super().keyPressEvent(event)

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
    def closeEvent(self, event) -> None:
        self._anim_timer.stop()
        self._behave_timer.stop()
        if self._react_timer is not None:
            self._react_timer.stop()
        self._esc_timer.stop()
        super().closeEvent(event)
