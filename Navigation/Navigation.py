import cv2
import numpy as np
import time
from picarx import Picarx
import APFAlgorithm
import laneDetection

# Global variables that APFAlgorithm uses
goal = (0, 100) 
obstacle = (0, 1000)

def create_grid(x_min, x_max, y_min, y_max, step):
    x = np.arange(x_min, x_max + step, step)
    y = np.arange(y_min, y_max + step, step)
    X, Y = np.meshgrid(x, y)
    return X, Y

def get_lane_center(frame):
    gray = laneDetection.grey_scale(frame)
    blurred = laneDetection.guass_blur(gray)
    edges = laneDetection.canny_edge_det(blurred, 50, 150)
    
    h, w = edges.shape
    mask = np.zeros_like(edges)
    polygon = np.array([[
        (0, h),
        (w * 0.45, h * 0.5),
        (w * 0.55, h * 0.5),
        (w, h)
    ]], np.int32)
    cv2.fillPoly(mask, polygon, 255)
    masked_edges = cv2.bitwise_and(edges, mask)
    
    histogram = np.sum(masked_edges[int(h/2):, :], axis=0)
    if np.sum(histogram) > 0:
        peak_x = np.argmax(histogram)
        lane_offset = peak_x - (w // 2)
    else:
        lane_offset = 0
    return lane_offset

def navigation_loop():
    global goal, obstacle
    car = Picarx()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not accessible")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            lane_offset = get_lane_center(frame)
            goal = lane_offset, 100

            # Read the ultrasonic sensor (from ObjectAvoidance.py logic)
            distance = round(car.ultrasonic.read(), 2)
            if distance < 40:
                obstacle = (0, distance)
            else:
                obstacle = (0, 1000)

            X, Y = create_grid(-50, 50, 0, 150, 10)
            
            steering_direction = APFAlgorithm.obstacleAvoidance(X, Y)
            print("Steering direction (degrees):", steering_direction)

            servo_command = steering_direction - 90
            car.set_dir_servo_angle(servo_command)

            car.forward(50)

            # This can be used for debugging. Not necessary for final product.
            cv2.imshow("Navigation Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Small delay
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Navigation interrupted by user.")
    finally:
        car.forward(0)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    navigation_loop()
