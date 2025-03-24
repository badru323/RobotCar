import cv2
import numpy as np

def grey_scale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def guass_blur(img):
    return cv2.GaussianBlur(img, (5,5), 0)

def canny_edge_det(img, low=100, high=200):
    return cv2.Canny(img, low, high)

def regionOfInterest(edges_):
    h, w = edges_.shape
    triMask = np.zeros_like(edges_)
    reg_of_int = np.array([[
        (0, h),
        (w * 0.45, h * 0.5),
        (w * 0.65, h * 0.5),
        (w, h)]], dtype=np.int32)
   
    cv2.fillPoly(triMask, reg_of_int, 255)
    return cv2.bitwise_and(edges_, triMask)

def houghLineTransform(img):
    lines = cv2.HoughLinesP(img, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
   
    line_img = np.zeros_like(img)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_img, (x1, y1), (x2, y2), 255, 2)
   
    return line_img
