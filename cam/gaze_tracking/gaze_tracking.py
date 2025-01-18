from __future__ import division
import os
import cv2
import dlib
from .eye import Eye
from .calibration import Calibration
import time,datetime
import numpy as np
from math import atan2, degrees


class GazeTracking(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()
        
        

        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor is used to get facial landmarks of a given face
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "trained_models/shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

    @property
    def pupils_located(self):
        """Check that the pupils have been located"""
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False

    def _analyze(self):
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        try:
            landmarks = self._predictor(frame, faces[0])
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)
            self.eye_right = Eye(frame, landmarks, 1, self.calibration)

        except IndexError:
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame):
        """Refreshes the frame and analyzes it.

        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self._analyze()

    def pupil_left_coords(self):
        """Returns the coordinates of the left pupil"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        """Returns the coordinates of the right pupil"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    def horizontal_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        horizontal direction of the gaze. The extreme right is 0.0,
        the center is 0.5 and the extreme left is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.x / (self.eye_left.center[0] * 2)
            pupil_right = self.eye_right.pupil.x / (self.eye_right.center[0] * 2)
            return (pupil_left + pupil_right) / 2


    def vertical_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        vertical direction of the gaze. The extreme top is 0.0,
        the center is 0.5 and the extreme bottom is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.y / (self.eye_left.center[1] * 2)
            pupil_right = self.eye_right.pupil.y / (self.eye_right.center[1] * 2)
            return (pupil_left + pupil_right) / 2

    def is_off_v(self):
        """Returns true if the user is looking away from screen (up and down)"""
        if self.pupils_located:
            return self.vertical_ratio() >= 0.80 or self.vertical_ratio() <= 0.37

    def is_off_h(self):
        """Returns true if the user is looking away from screen (right and left)"""
        if self.pupils_located:
               return self.horizontal_ratio() <= 0.44 or self.horizontal_ratio() >= 0.74

    def is_on_v(self):
        """Returns true if the user is looking on screen"""
        if self.pupils_located:
            return self.vertical_ratio() < 0.80 and self.vertical_ratio() > 0.37
            
    def is_on_h(self):
        """Returns true if the user is looking on screen"""
        if self.pupils_located:
            return self.horizontal_ratio() > 0.44 and self.horizontal_ratio() < 0.74
        
    def is_off(self):
        """Returns true if the user is looking away"""
        if self.is_on_h is False or self.is_on_v is False:
            return True
    def is_on(self):
        """Returns true if the user is looking away"""
        if self.is_on_h is True and self.is_on_v is True:
            return True
        
    def no_eye(self):
        """Returns true if there is np eye"""
        if self.pupils_located is False:
            return True
    
    def is_right(self):
        """Returns true if the user is looking to the right"""
        if self.pupils_located:
            return self.horizontal_ratio() <= 0.35

    def is_left(self):
        """Returns true if the user is looking to the left"""
        if self.pupils_located:
            return self.horizontal_ratio() >= 0.65

    def is_center(self):
        """Returns true if the user is looking to the center"""
        if self.pupils_located:
            return self.is_right() is not True and self.is_left() is not True

    def is_blinking(self):
        """Returns true if the user closes his eyes"""
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2
            return blinking_ratio 

    def annotated_frame(self):
        """Returns the main frame with pupils highlighted"""
        frame = self.frame.copy()

        if self.pupils_located:
            color = (0, 255, 0)
            x_left, y_left = self.pupil_left_coords()
            x_right, y_right = self.pupil_right_coords()
            cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color)
            cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color)
            cv2.line(frame, (x_right - 5, y_right), (x_right + 5, y_right), color)
            cv2.line(frame, (x_right, y_right - 5), (x_right, y_right + 5), color)
            
        return frame
    

    def get_head_pose_direction(self, gray, draw_line=False):
        """
        Computes head pose from the current frame using the nose tip line.
        Returns one of: 'Left', 'Right', 'Center', or None if no face is found.
        
        If draw_line=True, draws the nose tip line on self.frame.
        """
        if self.frame is None:
            return 0 # No frame to analyze (detect as center)
        
        # Convert to gray for face detection
        faces = self._face_detector(gray)

        if len(faces) == 0:
            return 0  # No face detected (detect as center)

        # For simplicity, assume first face
        face = faces[0]  
        landmarks = self._predictor(gray, face)
        
        # 2D image points from `shape_predictor_68_face_landmarks.dat`
        image_points = np.array([
            (landmarks.part(33).x, landmarks.part(33).y),  # Nose tip
            (landmarks.part(8).x,  landmarks.part(8).y),   # Chin
            (landmarks.part(36).x, landmarks.part(36).y),  # Left eye left corner
            (landmarks.part(45).x, landmarks.part(45).y),  # Right eye right corner
            (landmarks.part(48).x, landmarks.part(48).y),  # Left mouth corner
            (landmarks.part(54).x, landmarks.part(54).y)   # Right mouth corner
        ], dtype="double")

        # 3D model points (same ones you used in your second script)
        model_points = np.array([
            (0.0, 0.0, 0.0),         # Nose tip
            (0.0, -330.0, -65.0),    # Chin
            (-225.0, 170.0, -135.0), # Left eye left corner
            (225.0, 170.0, -135.0),  # Right eye right corner
            (-150.0, -150.0, -125.0),# Left mouth corner
            (150.0, -150.0, -125.0)  # Right mouth corner
        ])

        # Camera internals
        (h, w) = self.frame.shape[:2]
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")

        dist_coeffs = np.zeros((4,1))  # Assume no lens distortion
        
        # Solve for head pose
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return 0
        
        # Project a line outward from nose tip
        (nose_end_point2D, jacobian) = cv2.projectPoints(
            np.array([(0.0, 0.0, 1000.0)]),
            rotation_vector, 
            translation_vector, 
            camera_matrix, 
            dist_coeffs
        )

        p1 = (int(image_points[0][0]), int(image_points[0][1]))  # nose tip
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

        if draw_line:
            cv2.line(self.frame, p1, p2, (255, 0, 0), 2)

        # Compute angle from vertical
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        angle_from_vertical = degrees(atan2(dx, dy))
        #  angle_from_vertical ~ 0 => line is straight down
        #  angle_from_vertical > 0 => line angled to the right
        #  angle_from_vertical < 0 => line angled to the left

        # Decide direction (tweak thresholds as you like)
        if angle_from_vertical is not None:
            return angle_from_vertical
        else:
            return 100  # No face detected
