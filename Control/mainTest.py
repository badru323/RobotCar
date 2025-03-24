from lane_detection import lane_processing as lane
from velocity_control import VelocityController as speed
import steering_control as steer 
import pid_control as pid
from Camera import camera_feed 
import picarx as Picarx 
from object_detection import objectDetection as obj
import time 
import threading 
import multiprocessing
import queue as Queue


# Initialize PiCar
px = Picarx.Picarx()

obj_queue = Queue()

def start_system():
    print("Starting PiCar System...")
    speed.set_speed(50,px)
    # Start camera feed
    camera_thread = camera_feed.start_camera_thread()
    camera_thread.start()
    
    # Start lane detection
    lane_process = multiprocessing.Process(target=lane.getLanes, daemon=True)
    lane_process.start()
    
    # Start object detection
    object_process = multiprocessing.Process(target=obj.obj_detect_process, args = (obj_queue,))
    object_process.start()
    
    # Start steering control
    steering_thread = threading.Thread(target=steer.steering_control_for_lanes, args = (camera_feed.image_queue,))
    steering_thread.start()
    
    # Start velocity control
    velocity_thread = threading.Thread(target=speed.set_speed, daemon=True)
    velocity_thread.start()
    
    try:
        while True:
            time.sleep(1)  # Keep the system running
    except KeyboardInterrupt:
        print("Stopping PiCar...")
        px.stop()

if __name__ == "__main__":
    start_system()


