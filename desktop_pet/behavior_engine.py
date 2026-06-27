"""Autonomous movement and reaction behaviour for the desktop pet."""

import random
from typing import TYPE_CHECKING

from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, QTimer
from PyQt6.QtWidgets import QWidget

if TYPE_CHECKING:
    from pet_window import DesktopPet


def trigger_random_walk(pet: "DesktopPet") -> None:
    """Move *pet* to a random position within the available screen geometry.

    The pet's animation is switched to WALK for the duration of the movement,
    then returned to IDLE.
    """
    screen_geo: QRect = (
        __import__("PyQt6.QtWidgets", fromlist=["QApplication"])
        .QApplication.instance()
        .primaryScreen()
        .availableGeometry()
    )

    margin = 80
    target_x = random.randint(margin, screen_geo.width() - pet.width() - margin)
    target_y = random.randint(margin, screen_geo.height() - pet.height() - margin)
    target = QPoint(target_x, target_y)

    duration = random.randint(2000, 4000)

    pet.anim_state.set_state(
        __import__("animation_manager", fromlist=["State"]).State.WALK
    )

    anim = QPropertyAnimation(pet, b"pos")
    anim.setEndValue(target)
    anim.setDuration(duration)
    anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def _on_finished() -> None:
        pet.anim_state.set_state(
            __import__("animation_manager", fromlist=["State"]).State.IDLE
        )

    anim.finished.connect(_on_finished)
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


def trigger_bounce(pet: "DesktopPet") -> None:
    """Quick vertical bounce (jump up 60 px, return) at current position.

    This is used as the REACT animation when the user double-clicks.
    """
    orig = pet.pos()
    peak = QPoint(orig.x(), orig.y() - 60)

    anim_up = QPropertyAnimation(pet, b"pos")
    anim_up.setEndValue(peak)
    anim_up.setDuration(200)
    anim_up.setEasingCurve(QEasingCurve.Type.OutQuad)

    anim_down = QPropertyAnimation(pet, b"pos")
    anim_down.setEndValue(orig)
    anim_down.setDuration(250)
    anim_down.setEasingCurve(QEasingCurve.Type.InBounce)

    anim_up.finished.connect(anim_down.start)

    def _on_done() -> None:
        pet.anim_state.set_state(
            __import__("animation_manager", fromlist=["State"]).State.IDLE
        )

    anim_down.finished.connect(_on_done)
    anim_up.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
