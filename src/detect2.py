import cv2
import apriltag
import numpy
import numpy.typing
import config
from dataclasses import dataclass

@dataclass
class DetectedTag:
    id: int
    corners: numpy.typing.NDArray[numpy.float64]

class TagDetector:
    def __init__(self):
        #params = apriltag.DetectorOptions(config.TagTrackerConfig.tag_family)
        self.detector = apriltag.Detector()

    def detect(self, image) -> list[DetectedTag]:
        detector = apriltag.Detector()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(gray)
        # corners, ids, _ = cv2.aruco.detectMarkers(image, self.dict, parameters=self.params)
        if len(tags) == 0:
            return []
            
        return [DetectedTag(tag.tag_id, tag.corners) for tag in tags]
