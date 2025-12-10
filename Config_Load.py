from pathlib import Path
import ipaddress


def load_config_path(path="Config.env"):
    pathp = Path(path)
    if not pathp.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")
    cfg = {}
    with pathp.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip().lower()] = v.strip()
    return cfg

def load_protocol(cfg):
    protocol = cfg.get("protocol")
    if protocol is None:
        raise ValueError("Missing 'Protocol' parameter in config file.")
    protocol = str(protocol).strip().upper()
    if protocol not in ("TCP", "UDP"):
        raise ValueError("Invalid 'Protocol' value in config file, TCP or UDP expected.")
    return protocol

def load_version(cfg):
    pick = cfg.get("pick")
    if pick is None:
        raise ValueError("Parameter 'pick' missing in configuration file.")
    pick = str(pick).strip()
    if pick not in ("4", "6"):
        raise ValueError("Invalid 'pick' in config file, expected 4 or 6.")
    return pick

def load_ipaddr(cfg,pick):
    ipaddr = cfg.get("ipaddr")
    if ipaddr is None:
        raise ValueError("Parameter 'ipaddr' missing in configuration file.")
    ipaddr = ipaddr.strip()
    try:
        if pick == "4":
            ipaddress.IPv4Address(ipaddr)
        elif pick == "6":
            ipaddress.IPv6Address(ipaddr)
    except ValueError:
        raise ValueError("Incorrect IP address for selected mode.")
    return ipaddr

def load_packetsize(cfg):
    packet_size = cfg.get("packet_size")
    if packet_size is None:
        raise ValueError(" 'packet_size' missing in configuration file.")
    return packet_size

def load_time(cfg):
    time_total = cfg.get("time_total")
    if time_total is None:
        raise ValueError("'time_total' is missing in configuration file.")
    pick = str(time_total).strip()
    time = int(pick)
    if time < 1:
        raise ValueError("'time_total' is out of range.")
    return time_total

def load_source_ip_minimal(cfg,pick):
    source_ip_minimal = cfg.get("source_ip_minimal")
    if source_ip_minimal is None:
        raise ValueError("'source_ip_minimal' is missing in configuration file.")
    load_ip_minimal = str(source_ip_minimal).strip()
    try:
        if pick == "4":
            ipaddress.IPv4Address(load_ip_minimal)
        elif pick == "6":
            ipaddress.IPv6Address(load_ip_minimal)
    except ValueError:
        raise ValueError("IP address is not valid.")
    return source_ip_minimal

def load_source_ip_maximal(cfg,pick):
    source_ip_maximal = cfg.get("source_ip_maximal")
    if source_ip_maximal is None:
        raise ValueError("'source_ip_maximal' is missing in configuration file.")
    load_ip_maximal = str(source_ip_maximal).strip()
    try:
        if pick == "4":
            ipaddress.IPv4Address(load_source_ip_maximal)
        elif pick == "6":
            ipaddress.IPv6Address(load_ip_maximal)
    except ValueError:
        raise ValueError("IP address is not valid.")
    return source_ip_maximal

def load_unique_users_count(cfg):
    unique_users_count = cfg.get("unique_users_count")
    if unique_users_count is None:
        raise ValueError("'unique_users_count' is missing in configuration file.")
    pick = str(unique_users_count).strip()
    unique_users_count = int(pick)
    if unique_users_count < 1:
        raise ValueError("'unique_users_count' is out of range.")
    return unique_users_count

def scan_port_range_tcp_start(cfg):
    tcp_range_start = cfg.get("scan_port_range_tcp_start")
    if tcp_range_start is None:
        raise ValueError("'scan_port_range_tcp_start' is missing in configuration file.")
    pick = str(tcp_range_start).strip()
    tcp_range_start = int(pick)
    if tcp_range_start > 65535:
        raise ValueError ("'scan_port_range_tcp_start' is out of range.")
    if tcp_range_start < 1:
        raise ValueError("'scan_port_range_tcp_start' is out of range.")
    return tcp_range_start

