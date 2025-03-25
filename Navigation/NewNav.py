import time
import cv2
import numpy as np

from picarx import Picarx
import lane_processing  as laneDetection  # use new lane_processing module
import APFAlgorithm
from vpfs_client import VPFSClient
import Map_Navigation as map_navigation  # alias for consistency
from state_machine import PiCarStateMachine

SERVER_IP = "127.0.0.1"
TEAM_NUM = 49
AUTH_KEY = "49"

NAV_EPSILON = 0.10  # waypoint threshold in meters
PIXEL_TO_METER = 0.01

def navigation_loop():
    car = Picarx()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not accessible.")
        return

    vpfs = VPFSClient(SERVER_IP, TEAM_NUM, AUTH_KEY)
    state_machine = PiCarStateMachine(car)

    active_fare = None
    pickup_done = False
    dropoff_done = False

    waypoints = []
    waypoint_index = 0

    object_queue = Queue()

    try:
        while True:
            match_info = vpfs.check_match()
            if not match_info or not match_info.get("inMatch", False):
                print("Not in an active match. Waiting...")
                time.sleep(2)
                continue

            if match_info["timeRemain"] < 0:
                print("Match ended. Stopping navigation.")
                break

            fare_status = vpfs.get_current_fare()
            if fare_status:
                fare_info = fare_status.get("fare", None)
                if fare_info:
                    active_fare = fare_info
                    pickup_done = fare_info.get("pickedUp", False)
                    dropoff_done = fare_info.get("completed", False)
                else:
                    active_fare = None
                    pickup_done = False
                    dropoff_done = False
            else:
                active_fare = None

            if dropoff_done and active_fare:
                print("Fare completed. Clearing active fare for a new claim.")
                active_fare = None
                waypoints = []
                waypoint_index = 0

            if not active_fare:
                print("No active fare, searching for fares...")
                fares = vpfs.get_fares()
                for f in fares:
                    if not f.get("claimed", True):
                        success, msg = vpfs.claim_fare(f["id"])
                        if success:
                            print(f"Claimed fare {f['id']}")
                            active_fare = f
                            pickup_done = False
                            dropoff_done = False
                            break
                        else:
                            print(f"Failed to claim fare {f['id']}: {msg}")
                if not active_fare:
                    print("No fare claimed, waiting...")
                    time.sleep(2)
                    continue

            if active_fare and not pickup_done:
                target_x = active_fare["src"]["x"]
                target_y = active_fare["src"]["y"]
                print(f"Navigating to pickup at ({target_x:.2f}, {target_y:.2f})")
            elif active_fare:
                target_x = active_fare["dest"]["x"]
                target_y = active_fare["dest"]["y"]
                print(f"Navigating to dropoff at ({target_x:.2f}, {target_y:.2f})")
            else:
                car.forward(0)
                time.sleep(1)
                continue

            pos_data = vpfs.get_position()
            if not pos_data or "position" not in pos_data:
                print("No GPS position. Stopping briefly.")
                car.forward(0)
                time.sleep(1)
                continue
            curr_x = pos_data["position"]["x"]
            curr_y = pos_data["position"]["y"]

            if not waypoints or waypoint_index >= len(waypoints):
                waypoints = map_navigation.plan_route(curr_x, curr_y, target_x, target_y)
                waypoint_index = 0
                if not waypoints:
                    print("No route found. Stopping briefly.")
                    car.forward(0)
                    time.sleep(2)
                    continue

            final_waypoint = waypoints[-1]
            final_dist = map_navigation.euclidean_dist(final_waypoint, (curr_x, curr_y))
            if final_dist < NAV_EPSILON:
                print("Reached final target. Stopping to register pickup/dropoff.")
                car.forward(0)
                time.sleep(2)
                continue

            ret, frame = cap.read()
            if not ret:
                print("Camera read failed.")
                car.forward(0)
                time.sleep(1)
                continue

            detected_objects = []  # Placeholder for object detection integration
            object_queue.put(detected_objects)
            state_machine.process_objects(object_queue)

            wx, wy = waypoints[waypoint_index]
            dist_to_wp = map_navigation.euclidean_dist((wx, wy), (curr_x, curr_y))
            if dist_to_wp < NAV_EPSILON:
                print(f"Reached waypoint {waypoint_index}.")
                waypoint_index += 1
                continue

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("User interrupted.")
    finally:
        car.forward(0)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    navigation_loop()
