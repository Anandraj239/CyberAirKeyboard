import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# ─── Config ───────────────────────────────────────────────────────────────────
WEBCAM_ID          = 0
WINDOW_W, WINDOW_H = 1280, 720

# Pinch detection tuning
PINCH_SCALE        = 0.26   # fraction of hand size → pinch threshold
PINCH_RELEASE_MULT = 1.18   # hysteresis multiplier for release
PINCH_MIN_PX       = 18.0   # absolute minimum threshold (px)
COOLDOWN_S         = 0.35   # seconds between consecutive key fires (debounce)

# Visual feedback
PRESS_EFFECT_DUR   = 0.18   # seconds to show "pressed" highlight

# ─── Keyboard Layout ──────────────────────────────────────────────────────────
ROWS = [
    ['`','1','2','3','4','5','6','7','8','9','0','-','=','⌫','DEL'],
    ['Q','W','E','R','T','Y','U','I','O','P','[',']','\\','CLR'],
    ['A','S','D','F','G','H','J','K','L',';',"'",'↵'],
    ['Z','X','C','V','B','N','M',',','.','/','⇧'],
    ['SPACE'],
]

KEY_MAP = {
    '⌫':    'backspace',
    'DEL':  'delete',
    '↵':    'enter',
    '⇧':    'shift',
    'SPACE':'space',
}

# ─── Build Key Rects ──────────────────────────────────────────────────────────
KEY_SIZE = 74
KEY_GAP  = 4
KB_TOP   = 250   # vertical start of keyboard on screen

def build_keys():
    keys = []
    for row_i, row in enumerate(ROWS):
        total_w = len(row) * (KEY_SIZE + KEY_GAP) - KEY_GAP
        start_x = (WINDOW_W - total_w) // 2
        y = KB_TOP + row_i * (KEY_SIZE + KEY_GAP)
        for col_i, label in enumerate(row):
            w = KEY_SIZE * 7 if label == 'SPACE' else KEY_SIZE
            x = start_x + col_i * (KEY_SIZE + KEY_GAP)
            keys.append({'label': label, 'x': x, 'y': y, 'w': w, 'h': KEY_SIZE})
    return keys

KEYS = build_keys()

# ─── MediaPipe ────────────────────────────────────────────────────────────────
mp_hands    = mp.solutions.hands
mp_drawing  = mp.solutions.drawing_utils
hands_model = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def dist(p1, p2):
    return np.hypot(p1[0] - p2[0], p1[1] - p2[1])

def get_hovered_key(cx, cy):
    """Return the key under point (cx, cy), or None."""
    for k in KEYS:
        if k['x'] <= cx <= k['x'] + k['w'] and k['y'] <= cy <= k['y'] + k['h']:
            return k
    return None

def draw_rounded_rect(img, pt1, pt2, color, alpha, thickness=-1, radius=10):
    """Draw a filled or outlined semi-transparent rounded rectangle."""
    overlay = img.copy()
    x1, y1 = pt1
    x2, y2 = pt2
    if thickness == -1:
        cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        cv2.circle(overlay, (x1 + radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y1 + radius), radius, color, -1)
        cv2.circle(overlay, (x1 + radius, y2 - radius), radius, color, -1)
        cv2.circle(overlay, (x2 - radius, y2 - radius), radius, color, -1)
    else:
        cv2.rectangle(overlay, pt1, pt2, color, thickness)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

# ─── Drawing ──────────────────────────────────────────────────────────────────
def draw_keyboard(frame, hovered_labels, pressed_key, typed_text):
    # Background panel
    draw_rounded_rect(frame, (10, KB_TOP - 90), (WINDOW_W - 10, WINDOW_H - 10),
                      (10, 5, 20), 0.75, radius=20)
    draw_rounded_rect(frame, (10, KB_TOP - 90), (WINDOW_W - 10, WINDOW_H - 10),
                      (255, 100, 200), 0.6, thickness=2)

    for k in KEYS:
        x, y, w, h = k['x'], k['y'], k['w'], k['h']
        label = k['label']

        is_hover   = label in hovered_labels
        is_pressed = (label == pressed_key)

        if is_pressed:
            bg, txt_col, alpha = (50, 255, 100), (0, 0, 0), 0.95
        elif is_hover:
            bg, txt_col, alpha = (255, 100, 200), (255, 255, 255), 0.85
        else:
            bg, txt_col, alpha = (50, 30, 80), (200, 200, 255), 0.60

        draw_rounded_rect(frame, (x, y), (x + w, y + h), bg, alpha, radius=8)

        if is_hover and not is_pressed:
            draw_rounded_rect(frame, (x - 2, y - 2), (x + w + 2, y + h + 2),
                              (255, 100, 200), 0.85, thickness=2)

        font_scale = 0.60 if len(label) == 1 else 0.44
        text_size  = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, font_scale, 1)[0]
        tx = x + (w - text_size[0]) // 2
        ty = y + (h + text_size[1]) // 2

        cv2.putText(frame, label, (tx + 1, ty + 1), cv2.FONT_HERSHEY_DUPLEX,
                    font_scale, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, label, (tx, ty), cv2.FONT_HERSHEY_DUPLEX,
                    font_scale, txt_col, 1, cv2.LINE_AA)

    # Text display bar
    draw_rounded_rect(frame, (40, KB_TOP - 75), (WINDOW_W - 40, KB_TOP - 15),
                      (0, 0, 0), 0.65, radius=10)
    draw_rounded_rect(frame, (40, KB_TOP - 75), (WINDOW_W - 40, KB_TOP - 15),
                      (100, 255, 200), 0.8, thickness=2)
    display = typed_text[-68:] + '|'
    cv2.putText(frame, display, (55, KB_TOP - 33), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (255, 255, 255), 2, cv2.LINE_AA)

