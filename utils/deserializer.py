import sys
import os
import ctypes

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers.packets.packet_parser import PacketHeader, packet_header_to_class_map

def ctypes_to_dict(ctypes_obj):
    """
    Convert a ctypes object to a dictionary.
    This function recursively converts nested ctypes structures and arrays.
    If the ctypes object is an array, it converts each element to a dictionary.
    If it is a structure, it converts each field to a dictionary entry.
    If it is a simple type, it returns the value directly.

    :param ctypes_obj: A ctypes object (Structure or Array).
    """
    if isinstance(ctypes_obj, ctypes.Array):
        return [ctypes_to_dict(item) for item in ctypes_obj]
    elif isinstance(ctypes_obj, ctypes.Structure):
        result = {}
        for field_name, _ in ctypes_obj._fields_:
            value = getattr(ctypes_obj, field_name)
            result[field_name] = ctypes_to_dict(value) if isinstance(value, (ctypes.Array, ctypes.Structure)) else value
        return result
    else:
        return ctypes_obj

def find_next_header(data, start_offset, header_bytes=b'\xe8\x07\x18'):
    """
    Search for the next valid header in the data stream starting from a given offset.
    The function looks for the specified header bytes in the data and returns the offset where it is found.
    If no valid header is found, it raises a ValueError.

    :param data: The byte stream to search in.
    :param start_offset: The offset from which to start searching.
    :param header_bytes: The bytes that represent a valid header (research done shows that the following
     hexadecimal is the one used in EA F1 24 to identify a header: 0xe8 0x07 0x18).
    """
    search_offset = data.find(header_bytes, start_offset)
    if search_offset == -1:
        raise ValueError("No valid header found in the remaining data")
    return search_offset

# Function to deserialize multiple packets
def deserialize_packets(data):
    """
    Deserialize multiple packets from a byte stream.
    The function iterates over the data stream, parsing each packet and storing it in a list.
    It validates the header for each packet, extracts the packet type, and uses the corresponding class
    to parse the packet data. If a header is invalid or incomplete, it searches for the next valid header.
    If a packet is incomplete, it stops parsing further packets.

    :param data: The byte stream containing the packets to be deserialized.
    """
    offset = 16  # Start with an initial offset
    packets = []  # Store parsed packets
    HEADER_BYTES = b'\xe8\x07\x18'  # Expected bytes for a valid header

    while offset < len(data):
        # Step 1: Validate the header
        if data[offset:offset + len(HEADER_BYTES)] != HEADER_BYTES:
            print(f"Invalid header at offset {offset}. Searching for next valid header...")
            try:
                offset = find_next_header(data, offset)
            except ValueError:
                print("No more valid headers found. Stopping parsing.")
                break

        # Step 2: Extract the packet header
        if offset + ctypes.sizeof(PacketHeader) > len(data):
            print(f"Incomplete PacketHeader at offset {offset}. Stopping parsing.")
            break

        header = PacketHeader.from_buffer_copy(data[offset:offset + ctypes.sizeof(PacketHeader)])
        print(f"Parsed header at offset {offset}: {ctypes_to_dict(header)}")

        # Step 3: Get the corresponding packet class
        packet_type = header.m_packetId
        if packet_type not in packet_header_to_class_map:
            print(f"Unknown packet type {packet_type} at offset {offset}. Skipping...")
            offset += 3 + ctypes.sizeof(PacketHeader)  # Skip this header and 3 bytes of padding
            continue

        packet_class = packet_header_to_class_map[packet_type]
        packet_size = ctypes.sizeof(packet_class)

        # Step 4: Validate and extract the packet
        if offset + packet_size > len(data):
            print(f"Incomplete packet at offset {offset}. Stopping parsing.")
            break

        packet = packet_class.from_buffer_copy(data[offset:offset + packet_size])
        parsed_packet = ctypes_to_dict(packet)
        packets.append(parsed_packet)

        # Step 5: Adjust the offset (account for 3-byte padding)
        offset += 3 + packet_size

    return packets

def flatten_dict(source_dict, parent_key="", sep="_"):
    """
    Flattens a nested dictionary, combining keys into a single level using `sep`.

    Example:
      {"m_header": {"m_packetFormat": 2024}} 
      => {"m_header_m_packetFormat": 2024}

    If we have lists, we also index them: 
      {"m_carTelemetryData": [{"m_speed": 280}, {"m_speed": 281}]}
      => {
           "m_carTelemetryData_0_m_speed": 280,
           "m_carTelemetryData_1_m_speed": 281
         }

    :param source_dict: The dictionary to flatten.
    :param parent_key: The base key to prepend to each flattened key.
    :param sep: The separator to use between keys. Default is the underscore _.
    """
    items = []
    for key, value in source_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            # Flatten sub-dict
            items.extend(flatten_dict(value, new_key, sep).items())
        elif isinstance(value, list):
            # Flatten each element in the list
            for i, elem in enumerate(value):
                elem_key = f"{new_key}{sep}{i}"
                if isinstance(elem, dict):
                    items.extend(flatten_dict(elem, elem_key, sep).items())
                else:
                    items.append((elem_key, elem))
        else:
            items.append((new_key, value))
    return dict(items)
