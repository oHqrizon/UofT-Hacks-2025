from flask import Flask, Response, jsonify, render_template
from emotion_cam import EmotionDetector
import cv2
import threading
import time
from flask_cors import CORS
import os
import logging
import numpy as np
from camera_manager import CameraManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Global variables
emotion_detector = None
frame_buffer = None
metrics_buffer = None
is_camera_active = False

# Add a root route
@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "endpoints": {
            "test_camera": "/api/test-camera",
            "start_session": "/api/start-emotion-detection",
            "stop_session": "/api/stop-emotion-detection",
            "video_feed": "/api/video-feed",
            "metrics": "/api/metrics"
        }
    })

# Add error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "message": "The requested endpoint does not exist"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error", "message": str(e)}), 500

def generate_frames():
    global emotion_detector, frame_buffer, metrics_buffer, is_camera_active
    
    try:
        logger.info("Starting frame generation...")
        
        # Clean up existing detector
        if emotion_detector:
            emotion_detector.release()
            emotion_detector = None
            
        time.sleep(1)  # Give more time for cleanup
        
        # Create new detector
        emotion_detector = EmotionDetector()
        logger.info("EmotionDetector initialized successfully")
        
        is_camera_active = True
        failed_frames = 0
        
        while is_camera_active:
            try:
                frame, metrics = emotion_detector.process_frame()
                
                if frame is None:
                    failed_frames += 1
                    if failed_frames > 10:
                        logger.error("Too many failed frames")
                        break
                    time.sleep(0.1)
                    continue
                    
                failed_frames = 0  # Reset on success
                metrics_buffer = metrics
                
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    logger.warning("Failed to encode frame")
                    continue
                    
                frame_buffer = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
                       
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error processing frame: {str(e)}")
                time.sleep(0.1)
                
    except Exception as e:
        logger.error(f"Error in generate_frames: {str(e)}")
        raise
    finally:
        logger.info("Cleaning up camera resources")
        if emotion_detector:
            emotion_detector.release()
            emotion_detector = None

@app.route('/api/start-emotion-detection', methods=['POST'])
def start_emotion_detection():
    global is_camera_active, emotion_detector
    try:
        if emotion_detector:
            emotion_detector.release()
        
        is_camera_active = True
        threading.Thread(target=generate_frames).start()
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop-emotion-detection', methods=['POST'])
def stop_emotion_detection():
    global is_camera_active, emotion_detector
    try:
        is_camera_active = False
        if emotion_detector:
            final_results = emotion_detector.get_final_results()
            emotion_detector.release()
            emotion_detector = None
            return jsonify(final_results)
        return jsonify({"status": "stopped"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/video-feed')
def video_feed():
    try:
        logger.info("Starting video feed...")
        return Response(
            generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        logger.error(f"Video feed error: {str(e)}")
        # Return an error image instead of JSON
        error_img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_img, "Camera Error", (200, 240),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        ret, buffer = cv2.imencode('.jpg', error_img)
        error_frame = buffer.tobytes()
        return Response(
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n',
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

@app.route('/api/metrics')
def get_metrics():
    global metrics_buffer
    return jsonify(metrics_buffer if metrics_buffer else {})

@app.route('/api/test-camera')
def test_camera():
    camera_manager = None
    try:
        logger.info("Testing camera...")
        camera_manager = CameraManager.get_instance()
        cap = camera_manager.acquire_camera()
        
        if not cap or not cap.isOpened():
            raise Exception("Could not open camera")
            
        ret, frame = camera_manager.read_frame()
        if not ret or frame is None:
            raise Exception("Could not read frame from camera")
            
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        logger.info(f"Camera test successful. Frame size: {frame_width}x{frame_height}, FPS: {fps}")
        return jsonify({
            "status": "success",
            "message": "Camera test successful",
            "details": {
                "frame_width": frame_width,
                "frame_height": frame_height,
                "fps": fps
            }
        })
        
    except Exception as e:
        error_msg = f"Camera test failed: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 500
    finally:
        if camera_manager:
            camera_manager.release_camera()

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    global emotion_detector, is_camera_active, frame_buffer, metrics_buffer
    try:
        logger.info("Starting cleanup...")
        is_camera_active = False
        # Wait for any ongoing frame processing to complete
        time.sleep(0.5)  
        if emotion_detector:
            try:
                emotion_detector.release()
            except Exception as e:
                logger.error(f"Error releasing emotion detector: {str(e)}")
            emotion_detector = None
        frame_buffer = None
        metrics_buffer = None
        # Force OpenCV to release any hanging resources
        cv2.destroyAllWindows()
        logger.info("Cleanup completed")
        return jsonify({"status": "cleaned up"})
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Add more detailed logging for startup
    logger.info("Starting Flask server...")
    logger.info("Debug mode: " + str(app.debug))
    logger.info("CORS enabled")
    app.run(debug=True)