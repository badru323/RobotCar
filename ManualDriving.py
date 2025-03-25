from picarx import Picarx
from time import sleep
import readchar
import RPi.GPIO as GPIO

# Brake light GPIO pins
GPIO17 = 17
GPIO4 = 4

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO17, GPIO.OUT)
GPIO.setup(GPIO4, GPIO.OUT)

def turn_on_brake_lights():
    GPIO.output(GPIO17, GPIO.HIGH)
    GPIO.output(GPIO4, GPIO.HIGH)
    print("[BRAKE LIGHTS] ON")

def turn_off_brake_lights():
    GPIO.output(GPIO17, GPIO.LOW)
    GPIO.output(GPIO4, GPIO.LOW)
    print("[BRAKE LIGHTS] OFF")

def get_manual(speed, angle):
    return f'''\nPress keys on keyboard to control PiCar-X!
    w: Forward
    a: Turn left
    s: Stop
    x: Backward
    d: Turn right
    i: Accelerate
    k: Decelerate
    Current speed: {speed}
    Current angle: {angle}
    ctrl+c: Press twice to exit the program
'''

def show_info(speed, angle):
    print("\033[H\033[J", end='')
    print(get_manual(speed, angle))

if __name__ == "__main__":
    try:
        speed = 80
        angle = 0
        px = Picarx()

        show_info(speed, angle)
        while True:
            key = readchar.readkey().lower()

            if key in ('wsadxik'):
                if key == 'w':
                    turn_off_brake_lights()
                    px.forward(speed)
                elif key == 's':
                    turn_on_brake_lights()
                    px.forward(0)
                elif key == 'x':
                    turn_off_brake_lights()
                    px.forward(-speed)
                elif key == 'a':
                    turn_on_brake_lights()
                    px.set_dir_servo_angle(-30)
                    sleep(0.5)
                    px.set_dir_servo_angle(0)
                    turn_off_brake_lights()
                elif key == 'd':
                    turn_on_brake_lights()
                    px.set_dir_servo_angle(30)
                    sleep(0.5)
                    px.set_dir_servo_angle(0)
                    turn_off_brake_lights()
                elif key == 'i':
                    speed += 10
                elif key == 'k':
                    speed -= 10

                show_info(speed, angle)

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        px.stop()
        GPIO.cleanup()
        print("GPIO cleaned up. Program ended.")
