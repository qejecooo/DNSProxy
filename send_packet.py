import struct
import socket


def send_tcp(data: list, host: str, port: int) -> bytes:
    """
    Method to send TCP packet to our upstream DNS server and return the response.
        :param data: The DNS packet to send.
        :param host: The upstream DNS server to send the packet to.
        :param port: The port to send the packet to.
        :return: The response from the upstream DNS server.
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.sendall(data)
        response = sock.recv(8192)
        length = struct.unpack("!H", bytes(response[:2]))[0]
        while len(response) - 2 < length:
            response += sock.recv(8192)
        return response
    finally:
        if (sock is not None):
            sock.close()


def send_udp(data: list, host: str, port: int) -> bytes:
    """
    Method to send UDP packet to our upstream DNS server and return the response.
        :param data: The DNS packet to send.
        :param host: The upstream DNS server to send the packet to.
        :param port: The port to send the packet to.
        :return: The response from the upstream DNS server.
    """
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (host, port))
        response, server = sock.recvfrom(8192)
        return response
    finally:
        if (sock is not None):
            sock.close()
