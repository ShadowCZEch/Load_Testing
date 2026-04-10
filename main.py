import os
import sys
import subprocess
from Config_Load import Config_Load
from Port_scanner import scan_ports_tcp, scan_ports_udp
import Create_IP_Pool_skript
import Remove_IP_Pool_skript
from Create_topology import create_topology_diagram
import time
from Network_monitor import NetworkMonitor

def run():

    cfg = Config_Load()
    host_ip = cfg.get("ipaddr")
    ip_start = cfg.get("source_ip_minimal")
    ip_end = cfg.get("source_ip_maximal")
    protocol = cfg.get("protocol", "").lower()
    worker_count = int(cfg.get("workers"))

    __ip_list = Create_IP_Pool_skript.main(ip_start, ip_end, interface="eth2")

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

    env = os.environ.copy()
    env["LOCUST_MODE"] = protocol
    env["TARGET_PORT"] = str(port)
    env["PYTHONPATH"] = os.getcwd()
    env["IP_POOL_FILE"] = "/home/me/Desktop/ip_pool.txt"

    master_cmd = [
        sys.executable, "-m", "locust",
        "-f", "Locust.py",
        "--master",
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "--run-time", f"{run_time}s",
        "--expect-workers", str(worker_count),
        "--html", "report.html",
        "--host", host
    ]

    worker_cmd = [
        sys.executable, "-m", "locust",
        "-f", "Locust.py",
        "--worker",
    ]

    processes = []

    try:
        print(f"Running Locust on {host}...")
        master_proc = subprocess.Popen(master_cmd, env=env)
        processes.append(master_proc)
        time.sleep(1)

        print(f"Running {worker_count} workers...")
        for i in range(worker_count):
            w_proc=subprocess.Popen(worker_cmd, env=env)
            processes.append(w_proc)

        master_proc.wait()
        print("Test done.")
        create_topology_diagram()

    except KeyboardInterrupt:
        print("\nStopping Locust...")
    finally:
        print("\n--- Čištění systému (Cleanup) ---")
        try:
            for p in processes:
                if p.poll() is None:
                    p.terminate()
            Remove_IP_Pool_skript.main(
                ip_start=ip_start,
                ip_end=ip_end,
                interface="eth2"
            )
            print("[OK] Všechny virtuální IP byly odstraněny.")
        except Exception as e:
            print(f"[WARN] Cleanup narazil na problém: {e}")

if __name__ == "__main__":
    run()

