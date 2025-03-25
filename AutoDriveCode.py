import asyncio
import cv2
from ultralytics import YOLO
from picarx import Picarx
from time import sleep

px = Picarx()
MODEL_TYPE = "yolov8n.pt"  # Use "yolov8n.pt" for a smaller model (YOLOv8 nano)
STOP_SIGN_LABEL = 11  # Label for stop sign, adjust according to your model
CONFIDENCE_THRESHOLD = 0.92  # Minimum confidence to consider a detection valid
SafeDistance = 30
dict = {
    "Speed": 80,
    "Angle": 0,
    "xSRC": 0,
    "ySRC": 0,
    "xDEST": 0,
    "yDEST": 0,     
    "StopL": False,
    "StopSign": False,
}


def detect_objects(image, model):
    """Perform object detection on the input image."""
    results = model(image)  # Call the model to detect objects
    return results

async def Driving():    
    if dict["StopL"] == True:
        dict["Speed"] = 0
    elif dict["StopSign"] == True:
        dict["Speed"] = 0
        sleep(.5)
        dict["StopSign"] == False
    px.forward(dict["Speed"])   

async def Steering():
    print("a")
    
async def Camera():
    model = YOLO(MODEL_TYPE)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = detect_objects(frame, model)
        for result in results:
            class_ids = result.boxes.cls
            confidences = result.boxes.conf            
            # Check each detection
            for class_id, confidence in zip(class_ids, confidences):
                if class_id == STOP_SIGN_LABEL and confidence > CONFIDENCE_THRESHOLD:
                    dict["StopSign"] = True
                
            annotated_frame = result.plot()  
            cv2.imshow("YOLOv8 Object Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    
async def Sensors():
    px_power = 10
    offset = 20
    
    while True:
        # Grayscale sensor logic for line following
        gm_val_list = px.get_grayscale_data()

        # Determine the robot's state based on sensor readings
        if gm_val_list == [0, 0, 0]:
            gm_state = 'stop'  # On the line, stop
        elif gm_val_list[1] == 1:
            gm_state = 'forward'  # Middle sensor sees the line
        elif gm_val_list[0] == 1:
            gm_state = 'right'  # Left sensor sees the line
        elif gm_val_list[2] == 1:
            gm_state = 'left'  # Right sensor sees the line

        # Move the robot based on the detected state
        if gm_state == 'stop':
            px.stop()
        elif gm_state == 'forward':
            px.set_dir_servo_angle(0)
            px.forward(px_power)
        elif gm_state == 'left':
            px.set_dir_servo_angle(offset)
            px.forward(px_power)
        elif gm_state == 'right':
            px.set_dir_servo_angle(-offset)
            px.forward(px_power)

        distance = round(px.ultrasonic.read(), 2)
        if distance <= SafeDistance:
            dict["StopL"] = True  
        else:
            dict["StopL"] = False
        
        sleep(0.1)  

async def main(): 
    # Create tasks and run them concurrently
    cameraThread =  asyncio.create_task(Camera())
    sensorThread =  asyncio.create_task(Sensors())
    # GPS Thread, if needed
    await asyncio.gather(cameraThread, sensorThread)

# Run the main coroutine
asyncio.run(main())
