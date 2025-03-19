import cv2
import matplotlib.pyplot as plt
import numpy as np

def grey_scale(img): # 1) converts frame to grey scale
    img = np.asarray(img)
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def guass_blur(img): # Applying a 5x5 Guassian kernel to remove noise/smooth image
    bluredImg = cv2.GaussianBlur(img, (5,5), 0)
    return bluredImg

def canny_edge_det(img, low, high): # Canny edge detection 
    edges = cv2.Canny(img, low, high) # low thresh = 100, high = 200
    # cv2.imshow("Edges", edges)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return edges

# Now all the edges are defined
# Next is to distinguish the lane edges 

# def regionOfInterest(edges): 
#     h, w = edges.shape
#     triMask = np.zeros((h,w))
#     for i in range(h):
#         for j in range(w):
#             if i > (h/w)*j and i > -(h/w)*j + h:
#                 triMask[i,j] = 1
#     regOfInt = edges*triMask # bitwise AND operation to isolate region of interest
#     return regOfInt

def regionOfInterest(edges_):
    h, w = edges_.shape
    triMask = np.zeros_like(edges_)
    reg_of_int = np.array([[
        (0,h), 
        (w*0.45, h*0.5), 
        (w*0.55, h*0.5),
        (w, 0.7*h ),
        (w, h)]], dtype=np.int32)
    cv2.fillPoly(triMask, reg_of_int, 255)
    # cv2.imshow("Mask", triMask)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    masked = cv2.bitwise_and(edges_, triMask)
    cv2.imshow("Masked edges", masked)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return masked
    


def houghLineTransform(img, threshold):
    y, x = img.shape
    diagLine = int(np.ceil(x**2 + y**2))
    rhos = np.linspace(-diagLine, diagLine, 2*diagLine + 1)
    angles = np.deg2rad(np.arange(-90,90))
    accum = np.zeros((len(rhos), len(angles)))

    y_coors, x_coors = np.nonzero(img) # Allows us to skip the nested loop when considering the columns
    print("Number of edge pixels:", len(x_coors))

    cos_a = np.cos(angles)
    sin_a = np.sin(angles)

# #     # Computes x*cos(angle) for all x coordinates and all angles all at once and stores the result in a 2D matrix
# #     # where  each row is an edge (x-coord) pixel and each columns corresponds to an angle
# #     # Does the above for y*sin(angle) as well 
# #     # rhos_matrix returns a matrix where each row corresponds to an (x,y) edge pixel and each column corresponds to an angle 
    rhos_matrix = np.outer(x_coors, cos_a) + np.outer(y_coors, sin_a)  # Vecotorization to avoid nested operations - where each (x,y) there would be a nested loop for each rho calculation
# #     # print(f"rhos min: {rhos.min()}, rhos max: {rhos.max()}")
# #     # print(f"rhos_matrix min: {rhos_matrix.min()}, rhos_matrix max: {rhos_matrix.max()}")

# #     # **Efficient rho binning using np.digitize()**
    rho_indexes = np.digitize(rhos_matrix.ravel(), rhos) - 1  # Get closest bin index
# #     # print(f"rho_indexes min: {rho_indexes.min()}, rho_indexes max: {rho_indexes.max()}")
    rho_indexes = rho_indexes.reshape(rhos_matrix.shape)  # Reshape to match (num_edges, num_thetas)

# #     # accumulate votes
    
    for i in range(len(angles)):
        np.add.at(accum[:,i], rho_indexes[:,i], 1) # increment index for each ith angle column correspinding to the rho indexes at the ith angle
    
# #
    rho_angles_peaks = np.argwhere(accum > threshold) # returns indexes (row, col) of peak votes
# #     print(rho_angles_peaks)
# #     # given the parameters of the most defined lines, we now transform from polor coordinates to cartesian coordinates
    for rho_idx, angles_idx in rho_angles_peaks:
        rho_val = rhos[rho_idx]
        angle_val = angles[angles_idx]

# #         # each line needs 2 points for the np.Lines function to create a line
        x0 = rho_val*np.cos(angle_val) # Vector (x0, y0) is the shortest line from origin to point (x0, y0) on line
        y0 = rho_val*np.sin(angle_val) # However, it wouldn;t be enough to use this as one of the points as we need 2 points that are far way to span the whole line

#             # The vector that is normal to (x0, y0) is the line of the edge which (x0, y0) lies. 
#             # To find this we take the inner product to be 0, givng L = (-sin(t),cos(t))
        l_x = -np.sin(angle_val)
        l_y = np.cos(angle_val)
        k = 1000 # Scalar to span the whole line

#             # Point 1
        x1 = int(x0 + k*l_x)
        y1 = int(y0 + k*l_y)

#             # Point 2
        x2 = int(x0 - k*l_x)
        y2 = int(y0 - k*l_y)

        img = cv2.line(img, (x1,y1), (x2,y2), (255,255,255), 2)

        y_new, x_new = np.nonzero(img)

#         # for y_p in y_new:
#         #     if y_p <= y*0.5:
#         #         img[y_p, :] = (0, 0 , 0)

    tempMask = np.zeros_like(img)

    reg_of_int = np.array([[
            (0,y*0.3), 
            (x, y*0.3), 
            (x, y),
            (0, y)]], dtype=np.int32)
    
    cv2.fillPoly(tempMask, reg_of_int, 255)
    
    img = cv2.bitwise_and(img, tempMask)

#     img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

# def houghLineTransform(img):
#     lines = cv2.HoughLinesP(img, 1, np.pi/180, 50, None, 50, 10)
#     if lines is not None: 
#         for i in range(0, len(lines)):
#             l = lines[i][0]
#             cv2.line(img, (l[0], l[1]), (l[2], l[3]), (255,,255), 3, cv2.LINE_AA)
    cv2.imshow("lanes", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    








