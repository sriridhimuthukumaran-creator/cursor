

import cv2
import mediapipe as mp
import pyautogui
import math
import time

# ---------- CONFIG ----------
CAM_INDEX       = 0
SMOOTHING       = 6       # higher = smoother, lower = more responsive
CLICK_THRESHOLD = 45      # pixel distance between thumb & index tip to trigger pinch
CLICK_COOLDOWN  = 0.5     # seconds between allowed clicks
FRAME_MARGIN    = 80      # pixels to ignore at frame edges
# ----------------------------

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0       # remove built-in delay

mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
)

screen_w, screen_h = pyautogui.size()
cap   = cv2.VideoCapture(CAM_INDEX)
cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

prev_x, prev_y   = screen_w // 2, screen_h // 2
last_click_time   = 0
is_pinching       = False   # track pinch state to avoid repeat clicks

print(f"Screen: {screen_w}x{screen_h} | Camera: {cam_w}x{cam_h}")
print("Show index finger to move. Pinch thumb+index to click. Press q to quit.")

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    status_text = "No hand detected"
    status_color = (100, 100, 100)

    if result.multi_hand_landmarks:
        lm    = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)
        pts   = lm.landmark

        h, w, _ = frame.shape
        index_tip = pts[8]   # index fingertip
        thumb_tip = pts[4]   # thumb tip

        ix = int(index_tip.x * w)
        iy = int(index_tip.y * h)
        tx = int(thumb_tip.x * w)
        ty = int(thumb_tip.y * h)

        dist = math.hypot(tx - ix, ty - iy)
        pinching_now = dist < CLICK_THRESHOLD

        # Draw fingertips
        cv2.circle(frame, (ix, iy), 12, (0, 255, 0), -1)   # index = green
        cv2.circle(frame, (tx, ty), 12, (255, 100, 0), -1)  # thumb = blue
        cv2.line(frame, (ix, iy), (tx, ty), (200, 200, 200), 1)

        if pinching_now:
            # --- PINCH: freeze cursor, click once per pinch gesture ---
            status_text  = f"PINCH  dist={int(dist)}"
            status_color = (0, 0, 255)
            cv2.circle(frame, (ix, iy), 20, (0, 0, 255), 3)

            if not is_pinching:  # rising edge only
                now = time.time()
                if now - last_click_time > CLICK_COOLDOWN:
                    pyautogui.click()
                    last_click_time = now
                    print("CLICK")
            is_pinching = True

        else:
            # --- INDEX ONLY: move cursor ---
            is_pinching  = False
            status_text  = f"MOVE   dist={int(dist)}"
            status_color = (0, 220, 0)

            # Map camera → screen
            clamped_x = min(max(ix, FRAME_MARGIN), w - FRAME_MARGIN)
            clamped_y = min(max(iy, FRAME_MARGIN), h - FRAME_MARGIN)
            screen_x  = (clamped_x - FRAME_MARGIN) / (w - 2 * FRAME_MARGIN) * screen_w
            screen_y  = (clamped_y - FRAME_MARGIN) / (h - 2 * FRAME_MARGIN) * screen_h

            # Smooth
            curr_x = prev_x + (screen_x - prev_x) / SMOOTHING
            curr_y = prev_y + (screen_y - prev_y) / SMOOTHING
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

    # HUD
    cv2.putText(frame, status_text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
    cv2.putText(frame, f"Threshold: {CLICK_THRESHOLD}px", (20, cam_h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    cv2.imshow("Finger Mouse  |  q = quit", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()