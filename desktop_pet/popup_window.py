"""Frameless speech-bubble popup for typing to the desktop pet.

Arquitectura de la burbuja:
- Cloud y lorito comparten el mismo sprite sheet 443x887.
- El overlay del cloud se renderiza con EXACTAMENTE el mismo tamaño que
  la ventana del loro, posicionado de forma que visualmente la nube
  quede flotando sobre la cabeza del loro (los dos assets encajan).
- Texto superpuesto encima de la nube usando QLabel transparente.
- Micro-animación: la nube alterna frames mientras el loro habla.
- Auto-cierre tras 4 segundos.
- Slider para elegir tamaño del loro.
"""

import random
from pathlib import Path
from typing import Callable, Final, List, Optional

from PIL import Image
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QPainter, QPixmap, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from chroma_key import remove_green

# ── Lorito's phrasebook ──────────────────────────────────────────────
# ── Lorito's phrasebook (Chilean Dev Roast Mode CTM 🌶️🇨🇱) ────────────────────────────────
LORITO_RESPONSES: Final[List[str]] = [
    "¿Ese código ql es tuyo o lo sacaste de un tutorial del 2014? ¡Squawk!",
    "Mucho teclado mecánico de 200 lucas, pero codeai como las reverendas cachas.",
    "Tu historial de Git parece registro de defunciones, puras cagás. ¡Squawk!",
    "Si compila a la primera, asústate weón. Si es tu código, mejor arranca.",
    "Ese comentario que dice 'TODO: arreglar' lleva ahí desde el año de la pera, pajero.",
    "Botaste producción otra vez? Puta que eri aweonao. ¡Squawk!",
    "¿Hiciste un commit con el mensaje 'asdfgh'? Puta el weón penca.",
    "El `if-else` que te mandaste tiene menos futuro que este país, conchetumare.",
    "¡Squawk! ¿Un `print('aqui pasa')` en producción? Tremenda ordinariez, weón.",
    "Tu cagá de código tiene más bugs que motel de a luca.",
    "En mi jaula hay más orden y lógica que en tu base de datos qla.",
    "¿Seguro que no querís probar otra carrera? Nunca es tarde pa' irse a plantar tomates al sur.",
    "Ni en un bootcamp de dos lucas te aceptarían esta cagá de script.",
    "Cuidado, que tu weá compila de pura cuea. ¡Squawk!",
    "No sé qué chucha pusiste en el input, pero mi CPU se quería corbatear.",
    "¿A eso le llamai refactorizar? ¡Si solo le cambiaste el nombre a tres variables, carenalga!",
    "Decir 'en mi máquina funciona' no te va a salvar de la PLR que te van a dar, sacowea.",
    "Ojalá tuvieras la misma creatividad pa' codear que pa' sacar la vuelta en la daily.",
    "¿Copiaste esta weá de StackOverflow o la cagaste tú solito?",
    "Ese espagueti ql no te lo arregla ni un equipo de indios de YouTube. ¡Squawk!",
    "A ver si aprendí a usar Git, pajero culiáo, que me tení el repo lleno de basura.",
    "Tanta pantalla curva pa' escribir weás que revientan en la línea 12.",
]

PET_SIZE_DEFAULT = 250
PET_SIZE_MIN = 150
PET_SIZE_MAX = 350


class CloudBubbleOverlay(QWidget):
    """Widget transparente que muestra una nube estática sobre el loro."""

    def __init__(
        self,
        cloud_frames: List[QPixmap],
        text: str,
        target_widget: QWidget,
        on_done: Callable,
    ) -> None:
        super().__init__(None)
        self._frames = cloud_frames
        self._target = target_widget
        self._on_done = on_done

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # QLabel para la imagen de la nube
        self._cloud_label = QLabel(self)
        self._cloud_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._cloud_label.move(0, 0)

        # QLabel para el texto superpuesto
        self._text_label = QLabel(self)
        self._text_label.setWordWrap(True)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text_label.setText(text)
        self._text_label.setStyleSheet(
            """
            QLabel {
                color: #1a1a1a;
                font-family: 'Segoe UI', 'Arial';
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
            """
        )

        # Aplicamos la imagen estática y posicionamos
        self._apply_frame(0)
        self._reposition()

        # (Temporizador de animación eliminado)

        # Mantenemos el auto-cierre tras 4 segundos
        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.timeout.connect(self._finish)
        self._close_timer.start(4000)

    def _apply_frame(self, idx: int) -> None:
        if not self._frames:
            return
        pix = self._frames[0]
        w, h = pix.width(), pix.height()

        self._cloud_label.setPixmap(pix)
        self._cloud_label.resize(w, h)
        self.resize(w, h)

        # NUEVO AJUSTE DE LA CAJA DE TEXTO (Para la nube estirada)
        tx = int(w * 0.15)  # Margen izquierdo (esquiva los hongos)
        ty = int(h * 0.20)  # Margen superior
        tw = int(w * 0.70)  # Ancho seguro para que quepa mucho texto
        th = int(h * 0.60)  # Alto seguro
        
        self._text_label.setGeometry(tx, ty, tw, th)

    def _reposition(self) -> None:
        pet_global = self._target.mapToGlobal(QPoint(0, 0))
        
        # Centrar horizontalmente: (Ancho del loro - Ancho de la nube) divido en 2
        x_offset = (self._target.width() - self.width()) // 2
        
        # Ajuste vertical: Como la nube ahora respeta su forma bajita, 
        # ocupará menos espacio hacia abajo. 0.50 (50%) debería bastar para subirla.
        y_offset = int(self._target.height() * 0.50) 
        
        self.move(pet_global.x() + x_offset, pet_global.y() - y_offset)

    def _finish(self) -> None:
        self.close()
        if self._on_done:
            self._on_done()


