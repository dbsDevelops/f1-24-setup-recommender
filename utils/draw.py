from helpers.packets.packet_parser import Listener
track = "losail"

PORT=20777
file=open(f"../tracks/{track}_2020_racingline.txt", "a")
file.write(f'"Track file for {track}","2020-07-01 19:31:18",0.000,4,1,v3" \n')
file.write(f'"dist","pos_z","pos_x","pos_y","drs","sector" \n')

file=open(f"../tracks/{track}_2020_racingline.txt", "a")
file.write(f'"Track file for {track}","2020-07-01 19:31:18",0.000,4,1,v3" \n')
file.write(f'"dist","pos_z","pos_x","pos_y","drs","sector" \n')

listener = Listener(port = PORT)
lap_packet, motion_packet, tel_packet = None, None, None
last_lap_distance = 0

# Wait for the first lap data packet to get the car index
while True:
    a = listener.get()
    if a is not None:
        header, packet = a
        car_index = header.m_player_car_index
        if header.m_packetId == 2 and packet.m_lapData[car_index].m_lapDistance<500:
            break

print("démarrage")

# Wait for the first lap data packet to get the car index
while True:
    a = listener.get()
    if a is not None:
        header, packet = a
        if header.m_packet_id == 0:
            motion_packet = (packet.m_carMotionData[car_index].m_worldPositionZ,
            packet.m_carMotionData[car_index].m_worldPositionX,
            packet.m_carMotionData[car_index].m_worldPositionY)
        elif header.m_packetId == 2:
            lap_packet = packet.m_lapData[car_index].m_lapDistance, packet.m_lapData[car_index].m_sector
            if last_lap_distance>lap_packet[0]:
                break
            last_lap_distance=lap_packet[0]
        elif header.m_packetId == 6:
            tel_packet = packet.m_carTelemetryData[car_index].m_drs
        if not (lap_packet is None or motion_packet is None or tel_packet is None):
            a, f = lap_packet
            b,c,d = motion_packet
            e = tel_packet
            file.write(f"{a},{c},{b},{d},{e},{f}\n")
            lap_packet, motion_packet, tel_packet = None, None, None
            file.flush()
listener.close()
