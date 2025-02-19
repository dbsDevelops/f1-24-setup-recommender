import sys
import time
from ttkbootstrap import Window

from config.settings_loader import load_settings
from ui.window_manager import WindowManager
from network.udp_listener import UDPListener
from helpers.packets.PacketHandler import PacketHandler


class TelemetryApp:
    def __init__(self):
        self.settings = load_settings()
        self.main_window = Window(themename="darkly")
        self.window_manager = WindowManager(self.main_window)
        self.packet_handler = PacketHandler(self.window_manager)

        self.listener = UDPListener(
            port=self.settings["port"],
            redirect=self.settings["redirect_active"],
            ip_address=self.settings["ip_adress"],
            redirect_port=self.settings["redirect_port"],
        )

        self.running = True
        self.last_update = time.time()
        self.packet_received = [0] * 15

    def run(self):
        """Main loop handling packet reception and UI updates."""
        while self.running:
            packet_data = self.listener.receive()
            if packet_data:
                header, packet = packet_data
                self.packet_received[header.m_packet_id] += 1
                self.packet_handler.process_packet(header.m_packet_id, packet)

            if time.time() > self.last_update + 1:
                self.last_update = time.time()
                self.window_manager.update_packet_reception(self.packet_received)
                self.packet_received = [0] * 15

            self.window_manager.refresh_ui()

        self.shutdown()

    def shutdown(self):
        """Handles cleanup operations on shutdown."""
        self.listener.close()
        self.main_window.quit()


if __name__ == "__main__":
    app = TelemetryApp()
    app.run()