import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print("Root dir:", root_dir)
sys.path.append(root_dir)

import time
from ttkbootstrap import Window

from config.settings_loader import load_settings
from ui.window_manager import WindowManager
from network.udp_listener import UDPListener
from helpers.packets.packet_handler import PacketHandler


class TelemetryApp:
    """
    Main application class for the telemetry system.
    Initializes the main window, network listener, and packet handler.
    Handles the main loop for receiving packets and updating the UI.

    Attributes:

        settings (dict): Application settings loaded from configuration.
        main_window (Window): The main application window.
        window_manager (WindowManager): Manages the UI components and updates.
        packet_handler (PacketHandler): Handles incoming packets and processes them.
        listener (UDPListener): Listens for incoming UDP packets.
        running (bool): Flag to control the main loop execution.
        last_update (float): Timestamp of the last UI update.
        packet_received (list): List to count received packets by type.
    """
    def __init__(self):
        """Initialize the telemetry application."""
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

        # Bind the window close event to the close_window method
        self.main_window.protocol("WM_DELETE_WINDOW", self.close_window)

    def run(self):
        """Main loop handling packet reception and UI updates."""
        while self.running:
            packet_data = self.listener.receive()
            if packet_data:
                header, packet = packet_data
                self.packet_received[header.m_packetId] += 1
                self.packet_handler.process_packet(header.m_packetId, packet)

            if time.time() > self.last_update + 1:
                self.last_update = time.time()
                self.window_manager.update_packet_reception(self.packet_received)
                self.packet_received = [0] * 15

            self.window_manager.refresh_ui()

        self.shutdown()
    
    def close_window(self):
        """Handles window closing event."""
        self.running = False  # Stop the main loop
        self.shutdown()

    def shutdown(self):
        """Handles cleanup operations on shutdown."""
        self.listener.close()
        self.main_window.quit()


if __name__ == "__main__":
    app = TelemetryApp()
    app.run()
    