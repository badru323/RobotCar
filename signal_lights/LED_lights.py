import RPi.GPIO as GPIO
import time

# Define GPIO pins
GPIO17 = 17  # First LED or device
GPIO4 = 4    # Second LED or device

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO17, GPIO.OUT)
GPIO.setup(GPIO4, GPIO.OUT)


# Cycles through i) just red (GPIO 17), ii) just yellow (GPIO 4), iii) both on, iv) both off


def turn_on_gpio(pin):
    """Turns on the specified GPIO pin."""
    GPIO.output(pin, GPIO.HIGH)
    print(f"GPIO {pin} is ON")

def turn_off_gpio(pin):
    """Turns off the specified GPIO pin."""
    GPIO.output(pin, GPIO.LOW)
    print(f"GPIO {pin} is OFF")

try:
    while True:
        print("\nTurning on GPIO 17 only...")
        turn_on_gpio(GPIO17)
        turn_off_gpio(GPIO4)
        time.sleep(2)  # Wait 2 seconds

        print("\nTurning on GPIO 4 only...")
        turn_off_gpio(GPIO17)
        turn_on_gpio(GPIO4)
        time.sleep(2)  # Wait 2 seconds

        print("\nTurning on both GPIO 17 and GPIO 4...")
        turn_on_gpio(GPIO17)
        turn_on_gpio(GPIO4)
        time.sleep(2)  # Wait 2 seconds

        print("\nTurning off both GPIO 17 and GPIO 4...")
        turn_off_gpio(GPIO17)
        turn_off_gpio(GPIO4)
        time.sleep(2)  # Wait 2 seconds

except KeyboardInterrupt:
    print("\nScript interrupted. Cleaning up...")
finally:
    GPIO.cleanup()  # Reset GPIO settings before exiting
