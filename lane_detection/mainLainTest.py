import time
import threading
from picarx import Picarx
import picarx as Picarx
import LaneTest 
from Camera import camera_feed as cam


# Initialize PiCar
px = Picarx()

def run_picar():
    try:
        print("Starting PiCar...")
        cam.start_camera_thread()
        px.forward(50)
        LaneTest.start_lane_threads()
        while True:
            time.sleep(1)  # Keep running
    except KeyboardInterrupt:
        print("Stopping PiCar...")
        px.stop()

if __name__ == "__main__":
    run_picar()
