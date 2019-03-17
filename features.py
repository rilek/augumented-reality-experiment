#!/usr/bin/env python3

import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

def draw_polylines(frame, dst_arr, color=(0, 0, 255), thickness=3):
    return cv2.polylines(frame, dst_arr, True, color, thickness)

def process_img(cap):
    base = cv2.imread("/home/rafcio/Mgr/img/base.jpg")

    if not cap:
        cap = cv2.VideoCapture(0)

    fps = int(1000/24)
    
    ## Features
    sift = cv2.xfeatures2d.SIFT_create()
    kp1, desc1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    base = cv2.drawKeypoints(base, kp1, base)

    ## Feature matching
    index_params = dict(algorithm=0, trees=3)
    search_params = dict()
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    i = 0

    h,w, _ = base.shape
    dst_arr = None
    good_points = []
    homography = None


    while True:
        _, frame = cap.read()
        # if i == 0:
        gframe = frame #cv2.resize(frame, (320, 240))
        gframe = cv2.cvtColor(gframe, cv2.COLOR_BGR2GRAY)
        kp2, desc2 = sift.detectAndCompute(gframe, None)
        # gframe = cv2.drawKeypoints(gframe, kp2, gframe)

        matches = flann.knnMatch(desc1, desc2, k=2)
        good_points = []
        for m, n in matches:
            if m.distance < 0.5 * n.distance:
                good_points.append(m)

        if len(good_points) > 7:
            qpts = np.float32([kp1[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2)
            tpts = np.float32([kp2[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2)

            matrix, mask = cv2.findHomography(qpts, tpts, cv2.RANSAC, 5.0)
            matches_mask = mask.ravel().tolist()

            # Perspective transform
            pts = np.float32([[0, 0], [0, h], [w, h], [w,0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, matrix)

            # print(dst)

            dst_arr = [np.int32(dst)]

            homography = frame #draw_polylines(frame, dst_arr)


            img = np.zeros([h,w,3], dtype=np.uint8)

            img[70:h//2+10,:,0] = 255
            img[70:h//2+10,:,1] = 255
            img[70:h//2+10,:,2] = 255
            cv2.putText(img,'TEST', (125, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(img,'wypisywania', (60, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            # cv2.imshow("Img", img)

            img = cv2.warpPerspective(img, matrix, (320, 240))
            img = cv2.resize(img, (320, 240))
            
            r, c, ch = img.shape
            roi = homography[0:r, 0:c]

            gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(gimg, 10, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)

            homography_bg = cv2.bitwise_and(roi, roi, mask = mask_inv)
            img_fg = cv2.bitwise_and(img, img, mask=mask)

            # img = np.expand_dims(np.asarray(img), axis=2)
            # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # pts = np.float32([[0, 0], [0, h//2], [w, h//2], [w,0]]).reshape(-1, 1, 2)
            # dst = cv2.perspectiveTransform(pts, matrix)
            # img = draw_polylines(frame, [np.int32(dst)], (255, 255, 255), cv2.FILLED)
            # homography = cv2.rectangle(homography, tuple(dst[0][0]), tuple(dst[2][0]), (255,255,255), cv2.FILLED)


            homography = cv2.addWeighted(homography_bg, 1,  img_fg, 1, gamma=0)
            # homography = cv2.resize(homography, (640, 480))

            cv2.imshow("Homography", homography)


            # cv2.imshow("Homography", homography)
        else:
            # frame = cv2.resize(frame, (640, 480))
            cv2.imshow("Homography", frame)
        
        # else:
        #     if len(good_points) > 10:
        #         homography = draw_polylines(frame, dst_arr)

        #         cv2.imshow("Homography", homography)
        #     else:
        #         cv2.imshow("Homography", frame)

        # i = (i + 1) % 2



        # res = cv2.drawMatches(base, kp1, gframe, kp2, good_points, None, flags=2)

        # cv2.imshow("Base", base)
        # cv2.imshow("Frame", gframe)
        # cv2.imshow("Result", res)

        key = cv2.waitKey(fps)
        if key==27:
            break


################
## Brute force detection
################

# ## ORB DETECTOR
# orb = cv2.ORB_create()
# kp1, desc1 = orb.detectAndCompute(org, None)
# kp2, desc2 = orb.detectAndCompute(i1, None)

# ## Brute Force matching
# bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
# matches = bf.match(desc1, desc2)
# matches = sorted(matches, key=lambda x:x.distance)

# res = cv2.drawMatches(org, kp1, i1, kp2, matches[:50], None, flags=2)

# cv2.imshow("Match", res)

################


################
## DETECTIONS ONLY
################

# sift = cv2.xfeatures2d.SURF_create()
# orb = cv2.ORB_create()

# kp, _ = orb.detectAndCompute(org, None)

# org = cv2.drawKeypoints(org, kp, None)

# cv2.imshow("Original", org)

################

if __name__ == "__main__":

    # cap = cv2.VideoCapture(0)

    # processStream(cap)



    base = cv2.imread("/home/rafcio/Mgr/img/014.png")
    # base = cv2.resize(base, (240, 320))

    ## Features
    sift = cv2.xfeatures2d.SIFT_create()
    kp1, desc1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    base = cv2.drawKeypoints(base, kp1, base)

    cv2.imshow("IMG", base)

    cv2.waitKey(0)
    cv2.destroyAllWindows()