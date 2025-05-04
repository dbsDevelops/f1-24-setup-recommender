import helpers.packets.packet_manager as pm

class PacketHandler:
    def __init__(self, window_manager):
        self.window_manager = window_manager
        self.map_canvas = window_manager.map_canvas

        self.function_hashmap = {
            0: (pm.update_motion, (self.map_canvas, None)),
            1: (pm.update_session, (window_manager.top_label1, window_manager.top_label2, window_manager.main_window, self.map_canvas)),
            2: (pm.update_lap_data, ()),
            3: (pm.warnings, ()),
            4: (pm.update_participants, ()),
            5: (pm.update_car_setups, ()),
            6: (pm.update_car_telemetry, ()),
            7: (pm.update_car_status, ()),
            8: (pm.nothing, ()),
            9: (pm.delete_map, ()),
            10: (pm.update_car_damage, ()),
        }

    def process_packet(self, packet_id, packet):
        """Processes the received packet based on its ID."""
        if packet_id in self.function_hashmap:
            func, args = self.function_hashmap[packet_id]
            func(packet, *args)