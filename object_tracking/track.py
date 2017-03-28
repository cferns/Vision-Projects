# USAGE
# python track.py --video video/iphonecase.mov

# import the necessary packages
import numpy as np
import argparse
import time
import cv2
from collections import deque

# construct the argument parse and parse the arguments

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help = "path to the (optional) video file")
args = vars(ap.parse_args())

# define the upper and lower boundaries for a color
# to be considered "blue"
lowerColorLimit = np.array([70, 70, 205], dtype = "uint8")
upperColorLimit = np.array([160, 150, 255], dtype = "uint8")

# load the video
camera = cv2.VideoCapture(args["video"])

center = None
pts = []

# keep looping
while True:
	# grab the current frame
	(grabbed, frame) = camera.read()

	# check to see if we have reached the end of the
	# video
	if not grabbed:
		break

	# determine which pixels fall within the blue boundaries
	# and then blur the binary image
	blue = cv2.inRange(frame, lowerColorLimit, upperColorLimit)
	blue = cv2.GaussianBlur(blue, (3, 3), 0)

	# find contours in the image
	(_, cnts, _) = cv2.findContours(blue.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

	# check to see if any contours were found
	if len(cnts) > 0:
		# sort the contours and find the largest one -- we
		# will assume this contour correspondes to the area
		# of my phone
		cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]

		M = cv2.moments(cnt)
		cx = int(M['m10'] / M['m00'])
		cy = int(M['m01'] / M['m00'])
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		pts.append(center)

		# compute the (rotated) bounding box around then
		# contour and then draw it		
		rect = np.int32(cv2.boxPoints(cv2.minAreaRect(cnt)))
		cv2.drawContours(frame, [rect], -1, (0, 255, 0), 2)
		cv2.circle(frame, center, 5, (0, 0, 255), -1)
		cv2.circle(frame, pts[0], 5, (0, 0, 0), -1)

		for i in range(1, len(pts)):
			# if either of the tracked points are None, ignore
			# them
			if pts[i - 1] is None or pts[i] is None:
				continue

			# otherwise, compute the thickness of the line and
			# draw the connecting lines
			#thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
			cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), 2)

	cv2.circle(frame, pts[-1], 5, (0, 0, 0), -1)
	# show the frame and the binary image
	cv2.imshow("Tracking", frame)
	cv2.imshow("Binary", blue)

	# if your machine is fast, it may display the frames in
	# what appears to be 'fast forward' since more than 32
	# frames per second are being displayed -- a simple hack
	# is just to sleep for a tiny bit in between frames;
	# however, if your computer is slow, you probably want to
	# comment out this line
	time.sleep(0.025)

	# if the 'q' key is pressed, stop the loop
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break


# cleanup the camera and close any open windows
cv2.waitKey(5000)
camera.release()
cv2.destroyAllWindows()