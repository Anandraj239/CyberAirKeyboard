# Cyber Air Keyboard ⌨️

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange)](https://mediapipe.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Type in mid-air — no physical keyboard required.**

Cyber Air Keyboard is a next-generation, computer-vision-based virtual keyboard that lets you type effortlessly using only your webcam and hand gestures. Built with Google MediaPipe hand tracking, it runs entirely offline with zero cloud dependency.

Developed by [Anandraj239](https://github.com/Anandraj239).

---

## ✨ Key Features

| Feature | Details |
|---|---|
| **Dual-Hand Tracking** | Tracks both hands simultaneously via MediaPipe for faster typing |
| **Precision Pinch-to-Click** | Dynamic threshold adapts to hand distance from camera — reduces misclicks |
| **Debounce Cooldown** | 350 ms per-hand cooldown prevents accidental double-fires |
| **Hysteresis Release** | Separate engage/release thresholds for stable, glitch-free clicks |
| **Cyber Neon UI** | Semi-transparent neon aesthetic rendered natively in OpenCV |
| **Fully Offline** | No internet required — runs locally at real-time framerate |

---

## 🛠️ How It Works

```
Webcam → MediaPipe Hands → Index Tip Position → Hover Detection
                         → Thumb–Index Distance → Pinch Detection → pyautogui.press()
```

- **Hovering**: The **index fingertip** (landmark 8) is used for precise key targeting.
- **Clicking**: A pinch between the **thumb tip** (landmark 4) and index tip fires a keystroke.
- **Dynamic threshold**: The pinch distance threshold scales with hand size (wrist→MCP distance), so the keyboard works correctly whether your hand is close or far from the camera.

---

## ⚙️ Installation & Setup

> Recommended: **Python 3.11** or **3.12** (required for `mediapipe` on Windows)

### 1. Clone the repository
```bash
git clone https://github.com/Anandraj239/CyberAirKeyboard.git
cd CyberAirKeyboard
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch
```bash
python air_keyboard.py
```

> **Windows shortcut**: Double-click `Run Air Keyboard.bat` — it activates the venv and launches automatically.

---

## 🎮 Controls

| Action | Gesture |
|---|---|
| **Hover over a key** | Point your index fingertip at the key |
| **Press a key** | Pinch thumb + index finger together |
| **Backspace** | Press `⌫` |
| **Clear buffer** | Press `CLR` |
| **Enter** | Press `↵` |
| **Space** | Press `SPACE` |
| **Quit** | Press `ESC` on keyboard |

---

## 🔧 Configuration

At the top of `air_keyboard.py` you can tune:

```python
WEBCAM_ID          = 0       # Change if you have multiple cameras
PINCH_SCALE        = 0.26    # Pinch sensitivity (lower = easier to trigger)
PINCH_RELEASE_MULT = 1.18    # Hysteresis ratio for release
PINCH_MIN_PX       = 18.0    # Minimum pinch distance in pixels
COOLDOWN_S         = 0.35    # Seconds between key fires (debounce)
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| `mediapipe` install fails | Use Python 3.11 or 3.12 (not 3.13+) |
| Webcam not detected | Change `WEBCAM_ID = 0` to `1` or `2` |
| Keys firing too easily | Increase `PINCH_SCALE` (e.g. `0.30`) |
| Keys hard to trigger | Decrease `PINCH_SCALE` (e.g. `0.22`) |
| Double-typing | Increase `COOLDOWN_S` (e.g. `0.5`) |
| Low FPS | Ensure good lighting; lower `min_detection_confidence` slightly |

---

## 📦 Dependencies

```
opencv-python==4.13.0.92
mediapipe==0.10.9
pyautogui==0.9.54
numpy==2.4.3
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
