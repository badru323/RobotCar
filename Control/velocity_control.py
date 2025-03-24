from signal_lights import LED_lights as LED
import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
from queue import Queue
import laneDetection_Main as lane_detect
from pid_control import PIDController as pid
from picarx import Picarx 

class VelocityController:
    NORMAL_SPEED = 50
    def __init__(self,px):
        self.speed = self.NORMAL_SPEED
        self.px = px
    
    def get_speed(self):
        return self.speed

    def set_speed(self, speed):
        brake_lights = False
        if speed < self.get_speed():
            brake_lights = True
        if brake_lights:
            LED.turn_on_gpios(17,4)
        time.sleep(0.1)
        self.speed = speed
        LED.turn_off_gpios(17,4)
        self.px.forward(self.speed)

    def stop(self):
        self.px.stop()
        
    def slow_stop_sign(self, distance): # for a stop sign
        brake_lights = True
        if distance > 50: 
            self.speed = self.NORMAL_SPEED
            brake_lights = False
        elif 50 >= distance > 20:
            self.speed = 30
        elif 20 >= distance > 5:
            self.speed = 10
        else: 
            self.speed = 0

        self.set_speed(self.speed)   

        if brake_lights:
            LED.turn_on_gpios(17,4)
        else:
            LED.turn_off_gpios(17,4)
    
    def yield_for_vehicle(self, distance, rel_vehicle_speed):
        our_vel = self.speed
        target_speed = our_vel + rel_vehicle_speed
        self.set_speed(target_speed)
    
    def yield_sign_control(self, distance):
        brake_lights = True
        if distance > 50: 
            self.speed = self.NORMAL_SPEED  # Maintain normal speed
            brake_lights = False
        elif 50 >= distance > 30:
            self.speed = 30  # Start slowing down
        elif 30 >= distance > 20:
            self.speed = 20  # Slow down further
        elif 20 >= distance > 10:
            self.speed = 10  # Almost stopping
        else: 
            self.speed = 5  # go slow
        if brake_lights:
            LED.turn_on_gpios(17,4)
        self.set_speed(self.speed)  # Apply the adjusted speed

    def crosswalk_control(self, distance):
        prev_speed = self.speed  # Store previous speed

        if distance > 50:
            self.speed = self.NORMAL_SPEED  # Maintain normal speed
        elif 50 >= distance > 30:
            self.speed = 30  # Reduce speed to anticipate stopping
        elif 30 >= distance > 10:
            self.speed = 10  # Prepare to stop if necessary
        else:
            self.speed = 0  # Stop at the crosswalk

        # Check if braking is needed
        if self.speed < prev_speed:
            LED.turn_on_gpios(17, 4)  # Brake lights ON
        else:
            LED.turn_off_gpios(17, 4)  # Brake lights OFF

        self.set_speed(self.speed)  # Apply speed adjustment




        



    

    
    

