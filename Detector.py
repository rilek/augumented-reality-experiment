import cv2
import numpy as np


class Detector(object):
    def __init__(self, machine):
        self.__machine = machine
        # Reference image
        ref_img = cv2.imread(machine["ref"])
        self.__ref_image = ref_img
        
        # Prepare descriptor
        self.__descriptor = cv2.ORB_create(1000)
        
        # Compute keypoints and descriptors for reference image
        self.__kp, self.__desc = self.detectAndCompute(self.__ref_image)

        # Just in case if poor 
        if self.__desc is None or self.__kp is None:
            raise ValueError("Reference image has no descriptors or keypoints")

        # Prepare matcher
        self.__index_params = dict(algorithm = 6,           # FLANN_INDEX_LSH
                                   table_number = 12,        # 12
                                   key_size = 20,           # 20
                                   multi_probe_level = 1)   # 2
        self.__search_params = dict(checks=300)
        self.__matcher = cv2.FlannBasedMatcher(self.__index_params, self.__search_params)

    def detect(self, frame):        
        # Compute keypoints and  for frame
        kp, desc = self.detectAndCompute(frame)
        
        # If none descriptors are found
        if desc is None or kp is None:
            return Detector.false_detection()

        # Match frame descriptors with those from reference image
        matches = self.__matcher.knnMatch(self.__desc, desc, k=2)

        # Filter out some bad matches for better confidence
        good_points = Detector.calc_good_points(matches)

        # If lack of good matches
        if len(good_points) < 50:
            return Detector.false_detection()

        # Find homography
        qpts = np.float32([self.__kp[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2)
        tpts = np.float32([kp[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2)
        matrix, mask = cv2.findHomography(qpts, tpts, cv2.RANSAC, 5.0)

        return True, matrix, mask

    def get_pts(self):
        h, w, _ = self.__ref_image.shape
        return np.float32([[[0, 0]], [[0, h]], [[w, h]], [[w, 0]]])

    def detectAndCompute(self, frame):
        gframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.__descriptor.detectAndCompute(gframe, None)

    @staticmethod
    def calc_good_points(matches):
        res = []
        for mn in matches:
            if len(mn) != 2: continue

            m, n = mn
            if m.distance < 0.7 * n.distance:
                res.append(m)
        return res
        
    @staticmethod
    def false_detection():
        return False, None, None