import cv2
import os
import pyrealsense2 as rs
import numpy as np

# Frame dimensions
frameWidth = 1000   # Frame Width
frameHeight = 480   # Frame Height

# Load the plate cascade
plateCascade = cv2.CascadeClassifier("D:/OneDrive - Middlesex University/Middlesex University/Final dissertation/ATS_codes/Husky_lens_code/Number_plate1/ANPR_with_opencv/haarcascade_russian_plate_number.xml")
minArea = 500

# Create the output directory if it doesn't exist
output_dir = ".\\IMAGES"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# RealSense pipeline and configuration
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, frameWidth, frameHeight, rs.format.bgr8, 30)

# Start the RealSense pipeline
pipeline.start(config)

count = 0

try:
    while True:
        # Get frames from the RealSense camera
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            continue

        # Convert RealSense frame to NumPy array
        img = np.asanyarray(color_frame.get_data())

        # Convert the image to grayscale
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect number plates
        numberPlates = plateCascade.detectMultiScale(imgGray, 1.1, 4)

        for (x, y, w, h) in numberPlates:
            area = w * h
            if area > minArea:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(img, "NumberPlate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                imgRoi = img[y:y+h, x:x+w]
                cv2.imshow("Number Plate", imgRoi)

        cv2.imshow("Result", img)

        # Save image if 's' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite(f"{output_dir}\\{str(count)}.jpg", imgRoi)
            cv2.rectangle(img, (0, 200), (640, 300), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, "Scan Saved", (15, 265), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 2)
            cv2.imshow("Result", img)
            cv2.waitKey(500)
            count += 1

        # Exit loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Stop the RealSense pipeline
    pipeline.stop()
    cv2.destroyAllWindows()
