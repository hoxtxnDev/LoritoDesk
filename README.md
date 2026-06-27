# Lorito — Interactive Desktop Pet 🦜

A frameless, always-on-top desktop pet application built with Python and PyQt6. The lorito (parrot) walks around your screen, reacts to clicks, and you can chat with it via a retro-styled speech-bubble popup.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.11-green)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Frameless window** — no title bar, no taskbar entry, stays on top
- **Drag anywhere** — left-click and drag to reposition
- **Right-click chat** — opens a cyberpunk-style input popup
- **Double-click bounce** — the pet jumps with a squash-and-stretch animation
- **Autonomous walking** — random screen walks every 8–20 seconds with smooth easing
- **Sprite animations** — IDLE (breathing), TALK (beak), WALK (cycle), REACT (bounce)
- **Chroma-key transparency** — green screen removal with configurable tolerance

## Requirements

- Python 3.10+
- [PyQt6](https://pypi.org/project/PyQt6/)
- [Pillow](https://pypi.org/project/Pillow/)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/lorito-desktop-pet.git
cd lorito-desktop-pet

# Install dependencies
pip install PyQt6 Pillow

# Run
python desktop_pet/main.py
```

## Project Structure

```
desktop_pet/
├── main.py                 # Entry point
├── pet_window.py           # DesktopPet QWidget (transparency, drag, animation loop)
├── popup_window.py         # InteractionPopup QDialog (input field, speech bubble)
├── animation_manager.py    # AnimationManager (state machine: IDLE, TALK, WALK, REACT)
├── behavior_engine.py      # Random autonomous movement + bounce reaction
├── chroma_key.py           # Utility: remove #00ff00 background from sprite frames
└── assets/
    ├── lorito_idle.png     # Sprite sheet — 4 frames, idle loop
    ├── lorito_talk.png     # Sprite sheet — 4 frames, beak open/close
    └── lorito_walk.png     # Sprite sheet — 6 frames, walk cycle
```

## Controls

| Action | Effect |
|--------|--------|
| Left-click + drag | Move the pet |
| Right-click | Open chat popup |
| Double-click | Bounce / react animation |
| Type + Enter in popup | Pet talks, displays speech bubble |
| Click outside popup | Close popup |

## Sprite Sheet Generation

The sprite sheets were generated as horizontal strips on a `#00ff00` green screen background:

| Sheet | Frames | Frame Size |
|-------|--------|------------|
| `lorito_idle.png` | 4 | 443×887 |
| `lorito_talk.png` | 4 | 443×887 |
| `lorito_walk.png` | 6 | 295×887 |

To generate your own, use any pixel-art generator with a green screen background (`#00ff00`, no gradients, no anti-aliasing at edges).

## Configuration

Edit `chroma_key.py` to adjust the green-screen tolerance:

```python
TOLERANCE = 40  # default — lower = stricter green detection
```

## Compatibility

- Windows 10/11 ✓
- Linux (X11) ✓ (untested on Wayland)
