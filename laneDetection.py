import cv2
import matplotlib.pyplot as plt
import numpy as np

def grey_scale(img): # 1) converts frame to grey scale
    img = np.asarray(img)
    return cv2.cvtColor(img, cv2.COLORRGB2GRAY)

#def guass_blur(img): # Applying a 5x5 Guassian kernel to remove noise/smooth image
    #bluredImg = cv2.GaussianBlur(img, (5,5), 0)
    #return bluredImg

def canny_edge_det(img): # Canny edge detection 
    edges = cv2.Canny(img, 100, 200) # low thresh = 100, high = 200
    return edges

# Now all the edges are defined
# Next is to distinguish the lane edges 

def regionOfInterest(edges): 
    h, w = edges.shape
    triMask = np.zeros((h,w))
    for i in range(h):
        for j in range(w):
            if i > (h/w)*j and i > -(h/w)*j + h:
                triMask[i,j] = 1
    regOfInt = edges*triMask # bitwise AND operation to isolate region of interest
    return regOfInt

def houghLineTransform(img):
    x, y = img.shape
    diagLine = int(np.ceil(x**2 + y**2))
    rhos = np.linspace(-diagLine, diagLine, 2*diagLine + 1)
    angles = np.deg2rad(np.arange(-90,90))
    accum = np.zeros((len(rhos), len(angles)))

    y_coors, x_coors = np.nonzero(img) # Allows us to skip the nested loop when considering the columns
    for i in range(len(x_coors)):
        x = x_coors[i]
        y = y_coors[i]
        for angles_idx in range(len(angles)):
            angle = angles[angles_idx]
            rho = x*np.cos(angle) + y*np.sin(angle)
            rho_idx = np.argmin(np.abs(rhos - rho)) # Finding the nearest integer in the rhos array
            accum[rho_idx, angles_idx] += 1 # Increment the vote value for the bin 

    return accum, rhos, angles







