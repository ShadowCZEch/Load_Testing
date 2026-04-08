import os
import sys
import subprocess
from Config_Load import Config_Load
from Port_scanner import scan_ports_tcp, scan_ports_udp
import Create_IP_Pool_skript
import Remove_IP_Pool_skript


def run():
    cfg = Config_Load()
    host_ip = cfg.get("ipaddr")
    ip_start = cfg.get("source_ip_minimal")
    ip_end = cfg.get("source_ip_maximal")
    protocol = cfg.get("protocol", "").lower()

    ip_list = Create_IP_Pool_skript.main(ip_start, ip_end, interface="ens33")

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
    env["IP_POOL_FILE"] = "/home/me/Desktop/ip_pool.txt"

    try:
        print(f"Running Locust on {host}...")
        subprocess.check_call(cmd, env=env)
    except KeyboardInterrupt:
        print("\nStopping Locust...")
    finally:
        print("\n--- Čištění systému (Cleanup) ---")
        try:
            Remove_IP_Pool_skript.main(
                ip_start=ip_start,
                ip_end=ip_end,
                interface="ens33"
            )
            print("[OK] Všechny virtuální IP byly odstraněny.")
        except Exception as e:
            print(f"[WARN] Cleanup narazil na problém: {e}")

if __name__ == "__main__":
    run()

