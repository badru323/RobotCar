import cv2
import numpy as np
import threading
import queue
import time
from camera_feed import start_camera_thread, image_queue
from pid_control import PIDController
from picarx import Picarx

# Queues for inter-thread communication
canny_queue = queue.Queue()
roi_queue = queue.Queue()
hough_queue = queue.Queue()
average_queue = queue.Queue()
drawn_image_queue = queue.Queue()
lane_queue = queue.Queue()

# Initialize PID controller and PiCar
pid_controller = PIDController(Kp=0.5, Ki=0.01, Kd=0.1)
px = Picarx()
prev_time = time.time()

def coords(image, parameters):
    slope, intercept = parameters
    y1 = image.shape[0]
    y2 = int(y1 * (4 / 5))
    if slope == 0:
        return np.array([0, y1, 0, y2])
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    return np.array([x1, y1, x2, y2])

def avg(image, lines):
    left, right = [], []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        slope, intercept = np.polyfit((x1, x2), (y1, y2), 1)
        (left if slope < 0 else right).append([slope, intercept])
    left_line = coords(image, np.mean(left, axis=0)) if left else None
    right_line = coords(image, np.mean(right, axis=0)) if right else None
    return np.array([l for l in [left_line, right_line] if l is not None])

def canny(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    return cv2.Canny(blur, 50, 150)

def region_of_interest(image):
    height, width = image.shape[:2]
    polygons = np.array([[
        (int(0.1 * width), height),
        (int(0.45 * width), int(0.6 * height)),
        (int(0.55 * width), int(0.6 * height)),
        (width, height)
    ]])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, 255)
    return cv2.bitwise_and(image, mask)

def draw_lines(image, lines):
    img = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 10)
    return cv2.addWeighted(image, 0.8, img, 1, 1)

def edge_detection():
    while True:
        image = image_queue.get()
        edges = canny(image)
        canny_queue.put((image, edges))

def roi_extraction():
    while True:
        image, edges = canny_queue.get()
        cropped = region_of_interest(edges)
        roi_queue.put((image, cropped))

def hough_transform():
    while True:
        image, cropped = roi_queue.get()
        lines = cv2.HoughLinesP(cropped, 2, np.pi / 180, 100, np.array([]), minLineLength=40, maxLineGap=15)
        hough_queue.put((image, lines))

def lane_averaging():
    while True:
        image, lines = hough_queue.get()
        avg_lines = avg(image, lines) if lines is not None else None
        average_queue.put((image, avg_lines))
        lane_queue.put(avg_lines)

def draw_lanes():
    while True:
        image, avg_lines = average_queue.get()
        final_image = draw_lines(image, avg_lines)
        drawn_image_queue.put(final_image)

def display_output():
    while True:
        final_image = drawn_image_queue.get()
        cv2.imshow("Lane Detection", cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR))
        cv2.waitKey(1)  # Keeps the window open

def get_center(frame):
    lane_edges = frame.shape
    _, width = lane_edges.shape
    if np.any(lane_edges > 0):
        lane_center = np.mean(np.where(lane_edges > 0)[1])
    else:
        lane_center = width // 2
    return lane_center

def error(frame):
    _, width = frame.shape
    center = width // 2
    return center - get_center(frame)

def set_steering(angle, px):
    angle = max(-45, min(45, angle))
    px.set_servo_angle(angle)

def steering_control_for_lanes():
    global prev_time
    while True:
        if not lane_queue.empty():
            frame = lane_queue.get()
            dt = time.time() - prev_time
            prev_time = time.time()
            lane_error = error(frame)
            steering_angle = pid_controller.update(lane_error, dt)
            set_steering(steering_angle, px)

#start_camera_thread()

threads = [
    threading.Thread(target=edge_detection, daemon=True),
    threading.Thread(target=roi_extraction, daemon=True),
    threading.Thread(target=hough_transform, daemon=True),
    threading.Thread(target=lane_averaging, daemon=True),
    threading.Thread(target=draw_lanes, daemon=True),
    threading.Thread(target=display_output, daemon=True),
    threading.Thread(target=steering_control_for_lanes, daemon=True)
]
def start_lane_threads():
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()