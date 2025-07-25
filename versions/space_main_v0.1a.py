## Cursor and Click Control with Camera Feed

import cv2
import mediapipe as mp
import pyautogui

# Webcam setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # reduce lag
screen_width, screen_height = pyautogui.size()

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Mouse smoothing and state trackers
prev_x, prev_y = 0, 0
state = "idle"
fist_frames = 0
open_frames = 0

# Threshold tuning
FIST_TAP_FRAMES = 1
FIST_HOLD_FRAMES = 7
OPEN_HOLD_FRAMES = 3

def is_fist_strict(landmarks, h, w):
    """True if all fingers are curled (fist)."""
    tip_ids = [8, 12, 16, 20]   # fingertips
    mcp_ids = [5, 9, 13, 17]    # finger base joints

    for tip, mcp in zip(tip_ids, mcp_ids):
        tip_y = landmarks[tip].y * h
        mcp_y = landmarks[mcp].y * h
        if tip_y < mcp_y - 20:  # finger is extended
            return False
    return True

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture = "None"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark

            # Cursor movement
            palm_x, palm_y = int(lm[9].x * w), int(lm[9].y * h)
            screen_x = int((palm_x / w) * screen_width)
            screen_y = int((palm_y / h) * screen_height)
            smooth_x = int(prev_x + (screen_x - prev_x) * 0.2)
            smooth_y = int(prev_y + (screen_y - prev_y) * 0.2)
            pyautogui.moveTo(smooth_x, smooth_y)
            prev_x, prev_y = smooth_x, smooth_y

            # Fist detection
            if is_fist_strict(lm, h, w):
                fist_frames += 1
                open_frames = 0
                gesture = f"FIST ({fist_frames})"
            else:
                open_frames += 1
                fist_frames = 0
                gesture = f"OPEN ({open_frames})"

            # Click logic
            if state == "idle":
                if fist_frames == FIST_TAP_FRAMES:
                    pyautogui.mouseDown()
                    state = "pressed"
                    gesture = "CLICK START"

            elif state == "pressed":
                if open_frames >= OPEN_HOLD_FRAMES:
                    pyautogui.mouseUp()
                    if fist_frames < FIST_HOLD_FRAMES:
                        pyautogui.click()
                        gesture = "CLICK TAP"
                    state = "idle"

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Debug text
    cv2.putText(frame, f"State: {state}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.putText(frame, f"Gesture: {gesture}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

    cv2.imshow("Touchless Interface", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
