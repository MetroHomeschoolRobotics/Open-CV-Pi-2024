
import cv2
class Util1825AprilTag:
	def draw(img, corners, imgpts):
		corner = tuple(corners[0].ravel())
		img = cv2.line(img. corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
		img = cv2.line(img. corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
		img = cv2.line(img. corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
		return img
	def distance_to_camera(knownWidth, focalLength, perWidth):
	# compute and return the distance from the maker to the camera
		return (knownWidth * focalLength) / perWidth
	