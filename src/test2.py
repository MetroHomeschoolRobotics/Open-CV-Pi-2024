import cv2
from picamera2 import Picamera2
import libcamera
import time
import numpy as np
import apriltag
import pickle
from scipy.spatial.transform import Rotation  

picam2 = Picamera2()
dispW=640
dispH=480
picam2.preview_configuration.main.size = (dispW,dispH)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.controls.FrameRate=120
picam2.preview_configuration.transform = libcamera.Transform(hflip=1, vflip=1) ## Line to flip camera preview rotation -George Horsey 
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()
fps=0
pos=(30,60)
font=cv2.FONT_HERSHEY_SIMPLEX
height=1.5
weight=3
myColor=(0,0,255)
detector = apriltag.Detector()
#loading camera calibration-if you need to recalibrate run CalibrationTest.py
with open("calibration_result.pkl", "rb") as file:
    calibration_result=pickle.load(file)

mtx = calibration_result["mtx"]
dist = calibration_result["dist"]
rvecs = calibration_result["rvecs"]
tvecs = calibration_result["tvecs"]

critera = (cv2.TERM_CRITERIA_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)
apriltag.Detector.detect
print(mtx)
while True:
    tStart=time.time()
    frame= picam2.capture_array()
    cv2.putText(frame,str(int(fps))+' FPS',pos,font,height,myColor,weight)

    frameHSV=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    result = detector.detect(frameHSV)
    if len(result) > 0:
        # If at least one tag was detected, draw a rectangle around it and put its ID
        for tag in result:
            cv2.polylines(frame, [np.int32(tag.corners)], True, (0,255,0), 2)
            cv2.putText(frame, str(tag.tag_id), tuple(np.int32(tag.corners[0])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
            # Util1825AprilTag.Util1825AprilTag.distance_to_camera(6.5, 793.70810553, tag.itemsize)
            # #### Modify the angles
            # #print(angles)

            # #angles = dresult[6]
            # # # Print the rotation angles
            # # print(f"Detected AprilTag ID: {tag.tag_id}")
            # # print(f"Rotation angles (degrees): {angles * 180 / np.pi}")

            # # # Add the angle information to the image box
            # angle_text = f"Angle: {angles[0][0]} deg"
            # cv2.putText(frame, angle_text, tuple(np.int32(tag.corners[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

            # # # Add the tag ID to the image box
            # id_text = f"ID: {tag.tag_id}"
            # cv2.putText(frame, id_text, (int(tag.corners[0][0]), int(tag.corners[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

    cv2.imshow("Camera", frame)
    if cv2.waitKey(1)==ord('q'):
        break
    tEnd=time.time()    
    loopTime=tEnd-tStart
    fps=.9*fps + .1*(1/loopTime)
cv2.destroyAllWindows()