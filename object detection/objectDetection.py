import CameraObjectDetect as ObjDet 
from aiymakerkit import vision
from aiymakerkit import utils
from pycoral.utils.dataset import read_label_file
import cv2
from picarx import Picarx
import multiprocessing

focal_length = 593.1712

def getPhysicalHeight(label):
    if label == "sign_stop":
        return 50.00
    elif label == "sign_oneway_right":
        return 25.00
    elif label == "sign_oneway_left":
        return 25.00
    elif label == "sign_yield":
        return 47.00
    elif label == "sign_noentry":
        return 40.00
    elif label == "traffic_cone":
        return 15.00
    elif label == "road_oneway":
        return 75.00 # width length of the one way signs
    
def getPhysicalWidth(label):
    if label == "sign_stop":
        return 50.00
    elif label == "sign_oneway_right":
        return 75.00
    elif label == "sign_oneway_left":
        return 75.00
    elif label == "sign_yield":
        return 54.00
    elif label == "sign_noentry":
        return 40.00
    elif label == "traffic_cone":
        return 15.50
    elif label == "road_oneway":
        return 25.00 # height length of the one way signs

def getDistance_H(label, obj):
    dist = getPhysicalHeight(label)*focal_length/getObjPixelHeight(obj)
    return dist

def getDistace_W(label, obj):
    return getPhysicalHeight(label)*focal_length/getObjPixelWidth(obj)

def getObjPixelHeight(object):
    bbox = object.bbox
    return bbox.ymax - bbox.ymin

def getObjPixelWidth(object):
    return object.bbox.xmax - object.bbox.xmin

def obj_detect_process(obj_queue):
    for frame in vision.get_frames(): 
        objects = ObjDet.detector.get_objects(frame, threshold=0.4)
        detected_data = []

        for obj in objects:
            label = ObjDet.labels.get(obj.id)
            if label:
                dist = getDistance_H(label, obj)
                detected_data.append((label, dist)) 
        
        # send detected objects and their distances
        obj_queue.put(detected_data)

def start_object_detection(object_queue):
    """ Launch object detection as a separate process. """
    process = multiprocessing.Process(target=obj_detect_process, args=(object_queue,))
    process.start()
    return process # activates in main node

    


