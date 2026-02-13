import time
from datetime import datetime
import socket
from scapy.error import Scapy_Exception
from scapy.layers.inet import IP, ICMP
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest
from scapy.sendrecv import sr1

from Config_Load import Config_Load
import ipaddress

def one_ping(ipaddr,timeout):
    try:
        ip_ver = ipaddress.ip_address(ipaddr)
        if ip_ver.version == 4:
            pkt = IP(dst=ipaddr)/ICMP()
        elif ip_ver.version == 6:
            pkt = IPv6(dst=ipaddr)/ICMPv6EchoRequest()
        else:
            raise ValueError("Invalid IP address.")
        reply = sr1(pkt, timeout=timeout,verbose=False)
        return reply is not None
    except (ValueError, Scapy_Exception, OSError, socket.error):
        return False

def PingSetup(ipaddr,timeout):
    one_ping(ipaddr,timeout)
    return 0.0

def Watchdog():
    cfg = Config_Load()
    ipaddr = cfg.get("ipaddr")
    interval = float(cfg.get("user_interval"))
    poll_interval = float(cfg.get("poll_interval"))
    ping_timeout = min(0.8, float(poll_interval))
    timeout = max(1.0, ping_timeout)

    last_state = None
    last_report_time = PingSetup(ipaddr,timeout)
    print(f"Running server monitoring on address {ipaddr} every {interval} seconds. Use Ctrl+C to stop monitoring.\n")

    if interval < poll_interval:
        raise ValueError("poll_interval can´t have smaller value than interval.")
    try:
        while True:
            start_time = time.time()
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            up = one_ping(ipaddr,timeout)

            if last_state is None:
                last_state = up
                last_report_time = start_time
                print(f"[{timestamp}]  {'Server is online' if up else 'Server is unavailable'}", flush=True)
            else:
                if up != last_state:
                    last_state = up
                    last_report_time = start_time
                    print(f"[{timestamp}]  {'Server is back up running' if up else 'Server is unavailable'}", flush=True)
                else:
                    if (start_time - last_report_time) >= interval:
                        last_report_time = start_time
                        print(f"[{timestamp}]  {'Server still running' if up else 'Server is still unavailable'}", flush=True)
            elapsed = time.time() - start_time
            sleep_time = max(0.0, float(poll_interval - elapsed))
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user.")
