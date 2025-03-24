import time 
from queue import Queue 
from picarx import Picarx 
import threading
import time


class PiCarStateMachine: 
    def __init__(self, px):
        self.state = "MOVING"
        self.px = px 
    
    def stop_sign(self):
        print("Stopping the car")
        self.px.forward(0) # Stop motion

    def slow_down(self):
        print("Slowing down")
        self.px.forward(30)
    
    def move_forward(self):
        print("Moving at normal speed")
        self.px.forward(50)
    

    def process_objects(self, object_queue):
    
        while True:
            if not object_queue.empty():
                detected_objects = object_queue.get() # detected objects for that frame
                event_list = set()  # Store detected event types

                for label, distance in detected_objects:
                    if label == "sign_stop" and distance < 40:
                        event_list.add("stop_sign")
                    elif label == "traffic_cone" and distance < 20:
                        event_list.add("slow_down")
                    elif label == "one_way_left" and distance < 30:
                        event_list.add("turn_left")
                    elif label == "one_way_right" and distance < 30:
                        event_list.add("turn_right")
                    elif label == "crosswalk" and distance < 40:
                        event_list.add("yield")
                    elif label == "vehicle" and distance < 50:
                        event_list.add("avoid_vehicle")
                    elif label == "duckie" and distance < 30:
                        event_list.add("avoid_duckie")

                self.handle_multiple_events(event_list)  # Process all detected events
            time.sleep(0.5)

    def handle_multiple_events(self, event_list):
        if "stop_sign" in event_list:
            self.transition("stop_sign")
            return  # Stop overrides everything else

        if "avoid_vehicle" in event_list:
            self.transition("avoid_vehicle")
            return

        if "avoid_duckie" in event_list:
            self.transition("avoid_duckie")
            return

        if "turn_left" in event_list and "turn_right" in event_list:
            print("[WARNING] Conflicting turn signs detected! Keeping straight.")
        
        elif "turn_left" in event_list:
            self.transition("turn_left")
            return
        
        elif "turn_right" in event_list:
            self.transition("turn_right")
            return

        if "yield" in event_list:
            self.transition("yield")
            return

        if "slow_down" in event_list:
            self.transition("slow_down")
            return

        # Default case: Move forward if no blocking events
        self.transition("clear")

    def transition(self, event):
        if event == "stop_sign":
            self.state = "STOPPED"
            self.stop_car()
        elif event == "avoid_vehicle":
            self.state = "AVOIDING_VEHICLE"
            self.avoid_obstacle()
        elif event == "avoid_duckie":
            self.state = "AVOIDING_DUCKIE"
            self.avoid_obstacle()
        elif event == "turn_left":
            self.state = "TURNING_LEFT"
            self.turn_left()
        elif event == "turn_right":
            self.state = "TURNING_RIGHT"
            self.turn_right()
        elif event == "yield":
            self.state = "YIELDING"
            self.yield_for_pedestrian()
        elif event == "slow_down":
            self.state = "SLOWING_DOWN"
            self.slow_down()
        elif event == "clear":
            self.state = "MOVING"
            self.move_forward()

        print(f"[STATE] New State: {self.state}")

