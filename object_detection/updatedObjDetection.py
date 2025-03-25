import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from pycoral.utils.dataset import read_label_file
from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
import multiprocessing
import time

# Load labels
LABELS_PATH = "ELEC390labels.txt"
labels = read_label_file(LABELS_PATH)

# Load the TensorFlow Lite model
MODEL_PATH = "efficientdet-lite-ELEC390-road-signs.tflite"  # Update if using EdgeTPU model
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

# Get input size
input_width, input_height = input_size(interpreter)

# Focal length for distance estimation
focal_length = 593.1712

def getPhysicalHeight(label):
    heights = {
        "sign_stop": 5.0,
        "sign_oneway_right": 2.5,
        "sign_oneway_left": 2.5,
        "sign_yield": 4.7,
        "sign_noentry": 4.0,
        "traffic_cone": 1.5,
        "road_oneway": 7.5,
    }
    return heights.get(label, None)

def getObjPixelHeight(obj):
    bbox = obj.bbox
    return bbox.ymax - bbox.ymin

def getDistance_H(label, obj):
    physical_height = getPhysicalHeight(label)
    if physical_height:
        return (physical_height * focal_length) / getObjPixelHeight(obj)
    return None

def detect_objects(frame, obj_queue):
    """ Runs object detection on a frame and sends results to queue."""
    resized_frame = cv2.resize(frame, (input_width, input_height))
    input_data = np.expand_dims(resized_frame, axis=0)

    input_tensor_index = interpreter.get_input_details()[0]['index']
    interpreter.set_tensor(input_tensor_index, input_data.astype(np.uint8))
    interpreter.invoke()

    objs = get_objects(interpreter, score_threshold=0.2)  # Lower threshold for sensitivity
    detected_objects = []

    for obj in objs:
        label = labels.get(obj.id, "Unknown")
        distance = getDistance_H(label, obj)
        if distance:
            detected_objects.append((label, distance))
            print(f"Detected: {label} at {distance:.2f} cm")

    obj_queue.put(detected_objects)

def object_detection_loop(obj_queue):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not accessible.")
        return
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error reading camera frame.")
                break
            detect_objects(frame, obj_queue)
            time.sleep(0.5)  # Reduce CPU usage
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def start_object_detection(obj_queue):
    process = multiprocessing.Process(target=object_detection_loop, args=(obj_queue,))
    process.start()
    return process
