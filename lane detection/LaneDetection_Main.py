import cvlane as laneDet
import cv2
import matplotlib.pyplot as plt

img = cv2.imread("lane_det_test_01.jpg")

blurred_img = laneDet.guass_blur(img)

grey_img = laneDet.grey_scale(blurred_img)

edges = laneDet.canny_edge_det(grey_img, 50, 150)

roi = laneDet.regionOfInterest(edges)

lines = laneDet.houghLineTransform(roi, 50)

if __name__ == '__main__':
    
# Display 
# plt.figure(figsize=(10, 5))
# plt.subplot(141)
# plt.imshow(lines)
# plt.title("Lane Detection Output")
# plt.axis("off")
# plt.subplot(142)
# plt.imshow(grey_img)
# plt.subplot(143)
# plt.imshow(edges)
# plt.subplot(144)
# plt.imshow(roi)
# plt.title("region of interest")
# plt.show()

# cv2.imshow(lines)
# cv2.waitKey(0)
# cv2.destroyAllWindows()



# laneDetection.canny_edge_det(grey_img, 50, 150)
# laneDetection.regionOfInterest(edges)



