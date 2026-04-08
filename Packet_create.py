
import random
from scapy.layers.inet import IP,UDP,TCP
from scapy.all import Raw,send
from Config_Load import Config_Load
import os

def udp_packet(dst_port):

    IP_BASE = 20
    UDP_HDR = 8

    cfg=Config_Load()
    packet_size=int(cfg.get("packet_size"))
    ip_dst=cfg.get("ipaddr")
    sport = random.randint(1,65535)

    if packet_size < IP_BASE + UDP_HDR:
        print(f"Zadána menší než standartní velikost paketu. Bude použita standartní velikost. \n "
                         f" Pro větší velikost  musí být packet_size alespoň >= {IP_BASE + UDP_HDR}")


    payload_len = packet_size - (IP_BASE + UDP_HDR)
    if payload_len > 0:
        payload = os.urandom(payload_len)
    else:
        payload = b""
    pkt = IP(dst=ip_dst)/UDP(sport=sport, dport=dst_port)/Raw(load=payload)
    pkt[IP].len = packet_size
    pkt[IP].chksum = None
    pkt[UDP].len = None
    pkt[UDP].chksum = None
    send(pkt,verbose=False)

def tcp_packet(dst_port):
    cfg=Config_Load()
    packet_size=int(cfg.get("packet_size"))
    ip_dst=cfg.get("ipaddr")
    sport = random.randint(1,65535)

    seq=None
    IP_BASE = 20
    TCP_BASE = 20

    min_total = IP_BASE + TCP_BASE
    if packet_size < min_total:
        print(f"target_ip_len musí být >= {min_total} (IP + TCP hlavička)")

    payload_len = packet_size - (IP_BASE + TCP_BASE)
    if payload_len > 0:
        payload = os.urandom(payload_len)
    else:
        payload = b""

    tcp_layer = TCP(sport=sport, dport=dst_port, flags="S",seq=(seq if seq is not None else 0))
    pkt = IP(dst=ip_dst)/tcp_layer/Raw(load=payload)
    pkt[IP].len = packet_size
    pkt[IP].chksum = None
    pkt[TCP].chksum = None
    send(pkt, verbose=False)

