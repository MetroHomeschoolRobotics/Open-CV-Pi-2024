# This is inteneded to be ran through SSH and operates on its own
import cv2
import numpy as np
from picamera2 import Picamera2
import warnings
import os
import datetime

from typing import List

CALIBRATION_FILENAME = "calibration.json"

if __name__ == "__main__":
    all_corners: List[np.ndarray] = []
    all_ids: List[np.ndarray] = []
    imsize = None

    # Create detecor and representation of ChArUco board
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
    aruco_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

    square_size_m = 0.0206375
    charuco_board = cv2.aruco.CharucoBoard((12,9), square_size_m, square_size_m * 7/9, aruco_dict) # Different from 6328
    charuco_detector = cv2.aruco.CharucoDetector(charuco_board, cv2.aruco.CharucoParameters(), aruco_params)

    # Create webcam
    picam2 = Picamera2()
    dispW=640
    dispH=400
    picam2.preview_configuration.main.size = (dispW,dispH)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.controls.FrameRate=120
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()

    frame_count = 0
    while True:
        frame= picam2.capture_array()

        frame_count += 1
        if (frame_count % 10 != 1):
            continue

        # Convert to grayscale
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if imsize is None:
            imsize = (image.shape[0], image.shape[1])

        # Detect tags
        corners, ids, rejected = detector.detectMarkers(image)

        if len(corners) > 0:
            cv2.aruco.drawDetectedMarkers(image, corners)

            # Find ChArUco
            ret, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, image, charuco_board)

            if ret > 20:

                cv2.aruco.drawDetectedCornersCharuco(image, charuco_corners, charuco_ids)

                # Save the corners
                all_corners.append(charuco_corners)
                all_ids.append(charuco_ids)
                print("Saved frame for calibration")

        # cv2.aruco.drawDetectedCornersCharuco(image, corners)
        small = cv2.resize(image, (0, 0), fx = 0.25, fy = 0.25)
        cv2.imshow("Image", small)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Calibration may take some time, be patient")

    # Check if nothing even got seen
    if len(all_corners) == 0:
        print("No calibration images found")
        quit()
    
    # Delete the previous calibration
    if os.path.exists(CALIBRATION_FILENAME):
        os.remove(CALIBRATION_FILENAME)

    ret, camera_matrix, distortion_coefficients, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(
        charucoCorners=all_corners, charucoIds=all_ids, board=charuco_board, imageSize=imsize, cameraMatrix=None, distCoeffs=None
    )

    if ret:
        storage = cv2.FileStorage(CALIBRATION_FILENAME, cv2.FILE_STORAGE_WRITE)
        storage.write("calibration_date", str(datetime.datetime.now()))
        storage.write("camera_resolution", imsize)
        storage.write("camera_matrix", camera_matrix)
        storage.write("distortion_coefficients", distortion_coefficients)
        storage.release()
        print("Finished calibration")
    else:
        print("Something went wrong when calculating the calibration")
    
    cv2.destroyAllWindows()
    picam2.stop()

        
else:
    warnings.warn("This file should be ran through the command prompt, not as a package")
