from unittest import result

from flask import Flask, render_template, request, jsonify
from deepface import DeepFace
import numpy as np
import time
import base64
import cv2

from flask import Response
import cv2

from collections import Counter

emotion_history = []   # ✅ correct

app = Flask(__name__)

camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
@app.route('/video')
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# -----------------------------
# Stress logic (FROM YOUR CODE)
# -----------------------------
def emotion_to_stress_percent(emotion, previous):
    base = {
        "happy": 10,
        "surprise": 20,
        "neutral": 35,
        "sad": 70,
        "fear": 85,
        "angry": 95
    }
    target = base.get(emotion, 50)
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
        return {
            "avoid": "Avoid multitasking and overcommitment",
            "alter": "Break large tasks into smaller steps",
            "adapt": "Practice breathing or short relaxation"
        }

    elif level == "MODERATE":
        return {
            "avoid": "Avoid unnecessary distractions",
            "alter": "Adjust workload balance",
            "adapt": "Take short mindful breaks"
        }

    else:  # LOW
        return {
            "avoid": "Avoid complacency",
            "alter": "Maintain routine",
            "adapt": "Continue healthy habits"
        }
# -----------------------------
# GLOBAL STATE (10 sec logic)
# -----------------------------
start_time = None
stress_values = []
locked_result = None
previous_stress = 50

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/reset")
def reset():
    global start_time, stress_values, locked_result, previous_stress, emotion_history
    start_time = None
    stress_values = []
    locked_result = None
    previous_stress = 50
    emotion_history.clear()
    return jsonify({"status": "reset"})



@app.route("/analyze", methods=["GET"])
def analyze():
    global start_time, stress_values, locked_result, previous_stress, emotion_history

    if locked_result:
        return jsonify(locked_result)

    success, frame = camera.read()
    if not success:
        return jsonify({"status": "detecting"})

    result = DeepFace.analyze(
        frame,
        actions=["emotion"],
        enforce_detection=False
    )

    # 1️⃣ Raw emotion
    # Get full emotion probabilities
    emotions = result[0]["emotion"]

    # If happy confidence is strong → force happy
    if emotions["happy"] > 60:
        raw_emotion = "happy"
    else:
        raw_emotion = result[0]["dominant_emotion"]

    # 2️⃣ Emotion smoothing (MOST IMPORTANT)
    emotion_history.append(raw_emotion)
    if len(emotion_history) > 10:
        emotion_history.pop(0)

    emotion = Counter(emotion_history).most_common(1)[0][0]

    # 3️⃣ Convert emotion → stress
    stress = emotion_to_stress_percent(emotion, previous_stress)
    

    # 5️⃣ Prevent sudden jumps
    if abs(stress - previous_stress) > 10:
        stress = previous_stress + (10 if stress > previous_stress else -10)

    previous_stress = stress
    stress_values.append(stress)

    # 6️⃣ Timer logic
    if start_time is None:
        start_time = time.time()

    elapsed = time.time() - start_time

    if elapsed >= 10:
        avg = int(np.mean(stress_values))
        level = classify_stress(avg)

        locked_result = {
            "status": "locked",
            "stress_percent": avg,
            "stress_level": level,
            "suggestions": get_suggestions(level)
        }
        return jsonify(locked_result)

    # 7️⃣ Live scanning response
    return jsonify({
        "status": "scanning",
        "stress_percent": stress,
        "stress_level": classify_stress(stress),
        "time_left": int(10 - elapsed)
    })

if __name__ == "__main__":
    app.run(debug=True)