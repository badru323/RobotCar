from picarx import Picarx 
import time 

    
def test():
    try:
        px = Picarx()
        start_time = time.time()
        px.set_servo_angle(30)
        px.forward(50)

        time.sleep(5)

        px.set_servo_angle(0)

        prev_time = start_time

        diff_time = start_time - prev_time
        print("The time it took is: ", diff_time)
    finally:
        px.forward(0)
if __name__ == '__main__':
    test()


