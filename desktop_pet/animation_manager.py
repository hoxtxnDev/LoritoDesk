"""Animation state-machine that loads sprite sheets and serves frames."""

from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image
from PyQt6.QtGui import QPixmap

from chroma_key import remove_green


class State(Enum):
    """Animation states for the desktop pet."""
    IDLE = auto()
    TALK = auto()
    WALK = auto()
    REACT = auto()


# ── Sprite-sheet definitions ──────────────────────────────────────────
# (path_stem, state, frame_count, frame_width, frame_height)
SHEET_DEFS = [
    ("lorito_idle.png", State.IDLE, 4, 443, 887),
    ("lorito_talk.png", State.TALK, 4, 443, 887),
    ("lorito_walk.png", State.WALK, 6, 295, 887),
]


class AnimationManager:
    """Loads, caches and serves sprite frames per state."""

    def __init__(self, assets_dir: Path) -> None:
        self._assets_dir = assets_dir
        self._frames: Dict[State, List[QPixmap]] = {}
        self._current_state: State = State.IDLE
        self._current_frame: int = 0

        self._load_all_sheets()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_state(self, new_state: State) -> None:
        """Switch to *new_state* and reset the frame counter."""
        if new_state in self._frames:
            self._current_state = new_state
            self._current_frame = 0

    def next_frame(self) -> QPixmap:
        """Return the next QPixmap for the current state (looping)."""
        frames = self._frames.get(self._current_state)
        if not frames:
            pix = QPixmap(1, 1)
            pix.fill(  # type: ignore[call-arg]
                __import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.GlobalColor.transparent  # noqa
            )
            return pix

        pixmap = frames[self._current_frame % len(frames)]
        self._current_frame += 1
        return pixmap

    @property
    def state(self) -> State:
        return self._current_state

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_all_sheets(self) -> None:
        for stem, state, count, fw, fh in SHEET_DEFS:
            path = self._assets_dir / stem
            if path.exists():
                self._load_sheet(path, state, count, fw, fh)

    def _load_sheet(
        self,
        path: Path,
        state: State,
        frame_count: int,
        frame_width: int,
        frame_height: int,
    ) -> None:
        sheet_pil = Image.open(path).convert("RGBA")
        sheet_w, sheet_h = sheet_pil.size
        frames: List[QPixmap] = []

        for i in range(frame_count):
            x0 = i * frame_width
            x1 = min(x0 + frame_width, sheet_w)
            y1 = min(frame_height, sheet_h)
            frame_pil = sheet_pil.crop((x0, 0, x1, y1))
            qpix = remove_green(frame_pil)
            frames.append(qpix)

        if frames:
            self._frames[state] = frames
