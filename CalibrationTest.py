import numpy as np
import cv2 as cv
import glob
from picamera2 import Picamera2
import libcamera
import pickle

picam2 = Picamera2()
dispW=640
dispH=480
picam2.preview_configuration.main.size = (dispW,dispH)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate=1
picam2.preview_configuration.transform = libcamera.Transform(hflip=1, vflip=1) ## Line to flip camera preview rotation -George Horsey 
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()
fps=0
pos=(30,60)
font=cv.FONT_HERSHEY_SIMPLEX
height=1.5
weight=3
myColor=(0,0,255)
cnt=0
# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((5*5,3), np.float32)
objp[:,:2] = np.mgrid[0:5,0:5].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
while True:
    images = picam2.capture_array()
    gray = cv.cvtColor(images,cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (5,5), None)
    # If found, add object points, image points (after refining them)
    if ret == True and cnt <11:
        cnt+=1
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        # Draw and display the corners
        cv.drawChessboardCorners(images, (5,5), corners2, ret)
    cv.imshow('img', images)
    if cv.waitKey(1)==ord('q'):
        break
ret, mtx, dist, rvecs, tvecs= cv.calibrateCamera(objpoints,imgpoints,gray.shape[::-1], None, None)
calibration_reslut = {"mtx": mtx, "dist": dist, "rvecs": rvecs, "tvecs": tvecs}
with open("calibration_result.pkl", "wb") as file:
    pickle.dump(calibration_reslut, file)
cv.destroyAllWindows()