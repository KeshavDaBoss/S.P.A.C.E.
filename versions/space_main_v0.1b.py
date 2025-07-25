##Scrolling Gesture Detection with Camera Feed

import cv2
import mediapipe as mp
import pyautogui
import time

cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

last_scroll_time = 0
SCROLL_INTERVAL = 0.5

def get_scroll_direction(lm, h):
    tip = lm[8].y * h
    pip = lm[6].y * h
    middle = lm[12].y * h
    ring = lm[16].y * h
    pinky = lm[20].y * h

    print(f"[DEBUG] Tip: {tip:.2f} | Base: {pip:.2f} | M: {middle:.2f} | R: {ring:.2f} | P: {pinky:.2f}")

    scroll_up = tip < pip - 35 and all(f > tip + 10 for f in [middle, ring, pinky])
    scroll_down = tip > pip + 40 and all(f < tip - 30 for f in [middle, ring, pinky])

    if scroll_up:
        return "up"
    elif scroll_down:
        return "down"
    return None

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture = "No scroll gesture"
    current_time = time.time()

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            direction = get_scroll_direction(lm, h)

            if direction == "up" and current_time - last_scroll_time > SCROLL_INTERVAL:
                gesture = "SCROLL UP 🔼"
                pyautogui.press("up")
                last_scroll_time = current_time

            elif direction == "down" and current_time - last_scroll_time > SCROLL_INTERVAL:
                gesture = "SCROLL DOWN 🔽"
                pyautogui.press("down")
                last_scroll_time = current_time

    cv2.putText(frame, gesture, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.imshow("Final Scroll Fix", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
