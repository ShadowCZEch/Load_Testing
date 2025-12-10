import ipaddress
import random

from scapy.layers.inet import IP,UDP,TCP
from scapy.all import Raw
from Config_Load import config_load
import os
import secrets
from Port_scanner import scan_ports_tcp, scan_ports_udp

def generate_users_from_ip():
    cfg=config_load()

    source_ip_minimal=cfg["source_ip_minimal"]
    source_ip_maximal=cfg["source_ip_maximal"]
    unique_users_count=int(cfg["unique_users_count"])
    pick=int(cfg["pick"])

    if pick == 4:
        ip_min=int(ipaddress.IPv4Address(source_ip_minimal))
        ip_max=int(ipaddress.IPv4Address(source_ip_maximal))
        protocol=ipaddress.IPv4Address
    elif pick == 6:
        ip_min=int(ipaddress.IPv6Address(source_ip_minimal))
        ip_max = int(ipaddress.IPv6Address(source_ip_maximal))
        protocol = ipaddress.IPv6Address
    else:
        raise ValueError("Chybná hodnota pick")

    check = ip_max - ip_min+1

    if ip_min > ip_max:
        raise ValueError("Chyba rozsahu")

    if check < unique_users_count:
        raise ValueError("Přílíš mnoho uživatelů na zvolený rozsah")

    if pick == 4:
        chosen=random.sample(range(ip_min,ip_max+1),unique_users_count)

    else:
        chosen_offset=set()
        while len(chosen_offset) < unique_users_count:
            offset=secrets.randbelow(check)
            chosen_offset.add(ip_min+offset)
        chosen=list(chosen_offset)

    ip_src=[str(protocol(c)) for c in chosen]
    #print(ip_src)
    return ip_src

def udp_packet():

    IP_BASE = 20
    UDP_HDR = 8

    cfg=config_load()
    packet_size=int(cfg["packet_size"])
    ip_dst=cfg["ipaddr"]
    source_generate=generate_users_from_ip()
    port_scan=scan_ports_udp()
    ip_src=random.choice(source_generate)
    dst_port=port_scan
    sport = 12345

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
    cfg=config_load()
    packet_size=int(cfg["packet_size"])
    ip_dst=cfg["ipaddr"]
    source_generate=generate_users_from_ip()
    #port_scan=scan_ports_tcp()
    ip_src=random.choice(source_generate)
    #open_ports,dst_port=port_scan
    sport = 12345
    dst_port = 12345

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
    #print(payload)
    #print("Cílový port",dst_port)
    return payload

