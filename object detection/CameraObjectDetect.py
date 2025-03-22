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

# Model
ROAD_SIGN_DETECTION_MODEL = path('efficientdet-lite-ELEC390-road-signs.tflite')
ROAD_SIGN_DETECTION_MODEL_EDGETPU = path('efficientdet-lite-ELEC390-road-signs_edgetpu.tflite')

# Labels
ROAD_SIGN_DETECTION_LABELS = path('ELEC390labels.txt')

detector = vision.Detector(ROAD_SIGN_DETECTION_MODEL_EDGETPU)
labels = read_label_file(ROAD_SIGN_DETECTION_LABELS)

for frame in vision.get_frames():
    objects = detector.get_objects(frame, threshold=0.4)
    vision.draw_objects(frame, objects, labels)

def getObjects_in_frame(frame):
    objects = detector.get_objects(frame, threshold = 0.4)
    return objects

def getObj_in_Objs(objs, label_name):
    for obj in objs:
        if labels.get(obj.id) == label_name:
            return obj
        return None

def getLabels_in_frame(objects):
    for obj in objects:
        labels_list = [labels.get(obj.id)]
    return labels_list

def getObjPixelHeight(object):
    bbox = object.bbox
    return bbox.ymax - bbox.ymin

def getObjPixelWidth(object):
    return object.bbox.xmax - object.bbox.xmin



    