from scapy.layers.inet import IP,UDP,TCP
from scapy.all import Raw,send,conf
from Config_Load import config_load
import os


def udp_packet(ip_src, dport, sport=12345):

    # Standartní velikosti částí UDP paketu
    IP_BASE = 20          # IP hlavička bez options
    UDP_HDR = 8

    cfg=config_load()
    packet_size=cfg["packet_size"]
    ip_dst=cfg["ipaddr"]
    if packet_size < IP_BASE + UDP_HDR:
        raise ValueError(f"Zadána menší než standartní velikost paketu. Bude použita standartní velikost. \n "
                         f" Pro větší velikost  musí být packet_size alespoň >= {IP_BASE + UDP_HDR}")


    payload_len = packet_size - (IP_BASE + UDP_HDR)
    payload = os.urandom(payload_len)

    pkt = IP(src=ip_src, dst=ip_dst)/UDP(sport=sport, dport=dport)/Raw(load=payload)
    pkt[IP].len = packet_size
    pkt[IP].chksum = None
    pkt[UDP].len = None
    pkt[UDP].chksum = None
    return pkt

def tcp_packet(ip_src, dport, sport=12345):

    IP_BASE = 20
    TCP_BASE = 20  # základ bez options

    # ip_src od user scriptu, dport od skeneru, sport?
    cfg=(config_load())
    packet_size=cfg["packet_size"]
    ip_dst=cfg["ipaddr"]

    min_total = IP_BASE + TCP_BASE
    if packet_size < min_total:
        raise ValueError(f"target_ip_len musí být >= {min_total} (IP + TCP hlavička)")

    payload_len = packet_size - (IP_BASE + TCP_BASE)
    payload = os.urandom(payload_len)

    tcp_layer = TCP(sport=sport, dport=dport)
    pkt = IP(src=ip_src, dst=ip_dst)/tcp_layer/Raw(load=payload)
    pkt[IP].len = packet_size
    pkt[IP].chksum = None
    pkt[TCP].chksum = None
    return pkt