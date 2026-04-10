

from scapy.error import Scapy_Exception

from Config_Load import config_load
import random
import socket
from scapy.layers.inet import IP,TCP,sr1
from concurrent.futures import ThreadPoolExecutor, as_completed


def syn_scan(target_ip,version, port, timeout=0.5,environment=None):
    from scapy.all import IPv6
    protocol = IP(dst=target_ip) if version == 4 else IPv6(dst=target_ip)
    pkt = protocol/TCP(dport=port,flags="S")
    resp = sr1(pkt,timeout=timeout,verbose=False)

    if resp and resp.haslayer(TCP) and resp[TCP].flags == 0x12:
        rst = IP(dst=target_ip)/TCP(dport=port,flags="R")
        sr1(rst,timeout=timeout,verbose=False)
        return True
    return False

def scan_ports_tcp(workers=50, timeout=0.5):
    open_ports = []
    cfg = config_load()
    ipaddr = cfg.get("ipaddr")
    version = int(cfg.get("version"))
    tcp_start = cfg.get("tcp_range_start")
    tcp_end = cfg.get("tcp_range_end")
    if tcp_end < tcp_start:
        raise ValueError("'tcp_range_end' must be greater than 'tcp_range_start'.")
    ports= range(tcp_start,tcp_end)
    total= len(ports)
    scanned = 0

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(syn_scan, ipaddr, version, port, timeout): port for port in ports}
        for fut in as_completed(futures):
            scanned += 1
            port = futures[fut]

            if scanned % max(1,total//20) == 0:
                percent = (scanned/total)*100
                print(f"Progress: {percent:.1f}% ({scanned}/{total})")
            try:
                if fut.result():
                    open_ports.append(port)

            except (Scapy_Exception, OSError, TimeoutError):
                pass
    open_ports.sort()
    if not open_ports:
        raise ValueError("No open ports found.")
    dst_port = random.choice(open_ports)
    print("Randomly chosen port:",dst_port)
    return dst_port

def probe_udp_simple(ipaddr,version, port, timeout=0.5, environment = None):
    family = socket.AF_INET if version == 4 else socket.AF_INET6
    with socket.socket(family, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        try:
            s.sendto(b"\x00", (ipaddr, port))
            data, _ = s.recvfrom(4096)

        except socket.timeout:
            return "open", None, "timeout"
        except ConnectionRefusedError:
            return "closed",None,"ICMP_unreachable"
        except Exception as e:
            return "filtered",None,str(e)

def scan_ports_udp(workers=50, timeout=0.5):
    open_ports = []
    results = {}
    cfg = config_load()
    ipaddr = cfg.get("ipaddr")
    version = int(cfg.get("version"))
    udp_start = cfg.get("udp_range_start")
    udp_end = cfg.get("udp_range_end")

    if udp_end < udp_start:
        raise ValueError("'udp_range_end' must be greater than 'udp_range_start'.")
    ports= range(udp_start,udp_end)
    total= len(ports)
    scanned = 0

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(probe_udp_simple,ipaddr,version, port,timeout): port for port in ports}
        for fut in as_completed(futures):
            scanned += 1
            port = futures[fut]

            if scanned % max(1,total//20) == 0:
                percent = (scanned/total)*100
                print(f"Progress: {percent:.1f}% ({scanned}/{total})")
            try:
                status,data,err = fut.result()
                if status == "open":
                    open_ports.append(port)
                results[port] = (status,err)
            except Exception as e:
                results[port] = ("error",str(e))
                continue
    open_ports.sort()
    if not open_ports:
        print("No open ports found.Selecting random port in specified range for bandwith jamming.")
        dst_port = random.randint(udp_start, udp_end)
    else:
        dst_port = random.choice(open_ports)
    print("Randomly chosen port:",dst_port)
    return dst_port
