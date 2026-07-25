import sys
import time
import tkinter as tk

import cv2
import numpy as np
from PIL import Image, ImageTk
from ultralytics import YOLO

# ---------------- CONFIG ----------------
REMINDER_INTERVAL_MINUTES = 30      # how often the reminder pops up
TEST_MODE = False               # True = short interval for quick testing. False = real 30-min reminders.
TEST_INTERVAL_SECONDS = 5

CONFIDENCE_THRESHOLD = 0.25         # detection confidence needed (0-1) — lower = easier/faster to detect
CONFIRM_SECONDS_NEEDED = 0.5        # how many seconds of continuous water-showing before it dismisses
CAMERA_INDEX = 0                    

WATER_CLASSES = {"bottle", "glass"}

REQUIRE_LIQUID_CHECK = True         # set False to go back to "any bottle/cup counts"
LIQUID_EDGE_THRESHOLD = 0.045       # lower = easier to pass (more lenient). Tune using the on-screen live score.
# -----------------------------------------

print("Loading detection model...")
try:
    MODEL = YOLO("yolo11n.pt")     
    print("Model ready: YOLO11n")
except Exception as e:
    print(f"YOLO11n unavailable ({e}), falling back to YOLOv8n...")
    MODEL = YOLO("yolov8n.pt")
    print("Model ready: YOLOv8n")


def liquid_score(crop):
    if crop is None or crop.size == 0:
        return 0.0
    h, w = crop.shape[:2]
    if h < 10 or w < 10:
        return 0.0
    lower = crop[int(h * 0.35):h, :]
    gray = cv2.cvtColor(lower, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 40, 130)
    return float(np.count_nonzero(edges)) / edges.size


class WaterReminderOverlay:
    def __init__(self):
        self.root = None
        self.cap = None
        self.detect_start_time = None
        self.running = False
        self.video_label = None
        self.status_label = None

    def show(self):
        self.running = True
        self.detect_start_time = None

        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#0a1f33")
        self.root.title("Drink Water!")

        # Block the normal window-close button — dismissing requires showing water
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        tk.Label(
            self.root, text="💧 Time to Drink Water!",
            font=("Helvetica", 46, "bold"), fg="#ffffff", bg="#0a1f33"
        ).pack(pady=(60, 10))

        self.status_label = tk.Label(
            self.root, text="Show me a bottle or glass of water to dismiss this reminder",
            font=("Helvetica", 18), fg="#8ecae6", bg="#0a1f33"
        )
        self.status_label.pack(pady=(0, 20))

        self.video_label = tk.Label(self.root, bg="#0a1f33")
        self.video_label.pack()

        tk.Label(
            self.root, text="(Ctrl+C in the terminal fully stops the program)",
            font=("Helvetica", 11), fg="#4a6a85", bg="#0a1f33"
        ).pack(side="bottom", pady=20)

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.update_frame()
        self.root.mainloop()

    def update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.status_label.config(text="Camera not found — check your webcam connection", fg="#e63946")
            self.root.after(500, self.update_frame)
            return

        frame = cv2.flip(frame, 1)
        results = MODEL.predict(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)[0]

        water_detected = False
        best_score = 0.0
        for box in results.boxes:
            cls_name = MODEL.names[int(box.cls[0])]
            if cls_name in WATER_CLASSES:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                x1, y1 = max(x1, 0), max(y1, 0)
                crop = frame[y1:y2, x1:x2]
                score = liquid_score(crop)
                best_score = max(best_score, score)

                has_liquid = (not REQUIRE_LIQUID_CHECK) or (score >= LIQUID_EDGE_THRESHOLD)
                box_color = (0, 255, 0) if has_liquid else (0, 165, 255)
                label = f"{cls_name} {score:.3f}" if REQUIRE_LIQUID_CHECK else cls_name

                cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 3)
                cv2.putText(frame, label, (x1, max(y1 - 10, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, box_color, 2)

                if has_liquid:
                    water_detected = True

        if water_detected:
            if self.detect_start_time is None:
                self.detect_start_time = time.time()
            elapsed = time.time() - self.detect_start_time
            remaining = CONFIRM_SECONDS_NEEDED - elapsed
            if remaining > 0:
                self.status_label.config(text=f"Water detected! Hold steady... ({remaining:.1f}s)", fg="#4caf50")
            else:
                self.status_label.config(text="Confirmed! Stay hydrated 💧", fg="#4caf50")
        else:
            self.detect_start_time = None
            if REQUIRE_LIQUID_CHECK and best_score > 0:
                self.status_label.config(
                    text=f"Container seen but looks empty (score {best_score:.3f}) — show one with water",
                    fg="#ffb703"
                )
            else:
                self.status_label.config(
                    text="Show me a bottle or glass of water to dismiss this reminder", fg="#8ecae6"
                )

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb).resize((640, 480))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

        if self.detect_start_time is not None and (time.time() - self.detect_start_time) >= CONFIRM_SECONDS_NEEDED:
            self.dismiss()
            return

        self.root.after(30, self.update_frame)

    def dismiss(self):
        self.running = False
        if self.cap:
            self.cap.release()
        if self.root:
            self.root.destroy()


def reminder_loop():
    interval = TEST_INTERVAL_SECONDS if TEST_MODE else REMINDER_INTERVAL_MINUTES * 60
    print(f"Water Reminder running. Next reminder in {interval} seconds.")
    print("Press Ctrl+C to stop.\n")
    while True:
        time.sleep(interval)
        WaterReminderOverlay().show()  # blocks until water is confirmed
        print(f"Dismissed. Next reminder in {interval} seconds.")


if __name__ == "__main__":
    try:
        reminder_loop()
    except KeyboardInterrupt:
        print("\nStopped. Stay hydrated!")
        sys.exit(0)