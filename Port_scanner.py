from Config_Load import config_load
import random
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed



def is_tcp_open(ipaddr, port, timeout=1.0):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((ipaddr, port)) == 0

def scan_ports_tcp(workers=100, timeout=1.0):
    open_ports = []
    cfg = config_load()
    ipaddr = cfg["ipaddr"]
    tcp_start = int(cfg["tcp_range_start"])
    tcp_end = int(cfg["tcp_range_end"])
    if tcp_end < tcp_start:
        raise ValueError("'tcp_range_end' must be greater than 'tcp_range_start'.")
    ports= range(tcp_start,tcp_end)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(is_tcp_open, ipaddr, port, timeout): port for port in ports}
        for fut in as_completed(futures):
            port = futures[fut]
            try:
                if fut.result():
                    open_ports.append(port)

            except (socket.timeout, TimeoutError, OSError):
                pass
    open_ports.sort()
    dst_port = random.choice(open_ports)
    print("Randomly chosen port:",dst_port)
    return dst_port

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

def scan_ports_udp(workers=100, timeout=1.0):
    open_ports = []
    results = {}
    cfg = config_load()
    ipaddr = cfg["ipaddr"]
    udp_start = cfg["udp_range_start"]
    udp_end = cfg["udp_range_end"]
    if udp_end < udp_start:
        raise ValueError("'udp_range_end' must be greater than 'udp_range_start'.")
    ports= range(udp_start,udp_end)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(probe_udp_simple,ipaddr,port,timeout): port for port in ports}
        for fut in as_completed(futures):
            port = futures[fut]
            try:
                status,data,err = fut.result()
                if status == "open":
                    open_ports.append(port)
                results[port] = (status,err)
            except Exception as e:
                results[port] = ("error",str(e))
                continue
    open_ports.sort()
    dst_port = random.choice(open_ports)
    print(open_ports,results,dst_port)
    return open_ports,results,dst_port
