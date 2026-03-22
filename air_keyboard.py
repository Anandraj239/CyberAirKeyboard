import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# ─── Config ───────────────────────────────────────────────────────────────────
CLICK_THRESHOLD   = 50    # px distance between index tip & middle tip → triggers key press
WEBCAM_ID         = 0
WINDOW_W, WINDOW_H = 1280, 720

# ─── Keyboard Layout ──────────────────────────────────────────────────────────
ROWS = [
    ['`','1','2','3','4','5','6','7','8','9','0','-','=','⌫', 'DEL'],
    ['Q','W','E','R','T','Y','U','I','O','P','[',']','\\', 'CLR'],
    ['A','S','D','F','G','H','J','K','L',';',"'",'↵'],
    ['Z','X','C','V','B','N','M',',','.','/','⇧'],
    ['SPACE'],
]

KEY_MAP = {
    '⌫': 'backspace',
    'DEL': 'delete',
    '↵': 'enter',
    '⇧': 'shift',
    'SPACE': 'space',
}

# ─── Build Key Rects ──────────────────────────────────────────────────────────
KEY_SIZE   = 75
KEY_GAP    = 4
KB_TOP     = 250   # vertical start of keyboard on screen

def build_keys():
    keys = []
    for row_i, row in enumerate(ROWS):
        total_w = len(row) * (KEY_SIZE + KEY_GAP) - KEY_GAP
        start_x = (WINDOW_W - total_w) // 2
        y = KB_TOP + row_i * (KEY_SIZE + KEY_GAP)
        for col_i, label in enumerate(row):
            if label == 'SPACE':
                w = KEY_SIZE * 7
            else:
                w = KEY_SIZE
            x = start_x + col_i * (KEY_SIZE + KEY_GAP)
            keys.append({'label': label, 'x': x, 'y': y, 'w': w, 'h': KEY_SIZE})
    return keys

KEYS = build_keys()

# ─── MediaPipe ────────────────────────────────────────────────────────────────
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands_model = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,       # SUPPORT BOTH HANDS
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def dist(p1, p2):
    return np.hypot(p1[0]-p2[0], p1[1]-p2[1])

def get_hovered_key(cx, cy):
    for k in KEYS:
        if k['x'] <= cx <= k['x']+k['w'] and k['y'] <= cy <= k['y']+k['h']:
            return k
    return None

def draw_transparent_rect(img, pt1, pt2, color, alpha, thickness=-1, radius=10):
    overlay = img.copy()
    if thickness == -1:
        # Drawing a rounded filled rectangle using shapes
        x1, y1 = pt1
        x2, y2 = pt2
        cv2.rectangle(overlay, (x1+radius, y1), (x2-radius, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1+radius), (x2, y2-radius), color, -1)
        cv2.circle(overlay, (x1+radius, y1+radius), radius, color, -1)
        cv2.circle(overlay, (x2-radius, y1+radius), radius, color, -1)
        cv2.circle(overlay, (x1+radius, y2-radius), radius, color, -1)
        cv2.circle(overlay, (x2-radius, y2-radius), radius, color, -1)
    else:
        # Just simple rect for borders
        cv2.rectangle(overlay, pt1, pt2, color, thickness)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

