# locustfile.py
from gevent import monkey

from Config_Load import load_ipaddr

monkey.patch_all()

import os
from Config_Load import config_load
from Port_scanner import scan_ports_tcp
from time import perf_counter
from pathlib import Path
import time
import socket
import sys
import subprocess
from typing import Optional
from locust import User, task, between, events

try:
    cfg = config_load()
except Exception as e:
    if __name__ == "__main__":
        print("Error when loading config file, process will be terminated.",e,file=sys.stderr)
        sys.exit(1)
    cfg=None

pick = cfg.get("pick") if cfg else None
host_ip = load_ipaddr(cfg,pick)
test_port = scan_ports_tcp()

def cfg_int(key):
    if cfg is None:
        return None
    k = cfg.get(key)
    if k is None:
        return None
    try:
        return int(k)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid number format in config file")

def cfg_str(key):
    if cfg is None:
        return None
    k = cfg.get(key)
    if k is None:
        return None
    try:
        return str(k)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid format in config file")


class GeventTcpClient:
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = int(port)
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None

    def connect(self):
        start = time.time()
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            elapsed_ms = max(1, int((perf_counter() - start) * 1000))
            events.request.fire(request_type="tcp", name="connect", response_time=elapsed_ms, response_length=0)
        except Exception as e:
            elapsed_ms = max(1, int((perf_counter() - start) * 1000))
            events.request.fire(request_type="tcp", name="connect", response_time=elapsed_ms, exception=e)
            raise

    def send_and_recv(self, data: bytes, recv_buf: int = 4096) -> Optional[bytes]:
        if not self.sock:
            raise RuntimeError("Socket not connected")
        start = perf_counter()
        try:
            self.sock.sendall(data)
            resp = self.sock.recv(recv_buf)
            elapsed_ms = max(1, int((perf_counter() - start) * 1000))
            events.request.fire(request_type="tcp", name="send_recv", response_time=elapsed_ms, response_length=len(resp))
            return resp
        except Exception as e:
            elapsed_ms = max(1, int((perf_counter() - start) * 1000))
            events.request.fire(request_type="tcp", name="send_recv", response_time=elapsed_ms, exception=e)
            try:
                if self.sock:
                    self.sock.close()
            except Exception:
                pass
            self.sock = None
            raise

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

class TcpUser(User):
    wait_time = between(0.5, 1.5)

    def __init__(self, environment):
        super().__init__(environment)
        host = load_ipaddr(cfg,pick)
        port = test_port
        self.client = GeventTcpClient(host=host, port=int(port), timeout=5)

    def on_start(self):
        try:
            self.client.connect()
        except Exception:
            time.sleep(1)

    @task
    def keep_send(self):
        packet_size = int(cfg["packet_size"])

        IP_BASE = 20
        TCP_BASE = 20
        min_total = IP_BASE + TCP_BASE
        if packet_size < min_total:
            raise ValueError(f"target_ip_len must be >= {min_total} (IP + TCP header)")

        payload_len = packet_size - (IP_BASE + TCP_BASE)
        payload = os.urandom(payload_len)
        if not self.client.sock:
            try:
                self.client.connect()
            except Exception:
                time.sleep(1)
                return
        try:
            self.client.send_and_recv(payload)
        except Exception:
            time.sleep(1)


    def on_stop(self):
        self.client.close()

def run_locust_headless_and_make_report(locustfile: str = "locustfile.py",
                                        users: int = None,
                                        spawn_rate: int = None,
                                        run_time: str = None,
                                        html_out: str = "report.html",
                                        host: Optional[str] = host_ip):
    locust_path = Path(locustfile).resolve()
    html_out_p = Path(html_out).resolve()
    if users is None:
        users = cfg_int("unique_users_count")
    else:
        raise ValueError("Users parameter not correctly loaded.")
    if run_time is None:
        run_time = cfg_str("time_total")
    else:
        raise ValueError("Runtime parameter not correctly loaded.")
    if spawn_rate is None:
        spawn_rate = cfg_int("spawn_rate")
    else:
        raise ValueError("Spawn rate parameter not correctly loaded.")

    cmd = [sys.executable, "-m", "locust", "-f", str(locust_path), "--headless",
           "-u", str(users), "-r", str(spawn_rate), "--run-time", run_time, "--html", str(html_out_p)]

    if host:
        cmd += ["--host", host]

    print("Starting TCP scan")
    print("Running Locust:", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    if cfg is None:
        try:
            cfg=config_load()
        except Exception as e:
            print("Error when loading configuration from file:",e,file=sys.stderr)
            sys.exit(1)

    try:
        users = cfg_int(cfg["unique_users_count"])
        spawn_rate = cfg_int(cfg["spawn_rate"])
        run_time = cfg_str(cfg["time_total"])
        html_out = "report.html"
    except Exception as e:
        print("Error when loading configuration from file:",e,file=sys.stderr)
        sys.exit(2)

    try:
        run_locust_headless_and_make_report(
            locustfile=__file__,
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            html_out=html_out,
        )
    except subprocess.CalledProcessError as e:
        print("Error when running Locust process:",e,file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print("Error generating report:",e,file=sys.stderr)
        sys.exit(4)