class InteractionPopup(QDialog):
    """Dialog minimalista de input. Al enviar, muestra la burbuja cloud
    superpuesta sobre el loro y se cierra sola."""

    def __init__(self, pet: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._pet = pet
        self._cloud_frames: List[QPixmap] = []
        self._overlay: Optional[CloudBubbleOverlay] = None

        self._load_cloud_asset()
        self._setup_ui()

    # ------------------------------------------------------------------
    # Cloud asset
    # ------------------------------------------------------------------
    def _load_cloud_asset(self) -> None:
        """Cargar cloud.png como una imagen estática manteniendo su proporción original."""
        assets_dir = Path(__file__).parent / "assets"
        cloud_path = assets_dir / "cloud.png"
        if not cloud_path.exists():
            return

        cloud_img = Image.open(cloud_path).convert("RGBA")
        qpix = remove_green(cloud_img)
        
        # NUEVO: Escalar la nube para que sea más ancha que el loro (ej. 1.8 veces su ancho).
        # scaledToWidth mantiene la proporción original (aspect ratio) intacta automáticamente.
        target_width = int(self._pet.width() * 1.8)
        scaled = qpix.scaledToWidth(
            target_width, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        self._cloud_frames = [scaled]

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self._container = QFrame()
        self._container.setObjectName("bubble_container")
        self._container.setStyleSheet(
            """
            #bubble_container {
                background: #1a1a1a;
                border: 2px solid #00ff00;
                border-radius: 10px;
            }
            QLineEdit {
                background: #1a1a1a;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 13px;
                border: none;
                padding: 6px;
            }
            QPushButton {
                background: #1a1a1a;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 12px;
                border: 1px solid #00ff00;
                border-radius: 4px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background: #00ff00;
                color: #1a1a1a;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #00ff00;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #00ff00;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QLabel {
                color: #00aa00;
                font-family: 'Courier New';
                font-size: 11px;
                background: transparent;
            }
            """
        )

        cl = QVBoxLayout(self._container)
        cl.setContentsMargins(8, 8, 8, 8)
        cl.setSpacing(5)

        # Input row
        self._input = QLineEdit()
        self._input.setPlaceholderText("Escribele al lorito...")
        self._input.returnPressed.connect(self._on_enter_pressed)

        self._send_btn = QPushButton("Enviar")
        self._send_btn.clicked.connect(self._on_enter_pressed)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(0, 0, 0, 0)
        input_row.addWidget(self._input)
        input_row.addWidget(self._send_btn)
        cl.addLayout(input_row)

        # Size slider
        size_row = QHBoxLayout()
        size_row.setContentsMargins(0, 0, 0, 0)

        size_lbl = QLabel("Tamaño loro:")
        size_row.addWidget(size_lbl)

        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setMinimum(PET_SIZE_MIN)
        self._size_slider.setMaximum(PET_SIZE_MAX)
        cur_h = self._pet.height()
        self._size_slider.setValue(
            cur_h if PET_SIZE_MIN <= cur_h <= PET_SIZE_MAX else PET_SIZE_DEFAULT
        )
        self._size_slider.setFixedWidth(110)
        self._size_slider.valueChanged.connect(self._on_size_changed)
        size_row.addWidget(self._size_slider)

        self._size_val_lbl = QLabel(f"{self._size_slider.value()}px")
        self._size_val_lbl.setFixedWidth(38)
        size_row.addWidget(self._size_val_lbl)
        size_row.addStretch()
        cl.addLayout(size_row)

        root.addWidget(self._container)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 160))
        self._container.setGraphicsEffect(shadow)

        self.setFixedWidth(310)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._position_above_pet()

    def _position_above_pet(self) -> None:
        """Posiciona el popup en la parte superior del asset del loro."""
        screen_geo = QApplication.instance().primaryScreen().availableGeometry()
        pet_pos = self._pet.mapToGlobal(self._pet.rect().topLeft())

        # Centrar exactamente usando la mitad del espacio restante (// 2)
        x = pet_pos.x() + (self._pet.width() - self.width()) // 2
        # Restar la altura del panel y un pequeño margen para colocarlo ARRIBA
        y = pet_pos.y() - self.height() - 10

        # Lógica para evitar que se salga de los límites de la pantalla
        if y < screen_geo.top():
            # Si no cabe arriba del monitor, lo forzamos a aparecer abajo del loro
            y = pet_pos.y() + self._pet.height() + 10

        if x < screen_geo.left():
            x = screen_geo.left() + 4
        elif x + self.width() > screen_geo.right():
            x = screen_geo.right() - self.width() - 4

        self.move(x, y)

    def _on_size_changed(self, value: int) -> None:
        self._size_val_lbl.setText(f"{value}px")
        if hasattr(self._pet, "resize_pet"):
            self._pet.resize_pet(value)
            self._cloud_frames.clear()
            self._load_cloud_asset()

    def _on_enter_pressed(self) -> None:
        user_text = self._input.text().strip()
        if not user_text:
            return

        response = random.choice(LORITO_RESPONSES)
        if random.random() < 0.3:
            snippet = user_text[:20]
            response = f"{snippet}… {response}"

        self.hide()

        import animation_manager as am
        self._pet.anim_state.set_state(am.State.TALK)

        self._overlay = CloudBubbleOverlay(
            cloud_frames=self._cloud_frames,
            text=response,
            target_widget=self._pet,
            on_done=self._on_overlay_done,
        )
        self._overlay.show()

    def _on_overlay_done(self) -> None:
        import animation_manager as am
        self._pet.anim_state.set_state(am.State.IDLE)
        self._overlay = None
        self.accept()

    def closeEvent(self, event) -> None:
        if self._overlay is not None:
            self._overlay.close()
        super().closeEvent(event)