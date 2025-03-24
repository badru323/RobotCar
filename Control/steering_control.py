import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from queue import Queue
import laneDetection_Main as lane_detect
from pid_control import PIDController as pid
from picarx import Picarx 


def get_center(frame):
    lane_edges = frame.shape
    _, width = lane_edges.shape
    if np.any(lane_edges>0):
        lane_center = np.mean(np.where(lane_edges > 0)[1])
    else:
        lane_center = width//2
    return lane_center

def error(frame):
    _, width = frame.shape
    center = width // 2
    error = center - get_center(frame)
    return error 

def set_steering(angle,px):
    angle = max(-45, min(45, angle)) # bounded
    px.set_servo_angle(angle)

def steering_control_for_lanes(lane_queue):
    if not lane_queue.empty():
        dt = time.time() - prev_time
        prev_time = time.time()
        lane_error = error(lane_queue.get())
        steering_angle = pid.update(lane_error, dt)
        set_steering(steering_angle)

def steering_control_for_objects(obj_queue):
    if not obj_queue.empty():
        object_detected = obj_queue.get()

        if obj_detected:
            state_machine(obj) ## Need to implement