def draw_keyboard(frame, hovered_keys, pressed_key, typed_text):
    # ── Background panel with Neon Glow ───────────────────────────────────────
    draw_transparent_rect(frame, (10, KB_TOP - 90), (WINDOW_W - 10, WINDOW_H - 10), (10, 5, 20), 0.75, radius=20)
    draw_transparent_rect(frame, (10, KB_TOP - 90), (WINDOW_W - 10, WINDOW_H - 10), (255, 100, 200), 0.6, thickness=2)

    for k in KEYS:
        x, y, w, h = k['x'], k['y'], k['w'], k['h']
        label = k['label']
        
        is_hover   = label in [hk['label'] for hk in hovered_keys if hk]
        is_pressed = (label == pressed_key)

        # Cooler neon colors
        if is_pressed:
            bg = (50, 255, 100)    # bright green
            txt_col = (0, 0, 0)
            alpha = 0.9
        elif is_hover:
            bg = (255, 100, 200)   # neon pink hover
            txt_col = (255, 255, 255)
            alpha = 0.8
        else:
            bg = (50, 30, 80)      # deep purple
            txt_col = (200, 200, 255)
            alpha = 0.6

        # Draw Key base
        draw_transparent_rect(frame, (x, y), (x+w, y+h), bg, alpha, radius=8)
        
        # Border glow for hovered
        if is_hover and not is_pressed:
            draw_transparent_rect(frame, (x-2, y-2), (x+w+2, y+h+2), (255, 100, 200), 0.8, thickness=2)

        font_scale = 0.6 if len(label) == 1 else 0.45
        text_size  = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, font_scale, 1)[0]
        tx = x + (w - text_size[0]) // 2
        ty = y + (h + text_size[1]) // 2
        
        # Add slight shadow to text
        cv2.putText(frame, label, (tx+1, ty+1), cv2.FONT_HERSHEY_DUPLEX, font_scale, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, label, (tx, ty), cv2.FONT_HERSHEY_DUPLEX, font_scale, txt_col, 1, cv2.LINE_AA)

    # ── Text display bar ──────────────────────────────────────────────────────
    draw_transparent_rect(frame, (40, KB_TOP - 75), (WINDOW_W - 40, KB_TOP - 15), (0, 0, 0), 0.6, radius=10)
    draw_transparent_rect(frame, (40, KB_TOP - 75), (WINDOW_W - 40, KB_TOP - 15), (100, 255, 200), 0.8, thickness=2)
    
    display = typed_text[-65:] + '|'   # show last 65 chars
    cv2.putText(frame, display, (55, KB_TOP - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

def draw_hud(frame, fps):
    draw_transparent_rect(frame, (0, 0), (WINDOW_W, 40), (10, 5, 20), 0.8, radius=0)
    cv2.putText(frame, 'CYBER AIR KEYBOARD | Both Hands | Pinch Thumb & Index to Type | ESC to quit',
                (20, 26), cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 100, 200), 1, cv2.LINE_AA)
    cv2.putText(frame, f'FPS: {fps:.0f}', (WINDOW_W - 120, 26),
                cv2.FONT_HERSHEY_DUPLEX, 0.55, (50, 255, 100), 1, cv2.LINE_AA)

# ─── Main Loop ────────────────────────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(WEBCAM_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WINDOW_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WINDOW_H)

    # State tracking per hand (left/right) -> to ensure clean click-and-release
    pinch_states    = {'Left': False, 'Right': False}
    
    last_pressed    = None
    typed_text      = ''
    prev_time       = time.time()
    
    # Store visual press feedback timer
    press_effect_timer = 0
    PRESS_EFFECT_DUR = 0.2  

    print("[AIR KEYBOARD] Starting in CYBER mode...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)                     # mirror
        frame = cv2.resize(frame, (WINDOW_W, WINDOW_H))
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = hands_model.process(rgb)

        hovered_keys = []
        now = time.time()
        
        # Reset visual effect
        if now - press_effect_timer > PRESS_EFFECT_DUR:
            last_pressed = None

        if result.multi_hand_landmarks:
            for hand_idx, hand_lm in enumerate(result.multi_hand_landmarks):
                # Identify if this is the Left or Right hand
                hand_label = result.multi_handedness[hand_idx].classification[0].label

                lm = hand_lm.landmark

                # pixel coords
                ix = int(lm[8].x  * WINDOW_W)
                iy = int(lm[8].y  * WINDOW_H)
                tx = int(lm[4].x  * WINDOW_W)
                ty = int(lm[4].y  * WINDOW_H)
                
                # Hand Scale Calculation for dynamic threshold
                wx = int(lm[0].x * WINDOW_W)
                wy = int(lm[0].y * WINDOW_H)
                mcp_x = int(lm[9].x * WINDOW_W)
                mcp_y = int(lm[9].y * WINDOW_H)
                hand_size = dist((wx, wy), (mcp_x, mcp_y))
                dynamic_threshold = max(20.0, hand_size * 0.28) # auto-adjust for hand depth
                
                # thumb/index for pinch visual (midpoint)
                cx = (ix + tx) // 2
                cy = (iy + ty) // 2

                # draw skeleton with neon cyan
                mp_drawing.draw_landmarks(
                    frame, hand_lm, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(255, 100, 200), thickness=2),
                )

                # USE INDEX TIP (ix, iy) FOR HOVER AIMING! The midpoint causes users to miss keys since they naturally point with the index tip.
                hovered = get_hovered_key(ix, iy)
                hovered_keys.append(hovered)

                # PINCH DETECTION STATE MACHINE
                pinch_d = dist((ix, iy), (tx, ty))
                
                # Hysteresis for stability
                if pinch_states[hand_label]:
                    is_currently_pinched = (pinch_d < dynamic_threshold + (hand_size * 0.15))
                else:
                    is_currently_pinched = (pinch_d < dynamic_threshold)

                # Determine if it's a NEW pinch
                if is_currently_pinched and not pinch_states[hand_label]:
                    # Just pinched!
                    # Draw a flash
                    cv2.circle(frame, (cx, cy), 40, (50, 255, 100), 3)
                    
                    if hovered:
                        label = hovered['label']
                        last_pressed = label
                        press_effect_timer = now

                        # send key
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

                        print(f"[{hand_label} Hand] Typed: {label!r}  |  Buffer: {typed_text!r}")
                
                # Update visual indicator based on pinch
                if is_currently_pinched:
                    cv2.circle(frame, (cx, cy), 15, (50, 255, 100), -1) # Green = Pinched
                else:
                    cv2.circle(frame, (ix, iy), 10, (255, 100, 200), -1) # Pink = Exploring
                    cv2.circle(frame, (tx, ty),  8, (255, 100, 200), -1)

                # Update state for next frame
                pinch_states[hand_label] = is_currently_pinched

        # ── Draw UI ───────────────────────────────────────────────────────────
        draw_keyboard(frame, hovered_keys, last_pressed, typed_text)

        now  = time.time()
        fps  = 1.0 / max(now - prev_time, 1e-9)
        prev_time = now
        draw_hud(frame, fps)

        cv2.imshow('Cyber Air Keyboard', frame)
        if cv2.waitKey(1) & 0xFF == 27:   # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n[AIR KEYBOARD] Session ended.")

if __name__ == '__main__':
    main()
