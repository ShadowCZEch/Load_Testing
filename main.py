import os
import sys
import subprocess
import socket
import ipaddress
from urllib.parse import urlparse
from Config_Load import Config_Load
from Port_scanner import scan_ports_tcp
import time
import random

def resolve_host(host_input):
    parsed = urlparse(host_input)
    hostname = parsed.hostname or host_input.strip()
    try:
        ipaddress.ip_address(hostname)
        return hostname
    except ValueError:
        pass
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        raise ValueError(f"Could not resolve host: {host_input}")

def scan(
    host_ip=None,
    protocol=None,
    range_start=None,
    range_end=None,
):
    cfg = Config_Load()
    host_ip = resolve_host(host_ip or cfg.get("ipaddr"))
    protocol = (protocol or cfg.get("protocol", "")).lower()

    if protocol == "tcp":
        print("Starting TCP scan...")
        return scan_ports_tcp(
            range_start=range_start or cfg.get("tcp_range_start"),
            range_end=range_end or cfg.get("tcp_range_end"),
            host_ip=host_ip,
            version=6 if ":" in host_ip else 4
        )
    else:
        dst_port = random.randint(int(range_start), int(range_end))
        return dst_port

def run(
    host_ip=None,
    protocol=None,
    worker_count=None,
    users=None,
    spawn_rate=None,
    run_time=None,
    packet_size=None,
    range_start=None,
    range_end=None,
    ip_pool_file=None,
    port=None,
    on_master_start=None,
    csv_prefix=None,
    iface=None,
    synack_timeout=None,
    stop_timeout=None,
):
    cfg = Config_Load()
    host_ip = resolve_host(host_ip or cfg.get("ipaddr"))
    protocol = (protocol or cfg.get("protocol", "")).lower()
    worker_count = int(worker_count or cfg.get("workers"))
    users = users or cfg.get("unique_users_count")
    spawn_rate = spawn_rate or cfg.get("spawn_rate")
    run_time = run_time or cfg.get("time_total")
    iface = iface or cfg.get("interface")
    print(f"[DEBUG] iface from config = {repr(iface)}")
    if not iface:
        raise ValueError("interface not set in config. Select an interface in the GUI.")
    stop_timeout = str(stop_timeout or cfg.get("stop_timeout") or 60)


    pool_file = ip_pool_file or os.path.join(os.getcwd(), "ip_pool.txt")
    if not os.path.isfile(pool_file):
        raise FileNotFoundError(
            f"IP pool file not found: {pool_file}\n"
            "Generate it first using the IP Pool section in the GUI."
        )

    if port is None:
        port = scan(host_ip=host_ip, protocol=protocol,
                    range_start=range_start, range_end=range_end)

    host = f"{host_ip}:{port}"

    env = os.environ.copy()
    env["LOCUST_MODE"] = protocol
    env["TARGET_PORT"] = str(port)
    env["PACKET_SIZE"] = str(packet_size or cfg.get("packet_size") or 60)
    env["TARGET_HOST"] = host_ip
    env["PYTHONPATH"] = os.getcwd()
    env["IP_POOL_FILE"] = pool_file
    env["IFACE"] = iface
    env["SYNACK_TIMEOUT"] = str(synack_timeout or cfg.get("synack_timeout") or "5")

    locust_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "Locust_tcp.py" if protocol == "tcp" else "Locust_udp.py")

    csv_out = csv_prefix or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "report")

    master_cmd = [
        "sudo",
        f"IFACE={iface}",
        f"IP_POOL_FILE={pool_file}",
        f"TARGET_HOST={host_ip}",
        f"TARGET_PORT={port}",
        f"PACKET_SIZE={packet_size or cfg.get('packet_size') or 60}",
        f"LOCUST_MODE={protocol}",
        f"PYTHONPATH={os.getcwd()}", sys.executable, "-m", "locust",
        f"SYNACK_TIMEOUT={synack_timeout or cfg.get('synack_timeout') or 5}",
        "-f", locust_file,
        "--master",
        "--headless",
        "--csv", csv_out,
        "-u", str(users),
        "--stop-timeout", stop_timeout,
        "-r", str(spawn_rate),
        "--stop-timeout", stop_timeout,
        "--run-time", f"{run_time}s",
        "--expect-workers", str(worker_count),
        "--html", os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.html"),
        "--csv", csv_out,
        "--host", host
    ]

    worker_cmd = [
        "sudo",
        f"IFACE={iface}",
        f"IP_POOL_FILE={pool_file}",
        f"TARGET_HOST={host_ip}",
        f"TARGET_PORT={port}",
        f"PACKET_SIZE={packet_size or cfg.get('packet_size') or 60}",
        f"LOCUST_MODE={protocol}",
        f"PYTHONPATH={os.getcwd()}",
        f"SYNACK_TIMEOUT={synack_timeout or cfg.get('synack_timeout') or 5}",
        sys.executable,
        "-m",
        "locust",
        "-f", locust_file,
        "--worker",
    ]

    processes = []

    try:
        print(f"Running Locust on {host}...")
        master_proc = subprocess.Popen(master_cmd)
        processes.append(master_proc)

        if on_master_start:
            on_master_start(master_proc)

        time.sleep(1)

        print(f"Running {worker_count} workers...")
        for i in range(worker_count):
            w_env = env.copy()
            w_env["LOCUST_WORKER_ID"] = str(i)
            w_proc = subprocess.Popen(worker_cmd)
            processes.append(w_proc)

        master_proc.wait()
        print("Test done.")

    except KeyboardInterrupt:
        print("\nStopping Locust...")
    finally:
        print("\n--- System cleanup running ---")
        try:
            for p in processes:
                if p.poll() is None:
                    p.terminate()
                    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report")
                    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
                    uid = os.getuid()
                    gid = os.getgid()
                    for path in [report_dir, data_dir]:
                        if os.path.exists(path):
                            os.chown(path, uid, gid)
                            for root, dirs, files in os.walk(path):
                                for d in dirs:
                                    os.chown(os.path.join(root, d), uid, gid)
                                for f in files:
                                    os.chown(os.path.join(root, f), uid, gid)
            print("[OK] All IPs successfully removed.")
        except Exception as e:
            print(f"[WARN] Encountered issue during cleanup: {e}")

if __name__ == "__main__":
    run()

