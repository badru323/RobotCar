import time 
from queue import Queue 
from picarx import Picarx 
import threading
import time

class PiCarStateMachine: 
    def __init__(self, px):
        self.state = "MOVING"
        self.px = px 
    
    def stop_car(self):
        print("Stopping the car")
        self.px.forward(0) # Stop motion

    def slow_down(self):
        print("Slowing down")
        self.px.forward(30)
    
    def move_forward(self):
        print("Moving at normal speed")
        self.px.forward(50)

    def transition_state(self, event):
        if event == "sign_stop":
            self.state = "STOPPED"
            self.stop_car()

        elif event == "road_traffic_cone":
            self.state = "SLOW_DOWN"
            self.slow_down()
        elif event == "avoid_vehicle":
            self.state = "OBJECT_AVOIDANCE"
            self.avoid_obstacle()
            
        elif event == "clear":
            self.state = "MOVING"
            self.move_forward()

        print(f"The new state is: {self.state}")
    
    def 