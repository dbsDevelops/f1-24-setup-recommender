import helpers.packets.packet_parser as parser

class UDPListener:
    """
    A class to listen for UDP packets on a specified port and redirect them to a given IP address and port.
    This class uses the `Listener` from the `packet_parser` module to handle incoming UDP packets.
    Attributes:
        port (int): The port number to listen on.
        redirect (bool): Whether to redirect the packets.
        ip_address (str): The IP address to redirect packets to.
        redirect_port (int): The port number to redirect packets to.
        listener (Listener): An instance of the Listener class to handle UDP packets.
    """
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