import cv2
import apriltag
from picamera2 import Picamera2
import picamera.array
import numpy as np

# Initialize the camera
with Picamera2() as camera:
    # Set up the camera settings
    camera.resolution = (640, 480)

    # Create an in-memory stream
    with picamera.array.PiRGBArray(camera) as stream:
        # Set up the AprilTag detector
        detector = apriltag.Detector()

        while True:
            # Capture into the stream
            camera.capture_array() 'RGB888', use_video_port=True)
            
            # Convert image to grayscale
            gray = cv2.cvtColor(stream.array, cv2.COLOR_BGR2GRAY)

            # Detect the AprilTags in the image
            result = detector.detect(gray)

            if len(result) > 0:
                # If at least one tag was detected, draw a rectangle around it and put its ID
                for tag in result:
                    cv2.polylines(stream.array, [np.int32(tag.corners)], True, (0,255,0), 2)
                    cv2.putText(stream.array, str(tag.tag_id), tuple(np.int32(tag.corners[0])), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

            # Display the resulting frame
            cv2.imshow('Frame', stream.array)

            # Clear the stream ready for the next frame
            stream.truncate(0)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

cv2.destroyAllWindows()

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