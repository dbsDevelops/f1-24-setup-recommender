import socket
import threading
import os
import datetime
import pandas as pd
from deserializer import ctypes_to_dict
from packet_parser.parser2024 import PacketHeader, HEADER_FIELD_TO_PACKET_TYPE
import ctypes

PORT = 20776
STOP_COMMAND = "stop"
DATA_DIRECTORY = "./data/raw"

def initialize_socket():
    """Creates and configures the UDP socket."""
    udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_socket.bind(('', PORT))
    udp_socket.setblocking(False)
    return udp_socket

def generate_file_path():
    """Generates a timestamped file path for storing recorded data."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{DATA_DIRECTORY}/data_{timestamp}.csv"

def confirm_overwrite(file_path):
    """Asks the user for confirmation before overwriting an existing file."""
    if os.path.isfile(file_path):
        print(f"WARNING: The file {file_path} already exists and will be overwritten if you continue.")
        user_choice = input("Continue? [y|N]: ")
        if user_choice.lower() != "y":
            print("Change the file path to prevent overwriting and restart the program.")
            exit(0)

def parse_packet(data):
    """Deserializes a UDP packet and converts it to a dictionary."""
    try:
        header = PacketHeader.from_buffer_copy(data)
        packet_type = HEADER_FIELD_TO_PACKET_TYPE.get(header.m_packetId)
        if packet_type:
            packet = packet_type.from_buffer_copy(data)
            return ctypes_to_dict(packet)
    except Exception as e:
        print(f"Error parsing packet: {e}")
    return None

def receive_packets(udp_socket, file_path):
    """Receives and processes UDP packets, storing them in a DataFrame."""
    columns = []
    all_data = []
    global STOP_COMMAND
    print("Receiving UDP packets. Type 'stop' to end recording.")
    
    while STOP_COMMAND != "stop":
        try:
            data, _ = udp_socket.recvfrom(2048)
            parsed_data = parse_packet(data)
            if parsed_data:
                if not columns:
                    columns = list(parsed_data.keys())
                all_data.append(parsed_data)
        except BlockingIOError:
            pass
    
    save_data_to_csv(all_data, columns, file_path)
    udp_socket.close()
    exit(0)

def save_data_to_csv(data, columns, file_path):
    """Saves the collected data to a CSV file."""
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(file_path, index=False)
    print(f"\nRecording finished: {len(df)} records stored in {file_path}")

def listen_for_stop_command():
    """Monitors user input for a stop command."""
    global STOP_COMMAND
    while STOP_COMMAND != "stop":
        STOP_COMMAND = input("Enter 'stop' to stop data recording: ")

def main():
    """Main execution function."""
    file_path = generate_file_path()
    confirm_overwrite(file_path)
    udp_socket = initialize_socket()
    
    receiver_thread = threading.Thread(target=receive_packets, args=(udp_socket, file_path))
    input_thread = threading.Thread(target=listen_for_stop_command)
    
    receiver_thread.start()
    input_thread.start()

if __name__ == "__main__":
    main()