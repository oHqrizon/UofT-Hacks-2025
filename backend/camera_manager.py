import cv2
import threading
import time
import os

class CameraManager:
    _instance = None
    _lock = threading.Lock()
    _camera = None
    _ref_count = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def acquire_camera(self):
        with self._lock:
            if self._camera is None:
                for _ in range(3):  # Try 3 times
                    try:
                        if os.name == 'nt':  # Windows
                            self._camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                        else:  # Other OS
                            self._camera = cv2.VideoCapture(0)
                            
                        if self._camera.isOpened():
                            # Configure camera
                            self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                            self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                            self._camera.set(cv2.CAP_PROP_FPS, 30)
                            self._camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                            
                            # Test read
                            ret, frame = self._camera.read()
                            if ret and frame is not None:
                                self._ref_count += 1
                                return self._camera
                                
                            self._camera.release()
                            self._camera = None
                            
                    except Exception as e:
                        print(f"Camera acquisition attempt failed: {e}")
                        if self._camera:
                            self._camera.release()
                            self._camera = None
                    time.sleep(1)
                    
                raise Exception("Failed to initialize camera after multiple attempts")
            else:
                self._ref_count += 1
                return self._camera

    def release_camera(self):
        with self._lock:
            if self._camera is not None:
                self._ref_count -= 1
                if self._ref_count <= 0:
                    self._camera.release()
                    self._camera = None
                    self._ref_count = 0
                    cv2.destroyAllWindows()
                    time.sleep(0.5)

    def read_frame(self):
        with self._lock:
            if self._camera is not None and self._camera.isOpened():
                return self._camera.read()
            return False, None 