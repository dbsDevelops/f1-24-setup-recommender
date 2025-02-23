import socket
import threading
import os
import datetime
import pandas as pd
from deserializer import ctypes_to_dict, flatten_dict
from helpers.packets.PackerParser import PacketHeader, HEADER_FIELD_TO_PACKET_TYPE

# Use the port where the data is being received
PORT = 20776
STOP_COMMAND = "run"
CURRENT_TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
DATA_DIRECTORY = "./data/raw/" + CURRENT_TIMESTAMP

# Lists to store packets for each stream
motion_packets = []
session_packets = []
lap_packets = []
car_setup_packets = []
car_telemetry_packets = []
time_trial_packets = []

def initialize_socket():
    """Creates and configures the UDP socket."""
    udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_socket.bind(('', PORT))
    udp_socket.setblocking(False)
    return udp_socket

def generate_file_path(packet_type):
    """Generates a timestamped file path for storing recorded data."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{DATA_DIRECTORY}/{packet_type}_data_{timestamp}.csv"

def confirm_overwrite(file_path):
    """Asks for confirmation if the file already exists."""
    if os.path.isfile(file_path):
        print(f"WARNING: The file {file_path} already exists and will be overwritten if you continue.")
        user_choice = input("Continue? [y|N]: ")
        if user_choice.lower() != "y":
            print("Change the file path to prevent overwriting and restart the program.")
            exit(0)

def parse_packet(data):
    """
    Deserializes a UDP packet and converts it to a dictionary.
    The PacketHeader is used to determine the packet type.
    """
    try:
        header = PacketHeader.from_buffer_copy(data)
        packet_type = HEADER_FIELD_TO_PACKET_TYPE.get(header.m_packetId)
        if packet_type:
            packet = packet_type.from_buffer_copy(data)
            packet_dict = ctypes_to_dict(packet)
            # Also extract the packetId from the header and put it at the top level
            packet_dict["m_packetId"] = ctypes_to_dict(header)["m_packetId"]
            return packet_dict
    except Exception as e:
        print(f"Error parsing packet: {e}")
    return None


def add_unique_key(packet):
    """
    Adds a unique key to the packet dictionary composed of m_sessionTime and m_frameIdentifier.
    This key will help during the join/merge process later.
    """
    try:
        session_time = packet.get("m_sessionTime")
        frame_identifier = packet.get("m_frameIdentifier")
        # Combine the two fields into a string; you can also store it as a tuple if desired.
        packet["unique_key"] = f"{session_time}_{frame_identifier}"
    except Exception as e:
        print(f"Error adding unique key: {e}")
    return packet

def process_motion_packet(packet):
    """Processes a motion packet, adding a unique key and storing it in the motion_packets list."""
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    motion_packets.append(flattened_packet)

def process_session_packet(packet):
    """Processes a session packet, adding a unique key and storing it in the session_packets list."""
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    session_packets.append(flattened_packet)

def process_lap_packet(packet):
    """Processes a lap packet, adding a unique key and storing it in the lap_packets list."""
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    lap_packets.append(flattened_packet)

def process_car_setup_packet(packet):
    """Processes a car setup packet, adding a unique key and storing it in the car_setup_packets list."""
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    car_setup_packets.append(flattened_packet)

def process_car_telemetry_packet(packet):
    """Processes a car telemetry packet, adding a unique key and storing it in the car_telemetry_packets list."""
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    car_telemetry_packets.append(flattened_packet)

def process_time_trial_packet(packet):
    """Processes a time trial packet, adding a unique key and storing it in the time_trial_packets list."""
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    time_trial_packets.append(flattened_packet)

def process_packet(parsed_data):
    """
    Routes the parsed packet to the correct processing function based on its packet ID.
    The IDs are defined in the UDP spec for F1 24:
      - Motion Data      : 0
      - Session Data     : 1
      - Lap Data         : 2
      - Car Setup Data   : 5
      - Car Telemetry Data: 6
      - Time Trial Data  : 14
    """
    if parsed_data is None:
        return

    packet_id = parsed_data["m_header"].get("m_packetId")
    if packet_id == 0:
        process_motion_packet(parsed_data)
    elif packet_id == 1:
        process_session_packet(parsed_data)
    elif packet_id == 2:
        process_lap_packet(parsed_data)
    elif packet_id == 5:
        process_car_setup_packet(parsed_data)
    elif packet_id == 6:
        process_car_telemetry_packet(parsed_data)
    elif packet_id == 14:
        process_time_trial_packet(parsed_data)
    # Ignore other packet types if not needed

def receive_packets(udp_socket: socket.socket):
    """Continuously receives packets and processes them until the stop command is received."""
    global STOP_COMMAND
    print("Receiving UDP packets. Type 'stop' to end recording.")
    
    while STOP_COMMAND != "stop":
        try:
            data, _ = udp_socket.recvfrom(2048)
            print("Received data:", data)
            parsed_data = parse_packet(data)
            print("Parsed data:", parsed_data)
            if parsed_data:
                process_packet(parsed_data)
        except BlockingIOError:
            pass
    
    udp_socket.close()

def save_data_to_csv(data, file_path):
    """Saves the list of packet dictionaries to a CSV file."""
    if data:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        print(f"Saved {len(df)} records to {file_path}")
    else:
        print(f"No data to save for in {file_path}")

def listen_for_stop_command():
    """Listens for the 'stop' command to end data recording."""
    global STOP_COMMAND
    while STOP_COMMAND != "stop":
        STOP_COMMAND = input("Enter 'stop' to stop the data recording: ")

def main():
    """Main execution function."""
    # Ensure the data directory exists before storing the data
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)

    # Initialize the UDP socket
    udp_socket = initialize_socket()

    # Start receiver and command-listener threads
    receiver_thread = threading.Thread(target=receive_packets, args=(udp_socket,))
    input_thread = threading.Thread(target=listen_for_stop_command)
    receiver_thread.start()
    input_thread.start()
    receiver_thread.join()
    input_thread.join()

    # After data collection, save each stream to its own CSV file.
    save_data_to_csv(motion_packets, generate_file_path("motion"))
    save_data_to_csv(session_packets, generate_file_path("session"))
    save_data_to_csv(lap_packets, generate_file_path("lap"))
    save_data_to_csv(car_setup_packets, generate_file_path("car_setup"))
    save_data_to_csv(car_telemetry_packets, generate_file_path("car_telemetry"))
    save_data_to_csv(time_trial_packets, generate_file_path("time_trial"))

if __name__ == "__main__":
    main()