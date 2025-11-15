from random import choice

from Config_Load import config_load
from scapy.layers.inet import IP,TCP
from scapy.layers.inet6 import IPv6
from scapy.all import  sr1
import time
import random
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
from contextlib import closing


def is_tcp_open(ipaddr, port, timeout=1.0):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((ipaddr, port)) == 0

def scan_ports_tcp(ipaddr, ports, workers=100, timeout=1.0):
    open_ports = []
    dst_port = None
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(is_tcp_open, ipaddr, port, timeout): port for port in ports}
        for fut in as_completed(futures):
            port = futures[fut]
            try:
                if fut.result():          # pokud True (otevřený)
                    open_ports.append(port)
            except Exception:
                # ignoruj chyby jednotlivých pokusů, můžeš logovat pokud chceš
                pass
    open_ports.sort()
    dst_port = random.choice(open_ports)
    print(open_ports,dst_port)
    return open_ports,dst_port


def tcp_scan():
    cfg = config_load()
    ipaddr = cfg["ipaddr"]
    ports= range(12000,13000)
    scan_ports_tcp(ipaddr,ports)

def probe_udp_simple(ipaddr, port, timeout=1.0):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        try:
            s.sendto(b"\x00", (ipaddr, port))
            data, _ = s.recvfrom(4096)
            return 'open', data, None
        except socket.timeout:
            return "no_response", None, "timeout"
        except ConnectionRefusedError:
            return "closed",None,"ICMP_unreachable"
        except Exception as e:
            return "filtered",None,str(e)

def scan_ports_udp(ipaddr, ports, workers=100, timeout=1.0):
    open_ports = []
    results = {}
    dst_port = None
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(probe_udp_simple,ipaddr,port,timeout): port for port in ports}
        for fut in as_completed(futures):
            port = futures[fut]
            try:
                status,data,err = fut.result()
                if status == "open":          # pokud True (otevřený)
                    open_ports.append(port)
                results[port] = (status,err)
            except Exception as e:
                results[port] = ("error",str(e))
                continue
    open_ports.sort()
    dst_port = random.choice(open_ports)
    print(open_ports,results,dst_port)
    return open_ports,results,dst_port

def udp_scan():
    cfg = config_load()
    ipaddr = cfg["ipaddr"]
    ports= range(23000,24000)
    scan_ports_udp(ipaddr,ports)