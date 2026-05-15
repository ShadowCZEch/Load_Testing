

from scapy.error import Scapy_Exception

from Config_Load import config_load
import random
from scapy.layers.inet import IP,TCP,sr1
from concurrent.futures import ThreadPoolExecutor, as_completed


def syn_scan(target_ip,version, port, timeout=0.5):
    from scapy.all import IPv6
    protocol = IP(dst=target_ip) if version == 4 else IPv6(dst=target_ip)
    pkt = protocol/TCP(dport=port,flags="S")
    resp = sr1(pkt,timeout=timeout,verbose=False)

    if resp and resp.haslayer(TCP) and resp[TCP].flags == 0x12:
        rst = IP(dst=target_ip)/TCP(dport=port,flags="R")
        sr1(rst,timeout=timeout,verbose=False)
        return True
    return False

def scan_ports_tcp(range_start=None, range_end = None, host_ip=None, version=None, workers=200, timeout=0.5):
    open_ports = []
    cfg = config_load()
    ipaddr  = host_ip or cfg.get("ipaddr")
    version = int(version or cfg.get("version"))
    tcp_start = int(range_start or cfg.get("tcp_range_start"))
    tcp_end   = int(range_end   or cfg.get("tcp_range_end"))
    if tcp_end < tcp_start:
        raise ValueError("'tcp_range_end' must be greater than 'tcp_range_start'.")
    ports= range(tcp_start,tcp_end +1)
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

