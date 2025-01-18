import numpy as np
import argparse
import matplotlib.pyplot as plt
import cv2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# command line argument
ap = argparse.ArgumentParser()
ap.add_argument("--mode",help="train/display")
mode = ap.parse_args().mode

faceexist=0
faceexistpercent=0
posinterest=0
neginterest=0
suminterest=0
absinterest=0
netinterest=0
pospercent=0
negpercent=0
netpercent=0

# New variables for teaching proficiency analysis
confidence_score = 0
consistency_score = 0
previous_emotion = None
emotion_changes = 0
teaching_duration = 0
confidence_indicators = {
    "Neutral": 0.7,    
    "Happy": 1.0,      
    "Surprised": 0.3,  
    "Angry": -0.5,     
    "Sad": -0.3,
    "Scared": -0.8,
    "Disgust": -0.4
}

abspercent=0
alcond=0
facetrue=0
facefalse=0
angrycount=0
disgustcount=0
scaredcount=0
happycount=0
neutralcount=0
sadcount=0
surprisedcount=0
angrypercent=0
disgustpercent=0
scaredpercent=0
happypercent=0
neutralpercent=0
sadpercent=0
surprisedpercent=0
facecond= ""
temp=1
maxrespon=0
respon=""
impression=""
faceval=0
presence2=""

# Create the model
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

model.load_weights('model.h5')

# prevents openCL usage and unnecessary logging messages
cv2.ocl.setUseOpenCL(False)

# dictionary which assigns each label an emotion (alphabetical order)
emotion_dict = {0: "Negatif - Marah", 1: "Negatif - Jijik", 2: "Negatif - Takut", 3: "Positif - Senang", 4: "Netral - Netral", 5: "Negatif - Sedih", 6: "Positif - Terkejut"}

# start the webcam feed
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if (cap.isOpened()== False):
    print("Unable to read video")

# Default resolutions of the frame are obtained
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

out = cv2.VideoWriter('output_emotion.mp4',cv2.VideoWriter_fourcc("m", "p", "4", "v"), 20, (frame_width,frame_height))

