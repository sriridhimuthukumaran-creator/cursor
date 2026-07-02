Finger Mouse 

Control your system cursor using just your index finger — no touchscreen needed.

Built with OpenCV + MediaPipe Hands.

Demo


Move index finger → cursor moves
Pinch thumb + index → click



How It Works


Webcam captures your hand in real time
MediaPipe detects 21 hand landmarks
Index fingertip (landmark 8) coordinates are mapped to screen resolution
Pinch distance between thumb (landmark 4) and index tip triggers a click


Setup

bashpip install opencv-python mediapipe pyautogui numpy
python finger_mouse.py

Known Issues


Jittery cursor movement (smoothing is basic)
Click accuracy needs improvement
Linux: requires X11 (doesn't work on Wayland)
Mac: needs Accessibility permission for PyAutoGUI to control the cursor


What's Next


Kalman filter for smoother tracking
Gesture for right-click and scroll
Better pinch detection


Tech Stack


Python
OpenCV
MediaPipe Hands
PyAutoGUI
