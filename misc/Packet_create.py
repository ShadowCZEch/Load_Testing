
import random
from scapy.layers.inet import IP,UDP,TCP
from scapy.all import Raw
from scapy.supersocket import L3RawSocket
import os
import ipaddress
from scapy.layers.inet6 import IPv6

TARGET_HOST = os.environ.get("TARGET_HOST")
PACKET_SIZE = int(os.environ.get("PACKET_SIZE", 60))
PROTOCOL = os.environ.get("LOCUST_MODE", "").lower()

IP_BASE = 20
UDP_HDR = 8
TCP_BASE = 20

_udp_payload_len = max(0, PACKET_SIZE - (IP_BASE + UDP_HDR))
_tcp_payload_len = max(0, PACKET_SIZE - (IP_BASE + TCP_BASE))
_udp_payload = os.urandom(_udp_payload_len) if _udp_payload_len > 0 else b""
_tcp_payload = os.urandom(_tcp_payload_len) if _tcp_payload_len > 0 else b""

_socket = None

def _is_ipv6(addr):
    try:
        ipaddress.IPv6Address(addr)
        return True
    except ValueError:
        return False

def _get_socket():
    global _socket
    if _socket is None:
        _iface = os.environ.get("IFACE")
        if not _iface:
            raise RuntimeError("IFACE environment variable not set. Cannot create socket.")
        print(f"[Packet_create] Using interface: {_iface}")
        if _is_ipv6(TARGET_HOST):
            from scapy.supersocket import L3RawSocket6
            _socket = L3RawSocket6(iface=_iface)
        else:
            _socket = L3RawSocket(iface=_iface)
    return _socket

def udp_packet(dst_port,src_ip=None):
    sport = random.randint(1,65535)

    if _is_ipv6(TARGET_HOST):
        pkt = IPv6(dst=TARGET_HOST, src=src_ip) / \
              UDP(sport=sport, dport=dst_port) / \
              Raw(load=_udp_payload)
    else:
        pkt = IP(dst=TARGET_HOST, src=src_ip, len=PACKET_SIZE, chksum=0) / \
              UDP(sport=sport, dport=dst_port, chksum=0) / \
              Raw(load=_udp_payload)
    _get_socket().send(pkt)

def tcp_packet(dst_port, src_ip=None):
    sport = random.randint(1,65535)

    if _is_ipv6(TARGET_HOST):
        pkt = IPv6(dst=TARGET_HOST, src=src_ip) / \
              TCP(sport=sport, dport=dst_port, flags="S") / \
              Raw(load=_tcp_payload)
    else:
        pkt = IP(dst=TARGET_HOST, src=src_ip, len=PACKET_SIZE, chksum=0) / \
              TCP(sport=sport, dport=dst_port, flags="S", chksum=0) / \
              Raw(load=_tcp_payload)
    _get_socket().send(pkt)

