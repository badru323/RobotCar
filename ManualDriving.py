from picarx import Picarx
from time import sleep
import readchar
import fullSystem  # exact filename is fullSystem.py

def get_manual(speed, angle):
    return f'''
Press keys on keyboard to control PiCar-X!
    w: Forward
    a: Turn left (blink left)
    s: Stop (brake lights on)
    x: Reverse (after full stop)
    d: Turn right (blink right)
    i: Accelerate
    k: Decelerate
    Current speed: {speed}
    Current angle: {angle}
    ctrl+c: Press twice to exit the program
'''

def show_info(speed, angle):
    print("\033[H\033[J", end='')  # Clear terminal window
    print(get_manual(speed, angle))

if __name__ == "__main__":
    try:
        speed = 80
        angle = 0
        px = Picarx()

        show_info(speed, angle)
        while True:
            key = readchar.readkey().lower()
            
            # Check for valid control keys
            if key in "wsadxik":
                if key == 'w':
                    # Clear lights and move forward
                    fullSystem.no_light()
                    px.forward(speed)
                elif key == 's':
                    # Stop the vehicle and turn on brake lights
                    px.forward(0)
                    fullSystem.brake_light()
                elif key == 'x':
                    # Reverse: first stop with brake lights, then reverse after a short delay
                    px.forward(0)
                    fullSystem.brake_light()
                    sleep(0.5)
                    px.forward(-speed)
                elif key == 'i':
                    speed = min(100, speed + 10)  # Increase speed, max 100
                elif key == 'k':
                    speed = max(0, speed - 10)    # Decrease speed, not negative
                elif key == 'd':
                    # Right turn: blink right LED briefly, then update angle
                    fullSystem.turn_on_gpio(fullSystem.GPIO4)
                    sleep(0.3)
                    fullSystem.turn_off_gpio(fullSystem.GPIO4)
                    angle = min(40, angle + 10)
                elif key == 'a':
                    # Left turn: blink left LED briefly, then update angle
                    fullSystem.turn_on_gpio(fullSystem.GPIO17)
                    sleep(0.3)
                    fullSystem.turn_off_gpio(fullSystem.GPIO17)
                    angle = max(-40, angle - 10)
                
                px.set_dir_servo_angle(angle)
                show_info(speed, angle)

    except KeyboardInterrupt:
        print("\nExiting...")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        px.stop()
        sleep(0.2)
