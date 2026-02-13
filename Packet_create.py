
import random

from scapy.layers.inet import IP,UDP,TCP
from scapy.all import Raw
from Config_Load import Config_Load
from IP_address import IPGenerator
import os
from Port_scanner import scan_ports_tcp, scan_ports_udp

def udp_packet():

    IP_BASE = 20
    UDP_HDR = 8

    cfg=Config_Load()
    packet_size=int(cfg("packet_size"))
    ip_dst=cfg("ipaddr")
    pool= IPGenerator()
    port_scan=scan_ports_udp()
    ip_src=pool.get_ips()
    dst_port=port_scan
    sport = random.sample(range(1,65535),1)

    if packet_size < IP_BASE + UDP_HDR:
        print(f"Zadána menší než standartní velikost paketu. Bude použita standartní velikost. \n "
                         f" Pro větší velikost  musí být packet_size alespoň >= {IP_BASE + UDP_HDR}")


    payload_len = packet_size - (IP_BASE + UDP_HDR)
    if payload_len > 0:
        payload = os.urandom(payload_len)
    else:
        payload = b""
    pkt = IP(src=ip_src, dst=ip_dst)/UDP(sport=sport, dport=dst_port)/Raw(load=payload)
    pkt[IP].len = packet_size
    pkt[IP].chksum = None
    pkt[UDP].len = None
    pkt[UDP].chksum = None
    return pkt

def tcp_packet():
    cfg=Config_Load()
    packet_size=int(cfg("packet_size"))
    ip_dst=cfg("ipaddr")
    pool= IPGenerator()
    port_scan=scan_ports_tcp()
    ip_src=pool.get_ips()
    sport = random.sample(range(1,65535),1)
    dst_port = port_scan

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
    pkt = IP(src=ip_src, dst=ip_dst)/tcp_layer/Raw(load=payload)
    pkt[IP].len = packet_size
    pkt[IP].chksum = None
    pkt[TCP].chksum = None
    return payload

