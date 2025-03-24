import time
import cv2
import numpy as np

from picarx import Picarx
import laneDetection
import APFAlgorithm
from vpfs_client import VPFSClient
import Map_Navigation

SERVER_IP = "127.0.0.1"
TEAM_NUM = 49
AUTH_KEY = "49"

NAV_EPSILON = 0.10  # how close (in m) we must get to a waypoint

def get_lane_offset(frame):
    gray = laneDetection.grey_scale(frame)
    blurred = laneDetection.guass_blur(gray)
    edges = laneDetection.canny_edge_det(blurred, 50, 150)
    
    # ROI mask
    h, w = edges.shape
    mask = np.zeros_like(edges)
    polygon = np.array([[
        (0, h),
        (w*0.45, h*0.5),
        (w*0.55, h*0.5),
        (w, h)
    ]], dtype=np.int32)
    cv2.fillPoly(mask, polygon, 255)
    masked_edges = cv2.bitwise_and(edges, mask)

    histogram = np.sum(masked_edges[int(h/2):, :], axis=0)
    if np.sum(histogram) > 0:
        peak_x = np.argmax(histogram)
        offset = peak_x - (w // 2)
    else:
        offset = 0
    return offset

def compute_servo_angle(apf_angle_degrees):
    servo_angle = 90 - apf_angle_degrees
    servo_angle = max(min(servo_angle, 90), -90)
    return servo_angle

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

    # store a route of intersections and our current index.
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

            # Check current fare
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

            # If the dropoff is done, release the fare
            if dropoff_done and active_fare:
                print("Fare is completed. Clearing active fare so we can claim another.")
                active_fare = None
                waypoints = []
                waypoint_index = 0

            # If no active fare, claim one
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

            # If we do have a fare, decide if we go to pickup or dropoff
            if active_fare and not pickup_done:
                target_x = active_fare["src"]["x"]
                target_y = active_fare["src"]["y"]
                print(f"Navigating to pickup at ({target_x:.2f}, {target_y:.2f})")
            elif active_fare:
                target_x = active_fare["dest"]["x"]
                target_y = active_fare["dest"]["y"]
                print(f"Navigating to dropoff at ({target_x:.2f}, {target_y:.2f})")
            else:
                # If still no fare, skip the rest
                car.forward(0)
                time.sleep(1)
                continue

            # Get current position
            pos_data = vpfs.get_position()
            if not pos_data or "position" not in pos_data:
                print("No GPS position. Stopping briefly.")
                car.forward(0)
                time.sleep(1)
                continue
            curr_x = pos_data["position"]["x"]
            curr_y = pos_data["position"]["y"]

            # If we have no route or we've reached the end, plan a new route
            if not waypoints or waypoint_index >= len(waypoints):
                waypoints = Map_Navigation.plan_route(curr_x, curr_y, target_x, target_y)
                waypoint_index = 0
                if not waypoints:
                    print("No route found. Stopping briefly.")
                    car.forward(0)
                    time.sleep(2)
                    continue

            # Check if we've reached the final waypoint
            final_waypoint = waypoints[-1]
            final_dist = Map_Navigation.euclidean_dist(final_waypoint, (curr_x, curr_y))
            if final_dist < NAV_EPSILON:
                print("Reached final target. Stopping to register pickup/dropoff.")
                car.forward(0)
                time.sleep(2)
                continue

            # Otherwise, aim for the current waypoint
            wx, wy = waypoints[waypoint_index]
            dist_to_wp = Map_Navigation.euclidean_dist((wx, wy), (curr_x, curr_y))
            if dist_to_wp < NAV_EPSILON:
                print(f"Reached waypoint {waypoint_index}.")
                waypoint_index += 1
                continue

            # Compute heading from current pos to this waypoint
            heading_deg_map = Map_Navigation.direct_heading(curr_x, curr_y, wx, wy)

            # Lane offset from camera
            ret, frame = cap.read()
            if not ret:
                print("Camera read failed.")
                car.forward(0)
                time.sleep(1)
                continue

            lane_offset_px = get_lane_offset(frame)
            lane_offset_m = lane_offset_px * 0.01

            # Ultrasonic
            distance_ultra = round(car.ultrasonic.read(), 2)
            if distance_ultra < 30:
                obstacle_dist = distance_ultra / 100.0
            else:
                obstacle_dist = 999.0

            # APF steering
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
