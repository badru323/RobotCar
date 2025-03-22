import cv2 
import threading 
import time 
from queue import Queue 

image_queue = Queue(maxsize=10)

def capture_camera_feed():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.Read()
        if ret: 
            resized_frame = cv2.resize(frame, (320,320))
            if not image_queue.full():
                image_queue.put(resized_frame)
        time.sleep(0.05)
        cap.release() # EDIT if needed

def start_camera_thread():
    thread = threading.Thread(capture=capture_camera_feed, daemon=True)
    thread.start()
    
