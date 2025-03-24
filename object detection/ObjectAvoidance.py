import multiprocessing
import time
from picarx import Picarx

POWER = 50
SafeDistance = 40   # > 40 safe
DangerDistance = 20 # > 20 && < 40 turn around, < 20 backward

def object_avoidance():
    """Object avoidance process using PiCar's ultrasonic sensor."""
    px = Picarx()  # Initialize PiCar-X in this process

    try:
        while True:
            distance = round(px.ultrasonic.read(), 2)
            print("Distance:", distance)

            if distance >= SafeDistance:
                px.set_dir_servo_angle(0)
                px.forward(POWER)
            elif distance >= DangerDistance:
                px.set_dir_servo_angle(30)
                px.forward(POWER)
                time.sleep(0.1)
            else:
                px.set_dir_servo_angle(-30)
                px.backward(POWER)
                time.sleep(0.5)

    finally:
        px.forward(0)  # Stop car when process exits

def start_ultrasonic_object_avoidance():
    obj_avoidance_process = multiprocessing.Process(target=object_avoidance)
    obj_avoidance_process.start()
    return obj_avoidance_process # activates in main node


