# 💧 Water Intake Reminder

> An intelligent hydration reminder that enforces healthy water consumption using real-time computer vision detection.

A fullscreen reminder that activates every 30 minutes and dismisses only when your webcam confirms you're holding a water-filled bottle or glass. Built with cutting-edge object detection and heuristic analysis to ensure genuine water consumption, not just waving an empty container.

---

## 🎯 Features

- **Persistent Reminders** — Fullscreen, always-on-top alerts every 30 minutes (fully configurable)
- **Real-time Detection** — Live webcam analysis using YOLO11n, no model training required
- **Smart Validation** — Distinguishes filled containers from empty ones using texture analysis
- **Confirmation Window** — Requires continuous water detection for ~2 seconds to dismiss
- **System Integration** — Optional Windows auto-start via Task Scheduler
- **Zero Setup** — Pre-trained model included; works out of the box

---

## 🔧 How It Works

The application follows a three-stage detection pipeline:

1. **Timer Stage** — A background service waits until the reminder interval expires, then triggers a fullscreen popup
2. **Object Detection** — YOLO11n scans the webcam feed in real-time, identifying bottles, cups, and glasses
3. **Liquid Validation** — Analyzes the lower section of detected containers to identify the liquid surface pattern, confirming the container is actually filled
4. **Confirmation** — Once water is continuously detected for `CONFIRM_SECONDS_NEEDED`, the reminder closes automatically

---

## 🛠️ Technical Stack

- **Object Detection**: [YOLO11n](https://docs.ultralytics.com/) (Ultralytics pretrained model)
- **Computer Vision**: OpenCV
- **Language**: Python
- **Platform Support**: Windows (with Task Scheduler integration)

---

## 📋 Requirements

- Python 3.8+
- Webcam
- Windows OS (for Task Scheduler auto-start)

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/rakhshanda479/water_intake_reminder.git
cd water_intake_reminder

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

---

## ⚙️ Configuration

Key settings can be customized in the main configuration:

- `REMINDER_INTERVAL` — Time between reminders (default: 30 minutes)
- `CONFIRM_SECONDS_NEEDED` — Duration to confirm water presence (default: 2 seconds)
- `OBJECT_CLASSES` — Detection targets (bottle, cup, glass)

---

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve detection accuracy or add new features.

---

## 📄 License

This project is open source. See the LICENSE file for details.

---

**Stay hydrated! 💦**
