import laneDetection
import cv2
import matplotlib.pyplot as plt

img = cv2.imread("lane_det_test_01.jpg")

blurred_img = laneDetection.guass_blur(img)

grey_img = laneDetection.grey_scale(blurred_img)

edges = laneDetection.canny_edge_det(grey_img, 50, 150)

roi = laneDetection.regionOfInterest(edges)

#lines = laneDetection.houghLineTransform(roi, 50)

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

laneDetection.houghLineTransform(roi, 50)

# laneDetection.canny_edge_det(grey_img, 50, 150)
# laneDetection.regionOfInterest(edges)



