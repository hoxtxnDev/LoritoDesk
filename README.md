# Lorito — Mascota de Escritorio Interactiva 🦜

Aplicación de mascota de escritorio sin bordes, siempre al frente, construida con Python y PyQt6. El lorito camina por tu pantalla, reacciona a clics y puedes chatear con él mediante una burbuja de diálogo de estilo retro.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.11-green)
![Licencia](https://img.shields.io/badge/license-MIT-green)

## Características

- **Ventana sin bordes** — sin barra de título, sin entrada en la barra de tareas, siempre al frente
- **Arrastrar** — clic izquierdo y arrastra para reposicionar
- **Chat con clic derecho** — abre un popup de entrada estilo cyberpunk
- **Rebote al doble clic** — la mascota salta con animación de estiramiento
- **Caminata autónoma** — paseos aleatorios por la pantalla cada 8–20 segundos con easing suave
- **Animaciones por sprites** — IDLE (respiración), TALK (pico), WALK (ciclo), REACT (salto)
- **Transparencia chroma-key** — eliminación de fondo verde con tolerancia configurable

## Requisitos

- Python 3.10+
- [PyQt6](https://pypi.org/project/PyQt6/)
- [Pillow](https://pypi.org/project/Pillow/)

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/lorito-desktop-pet.git
cd lorito-desktop-pet

# Instalar dependencias
pip install PyQt6 Pillow

# Ejecutar
python desktop_pet/main.py
```

## Estructura del Proyecto

```
desktop_pet/
├── main.py                 # Punto de entrada
├── pet_window.py           # DesktopPet QWidget (transparencia, arrastre, bucle de animación)
├── popup_window.py         # InteractionPopup QDialog (campo de texto, burbuja de diálogo)
├── animation_manager.py    # AnimationManager (máquina de estados: IDLE, TALK, WALK, REACT)
├── behavior_engine.py      # Movimiento autónomo aleatorio + reacción de rebote
├── chroma_key.py           # Utilidad: elimina fondo #00ff00 de los sprites
└── assets/
    ├── lorito_idle.png     # Sprite sheet — 4 fotogramas, bucle idle
    ├── lorito_talk.png     # Sprite sheet — 4 fotogramas, apertura/cierre de pico
    └── lorito_walk.png     # Sprite sheet — 6 fotogramas, ciclo de caminata
```

## Controles

| Acción | Efecto |
|--------|--------|
| Clic izquierdo + arrastrar | Mover la mascota |
| Clic derecho | Abrir popup de chat |
| Doble clic | Animación de rebote / reacción |
| Escribir + Enter en popup | La mascota habla, muestra burbuja de texto |
| Clic fuera del popup | Cerrar popup |

## Generación de Sprite Sheets

Los sprite sheets se generaron como tiras horizontales sobre un fondo verde `#00ff00`:

| Hoja | Fotogramas | Tamaño por fotograma |
|------|------------|----------------------|
| `lorito_idle.png` | 4 | 443×887 |
| `lorito_talk.png` | 4 | 443×887 |
| `lorito_walk.png` | 6 | 295×887 |

Para generar los tuyos, usa cualquier generador de pixel art con fondo verde (`#00ff00`, sin degradados, sin anti-aliasing en los bordes).

## Configuración

Edita `chroma_key.py` para ajustar la tolerancia del chroma-key:

```python
TOLERANCIA = 40  # valor por defecto — menor = detección de verde más estricta
```

## Compatibilidad

- Windows 10/11 ✓
- Linux (X11) ✓ (no probado en Wayland)
