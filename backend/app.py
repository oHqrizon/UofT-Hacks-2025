from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from transcribe import TranscriptionService
from camera_manager import CameraManager
from emotion_cam import EmotionDetector
import threading
import os
import cv2
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global instances
transcription_service = None
emotion_detector = None
camera_manager = CameraManager()

def generate_frames():
    global emotion_detector
    while True:
        if emotion_detector is None:
            break
        
        frame = emotion_detector.get_frame()
        if frame is None:
            continue
            
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/test-camera', methods=['GET'])
def test_camera():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return jsonify({"status": "error", "message": "Could not open camera"}), 500
            
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return jsonify({"status": "error", "message": "Could not read from camera"}), 500
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/start-session', methods=['POST'])
def start_session():
    global emotion_detector, transcription_service
    try:
        data = request.json
        subject = data.get('subject', '')
        logger.info("Starting new session for subject: %s", subject)
        
        # Start transcription service first
        try:
            if transcription_service is None:
                logger.info("Initializing transcription service...")
                transcription_service = TranscriptionService()
                thread = threading.Thread(target=transcription_service.start_recording)
                thread.daemon = True
                thread.start()
                logger.info("Transcription service started successfully")
        except Exception as e:
            logger.error("Failed to start transcription service: %s", str(e))
            logger.error(traceback.format_exc())
            return jsonify({"status": "error", "message": "Failed to start transcription"}), 500
            
        # Initialize and start emotion detector
        try:
            logger.info("Initializing emotion detector...")
            emotion_detector = EmotionDetector()
            if not emotion_detector.start():
                raise Exception("Failed to start emotion detector")
            logger.info("Emotion detector started successfully")
        except Exception as e:
            logger.error("Failed to start emotion detector: %s", str(e))
            logger.error(traceback.format_exc())
            # Continue even if emotion detector fails
            
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error("Error in start_session: %s", str(e))
        logger.error(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stop-session', methods=['POST'])
def stop_session():
    global emotion_detector, transcription_service
    try:
        logger.info("Stopping session...")
            
        # Stop emotion detector
        try:
            if emotion_detector:
                logger.info("Stopping emotion detector...")
                emotion_detector.stop()
                emotion_detector = None
                logger.info("Emotion detector stopped successfully")
        except Exception as e:
            logger.error("Error stopping emotion detector: %s", str(e))
            logger.error(traceback.format_exc())
            
        # Stop transcription
        try:
            if transcription_service:
                logger.info("Stopping transcription service...")
                transcription_service.stop_recording()
                transcription_service = None
                logger.info("Transcription service stopped successfully")
        except Exception as e:
            logger.error("Error stopping transcription: %s", str(e))
            logger.error(traceback.format_exc())
            
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error("Error in stop_session: %s", str(e))
        logger.error(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/set-subject', methods=['POST'])
def set_subject():
    try:
        data = request.json
        subject = data.get('subject', '')
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    global emotion_detector
    try:
        if emotion_detector:
            metrics = emotion_detector.get_current_metrics()
            return jsonify(metrics)
        return jsonify({"error": "No active session"}), 404
    except Exception as e:
        logger.error("Error getting metrics: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure the transcripts directory exists
    os.makedirs("transcripts", exist_ok=True)
    logger.info("Starting Flask server...")
    app.run(debug=True)