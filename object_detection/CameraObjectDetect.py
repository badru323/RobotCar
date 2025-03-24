"""
Performs continuous object detection with the camera.

Simply run the script and it will draw boxes around detected objects along 
with the predicted labels:

    python3 detect_road_signs.py
"""

from aiymakerkit import vision
from aiymakerkit import utils
from pycoral.utils.dataset import read_label_file
import cv2

import os.path

def path(name):
    root = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(root, 'models', name)

def main():
    # Model
    ROAD_SIGN_DETECTION_MODEL = path('efficientdet-lite-ELEC390-traffic-signs.tflite')
    ROAD_SIGN_DETECTION_MODEL_EDGETPU = path('efficientdet-lite-ELEC390-traffic-signs_edgetpu.tflite')

    # Labels
    ROAD_SIGN_DETECTION_LABELS = path('ELEC390labels.txt')

    detector = vision.Detector(ROAD_SIGN_DETECTION_MODEL_EDGETPU)
    labels = read_label_file(ROAD_SIGN_DETECTION_LABELS)

    for frame in vision.get_frames():
        objects = detector.get_objects(frame, threshold=0.4)
        vision.draw_objects(frame, objects, labels)
    return detector, labels



    