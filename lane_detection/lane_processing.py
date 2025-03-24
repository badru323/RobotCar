import cv2
import numpy as np
import threading
import queue

# Thread function to process yellow lines
def process_yellow_lines(yroi, image, x_offset, y_offset, result_queue):
    yhough, yresult = avg(yroi, image.copy(), x_offset, y_offset) 
    result_queue.put(('yellow', yresult))  # Send the result to the queue

# Thread function to process white lines
def process_white_lines(wroi, image, x_offset, y_offset, result_queue):
    whough, wresult = avg(wroi, image.copy(), x_offset, y_offset)
    result_queue.put(('white', wresult))  # Send the result to the queue

def midPoints(yresult, wresult):
    midpoints = []
    if yresult:
        for line in yresult:
            yx1, yy1, yx2, yy2 = line
            if wresult:
                for wline in wresult:
                    wx1, wy1, wx2, wy2 = wline
                    midpoints.append((wx2 + yx2) / 2)  
                    print(f"Midpoint: {(wx2 + yx2) / 2}")
    else:
        if wresult:
            total = 0
            for line in wresult:
                wx1, wy1, wx2, wy2 = line
                total += wx1
            total /= len(wresult)  # average calculation
            midpoints.append(total)
            print(f"Total: {total}")
    return midpoints


def avg(edges, output_image, x_offset, y_offset):
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=75, maxLineGap=40)
    
    posSlopes, posInt = [], []
    negSlopes, negInt = [], []
    result = []
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            x1 += x_offset
            x2 += x_offset
            y1 += y_offset
            y2 += y_offset
            
            if x2 - x1 != 0:  # Avoid division by zero
                m = (y2 - y1) / (x2 - x1)  # Slope
                b = y1 - m * x1  # Intercept
                
                # Separate lines into positive and negative slopes
                if m >= 0:
                    posSlopes.append(m)
                    posInt.append(b)
                else:
                    negSlopes.append(m)
                    negInt.append(b)

    if posSlopes:
        avg_m_pos = sum(posSlopes) / len(posSlopes)
        avg_b_pos = sum(posInt) / len(posInt)
        y_start = 300
        y_end = 600
        x_start = int((y_start - avg_b_pos)/avg_m_pos)
        x_end = int((y_end - avg_b_pos)/avg_m_pos)
        cv2.line(output_image, (x_start, y_start), (x_end, y_end), (255, 0, 0), 3)  
        result.append([x_start, y_start, x_end, y_end])
    if negSlopes:
        avg_m_neg = sum(negSlopes) / len(negSlopes)
        avg_b_neg = sum(negInt) / len(negInt)
        y_start = 300
        y_end = 600
        x_start = int((y_start - avg_b_neg)/avg_m_neg)
        x_end = int((y_end - avg_b_neg)/avg_m_neg)
        result.append([x_start, y_start, x_end, y_end])
        cv2.line(output_image, (x_start, y_start), (x_end, y_end), (0, 0, 255), 3)  
    
    return output_image, result

# Image preprocessing functions
def preprocess(image):
    x1, y1 = 150, 150  
    x2, y2 = 450, 450 
    roi_image = image[y1:y2, x1:x2]
    hsv_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
    return hsv_roi, roi_image

def preyellow(hsv_roi):
    yellowLow = np.array([20, 100, 100])
    yellowHigh = np.array([30, 255, 255])
    yellowMask = cv2.inRange(hsv_roi, yellowLow, yellowHigh)
    return yellowMask

def prewhite(hsv_roi):
    whiteLow = np.array([0, 0, 200])     
    whiteHigh = np.array([180, 25, 255])
    whiteMask = cv2.inRange(hsv_roi, whiteLow, whiteHigh)
    return whiteMask

def roi(mask, roi_image):
    maskRoi = cv2.bitwise_and(roi_image, roi_image, mask=mask)
    return maskRoi

def color(roi_image):
    colourRoi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
    return colourRoi

def canny(colourRoi):
    return cv2.Canny(colourRoi, 50, 150)

# Main execution flow
def getLanes(frame):
   # frame = cv2.resize(frame, (320, 320))

    # Preprocessing
    hsv, roi_image = preprocess(frame)
    yellowMask = preyellow(hsv)
    whiteMask = prewhite(hsv)
    yellowRoi = roi(yellowMask, roi_image)
    whiteRoi = roi(whiteMask, roi_image)
    gyRoi = color(yellowRoi)
    gwRoi = color(whiteRoi)
    yroi = canny(gyRoi)
    wroi = canny(gwRoi)

    # Create a queue to collect results from threads
    result_queue = queue.Queue()

    # Create threads for yellow and white lines processing
    yellow_thread = threading.Thread(target=process_yellow_lines, args=(yroi, image, 150, 150, result_queue))
    white_thread = threading.Thread(target=process_white_lines, args=(wroi, image, 150, 150, result_queue))

    # Start the threads
    yellow_thread.start()
    white_thread.start()

    # Wait for both threads to finish
    yellow_thread.join()
    white_thread.join()

    # Collect results from the queue
    yresult = None
    wresult = None
    while not result_queue.empty():
        label, result = result_queue.get()
        if label == 'yellow':
            yresult = result
        elif label == 'white':
            wresult = result

    # Calculate midpoints
    midpoints = midPoints(yresult, wresult)
    return midpoints

    # # Display results
    # cv2.imshow("Yellow Filtered with Hough Lines (ROI)", yroi)
    # cv2.imshow("White Filtered with Hough Lines (ROI)", wroi)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()