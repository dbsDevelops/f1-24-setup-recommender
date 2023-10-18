from parser2023 import Listener
file = open("tracks/Las Vegas_2020_racingline.txt", "x")
file.close()


PORT=20777
file=open("tracks/Las Vegas_2020_racingline.txt", "a")
file.write('"Track file for Melbourne","2020-07-01 19:31:18",0.000,4,1,v3" \n')
file.write('"dist","pos_z","pos_x","pos_y","drs","sector" \n')
listener = Listener(port = PORT)
running=True
lap_packet, motion_packet, tel_packet = None, None, None
condition=True
last_lap_distance = 0
car_index = 0
while condition:
    a = listener.get()
    if a is not None:
        header, packet = a
        if header.m_packet_id == 2 and packet.m_lap_data[car_index].m_lap_distance<1_000:
            condition=False

print("démarrage")

while running:
    a = listener.get()
    if a is not None:
        header, packet = a
        if header.m_packet_id == 0:
            motion_packet = (packet.m_car_motion_data[car_index].m_world_position_z,
            packet.m_car_motion_data[car_index].m_world_position_x,
            packet.m_car_motion_data[car_index].m_world_position_y)
        elif header.m_packet_id == 2:
            lap_packet = packet.m_lap_data[car_index].m_lap_distance, packet.m_lap_data[car_index].m_sector
            if last_lap_distance>lap_packet[car_index]:
                file.close()
                print("terminé")
                exit()
            last_lap_distance=lap_packet[car_index]
        elif header.m_packet_id == 6:
            tel_packet = packet.m_car_telemetry_data[car_index].m_drs
        if not (lap_packet is None or motion_packet is None or tel_packet is None):
            a, f = lap_packet
            b,c,d = motion_packet
            e = tel_packet
            file.write(f"{a},{c},{b},{d},{e},{f}\n")
            lap_packet, motion_packet, tel_packet = None, None, None





