from flask import Flask, Response, jsonify
import cv2
import numpy as np
from cam.emotion_cam import EmotionDetector  # Updated import path
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

emotion_detector = None

@app.route('/start-session', methods=['POST'])
def start_session():
    global emotion_detector
    emotion_detector = EmotionDetector()
    return jsonify({"status": "started"})

@app.route('/video-feed')
def video_feed():
    def generate():
        global emotion_detector
        while True:
            frame, metrics = emotion_detector.process_frame()
            if frame is None:
                break
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/end-session', methods=['POST'])
def end_session():
    global emotion_detector
    if emotion_detector:
        results = emotion_detector.get_final_results()
        emotion_detector.release()
        emotion_detector = None
        return jsonify(results)
    return jsonify({"error": "No active session"})

@app.route('/get-metrics', methods=['GET'])
def get_metrics():
    global emotion_detector
    if emotion_detector:
        return jsonify(emotion_detector.get_current_metrics())
    return jsonify({"error": "No active session"})

if __name__ == '__main__':
    app.run(debug=True)