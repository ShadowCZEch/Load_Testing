
import random
from scapy.layers.inet import IP,UDP,TCP
from scapy.all import Raw
from scapy.supersocket import L3RawSocket
import os

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

_iface = os.environ.get("IFACE", "eth0")
_socket = L3RawSocket(iface=_iface)


def udp_packet(dst_port,src_ip=None):

    sport = random.randint(1,65535)

    pkt = IP(dst=TARGET_HOST, src=src_ip, len=PACKET_SIZE, chksum=0) / \
          UDP(sport=sport, dport=dst_port, chksum=0) / \
          Raw(load=_udp_payload)
    _socket.send(pkt)

def tcp_packet(dst_port, src_ip=None):
    sport = random.randint(1,65535)

    pkt = IP(dst=TARGET_HOST, src=src_ip, len=PACKET_SIZE, chksum=0) / \
          TCP(sport=sport, dport=dst_port, flags="S", chksum=0) / \
          Raw(load=_tcp_payload)
    _socket.send(pkt)