def draw_hud(frame, fps):
    draw_rounded_rect(frame, (0, 0), (WINDOW_W, 40), (10, 5, 20), 0.85, radius=0)
    cv2.putText(frame,
                'CYBER AIR KEYBOARD  |  Hover Index Tip  |  Pinch Thumb+Index to Type  |  ESC to quit',
                (20, 26), cv2.FONT_HERSHEY_DUPLEX, 0.50, (255, 100, 200), 1, cv2.LINE_AA)
    cv2.putText(frame, f'FPS: {fps:.0f}', (WINDOW_W - 120, 26),
                cv2.FONT_HERSHEY_DUPLEX, 0.55, (50, 255, 100), 1, cv2.LINE_AA)

# ─── Main Loop ────────────────────────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(WEBCAM_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WINDOW_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_H)

    # Per-hand state
    pinch_states  = {'Left': False, 'Right': False}
    last_fire_t   = {'Left': 0.0,  'Right': 0.0}   # per-hand cooldown

    last_pressed       = None
    press_effect_timer = 0.0
    typed_text         = ''
    prev_time          = time.time()

    print("[AIR KEYBOARD] Starting in CYBER mode...")
    print("[AIR KEYBOARD] Controls: Hover with index tip → Pinch thumb+index to type → ESC to quit\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[AIR KEYBOARD] Webcam read failed. Check camera connection.")
            break

        frame = cv2.flip(frame, 1)                      # mirror
        frame = cv2.resize(frame, (WINDOW_W, WINDOW_H))
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = hands_model.process(rgb)

        hovered_labels = set()
        now = time.time()

        # Clear visual press effect when timer expires
        if now - press_effect_timer > PRESS_EFFECT_DUR:
            last_pressed = None

        if result.multi_hand_landmarks:
            for hand_idx, hand_lm in enumerate(result.multi_hand_landmarks):
                hand_label = result.multi_handedness[hand_idx].classification[0].label
                lm = hand_lm.landmark

                # Index tip (landmark 8) → used for hovering
                ix = int(lm[8].x * WINDOW_W)
                iy = int(lm[8].y * WINDOW_H)
                # Thumb tip (landmark 4)
                tx = int(lm[4].x * WINDOW_W)
                ty = int(lm[4].y * WINDOW_H)
                # Midpoint for pinch visual
                cx = (ix + tx) // 2
                cy = (iy + ty) // 2

                # Dynamic threshold based on hand size (wrist→middle MCP distance)
                wx   = int(lm[0].x * WINDOW_W)
                wy   = int(lm[0].y * WINDOW_H)
                mx   = int(lm[9].x * WINDOW_W)
                my   = int(lm[9].y * WINDOW_H)
                hand_size         = dist((wx, wy), (mx, my))
                pinch_thresh      = max(PINCH_MIN_PX, hand_size * PINCH_SCALE)
                pinch_thresh_rel  = pinch_thresh * PINCH_RELEASE_MULT

                # Draw neon hand skeleton
                mp_drawing.draw_landmarks(
                    frame, hand_lm, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(255, 100, 200), thickness=2),
                )

                # Hover detection: use index TIP only (accurate aiming)
                hovered = get_hovered_key(ix, iy)
                if hovered:
                    hovered_labels.add(hovered['label'])

                # Pinch detection with hysteresis
                pinch_d = dist((ix, iy), (tx, ty))
                threshold = pinch_thresh_rel if pinch_states[hand_label] else pinch_thresh
                is_pinched = pinch_d < threshold

                # Rising edge → new pinch
                if is_pinched and not pinch_states[hand_label]:
                    # Flash circle at midpoint
                    cv2.circle(frame, (cx, cy), 42, (50, 255, 100), 3)

                    # Debounce: skip if fired too recently
                    if (now - last_fire_t[hand_label]) >= COOLDOWN_S:
                        if hovered:
                            label = hovered['label']
                            last_pressed       = label
                            press_effect_timer = now
                            last_fire_t[hand_label] = now

                            # Fire the key
                            if label == 'CLR':
                                typed_text = ''
                            elif label in KEY_MAP:
                                pyautogui.press(KEY_MAP[label])
                                if label == '⌫' and typed_text:
                                    typed_text = typed_text[:-1]
                                elif label == '↵':
                                    typed_text += '\n'
                                elif label == 'SPACE':
                                    typed_text += ' '
                            else:
                                pyautogui.press(label.lower())
                                typed_text += label

                            print(f"  [{hand_label:5s}] '{label}'  →  buffer: {typed_text!r}")

                # Visual indicator on fingertips
                if is_pinched:
                    cv2.circle(frame, (cx, cy),  15, (50, 255, 100),  -1)  # green = pinching
                    cv2.circle(frame, (ix, iy),  10, (50, 255, 100),  -1)
                    cv2.circle(frame, (tx, ty),   8, (50, 255, 100),  -1)
                else:
                    cv2.circle(frame, (ix, iy),  10, (255, 100, 200), -1)  # pink = exploring
                    cv2.circle(frame, (tx, ty),   8, (180,  80, 180), -1)

                pinch_states[hand_label] = is_pinched

        # ── Draw UI ───────────────────────────────────────────────────────────
        draw_keyboard(frame, hovered_labels, last_pressed, typed_text)

        now      = time.time()
        fps      = 1.0 / max(now - prev_time, 1e-9)
        prev_time = now
        draw_hud(frame, fps)

        cv2.imshow('Cyber Air Keyboard', frame)
        if cv2.waitKey(1) & 0xFF == 27:   # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n[AIR KEYBOARD] Session ended. Goodbye!")

if __name__ == '__main__':
    main()
