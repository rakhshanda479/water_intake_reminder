''Water Intake Reminder'' Computer Vision Project

A hydration reminder that doesn't take "later" for an answer. Every 30 minutes it takes over your screen, and only closes once your webcam sees you holding up a bottle or glass with water in it.

Built with YOLO11n (Ultralytics' pretrained object detector) for real-time bottle/cup detection, plus an OpenCV heuristic to tell an empty container from a filled one.

Features
Fullscreen, always-on-top reminder every 30 minutes (configurable)
Live webcam detection of bottles/cups/glasses — pretrained model, no training needed
Empty vs. filled check, so waving an empty bottle doesn't count
Must show water continuously for ~2 seconds before it dismisses
Optional Windows auto-start via Task Scheduler
How it works
A background timer waits, then launches a fullscreen popup.
YOLO11n scans the webcam feed for bottle, cup, or wine glass.
A second check looks at the lower part of the detected box for the edge/texture pattern a liquid surface creates — distinguishing empty from filled.
