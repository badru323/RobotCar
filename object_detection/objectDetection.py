import CameraObjectDetect as ObjDet 
from aiymakerkit import vision
from aiymakerkit import utils
from pycoral.utils.dataset import read_label_file
import cv2
from picarx import Picarx
import multiprocessing

focal_length = 593.1712

def getPhysicalHeight(label): # cm values 
    if label == "sign_stop":
        return 5.0  
    elif label == "sign_oneway_right":
        return 2.5  
    elif label == "sign_oneway_left":
        return 2.5  
    elif label == "sign_yield":
        return 4.7  
    elif label == "sign_noentry":
        return 4.0  
    elif label == "traffic_cone":
        return 1.5  
    elif label == "road_oneway":
        return 7.5  
    else:
        return None

def getPhysicalWidth(label): # cm values 
    if label == "sign_stop":
        return 5.0  
    elif label == "sign_oneway_right":
        return 7.5  
    elif label == "sign_oneway_left":
        return 7.5  
    elif label == "sign_yield":
        return 5.4  
    elif label == "sign_noentry":
        return 4.0  
    elif label == "traffic_cone":
        return 1.55  
    elif label == "road_oneway":
        return 2.5  
    else:
        return None
    
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
        objects, _ = ObjDet.main().get_objects(frame, threshold=0.4)
        detected_data = []

        for obj in objects:
            _, label = ObjDet.main().get(obj.id)
            if label:
                dist = getDistance_H(label, obj)
                detected_data.append((label, dist)) 
        detected_data.sort(key=lambda x: x[1]) # sorted based on their distances (smallest to largest)
        # send detected objects and their distances
        obj_queue.put(detected_data)

def start_object_detection(object_queue):
    """ Launch object detection as a separate process. """
    process = multiprocessing.Process(target=obj_detect_process, args=(object_queue,))
    process.start()
    return process # activates in main node

    


