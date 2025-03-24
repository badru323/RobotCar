import RPi.GPIO as GPIO
import time

# Define GPIO pins
GPIO17 = 17  # First LED or device
GPIO4 = 4    # Second LED or device

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO17, GPIO.OUT)
GPIO.setup(GPIO4, GPIO.OUT)

def turn_on_gpio(pin):
    """Turns on the specified GPIO pin."""
    GPIO.output(pin, GPIO.HIGH)
    print(f"GPIO {pin} is ON")

def turn_on_gpios(pin1, pin2):
    GPIO.output(pin1, GPIO.HIGH)
    GPIO.output(pin2, GPIO.HIGH)

def turn_off_gpio(pin):
    """Turns off the specified GPIO pin."""
    GPIO.output(pin, GPIO.LOW)
    print(f"GPIO {pin} is OFF")

def turn_off_gpios(pin1, pin2):
    GPIO.output(pin1, GPIO.LOW)
    GPIO.output(pin2, GPIO.LOW)
    reset_leds()

def reset_leds():
    GPIO.cleanup()

#
