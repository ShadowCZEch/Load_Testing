# locustfile.py

import os
from gevent import monkey
import time
import queue
from locust import User, task, events, constant
from gevent import sleep
from Config_Load import Config_Load

monkey.patch_all()

POOL_FILE = "/home/me/Desktop/ip_pool.txt"
cfg = Config_Load()

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

TARGET_PORT = int(os.environ.get("TARGET_PORT", 0))
LOCUST_MODE = os.environ.get("LOCUST_MODE")

ip_queue = queue.Queue()

@events.test_start.add_listener
def on_test_start(environment, **_kwargs):
    pool_file = os.environ.get("IP_POOL_FILE")
    if pool_file and os.path.exists(pool_file):
        with open(pool_file, "r") as f:
            for line in f:
                addr = line.strip()
                if addr:
                    ip_queue.put(addr)
        print(f"[Locust] Načteno {ip_queue.qsize()} unikátních zdrojových IP.")
    else:
        print("[Error] Soubor s IP pool nebyl nalezen!")

class UserClass(User):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_ip = None

    wait_time = constant(0)

    def on_start(self):
        try:
            self.source_ip = ip_queue.get_nowait()
        except queue.Empty:
            self.source_ip = None

    @task
    def keep_send(self):
        from Packet_create import tcp_packet, udp_packet

        if LOCUST_MODE == "tcp":
                start = time.perf_counter()
                try:
                    tcp_packet(dst_port=TARGET_PORT)
                    rt = (time.perf_counter() - start) * 1000
                    self.environment.events.request.fire(
                        request_type="TCP",
                        name="tcp_flood",
                        response_time=rt,
                        response_length=0,
                        exception=None,
                    )
                except Exception as e:
                    self.environment.events.request.fire(
                        request_type="TCP",
                        name="tcp_flood",
                        response_time=0,
                        response_length=0,
                        exception=e,
                    )
                sleep(0)


        elif LOCUST_MODE == "udp":
                start = time.perf_counter()
                try:
                    udp_packet(dst_port=TARGET_PORT)
                    rt = (time.perf_counter() - start) * 1000
                    self.environment.events.request.fire(
                        request_type="UDP",
                        name="udp_flood",
                        response_time=rt,
                        response_length=0,
                        exception=None,
                    )
                except Exception as e:
                    self.environment.events.request.fire(
                        request_type="UDP",
                        name="udp_flood",
                        response_time=0,
                        response_length=0,
                        exception=e,
                    )
                sleep(0)

