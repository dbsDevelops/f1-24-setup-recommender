import helpers.packets.packet_parser as parser

class UDPListener:
    def __init__(self, port, redirect, ip_address, redirect_port):
        self.port = int(port)
        self.redirect = redirect
        self.ip_address = ip_address
        self.redirect_port = int(redirect_port)

        self.listener = parser.Listener(
            port=self.port,
            redirect=self.redirect,
            address=self.ip_address,
            redirect_port=self.redirect_port
        )

    def receive(self):
        """Receives data from the UDP socket."""
        return self.listener.get()

    def close(self):
        """Closes the socket connection."""
        self.listener.socket.close()