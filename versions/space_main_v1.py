import cv2
import mediapipe as mp
import pyautogui
import time

wScr, hScr = pyautogui.size()

cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

clicking = False
click_cooldown = 0
right_click_time = 0
enter_press_time = 0
scroll_time = 0

SCROLL_INTERVAL = 0.5
RIGHT_CLICK_COOLDOWN = 1
ENTER_COOLDOWN = 1
CLICK_HOLD_DELAY = 0.15

def get_palm_position_scaled(lm, w, h):
    x_raw = (lm[0].x + lm[5].x + lm[9].x + lm[13].x + lm[17].x) / 5
    y_raw = (lm[0].y + lm[5].y + lm[9].y + lm[13].y + lm[17].y) / 5
    x_scaled = min(max((x_raw - 0.1) / 0.8, 0), 1)
    y_scaled = min(max((y_raw - 0.1) / 0.8, 0), 1)
    return int(x_scaled * w), int(y_scaled * h)

def detect_scroll(lm, h):
    tip = lm[8].y * h
    base = lm[6].y * h
    middle = lm[12].y * h
    ring = lm[16].y * h
    pinky = lm[20].y * h

    scroll_up = tip < base - 40 and all(f > tip + 10 for f in [middle, ring, pinky])
    scroll_down = tip > base + 40 and all(f < tip - 15 for f in [middle, ring, pinky])

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
    up_fingers = sum([
        lm[8].y * h < lm[6].y * h,
        lm[12].y * h < lm[10].y * h,
        lm[16].y * h < lm[14].y * h,
        lm[20].y * h < lm[18].y * h
    ])
    return up_fingers >= 3

def is_right_click(lm, h):
    index_up = lm[8].y * h < lm[6].y * h - 15
    middle_up = lm[12].y * h < lm[10].y * h - 15
    ring_down = lm[16].y * h > lm[14].y * h + 25
    pinky_down = lm[20].y * h > lm[18].y * h + 25
    return index_up and middle_up and ring_down and pinky_down

def is_enter_gesture(lm, h):
    index_up = lm[8].y * h < lm[6].y * h - 15
    middle_up = lm[12].y * h < lm[10].y * h - 15
    ring_up = lm[16].y * h < lm[14].y * h - 15
    pinky_down = lm[20].y * h > lm[18].y * h + 10
    thumb_folded = abs(lm[4].x - lm[2].x) < 0.05
    return index_up and middle_up and ring_up and pinky_down and thumb_folded

prev_enter_state = False

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    current_time = time.time()

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark

            # Cursor
            palm_x, palm_y = get_palm_position_scaled(lm, w, h)
            screen_x = int(palm_x * wScr / w)
            screen_y = int(palm_y * hScr / h)
            pyautogui.moveTo(screen_x, screen_y, duration=0.01)

            # Scroll
            scroll_dir = detect_scroll(lm, h)
            if scroll_dir == "up" and current_time - scroll_time > SCROLL_INTERVAL:
                pyautogui.press("pageup")
                scroll_time = current_time
            elif scroll_dir == "down" and current_time - scroll_time > SCROLL_INTERVAL:
                pyautogui.press("pagedown")
                scroll_time = current_time

            # Click + Drag
            if is_full_fist(lm, h):
                if not clicking and current_time - click_cooldown > CLICK_HOLD_DELAY:
                    pyautogui.mouseDown()
                    clicking = True
            elif is_fist_released(lm, h):
                if clicking:
                    pyautogui.mouseUp()
                    clicking = False
                    click_cooldown = current_time

            # Right click
            if is_right_click(lm, h) and (current_time - right_click_time > RIGHT_CLICK_COOLDOWN):
                pyautogui.click(button='right')
                right_click_time = current_time

            # ENTER key
            enter_now = is_enter_gesture(lm, h)
            if enter_now and not prev_enter_state and (current_time - enter_press_time > ENTER_COOLDOWN):
                pyautogui.press("enter")
                enter_press_time = current_time
            prev_enter_state = enter_now

    else:
        clicking = False
        prev_enter_state = False

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
