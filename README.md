# S.P.A.C.E.
**Spacial Pointer And Control Environment**  
_A gesture-based touchless system for controlling your device with hand movements._

---

## Overview

S.P.A.C.E. is a Python-based interface that allows users to control system actions — like mouse movement, clicks, scrolling, and keypresses — using only hand gestures and a webcam. No external hardware is needed.

The system is built using:

- [MediaPipe](https://github.com/google/mediapipe) for hand tracking
- [OpenCV](https://opencv.org/) for video capture and image processing
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for simulating keyboard and mouse input

---

## Features


###Gesture – Action Mapping

1) Middle, Pointer, and Ring Finger Up – Play/Pause/Enter (Enter)
2) Pointer Finger Up – Scroll up (UP Arrow Key)
3) Pointer Finger Down – Scroll down (DOWN Arrow Key)
4) Open/Close Fist – Click (Left Mouse Key)
5) Move Palm – Move Mouse
6) Pointer and Middle Finger Up – Right Click

---

## How It Works

### 1. Input Capture
- Captures webcam feed using OpenCV (`cv2.VideoCapture`).
- Flips the image for mirrored interaction.

### 2. Hand Detection
- Uses MediaPipe's 21-point hand landmark model.
- Landmarks include all finger joints, tips, and the wrist.

### 3. Gesture Recognition
- Gestures are identified by checking relative positions between landmarks.
  - Example: If the index fingertip is above its base and other fingers are curled → pointing up.
- Each gesture has a condition function and cooldown to prevent accidental repetition.

### 4. System Control
- `pyautogui` is used to:
  - Move the mouse based on hand position
  - Simulate clicks and drags
  - Press Page Up, Page Down, Enter keys

---

## Requirements

- Python 3.9 or 3.10 (MediaPipe may break on newer versions)
- A working webcam
- OS: Windows (tested), Linux (not tested), macOS (not tested)

---

## Installation

### 1. Install Python 3.10

Download from: [https://www.python.org/downloads/release/python-3100/](https://www.python.org/downloads/release/python-3100/)

### 2. Install Required Libraries

Open your terminal or command prompt and run:

```bash
pip install mediapipe opencv-python pyautogui
```

### 3. Run the Program

Navigate to your project directory and run:

```bash
python space_main_v1.1-gui.py
```
Make sure your webcam is connected and camera permission is granted.

## Tips for Best Results

-> Ensure your hand is fully visible in the camera frame.
-> Use clear and deliberate gestures.
-> Bright lighting improves detection accuracy.
-> Avoid fast motion or background clutter.

## Customizing or Extending

To add your own gestures:

1) Learn the landmark indices from MediaPipe.
2) Write a new condition function in `space_main.py`.
2) Trigger a new pyautogui event like `pyautogui.press('z')` or `pyautogui.hotkey()`.

## Credits
Developer: Pratham Yadav
Technical Assistant: ChatGPT by OpenAI
Libraries Used:
-> MediaPipe
-> OpenCV
-> PyAutoGUI

## License
This software is released for personal and educational use.
Reuse, modification, and redistribution are permitted with attribution.
