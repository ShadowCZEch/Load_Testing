import sys
import subprocess
import time
from datetime import datetime
from Config_Load import config_load

def CmdSelect(cfg):
    pick = cfg["pick"]
    ipaddr = cfg["ipaddr"]

    if pick == "4":
        if sys.platform == "win32":
            cmd_base = ["ping", "-n", "1", ipaddr]
            return cmd_base
        else:
            cmd_base = ["ping", "-c", "1", "-W", "1", ipaddr]
            return cmd_base

    if pick == "6":
        if sys.platform == "win32":
            cmd_base = ["ping", "-6", "-n", "1", ipaddr]
            return cmd_base
        else:
            cmd_base = ["ping", "-6", "-c", "1", "-W", "1", ipaddr]
            return cmd_base
    raise ValueError("Unknown value of pick. Watchdog script aborted")

def parse_ping_success(out_bytes):
    out = out_bytes.decode("utf-8", errors="ignore").lower()
    if ("1 received" in out) or ("bytes from" in out) or ("bytes=" in out and "ttl=" in out):
        return True
    return False

def one_ping(cfg):
    cmd = CmdSelect(cfg)
    cfg = config_load()
    poll_interval = float(cfg["poll_interval"])
    timeout = min(0.8, poll_interval)
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        success = parse_ping_success(r.stdout)
        return success, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        return False, getattr(e, "stdout", b""), getattr(e, "stderr", b"")

def PingSetup(cfg):
    poll_interval = cfg["poll_interval"]
    ping_timeout = min(0.8, float(poll_interval))
    timeout_val = max(1.0, ping_timeout)
    for _ in range(2):
        try:
            subprocess.run(CmdSelect(cfg), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout_val)
        except subprocess.TimeoutExpired:
            pass
    last_report_time = 0.0
    return last_report_time

def StatusLoop(cfg):
    last_state = None
    last_report_time = PingSetup(cfg)
    poll_interval = float(cfg["poll_interval"])
    interval = float(cfg["user_interval"])
    if interval < poll_interval:
        raise ValueError("poll_interval can´t have smaller value than interval.")
    try:
        while True:
            start_time = time.time()
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            up, out, err = one_ping(cfg)

            if last_state is None:
                last_state = up
                last_report_time = start_time
                print(f"[{timestamp}]  {'Server is online' if up else 'Server is unavailable'}", flush=True)
            else:
                if up != last_state:
                    last_state = up
                    last_report_time = start_time
                    print(f"[{timestamp}]  {'Server is back up running' if up else 'Server in unavailable'}", flush=True)
                else:
                    if (start_time - last_report_time) >= interval:
                        last_report_time = start_time
                        print(f"[{timestamp}]  {'Server still running' if up else 'Server is still unavailable'}", flush=True)
            elapsed = time.time() - start_time
            sleep_time = max(0.0, float(poll_interval - elapsed))
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user.")


def run():
    cfg = config_load()
    pick = cfg["pick"]
    ipaddr = cfg["ipaddr"]
    interval = cfg["user_interval"]
    print("Loaded user values:")
    print("Protocol:",repr(pick))
    print("IP Address:", repr(ipaddr))
    print("Print interval:", repr(interval),"seconds")
    CmdSelect(cfg)
    PingSetup(cfg)
    print(f"Running server monitoring on address {ipaddr} every {interval} seconds. Use Ctrl+C to stop monitoring.\n")
    StatusLoop(cfg)