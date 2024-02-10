import cv2
from picamera2 import Picamera2
import libcamera
import time
import numpy as np
import apriltag
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
             # Calculate the homography matrix
            # H = tag.homography
            
            # # Compute the rotation matrix and translation vector from the homography matrix
            # K = np.array([[1000, 0, 320], [0, 1000, 240], [0, 0, 1]]) # Intrinsic parameters of the camera
            # [R, T] = cv2.decomposeHomographyMat(H, K)

            # # Extract the rotation angles from the rotation matrix
            # angles, _, _ = cv2.RQDecomp3x3(R)

            # # Print the rotation angles
            # print(f"Detected AprilTag ID: {tag.tag_id}")
            # print(f"Rotation angles (degrees): {angles * 180 / np.pi}")

            # # Add the angle information to the image box
            # angle_text = f"Angle: {angles[0][0] * 180 / np.pi:.2f} deg"
            # cv2.putText(frame, angle_text, tuple(np.int32(tag.corners[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

            # # Add the tag ID to the image box
            # id_text = f"ID: {tag.tag_id}"
            # cv2.putText(frame, id_text, (int(tag.corners[0][0]), int(tag.corners[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)


    cv2.imshow("Camera", frame)
    if cv2.waitKey(1)==ord('q'):
        break
    tEnd=time.time()
    loopTime=tEnd-tStart
    fps=.9*fps + .1*(1/loopTime)
cv2.destroyAllWindows()