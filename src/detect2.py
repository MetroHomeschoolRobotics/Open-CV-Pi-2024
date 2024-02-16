import cv2
import apriltag
import numpy
import numpy.typing
from dataclasses import dataclass

@dataclass
class DetectedTag2:
    id: int
    corners: numpy.typing.NDArray[numpy.float64]

class TagDetector2:
    def __init__(self, aruco_dict: int):
        dict = cv2.aruco.getPredefinedDictionary(aruco_dict)
        params = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(dict, params)

    def detect(self, image) -> list[DetectedTag2]:
        corners, ids, _ = self.detector.detectMarkers(image)
        # corners, ids, _ = cv2.aruco.detectMarkers(image, self.dict, parameters=self.params)
        if len(corners) == 0:
            return []
        return [DetectedTag2(id[0], corner) for id, corner in zip(ids, corners)]
