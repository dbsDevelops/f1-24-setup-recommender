import sys
import os
import ctypes

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from helpers.packets.packet_parser import PacketHeader, HEADER_FIELD_TO_PACKET_TYPE

def ctypes_to_dict(ctypes_obj):
    """
    Convert a ctypes object to a dictionary.
    This function recursively converts nested ctypes structures and arrays.
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
        if packet_type not in HEADER_FIELD_TO_PACKET_TYPE:
            print(f"Unknown packet type {packet_type} at offset {offset}. Skipping...")
            offset += 3 + ctypes.sizeof(PacketHeader)  # Skip this header and 3 bytes of padding
            continue

        packet_class = HEADER_FIELD_TO_PACKET_TYPE[packet_type]
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