while True:
    # Find haar cascade to draw bounding box around face
    ret, frame = cap.read()
    if not ret:
        break
    facecasc = cv2.CascadeClassifier('haarcascade_files/haarcascade_frontalface_default.xml')
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facecasc.detectMultiScale(gray,scaleFactor=1.3, minNeighbors=5)

    face_found = False
    for (x, y, w, h) in faces:
        if w > 0:
            face_found = True
            
        cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
        prediction = model.predict(cropped_img)
        maxindex = int(np.argmax(prediction))
        cv2.putText(frame, emotion_dict[maxindex], (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
        angrycount=0
        disgustcount=0
        scaredcount=0
        happycount=0
        neutralcount=0
        sadcount=0
        surprisedcount=0

        if maxindex ==0:
            angrycount=1
            neginterest+=1
        elif maxindex ==1:
            disgustcount=1
            neginterest+=1
        elif maxindex ==2:
            scaredcount=1
            neginterest+=1
        elif maxindex ==3:
            happycount=1
            posinterest+=1
        elif maxindex ==4:
            neutralcount=1
            netinterest+=1
        elif maxindex == 5:
            sadcount=1
            neginterest+=1
        elif maxindex == 6:
            surprisedcount = 1
            posinterest+=1
        else:
            absinterest+=1
       
        suminterest=angrycount+disgustcount+scaredcount+happycount+neutralcount+sadcount+surprisedcount
        faceexist=posinterest+neginterest
        
        pospercent=round(((posinterest * 100) / suminterest),2) if suminterest != 0 else 0
        negpercent=round((neginterest*100/suminterest),2) if suminterest != 0 else 0
        netpercent=round((netinterest*100/suminterest),2) if suminterest != 0 else 0
        neutralpercent=round((neutralcount*100/suminterest),2) if suminterest != 0 else 0
        disgustpercent=round((disgustcount*100/suminterest),2) if suminterest != 0 else 0
        angrypercent=round((angrycount*100/suminterest),2) if suminterest != 0 else 0
        happypercent=round((happycount*100/suminterest),2) if suminterest != 0 else 0
        sadpercent=round((sadcount*100/suminterest),2) if suminterest != 0 else 0
        surprisedpercent=round((surprisedcount*100/suminterest),2) if suminterest != 0 else 0
        scaredpercent=round((scaredcount*100/suminterest),2) if suminterest != 0 else 0
        
    if face_found is True:
        facecond = "Ya"
        faceval += 1
        
        # Track emotion consistency
        if previous_emotion is not None and previous_emotion != respon:
            emotion_changes += 1
        previous_emotion = respon
        teaching_duration += 1
        
        # Calculate confidence score
        current_confidence = confidence_indicators.get(respon, 0)
        confidence_score += current_confidence
        
        # Calculate consistency score
        if teaching_duration > 0:
            consistency_score = 1 - (emotion_changes / teaching_duration)
            
            # Calculate overall teaching proficiency
            avg_confidence = confidence_score / teaching_duration
            proficiency_score = (avg_confidence + consistency_score) / 2
            proficiency_score = max(0, min(1, proficiency_score))  # Normalize between 0 and 1
            proficiency_percentage = round(proficiency_score * 100, 2)
    else:
        facecond = "Tidak"
        
    maxrespon=max(netpercent,pospercent,negpercent)
    if netpercent==maxrespon and netpercent!=0:
        respon="Netral"
    elif pospercent==maxrespon and pospercent!=0:
        respon="Positif"
    elif negpercent==maxrespon and negpercent!=0:
        respon="Negatif"
    else:
        respon="No Attendance (null)"

    if netpercent+pospercent < negpercent and (netpercent+pospercent!=0):
        impression="Bad"
    elif netpercent+pospercent >= negpercent and negpercent!=0:
        impression="Good"
    else:
        impression="No Attendance (null)"

    emotion_counts = {
        "Angry": angrycount,
        "Disgust": disgustcount,
        "Scared": scaredcount,
        "Happy": happycount,
        "Neutral": neutralcount,
        "Sad": sadcount,
        "Surprised": surprisedcount
    }

    respon = max(emotion_counts, key=emotion_counts.get)
        
    cv2.putText(frame, "  Presence: " + str(respon), (20, 410), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv2.putText(frame, "  Impression: " + str(impression), (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv2.putText(frame, "  Overall Emotional Response: " + str(respon), (20, 490), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    if teaching_duration > 0:
        cv2.putText(frame, f"Teaching Proficiency: {proficiency_percentage}%", (20, 530),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        cv2.putText(frame, f"Emotional Consistency: {round(consistency_score * 100, 2)}%", (20, 570),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        cv2.putText(frame, f"Confidence Level: {round(avg_confidence * 100, 2)}%", (20, 610),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    out.write(frame)
    cv2.imshow("Participant Detection and Emotion Recognition", frame)
    
    if faceval>=1:
        presence2="Yes"
    else:
        presence2="No"
    
    f = open("resultEmotion.txt", "w")
    f.write("Participant Detection and Emotion Recognition \n")
    f.write("Teaching Proficiency Analysis \n\n")
    f.write("  Presence                   : " + str(presence2) + "\n")
    f.write("  Impression                 : " + str(impression)+"\n")
    f.write("  Overall Emotional Response : " + str(respon)+"\n\n")
    
    if teaching_duration > 0:
        f.write(f"  Teaching Proficiency Score : {proficiency_percentage}%\n")
        f.write(f"  Emotional Consistency     : {round(consistency_score * 100, 2)}%\n")
        f.write(f"  Confidence Level          : {round(avg_confidence * 100, 2)}%\n\n")
    
    f.write("  Percentage Neutral  : " + str(netpercent) + " % \n")
    f.write("  Percentage Positive : " + str(pospercent) + " % \n")
    f.write("  Percentage Negative : " + str(negpercent) + " % \n\n")
    
    f.write("  Neutral Count   : " + str(netinterest)+"\n")
    f.write("  Positive Count  : " + str(posinterest)+"\n")
    f.write("  Negative Count  : " + str(neginterest)+"\n\n")
    
    f.write("Detailed Emotion Breakdown:\n")
    f.write("  Neutral:   " + str(neutralpercent)+" % \n")
    f.write("  Happy:     " + str(happypercent)+" % \n")
    f.write("  Sad:       " + str(sadpercent)+" % \n")
    f.write("  Angry:     " + str(angrypercent)+" % \n")
    f.write("  Scared:    " + str(scaredpercent)+" % \n")
    f.write("  Surprised: " + str(surprisedpercent)+" % \n")
    f.write("  Disgust:   " + str(disgustpercent)+" % \n")
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()