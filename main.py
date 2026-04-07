import os
import sys
import subprocess
from Config_Load import Config_Load
from Port_scanner import scan_ports_tcp, scan_ports_udp


def run():
    cfg = Config_Load()
    host_ip = cfg.get("ipaddr")
    protocol = cfg.get("protocol", "").lower()

    if protocol == "tcp":
        print("Starting TCP scan...")
        port = scan_ports_tcp()
    else:
        print("Starting UDP scan...")
        port = scan_ports_udp()

    host = f"{host_ip}:{port}"

    users = cfg.get("unique_users_count")
    spawn_rate = cfg.get("spawn_rate")
    run_time = cfg.get("time_total")

    cmd = [
        sys.executable, "-m", "locust",
        "-f", "Locust.py",
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "--run-time", f"{run_time}s",
        "--html", "report.html",
        "--host", host
    ]

    env = os.environ.copy()
    env["LOCUST_MODE"] = protocol
    env["TARGET_PORT"] = str(port)
    env["PYTHONPATH"] = os.getcwd()

    print(f"Running Locust on {host}...")
    try:
        subprocess.check_call(cmd, env=env)
    except KeyboardInterrupt:
        print("\nStopping...")


if __name__ == "__main__":
    run()

