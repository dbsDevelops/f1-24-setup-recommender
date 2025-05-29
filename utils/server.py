import socket

def create_socket(port):
    """
    Creates a UDP socket bound to the specified port.
    The socket is set to non-blocking mode to allow for asynchronous operations.
    
    :param port: The port number to bind the socket to.
    :return: A UDP socket object.
    """
    my_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    my_socket.bind(('', port))
    my_socket.setblocking(False)
    return my_socket


def get(my_socket):
    try:
        packet = my_socket.recv(2048)
        my_socket.sendto(packet, ("90.3.127.79", 20777))
        #my_socket.sendto(packet, ("78.118.228.123", 20785))
        #my_socket.sendto(packet, ("127.0.0.1", 20795))
    except BlockingIOError:
        return
    except ConnectionResetError as e:
        print(e)


udp_sockets = [create_socket(port_number) for port_number in [20773,20775,20776,20777]]

while True:
    for udp_socket in udp_sockets:
        get(udp_socket)
