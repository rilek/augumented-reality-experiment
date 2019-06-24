import numpy as np
import cv2
from matplotlib import pyplot as plt

img = cv2.imread('AR/img/base.png')
gimg = img
# cv2.imshow("img", img)
# cv2.waitKey()
# Initiate STAR detector
orb = cv2.ORB_create(1000)

# find the keypoints with ORB
kp, desc = orb.detectAndCompute(img, None)

# draw only keypoints location,not size and orientation
img2 = cv2.drawKeypoints(gimg,kp, None,color=(0,255,0), flags=0)
# plt.imshow(img2),plt.show()
cv2.imshow("Keypoints", img2)
cv2.waitKey()