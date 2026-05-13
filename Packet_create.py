
import random
from scapy.layers.inet import IP,UDP,TCP
from scapy.all import Raw,send
import os

TARGET_HOST = os.environ.get("TARGET_HOST")
PACKET_SIZE = int(os.environ.get("PACKET_SIZE", 60))

IP_BASE = 20
UDP_HDR = 8
TCP_BASE = 20

if PACKET_SIZE < IP_BASE + UDP_HDR:
    print(f"Zadána menší než standartní velikost paketu. Bude použita standartní velikost. \n "
          f" Pro větší velikost  musí být packet_size alespoň >= {IP_BASE + UDP_HDR}")

if PACKET_SIZE < IP_BASE + TCP_BASE:
    print(f"target_ip_len musí být >= {IP_BASE + TCP_BASE} (IP + TCP hlavička)")

def udp_packet(dst_port,src_ip=None):

    sport = random.randint(1,65535)

    payload_len = PACKET_SIZE - (IP_BASE + UDP_HDR)
    if payload_len > 0:
        payload = os.urandom(payload_len)
    else:
        payload = b""
    pkt = IP(dst=TARGET_HOST, src=src_ip) / UDP(sport=sport, dport=dst_port) / Raw(load=payload)
    pkt[IP].len = PACKET_SIZE
    pkt[IP].chksum = None
    pkt[UDP].len = None
    pkt[UDP].chksum = None
    send(pkt,verbose=False)

def tcp_packet(dst_port, src_ip=None):
    sport = random.randint(1,65535)

    min_total = IP_BASE + TCP_BASE
    if PACKET_SIZE < min_total:
        print(f"target_ip_len musí být >= {min_total} (IP + TCP hlavička)")

    payload_len = PACKET_SIZE - (IP_BASE + TCP_BASE)
    if payload_len > 0:
        payload = os.urandom(payload_len)
    else:
        payload = b""

    tcp_layer = TCP(sport=sport, dport=dst_port, flags="S")
    pkt = IP(dst=TARGET_HOST, src=src_ip)/tcp_layer/Raw(load=payload)
    pkt[IP].len = PACKET_SIZE
    pkt[IP].chksum = None
    pkt[TCP].chksum = None
    send(pkt, verbose=False)

