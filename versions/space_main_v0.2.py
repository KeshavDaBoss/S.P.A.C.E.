## v0.1a and b COMBINED- Cursor, Scrolling, Clicking Control with Camera Feed

import cv2
import mediapipe as mp
import pyautogui
import time

wScr, hScr = pyautogui.size()

cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
draw = mp.solutions.drawing_utils

clicking = False
last_scroll_time = 0
SCROLL_INTERVAL = 0.5

def get_palm_position_scaled(lm, w, h):
    x_raw = (lm[0].x + lm[5].x + lm[9].x + lm[13].x + lm[17].x) / 5
    y_raw = (lm[0].y + lm[5].y + lm[9].y + lm[13].y + lm[17].y) / 5

    # Scaled mapping to reach screen edges better
    x_scaled = min(max((x_raw - 0.1) / 0.8, 0), 1)
    y_scaled = min(max((y_raw - 0.1) / 0.8, 0), 1)

    return int(x_scaled * w), int(y_scaled * h)

def detect_scroll(lm, h):
    tip = lm[8].y * h
    pip = lm[6].y * h
    middle = lm[12].y * h
    ring = lm[16].y * h
    pinky = lm[20].y * h

    scroll_up = tip < pip - 35 and all(f > tip + 10 for f in [middle, ring, pinky])
    scroll_down = tip > pip + 40 and all(f < tip - 30 for f in [middle, ring, pinky])

    if scroll_up:
        return "up"
    elif scroll_down:
        return "down"
    return None

def is_full_fist(lm, h):
    return all([
        lm[8].y * h > lm[6].y * h + 25,
        lm[12].y * h > lm[10].y * h + 25,
        lm[16].y * h > lm[14].y * h + 25,
        lm[20].y * h > lm[18].y * h + 25
    ])

def is_fist_released(lm, h):
    return any([
        lm[8].y * h < lm[6].y * h + 5,
        lm[12].y * h < lm[10].y * h + 5,
        lm[16].y * h < lm[14].y * h + 5,
        lm[20].y * h < lm[18].y * h + 5
    ])

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture = ""
    current_time = time.time()

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark
            draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Cursor movement
            palm_x, palm_y = get_palm_position_scaled(lm, w, h)
            screen_x = int(palm_x * wScr / w)
            screen_y = int(palm_y * hScr / h)
            pyautogui.moveTo(screen_x, screen_y, duration=0.01)
            gesture = "Moving Cursor"

            # Scroll detection
            scroll_direction = detect_scroll(lm, h)
            if scroll_direction == "up" and current_time - last_scroll_time > SCROLL_INTERVAL:
                pyautogui.press("up")
                gesture = "SCROLL UP 🔼"
                last_scroll_time = current_time

            elif scroll_direction == "down" and current_time - last_scroll_time > SCROLL_INTERVAL:
                pyautogui.press("down")
                gesture = "SCROLL DOWN 🔽"
                last_scroll_time = current_time

            # Click detection
            if is_full_fist(lm, h) and not clicking:
                pyautogui.mouseDown()
                clicking = True
                gesture = "Clicking ⬇"

            elif is_fist_released(lm, h) and clicking:
                pyautogui.mouseUp()
                clicking = False
                gesture = "Click Released ⬆"

    else:
        clicking = False  # Reset if hand lost

    cv2.putText(frame, gesture, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Touchless Interface Alpha (Expanded FOV)", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
