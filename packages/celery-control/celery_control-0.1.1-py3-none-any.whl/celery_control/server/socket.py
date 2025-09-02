"""This module provides methods for setup socket."""
import socket


def get_best_family(host: str, port: int) -> tuple[socket.AddressFamily, str, int]:
    """Automatically select address family depending on address."""
    # HTTPServer defaults to AF_INET, which will not start properly if
    # binding an ipv6 address is requested.
    # This function is based on what upstream python did for http.server
    # in https://github.com/python/cpython/pull/11767
    addr_info_list = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM, flags=socket.AI_PASSIVE)
    addr_info = addr_info_list[0]
    family = addr_info[0]
    sockaddr = addr_info[4]
    return family, sockaddr[0], sockaddr[1]