def scan_port_range_tcp_end(cfg):
    tcp_range_end = cfg.get("scan_port_range_tcp_end")
    if tcp_range_end is None:
        raise ValueError("'scan_port_range_tcp_end' is missing in configuration file.")
    pick = str(tcp_range_end).strip()
    tcp_range_end = int(pick)
    if tcp_range_end > 65535:
        raise ValueError("'scan_port_range_tcp_end' is out of range.")
    if tcp_range_end < 1:
        raise ValueError("'scan_port_range_tcp_end' is out of range.")
    return tcp_range_end

def scan_port_range_udp_start(cfg):
    udp_range_start = cfg.get("scan_port_range_udp_start")
    if udp_range_start is None:
        raise ValueError("'scan_port_range_udp_start' is missing in configuration file.")
    pick = str(udp_range_start).strip()
    udp_range_start= int(pick)
    if udp_range_start < 1:
        raise ValueError("'scan_port_range_udp_start' is out of range.")
    return udp_range_start

def scan_port_range_udp_end(cfg):
    udp_range_end = cfg.get("scan_port_range_udp_end")
    if udp_range_end is None:
        raise ValueError("'scan_port_range_udp_end' is missing in configuration file.")
    pick = str(udp_range_end).strip()
    udp_range_end = int(pick)
    if udp_range_end > 65535:
        raise ValueError("'scan_port_range_udp_end' is out of range.")
    return udp_range_end

def user_interval(cfg):
    interval = cfg.get("interval")
    check = int(interval)
    if check is None:
        raise ValueError("'interval' is missing in configuration file.")
    if check < 0:
        raise ValueError("'interval' is in unacceptable range.")
    return interval

def poll_interval(cfg):
    ping_interval = cfg.get("poll_interval")
    check = int(ping_interval)
    if check is None:
        raise ValueError("'poll_interval' is missing in configuration file.")
    if check < 0:
        raise ValueError("'poll_interval' is in unacceptable range.")
    return ping_interval

def spawn_rate(cfg):
    spwn_rate = cfg.get("spawn_rate")
    check = int(spwn_rate)
    if check is None:
        raise ValueError("'spawn_rate' is missing in configuration file.")
    if check < 0:
        raise ValueError("'spawn_rate' is in unacceptable range.")
    return spwn_rate

def config_load():
    cfg = load_config_path()
    pick = load_protocol(cfg)
    protocol = load_protocol(cfg)
    version = load_version(cfg)
    ipaddr = load_ipaddr(cfg, version)
    packet_size = load_packetsize(cfg)
    time_total = load_time(cfg)
    source_ip_minimal = load_source_ip_minimal(cfg,pick)
    source_ip_maximal = load_source_ip_maximal(cfg,pick)
    unique_users_count = load_unique_users_count(cfg)
    tcp_range_start=scan_port_range_tcp_start(cfg)
    tcp_range_end=scan_port_range_tcp_end(cfg)
    udp_range_start=scan_port_range_udp_start(cfg)
    udp_range_end=scan_port_range_udp_end(cfg)
    interval = user_interval(cfg)
    ping_interval = poll_interval(cfg)
    spwn_rate = spawn_rate(cfg)

    return {
        "protocol": protocol,
        "pick": version,
        "ipaddr": ipaddr,
        "packet_size": packet_size,
        "time_total": time_total,
        "source_ip_minimal": source_ip_minimal,
        "source_ip_maximal" : source_ip_maximal,
        "unique_users_count": unique_users_count,
        "tcp_range_start":tcp_range_start,
        "tcp_range_end":tcp_range_end,
        "udp_range_start":udp_range_start,
        "udp_range_end":udp_range_end,
        "user_interval": interval,
        "poll_interval": ping_interval,
        "spawn_rate": spwn_rate,
    }