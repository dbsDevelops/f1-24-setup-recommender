import socket
import threading
import os
import datetime
import pandas as pd
import glob

from deserializer import ctypes_to_dict, flatten_dict
from helpers.packets.packet_parser import PacketHeader, packet_header_to_class_map
from models.packet_type import PacketType

# Use the port where the data is being received
CIRCUIT = "monza"
PORT = 20776
EXECUTION_COMMAND = "run"
CURRENT_TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
DATA_DIRECTORY = f"./data/raw/{CIRCUIT}/" + CURRENT_TIMESTAMP
BUFFER_SIZE = 2048

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
    """
    Generates a timestamped file path for storing recorded data.
    The file path is based on the packet type and the current timestamp.

    :param packet_type: The type of packet (e.g., "motion", "session", etc.)
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{DATA_DIRECTORY}/{packet_type}_data_{timestamp}.csv"

def parse_packet(data):
    """
    Deserializes a UDP packet and converts it to a dictionary.
    The PacketHeader is used to determine the packet type.

    :param data: The raw byte data of the packet.
    """
    try:
        header = PacketHeader.from_buffer_copy(data)
        packet_type = packet_header_to_class_map.get(header.m_packetId)
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

    :param packet: The packet dictionary to which the unique key will be added.
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
    """
    Processes a motion packet, adding a unique key and storing it in the motion_packets list.
    
    :param packet: The motion packet dictionary to be processed.
    """
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    motion_packets.append(flattened_packet)

def process_session_packet(packet):
    """
    Processes a session packet, adding a unique key and storing it in the session_packets list.
    
    :param packet: The session packet dictionary to be processed.
    """
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    session_packets.append(flattened_packet)

def process_lap_packet(packet):
    """
    Processes a lap packet, adding a unique key and storing it in the lap_packets list.
    
    :param packet: The lap packet dictionary to be processed.
    """
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    lap_packets.append(flattened_packet)

def process_car_setup_packet(packet):
    """
    Processes a car setup packet, adding a unique key and storing it in the car_setup_packets list.
    
    :param packet: The car setup packet dictionary to be processed.
    """
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    car_setup_packets.append(flattened_packet)

def process_car_telemetry_packet(packet):
    """
    Processes a car telemetry packet, adding a unique key and storing it in the car_telemetry_packets list.
    
    :param packet: The car telemetry packet dictionary to be processed.
    """
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    car_telemetry_packets.append(flattened_packet)

def process_time_trial_packet(packet):
    """
    Processes a time trial packet, adding a unique key and storing it in the time_trial_packets list.
    
    :param packet: The time trial packet dictionary to be processed.
    """
    packet = add_unique_key(packet)
    flattened_packet = flatten_dict(packet)
    time_trial_packets.append(flattened_packet)

def process_packet(parsed_data):
    """
    Routes the parsed packet to the correct processing function based on its packet ID.
    The IDs are defined in the UDP spec for EA F1 24:
      - Motion Data      : 0
      - Session Data     : 1
      - Lap Data         : 2
      - Car Setup Data   : 5
      - Car Telemetry Data: 6
      - Time Trial Data  : 14

    :param parsed_data: The parsed packet data as a dictionary.
    """
    if parsed_data is None:
        return

    packet_id = parsed_data["m_header"].get("m_packetId")
    if packet_id == PacketType.MOTION_DATA.value:
        process_motion_packet(parsed_data)
    elif packet_id == PacketType.SESSION_DATA.value:
        process_session_packet(parsed_data)
    elif packet_id == PacketType.LAP_DATA.value:
        process_lap_packet(parsed_data)
    elif packet_id == PacketType.CAR_SETUP_DATA.value:
        process_car_setup_packet(parsed_data)
    elif packet_id == PacketType.CAR_TELEMETRY_DATA.value:
        process_car_telemetry_packet(parsed_data)
    elif packet_id == PacketType.TIME_TRIAL_DATA.value:
        process_time_trial_packet(parsed_data)
    # Ignore other packet types if not needed

def receive_packets(udp_socket: socket.socket):
    """
    Continuously receives packets and processes them until the stop command is received.
    
    :param socket.socket udp_socket: The UDP socket to listen for incoming packets.
    """
    global EXECUTION_COMMAND
    print("Receiving UDP packets. Type 'stop' to end recording.")
    
    while EXECUTION_COMMAND != "stop":
        try:
            data, _ = udp_socket.recvfrom(BUFFER_SIZE)
            # print("Received data:", data)
            parsed_data = parse_packet(data)
            # print("Parsed data:", parsed_data)
            if parsed_data:
                process_packet(parsed_data)
        except BlockingIOError:
            pass
    
    udp_socket.close()

def save_data_to_csv(data, file_path):
    """
    Saves the list of packet dictionaries to a CSV file.
    
    :param data: The list of packet dictionaries to be saved.
    :param file_path: The path where the CSV file will be saved.
    """
    if data:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        print(f"Saved {len(df)} records to {file_path}")
    else:
        print(f"No data to save for in {file_path}")

def filter_columns(df):
    """
    Only keep m_header_m_sessionTime and m_header_m_frameIdentifier from header columns.
    
    :param df: The DataFrame containing the packet data.
    :return: A DataFrame with filtered columns.
    """
    keep = {"m_header_m_sessionTime", "m_header_m_frameIdentifier"}
    cols = [col for col in df.columns if not col.startswith("m_header_") or col in keep]
    return df[cols]

def join_session_csvs():
    """
    Joins the six CSV files into one general CSV file for this session.
    This function searches for CSV files in the DATA_DIRECTORY that match the expected patterns
    for each packet type and concatenates them into a single DataFrame.
    The resulting DataFrame is then saved as a general CSV file.
    If no CSV files are found, it prints a message and returns None.

    :return: The path to the general CSV file or None if no files were found.
    """
    csv_types = ["motion", "session", "lap", "car_setup", "car_telemetry", "time_trial"]
    df_list = []
    for t in csv_types:
        # Find files that match the pattern in this session folder.
        files = glob.glob(os.path.join(DATA_DIRECTORY, f"{t}_data_*.csv"))
        for f in files:
            df = pd.read_csv(f)
            df = filter_columns(df)
            # Optionally add a column indicating the packet type:
            df["packet_type"] = t
            df_list.append(df)
    if df_list:
        general_df = pd.concat(df_list, ignore_index=True, sort=False)
        general_csv = os.path.join(DATA_DIRECTORY, f"general_data_{CURRENT_TIMESTAMP}.csv")
        general_df.to_csv(general_csv, index=False)
        print(f"General CSV saved: {general_csv}")
        return general_csv
    else:
        print("No CSV files to join in the session folder.")
        return None
    
def save_general_csv(df, file_path):
    """
    Saves the general CSV file to the specified path.
    
    :param df: The DataFrame containing the general data to be saved.
    :param file_path: The path where the general CSV file will be saved.
    """
    df.to_csv(file_path, index=False)
    print(f"General CSV saved: {file_path}")

def update_master_dataset(new_general_csv):
    """
    Updates the master dataset CSV with the new general CSV.
    
    :param new_general_csv: The path to the new general CSV file to be added to the master dataset.
    """
    master_csv = "./data/dataset.csv"
    # Ensure the parent folder for the master CSV exists:
    os.makedirs("./data", exist_ok=True)
    new_df = pd.read_csv(new_general_csv)
    if os.path.exists(master_csv):
        master_df = pd.read_csv(master_csv)
        combined_df = pd.concat([master_df, new_df], ignore_index=True, sort=False)
    else:
        combined_df = new_df
    combined_df.to_csv(master_csv, index=False)
    print(f"Master dataset updated: {master_csv}")

def listen_for_stop_command():
    """Listens for the 'stop' command to end data recording."""
    global EXECUTION_COMMAND
    while EXECUTION_COMMAND != "stop":
        EXECUTION_COMMAND = input("Enter 'stop' to stop the data recording: ")

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

    # Join the six CSV files into one general CSV file for this session.
    join_session_csvs()
    # if general_csv:
    #     update_master_dataset(general_csv)

if __name__ == "__main__":
    main()
