import cvlane as laneDet
import cv2
import matplotlib.pyplot as plt
import time
from queue import Queue

def lane_detecion(image_queue, lane_queue):
    while True:
        if not image_queue.empty():
            frame = image_queue.get()
            blur = laneDet.grey_scale(frame)
            grey = laneDet.grey_scale(blur)
            edges = laneDet.canny_edge_det(grey, 50, 150)
            masked = laneDet.regionOfInterest(edges)
            lanes = laneDet.houghLineTransform(masked, 50)
            lane_queue.put(lanes) # send lanes to motion control
        time.sleep(0.1)


