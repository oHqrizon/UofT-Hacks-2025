import cv2
import time

def test_camera():
    print("\n=== Simple Camera Test ===")
    
    # First try to list all cameras
    for i in range(3):
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"Camera {i} is available")
                ret, frame = cap.read()
                if ret:
                    print(f"Successfully read frame from camera {i}: {frame.shape}")
                cap.release()
            else:
                print(f"Camera {i} is not available")
        except Exception as e:
            print(f"Error testing camera {i}: {e}")
    
    print("\nTrying to open main camera...")
    cap = None
    try:
        # Try to open camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Failed to open camera")
            return
        
        print("Camera opened successfully")
        
        # Try to read and display frames
        for i in range(5):
            ret, frame = cap.read()
            if ret:
                print(f"Frame {i+1} read successfully: {frame.shape}")
                
                # Show the frame
                cv2.imshow('Camera Test', frame)
                key = cv2.waitKey(500)  # Wait for 500ms
                if key == 27:  # ESC key
                    break
            else:
                print(f"Failed to read frame {i+1}")
            
            time.sleep(0.1)
            
    except Exception as e:
        print(f"Error during camera test: {e}")
    finally:
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        print("\nCamera test completed")

if __name__ == "__main__":
    test_camera()
    input("Press Enter to exit...") 