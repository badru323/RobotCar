import time
import cv2
import numpy as np

from picarx import Picarx
import lane_processing  as laneDetection  # use new lane_processing module
import APFAlgorithm
from vpfs_client import VPFSClient
import Map_Navigation as map_navigation  # alias for consistency

SERVER_IP = "127.0.0.1"
TEAM_NUM = 49
AUTH_KEY = "49"

NAV_EPSILON = 0.10  # waypoint threshold in meters

# Conversion: ROI width = 300 pixels, center at 150.
# Adjust the conversion factor as needed.
PIXEL_TO_METER = 0.01

def compute_lane_offset(frame):
    midpoints = laneDetection.getLanes(frame)
    if midpoints:
        # Compute average x-coordinate of the detected midpoints
        avg_midpoint = sum(midpoints) / len(midpoints)
        # Calculate offset relative to the ROI center (which is 150 pixels)
        offset_px = avg_midpoint - 150
        offset_m = offset_px * PIXEL_TO_METER
        return offset_m
    else:
        # If no lanes detected, assume no lateral offset
        return 0.0

def compute_servo_angle(apf_angle_degrees):
    servo_angle = 90 - apf_angle_degrees
    return max(min(servo_angle, 90), -90)

def navigation_loop():
    car = Picarx()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not accessible.")
        return

    vpfs = VPFSClient(SERVER_IP, TEAM_NUM, AUTH_KEY)

    active_fare = None
    pickup_done = False
    dropoff_done = False

    # Store the current route (waypoints) and index.
    waypoints = []
    waypoint_index = 0

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

            # Retrieve current fare status.
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

            # If dropoff is complete, clear the fare for a new one.
            if dropoff_done and active_fare:
                print("Fare completed. Clearing active fare for a new claim.")
                active_fare = None
                waypoints = []
                waypoint_index = 0

            # If no active fare, attempt to claim one.
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

            # Set target based on fare status.
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

            # Get current GPS position.
            pos_data = vpfs.get_position()
            if not pos_data or "position" not in pos_data:
                print("No GPS position. Stopping briefly.")
                car.forward(0)
                time.sleep(1)
                continue
            curr_x = pos_data["position"]["x"]
            curr_y = pos_data["position"]["y"]

            # Plan or update route if necessary.
            if not waypoints or waypoint_index >= len(waypoints):
                waypoints = map_navigation.plan_route(curr_x, curr_y, target_x, target_y)
                waypoint_index = 0
                if not waypoints:
                    print("No route found. Stopping briefly.")
                    car.forward(0)
                    time.sleep(2)
                    continue

            # Check if final waypoint is reached.
            final_waypoint = waypoints[-1]
            final_dist = map_navigation.euclidean_dist(final_waypoint, (curr_x, curr_y))
            if final_dist < NAV_EPSILON:
                print("Reached final target. Stopping to register pickup/dropoff.")
                car.forward(0)
                time.sleep(2)
                continue

            # Aim for the current waypoint.
            wx, wy = waypoints[waypoint_index]
            dist_to_wp = map_navigation.euclidean_dist((wx, wy), (curr_x, curr_y))
            if dist_to_wp < NAV_EPSILON:
                print(f"Reached waypoint {waypoint_index}.")
                waypoint_index += 1
                continue

            # Compute global heading from current position to this waypoint.
            heading_deg_map = map_navigation.direct_heading(curr_x, curr_y, wx, wy)

            # Get lane offset using the new lane_processing module.
            ret, frame = cap.read()
            if not ret:
                print("Camera read failed.")
                car.forward(0)
                time.sleep(1)
                continue

            # Compute lane offset (in meters) from detected lane midpoints.
            lane_offset_m = compute_lane_offset(frame)

            # Ultrasonic sensor reading.
            distance_ultra = round(car.ultrasonic.read(), 2)
            if distance_ultra < 30:
                obstacle_dist = distance_ultra / 100.0
            else:
                obstacle_dist = 999.0

            # Compute the local steering angle using the APF algorithm.
            steer_deg = APFAlgorithm.computeSteering(heading_deg_map, lane_offset_m, obstacle_dist)
            servo_angle = compute_servo_angle(steer_deg)
            car.set_dir_servo_angle(servo_angle)
            car.forward(30)

            cv2.imshow("Nav Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("User interrupted.")
    finally:
        car.forward(0)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    navigation_loop()
