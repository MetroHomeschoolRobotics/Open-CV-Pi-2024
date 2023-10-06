import numpy
import numpy.typing
import cv2
import detect
import math
import environment
from wpimath.geometry import *
from dataclasses import dataclass

@dataclass
class PoseEstimation:
    ids: list[int]
    # Tuple of (pose, error)
    estimate_a: tuple[Pose3d, float]
    estimate_b: tuple[Pose3d, float]

@dataclass
class CalibrationInfo:
    matrix: numpy.typing.NDArray[numpy.float64]
    distortion_coeffs: numpy.typing.NDArray[numpy.float64]

def cvToWpi(tvec: numpy.typing.NDArray[numpy.float64], rvec: numpy.typing.NDArray[numpy.float64]) -> Pose3d:
    # Different from 6328 (they swapped and inverted the vector components)
    return Pose3d(
        Translation3d(tvec[0][0], tvec[1][0], tvec[2][0]),
        Rotation3d(
            numpy.array([rvec[0][0], rvec[1][0], rvec[2][0]]),
            math.sqrt(math.pow(rvec[0][0], 2) + math.pow(rvec[1][0], 2) + math.pow(rvec[2][0], 2))
        ))

def wpiToCv(tx: Translation3d) -> list[float]:
    return [tx.X(), tx.Y(), tx.Z()]

class PoseEstimator:
    def __init__(self, tag_size, calibration: CalibrationInfo, env: environment.TagEnvironment):
        self.tag_size = tag_size
        self.calibration = calibration
        self.env = env

    def estimate_pose(self, tag_infos: list[detect.DetectedTag]) -> PoseEstimation:    
        # Collect the corner positions of all the detected tags in field space
        half_sz = self.tag_size / 2.0
        object_points = []
        image_points = []
        tag_ids = []
        tag_poses = []
        for tag_info in tag_infos:
            tag_pose = self.env.get_tag_pose(tag_info.id)
            if tag_pose:
                # Get corner positions in field space
                corner_0 = tag_pose + Transform3d(Translation3d(0, half_sz, -half_sz), Rotation3d())
                corner_1 = tag_pose + Transform3d(Translation3d(0, -half_sz, -half_sz), Rotation3d())
                corner_2 = tag_pose + Transform3d(Translation3d(0, -half_sz, half_sz), Rotation3d())
                corner_3 = tag_pose + Transform3d(Translation3d(0, half_sz, half_sz), Rotation3d())
                
                # Put all the things in the lists
                # Important: the indices all align in the lists
                object_points += [
                    wpiToCv(corner_0.translation()),
                    wpiToCv(corner_1.translation()),
                    wpiToCv(corner_2.translation()),
                    wpiToCv(corner_3.translation())
                ]
                image_points += [
                    [tag_info.corners[0][0][0], tag_info.corners[0][0][1]],
                    [tag_info.corners[0][1][0], tag_info.corners[0][1][1]],
                    [tag_info.corners[0][2][0], tag_info.corners[0][2][1]],
                    [tag_info.corners[0][3][0], tag_info.corners[0][3][1]]
                ]
                tag_ids.append(tag_info.id)
                tag_poses.append(tag_pose)
        
        if len(tag_ids) == 1:
            object_points = numpy.array([[-half_sz, half_sz, 0.0],
                                         [half_sz, half_sz, 0.0],
                                         [half_sz, -half_sz, 0.0],
                                         [-half_sz, -half_sz, 0.0]])
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                    object_points, numpy.array(image_points),
                    self.calibration.matrix, self.calibration.distortion_coeffs, flags=cv2.SOLVEPNP_IPPE_SQUARE)
            except Exception as e:
                print(e)
                return None

            # Calculate WPILib camera poses
            field_to_tag_pose = tag_poses[0]
            camera_to_tag_pose_0 = cvToWpi(tvecs[0], rvecs[0])
            camera_to_tag_pose_1 = cvToWpi(tvecs[1], rvecs[1])
            camera_to_tag_0 = Transform3d(camera_to_tag_pose_0.translation(), camera_to_tag_pose_0.rotation())
            camera_to_tag_1 = Transform3d(camera_to_tag_pose_1.translation(), camera_to_tag_pose_1.rotation())
            field_to_camera_0 = field_to_tag_pose.transformBy(camera_to_tag_0.inverse())
            field_to_camera_1 = field_to_tag_pose.transformBy(camera_to_tag_1.inverse())
            field_to_camera_pose_0 = Pose3d(field_to_camera_0.translation(), field_to_camera_0.rotation())
            field_to_camera_pose_1 = Pose3d(field_to_camera_1.translation(), field_to_camera_1.rotation())

            return PoseEstimation(
                ids=tag_ids,
                estimate_a=(field_to_camera_pose_0, errors[0][0]),
                estimate_b=(field_to_camera_pose_1, errors[1][0])
            )
        elif len(tag_ids) > 1:
            # Multiple tags were found, solve with all of them
            try:
                _, rvecs, tvecs, errors = cv2.solvePnPGeneric(
                    numpy.array(object_points), numpy.array(image_points),
                    self.calibration.matrix, self.calibration.distortion_coeffs, flags=cv2.SOLVEPNP_SQPNP)
            except Exception as e:
                print(e)
                return None
            
            camera_to_field_pose = cvToWpi(tvecs[0], rvecs[0])
            camera_to_field = Transform3d(camera_to_field_pose.translation(), camera_to_field_pose.rotation())
            field_to_camera = camera_to_field.inverse()
            field_to_camera_pose = Pose3d(field_to_camera.translation(), field_to_camera.rotation())

            return PoseEstimation(
                ids=tag_ids,
                estimate_a=(field_to_camera_pose, errors[0][0]),
                estimate_b=None
            )
        else:
            return None
