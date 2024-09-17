#This is a working pi code, the servos move along with the detected object but with a great angular differnce
import socket
import pigpio  # Import pigpio for controlling PWM

# Initialize pigpio and define GPIO pins for pan and tilt servos
pi = pigpio.pi()

# Define the GPIO pins connected to the pan and tilt servos
PAN_PIN = 13  # Replace with your actual GPIO pin for pan servo
TILT_PIN = 12  # Replace with your actual GPIO pin for tilt servo

# Define the PWM range for the servos (typically between 500 and 2500 microseconds)
PWM_MIN = 500
PWM_MAX = 2500

# Define the corresponding angles for the servos (0ï¿½ to 180ï¿½)
ANGLE_MIN = 0
ANGLE_MAX = 180

# Frame dimensions (same as the camera frame dimensions)
frameWidth = 640
frameHeight = 480

# Function to map a value from one range to another
def map_value(value, from_min, from_max, to_min, to_max):
    return (value - from_min) * (to_max - to_min) // (from_max - from_min) + to_min

# Function to control the pan and tilt servos and print motor angles
def control_pan_tilt(center_x, center_y, depth):
    # Map the center_x and center_y coordinates to the servo PWM range
    pan_pwm = map_value(center_x, 0, frameWidth, PWM_MIN, PWM_MAX)
    tilt_pwm = map_value(center_y, 0, frameHeight, PWM_MIN, PWM_MAX)

    # Send the PWM signal to the pan and tilt servos
    pi.set_servo_pulsewidth(PAN_PIN, pan_pwm)
    pi.set_servo_pulsewidth(TILT_PIN, tilt_pwm)

    # Map the PWM values back to angles (for printing)
    pan_angle = map_value(pan_pwm, PWM_MIN, PWM_MAX, ANGLE_MIN, ANGLE_MAX)
    tilt_angle = map_value(tilt_pwm, PWM_MIN, PWM_MAX, ANGLE_MIN, ANGLE_MAX)

    # Print the current motor angles and depth
    print(f"Adjusted pan to {pan_pwm} microseconds (~{pan_angle}degrees) and tilt to {tilt_pwm} microseconds (~{tilt_angle}degrees)")
    print(f"Depth to object: {depth:.2f} meters")

# Initialize the socket for receiving data
def receive_coordinates():
    # Define IP and port for the server (Raspberry Pi)
    server_ip = '172.20.10.2'  # Listen on all available interfaces
    port = 5005

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    sock.bind((server_ip, port))

    # Listen for incoming connections
    sock.listen(1)
    print("Waiting for connection...")

    while True:
        # Wait for a connection
        connection, client_address = sock.accept()

        try:
            print(f"Connection from {client_address}")

            # Receive the data in small chunks
            data = connection.recv(32)
            if data:
                # Split the received data into coordinates and depth
                coordinates = data.decode('utf-8')
                center_x, center_y, depth = map(float, coordinates.split(','))
                center_x, center_y = int(center_x), int(center_y)

                print(f"Received coordinates: X={center_x}, Y={center_y}, Depth={depth:.2f}")

                # Control the pan/tilt mechanism with the received coordinates and depth
                control_pan_tilt(center_x, center_y, depth)

        finally:
            # Clean up the connection
            connection.close()

# Start receiving coordinates and controlling the pan/tilt mechanism
receive_coordinates()