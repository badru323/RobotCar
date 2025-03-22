import CameraObjectDetect as ObjDet 
from aiymakerkit import vision
from aiymakerkit import utils
from pycoral.utils.dataset import read_label_file
import cv2
from picarx import Picarx
import CarStates as sm

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
    dist = getPhysicalHeight(label)*focal_length/ObjDet.getObjPixelHeight(obj)
    return dist

def getDistace_W(label, obj):
    return getPhysicalHeight(label)*focal_length/ObjDet.getObjPixelWidth(obj)

def detectStop():
    current_state = 'stop' #px.stop()
    # getDistance_H("sign_stop", ObjDet.getObj_in_Objs(objs, "sign_stop"))

def detectYield(): 
    
    
def obj_detect():
    while True: 
        for frame in vision.get_frames(): 
            objects = ObjDet.getObjects_in_frame(frame)
            labels_list = ObjDet.getLabels_in_frame(objects)
            for label in labels_list: 
                
                

