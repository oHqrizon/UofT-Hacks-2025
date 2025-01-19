import numpy as np
import cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import time
import threading
from camera_manager import CameraManager
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class EmotionDetector:
    camera_lock = threading.Lock()

    def __init__(self):
        try:
            print("\n=== Initializing EmotionDetector ===")
            
            # Initialize variables
            self.cap = None
            self.camera_manager = CameraManager.get_instance()
            self.is_running = False
            
            # Set up paths
            self.base_path = os.path.dirname(os.path.abspath(__file__))
            self.model_path = os.path.join(self.base_path, 'models', 'model.h5')
            self.cascade_path = os.path.join(self.base_path, 'models', 'haarcascade_files', 'haarcascade_frontalface_default.xml')
            
            # Initialize other variables and load model first
            self._init_variables()
            self._load_model()
            
            # Initialize camera last
            self._init_camera()
            
        except Exception as e:
            print(f"Initialization error: {str(e)}")
            self.release()
            raise

    def start(self):
        """Start the emotion detection process"""
        print("Starting emotion detection...")
        self.is_running = True
        return True

    def stop(self):
        """Stop the emotion detection process"""
        print("Stopping emotion detection...")
        self.is_running = False
        self.release()

    def get_frame(self):
        """Process a frame and return it encoded as JPEG"""
        if not self.is_running:
            return None
            
        frame, metrics = self.process_frame()
        if frame is None:
            return None
            
        # Encode the frame as JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            return None
            
        return jpeg.tobytes()

    def _init_variables(self):
        self.emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
        self.start_time = time.time()
        self.last_face_detection_time = time.time()
        self.face_absence_duration = 0
        self.MAX_ACCEPTABLE_ABSENCE = 1.5
        self.total_face_absence_time = 0
        
        # Initialize metrics
        self.netinterest = 0
        self.posinterest = 0
        self.neginterest = 0
        self.suminterest = 0
        self.netpercent = 0
        self.pospercent = 0
        self.negpercent = 0
        self.face_presence_percentage = 100

    def _load_model(self):
        print("Loading model...")
        self.model = self._create_model()
        self.model.load_weights(self.model_path)
        print("Model loaded successfully")

    def _init_camera(self):
        print("\n=== Initializing Camera ===")
        try:
            self.cap = self.camera_manager.acquire_camera()
            if not self.cap or not self.cap.isOpened():
                raise Exception("Failed to acquire camera")
            print("Camera initialized successfully")
        except Exception as e:
            print(f"Camera initialization failed: {str(e)}")
            raise

    def _create_model(self):
        model = Sequential()
        model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48,48,1)))
        model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(1024, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(7, activation='softmax'))
        return model

    def process_frame(self):
        try:
            if not self.cap:
                print("Camera not initialized")
                return None, None
                
            ret, frame = self.camera_manager.read_frame()
            if not ret or frame is None:
                print("Failed to read frame")
                return None, None
                
            facecasc = cv2.CascadeClassifier(self.cascade_path)
            if facecasc.empty():
                raise Exception("Failed to load cascade classifier")

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = facecasc.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            face_found = False
            current_time = time.time()
            
            for (x, y, w, h) in faces:
                if w > 0:
                    face_found = True
                    self.last_face_detection_time = current_time
                    
                cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]
                try:
                    cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
                    prediction = self.model.predict(cropped_img, verbose=0)
                    maxindex = int(np.argmax(prediction))
                    cv2.putText(frame, self.emotion_dict[maxindex], (x+20, y-60), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    
                    self._update_metrics(maxindex)
                except Exception as e:
                    print(f"Error processing face: {str(e)}")
                    continue

            # Calculate face presence
            if not face_found:
                self.face_absence_duration = current_time - self.last_face_detection_time
                if self.face_absence_duration > self.MAX_ACCEPTABLE_ABSENCE:
                    self.total_face_absence_time += 0.5

            total_time = current_time - self.start_time
            if total_time > 0:
                absence_factor = (self.total_face_absence_time / total_time) * 0.3
                recovery_factor = 10  # Adjust this value to control recovery speed
                self.face_presence_percentage = min(100, 100 * (1 - absence_factor) + recovery_factor)

            self._calculate_teaching_effectiveness()
            self._add_metrics_to_frame(frame)
            
            return frame, self.get_current_metrics()
            
        except Exception as e:
            print(f"Error in process_frame: {str(e)}")
            return None, None

    def _update_metrics(self, maxindex):
        # Update emotion counts and percentages
        if maxindex == 4:  # Neutral
            self.netinterest += 1
        elif maxindex in [3, 6]:  # Happy or Surprised
            self.posinterest += 1
        else:  # Negative emotions
            self.neginterest += 1
            
        self.suminterest = self.netinterest + self.posinterest + self.neginterest
        
        if self.suminterest > 0:
            self.netpercent = round((self.netinterest * 100 / self.suminterest), 2)
            self.pospercent = round((self.posinterest * 100 / self.suminterest), 2)
            self.negpercent = round((self.neginterest * 100 / self.suminterest), 2)

    def _calculate_teaching_effectiveness(self):
        # Calculate teaching effectiveness based on all metrics
        self.teaching_effectiveness = (
            (self.pospercent * 0.3) +           # Positive emotions
            (self.netpercent * 0.2) +           # Neutral emotions
            (self.face_presence_percentage * 0.3) + # Face presence
            ((100 - self.negpercent) * 0.2)     # Inverse of negative emotions
        ) / 100
        
        self.effectiveness_percentage = round(self.teaching_effectiveness * 100, 2)

    def _add_metrics_to_frame(self, frame):
        cv2.putText(frame, f"Teaching Effectiveness: {self.effectiveness_percentage}%", 
                   (20, 530), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        cv2.putText(frame, f"Face Presence: {round(self.face_presence_percentage, 2)}%", 
                   (20, 570), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        cv2.putText(frame, f"Positive Emotions: {self.pospercent}%", 
                   (20, 610), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    def get_current_metrics(self):
        return {
            "teaching_effectiveness": self.effectiveness_percentage,
            "face_presence": round(self.face_presence_percentage, 2),
            "positive_emotions": self.pospercent,
            "neutral_emotions": self.netpercent,
            "negative_emotions": self.negpercent
        }

    def get_final_results(self):
        return {
            "final_metrics": self.get_current_metrics(),
            "detailed_breakdown": {
                "neutral_percent": self.netpercent,
                "positive_percent": self.pospercent,
                "negative_percent": self.negpercent,
                "total_face_absence_time": round(self.total_face_absence_time, 2)
            }
        }

    def release(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'camera_manager'):
                self.camera_manager.release_camera()
            self.cap = None
        except Exception as e:
            print(f"Error during release: {str(e)}")