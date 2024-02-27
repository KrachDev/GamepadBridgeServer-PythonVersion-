import socket
import binascii
import vgamepad as vg
import threading

# Get the list of current available IP addresses on the machine
def get_available_ip_addresses():
    hostname = socket.gethostname()
    ip_addresses = socket.getaddrinfo(hostname, None)
    return [ip[4][0] for ip in ip_addresses]

# Prompt the user to choose an IP address by its index
def choose_ip_address(ip_addresses):
    print("Available IP addresses:")
    for i, ip in enumerate(ip_addresses):
        print(f"{i + 1}. {ip}")
    index = int(input("Enter the index of the desired IP address: ")) - 1
    if index < 0 or index >= len(ip_addresses):
        raise ValueError("Invalid index")
    return ip_addresses[index]

# Get the machine's IP address
ip_addresses = get_available_ip_addresses()
selected_ip = choose_ip_address(ip_addresses)

# Set the SERVER_HOST variable
SERVER_HOST = selected_ip

# Server settings
SERVER_PORT = 5000
BUFFER_SIZE = 8024
TIMEOUT = 0.1 # in seconds

# Initialize virtual gamepad
gamepad = vg.VX360Gamepad()
print("Gamepad Started!")
# Define the function to convert a byte to a float value
def convert_byte_to_float(byte):
    return byte / 255.0
def byte_to_float(byte):
    return (byte / 127.5) - 1.0
def convert_to_analog(value):
  # Convert the value from the range [0, 100] to the range [0, 1]
  normalized_value = value / 100.0
  # Convert the normalized value to the range [-1, 1]
  analog_value = (normalized_value * 2) - 1
  return analog_value
# Define payload-action mappings
payload_actions = {
    b'\x16': lambda data: gamepad.left_joystick_float(x_value_float=convert_to_analog(data[1]), y_value_float=-convert_to_analog(data[2])),
    b'\x13': lambda data: gamepad.right_joystick_float(x_value_float=convert_to_analog(data[1]), y_value_float=-convert_to_analog(data[2])),
    b'\x00\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A),
    b'\x00\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A),
    b'\x01\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B),
    b'\x01\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B),
    b'\x02\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X),
    b'\x02\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X),
    b'\x03\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y),
    b'\x03\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y),
    b'\x04\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER),
    b'\x04\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER),
    b'\x05\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER),
    b'\x05\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER),
    b'\x06\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START),
    b'\x06\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START),
    b'\x07\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK),
    b'\x07\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK),
    b'\x08\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB),
    b'\x08\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB),
    b'\x09\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB),
    b'\x09\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB),
    b'\x10\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE ),
    b'\x10\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE),
    b'\x11\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN),
    b'\x11\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN),
    b'\x12\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP),
    b'\x12\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP),
    b'\x14\x00': lambda data: gamepad.right_trigger(value=int(convert_byte_to_float(data[-1]) * 255)), # value between 0 and 255
    b'\x15\x00': lambda data: gamepad.left_trigger(value=int(convert_byte_to_float(data[-1]) * 255)),  # value between 0 and 255
    b'\x17\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT),
    b'\x17\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT),
    b'\x18\x01': lambda data: gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT),
    b'\x18\x00': lambda data: gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT),
    b'\x99\x99': lambda data: print("Client Connected!!"),
    b'\x99\x88': lambda data: print(f"Client Disconnected!!: [client_address]"),

}


# Function to handle client requests
def handle_client(data, client_address):
    # Print raw data received from the client as hexadecimal
    hex_data = binascii.hexlify(data).decode()
    #print(f"Received data from {client_address}: {hex_data}")

    # Check if the first byte of the received data is in the payload-action mappings
    first_byte = data[:2]
    if first_byte in payload_actions:
        action = payload_actions[first_byte]
        #print("Performing action:", action)
        action(data)  # Call the lambda function with the data argument

    analog_byte = data[:1]
    if analog_byte in payload_actions:
        action = payload_actions[analog_byte]
        #print("Performing action:", action)
        action(data)  # Call the lambda function with the data argument  
# Function to start the UDP server
def start_server():
    # Initialize server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.settimeout(TIMEOUT)
    print("Server Started!")

    print(f"UDP server is running on {SERVER_HOST}:{SERVER_PORT}")

    # Main server loop
    while True:
        try:
            # Receive packet from client
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            
            # Handle client request in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(data, client_address))
            client_thread.start()
            gamepad.update()  # send the updated state to the computer

        except socket.timeout:
            #print("Timeout occurred. Waiting for new packets...")
            pass
        
        except KeyboardInterrupt:
            print("Server stopped.")
            break

    # Close server socket
    server_socket.close()

# Start the server
start_server()
