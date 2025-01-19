from flask import Flask, request, jsonify
from flask_cors import CORS
from speech.transcribe import TranscriptionService
import threading

app = Flask(__name__)
CORS(app)

# Global transcription service instance
transcription_service = None

@app.route('/start_transcription', methods=['POST'])
def start_transcription():
    global transcription_service
    try:
        transcription_service = TranscriptionService()
        transcription_service.start_recording()
        return jsonify({"status": "success", "message": "Transcription started"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stop_transcription', methods=['POST'])
def stop_transcription():
    global transcription_service
    try:
        if transcription_service:
            transcription_service.stop_recording()
            transcription_service = None
        return jsonify({"status": "success", "message": "Transcription stopped"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 