"""
Demonstration of the GazeTracking library.
Check the README.md for complete documentation.
"""
import imutils
import cv2
from cam.gaze_tracking import GazeTracking
import time, datetime
import numpy as np


def eyegaze():
    gaze = GazeTracking()

    ongaze=0
    offgaze=0
    sumtask=0
    absgaze=0
    focuspercent=0
    distractedpercent=0
    abspercent=0
    onscreen=0
    offscreen=0
    onscreenpercent=0
    offscreenpercent=0
    maxpresence=0
    att=""



    cap = cv2.VideoCapture(0)

    if (cap.isOpened() == False):
        print("Unable to read video")

    # Default resolutions of the frame are obtained.The default resolutions are system dependent.
    # We convert the resolutions from float to integer.
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # Define the codec and create VideoWriter object.The output is stored in 'output_gaze.mp4' file.
    # Define the fps to be equal to 10. Also frame size is passed.


    out = cv2.VideoWriter('output_eyegaze.mp4',cv2.VideoWriter_fourcc("m", "p", "4", "v"), 20, (frame_width,frame_height))

    while True:
        # We get a new frame from the webcam
        ret, frame = cap.read()


        
        if ret == True:
            # We send this frame to GazeTracking to analyze it
            gaze.refresh(frame)
            frame = gaze.annotated_frame()
            
            # use grayscale for faster processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            text = ""
            #left_pupil = gaze.pupil_left_coords()
            #right_pupil = gaze.pupil_right_coords()
            vertical_c = gaze.vertical_ratio()
            horizontal_c = gaze.horizontal_ratio()
            
            if vertical_c is None or horizontal_c is None:
                text = "Eyes not detected"
                absgaze += 1
            elif vertical_c<=0.4 or vertical_c>=0.6 or horizontal_c<=0.44 or horizontal_c>=0.74:
                text = "Eyes not paying attention"
                offgaze += 1
                
            else:
                text = "Eyes paying attention"
                ongaze += 1

            angle_from_vertical = gaze.get_head_pose_direction(gray, draw_line = True)

            if angle_from_vertical > 60 and angle_from_vertical < 95:
                face_direction = "Right"
            elif angle_from_vertical < -60:
                face_direction = "Left"
            elif angle_from_vertical  == 100:
                face_direction = "No face detected"
            else:
                face_direction = "Center"

            # detect face(s)
            sumtask=ongaze+offgaze+absgaze
            focuspercent=round((ongaze * 100 / sumtask),2) if sumtask != 0 else 0
            #distractedpercent=round((offgaze*100/sumtask),2)
            abspercent=round((absgaze*100/sumtask),2) if sumtask != 0 else 0
            onscreen=ongaze
            offscreen=offgaze+absgaze
            onscreenpercent=focuspercent
            offscreenpercent=round((offscreen*100/sumtask),2) if sumtask != 0 else 0
            
            maxpresence=max(onscreenpercent,offscreenpercent,abspercent)
            if onscreenpercent==maxpresence:
                att="On Screen"
            elif offscreenpercent==maxpresence and abspercent!=100:
                att="Off Screen"
            elif abspercent==100:
                att="No Attendance (null)"
            
            
            cv2.putText(frame,text,(50,450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            cv2.putText(frame,"Overall Attendance : " + str(att),(50,490), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
            cv2.putText(frame, "Facing Direction : " + str(face_direction), (50, 530), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0,255, 0), 2)
            cv2.putText(frame, "Off Screen Percentage              : " + str(offscreenpercent) + " %", (50, 560), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0,255, 0), 2)
            cv2.putText(frame, "Eyes not detected percentage   : " + str(abspercent) + " %", (50, 590), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0,255, 0), 2)
            cv2.putText(frame, "Number of eyes paying attention       : " + str(ongaze), (50, 620), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0,255, 0), 2)
            cv2.putText(frame, "Number of eyes not paying attention : " + str(offgaze), (50, 650), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0,255, 0), 2)
            # cv2.putText(frame, "Number of eyes not detected      : " + str(absgaze), (50, 680), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0,255, 0), 2)

                
            cv2.putText(frame, str(text), (50, 680), cv2.FONT_HERSHEY_DUPLEX, 1, (147, 58, 31), 3,cv2.LINE_AA)
            
            
            
            
            #cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
            #cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
            cv2.putText(frame, "Iris Horizontal:  " + str(horizontal_c), (30, 50), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
            cv2.putText(frame, "Iris Vertical:  " + str(vertical_c), (30, 80), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
            out.write(frame)
            cv2.imshow("EyeGaze On Screen-Off Screen Detection", frame)
    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            return [text, face_direction]
        # Break the loop
        else:
            break

    # When everything done, release the video capture and video write objects
    cap.release()
    out.release()

    # Closes all the frames
    cv2.destroyAllWindows()
