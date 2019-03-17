import cv2
import numpy as np


# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Load camera matrix and distortions matrix
mtx = np.loadtxt('mtx.txt')
dist = np.loadtxt('dist.txt')

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(8,6,0)
objp = np.zeros((7*9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:7].T.reshape(-1, 2)

# prepare axis
axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]]).reshape(-1, 3)

FPS = int(1000/60)



### Functions

def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255, 0, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0, 255, 0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0, 0, 255), 5)
    return img

def process_img(cap):
    while(True):
        # Capture frame-by-frame
        ret, img = cap.read()
        if img is not None:
            # Display the resulting frame
            # cv2.imshow('img', img)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # cv2.imshow('img', gray)
            ret, corners = cv2.findChessboardCorners(gray, (9, 7), flags=cv2.CALIB_CB_FAST_CHECK)

            if ret is True:
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

                # Find the rotation and translation vectors.
                ret, rvecs, tvecs, _ = cv2.solvePnPRansac(objp, corners2, mtx, dist)

                # project 3D points to image plane
                imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)
                img = draw(img, corners2, imgpts)
                cv2.imshow('img', img)
            else:
                cv2.imshow("img", img)

            # Press q to close the video windows before it ends if you want
            cv2.waitKey(FPS)
        else:
            print("Frame is None")
            break
