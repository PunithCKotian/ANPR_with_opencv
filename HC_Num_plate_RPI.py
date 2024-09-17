import cv2
import os
import pyrealsense2 as rs
import numpy as np
import socket

# Function to send coordinates and depth to Raspberry Pi
def send_coordinates_to_raspberry_pi(center_x, center_y, depth):
    # Use the Raspberry Pi's IP address
    raspberry_pi_ip = '172.20.10.2'  # Replace with the actual IP address of the Raspberry Pi
    port = 5005  # Port used by the server on Raspberry Pi

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the Raspberry Pi
        sock.connect((raspberry_pi_ip, port))
        # Create a message with the coordinates and depth
        message = f"{center_x},{center_y},{depth}"
        # Send the message
        sock.sendall(message.encode('utf-8'))

    finally:
        # Close the socket
        sock.close()

# Frame dimensions
frameWidth = 640   # Adjust based on your needs
frameHeight = 480

# Load the number plate cascade
plateCascade = cv2.CascadeClassifier(r"D:\OneDrive - Middlesex University\Middlesex University\Final dissertation\ATS_codes\Husky_lens_code\Number_plate1\ANPR_with_opencv\haarcascade_russian_plate_number.xml")  # Replace with the path to your cascade file
minArea = 500

# Create the output directory if it doesn't exist
output_dir = "./IMAGES"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# RealSense pipeline and configuration
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, frameWidth, frameHeight, rs.format.bgr8, 30)  # Color stream
config.enable_stream(rs.stream.depth, frameWidth, frameHeight, rs.format.z16, 30)   # Depth stream

# Start the RealSense pipeline
pipeline.start(config)

# Align depth to color stream
align_to = rs.stream.color
align = rs.align(align_to)

count = 0

try:
    while True:
        # Wait for frames from the RealSense camera
        frames = pipeline.wait_for_frames()

        # Align the depth frame to the color frame
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            continue

        # Convert RealSense frame to NumPy array for OpenCV
        img = np.asanyarray(color_frame.get_data())

        # Convert the image to grayscale for number plate detection
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect number plates
        numberPlates = plateCascade.detectMultiScale(imgGray, 1.1, 4)

        for (x, y, w, h) in numberPlates:
            area = w * h
            if area > minArea:
                # Print the coordinates of the detected number plate
                print(f"Detected object at: X={x}, Y={y}, Width={w}, Height={h}")

                # Draw rectangle around the detected plate
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

                # Get the center of the detected number plate
                center_x = x + w // 2
                center_y = y + h // 2

                # Get the distance at the center of the detected number plate
                distance = depth_frame.get_distance(center_x, center_y)
                print(f"Distance to object: {distance:.2f} meters")

                # Send the coordinates and depth to the Raspberry Pi
                send_coordinates_to_raspberry_pi(center_x, center_y, distance)

                # Display the detected number plate ROI
                imgRoi = img[y:y+h, x:x+w]
                cv2.imshow("Number Plate", imgRoi)

        # Show the result
        cv2.imshow("Result", img)

        # Save the detected plate image if 's' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('s'):
            cv2.imwrite(f"{output_dir}/{str(count)}.jpg", imgRoi)
            cv2.rectangle(img, (0, 200), (640, 300), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, "Scan Saved", (15, 265), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 2)
            cv2.imshow("Result", img)
            cv2.waitKey(500)
            count += 1

        # Exit the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Stop the RealSense pipeline and close windows
    pipeline.stop()
    cv2.destroyAllWindows()
