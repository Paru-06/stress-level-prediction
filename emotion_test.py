from deepface import DeepFace
import cv2
import numpy as np
from collections import deque

# -----------------------------
# Camera setup
# -----------------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera not accessible")
    exit()

# -----------------------------
# Emotion smoothing buffer
# -----------------------------
emotion_buffer = deque(maxlen=15)

# Initial stress value
stress_percent = 50

# -----------------------------
# Helper Functions
# -----------------------------
def emotion_to_stress_percent(emotion, previous):
    base = {
        "happy": 20,
        "surprise": 40,
        "neutral": 55,
        "sad": 70,
        "fear": 85,
        "angry": 90
    }

    target = base.get(emotion, 50)

    # Smooth transition (prevents jumping)
    return int(previous * 0.7 + target * 0.3)


def classify_stress(percent):
    if percent < 35:
        return "LOW"
    elif percent < 65:
        return "MODERATE"
    else:
        return "HIGH"


def get_suggestions(level):
    if level == "HIGH":
        return "Avoid: Reduce workload | Alter: Take breaks | Adapt: Deep breathing"
    elif level == "MODERATE":
        return "Avoid: Plan tasks | Alter: Reduce screen time | Adapt: Light exercise"
    else:
        return "You are relaxed. Maintain healthy habits 😊"


# -----------------------------
# Fullscreen window
# -----------------------------
cv2.namedWindow("AI Stress Monitor", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("AI Stress Monitor",
                      cv2.WND_PROP_FULLSCREEN,
                      cv2.WINDOW_FULLSCREEN)

print("Press Q to quit")

# -----------------------------
# Main loop
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        result = DeepFace.analyze(
            frame,
            actions=['emotion'],
            enforce_detection=False
        )

        emotion = result[0]['dominant_emotion']
        emotion_buffer.append(emotion)

        # Stabilize emotion
        stable_emotion = max(set(emotion_buffer), key=emotion_buffer.count)

        # Smooth stress calculation
        stress_percent = emotion_to_stress_percent(stable_emotion, stress_percent)

        stress_level = classify_stress(stress_percent)
        suggestion = get_suggestions(stress_level)

        # Emoji + color
        if stress_level == "LOW":
            emoji = "😊"
            color = (0, 255, 0)
        elif stress_level == "MODERATE":
            emoji = "😐"
            color = (0, 255, 255)
        else:
            emoji = "😣"
            color = (0, 0, 255)

        # -----------------------------
        # UI TEXT
        # -----------------------------
        cv2.putText(frame, "AI Stress Monitoring System",
                    (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cv2.putText(frame, f"Emotion: {stable_emotion}",
                    (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)

        cv2.putText(frame, f"Stress Level: {stress_level} {emoji}",
                    (30, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        cv2.putText(frame,
                    "I can help you manage your stress",
                    (30, 190),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255), 2)

        cv2.putText(frame, suggestion,
                    (30, 230),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)

        # -----------------------------
        # Stress Bar
        # -----------------------------
        bar_width = int((stress_percent / 100) * frame.shape[1])

        cv2.rectangle(frame,
                      (0, frame.shape[0] - 35),
                      (bar_width, frame.shape[0]),
                      color, -1)

        cv2.putText(frame,
                    f"Stress Intensity: {stress_percent}%",
                    (30, frame.shape[0] - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255,255,255), 2)

    except Exception as e:
        pass

    cv2.imshow("AI Stress Monitor", frame)

    # Exit keys
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty("AI Stress Monitor", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()