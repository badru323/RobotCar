import cv2
import os
from datetime import datetime

# Create a directory to store images
SAVE_DIR = "captured_images"
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize the Pi Camera
cap = cv2.VideoCapture(0)  # 0 is usually the Pi Camera

if not cap.isOpened():
    print("Error: Could not access the camera.")
    exit()

print("Press 's' to take a picture or 'q' to quit.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Display the frame
        cv2.imshow("Camera", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s'):
            # Generate a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(SAVE_DIR, f"image_{timestamp}.jpg")
            
            # Save the captured frame
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
        
        elif key == ord('q'):
            print("Exiting...")
            break

except KeyboardInterrupt:
    print("Capture stopped by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
