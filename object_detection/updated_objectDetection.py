import sys 
import os
sys.path.append(os.path.abspath("aiy_maker_kit"))
import time 

# Add the path to your local aiymakerkit module (where your project files are)
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'aiy_maker_kit'))
sys.path.insert(0, project_path)

from aiy_maker_kit.examples import CameraObjectDetect as ObjDet 
from aiy_maker_kit.aiymakerkit import vision
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
    elif label == "duck_regular":
        return 3.0
    elif label == "duck_specialty":
        return 5.0
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
    elif label == "duck_regular":
        return 4.0
    elif label == "duck_specialty":
        return 5.0
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
    print("Object detection process started correctly")
    while True:
        objects, labels = ObjDet.main()  # Call main only once
        if objects:
            print(f"Detected {len(objects)} objects")
        else:
            print("No objects detected in frame")
        detected_data = []

        for obj in objects:
            label = labels.get(obj.id)  # Directly get label from labels
            if label:
                print(label)
                height = getObjPixelHeight(obj)
                if height is not None:
                    dist = getDistance_H(label, obj)
                    detected_data.append((label, dist))
                else:
                    print(f"Warning: Unkown label: '{label}' received.")

            detected_data.sort(key=lambda x: x[1]) # sorted based on their distances (smallest to largest)
            print("Sending detected objects to queue:", detected_data)  # Debugging line
            # send detected objects and their distances
            obj_queue.put(detected_data)

            time.sleep(0.5)


    


