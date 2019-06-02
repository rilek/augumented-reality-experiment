#!/usr/bin/env python3


import argparse
import numpy as np
import cv2


def parse_arguments():
    parser = argparse.ArgumentParser(description='Process video stream')
    parser.add_argument('-s','--source', type=str,
                        help="""Path to chessboard image.""")
    parser.add_argument('-o', "--output", type=str,
                        help="""Output directory""")
    parser.add_argument('-d', "--draw", action="store_true",
                        help="""Draw image with keypoints on chessboard""")
    args = parser.parse_args()

    if args.source is None:
        raise Exception("Source argument is mandatory!")

    return args

if __name__ == "__main__":
    args = parse_arguments()

    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((9*7,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:9].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    img = cv2.imread(args.source)
    img = cv2.resize(img, None, None, 0.25, 0.25)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,9),None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        if args.draw:
            img = cv2.drawChessboardCorners(img, (7,9), corners2,ret)
            cv2.imshow('img',img)
            cv2.waitKey(0)

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
        
        if args.output:
            path = args.output.replace("[/]$", "")
            np.savetxt(path + "/cm.txt", mtx)
            np.savetxt(path + "/dist.txt", dist)
            np.savetxt(path + "/r.txt", rvecs[0])
            np.savetxt(path + "/t.txt", tvecs[0])
            

cv2.destroyAllWindows()