from pathlib import Path
import ipaddress


def load_config_path(path="Config.conf"):
    pathp = Path(path)
    if not pathp.is_file():
        raise FileNotFoundError(f"Konfigurační soubor nenalezen: {path}")
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
        raise ValueError("Chybí 'Protokol' v konfiguračním souboru.")
    pick = str(protocol).strip()
    if pick not in ("TCP", "UDP"):
        raise ValueError("Chybná hodnota 'Protokol', očekává se TCP nebo UDP.")
    print(protocol)
    return protocol

def load_version(cfg):
    pick = cfg.get("pick")
    if pick is None:
        raise ValueError("Chybná nebo chybějící volba 'pick' (4 nebo 6).")
    pick = str(pick).strip()
    if pick not in ("4", "6"):
        raise ValueError("Chybná hodnota 'pick', očekává se 4 nebo 6.")
    print(pick)
    return pick

def load_ipaddr(cfg,pick):
    ipaddr = cfg.get("ipaddr")
    if not ipaddr:
        raise ValueError("Chybi 'ipaddr' v konfiguračním souboru.")
    ipaddr = ipaddr.strip()
    try:
        if pick == "4":
            ipaddress.IPv4Address(ipaddr)
        else:
            ipaddress.IPv6Address(ipaddr)
    except ValueError:
        raise ValueError("Špatně zadaná IP adresa pro zvolený režim.")
    print(ipaddr)
    return ipaddr

def load_packetsize(cfg):
    packet_size = cfg.get("packet_size")
    if packet_size is None:
        raise ValueError("Chybí 'packet_size' v konfiguračním souboru.")
    pick = str(packet_size).strip()
    print(pick)
    return packet_size

def load_time(cfg):
    time_total = cfg.get("time_total")
    if time_total is None:
        raise ValueError("Chybí 'time_total' v konfiguračním souboru.")
    pick = str(time_total).strip()
    print(pick)
    return time_total

def config_load():
    cfg = load_config_path()
    protocol = load_protocol(cfg)
    version = load_version(cfg)
    ipaddr = load_ipaddr(cfg, version)
    packet_size = load_packetsize(cfg)
    time_total = load_time(cfg)
    return {
        "protocol": protocol,
        "pick": version,
        "ipaddr": ipaddr,
        "packet_size": packet_size,
        "time_total": time_total
    }