import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from queue import Queue
import laneDetection_Main as lane_detect
from pid_control import PIDController as pid
from picarx import Picarx 
import velocity_control as speed
import lane_processing as lane

def error(frame):
    center = 320 // 2
    error = center - lane.getLanes(frame)[0] 
    return error 

def set_steering(angle,px):
    angle = max(-45, min(45, angle)) # bounded
    px.set_servo_angle(angle)

def steering_control_for_lanes(image_queue):
    if not image_queue.empty():
        dt = time.time() - prev_time
        prev_time = time.time()
        lane_error = error(image_queue.get())
        steering_angle = pid.update(lane_error, dt)
        set_steering(steering_angle)

def turn_right(right_angle, px):
    set_steering(right_angle,px) 
    speed.set_speed(50) 
    time.sleep(1.7)
    set_steering(0,px)

def turn_left(left_angle,px):
    speed.set_speed(50)
    time.sleep(0.68)
    set_steering(left_angle,px)
    time.sleep(2)
    set_steering(0,px)





