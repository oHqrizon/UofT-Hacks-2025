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
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class EmotionDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.start_time = time.time()
        self.last_face_detection_time = time.time()
        self.face_absence_duration = 0
        self.MAX_ACCEPTABLE_ABSENCE = 1.5
        self.total_face_absence_time = 0
        self.face_presence_percentage = 100
        
        # Initialize metrics
        self.faceexist = 0
        self.faceexistpercent = 0
        self.posinterest = 0
        self.neginterest = 0
        self.suminterest = 0
        self.absinterest = 0
        self.netinterest = 0
        self.pospercent = 0
        self.negpercent = 0
        self.netpercent = 0
        
        # Create and load model
        self.model = self._create_model()
        self.model.load_weights('cam/model.h5')
        
        # Initialize emotion tracking
        self.emotion_dict = {
            0: "Negatif - Marah", 
            1: "Negatif - Jijik", 
            2: "Negatif - Takut", 
            3: "Positif - Senang", 
            4: "Netral - Netral", 
            5: "Negatif - Sedih", 
            6: "Positif - Terkejut"
        }
        
        # Teaching effectiveness variables
        self.teaching_effectiveness = 0
        self.engagement_score = 0
        self.confusion_score = 0
        self.recent_confidence = 0
        self.effectiveness_percentage = 0
        
        # Initialize video writer
        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))
        self.out = cv2.VideoWriter('cam/output_emotion.mp4', 
                                 cv2.VideoWriter_fourcc("m", "p", "4", "v"), 
                                 20, 
                                 (frame_width,frame_height))

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
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        facecasc = cv2.CascadeClassifier('cam/haarcascade_files/haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facecasc.detectMultiScale(gray,scaleFactor=1.3, minNeighbors=5)

        face_found = False
        current_time = time.time()
        
        for (x, y, w, h) in faces:
            if w > 0:
                face_found = True
                self.last_face_detection_time = current_time
                
            cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
            prediction = self.model.predict(cropped_img)
            maxindex = int(np.argmax(prediction))
            cv2.putText(frame, self.emotion_dict[maxindex], (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Update metrics based on emotion detection
            self._update_metrics(maxindex)

        # Calculate face presence
        if not face_found:
            self.face_absence_duration = current_time - self.last_face_detection_time
            if self.face_absence_duration > self.MAX_ACCEPTABLE_ABSENCE:
                self.total_face_absence_time += 0.5

        total_time = current_time - self.start_time
        if total_time > 0:
            self.face_presence_percentage = max(0, min(100, 100 * (1 - (self.total_face_absence_time / total_time) * 2)))

        # Update teaching effectiveness
        self._calculate_teaching_effectiveness()

        # Add metrics to frame
        self._add_metrics_to_frame(frame)
        
        # Write frame to video
        self.out.write(frame)
        
        return frame, self.get_current_metrics()

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
        if self.cap:
            self.cap.release()
        if self.out:
            self.out.release()